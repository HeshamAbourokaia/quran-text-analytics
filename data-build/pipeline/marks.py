# -*- coding: utf-8 -*-
"""Where each juz, each quarter of a hizb and each printed page begins.

  page     the first verse that starts on each of the 604 pages, read from the mushaf layout in
           sources/mushaf (the same layout the Mushaf Layouts page draws)
  juz      the 30 juz
  quarter  the 240 quarters of a hizb; a hizb is four of them and a juz is eight

A quarter is read from the mushaf itself: the print marks it with the sign ۞, and the layout has 199 of
them. The other 41 quarters open a surah, where the print leaves the sign out; those come from the
Tanzil Project's Quran metadata (tanzil.net, Creative Commons Attribution 3.0). The two sources agree
everywhere but once: the print puts a sign on 15:49 and the Tanzil list has 15:50. The print is followed.

Output: {'juz': [30 x "sura:aya"], 'quarter': [240 x ...], 'page': [604 x ...]}

Run:  python3 -m pipeline.marks      (from data-build/)
"""
import os, json, glob

SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'sources', 'mushaf')
RUB = '۞'                      # the sign ۞ that the mushaf prints where a quarter begins

# the surahs whose first verse opens a quarter (Tanzil metadata); the print does not mark these
OPENS = [1, 4, 5, 7, 8, 9, 15, 16, 17, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 33, 40, 46, 49, 55, 56, 58,
         62, 65, 66, 67, 68, 69, 72, 75, 78, 80, 82, 84, 87, 90, 94]
JUZ = """1:1 2:142 2:253 3:93 4:24 4:148 5:82 6:111 7:88 8:41 9:93 11:6 12:53 15:1 17:1 18:75 21:1 23:1 25:21
27:56 29:46 33:31 36:28 39:32 41:47 46:1 51:31 58:1 67:1 78:1""".split()

def _layout():
    """(page of each verse's first word, the verses that carry the quarter sign), from the layout."""
    first, signed = {}, []
    for f in sorted(glob.glob(os.path.join(SRC_DIR, 'page-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for ln in d['lines']:
            for w in ln.get('words', []):
                s, a, _ = w['location'].split(':')
                k = s + ':' + a
                first.setdefault(k, d['page'])
                if RUB in w.get('word', ''):
                    signed.append(k)
    return first, signed

def build():
    first, signed = _layout()
    page = {}
    for k, p in first.items():          # verses come in reading order, so the first seen on a page opens it
        page.setdefault(p, k)
    pages = [page[p] for p in sorted(page)]
    # quarters: every sign in the print, and the surah openings that carry none, in reading order
    order = {k: i for i, k in enumerate(first)}
    opens = ['%d:1' % n for n in OPENS]
    assert len(signed) == 199 and len(opens) == 41 and not set(signed) & set(opens)
    quarters = sorted(signed + opens, key=order.get)
    # a juz is eight quarters: the list that falls out must be the thirty juz every mushaf prints
    assert len(quarters) == 240 and quarters[::8] == JUZ, quarters[::8]
    return {'juz': JUZ, 'quarter': quarters, 'page': pages}

if __name__ == '__main__':
    m = build()
    print('juz', len(m['juz']), '| quarters', len(m['quarter']), '| pages', len(m['page']))
