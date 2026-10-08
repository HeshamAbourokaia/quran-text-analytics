# -*- coding: utf-8 -*-
"""The discovery studies, run exactly as pre-registered in data-build/discover/PREREGISTRATION.md.

Each study returns what the app's Discoveries pages show (web/discoveries.js): the numbers, the chance
baseline and p-value of every primary test, the verdict the rules give, and the material for the figures.
Nothing here decides a rule after seeing a result; see the pre-registration's Deviations and Corrections for changes.

Run (from data-build):  python3 -m pipeline.discoveries [study ...]   prints a summary of each study
                        python3 -m pipeline.discoveries --write         writes out/discoveries.json and ../web/discoveries.js
tests/test_discoveries.py checks that the committed results still match this code.
"""
import ast, difflib, math, os, re
from collections import Counter, defaultdict

import numpy as np
from scipy import stats
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_predict

from .corpus import normalize, _read_rows

HERE = os.path.dirname(__file__)
ALPHA = 0.05


class SurahFolds:
    """Five folds that keep each surah whole: the largest surahs first, each to the fold with the fewest verses so far
    (GroupKFold's rule), with surahs of equal size taken later surah first. GroupKFold breaks those ties with numpy's
    default sort, whose order differs between machines, so the same code gave study 1 an accuracy of 0.3565 on the
    machine that published it and 0.3435 on another. A stable sort fixes the published folds everywhere."""
    def __init__(self, n_splits=5):
        self.n_splits = n_splits
    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits
    def split(self, X, y=None, groups=None):
        u, gi = np.unique(groups, return_inverse=True); n = np.bincount(gi)
        load, fold = np.zeros(self.n_splits), np.zeros(len(u), int)
        for i in np.argsort(n, kind='stable')[::-1]:
            f = int(np.argmin(load)); load[f] += n[i]; fold[i] = f
        of, idx = fold[gi], np.arange(len(gi))
        for f in range(self.n_splits):
            yield idx[of != f], idx[of == f]


# ---------------------------------------------------------------- common ground
def _verses(words):
    """(sura, aya) -> the verse's words, in mushaf order."""
    v = defaultdict(list)
    for w in words:
        v[(w['sura'], w['aya'])].append(w)
    return dict(sorted(v.items()))

def _content_doc(ws):
    return ' '.join(w['lemma'] for w in ws if w['pos'] in ('N', 'V') and w['lemma'])

def _verse_matrix(V):
    """TF-IDF over the lemmas of each verse's content words (min_df=2, sublinear tf, unit rows)."""
    keys = list(V)
    vec = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2, sublinear_tf=True)
    X = vec.fit_transform([_content_doc(V[k]) for k in keys])
    return keys, X, vec

