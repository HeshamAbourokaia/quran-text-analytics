# -*- coding: utf-8 -*-
"""Pin the Discoveries results (web/discoveries.js) that the app's texts (web/discover.js) quote, and check that
the committed results still match the code and the corpus.

The permutation tests take minutes (study 1 refits its model 4,000 times), so this test does not rerun them:
it recomputes each study's observed statistic, which is fast and deterministic, and compares it with the
committed file, whose p-values and verdicts it pins. After changing a study, rebuild the file with
`python3 -m pipeline.discoveries --write` (from data-build) and update these numbers and the texts together.

Run:  python3 tests/test_discoveries.py      (or: pytest)
"""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.corpus import load_words, normalize
from pipeline import datasets as datasets_mod
from pipeline import discoveries as D

HERE = os.path.dirname(__file__)
with open(os.path.join(HERE, '..', '..', 'web', 'discoveries.js'), encoding='utf-8') as fh:
    _JS = fh.read()
assert _JS.startswith('window.DALEEL_DISCOVERIES = ')
R = json.loads(_JS[len('window.DALEEL_DISCOVERIES = '):].rstrip().rstrip(';'))

_WORDS = load_words()
_META = datasets_mod.build(_WORDS, None)['surahMeta']
_V = D._verses(_WORDS)
_KEYS, _X, _VEC = D._verse_matrix(_V)

def test_plan_is_there():
    assert R['prereg'] == 'data-build/discover/PREREGISTRATION.md'
    assert os.path.exists(os.path.join(HERE, '..', 'discover', 'PREREGISTRATION.md'))
    assert R['nVerses'] == 6236

def test_verdicts():
    assert R['endings']['verdict'] == 'holds'
    assert R['rings']['baqara']['verdict'] == 'does not hold' and not any(r['bh'] for r in R['rings']['scan'])
    assert R['ringClaims']['farrin']['verdict'] == 'does not hold'
    assert R['rhyme']['verdict'] == 'holds'
    assert R['retellings']['verdict'] == 'holds'
    assert R['letters']['verdict'] == 'does not hold'
    assert R['families']['verdict'] == 'holds'
    assert R['chronology']['verdict'] == 'holds'

def test_p_values_and_shuffles():
    e = R['endings']   # corrected on 30 Sep 2026: the shuffles rebuild the ending-dependent features (first published 0.001 / 0.004)
    assert (e['pAll'], e['pWithin'], e['pHolm']) == (0.001, 0.0075, [0.002, 0.0075])
    assert (e['nullAll']['n'], e['nullAll']['ge'], e['nullWithin']['ge']) == (2000, 1, 14)
    assert (round(e['nullAll']['mean'], 4), round(e['nullWithin']['mean'], 4)) == (0.2611, 0.2862)
    r = e['robust'][0]   # the check: the same roots left out of every verse, so the features never depend on the ending
    assert (r['accuracy'], r['pAll'], r['pWithin'], r['pHolm']) == (0.3565, 0.001, 0.002, [0.002, 0.002])
    assert (r['nullAll']['ge'], r['nullWithin']['ge'], r['perms']) == (1, 3, 2000)
    assert (R['rings']['baqara']['p'], R['rings']['baqara']['null']['ge'], R['rings']['baqara']['rotations']) == (0.2552, 72, 285)
    assert (R['rhyme']['p'], R['rhyme']['null']['ge']) == (0.0005, 0)
    assert (R['retellings']['p'], R['retellings']['null']['ge']) == (0.0002, 0)
    assert (R['letters']['p'], R['letters']['null']['ge']) == (0.0586, 585)
    assert (R['families']['p'], R['families']['null']['ge']) == (0.0091, 90)
    assert (R['chronology']['p'], R['chronology']['pMeccan']) == (0.0001, 0.0001)

def test_endings_as_quoted():
    got = D.endings(_WORDS, _V, perms=2)          # the permutation nulls are the committed ones
    e = R['endings']
    assert (got['nVerses'], got['nSurahs'], got['nAllNameEndings']) == (e['nVerses'], e['nSurahs'], e['nAllNameEndings']) == (230, 48, 395)
    assert got['accuracy'] == e['accuracy'] == 0.3565 and got['baseline'] == e['baseline'] == 0.3087
    assert [p['en'] for p in e['pairs']][:3] == ['Forgiving, Merciful', 'Mighty, Wise', 'Hearing, Knowing']
    assert e['pairs'][0]['recall'] == 0.803
    guess = {k: (t, p) for k, t, p in e['verses']}
    assert guess['5:38'] == guess['5:118'] == (1, 0)   # «Mighty, Wise» in the text, «Forgiving, Merciful» guessed
    r = got['robust'][0]
    assert r['accuracy'] == e['robust'][0]['accuracy'] == 0.3565 and r['roots'] == e['robust'][0]['roots'] and len(r['roots']) == 11
    # the telling words come from the model that never sees the names' roots, so none of them is from one of those roots
    name_lemmas = {w['lemma'] for w in _WORDS if normalize(w['root'] or '') in set(r['roots'])}
    assert [p['top'] for p in got['pairs']] == [p['top'] for p in e['pairs']]
    assert not [t for p in e['pairs'] for t in p['top'] if t in name_lemmas]

def test_save_makes_the_output_folder():
    # data-build/out is not in the repository, so writing the results must create it
    with tempfile.TemporaryDirectory() as tmp:
        out, web = os.path.join(tmp, 'out', 'nested'), os.path.join(tmp, 'web')
        os.makedirs(web)
        D.save({'prereg': 'x'}, out, web)
        assert json.load(open(os.path.join(out, 'discoveries.json'))) == {'prereg': 'x'}
        assert open(os.path.join(web, 'discoveries.js')).read() == 'window.DALEEL_DISCOVERIES = {"prereg":"x"};\n'

