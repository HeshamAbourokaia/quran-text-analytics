# -*- coding: utf-8 -*-
"""Pin where each juz, hizb and printed page begins, and that the site's data file carries the same.

Run:  python3 tests/test_marks.py      (or: pytest)
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline.marks import build, _layout

_M = build()
_WEB = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'data.js')

def test_sizes():
    assert len(_M['juz']) == 30 and len(_M['quarter']) == 240 and len(_M['page']) == 604

def test_the_thirty_juz():
    assert _M['juz'] == ['1:1', '2:142', '2:253', '3:93', '4:24', '4:148', '5:82', '6:111', '7:88', '8:41',
                         '9:93', '11:6', '12:53', '15:1', '17:1', '18:75', '21:1', '23:1', '25:21', '27:56',
                         '29:46', '33:31', '36:28', '39:32', '41:47', '46:1', '51:31', '58:1', '67:1', '78:1']

def test_the_sixty_hizb():
    hizb = _M['quarter'][::4]
    assert len(hizb) == 60 and hizb[::2] == _M['juz']
    assert hizb[1] == '2:75' and hizb[31] == '20:1' and hizb[59] == '87:1'

def test_quarters_are_the_signs_printed_in_the_mushaf():
    _, signed = _layout()
    assert len(signed) == 199 and set(signed) <= set(_M['quarter'])
    opens = [q for q in _M['quarter'] if q not in set(signed)]
    assert len(opens) == 41 and all(q.endswith(':1') for q in opens)       # the print leaves the sign off a surah's opening
    assert '15:49' in _M['quarter'] and '15:50' not in _M['quarter']       # the print, where one published list has 15:50

def test_pages():
    p = _M['page']
    assert p[0] == '1:1' and p[1] == '2:1' and p[2] == '2:6' and p[49] == '3:1'
    assert p[41] == '2:253' and p[581] == '78:1' and p[603] == '112:1'       # juz 3 opens page 42, juz 30 page 582
    assert len(set(p)) == 604

def test_the_site_carries_the_same_lists():
    s = open(_WEB, encoding='utf-8').read()
    d = json.loads(s[s.index('{'):s.rindex('}') + 1])
    assert d['marks'] == _M

if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