def _holm(ps):
    """Holm-adjusted p-values, in the given order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj

def _bh(ps, q):
    """Benjamini-Hochberg: which hypotheses are rejected at level q."""
    m = len(ps); order = np.argsort(ps); keep = np.zeros(m, bool); thr = -1
    for rank, i in enumerate(order, 1):
        if ps[i] <= q * rank / m: thr = rank
    if thr > 0: keep[order[:thr]] = True
    return keep

def _pval(null, obs):
    null = np.asarray(null)
    return float(((null >= obs).sum() + 1) / (len(null) + 1))

def _summ(null, obs=None, bins=30):
    """A null distribution as the site shows it: its summary, how far the real value sits from it (z), and a histogram."""
    null = np.asarray(null, dtype=float); sd = float(null.std())
    out = {'mean': round(float(null.mean()), 6), 'sd': round(sd, 6), 'p95': round(float(np.percentile(null, 95)), 6),
           'max': round(float(null.max()), 6), 'n': int(len(null))}
    if obs is not None:
        lo, hi = float(min(null.min(), obs)), float(max(null.max(), obs))
        counts = np.histogram(null, bins=bins, range=(lo, hi if hi > lo else lo + 1e-9))[0]
        out.update({'obs': round(float(obs), 6), 'ge': int((null >= obs).sum()), 'z': round((obs - float(null.mean())) / sd, 2) if sd else None,
                    'hist': {'lo': round(lo, 6), 'hi': round(hi, 6), 'counts': [int(c) for c in counts]}})
    return out

def _cos(a, b):
    a = np.asarray(a).ravel(); b = np.asarray(b).ravel()
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a @ b / (na * nb)) if na and nb else 0.0


# ---------------------------------------------------------------- 1. verse-ending names
NAME_ROOTS = ['غفر','رحم','عزز','حكم','علم','خبر','سمع','بصر','قدر','حمد','غني','رأف','توب','حلم','كرم','شكر','ودد','مجد',
              'لطف','قوي','عفو','وسع','شهد','رقب','وكل','حفظ','قهر','ولي','نصر','قرب','جيب','حسب','كبر','علو','عظم','حقق',
              'بين','وهب','رزق','فتح','ملك','قدس','سلم','أمن','هيمن','جبر','خلق','برأ','صور','حيي','قوم','وحد','صمد','أول',
              'أخر','ظهر','بطن','برر','جلل']
NAME_EN = {'غفر': 'Forgiving', 'رحم': 'Merciful', 'عزز': 'Mighty', 'حكم': 'Wise', 'علم': 'Knowing', 'خبر': 'Aware',
           'سمع': 'Hearing', 'بصر': 'Seeing', 'قدر': 'Powerful', 'حمد': 'Praiseworthy', 'غني': 'Self-sufficient',
           'راف': 'Kind', 'توب': 'Relenting', 'حلم': 'Forbearing', 'كرم': 'Generous', 'شكر': 'Appreciative', 'ودد': 'Loving',
           'مجد': 'Glorious', 'لطف': 'Subtle', 'قوي': 'Strong', 'عفو': 'Pardoning', 'وسع': 'Vast', 'شهد': 'Witness',
           'رقب': 'Watchful', 'وكل': 'Trustee', 'حفظ': 'Guardian', 'قهر': 'Irresistible', 'ولي': 'Protector', 'نصر': 'Helper',
           'قرب': 'Near', 'جيب': 'Responsive', 'حسب': 'Reckoner', 'كبر': 'Great', 'علو': 'Most High', 'عظم': 'Magnificent'}

def endings(words, V, perms=2000):
    roots = set(map(normalize, NAME_ROOTS))
    rows = []
    for (s, a), W in V.items():
        if len(W) < 4: continue
        x, z = W[-2], W[-1]
        if x['pos'] != 'N' or z['pos'] != 'N' or not x['root'] or not z['root']: continue
        r1, r2 = normalize(x['root']), normalize(z['root'])
        if r1 in roots and r2 in roots and r1 != r2 and r1 != normalize('قوم'):
            rows.append({'s': s, 'a': a, 'end': (r1, r2), 'W': W, 'lem': (x['lemma'], z['lemma'])})
    cnt = Counter(r['end'] for r in rows)
    keep = {e for e, c in cnt.items() if c >= 8}
    rows = [r for r in rows if r['end'] in keep]
    classes = sorted(keep, key=lambda e: (-cnt[e], e))   # ties in order of the roots, so the output does not depend on hashing
    cidx = {e: i for i, e in enumerate(classes)}
    y = np.array([cidx[r['end']] for r in rows]); groups = np.array([r['s'] for r in rows])
    clf = LogisticRegression(max_iter=3000, C=3.0); cv = SurahFolds(5)

    def docs(drop):
        """Each verse's lemmas before its last two words, leaving out the words whose root is in drop[i]."""
        return [' '.join(w['lemma'] for w in r['W'][:-2] if w['lemma'] and normalize(w['root'] or '') not in d) or 'EMPTY'
                for r, d in zip(rows, drop)]
    tfidf = lambda ds: TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2).fit_transform(ds)
    accuracy = lambda X, yy: float((cross_val_predict(clf, X, yy, cv=cv, groups=groups) == yy).mean())
    by_s = defaultdict(list)
    for i, s in enumerate(groups): by_s[s].append(i)
    def nulls(stat):
        """Test A (endings shuffled across all verses, seed 7) and test B (within each surah, seed 8)."""
        rng = np.random.default_rng(7); A = [stat(rng.permutation(y)) for _ in range(perms)]
        rng = np.random.default_rng(8); B = []
        for _ in range(perms):
            yy = y.copy()
            for idx in by_s.values(): yy[idx] = y[rng.permutation(idx)]
            B.append(stat(yy))
        return A, B

    # The pre-registered features leave out the roots of each verse's own ending, so they depend on the ending: every
    # shuffle rebuilds them from the shuffled endings. (The first version kept them fixed, which set chance a little
    # too low; found in review after publication, see the plan's «Corrections after publication».)
    feats = lambda yy: tfidf(docs([classes[k] for k in yy]))
    X = feats(y)
    proba = cross_val_predict(clf, X, y, cv=cv, groups=groups, method='predict_proba')
    pred = proba.argmax(1); acc = float((pred == y).mean())
    nullA, nullB = nulls(lambda yy: accuracy(feats(yy), yy))
    pA, pB = _pval(nullA, acc), _pval(nullB, acc)
    adjA, adjB = _holm([pA, pB])
    # Check: the roots of all the kept endings left out of every verse alike, so the input never depends on the ending
    fixed = sorted(set(r for e in classes for r in e))
    XF = tfidf(docs([set(fixed)] * len(rows)))
    accF = accuracy(XF, y)
    fA, fB = nulls(lambda yy: accuracy(XF, yy))
    robust = [{'what': 'the same roots left out of every verse', 'roots': fixed, 'accuracy': round(accF, 4),
               'nullAll': _summ(fA, accF), 'pAll': round(_pval(fA, accF), 4), 'nullWithin': _summ(fB, accF), 'pWithin': round(_pval(fB, accF), 4),
               'pHolm': [round(v, 4) for v in _holm([_pval(fA, accF), _pval(fB, accF)])], 'perms': perms}]
    # What each ending listens to (exploratory): from a model fitted on all the verses with those roots left out of every
    # verse, so no word can look telling just because it was left out of one ending's verses
    vec = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2); M = vec.fit_transform(docs([set(fixed)] * len(rows)))
    full = LogisticRegression(max_iter=3000, C=3.0).fit(M, y); vocab = np.array(vec.get_feature_names_out())
    lem_of = defaultdict(Counter)
    for r in rows: lem_of[r['end']][r['lem']] += 1
    pairs = []
    for e in classes:
        i = cidx[e]; m = y == i
        pairs.append({'roots': list(e), 'ar': ' '.join(lem_of[e].most_common(1)[0][0]), 'en': ', '.join(NAME_EN.get(r, r) for r in e),
                      'n': int(m.sum()), 'recall': round(float((pred[m] == i).mean()), 3),
                      'top': [str(t) for t in vocab[np.argsort(full.coef_[i])[-8:][::-1]]]})
    ptrue = proba[np.arange(len(y)), y]
    surprising = [{'k': f"{rows[i]['s']}:{rows[i]['a']}", 'end': int(y[i]), 'expected': int(pred[i]), 'p': round(float(ptrue[i]), 3)}
                  for i in np.argsort(ptrue, kind="stable")[:15]]   # ties (a refrain repeats the same verse) in mushaf order
    return {'nVerses': len(rows), 'nSurahs': int(len(set(groups))), 'nAllNameEndings': int(sum(cnt.values())),
            'accuracy': round(acc, 4), 'baseline': round(float(np.bincount(y).max() / len(y)), 4),
            'nullAll': _summ(nullA, acc), 'pAll': round(pA, 4), 'nullWithin': _summ(nullB, acc), 'pWithin': round(pB, 4),
            'pHolm': [round(adjA, 4), round(adjB, 4)], 'verdict': 'holds' if max(adjA, adjB) < ALPHA else ('mixed' if min(adjA, adjB) < ALPHA else 'does not hold'),
            'robust': robust, 'pairs': pairs, 'surprising': surprising,
            'confusion': [[int(((y == i) & (pred == j)).sum()) for j in range(len(classes))] for i in range(len(classes))],
            'verses': [[f"{r['s']}:{r['a']}", int(y[i]), int(pred[i])] for i, r in enumerate(rows)]}