def test_rings_as_quoted():
    got = D.rings(_V, _KEYS, _X, _META)['baqara']
    assert got['stat'] == R['rings']['baqara']['stat'] == 0.00384
    assert got['peak'][0] == R['rings']['baqara']['peak'][0] == 231.0 and not got['peakInClaimedZone']
    assert len(R['rings']['scan']) == 38

def test_ring_claims_as_quoted():
    # the plan's addendum A: the three mirror claims, told apart (recomputed in full, since none needs shuffles)
    assert D.mirror_claims(_WORDS, _V, _KEYS, _X) == R['ringClaims']
    m = R['ringClaims']['middle']   # the middle verse: exact by verses in the Kufan count, not by words or letters
    assert (m['verses'], m['firstHalfEnds'], m['words'], m['wasatWord'], m['letters'], m['wasatLetter']) == (286, 143, 6116, 2518, 25899, 10662)
    assert (m['midWordVerse'], m['midLetterVerse'], m['wasatWordAt'], m['wasatLetterAt']) == (172, 171, 0.4117, 0.4117)
    assert [o['k'] for o in m['root']] == ['2:143', '2:238', '5:89', '68:28', '100:5']
    f = R['ringClaims']['farrin']   # Farrin's sections: pre-registered; 24 pairings, so p is at least 1/24
    assert (f['arrangements'], f['ge'], f['p'], f['verdict']) == (24, 6, 0.25, 'does not hold')
    assert (f['obs'], f['best'], f['parallel']) == (1.639613, 1.702161, 1.580252)
    assert [(p['cos'], p['rank']) for p in f['pairs']] == [(0.217, 4), (0.4133, 2), (0.5626, 1), (0.4466, 3)]
    k = R['ringClaims']['kursi']    # Ayat al-Kursi: exploratory, so no verdict
    assert 'verdict' not in k and (k['arrangements'], k['obs'], k['ge'], k['p'], k['parallel']) == (24, 2, 6, 0.25, 0)
    assert [p['shared'] for p in k['pairs']] == [[], [], ['ارض', 'سمو'], []] and k['centreShares'] == [{'with': 6, 'shared': ['علم']}]
    assert [len(s['words']) for s in k['statements']] == [7, 5, 7, 7, 6, 8, 4, 3, 3]

def test_rhyme_as_quoted():
    got = D.rhyme(_V, _KEYS, _X, _META, perms=2)
    r = R['rhyme']
    assert (got['stat'], got['meanChanged'], got['meanSame']) == (r['stat'], r['meanChanged'], r['meanSame']) == (0.0063, 0.889, 0.8827)
    assert (got['boundaries'], got['changes']) == (r['boundaries'], r['changes']) == (5674, 1566)
    assert [w['p'] for w in r['robust']] == [0.001, 0.001]
    assert r['shares'][0] == ['ون', 3052]

def test_retellings_as_quoted():
    got = D.retellings(_V, _KEYS, _X, perms=2)
    t = R['retellings']
    assert got['stat'] == t['stat'] == 0.0361 and got['tellings'] == t['tellings'] == 23
    assert sum(1 for x in t['each'] if x['own'] > x['others']) == 19
    assert (t['prophets']['Moses']['n'], t['prophets']['Abraham']['n']) == (14, 9)
    assert t['robust'][0]['p'] == 0.0002

def test_letters_and_families_as_quoted():
    got = D.opening_letters(_META, _WORDS, perms=2)
    assert got['meanPct'] == R['letters']['meanPct'] == 0.5426 and got['cases'] == 78
    pct = {(c['s'], c['letter']): c['pct'] for c in R['letters']['perCase']}
    assert (pct[(50, 'ق')], pct[(68, 'ن')], pct[(38, 'ص')]) == (0.969, 0.917, 0.741)
    fam = D.letter_families(_WORDS, _META, perms=2)
    assert {k: v['sim'] for k, v in fam['families'].items()} == {k: v['sim'] for k, v in R['families']['families'].items()}
    assert R['families']['meanZ'] == 1.178 and R['families']['consecutive'] == {'حم': {'rank': 24, 'of': 108}, 'طسم': {'rank': 11, 'of': 112}}

def test_maps_as_quoted():
    th = R['themes']
    assert th['k'] == 12 and [x['named'] for x in th['themes']].count(True) == 10
    c = R['companions']
    assert (c['lemmas'], c['pairsTested'], c['significant']) == (418, 86945, 1207)
    rp = R['repeats']
    assert (rp['nRefrains'], rp['refrainVerses'], rp['nPairs']) == (74, 208, 217) and rp['refrains'][0]['n'] == 31

def test_chronology_as_quoted():
    got = D.chronology(_WORDS, _META, perms=2)
    assert (got['rho'], got['rhoMeccan']) == (R['chronology']['rho'], R['chronology']['rhoMeccan']) == (0.669, 0.515)
    assert [round(p['share'], 3) for p in R['chronology']['phases']] == [0.323, 0.271, 0.146, 0.244, 0.213]

if __name__ == '__main__':
    tests = [(k, f) for k, f in sorted(globals().items()) if k.startswith('test_') and callable(f)]
    bad = 0
    for k, f in tests:
        try: f(); print('ok  ', k)
        except AssertionError as err: bad += 1; print('FAIL', k, err)
    print(f'{len(tests) - bad}/{len(tests)} passed'); sys.exit(1 if bad else 0)
