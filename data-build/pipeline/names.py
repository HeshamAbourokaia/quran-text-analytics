# -*- coding: utf-8 -*-
"""Name studies: every verse whose root carries one of God's Names, read as one body of text, and a du'a
built from those verses' own phrases. One engine here, one config module per Name: pipeline/rizq.py
(ar-Razzaq, root ر ز ق) and pipeline/wahhab.py (al-Wahhab, root و ه ب). The next Name is one more config.

From the Quranic Arabic Corpus morphology the engine reads, for the study's root:
  - every word with that root, its verse, its word position, its lemma and its verb tags;
  - who gives (the verb's subject from the person, voice and mood tags; nouns counted apart by lemma);
  - which other roots sit in the same verse far more often than in the rest of the Quran (log-odds with a
    smoothing prior of 0.5, as in Monroe, Colaresi and Quinn's "Fightin' Words", read as a z score);
  - the forms of the word (each written form, for the forms chart) and the phrases repeated word for word
    across the verses (for the formulas table), when the study's page shows them.
The config holds what a person decided after reading the verses: themes and their groups, conditions,
the prophetic du'as read span by span, the du'a itself, findings, and the page's own sentences in both
languages. The engine checks every hand label against the corpus and stops if one does not fit.

The du'a: each phrase names its source verses and the Quranic phrase it is built on (q, or the whole
phrase when it has no q). The mode is «text» when that Quranic phrase is found word for word in a source
verse and «shift» when it is not (a pronoun changed, or the words recast); «whole» says whether the phrase
exactly as shown stands in a source verse; kw flags each shown word as standing in a source verse as
written (1) or adapted (0), which the page underlines solid or dotted. Sources must be a study verse or a
verse within the config's window of one (CTX_WINDOW verses away, in the same surah).

The page reads the verse texts from corpus.js; a study's key holds positions, labels, the du'a and copy.
"""
import collections, math, re
from .corpus import _read_rows, load_verses, load_words
from .datasets import _surah_meta

# the standard Egyptian order of revelation (the 1924 Cairo edition): position -> surah number; 86 Meccan, then 28 Medinan
CHRONO = [96, 68, 73, 74, 1, 111, 81, 87, 92, 89, 93, 94, 103, 100, 108, 102, 107, 109, 105, 113, 114, 112, 53, 80, 97, 91, 85, 95, 106, 101,
          75, 104, 77, 50, 90, 86, 54, 38, 7, 72, 36, 25, 35, 19, 20, 56, 26, 27, 28, 17, 10, 11, 12, 15, 6, 37, 31, 34, 39, 40,
          41, 42, 43, 44, 45, 46, 51, 88, 18, 16, 71, 14, 21, 23, 32, 52, 67, 69, 70, 78, 79, 82, 84, 30, 29, 83,
          2, 8, 3, 33, 60, 4, 99, 57, 47, 13, 55, 76, 65, 98, 59, 24, 22, 63, 58, 49, 66, 64, 61, 62, 48, 5, 9, 110]

# ---------------------------------------------------------------- normalisation (Uthmani -> plain letters)
_MARKS = re.compile('[ؐ-ًؚ-ٟۖ-ۭـ࣓-ࣿ]')