# ---------------------------------------------------------------- 2. ring composition
def _mirror_stat(Sim, order=None):
    S = Sim if order is None else Sim[np.ix_(order, order)]
    n = S.shape[0]
    iu = np.triu_indices(n, 1); d = iu[1] - iu[0]; vals = S[iu]
    far = vals[d > 20].mean() if (d > 20).any() else 0.0
    e = np.full(n, far)
    for dd in range(1, min(21, n)):
        e[dd] = vals[d == dd].mean()
    i = np.arange(n); j = n - 1 - i; m = (j - i) >= 2
    i, j = i[m], j[m]
    return float((S[i, j] - e[j - i]).mean()) if len(i) else 0.0, e

def _profile(Sim, e, min_pairs=30):
    n = Sim.shape[0]; out = []
    for tot in range(2, 2 * n - 3):                      # i + j = tot (0-based); centre = tot/2
        i = np.arange(max(0, tot - (n - 1)), tot // 2 + 1); j = tot - i; m = (j - i) >= 2
        i, j = i[m], j[m]
        if len(i) >= min_pairs:
            out.append([round(tot / 2 + 1, 1), round(float((Sim[i, j] - e[np.minimum(j - i, len(e) - 1)]).mean()), 5)])
    return out

def rings(V, keys, X, meta):
    pos = {k: i for i, k in enumerate(keys)}
    def surah_sim(s):
        idx = [pos[k] for k in keys if k[0] == s]
        A = X[idx]; return (A @ A.T).toarray()
    def test(s):
        Sim = surah_sim(s); n = Sim.shape[0]
        obs, e = _mirror_stat(Sim)
        null = [_mirror_stat(Sim, np.roll(np.arange(n), -k))[0] for k in range(1, n)]
        return obs, float((np.sum(np.array(null) >= obs) + 1) / n), null, Sim, e
    obs, p, null, Sim, e = test(2)
    prof = _profile(Sim, e)
    n2 = Sim.shape[0]; ii, jj = np.meshgrid(np.arange(n2), np.arange(n2), indexing='ij'); dd = np.abs(ii - jj)
    R = Sim - e[np.minimum(dd, len(e) - 1)]; R[dd == 0] = 0.0
    B = 4; nb = -(-n2 // B); mat = []
    for a in range(nb):
        row = []
        for b in range(nb):
            blk, off = R[a * B:(a + 1) * B, b * B:(b + 1) * B], dd[a * B:(a + 1) * B, b * B:(b + 1) * B] > 0
            row.append(int(round(float(blk[off].mean()) * 1000)) if off.any() else 0)
        mat.append(row)
    peak = max(prof, key=lambda r: r[1]) if prof else None
    scan = []
    for m in meta:
        if m['verses'] >= 60:
            o, pp, _, _, _ = test(m['n'])
            scan.append({'n': m['n'], 'verses': m['verses'], 'stat': round(o, 5), 'p': round(pp, 4)})
    keep = _bh([r['p'] for r in scan], 0.10)
    for r, k in zip(scan, keep): r['bh'] = bool(k)
    return {'baqara': {'stat': round(obs, 5), 'p': round(p, 4), 'null': _summ(null, obs), 'rotations': len(null), 'matrix': mat, 'block': B,
                       'verdict': 'holds' if p < ALPHA else 'does not hold',
                       'profile': prof, 'peak': peak, 'peakInClaimedZone': bool(peak and 130 <= peak[0] <= 160)},
            'scan': scan}


# ---------------------------------------------------------------- 2b. the mirror claims, one by one (addendum)
# Written down in the plan's «Addendum A: the mirror claims, told apart» before these were run. Three claims are told apart:
# a ring of sections around the qibla passage, the observation that 2:143 («a middle nation») is the surah's middle
# verse, and a mirror inside Ayat al-Kursi (2:255). None of them is the verse-by-verse test above.

# Ayat al-Kursi in nine statements, as word spans of 2:255 in the corpus (1-based, inclusive)
KURSI = [(1, 7), (8, 12), (13, 19), (20, 26), (27, 32), (33, 40), (41, 44), (45, 47), (48, 50)]
# Farrin's nine sections of al-Baqarah (see the plan for the source); the fifth is the centre
FARRIN = [(1, 20), (21, 39), (40, 103), (104, 141), (142, 152), (153, 177), (178, 253), (254, 284), (285, 286)]

def _cross_matchings(score, left, right):
    """Every way to pair the items before a centre with those after it; the mirror pairs the first with the last."""
    import itertools
    mirror = list(reversed(right))
    rows = [(list(m), float(sum(score(a, b) for a, b in zip(left, m)))) for m in itertools.permutations(right)]
    obs = next(t for m, t in rows if m == mirror)
    ge = int(sum(t >= obs - 1e-12 for m, t in rows))
    return {'obs': round(obs, 6), 'arrangements': len(rows), 'ge': ge, 'p': round(ge / len(rows), 4),
            'verdict': 'holds' if ge / len(rows) < ALPHA else 'does not hold',
            'best': round(max(t for m, t in rows), 6), 'parallel': round(next(t for m, t in rows if m == list(right)), 6)}

def middle_verse(words, V):
    """Where al-Baqarah's middle falls, by verses, words and letters, and where «وسطا» sits (descriptive)."""
    s2 = [w for w in words if w['sura'] == 2]
    n = len({w['aya'] for w in s2})
    at = next(i for i, w in enumerate(s2, 1) if w['aya'] == 143 and normalize(w['root'] or '') == 'وسط')
    tw = len(s2); lw = (tw + 1) // 2
    let = [len(re.findall('[ء-ي]', w['norm'])) for w in s2]; tl = sum(let)
    cum, mid_l_verse, wasat_l = 0, None, sum(let[:at - 1]) + 1
    for w, k in zip(s2, let):
        cum += k
        if mid_l_verse is None and cum >= tl / 2: mid_l_verse = w['aya']
    per = Counter(k[0] for k in V)
    occ = [{'k': f"{w['sura']}:{w['aya']}", 'form': w['surface'], 'of': per[w['sura']], 'at': round(w['aya'] / per[w['sura']], 3)}
           for w in words if normalize(w['root'] or '') == 'وسط']
    return {'verses': n, 'firstHalfEnds': n // 2, 'even': n % 2 == 0,
            'words': tw, 'wasatWord': at, 'wasatWordAt': round(at / tw, 4), 'midWords': [lw, lw + (1 - tw % 2)],
            'midWordVerse': s2[lw - 1]['aya'], 'letters': tl, 'wasatLetter': wasat_l, 'wasatLetterAt': round(wasat_l / tl, 4),
            'midLetterVerse': mid_l_verse, 'root': occ}

def kursi(words):
    """Ayat al-Kursi's nine statements: the roots each mirror pair shares, and how the mirror ranks among every way
    to pair statements 1–4 with 6–9 by shared roots (exploratory: the verse is the one the claim was read from)."""
    ws = [w for w in words if w['sura'] == 2 and w['aya'] == 255]
    assert len(ws) == 50 and KURSI[-1][1] == 50
    st = [ws[a - 1:b] for a, b in KURSI]
    roots = [sorted({normalize(w['root']) for w in x if w['root']}) for x in st]
    shared = lambda a, b: sorted(set(roots[a]) & set(roots[b]))
    res = _cross_matchings(lambda a, b: len(shared(a, b)), [0, 1, 2, 3], [5, 6, 7, 8]); res.pop('verdict')   # exploratory: no verdict
    return {'statements': [{'words': [[w['surface'], normalize(w['root'] or '')] for w in x], 'roots': r} for x, r in zip(st, roots)],
            'pairs': [{'a': a + 1, 'b': b + 1, 'shared': shared(a, b)} for a, b in [(0, 8), (1, 7), (2, 6), (3, 5)]],
            'centreShares': [{'with': j + 1, 'shared': shared(4, j)} for j in range(9) if j != 4 and shared(4, j)],
            'links': [[len(shared(a, b)) for b in range(9)] for a in range(9)], **res}

def farrin_sections(keys, X):
    """Farrin's sections as vocabulary: are the paired sections more alike than any other way of pairing the four
    before the centre with the four after it? (24 arrangements; the smallest possible p is 1/24.)"""
    pos = {k: i for i, k in enumerate(keys)}
    vec = []
    for a, b in FARRIN:
        v = np.asarray(X[[pos[(2, i)] for i in range(a, b + 1)]].sum(axis=0)).ravel()
        vec.append(v / (np.linalg.norm(v) or 1))
    C = np.array([[float(vec[i] @ vec[j]) for j in range(len(vec))] for i in range(len(vec))])
    res = _cross_matchings(lambda a, b: C[a, b], [0, 1, 2, 3], [5, 6, 7, 8])
    # each pair's cosine, and its partner's rank among the four sections after the centre (seen from the one before)
    ranks = [{'a': a + 1, 'b': b + 1, 'cos': round(float(C[a, b]), 4), 'rank': int(1 + sum(C[a, x] > C[a, b] for x in [5, 6, 7, 8]))}
             for a, b in [(0, 8), (1, 7), (2, 6), (3, 5)]]
    return {'sections': [list(x) for x in FARRIN], 'cos': [[round(float(v), 4) for v in r] for r in C], 'pairs': ranks, **res}

def mirror_claims(words, V, keys, X):
    return {'middle': middle_verse(words, V), 'kursi': kursi(words), 'farrin': farrin_sections(keys, X)}


# ---------------------------------------------------------------- 3. rhyme and topic change
LONG = set('اوي')
def rhyme_of(norm_last):
    t = norm_last
    if not t: return ''
    last = t[-1]; prev = t[-2] if len(t) > 1 else ''
    if last not in LONG and prev in LONG:
        return ('ا' if prev == 'ا' else 'و') + last
    return last

def _rhyme_test(keys, X, rh, w, perms, seed):
    """Mean topic change where the rhyme changes minus where it stays, and its within-surah shuffle null (w verses a side)."""
    by_s = defaultdict(list)
    for i, k in enumerate(keys): by_s[k[0]].append(i)
    change, chg, sur = [], [], []
    for s, idx in by_s.items():
        n = len(idx)
        for b in range(w - 1, n - w):                   # boundary after verse b (0-based): b-w+1..b | b+1..b+w
            L = np.asarray(X[idx[b - w + 1:b + 1]].sum(0)); R = np.asarray(X[idx[b + 1:b + 1 + w]].sum(0))
            change.append(1 - _cos(L, R)); chg.append(rh[keys[idx[b]]] != rh[keys[idx[b + 1]]]); sur.append(s)
    change, chg, sur = np.array(change), np.array(chg), np.array(sur)
    stat = lambda c: float(change[c].mean() - change[~c].mean())
    obs = stat(chg)
    groups = defaultdict(list)
    for i, s in enumerate(sur): groups[s].append(i)
    rng = np.random.default_rng(seed); null = []
    for _ in range(perms):
        c = chg.copy()
        for idx in groups.values(): c[idx] = chg[rng.permutation(idx)]
        null.append(stat(c))
    return obs, null, change, chg, sur

def rhyme(V, keys, X, meta, perms=2000):
    place = {m['n']: m['place'] for m in meta}
    rh = {k: rhyme_of(W[-1]['norm']) for k, W in V.items()}
    obs, null, change, chg, sur = _rhyme_test(keys, X, rh, 3, perms, 11)
    p = _pval(null, obs)
    robust = []                                         # exploratory: the same test with 2 and 4 verses a side
    for w, seed in ((2, 111), (4, 112)):
        o2, n2, _, _, _ = _rhyme_test(keys, X, rh, w, 1000, seed)
        robust.append({'window': w, 'stat': round(o2, 4), 'p': round(_pval(n2, o2), 4), 'perms': 1000})
    split = {}
    for pl in ('Mecca', 'Medina'):
        m = np.array([place[s] == pl for s in sur])
        split[pl] = {'boundaries': int(m.sum()), 'changed': int((chg & m).sum()),
                     'diff': round(float(change[chg & m].mean() - change[~chg & m].mean()), 4) if (chg & m).any() and (~chg & m).any() else None}
    shares = Counter(rh.values())
    runs, cur = [], None
    for k in keys:
        if cur and cur['s'] == k[0] and cur['r'] == rh[k]: cur['end'] = k[1]; cur['len'] += 1
        else:
            if cur: runs.append(cur)
            cur = {'s': k[0], 'start': k[1], 'end': k[1], 'r': rh[k], 'len': 1}
    runs.append(cur)
    return {'stat': round(obs, 4), 'p': round(p, 4), 'null': _summ(null, obs), 'verdict': 'holds' if p < ALPHA else 'does not hold', 'robust': robust,
            'meanChanged': round(float(change[chg].mean()), 4), 'meanSame': round(float(change[~chg].mean()), 4),
            'boundaries': int(len(chg)), 'changes': int(chg.sum()), 'split': split,
            'shares': [[r, c] for r, c in shares.most_common(12)], 'total': len(rh),
            'runs': sorted(runs, key=lambda r: -r['len'])[:12],
            'perVerse': [rh[k] for k in keys]}


# ---------------------------------------------------------------- 4. retold stories
PROPHETS = [('Moses', 'موسى', ['موسي', 'فرعون']), ('Abraham', 'إبراهيم', ['ابراهيم']), ('Noah', 'نوح', ['نوح']), ('Lot', 'لوط', ['لوط']),
            ('Hud', 'هود', ['هود']), ('Salih', 'صالح', ['صالح']), ("Shu'ayb", 'شعيب', ['شعيب'])]

def _pn_verses():
    out = defaultdict(set)
    for r in _read_rows():
        f = r['feats'].split('|')
        if 'PN' in f:
            m = re.search(r'LEM:([^|]+)', r['feats'])
            if m: out[normalize(m.group(1))].add((r['sura'], r['aya']))
    return out

def retellings(V, keys, X, perms=5000):
    pn = _pn_verses(); pos = {k: i for i, k in enumerate(keys)}
    by_s = defaultdict(list)
    for k in keys: by_s[k[0]].append(k)
    tellings = {}
    for en, ar, lems in PROPHETS:
        vs = set().union(*[pn.get(l, set()) for l in lems])
        per = defaultdict(list)
        for k in sorted(vs): per[k[0]].append(k)
        T = {}
        for s, tv in per.items():
            if len(tv) < 3: continue
            near = {(s, a + d) for (_, a) in tv for d in range(-3, 4)}
            rest = [k for k in by_s[s] if k not in near]
            if not rest: continue
            T[s] = {'t': np.asarray(X[[pos[k] for k in tv]].sum(0)), 'r': np.asarray(X[[pos[k] for k in rest]].sum(0)), 'verses': [f'{k[0]}:{k[1]}' for k in tv]}
        if len(T) >= 5: tellings[en] = (ar, T)
    def stat(assign):
        diffs = []
        for en, (ar, T) in tellings.items():
            ss = list(T)
            for s in ss:
                own = assign[en][s]; others = [t for t in ss if t != own]
                diffs.append(_cos(T[s]['t'], T[own]['r']) - np.mean([_cos(T[s]['t'], T[o]['r']) for o in others]))
        return float(np.mean(diffs)), diffs
    ident = {en: {s: s for s in T} for en, (ar, T) in tellings.items()}
    obs, diffs = stat(ident)
    # cache cosines for speed
    rng = np.random.default_rng(13); null = []
    cache = {en: {(a, b): _cos(T[a]['t'], T[b]['r']) for a in T for b in T} for en, (ar, T) in tellings.items()}
    def fast(assign):
        d = []
        for en, (ar, T) in tellings.items():
            ss = list(T); C = cache[en]
            for s in ss:
                own = assign[en][s]
                d.append(C[(s, own)] - np.mean([C[(s, o)] for o in ss if o != own]))
        return float(np.mean(d))
    def derange(ss):
        while True:
            p = list(rng.permutation(ss))
            if all(a != b for a, b in zip(ss, p)): return dict(zip(ss, p))
    for _ in range(perms):
        null.append(fast({en: derange(list(T)) for en, (ar, T) in tellings.items()}))
    p = _pval(null, obs)
    per, each = {}, []
    for en, (ar, T) in tellings.items():
        ss = list(T); C = cache[en]
        d = [C[(s, s)] - np.mean([C[(s, o)] for o in ss if o != s]) for s in ss]
        per[en] = {'ar': ar, 'surahs': ss, 'mean': round(float(np.mean(d)), 4), 'own>others': int(sum(x > 0 for x in d)), 'n': len(ss)}
        for s in ss:
            each.append({'prophet': en, 's': s, 'verses': len(T[s]['verses']), 'first': T[s]['verses'][0],
                         'own': round(C[(s, s)], 4), 'others': round(float(np.mean([C[(s, o)] for o in ss if o != s])), 4)})
    # exploratory: the same test without Moses, whose tellings are the most numerous
    rest = {en: v for en, v in tellings.items() if en != 'Moses'}
    rng2 = np.random.default_rng(113); null2 = []
    def fast2(assign):
        d = []
        for en, (ar, T) in rest.items():
            ss = list(T); C = cache[en]
            for s in ss:
                own = assign[en][s]; d.append(C[(s, own)] - np.mean([C[(s, o)] for o in ss if o != own]))
        return float(np.mean(d))
    def derange2(ss):
        while True:
            q = list(rng2.permutation(ss))
            if all(a != b for a, b in zip(ss, q)): return dict(zip(ss, q))
    obs2 = fast2({en: {s: s for s in T} for en, (ar, T) in rest.items()})
    for _ in range(5000): null2.append(fast2({en: derange2(list(T)) for en, (ar, T) in rest.items()}))
    robust = [{'what': 'without Moses', 'tellings': sum(len(T) for ar, T in rest.values()), 'stat': round(obs2, 4), 'p': round(_pval(null2, obs2), 4), 'perms': 5000}]
    # Moses: each telling's most distinctive words (exploratory)
    moses = {}
    if 'Moses' in tellings:
        T = tellings['Moses'][1]
        docs = [' '.join(_content_doc(V[tuple(map(int, k.split(':')))]) for k in T[s]['verses']) for s in T]
        vec = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=1, sublinear_tf=True); M = vec.fit_transform(docs); voc = np.array(vec.get_feature_names_out())
        for row, s in enumerate(T):
            w = M[row].toarray().ravel(); moses[s] = {'verses': len(T[s]['verses']), 'first': T[s]['verses'][0], 'words': [str(t) for t in voc[np.argsort(w)[-6:][::-1]]]}
    return {'stat': round(obs, 4), 'p': round(p, 4), 'null': _summ(null, obs), 'verdict': 'holds' if p < ALPHA else 'does not hold',
            'tellings': sum(len(T) for ar, T in tellings.values()), 'prophets': per, 'each': each, 'robust': robust, 'moses': moses}


# ---------------------------------------------------------------- 5. themes
def themes(V, keys, X, vec, meta, k=12):
    nmf = NMF(n_components=k, init='nndsvda', random_state=0, max_iter=800); Wt = nmf.fit_transform(X); H = nmf.components_
    voc = np.array(vec.get_feature_names_out())
    Hn = H / (np.linalg.norm(H, axis=1, keepdims=True) + 1e-12)
    stab = np.zeros(k)
    for seed in range(1, 6):
        H2 = NMF(n_components=k, init='random', random_state=seed, max_iter=800).fit(X).components_
        H2 = H2 / (np.linalg.norm(H2, axis=1, keepdims=True) + 1e-12)
        stab += (Hn @ H2.T).max(1)
    stab /= 5
    dom = np.where(Wt.max(1) > 0, Wt.argmax(1), -1)
    out = []
    for t in range(k):
        out.append({'i': t, 'top': [str(w) for w in voc[np.argsort(H[t])[-10:][::-1]]], 'stability': round(float(stab[t]), 3),
                    'named': bool(stab[t] >= 0.8), 'share': round(float((dom == t).mean()), 4)})
    per_s = defaultdict(Counter)
    for key, d in zip(keys, dom): per_s[key[0]][int(d)] += 1
    mix = {s: [[t, c] for t, c in per_s[s].most_common(3)] for s in sorted(per_s)}
    return {'k': k, 'themes': out, 'perVerse': [int(d) for d in dom], 'surahMix': mix}


# ---------------------------------------------------------------- 6. words that travel together
def companions(V, keys, q=0.01, min_verses=20, top=8):
    sets = []
    root_of = {}
    for k in keys:
        s = set()
        for w in V[k]:
            if w['pos'] in ('N', 'V') and w['lemma'] and w['root']:
                s.add(w['lemma']); root_of[w['lemma']] = normalize(w['root'])
        sets.append(s)
    df = Counter(l for s in sets for l in s)
    L = sorted([l for l, c in df.items() if c >= min_verses], key=lambda l: -df[l]); ix = {l: i for i, l in enumerate(L)}
    N = len(sets); A = np.zeros((N, len(L)), dtype=np.uint8)
    for r, s in enumerate(sets):
        for l in s:
            if l in ix: A[r, ix[l]] = 1
    co = (A.T.astype(np.int32) @ A.astype(np.int32)); K = np.diag(co).astype(float)
    iu = np.triu_indices(len(L), 1)
    same = np.array([root_of[L[a]] == root_of[L[b]] for a, b in zip(*iu)])
    a, b = iu[0][~same], iu[1][~same]; c = co[a, b]
    p = stats.hypergeom.sf(c - 1, N, K[a], K[b])
    keep = _bh(p, q) & (c >= 3)
    pmi = np.log2(np.maximum(c, 1) * N / (K[a] * K[b]))
    out = defaultdict(list)
    for i in np.where(keep)[0]:
        out[L[a[i]]].append((float(pmi[i]), L[b[i]], int(c[i]))); out[L[b[i]]].append((float(pmi[i]), L[a[i]], int(c[i])))
    res = {l: [{'w': w, 'c': cc, 'pmi': round(pm, 2)} for pm, w, cc in sorted(out[l], reverse=True)[:top]] for l in L if out[l]}
    return {'lemmas': len(L), 'pairsTested': int(len(p)), 'significant': int(keep.sum()), 'q': q, 'minVerses': min_verses,
            'verses': {l: int(df[l]) for l in L}, 'companions': res}


# ---------------------------------------------------------------- 7. the opening letters
LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويةءؤئى')

def opening_letters(meta, words, perms=10000):
    rows = _read_rows(); inl = defaultdict(set); inl_pos = set()
    for r in rows:
        if 'INL' in r['feats']:
            inl[r['sura']] |= set(normalize(r['form'])); inl_pos.add((r['sura'], r['aya'], r['word']))
    inl = {s: sorted(l for l in ls if l in LETTERS) for s, ls in inl.items()}
    cnt = defaultdict(Counter)
    for w in words:
        if (w['sura'], w['aya'], w['word']) in inl_pos: continue
        for ch in w['norm']:
            if ch in LETTERS: cnt[w['sura']][ch] += 1
    S = sorted(cnt); share = {s: {ch: cnt[s][ch] / sum(cnt[s].values()) for ch in LETTERS} for s in S}
    def pct(s, ch):
        v = share[s][ch]; allv = np.array([share[t][ch] for t in S])
        return float(((allv < v).sum() + 0.5 * ((allv == v).sum() - 1) + 0.5) / len(S))
    cases = [(s, ch) for s in sorted(inl) for ch in inl[s]]
    obs = float(np.mean([pct(s, ch) for s, ch in cases]))
    P = {(s, ch): pct(s, ch) for s in S for ch in set(ch for _, ch in cases)}
    rng = np.random.default_rng(17); null = []
    lettered = sorted(inl)
    for _ in range(perms):
        tgt = rng.choice(S, size=len(lettered), replace=False)
        null.append(float(np.mean([P[(t, ch)] for s, t in zip(lettered, tgt) for ch in inl[s]])))
    p = _pval(null, obs)
    quran = Counter(); [quran.update(cnt[s]) for s in S]; qt = sum(quran.values())
    per = [{'s': s, 'letter': ch, 'share': round(share[s][ch], 5), 'quran': round(quran[ch] / qt, 5), 'pct': round(P[(s, ch)], 3)} for s, ch in cases]
    return {'cases': len(cases), 'meanPct': round(obs, 4), 'p': round(p, 4), 'null': _summ(null, obs),
            'verdict': 'holds' if p < ALPHA else 'does not hold', 'sets': {s: ''.join(inl[s]) for s in sorted(inl)}, 'perCase': per}

FAMILIES = {'الم': [2, 3, 29, 30, 31, 32], 'الر': [10, 11, 12, 14, 15], 'حم': [40, 41, 42, 43, 44, 45, 46], 'طسم': [26, 27, 28]}

def letter_families(words, meta, perms=10000):
    lem = defaultdict(list)
    for w in words:
        if w['lemma']: lem[w['sura']].append(w['lemma'])
    nums = sorted(lem)
    X = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2).fit_transform([' '.join(lem[n]) for n in nums])
    Sim = (X @ X.T).toarray(); ix = {n: i for i, n in enumerate(nums)}
    msim = lambda g: float(np.mean([Sim[ix[a], ix[b]] for i, a in enumerate(g) for b in g[i + 1:]]))
    place = {m['n']: m['place'] for m in meta}; wc = {m['n']: m['words'] for m in meta}
    qs = np.quantile([wc[n] for n in nums], [.25, .5, .75]); quart = {n: int(np.searchsorted(qs, wc[n], side='right')) for n in nums}
    pool = defaultdict(list)
    for n in nums: pool[(place[n], quart[n])].append(n)
    rng = np.random.default_rng(19)
    obs = {f: msim(g) for f, g in FAMILIES.items()}
    draws = {f: [] for f in FAMILIES}
    for _ in range(perms):
        for f, g in FAMILIES.items():
            pick, used = [], set()
            for m in g:
                cand = [c for c in pool[(place[m], quart[m])] if c not in used]
                c = int(rng.choice(cand)); used.add(c); pick.append(c)
            draws[f].append(msim(pick))
    mu = {f: float(np.mean(draws[f])) for f in FAMILIES}; sd = {f: float(np.std(draws[f])) for f in FAMILIES}
    z = {f: (obs[f] - mu[f]) / sd[f] for f in FAMILIES}
    zobs = float(np.mean(list(z.values())))
    zn = np.mean([(np.array(draws[f]) - mu[f]) / sd[f] for f in FAMILIES], axis=0)   # the same draws, all families at once
    p = _pval(zn, zobs)
    runs = {}
    for f in ('حم', 'طسم'):
        g = FAMILIES[f]; L = len(g); allruns = [msim(list(range(a, a + L))) for a in range(1, 115 - L + 1)]
        runs[f] = {'rank': int(sum(x > obs[f] for x in allruns) + 1), 'of': len(allruns)}
    return {'families': {f: {'surahs': g, 'sim': round(obs[f], 4), 'nullMean': round(float(np.mean(draws[f])), 4), 'z': round(float(z[f]), 2)} for f, g in FAMILIES.items()},
            'meanZ': round(zobs, 3), 'p': round(p, 4), 'null': _summ(zn, zobs), 'verdict': 'holds' if p < ALPHA else 'does not hold', 'consecutive': runs}


