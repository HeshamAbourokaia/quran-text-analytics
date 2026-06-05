# -*- coding: utf-8 -*-
"""Golden-file tests: pin the authoritative totals and every verified lemma count
so a future change to the corpus or engine cannot silently shift the numbers.

Run:  python3 tests/test_counts.py      (or: pytest)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.corpus import load_words, load_verses, normalize
from pipeline import claims as claims_mod

_WORDS = load_words()
_VN = {f"{s}:{a}": normalize(t) for (s, a), t in load_verses(_WORDS).items()}
_CLAIMS = {c['id']: c for c in claims_mod.compute(_WORDS, _VN)}

def test_totals():
    suras = {w['sura'] for w in _WORDS}
    verses = {(w['sura'], w['aya']) for w in _WORDS}
    assert len(suras) == 114
    assert len(verses) == 6236          # not the v1 bug of 6348
    assert len(_WORDS) == 77429          # not the v1 bug of 56108

# Verified lemma counts (authoritative, from the Quranic Arabic Corpus).
GOLDEN_LEMMA = {
    'day-365': 475,
    'month-12': 21,
    'devil-88': 88,      # exact match to the claim
    'angel-88': 88,      # exact - morphology separates malak from mulk/malik
    'hell-77': 77,       # exact
    'paradise-77': 147,
    'man-24': 29,
    'woman-24': 26,
    'jesus-24': 25,
    'adam-24': 25,
    'allah-2806': 2699,
    'rabb-846': 975,
}

def test_verified_lemma_counts():
    for cid, expected in GOLDEN_LEMMA.items():
        assert _CLAIMS[cid]['verifiedLemma'] == expected, \
            f"{cid}: got {_CLAIMS[cid]['verifiedLemma']} expected {expected}"

def test_exact_claims_really_match():
    for cid in ('devil-88', 'angel-88', 'hell-77'):
        c = _CLAIMS[cid]
        assert c['verifiedLemma'] == c['claimed'], f"{cid} should match exactly"

def test_jesus_equals_adam():
    assert _CLAIMS['jesus-24']['verifiedLemma'] == _CLAIMS['adam-24']['verifiedLemma'] == 25

if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print('PASS', fn.__name__)
    print(f'\n{passed}/{len(fns)} tests passed')
