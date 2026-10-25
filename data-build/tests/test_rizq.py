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
    keys = ('segments', 'text', 'shift', 'whole', 'words', 'kept', 'pctKept', 'pctTarget', 'pctQuran')
    assert {k: S['full'][k] for k in keys} == {'segments': 36, 'text': 20, 'shift': 16, 'whole': 6, 'words': 237, 'kept': 136, 'pctKept': 57, 'pctTarget': 66, 'pctQuran': 86}
    assert {k: S['short'][k] for k in keys} == {'segments': 15, 'text': 10, 'shift': 5, 'whole': 7, 'words': 69, 'kept': 54, 'pctKept': 78, 'pctTarget': 74, 'pctQuran': 90}
    assert S['full']['ctx'] == ['2:127', '65:2'] and S['short']['ctx'] == ['2:127']
    segs = [s for p in _R['dua']['full'] for s in p['segs']] + _R['dua']['short']
    assert [p['ar'] for p in _R['dua']['full']] == ['النداء', 'الثناء بأسماء الرزق', 'الإقرار: التوحيد والافتقار', 'الطلب بصيغ القرآن', 'العهد: ما قرنته الآيات بالرزق', 'الغاية والختم']
    for s in segs:
        assert s['mode'] in ('text', 'shift') and s['src']
        shown = s['t'].split(' ')
        assert len(s['kw']) == len(shown) and set(s['kw']) <= {0, 1}, s['t']
        bag = {w for src in s['src'] for w in _V[src['k']].split()}
        bag = {norm(w) for w in bag} | {norm(w).lstrip('وف') for w in bag}
        for w, k in zip(shown, s['kw']):
            n = norm(w.strip('،,.:؛'))
            assert k == (1 if (n in bag or n.lstrip('وف') in bag) else 0), (s['t'], w)   # a solid underline means the word stands in a source verse
        if s['whole']:
            assert s['mode'] == 'text' and all(s['kw']), s['t']                             # a whole phrase is verbatim, so every word is kept
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
    assert len(blob.encode()) < 42000                          # the key stays small: verse texts come from corpus.js
    assert set(_R['copy']) >= {'lead', 'ctxNote', 'agentsAha', 'chronoAha'} and all(len(v) == 2 or isinstance(v[0], list) for v in _R['copy'].values())

def test_revelation_order():
    ch = _R['chrono']                                           # the standard Egyptian order: position -> surah
    assert len(ch) == 114 and sorted(ch) == list(range(1, 115))
    assert ch[0] == 96 and ch[85] == 83 and ch[86] == 2 and ch[-1] == 110   # 86 Meccan surahs (the last is 83), then the 28 Medinan
    from pipeline.datasets import _surah_meta
    meta = _surah_meta()
    assert all((i < 86) == (meta[s]['p'] == 'Mecca') for i, s in enumerate(ch))   # the order's split agrees with the corpus
    pos = {s: i + 1 for i, s in enumerate(ch)}
    by = sorted(_R['verses'], key=lambda v: (pos[int(v['k'].split(':')[0])], int(v['k'].split(':')[1])))
    assert by[0]['k'] == '89:16' and by[-1]['k'] == '5:114'   # the first rizq verse to come down, and the last

def test_surah_counts_behind_the_grid():
    import collections
    per = collections.Counter(int(v['k'].split(':')[0]) for v in _R['verses'])
    assert per.most_common(4) == [(2, 10), (16, 8), (22, 5), (34, 5)]
    assert len(per) == 44 and 114 - len(per) == 70

def test_groups_behind_the_chart_colours():
    assert [g['ar'] for g in _R['groups']] == ['الله هو الرازق', 'ما يُطلب من العبد', 'رزق الآخرة']
    assert [t['g'] for t in _R['themes']] == [1, 0, 0, 1, 0, 1, 2, 1, 1]
    assert [sum(t['n'] for t in _R['themes'] if t['g'] == g) for g in range(3)] == [39, 55, 15]
    assert [g['ar'] for g in _R['netGroups']] == ['فعل الله', 'فعل العبد', 'الرزق نفسه: صفته ومصدره']
    assert [r['g'] for r in _R['assoc']] == [2, 1, 0, 2, 0, 1, 2, 1, 2, 2, 1, 2, 1, 1, 2, 0]
    for g in _R['groups'] + _R['netGroups']:
        assert g['ar'] and g['en']

def test_roots_that_keep_company():
    V = {r['root']: set(r['verses']) for r in _R['assoc']}
    assert len(V['بسط'] & V['قدر']) == 10                       # He widens and He measures, in the same breath
    assert len(V['طيب'] & V['أكل']) == 7 and len(V['نفق'] & V['صلو']) == 7
    pairs = sum(1 for a in V for b in V if a < b and len(V[a] & V[b]) >= 2)
    assert pairs == 18

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