# ---------------------------------------------------------------- 8. near-repeated verses
def near_repeats(V, keys, ratio=0.8):
    seqs = [[w['lemma'] or w['norm'] for w in V[k]] for k in keys]
    norms = [' '.join(w['norm'] for w in V[k]) for k in keys]
    groups = defaultdict(list)
    for k, t, s in zip(keys, norms, seqs):
        if len(s) >= 4: groups[t].append(k)
    refrains = sorted([{'text': t, 'verses': [f'{k[0]}:{k[1]}' for k in ks], 'n': len(ks)} for t, ks in groups.items() if len(ks) > 1], key=lambda r: -r['n'])
    # candidates: similar length and enough shared lemmas (a bound the ratio cannot beat), then the exact ratio.
    # The ratio 2M/(|a|+|b|) needs M >= 0.4(|a|+|b|) matched words, and M is at most the sum of tf_a * tf_b.
    from scipy.sparse import csr_matrix
    voc = {}; rowsI, colsI, vals = [], [], []
    for i, s in enumerate(seqs):
        for l, c in Counter(s).items():
            rowsI.append(i); colsI.append(voc.setdefault(l, len(voc))); vals.append(c)
    tf = csr_matrix((vals, (rowsI, colsI)), shape=(len(seqs), len(voc)), dtype=np.float32)
    lens = np.array([len(s) for s in seqs]); pairs = []
    for start in range(0, len(seqs), 400):
        P = (tf[start:start + 400] @ tf.T).toarray()
        for r in range(P.shape[0]):
            i = start + r
            if lens[i] < 4: continue
            js = np.where((P[r] >= 0.4 * (lens[i] + lens)) & (np.arange(len(seqs)) > i) & (lens >= 4))[0]
            for j in js:
                lo, hi = sorted((lens[i], lens[j]))
                if lo / hi < 2 / 3 or norms[i] == norms[j]: continue
                sm = difflib.SequenceMatcher(None, seqs[i], seqs[j], autojunk=False); rt = sm.ratio()
                if rt >= ratio:
                    # the words that differ, shown as written (two verses can share every lemma and still differ in form)
                    wa, wb = [w['norm'] for w in V[keys[i]]], [w['norm'] for w in V[keys[j]]]
                    ops = [o for o in difflib.SequenceMatcher(None, wa, wb, autojunk=False).get_opcodes() if o[0] != 'equal']
                    pairs.append({'a': f'{keys[i][0]}:{keys[i][1]}', 'b': f'{keys[j][0]}:{keys[j][1]}', 'ratio': round(rt, 3),
                                  'diffA': [[a1, a2] for _, a1, a2, _, _ in ops], 'diffB': [[b1, b2] for _, _, _, b1, b2 in ops]})
    pairs.sort(key=lambda p: (-p['ratio'], p['a']))
    return {'refrains': refrains, 'pairs': pairs, 'nPairs': len(pairs), 'nRefrains': len(refrains),
            'refrainVerses': sum(r['n'] for r in refrains)}


