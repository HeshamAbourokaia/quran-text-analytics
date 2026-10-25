# -*- coding: utf-8 -*-
"""Pin the Hiba page (al-Wahhab, root و ه ب): its counts, who gives, what is given, what sits with the gift, the
five themes, the du'a's traceability with its English meanings, and every finding the page states, each checked
against the verse text itself. Also the rules the Name-study engine keeps for every study.

Run:  python3 tests/test_wahhab.py      (or: pytest)
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline import names, rizq, wahhab
from pipeline.names import norm

_W = wahhab.build()
_R = rizq.build()
_V, _ROOTS, _TOK = names._read()
_KEYS = [v['k'] for v in _W['verses']]
_SET = set(_KEYS)
_POS = {s: i + 1 for i, s in enumerate(names.CHRONO)}

def _order(k):
    s, a = k.split(':'); return int(s), int(a)

def test_totals():
    assert _W['totals'] == {'tokens': 25, 'verses': 22, 'surahs': 12, 'mecca': 19, 'medina': 3, 'verbs': 22, 'nouns': 3, 'quran': 6236}
    assert sum(len(v['w']) for v in _W['verses']) == 25
    assert [v['k'] for v in _W['verses'] if v['p'] == 'd'] == ['3:8', '3:38', '33:50']

def test_every_marked_word_is_a_word_of_giving():
    for v in _W['verses']:
        words = _V[v['k']].split()
        for w in v['w']:
            assert any(x in norm(words[w - 1]) for x in ('هب', 'هاب')), (v['k'], words[w - 1])   # وهب, and the Name الوهاب

def test_the_name_and_the_seven_duas():
    assert {x['id']: (x['n'], x['ex']) for x in _W['nouns']} == {'wahhab': (3, ['3:8', '38:9', '38:35'])}
    asks = [k for k in _KEYS if any('IMPV' in t['tags'] and '2MS' in t['tags'] for t in _TOK['وهب'][k])]
    assert asks == ['3:8', '3:38', '19:5', '25:74', '26:83', '37:100', '38:35']
    assert asks == wahhab.THEMES[0][2][:3] + ['25:74', '26:83', '37:100', '38:35'] and [m['k'] for m in _W['models']] == asks
    for k in ('3:8', '38:35'):                                   # twice the Name closes a du'a
        assert norm(_V[k]).endswith('انك انت الوهاب'), k

def test_who_gives():
    assert {a['id']: a['n'] for a in _W['agents']} == {'we': 9, 'ask': 7, 'he': 4, 'jibril': 1, 'woman': 1}
    assert {a['id']: a['ex'] for a in _W['agents'] if a['id'] in ('jibril', 'woman')} == {'jibril': ['19:19'], 'woman': ['33:50']}

def test_themes_and_objects_cover_the_verses_once():
    assert [t['n'] for t in _W['themes']] == [7, 9, 2, 2, 2] and [t['mecca'] for t in _W['themes']] == [5, 9, 2, 2, 1]
    labelled = [k for th in wahhab.THEMES for k in th[2]]
    assert len(labelled) == len(set(labelled)) == 22 and set(labelled) == _SET
    assert [o['n'] for o in _W['objects']] == [13, 3, 2, 2, 1, 1] and sum(o['n'] for o in _W['objects']) == 22
    assert set(k for o in _W['objects'] for k in o['verses']) == _SET
    assert sum(t['n'] for t in _W['themes'][:2]) == 16             # du'as and answers: three quarters of the 22

def test_what_sits_with_the_gift():
    rows = _W['assoc']
    assert [r['root'] for r in rows[:4]] == ['ذرر', 'لدن', 'صلح', 'زوج'] and len(rows) == 13
    assert all(r['z'] >= 2 for r in rows) and rows[0]['z'] == 6.92 and rows[0]['pctAll'] == 0.6
    for r in rows:
        assert r['ar'] and r['en'] and len(r['verses']) == r['n'] and set(r['verses']) <= _SET, r['root']

def test_findings_hold_on_the_text():
    # five of the seven du'as are answered in the next verse or the one after
    for k, w in (('3:39', 'فنادته'), ('19:7', 'نبشرك'), ('25:75', 'يجزون'), ('37:101', 'فبشرناه'), ('38:36', 'فسخرنا')):
        assert w in norm(_V[k]), k
    # «from Your presence» three times; the answer «of Our mercy» twice and «a mercy from Us» once
    assert [k for k in _KEYS if 'من لدنك' in norm(_V[k])] == ['3:8', '3:38', '19:5']
    assert [k for k in _KEYS if 'من رحمتنا' in norm(_V[k])] == ['19:50', '19:53'] and 'رحمه منا' in norm(_V['38:43'])
    # «without reckoning»: five rizq verses, and the gift to Sulayman four verses after his prayer
    assert [v['k'] for v in _R['verses'] if 'بغير حساب' in norm(_V[v['k']])] == ['2:212', '3:27', '3:37', '24:38', '40:40']
    assert 'بغير حساب' in norm(_V['38:39'])
    # 42:50 is the verse after 42:49, and names the barren
    assert 'عقيما' in norm(_V['42:50'])
    # thirteen verses are about offspring, the same verses the finding cites
    assert _W['objects'][0]['n'] == 13 and set(_W['findings'][4]['verses']) == set(_W['objects'][0]['verses'])
    for f in _W['findings']:
        assert f['ar'] and f['en'] and f['bar'] and f['ben'] and all(k in _V for k in f['verses']), f['en']
    assert len(_W['findings']) == 10

def test_revelation_order():
    by = sorted(_KEYS, key=lambda k: (_POS[int(k.split(':')[0])], int(k.split(':')[1])))
    assert by[0] == '38:9' and by[-1] == '33:50'                   # the Name itself comes first; the ruling of 33:50 last
    assert norm(_V['38:9']).endswith('العزيز الوهاب')
    assert min(_POS[int(k.split(':')[0])] for k in _KEYS) == _POS[38]

def test_the_conditions_table():
    theme = {v['k']: v['t'] for v in _W['verses']}
    cells = collections.Counter(theme[k] for c in _W['conditions'] for k in c['verses'])
    assert cells[0] * 2 > sum(cells.values())                      # most pairs sit in the column of the seven du'as
    assert all(set(c['verses']) <= _SET for c in _W['conditions'])

def test_forms_and_formulas():
    assert len(_W['forms']) == 11 and sum(f['n'] for f in _W['forms']) == 25
    assert {g: sum(f['n'] for f in _W['forms'] if f['g'] == g) for g in (0, 2)} == {0: 22, 2: 3}
    F = {f['t']: f for f in _W['formulas']}
    assert F['ووهبنا له']['n'] == 6 and F['من لدنك']['verses'] == ['3:8', '3:38', '19:5'] and F['انك انت الوهاب']['n'] == 2
    for f in _W['formulas']:
        assert len(f['verses']) == f['n'] >= 2 and all(f['t'] in norm(_V[k]) for k in f['verses']), f['t']
        assert norm(f['u']) == f['t']

def test_dua_traceability():
    S = _W['dua']['sum']
    keys = ('segments', 'text', 'shift', 'whole', 'words', 'kept', 'pctKept', 'pctTarget', 'pctQuran')
    assert {k: S['full'][k] for k in keys} == {'segments': 32, 'text': 23, 'shift': 9, 'whole': 8, 'words': 174, 'kept': 107, 'pctKept': 61, 'pctTarget': 68, 'pctQuran': 94}
    assert {k: S['short'][k] for k in keys} == {'segments': 9, 'text': 6, 'shift': 3, 'whole': 4, 'words': 53, 'kept': 44, 'pctKept': 83, 'pctTarget': 96, 'pctQuran': 100}
    assert S['full']['ctx'] == ['14:40', '19:3', '19:4', '19:6', '19:9', '21:89', '26:84', '26:85', '38:39', '38:44'] and S['short']['ctx'] == []
    segs = [s for p in _W['dua']['full'] for s in p['segs']] + _W['dua']['short']
    for s in segs:
        assert s['en'] and not re.search('[؀-ۿ]', s['en']), s['t']          # a plain English meaning under every phrase
        shown = s['t'].split(' ')
        assert len(s['kw']) == len(shown)
        bag = {w for src in s['src'] for w in _V[src['k']].split()}
        bag = {norm(w) for w in bag} | {norm(w).lstrip('وف') for w in bag}
        for w, k in zip(shown, s['kw']):
            n = norm(w.strip('،,.:؛'))
            assert k == (1 if (n in bag or n.lstrip('وف') in bag) else 0), (s['t'], w)
        if s['whole']:
            assert s['mode'] == 'text' and all(s['kw']), s['t']
        for src in s['src']:
            assert src['ctx'] == (src['k'] not in _SET)
            if src['ctx']:                                          # a source near a verse of giving: same surah, within four verses
                ss, aa = _order(src['k'])
                assert any(_order(k)[0] == ss and 0 < abs(_order(k)[1] - aa) <= 4 for k in _KEYS), src['k']
    assert [p['ar'] for p in _W['dua']['full']] == ['النداء والتمهيد', 'الثناء بالاسم', 'الطلب بصيغ القرآن', 'العهد: ما قرنته الآيات بالهبة', 'الحمد والختم']
    assert all(p['en'] for p in _W['dua']['full'])

def test_models_read_whole_verses():
    for m in _W['models']:
        words = _V[m['k']].split()
        sp = m['spans']
        assert sp[-1][1] <= len(words) and all(sp[i][1] + 1 == sp[i + 1][0] for i in range(len(sp) - 1)), m['k']
        assert any('هب' in norm(w) for a, b, _, _ in sp for w in words[a - 1:b]), m['k']
        assert all(x[2] and x[3] for x in sp)

def test_page_content_rules():
    for R in (_W, _R):
        blob = json.dumps(R, ensure_ascii=False)
        for ch in (chr(0x2014), chr(0x2013), chr(0x2212)):         # em dash, en dash, minus sign
            assert ch not in blob, R['slug']
        for key, v in R['copy'].items():                            # every sentence in both languages; only the page's own placeholders left
            pairs = v if isinstance(v[0], list) else [v]
            for en, ar in pairs:
                assert en and ar, key
                assert set(re.findall(r'\{(\w+)\}', en + ar)) <= {'pctQuran', 'pctTarget', 'ctx', 'n', 'top', 'none', 'cnt', 'm', 'first', 'last'}, key
        assert set(re.findall(r'\{(\w+)\}', ' '.join(R['copy']['sumWords']))) == {'pctQuran', 'pctTarget'}   # filled by the page, not by the build
    assert len(json.dumps(_W, ensure_ascii=False).encode()) < 60000
    assert _W['sections'] and set(_W['sections']) >= set(_R['sections'])     # the Hiba page shows everything the Rizq page does, and more
    assert (_R['name']['en'], _W['name']['en']) == ('Ar-Razzaq', 'Al-Wahhab') and (_R['slug'], _W['slug']) == ('rizq', 'wahhab')

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
