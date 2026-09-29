# -*- coding: utf-8 -*-
"""Pin the numbers that the app's scientific explanations (web/explain.js) quote but the site does not
show elsewhere: effect sizes, medians, the PCA variance shares, the choice of K, the vocabulary's shape.
If the corpus or a method changes, these fail and the texts need updating with them.

Run:  python3 tests/test_methods.py      (or: pytest)
"""
import math, os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from pipeline.corpus import load_words
from pipeline import datasets as datasets_mod
from pipeline import analytics as analytics_mod

_WORDS = load_words()
_DS = datasets_mod.build(_WORDS, None)
_META = _DS['surahMeta']
_AN = analytics_mod.build(_WORDS, _META)
_LEM = Counter(w['lemma'] for w in _WORDS if w['lemma'])

def _features():
    """The Clusters page's four measurements, standardized as analytics.py does."""
    f = np.array([[m['words'] / m['verses'], m['verses'], m['words'], 1 if m['place'] == 'Medina' else 0] for m in _META], dtype=float)
    return StandardScaler().fit_transform(f)

def _verse_lengths():
    n = Counter((w['sura'], w['aya']) for w in _WORDS)
    med = {m['n'] for m in _META if m['place'] == 'Medina'}
    return (np.array([c for (s, a), c in n.items() if s not in med]), np.array([c for (s, a), c in n.items() if s in med]))

def test_overview_shape():
    words = sorted((m['words'] for m in _META), reverse=True)
    assert sum(words[:16]) / sum(words) >= .5 > sum(words[:15]) / sum(words)   # the 16 longest surahs hold half the words
    assert np.median([m['verses'] for m in _META]) == 39 and np.median([m['words'] for m in _META]) == 344
    assert sum(1 for w in _WORDS if not w['lemma']) == 857
    assert sum(1 for w in _WORDS if w['root']) == 50268

def test_vocabulary_is_heavy_tailed():
    f = sorted(_LEM.values(), reverse=True)
    assert len(f) == 4771
    assert round(sum(1 for x in f if x == 1) / len(f) * 100, 1) == 41.1            # occur once
    assert round(sum(1 for x in f if x < 10) / len(f) * 100, 1) == 82.2              # fewer than 10 times
    assert round(sum(f[:10]) / sum(f) * 100, 1) == 25.1                              # the 10 commonest cover a quarter
    x = [math.log(r) for r in range(1, 1001)]; y = [math.log(f[r - 1]) for r in range(1, 1001)]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    assert round(slope, 1) == -1.1                                                   # Zipf, ranks 1 to 1,000

def test_verse_length_by_place():
    mec, med = _verse_lengths()
    assert (len(mec), len(med)) == (4613, 1623)
    assert (np.median(mec), np.median(med)) == (8, 16)
    assert (round(mec.std(ddof=1), 1), round(med.std(ddof=1), 1)) == (7.4, 11.7)
    assert (mec.min(), mec.max(), med.min(), med.max()) == (1, 78, 1, 128)
    sp = math.sqrt(((len(mec) - 1) * mec.var(ddof=1) + (len(med) - 1) * med.var(ddof=1)) / (len(mec) + len(med) - 2))
    assert round((med.mean() - mec.mean()) / sp, 2) == 0.94                          # Cohen's d
    assert round(sp, 2) == 8.70

def test_verses_and_words_across_surahs():
    v = np.array([m['verses'] for m in _META], dtype=float); w = np.array([m['words'] for m in _META], dtype=float)
    assert round(np.corrcoef(v, w)[0, 1], 2) == 0.88
    assert round(np.corrcoef(np.log10(v), np.log10(w))[0, 1], 2) == 0.92
    assert round(np.polyfit(np.log10(v), np.log10(w), 1)[0], 2) == 1.28

def test_pca_variance_shares():
    ev = PCA().fit(_features()).explained_variance_ratio_
    assert [round(x * 100, 1) for x in ev] == [60.1, 29.9, 8.0, 2.0]

def test_four_groups_have_the_best_silhouette():
    xs = _features()
    sil = {k: silhouette_score(xs, KMeans(n_clusters=k, n_init=10, random_state=42).fit(xs).labels_) for k in range(2, 9)}
    assert max(sil, key=sil.get) == 4 and round(sil[4], 2) == 0.55

def test_clusters_as_described():
    rows = {}
    for c in _AN['clusters']:
        m = _META[c['n'] - 1]; r = rows.setdefault(c['cluster'], [0, 0])
        r[0] += 1; r[1] += m['place'] == 'Medina'
    assert sorted(map(tuple, rows.values())) == [(7, 5), (23, 23), (31, 0), (53, 0)]   # (surahs, of them Medinan)

def test_similarity_and_vocabulary():
    docs = {}
    for w in _WORDS:
        if w['lemma']: docs.setdefault(w['sura'], []).append(w['lemma'])
    x = TfidfVectorizer(token_pattern=r'[^ ]+', min_df=2).fit_transform([' '.join(docs[n]) for n in sorted(docs)])
    assert x.shape == (114, 2587)
    place = {m['n']: m['place'] for m in _META}
    same = sum(place[int(n)] == place[nb[0]['n']] for n, nb in _AN['similarity'].items())
    assert same == 100
    assert _AN['similarity']['2'][0] == {'n': 3, 's': 0.916}                        # Al-Baqarah's closest: Aal-Imran

if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    for fn in fns:
        fn(); print('PASS', fn.__name__)
    print(f'\n{len(fns)}/{len(fns)} tests passed')