# ---------------------------------------------------------------- 9. style over the order of revelation
def rev_order():
    src = open(os.path.join(HERE, '..', '..', 'scripts', 'enrich_quran_corpus.py'), encoding='utf-8').read()
    m = re.search(r'REV_ORDER = (\{.*?\})', src, re.S)
    return {int(k): int(v) for k, v in ast.literal_eval(m.group(1)).items()}

def chronology(words, meta, perms=10000):
    R = rev_order(); place = {m['n']: m['place'] for m in meta}
    assert sorted(R) == list(range(1, 115)) and sorted(R.values()) == list(range(1, 115)), 'not a permutation'
    assert {s for s, r in R.items() if r >= 87} == {s for s, p in place.items() if p == 'Medina'}, 'Medinan block mismatch'
    mlen = {m['n']: m['words'] / m['verses'] for m in meta}
    def sp(ns):
        x = np.array([R[n] for n in ns]); y = np.array([mlen[n] for n in ns])
        rho = stats.spearmanr(x, y).correlation
        rng = np.random.default_rng(23); null = [stats.spearmanr(rng.permutation(x), y).correlation for _ in range(perms)]
        return float(rho), float((np.sum(np.abs(null) >= abs(rho)) + 1) / (perms + 1)), null   # two-sided
    rho, p, null = sp(list(R)); rhoM, pM, _ = sp([n for n in R if place[n] == 'Mecca'])
    seen = set(); curve = []
    by_s = defaultdict(set)
    for w in words:
        if w['lemma']: by_s[w['sura']].add(w['lemma'])
    for s in sorted(R, key=R.get):
        seen |= by_s[s]; curve.append([R[s], s, len(seen)])
    phases = [('early Meccan', 1, 50), ('middle Meccan', 51, 75), ('late Meccan', 76, 86), ('early Medinan', 87, 100), ('late Medinan', 101, 114)]
    ph_of = {s: next(i for i, (_, a, b) in enumerate(phases) if a <= R[s] <= b) for s in R}
    lem_ph = defaultdict(set)
    for s, ls in by_s.items():
        for l in ls: lem_ph[l].add(ph_of[s])
    only = Counter(next(iter(v)) for v in lem_ph.values() if len(v) == 1)
    tot = Counter(ph for l, v in lem_ph.items() for ph in v)
    return {'rho': round(rho, 3), 'p': round(p, 4), 'null': _summ(null, rho), 'verdict': 'holds' if p < ALPHA else 'does not hold',
            'rhoMeccan': round(rhoM, 3), 'pMeccan': round(pM, 4),
            'points': [[R[m['n']], m['n'], round(mlen[m['n']], 2)] for m in meta], 'curve': curve,
            'phases': [{'name': n, 'from': a, 'to': b, 'own': int(only[i]), 'words': int(tot[i]), 'share': round(only[i] / tot[i], 3) if tot[i] else 0}
                       for i, (n, a, b) in enumerate(phases)]}


