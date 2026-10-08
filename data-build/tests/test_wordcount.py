# -*- coding: utf-8 -*-
"""Pin the "How many words?" totals: the same text counted under each rule.

Run:  python3 tests/test_wordcount.py      (or: pytest)
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.wordcount import build, PARTS

_WC = build()
_N = {p: _WC['rules'][p]['n'] for p in PARTS}

def test_printed_total():
    assert _WC['base'] == 77429                       # the printed Madani mushaf, word between spaces

def test_rules_are_disjoint_and_add_up_to_the_segments():
    assert _WC['segments'] == 130030
    assert _WC['base'] + sum(_N[p] for p in PARTS if p != 'basmala') == 130030

def test_each_rule():
    assert _N == {'basmala': 448, 'voc': 361, 'haAttn': 8, 'ibnUmm': 1, 'fused': 562,
                  'particles': 19914, 'article': 8377, 'pronouns': 21380, 'small': 1998}

def test_published_totals():
    t = _WC['totals']
    assert t['modern'] == 77799        # يا 361 + ها 8 + ابن أم 1 = 370 more in modern spelling
    assert t['basmala'] == 77877       # 112 surah heads x 4 words
    assert t['everyPiece'] == 130030

def test_opening_letters():
    L = _WC['letters']
    assert (L['words'], L['letters']) == (30, 78)
    assert sum(L['bySurah']) == 30

def test_by_surah_sums():
    for p in PARTS:
        assert sum(_WC['rules'][p]['bySurah']) == _N[p], p

def test_samples_rebuild_the_verse():
    for smp in _WC['samples']:
        assert smp['words'], smp['k']
        for w in smp['words']:
            assert w[0][1] == '' or w[0][1] in PARTS

def test_example_pieces_join_back():
    for p in PARTS:
        if p == 'basmala':
            continue
        for e in _WC['rules'][p]['ex']:
            assert ''.join(t for t, _ in e['p']) == e['w'], (p, e['w'])
            assert len(e['p']) >= 2 and any(c for _, c in e['p']), (p, e['w'])
            assert all(t or c for t, c in e['p']), ('empty piece', p, e['w'])

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