def norm(s):
    """Plain letters from Uthmani text: wasla and dagger alif resolved, hamza seats, ة as ه, ى as ي."""
    s = s.replace('ٱ', 'ا')                              # alif wasla
    s = s.replace('وٰ', 'ا').replace('ىٰ', 'ي')     # Uthmani long vowels (ٱلصَّلَوٰةَ, عَلَىٰ)
    s = s.replace('ٰ', 'ا')                              # dagger alif elsewhere
    s = re.sub('ـ[ً-ْ]*ٔ[ً-ْ]*', 'ئ', s)   # hamza on a tatweel seat
    s = _MARKS.sub('', s)
    s = re.sub('[أإآ]', 'ا', s)
    s = s.replace('ءا', 'ا').replace('ة', 'ه').replace('ى', 'ي')
    for a, b in (('هاذ', 'هذ'), ('ذالك', 'ذلك'), ('اولائك', 'اولئك'), ('لاكن', 'لكن'),
                 ('الرحمان', 'الرحمن'), ('ابراهم', 'ابراهيم')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()

def _words(s):
    return [w for w in re.split(r'[\s،,.:؛]+', norm(s)) if w]

def _strip(w):
    return w[1:] if w[:1] in 'وف' else w

def _order(k):
    s, a = k.split(':')
    return int(s), int(a)

_PUNCT = re.compile('[،,.:؛]')

# ---------------------------------------------------------------- the corpus, read once for every study
_CORPUS = {}

def _read():
    """Verse texts in mushaf order, the roots in each verse, and every token of every root with its word position."""
    if not _CORPUS:
        verses = {f'{s}:{a}': t for (s, a), t in load_verses(load_words()).items()}
        roots = collections.defaultdict(list)
        tokens = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in _read_rows():
            key = f"{r['sura']}:{r['aya']}"
            feats = r['feats'].split('|')
            root = next((p[5:] for p in feats if p.startswith('ROOT:')), None)
            if not root:
                continue
            roots[key].append(root)
            lem = next((p[4:] for p in feats if p.startswith('LEM:')), None)
            tokens[root][key].append({'w': r['word'], 'form': r['form'], 'pos': r['pos'], 'lemma': lem,
                                      'tags': {p for p in feats if not p.startswith(('ROOT:', 'LEM:'))}})
        _CORPUS.update(verses=verses, roots=roots, tokens=tokens)
    return _CORPUS['verses'], _CORPUS['roots'], _CORPUS['tokens']

def _agent(tok, cfg):
    """Who gives, from the tags: a noun goes by its lemma; a verb by its voice, mood and person."""
    t = tok['tags']
    if tok['pos'] != 'V':
        for i, _, _, lemmas in cfg.NOUNS:
            if tok['lemma'] in lemmas:
                return i
        return 'other'
    if 'PASS' in t: return 'passive'
    if 'IMPV' in t and '2MS' in t: return 'ask'
    if 'IMPV' in t and '2MP' in t: return 'people'
    if '1P' in t: return 'we'
    if '3MS' in t: return 'he'
    if '2MS' in t: return 'you'
    for tag, i in getattr(cfg, 'AGENT_TAGS', {}).items():
        if tag in t:
            return i
    return 'other'

def _association(all_keys, roots, target, root, min_in):
    """Which roots come in the target verses more than in the rest: log-odds with a Dirichlet prior (alpha 0.5) and its z."""
    a, b = collections.Counter(), collections.Counter()
    for k in all_keys:
        (a if k in target else b).update(set(roots[k]) - {root})
    n1, n2, n = len(target), len(all_keys) - len(target), len(all_keys)
    rows = []
    for r in set(a) | set(b):
        x, y = a[r], b[r]
        if x < min_in:
            continue
        d = math.log((x + .5) / (n1 - x + .5)) - math.log((y + .5) / (n2 - y + .5))
        var = 1 / (x + .5) + 1 / (n1 - x + .5) + 1 / (y + .5) + 1 / (n2 - y + .5)
        rows.append({'root': r, 'n': x, 'rest': y, 'pct': round(100 * x / n1, 1), 'pctAll': round(100 * (x + y) / n, 1),
                     'lift': round((x / n1) / ((x + y) / n), 2), 'z': round(d / math.sqrt(var), 2)})
    rows.sort(key=lambda r: (-r['z'], r['root']))
    return rows

# ---------------------------------------------------------------- the du'a against its verses
def _span_core(words, core):
    """1-based positions of the core phrase inside the verse, or of it with a joined و / ف allowed on the first word."""
    ws = [norm(w) for w in words]
    target = norm(core).split()
    n = len(target)
    for strip in (False, True):
        for i in range(len(ws) - n + 1):
            seg = ws[i:i + n]
            if strip:
                seg, tgt = [_strip(x) for x in seg], [_strip(x) for x in target]
            else:
                tgt = target
            if seg == tgt:
                return list(range(i + 1, i + n + 1))
    return []

def _span_shift(words, text):
    """For an adapted phrase: the verse words that the du'a kept (three letters or more)."""
    bag = {_strip(x) for x in _words(text)}
    return [i for i, w in enumerate(words, 1) if _strip(norm(w)) in bag and len(_strip(norm(w))) > 2]

def _check(seg, verses, target, ctx, vocab):
    q = seg.get('q', seg['t'])
    nq = ' '.join(_PUNCT.sub(' ', norm(q)).split())
    hits = [k for k in seg['src'] if nq in norm(verses[k])]
    mode = 'text' if hits else 'shift'
    shown = seg['t'].split(' ')
    bag, bag_s = set(), set()
    for k in seg['src']:
        if k not in target and k not in ctx:
            raise ValueError(f"du'a source {k} is neither a study verse nor near one")
        for w in _words(verses[k]):
            bag.add(w); bag_s.add(_strip(w))
    def kept(w):
        n = norm(_PUNCT.sub('', w))
        return 1 if (n in bag or _strip(n) in bag_s) else 0
    kw = [kept(w) for w in shown]
    whole = any(_span_core(verses[k].split(), _PUNCT.sub(' ', seg['t'])) for k in seg['src'])
    src = []
    for k in seg['src']:
        words = verses[k].split()
        hi = set(_span_shift(words, seg['t']))
        if mode == 'text' and k in hits:
            hi |= set(_span_core(words, q))
        src.append({'k': k, 'ctx': k not in target, 'hi': sorted(hi)})
    ws = _words(seg['t'])
    def tier(w):
        for cand in (w, _strip(w) if w[:1] in 'وف' else None):
            if cand:
                for name in ('target', 'ctx', 'quran'):
                    if cand in vocab[name]:
                        return name
        return 'shift'
    out = {'t': seg['t'], 'mode': mode, 'whole': whole, 'kw': kw, 'src': src}
    if seg.get('en'):
        out['en'] = seg['en']
    return out, [tier(w) for w in ws]

def _summary(segs, tiers):
    n = len(segs)
    exact = sum(1 for s in segs if s['mode'] == 'text')
    tot = len(tiers)
    c = collections.Counter(tiers)
    shown = sum(len(s['kw']) for s in segs)
    kept = sum(sum(s['kw']) for s in segs)
    return {'segments': n, 'text': exact, 'shift': n - exact, 'whole': sum(1 for s in segs if s['whole']),
            'words': shown, 'kept': kept, 'pctKept': round(100 * kept / shown),
            'pctTarget': round(100 * c['target'] / tot), 'pctQuran': round(100 * (tot - c['shift']) / tot),
            'ctx': sorted({s['k'] for seg in segs for s in seg['src'] if s['ctx']}, key=_order)}

# ---------------------------------------------------------------- the formulas: phrases repeated word for word
def _formulas(keys, verses, stop, top):
    """Phrases of two to seven words found, after normalisation, in two or more of the verses. A phrase inside a
    longer one found in exactly the same verses is dropped. Each comes with its Uthmani wording from its first verse."""
    docs = {k: [norm(w) for w in verses[k].split()] for k in keys}
    found = collections.defaultdict(set)
    for k, ws in docs.items():
        for n in range(2, 8):
            for i in range(len(ws) - n + 1):
                found[' '.join(ws[i:i + n])].add(k)
    cands = {g: d for g, d in found.items() if len(d) >= 2}
    out = []
    for g, d in cands.items():
        if any(h != g and f' {g} ' in f' {h} ' and e == d for h, e in cands.items()):
            continue
        if all(w in stop for w in g.split()):
            continue
        ks = sorted(d, key=_order)
        ws, gw = docs[ks[0]], g.split()
        i = next(i for i in range(len(ws)) if ws[i:i + len(gw)] == gw)
        out.append({'t': g, 'u': ' '.join(verses[ks[0]].split()[i:i + len(gw)]), 'n': len(d), 'verses': ks})
    out.sort(key=lambda f: (-f['n'], -len(f['t'].split()), _order(f['verses'][0]), f['t']))
    return out[:top]

# the placeholders the page fills (counts that depend on the reader's choices); no build-time count may share these names
PAGE_FILLS = {'pctQuran', 'pctTarget', 'ctx', 'n', 'top', 'none', 'cnt', 'm', 'first', 'last'}

class _Keep(dict):
    """format_map helper: a placeholder the build does not know stays as it is, for the page to fill."""
    def __missing__(self, key):
        return '{' + key + '}'

def _pair(p, nums):
    en, ar = p
    return [en.format_map(nums), ar.format_map(nums)]

# ---------------------------------------------------------------- build one study
def build(cfg):
    verses, roots, tokens_by_root = _read()
    tokens = tokens_by_root[cfg.ROOT]
    all_keys = list(verses)
    keys = [k for k in all_keys if k in tokens]
    target = set(keys)
    meta = _surah_meta()
    period = lambda k: 'm' if meta[int(k.split(':')[0])]['p'] == 'Mecca' else 'd'
    sections = list(getattr(cfg, 'SECTIONS', []))

    if sorted(CHRONO) != list(range(1, 115)):
        raise ValueError('the order of revelation is not a permutation of the 114 surahs')
    theme_of = {}
    for i, th in enumerate(cfg.THEMES):
        ar, ks = th[0], th[2]
        if ar not in cfg.GROUP_OF_THEME: raise ValueError(f'theme {ar} has no group')
        for k in ks:
            if k not in target: raise ValueError(f'theme verse {k} has no {cfg.ROOT} word')
            if k in theme_of: raise ValueError(f'theme verse {k} labelled twice')
            theme_of[k] = i
    if set(theme_of) != target:
        raise ValueError(f'unlabelled verses: {sorted(target - set(theme_of), key=_order)}')

    win = getattr(cfg, 'CTX_WINDOW', 1)
    ctx = set()
    for k in keys:
        s, a = _order(k)
        for d in range(-win, win + 1):
            kk = f'{s}:{a + d}'
            if d and kk in verses and kk not in target:
                ctx.add(kk)
    vocab = {'target': {w for k in target for w in _words(verses[k])},
             'ctx': {w for k in ctx for w in _words(verses[k])},
             'quran': {w for k in verses for w in _words(verses[k])}}

    # the du'a, each phrase checked
    full, tiers_f = [], []
    for ar, en, segs in cfg.FULL:
        out = []
        for seg in segs:
            s, t = _check(seg, verses, target, ctx, vocab)
            out.append(s); tiers_f += t
        full.append({'ar': ar, 'en': en, 'segs': out})
    short, tiers_s = [], []
    for seg in cfg.SHORT:
        s, t = _check(seg, verses, target, ctx, vocab)
        short.append(s); tiers_s += t
    flat_full = [s for p in full for s in p['segs']]

    # who gives
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    for k in keys:
        for tok in tokens[k]:
            lab = _agent(tok, cfg)
            counts[lab] += 1
            if len(examples[lab]) < 4:
                examples[lab].append(k)
    if counts['other']:
        raise ValueError(f'a {cfg.ROOT} word with no known subject or lemma')
    agents = [{'id': i, 'ar': ar, 'en': en, 'n': counts[i], 'ex': examples[i]} for i, ar, en in cfg.AGENTS]
    nouns = [{'id': i, 'ar': ar, 'en': en, 'n': counts[i], 'ex': examples[i]} for i, ar, en, _ in cfg.NOUNS]
    shown_ids = {a['id'] for a in agents} | {x['id'] for x in nouns}
    if set(counts) - shown_ids:
        raise ValueError(f'subjects found but not shown: {sorted(set(counts) - shown_ids)}')

    # what sits with the root in the same verse
    assoc = []
    for r in _association(all_keys, roots, target, cfg.ROOT, getattr(cfg, 'MIN_IN', 3)):
        if r['root'] in cfg.GENERIC:
            continue
        g = cfg.GLOSS.get(r['root'])
        if not g: raise ValueError(f"root {r['root']} has no gloss")
        net_g = cfg.NET_GROUP_OF.get(r['root'], getattr(cfg, 'NET_DEFAULT', None))
        if net_g is None: raise ValueError(f"root {r['root']} has no network group")
        r.update({'ar': g[0], 'en': g[1], 'g': net_g, 'verses': [k for k in keys if r['root'] in roots[k]]})
        if len(r['verses']) != r['n']:
            raise ValueError(f"root {r['root']}: {len(r['verses'])} verses listed, {r['n']} counted")
        assoc.append(r)
        if len(assoc) == cfg.N_ASSOC:
            break

    models = []
    for k, ar, en, spans in cfg.MODELS:
        n = len(verses[k].split())
        if spans[-1][1] > n:
            raise ValueError(f'{k} has {n} words, span to {spans[-1][1]}')
        models.append({'k': k, 'ar': ar, 'en': en, 'spans': [list(s) for s in spans]})

    conditions = []
    for ar, en, ks, ev in cfg.CONDITIONS:
        for k in ks:
            if k not in target: raise ValueError(f'condition verse {k} has no {cfg.ROOT} word')
        conditions.append({'ar': ar, 'en': en, 'n': len(ks), 'verses': sorted(ks, key=_order), 'ev': ev})

    vs = [{'k': k, 'p': period(k), 't': theme_of[k], 'w': [t['w'] for t in tokens[k]]} for k in keys]
    surahs = {int(k.split(':')[0]) for k in keys}
    themes = []
    for th in cfg.THEMES:
        ar, en, ks = th[0], th[1], th[2]
        row = {'ar': ar, 'en': en, 'n': len(ks), 'mecca': sum(1 for k in ks if period(k) == 'm'), 'g': cfg.GROUP_OF_THEME[ar]}
        if len(th) > 3:
            row.update({'sar': th[3], 'sen': th[4]})
        themes.append(row)
    out = {
        'slug': cfg.SLUG, 'root': cfg.ROOT,
        'name': {'ar': cfg.NAME[0], 'en': cfg.NAME[1]}, 'title': {'ar': cfg.TITLE[0], 'en': cfg.TITLE[1]},
        'sections': sections, 'trans': bool(getattr(cfg, 'TRANS', False)),
        'totals': {'tokens': sum(len(v) for v in tokens.values()), 'verses': len(keys), 'surahs': len(surahs),
                   'mecca': sum(1 for v in vs if v['p'] == 'm'), 'medina': sum(1 for v in vs if v['p'] == 'd'),
                   'verbs': sum(a['n'] for a in agents), 'nouns': sum(x['n'] for x in nouns), 'quran': len(all_keys)},
        'themes': themes,
        'groups': [{'ar': ar, 'en': en} for ar, en in cfg.GROUPS],
        'netGroups': [{'ar': ar, 'en': en} for ar, en in cfg.NET_GROUPS],
        'chrono': list(CHRONO),
        'verses': vs,
        'agents': agents, 'nouns': nouns,
        'assoc': assoc,
        'conditions': conditions,
        'models': models,
        'dua': {'full': full, 'short': short,
                'sum': {'full': _summary(flat_full, tiers_f), 'short': _summary(short, tiers_s)}},
    }

    # the optional sections: each only when the study's page shows it
    nums = _Keep(out['totals'])
    nums.update({'rest': len(all_keys) - len(keys), 'n_assoc': len(assoc), 'allah': counts['we'] + counts['he']})
    nums.update({f'a_{a["id"]}': a['n'] for a in agents}); nums.update({f'n_{x["id"]}': x['n'] for x in nouns})
    if 'forms' in sections:
        fc, fv, fl, fu = collections.Counter(), collections.defaultdict(list), {}, {}
        for k in keys:
            ws = verses[k].split()
            for t in tokens[k]:
                f = norm(ws[t['w'] - 1]); fc[f] += 1; fl[f] = t['lemma']; fu.setdefault(f, ws[t['w'] - 1])
                if k not in fv[f]: fv[f].append(k)
        groups = {}
        for lem, (gar, gen, g) in cfg.LEMMA_GROUPS.items():
            groups.setdefault(g, {'ar': gar, 'en': gen, 'g': g})
        if set(fl.values()) - set(cfg.LEMMA_GROUPS):
            raise ValueError(f'lemmas with no form group: {set(fl.values()) - set(cfg.LEMMA_GROUPS)}')
        out['forms'] = [{'f': f, 'u': fu[f], 'n': c, 'g': cfg.LEMMA_GROUPS[fl[f]][2], 'verses': fv[f]} for f, c in sorted(fc.items(), key=lambda x: (-x[1], x[0]))]
        out['formGroups'] = [groups[g] for g in sorted(groups)]
        nums.update({'n_forms': len(fc)})
        for g in groups:
            nums[f'fg_{g}'] = sum(x['n'] for x in out['forms'] if x['g'] == g)
    if 'formulas' in sections:
        out['formulas'] = _formulas(keys, verses, cfg.FORMULA_STOP, cfg.N_FORMULAS)
    def refs_ok(ks, where, inside):
        for k in ks:
            if k not in verses: raise ValueError(f'{where}: {k} is not a verse')
            if inside and k not in target: raise ValueError(f'{where}: {k} is not a study verse')
    if 'findings' in sections:
        out['findings'] = []
        for tar, ten, bar, ben, ks in cfg.FINDINGS:
            refs_ok(ks, tar, False)
            out['findings'].append({'ar': tar, 'en': ten, 'bar': bar, 'ben': ben, 'verses': list(ks)})
    if 'objects' in sections:
        seen = collections.Counter(k for _, _, ks in cfg.OBJECTS for k in ks)
        if set(seen) != target or max(seen.values()) > 1:
            raise ValueError('the objects must place every study verse exactly once')
        out['objects'] = [{'ar': ar, 'en': en, 'n': len(ks), 'verses': sorted(ks, key=_order)} for ar, en, ks in cfg.OBJECTS]
    if 'adab' in sections:
        out['adab'] = []
        for tar, ten, ks, nar, nen in cfg.ADAB:
            refs_ok(ks, tar, True)
            out['adab'].append({'ar': tar, 'en': ten, 'verses': list(ks), 'nar': nar, 'nen': nen})
    if 'sankey' in sections:
        nums['n_dua_surahs'] = len({int(s['k'].split(':')[0]) for seg in flat_full for s in seg['src']})
    if PAGE_FILLS & set(nums):
        raise ValueError(f'a build count shares a name with a page placeholder: {PAGE_FILLS & set(nums)}')
    out['copy'] = {k: _pair(v, nums) if isinstance(v, tuple) else [_pair(p, nums) for p in v] for k, v in cfg.COPY.items()}
    return out