# ---------------------------------------------------------------- all together
def build(words, meta, log=None):
    import time
    V = _verses(words); keys, X, vec = _verse_matrix(V)
    studies = [('endings', lambda: endings(words, V)), ('rings', lambda: rings(V, keys, X, meta)),
               ('ringClaims', lambda: mirror_claims(words, V, keys, X)),
               ('rhyme', lambda: rhyme(V, keys, X, meta)), ('retellings', lambda: retellings(V, keys, X)),
               ('themes', lambda: themes(V, keys, X, vec, meta)), ('companions', lambda: companions(V, keys)),
               ('letters', lambda: opening_letters(meta, words)), ('families', lambda: letter_families(words, meta)),
               ('repeats', lambda: near_repeats(V, keys)), ('chronology', lambda: chronology(words, meta))]
    out = {'prereg': 'data-build/discover/PREREGISTRATION.md'}
    for name, fn in studies:
        t0 = time.time(); out[name] = fn()
        if log: log(f'{name}: {time.time() - t0:.0f}s')
    out['nVerses'] = len(keys)   # the per-verse lists run in mushaf order, one entry a verse
    return out

def write(out_dir, web_dir, log=None):
    """Run every study and write data-build/out/discoveries.json and web/discoveries.js (loaded when the Discoveries pages open)."""
    from .corpus import load_words
    from . import datasets as ds
    ws = load_words(); res = build(ws, ds.build(ws, None)['surahMeta'], log)
    save(res, out_dir, web_dir)
    return res

