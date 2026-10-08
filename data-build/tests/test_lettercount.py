# -*- coding: utf-8 -*-
"""Pin the "How many letters?" totals: the same text counted under each rule.

Run:  python3 tests/test_lettercount.py      (or: pytest)
"""
import itertools, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.lettercount import build, total, tiles, count, RULES

_LC = build()
_N = {r: _LC['rules'][r]['n'] for r in RULES}

def test_printed_total():
    assert _LC['base'] == 325665                      # the letters page's count: written letters, no marks or tatweel
    assert sum(_LC['baseBySurah']) == 325665

def test_each_rule():
    assert _N == {'basmala': 2128, 'hamza': -3059, 'smallAlif': 6652, 'smallWawYa': 2252,
                  'shadda': 22678, 'tanween': 8893, 'names': 135}
    assert _LC['rules']['basmala']['with'] == {'smallAlif': 112, 'shadda': 336}

def test_first_mushaf_falls_between_two_early_counts():
    assert _LC['totals']['firstMushaf'] == 322606
    early = {x['id']: x['n'] for x in _LC['reported']}
    assert early == {'mujahid': 321180, 'ata': 323015, 'hammani': 340740}
    assert early['mujahid'] < _LC['totals']['firstMushaf'] < early['ata']

def test_no_rule_set_gives_an_early_count():
    totals = {total(_LC, c) for r in range(len(RULES) + 1) for c in itertools.combinations(RULES, r)}
    assert len(totals) == 128
    assert not totals & {x['n'] for x in _LC['reported']}

def test_by_surah_sums():
    for r in RULES:
        assert sum(_LC['rules'][r]['bySurah']) == _N[r], r

def test_tiles():
    assert count(tiles('ٱللَّهِ')) == 4 and count(tiles('ٱللَّهِ'), {'shadda'}) == 5
    assert count(tiles('ٱلرَّحْمَٰنِ'), {'smallAlif'}) == 7
    assert count(tiles('عَلَىٰ'), {'smallAlif'}) == 3                     # the small alif on ى adds nothing
    assert count(tiles('شَىْءٍ'), {'hamza'}) == 2 and count(tiles('شَىْءٍ'), {'tanween'}) == 4
    assert count(tiles('الٓمٓ', opening=True), {'names'}) == 9            # alif lam mim

def test_samples_add_up():
    for smp in _LC['samples']:
        assert smp['words'], smp['k']
        for on in ([], ['shadda'], ['hamza', 'tanween']):
            assert all(count(ts, on) >= 0 for ts in smp['words'])

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
