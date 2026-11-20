# -*- coding: utf-8 -*-
"""Pin the repeated phrases: every place points at the right words, the rules that keep a phrase hold, the
best-known phrases have their counts, and the site's file is what the code builds.

Run:  python3 tests/test_phrases.py      (or: pytest)
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from collections import Counter
from pipeline.corpus import load_words
from pipeline.phrases import build, word_tags, MIN_COUNT, MIN_WORDS, MIN_MEANING

_W = load_words()
_T = word_tags()
_P = build(_W, _T)
_BY = {p: (n, st) for p, n, st in _P['list']}
_WEB = os.path.join(os.path.dirname(__file__), '..', '..', 'web')


def _load(name, var):
    s = open(os.path.join(_WEB, name), encoding='utf-8').read()
    assert s.startswith('window.%s = ' % var)
    return json.loads(s[s.index('=') + 1:s.rindex(';')])


def test_every_place_is_the_phrase_inside_one_verse():
    for p, n, st in _P['list']:
        words = p.split(' ')
        assert len(words) == n >= MIN_WORDS
        assert st == sorted(st) and len(set(st)) == len(st)
        for s in st:
            assert [w['norm'] for w in _W[s:s + n]] == words, (p, s)
            assert len({(w['sura'], w['aya']) for w in _W[s:s + n]}) == 1, ('crosses a verse', p, s)


def test_the_counts_are_every_place():
    # the full count of each kept phrase, found again by a plain scan of every verse
    verses = {}
    for i, w in enumerate(_W):
        verses.setdefault((w['sura'], w['aya']), []).append(w['norm'])
    sample = [p for i, (p, n, st) in enumerate(_P['list']) if i % 37 == 0]
    for p in sample:
        g, n = p.split(' '), len(p.split(' '))
        found = sum(1 for v in verses.values() for j in range(len(v) - n + 1) if v[j:j + n] == g)
        assert found == len(_BY[p][1]) >= MIN_COUNT, p


def test_best_known_phrases():
    want = {'يايها الذين ءامنوا': 89, 'من دون الله': 71, 'تجري من تحتها الانهر': 34, 'فباي ءالاء ربكما تكذبان': 31,
            'لا اله الا هو': 30, 'ولكن اكثر الناس لا يعلمون': 11, 'واذا قيل لهم': 13, 'والله عليم حكيم': 13,
            'الحمد لله رب العلمين': 4}
    for p, c in want.items():
        assert p in _BY and len(_BY[p][1]) == c, (p, len(_BY.get(p, (0, []))[1]))
    assert _P['list'][0][0] == 'يايها الذين ءامنوا'


def test_no_phrase_is_only_a_piece_of_a_longer_one():
    # one word more on either side, at every place, never gives the same phrase every time
    for p, n, st in _P['list']:
        for side in (-1, n):
            ext = Counter()
            for s in st:
                i = s + side
                inside = 0 <= i < len(_W) and (_W[i]['sura'], _W[i]['aya']) == (_W[s]['sura'], _W[s]['aya'])
                ext[_W[i]['norm'] if inside else None] += 1
            assert not (len(ext) == 1 and None not in ext), (p, side, ext)


def test_every_phrase_carries_meaning_and_does_not_end_hanging():
    for p, n, st in _P['list']:
        s = st[0]
        assert sum(t[1] for t in _T[s:s + n]) >= MIN_MEANING, p
        assert _T[s + n - 1][2], p
    # phrases the rules leave out: a hanging ending, or too little meaning
    for p in ('ان الله لا', 'ان في ذلك', 'من بعد ما', 'من قبل ان', 'ولكن اكثر الناس لا', 'يايها الذين ءامنوا لا'):
        assert p not in _BY, p


def test_the_word_tags():
    tag = {(w['norm']): t for w, t in zip(_W, _T)}
    # a name, a noun, a verb, an adjective, a pronoun on its own, and pronouns attached, however the corpus splits
    # them (فيها is a preposition with a pronoun suffix, لهم a pronoun with a preposition prefix)
    for w in ('الله', 'كتب', 'ءامنوا', 'الرحيم', 'هو', 'فيها', 'لهم', 'عليه'):
        assert tag[w][1] and tag[w][2], w
    for w in ('الذين', 'ذلك', 'لا', 'ان', 'من', 'اذا', 'الي', 'في'):   # a relative, a demonstrative, particles, a time word
        assert not tag[w][1] and not tag[w][2], w


def test_meta():
    m = _P['meta']
    assert m['phrases'] == len(_P['list']) and m['places'] == sum(len(p[2]) for p in _P['list'])
    assert m['words'] == 77429
    assert 0 < m['covered'] < m['words'] and abs(m['covered'] / m['words'] - m['coverage']) < 1e-4
    assert sum(m['byLength'].values()) == m['phrases'] and m['longest'] == max(int(k) for k in m['byLength'])
    assert 1000 <= m['phrases'] <= 1500


def test_the_site_carries_what_the_code_builds():
    assert _load('phrases.js', 'QURAN_PHRASES') == _P


def test_the_explanations_quote_the_build():
    # the numbers web/explain.js and the page's plain text give are the ones built here
    m, by = _P['meta'], Counter(p[1] for p in _P['list'])
    sci = open(os.path.join(_WEB, 'explain.js'), encoding='utf-8').read()
    sci = sci[sci.index('    phrases: {'):sci.index('    cluster: {')]
    longer = sum(v for k, v in by.items() if k > 5)
    for n in (m['phrases'], m['places'], m['covered'], by[3], by[4], by[5], longer, 77429):
        assert '{:,}'.format(n) in sci, n
    assert '%.1f%%' % (100 * m['coverage']) in sci
    assert m['longest'] == 12 and 'up to twelve' in sci
    top = {p: len(st) for p, n, st in _P['list'][:3]}
    assert top == {'يايها الذين ءامنوا': 89, 'من دون الله': 71, 'علي كل شيء': 52} and '(89)' in sci and '(71)' in sci and '(52)' in sci
    app = open(os.path.join(_WEB, 'app.html'), encoding='utf-8').read()
    plain = app[app.index('  phrases:{'):app.index('  coincidence:{')]
    assert '«O you who believe», 89 times' in plain and '«besides Allah», 71 times' in plain
    assert 0.18 < m['coverage'] < 0.22   # «about one word in five»


def test_places_point_into_the_site_word_index():
    w = _load('words.js', 'QURAN_WORDS')
    for p, n, st in _P['list'][:200]:
        for s in st:
            assert w['norm'][s:s + n] == p.split(' '), (p, s)


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