def save(res, out_dir, web_dir):
    """Write the results; out_dir (data-build/out) is not in the repository, so it is made here if missing."""
    import json
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'discoveries.json'), 'w', encoding='utf-8') as fh:
        json.dump(res, fh, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(web_dir, 'discoveries.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.DALEEL_DISCOVERIES = '); json.dump(res, fh, ensure_ascii=False, separators=(',', ':')); fh.write(';\n')

if __name__ == '__main__':
    import json, sys, time
    if sys.argv[1:] == ['--write']:
        base = os.path.join(HERE, '..')
        write(os.path.join(base, 'out'), os.path.join(base, '..', 'web'), lambda m: print(m, flush=True)); sys.exit(0)
    from .corpus import load_words
    from . import datasets as ds
    t = time.time(); ws = load_words(); meta = ds.build(ws, None)['surahMeta']
    only = sys.argv[1:] or None
    V = _verses(ws); keys, X, vec = _verse_matrix(V)
    runs = {'endings': lambda: endings(ws, V), 'rings': lambda: rings(V, keys, X, meta), 'ringClaims': lambda: mirror_claims(ws, V, keys, X), 'rhyme': lambda: rhyme(V, keys, X, meta),
            'retellings': lambda: retellings(V, keys, X), 'themes': lambda: themes(V, keys, X, vec, meta), 'companions': lambda: companions(V, keys),
            'letters': lambda: opening_letters(meta, ws), 'families': lambda: letter_families(ws, meta), 'repeats': lambda: near_repeats(V, keys),
            'chronology': lambda: chronology(ws, meta)}
    for name, fn in runs.items():
        if only and name not in only: continue
        t0 = time.time(); r = fn()
        slim = {k: v for k, v in r.items() if k not in ('perVerse', 'verses', 'surahMix', 'companions', 'curve', 'points', 'pairs', 'refrains', 'profile', 'perCase', 'moses')}
        print(f'== {name} ({time.time() - t0:.0f}s)'); print(json.dumps(slim, ensure_ascii=False)[:1500])
