# -*- coding: utf-8 -*-
"""Pin what the Name pages share: the heroes, the chart-form rule, and the comparison of Names (its measures, the
verses behind each side, and its sentences), and check that web/data.js holds exactly what the pipeline builds.

Run:  python3 tests/test_names.py      (or: pytest)
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline import names, rizq, wahhab
from pipeline.names import norm

_R, _W = rizq.build(), wahhab.build()
_C = names.compare([_R, _W])
_V = names._read()[0]
with open(os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'data.js'), encoding='utf-8') as fh:
    _JS = fh.read()
_D = json.loads(_JS[len('window.QURAN_DATA = '):].rstrip().rstrip(';'))

def test_data_file_matches_the_pipeline():
    assert _D['rizq'] == _R and _D['wahhab'] == _W and _D['names'] == _C

def test_rizq_hero_who_gives():
    assert _R['hero'] == {'type': 'agents', 'named': ['he', 'we', 'you']}
    A = {a['id']: a for a in _R['agents']}
    assert {i: a['n'] for i, a in A.items()} == {'he': 26, 'we': 24, 'passive': 5, 'ask': 3, 'people': 2, 'you': 1}
    assert sum(A[i]['n'] for i in ('he', 'we', 'you')) == 51 and sum(a['n'] for a in A.values()) == 61
    assert A['you']['verses'] == ['3:27'] and A['ask']['verses'] == ['2:126', '5:114', '14:37'] and A['people']['verses'] == ['4:5', '4:8']
    rv = {v['k'] for v in _R['verses']}
    assert all(set(a['verses']) <= rv and len(a['verses']) <= a['n'] for a in A.values())
    line = _R['copy']['heroLine'][0]
    for n in ('61', '50', '51', ' 1 ', '5 are passive', '3 are du', 'only 2'):
        assert n in line, n

def test_wahhab_hero_answers():
    H = _W['hero']
    assert H['type'] == 'duas' and H['window'] == 2
    got = [(d['k'], d['status'], d['ans'], d['cont']) for d in H['items']]
    assert got == [('3:8', 'open', None, ['3:9']), ('3:38', 'answered', '3:39', []), ('19:5', 'answered', '19:7', ['19:6']),
                   ('25:74', 'answered', '25:75', []), ('26:83', 'open', None, ['26:84', '26:85']),
                   ('37:100', 'answered', '37:101', []), ('38:35', 'answered', '38:36', [])]
    marks = {'3:39': 'يبشرك', '19:7': 'نبشرك', '25:75': 'يجزون', '37:101': 'فبشرناه', '38:36': 'فسخرنا'}
    for d in H['items']:
        if d['ans']:                                     # the answer's marked word is the word that answers
            ws = _V[d['ans']].split()
            assert [norm(ws[w - 1]) for w in d['ansW']] == [marks[d['ans']]], d['ans']
    assert _W['copy']['heroLine'][0].startswith('The Quran has 7 du’as') and '5 are answered' in _W['copy']['heroLine'][0] and '2 go on' in _W['copy']['heroLine'][0]

def test_the_chart_form_rule():
    assert _R['net'] == {'mode': 'ring', 'links': 18} and _W['net'] == {'mode': 'grid', 'links': 3}
    for R in (_R, _W):                                   # the rule: a ring when the roots link as often as there are roots
        rv = [set(r['verses']) for r in R['assoc']]
        links = sum(1 for i in range(len(rv)) for j in range(i + 1, len(rv)) if len(rv[i] & rv[j]) >= 2)
        assert R['net']['links'] == links and R['net']['mode'] == ('ring' if links >= len(rv) else 'grid')

def test_comparison_measures():
    assert _C['order'] == ['rizq', 'wahhab'] and _C['nouns'] == {'rizq': ['rizq', 'الرزق'], 'wahhab': ['hiba', 'الهبة']}
    keep = ('verses', 'tokens', 'mecca', 'verbs', 'nouns', 'named', 'ask', 'forms', 'formTop')
    assert {k: _C['sides']['rizq'][k] for k in keep} == {'verses': 109, 'tokens': 123, 'mecca': 72, 'verbs': 61, 'nouns': 62, 'named': 51, 'ask': 3, 'forms': 39, 'formTop': 'رِزْقًا'}
    assert {k: _C['sides']['wahhab'][k] for k in keep} == {'verses': 22, 'tokens': 25, 'mecca': 19, 'verbs': 22, 'nouns': 3, 'named': 13, 'ask': 7, 'forms': 11, 'formTop': 'وَوَهَبْنَا'}
    assert [r['root'] for r in _C['sides']['rizq']['roots']] == ['طيب', 'نفق', 'بسط'] and [r['root'] for r in _C['sides']['wahhab']['roots']] == ['ذرر', 'لدن', 'صلح']
    M = {m['id']: m for m in _C['measures']}
    assert list(M) == ['size', 'mecca', 'verbs', 'named', 'duas', 'roots', 'forms']
    assert {k: (len(m['verses']['rizq']), len(m['verses']['wahhab'])) for k, m in M.items()} == {
        'size': (109, 22), 'mecca': (72, 19), 'verbs': (60, 21), 'named': (51, 12), 'duas': (3, 7), 'roots': (40, 10), 'forms': (15, 8)}
    assert M['duas']['verses'] == {'rizq': ['2:126', '5:114', '14:37'], 'wahhab': ['3:8', '3:38', '19:5', '25:74', '26:83', '37:100', '38:35']}

def test_comparison_sentences_follow_the_numbers():
    M = {m['id']: m['line'] for m in _C['measures']}
    assert M['size'][0] == 'Rizq fills 109 verses and hiba 22: about 5 times as many.'
    assert M['mecca'][0] == 'Both are mostly Meccan, hiba more so: 86% against 66%.'
    assert M['verbs'][0].startswith('Hiba is almost always a verb (22 of 25 words); rizq is a verb about half the time (61 of 123)')
    assert '84%' in M['named'][0] and '59%' in M['named'][0] and '(7 of 9)' in M['named'][0]
    assert M['duas'][0] == 'Hiba is asked for directly in 7 du’as, rizq in 3, though rizq fills 5 times as many verses.'
    assert M['duas'][1].startswith('تُطلب الهبة') and M['size'][1].startswith('يملأ الرزق')     # the Arabic verb agrees with the noun
    for en, ar in M.values():
        assert en and ar and not re.search('[\u2013\u2014\u2212]', en + ar)     # no en dash, em dash or minus sign

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
