# -*- coding: utf-8 -*-
"""Pin the Rizq page: the counts of the root ر ز ق, who provides, what sits with provision, the nine
themes, and the du'a's traceability (which phrases are verbatim, which only change a pronoun, and
that every source is a rizq verse or the verse beside one).

Run:  python3 tests/test_rizq.py      (or: pytest)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.corpus import load_words, load_verses
from pipeline.rizq import build, norm, THEMES, CONDITIONS

_R = build()
_V = {f'{s}:{a}': t for (s, a), t in load_verses(load_words()).items()}
_RIZQ = {v['k'] for v in _R['verses']}
_POS = {v['k']: v['w'] for v in _R['verses']}

def _has_rizq(word):
    w = norm(word)
    return any(x in w for x in ('رزق', 'رازق', 'رزاق'))

def test_totals():
    assert _R['totals'] == {'tokens': 123, 'verses': 109, 'surahs': 44, 'mecca': 72, 'medina': 37, 'verbs': 61, 'nouns': 62, 'quran': 6236}
    assert len(_R['verses']) == 109 and sum(len(v['w']) for v in _R['verses']) == 123

def test_every_marked_word_is_a_rizq_word():
    for v in _R['verses']:
        words = _V[v['k']].split()
        for w in v['w']:
            assert 1 <= w <= len(words), (v['k'], w)
            assert _has_rizq(words[w - 1]), (v['k'], words[w - 1])

def test_themes_cover_the_verses_once():
    assert [t['n'] for t in _R['themes']] == [16, 17, 16, 18, 6, 4, 15, 13, 4]
    assert [t['mecca'] for t in _R['themes']] == [8, 17, 12, 11, 5, 4, 6, 8, 1]
    assert sum(t['n'] for t in _R['themes']) == 109
    labelled = [k for _, _, ks in THEMES for k in ks]
    assert len(labelled) == len(set(labelled)) == 109 and set(labelled) == _RIZQ

def test_who_provides():
    assert {a['id']: a['n'] for a in _R['agents']} == {'he': 26, 'we': 24, 'passive': 5, 'ask': 3, 'people': 2, 'you': 1}
    assert {a['id']: a['n'] for a in _R['nouns']} == {'rizq': 55, 'raziq': 6, 'razzaq': 1}
    ask = next(a for a in _R['agents'] if a['id'] == 'ask')
    assert ask['ex'] == ['2:126', '5:114', '14:37']           # the three prophetic du'as
    people = next(a for a in _R['agents'] if a['id'] == 'people')
    assert people['ex'] == ['4:5', '4:8']

def test_what_sits_with_rizq():
    top = [(r['root'], r['n'], r['rest']) for r in _R['assoc'][:5]]
    assert top == [('طيب', 15, 31), ('نفق', 16, 70), ('بسط', 10, 13), ('ثمر', 7, 15), ('قدر', 14, 107)]
    assert _R['assoc'][0]['z'] == 10.57 and _R['assoc'][0]['lift'] == 18.66 and _R['assoc'][0]['pctAll'] == 0.7
    assert len(_R['assoc']) == 16
    for r in _R['assoc']:
        assert len(r['verses']) == r['n'] and set(r['verses']) <= _RIZQ, r['root']
        assert r['ar'] != r['root'], r['root']                   # every shown root has a gloss

def test_conditions_point_at_rizq_verses():
    assert len(_R['conditions']) == len(CONDITIONS) == 15
    for c in _R['conditions']:
        assert c['n'] == len(c['verses']) >= 2 and set(c['verses']) <= _RIZQ, c['ar']

def test_models_read_whole_verses():
    for m in _R['models']:
        words = _V[m['k']].split()
        spans = m['spans']
        assert spans[0][0] >= 1 and spans[-1][1] <= len(words), m['k']
        assert all(a <= b for a, b, _, _ in spans) and all(spans[i][1] + 1 == spans[i + 1][0] for i in range(len(spans) - 1)), m['k']
        assert any(_has_rizq(w) for a, b, _, _ in spans for w in words[a - 1:b]), m['k']

def test_dua_traceability():
    S = _R['dua']['sum']
    assert {k: S['full'][k] for k in ('segments', 'text', 'shift', 'pctRizq', 'pctQuran')} == {'segments': 36, 'text': 20, 'shift': 16, 'pctRizq': 66, 'pctQuran': 86}
    assert {k: S['short'][k] for k in ('segments', 'text', 'shift', 'pctRizq', 'pctQuran')} == {'segments': 15, 'text': 10, 'shift': 5, 'pctRizq': 74, 'pctQuran': 90}
    assert S['full']['ctx'] == ['2:127', '65:2'] and S['short']['ctx'] == ['2:127']
    segs = [s for p in _R['dua']['full'] for s in p['segs']] + _R['dua']['short']
    assert [p['ar'] for p in _R['dua']['full']] == ['النداء', 'الثناء بأسماء الرزق', 'الإقرار: التوحيد والافتقار', 'الطلب بصيغ القرآن', 'العهد: ما قرنته الآيات بالرزق', 'الغاية والختم']
    for s in segs:
        assert s['mode'] in ('text', 'shift') and s['src']
        for src in s['src']:
            assert src['ctx'] == (src['k'] not in _RIZQ), src['k']
            words = _V[src['k']].split()
            assert all(1 <= i <= len(words) for i in src['hi']), (s['t'], src['k'])
    # a verbatim phrase lights its words in at least one source, and those words end where the phrase ends
    for s in segs:
        if s['mode'] != 'text':
            continue
        lit = [src for src in s['src'] if src['hi']]
        assert lit, s['t']
        words = _V[lit[0]['k']].split()
        shown = norm(' '.join(words[i - 1] for i in lit[0]['hi']))
        assert shown.split()[-1] in norm(s['t']), (s['t'], shown)

def test_page_content_rules():
    blob = json.dumps(_R, ensure_ascii=False)
    for ch in (chr(0x2014), chr(0x2013), chr(0x2212)):         # em dash, en dash, minus sign
        assert ch not in blob
    assert len(blob.encode()) < 32000                          # the key stays small: texts come from corpus.js

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
