# -*- coding: utf-8 -*-
"""The phrases the Quran comes back to: runs of three or more words, inside one verse, that come again.

Words are compared as written with the vowel marks taken off (corpus.normalize), so a phrase is the same
wherever it stands. A phrase is kept when
  - it comes at least MIN_COUNT times (each place counted, two in one verse included);
  - it is closed: no phrase one word longer, on either side, comes as often. Otherwise the longer phrase is the
    one that repeats and this is only a piece of it;
  - it carries meaning: at least two words that do, by the Quranic Arabic Corpus's own tags. A word carries
    meaning when it is or holds a verb, a noun, a name, an adjective, a participle, a verbal noun or a pronoun,
    standing alone or attached (the هو of «لا إله إلا هو», the هم of «لهم»): a pronoun stands for someone or
    something. Relatives (الذين), demonstratives (ذلك), time and place words (إذا, قبل), question and
    condition words and particles (لا, ما, إن, في) do not;
  - it ends on a word that carries meaning, never on one that leaves the sentence hanging (لا, ما, إن, الذين,
    ذلك).

Output ../web/phrases.js: window.QURAN_PHRASES = {meta: {...}, list: [[phrase, words, [starts]], ...]}
  phrase  the words as compared, joined by a space
  words   how many words it has
  starts  the index in words.js of the first word of each place, in reading order
Most repeated first; then longer first; then the earlier first place.

Run:  python3 -m pipeline.phrases      (from data-build/) writes ../web/phrases.js and nothing else
"""
import json
import os
from collections import Counter, defaultdict

from .corpus import load_words, _read_rows

MIN_COUNT = 3
MIN_WORDS = 3
MIN_MEANING = 2
# noun-class stems that do not carry meaning by themselves (the corpus's fine tags)
FUNCTION_NOUNS = {'REL', 'PRON', 'DEM', 'T', 'LOC', 'INTG', 'COND'}
HERE = os.path.dirname(os.path.abspath(__file__))


def word_tags():
    """For each word in reading order: (its place, carries meaning, may end a phrase). A phrase may end on a word
    exactly when it carries meaning; both are kept so the rule can be read where it is used."""
    groups, order = defaultdict(list), []
    for r in _read_rows():
        k = (r['sura'], r['aya'], r['word'])
        if k not in groups:
            order.append(k)
        groups[k].append(r)
    out = []
    for k in order:
        meaning = False
        for s in groups[k]:
            f = s['feats'].split('|')
            tag = f[0] if f and ':' not in f[0] else ''
            if tag == 'PRON' or (('PREF' not in f and 'SUFF' not in f)
                                 and (s['pos'] == 'V' or (s['pos'] == 'N' and tag not in FUNCTION_NOUNS))):
                meaning = True
        out.append((k, meaning, meaning))
    return out


def build(words=None, tags=None):
    """The kept phrases and the figures about them."""
    words = words if words is not None else load_words()
    tags = tags if tags is not None else word_tags()
    assert len(tags) == len(words) and all(t[0] == (w['sura'], w['aya'], w['word']) for t, w in zip(tags, words))
    norm = [w['norm'] for w in words]
    meaning = [t[1] for t in tags]
    ends = [t[2] for t in tags]

    verses = defaultdict(list)
    for i, w in enumerate(words):
        verses[(w['sura'], w['aya'])].append(i)

    count, places = Counter(), defaultdict(list)
    for ix in verses.values():
        a, L = ix[0], len(ix)
        for n in range(MIN_WORDS, L + 1):
            for j in range(a, a + L - n + 1):
                g = tuple(norm[j:j + n])
                count[g] += 1
                places[g].append(j)

    # a phrase is a piece of a longer one when a phrase one word longer comes as often
    piece = set()
    for g, c in count.items():
        if c < MIN_COUNT or len(g) <= MIN_WORDS:
            continue
        for sub in (g[1:], g[:-1]):
            if count.get(sub) == c:
                piece.add(sub)

    kept = []
    for g, c in count.items():
        if c < MIN_COUNT or g in piece:
            continue
        s = places[g][0]
        n = len(g)
        if sum(meaning[s:s + n]) < MIN_MEANING or not ends[s + n - 1]:
            continue
        kept.append((' '.join(g), n, sorted(places[g])))
    kept.sort(key=lambda p: (-len(p[2]), -p[1], p[2][0]))

    covered = set()
    for _, n, st in kept:
        for s in st:
            covered.update(range(s, s + n))
    meta = {'phrases': len(kept), 'places': sum(len(p[2]) for p in kept), 'minCount': MIN_COUNT, 'minWords': MIN_WORDS,
            'words': len(words), 'covered': len(covered), 'coverage': round(len(covered) / len(words), 4),
            'byLength': {str(k): v for k, v in sorted(Counter(p[1] for p in kept).items())},
            'longest': max(p[1] for p in kept)}
    return {'meta': meta, 'list': [list(p) for p in kept]}


def write(web_dir=None):
    data = build()
    web_dir = web_dir or os.path.join(HERE, '..', '..', 'web')
    with open(os.path.join(web_dir, 'phrases.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.QURAN_PHRASES = ')
        json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write(';\n')
    return data


if __name__ == '__main__':
    d = write()
    m = d['meta']
    print('phrases', m['phrases'], '| places', m['places'], '| words inside one', m['covered'], 'of', m['words'],
          '(%.1f%%)' % (100 * m['coverage']), '| by length', m['byLength'])
    for p, n, st in d['list'][:20]:
        print(' ', len(st), n, p)
