# -*- coding: utf-8 -*-
"""How many words are in the Quran? The same text counted under different rules.

The printed Madani mushaf has 77,429 written words (a word is what sits between two spaces).
Every other well-known total comes from the same letters counted with a different idea of what a
word is. Each rule here is a set of pieces the corpus already separates; switching a rule on
counts those pieces as words of their own. The pieces never overlap, so the rules add up: with
every rule on, the total is the corpus's 130,030 segments.

  basmala    the Basmala (4 words) at the head of the 112 surahs where it is not a verse
  voc        the vocative يا written joined to the next word (يَٰٓأَيُّهَا)          modern spelling
  haAttn     the ها of attention before أنتم and هنا (هَٰٓأَنتُمْ, هَٰهُنَا)     modern spelling
  ibnUmm     the second noun in يَبْنَؤُمَّ (20:94), spelled يا ابن أم today      modern spelling
  fused      two words written as one (إِنَّمَا, يَوْمَئِذٍ, مِمَّا)
  particles  the joined particles و ف ب ل ك س and the question أ
  article    the article ال
  pronouns   attached pronouns (كِتَٰبُهُۥ), including the few understood but not written
  small      the other pieces: the ها of هذا, the لِ and كَ of ذٰلِكَ, the emphatic نَّ
The opening letters (الٓمٓ) are a separate choice: one word each (as printed), a word a letter, or none.
"""
import collections, unicodedata
from .corpus import _read_rows, normalize

PARTS = ['basmala', 'voc', 'haAttn', 'ibnUmm', 'fused', 'particles', 'article', 'pronouns', 'small']
SPELLING = ['voc', 'haAttn', 'ibnUmm']           # Uthmani spelling -> modern (imla'i) spelling
BASMALA = ['بِسْمِ', 'ٱللَّهِ', 'ٱلرَّحْمَٰنِ', 'ٱلرَّحِيمِ']
SAMPLES = ['2:21', '3:66', '20:94', '2:2', '30:4', '2:1']

def _tags(seg):
    return set(seg['feats'].split('|'))

def _parts(segs):
    """The rule that separates each segment of one written word ('' = stays with the stem)."""
    tags = [_tags(s) for s in segs]
    stems = [i for i, t in enumerate(tags) if 'PREF' not in t and 'SUFF' not in t]
    voc = any('VOC' in t and 'PREF' in t for t in tags)
    out = []
    for i, (s, t) in enumerate(zip(segs, tags)):
        if 'PREF' in t:
            if 'VOC' in t:
                p = 'voc'
            elif 'ATT' in t:
                nxt = normalize(segs[i + 1]['form']) if i + 1 < len(segs) else ''
                p = 'haAttn' if nxt in ('انتم', 'هنا') else 'small'
            elif 'DET' in t:
                p = 'article'
            else:
                p = 'particles'
        elif 'SUFF' in t:
            p = 'pronouns' if 'PRON' in t else 'small'
        else:
            p = '' if i == stems[0] else ('ibnUmm' if voc else 'fused')
        out.append(p)
    return out

def _pieces(segs, parts, on):
    """The word as it splits when the rules in `on` are switched on: [text, 1 if a rule cut it off]."""
    pieces, cur = [], None
    for s, p in zip(segs, parts):
        if p and p in on:
            pieces.append([s['form'], 1]); cur = None
        elif s['form'] or cur is not None:      # an unwritten piece left whole adds no word
            if cur is None:
                pieces.append(['', 0]); cur = len(pieces) - 1
            pieces[cur][0] += s['form']
    return pieces

def _letters(form):
    return [c for c in unicodedata.normalize('NFD', form) if unicodedata.category(c).startswith('L')]

def build():
    rows = _read_rows()
    words = collections.OrderedDict()
    for r in rows:
        words.setdefault((r['sura'], r['aya'], r['word']), []).append(r)
    for k in words:
        words[k].sort(key=lambda r: r['seg'])

    n = {p: 0 for p in PARTS}
    by_surah = {p: [0] * 114 for p in PARTS}
    seen = {p: collections.OrderedDict() for p in PARTS}   # surface -> [count, key, index]
    letters, samples = [], {k: [] for k in SAMPLES}
    for (s, a, w), segs in words.items():
        parts = _parts(segs)
        surface = ''.join(x['form'] for x in segs)
        for p in set(x for x in parts if x):
            c = parts.count(p)
            n[p] += c; by_surah[p][s - 1] += c
            e = seen[p].setdefault(surface, [0, f'{s}:{a}', w])
            e[0] += c
        if any('INL' in _tags(x) for x in segs):
            letters.append({'k': f'{s}:{a}', 'w': surface, 'l': len(_letters(surface))})
        key = f'{s}:{a}'
        if key in samples:
            samples[key].append([[x['form'], p] for x, p in zip(segs, parts)])

    # the Basmala opens every surah but al-Tawba; in al-Fatiha it is verse 1 and already counted
    for s in range(2, 115):
        if s != 9:
            n['basmala'] += 4; by_surah['basmala'][s - 1] += 4

    def examples(p, many=6):
        top = sorted(seen[p].items(), key=lambda kv: -kv[1][0])[:many]
        out = []
        for surface, (c, key, w) in top:
            s, a = map(int, key.split(':'))
            segs = words[(s, a, w)]
            out.append({'w': surface, 'n': c, 'k': key, 'i': w, 'p': _pieces(segs, _parts(segs), {p})})
        return out

    base = len(words)
    rules = {p: {'n': n[p], 'bySurah': by_surah[p], 'ex': examples(p) if p != 'basmala' else
                 [{'w': ' '.join(BASMALA), 'n': 112, 'k': '1:1', 'i': 1, 'p': [[w, 1] for w in BASMALA]}]} for p in PARTS}
    n_letters = sum(x['l'] for x in letters)
    return {
        'base': base,
        'segments': len(rows),
        'rules': rules,
        'spelling': SPELLING,
        'letters': {'words': len(letters), 'letters': n_letters, 'list': letters,
                    'bySurah': [sum(1 for x in letters if int(x['k'].split(':')[0]) == s) for s in range(1, 115)]},
        'samples': [{'k': k, 'words': samples[k]} for k in SAMPLES],
        'totals': {
            'printed': base,
            'modern': base + sum(n[p] for p in SPELLING),
            'basmala': base + n['basmala'],
            'everyPiece': base + sum(n[p] for p in PARTS if p != 'basmala'),
        },
        # counts reported in the classical sources, with where they are recorded
        'reported': [{'id': 'ata', 'n': 77439}],
    }

if __name__ == '__main__':
    wc = build()
    print('base', wc['base'], '| segments', wc['segments'])
    for p in PARTS:
        print('  %-10s %+7d' % (p, wc['rules'][p]['n']), [e['w'] for e in wc['rules'][p]['ex'][:4]])
    print('letters', wc['letters']['words'], 'words,', wc['letters']['letters'], 'letters')
    print('totals', wc['totals'])
