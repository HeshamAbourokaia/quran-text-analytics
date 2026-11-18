# -*- coding: utf-8 -*-
"""How each dictionary word sounds, so a reader without an Arabic keyboard can type «rahma» and find «رحمة».

The word index in the browser stores lemmas without vowel marks. This table gives, for each of them, the
sound of the voweled lemma it stands for (several where one spelling covers several words: ملك is malak,
mulk and malik), most frequent first. web/translit.js turns a sound into the spelling shown to the reader
and into the keys a typed word is compared with.

A sound is written one sign to a letter of speech:
  ' hamza   E ع   H ح   x خ   v ث   * ذ   $ ش   S ص   D ض   T ط   Z ظ   g غ   p ة
  a i u short vowels, A I U long ones; a doubled consonant is written twice; the rest are as in English.

Output: {"رحمة": "raHmap", "ملك": "malak mulk malik malk", ...}

Run:  python3 -m pipeline.roman      (from data-build/)
"""
from collections import Counter, defaultdict
from .corpus import load_words, normalize

FATHA, DAMMA, KASRA, SHADDA, SUKUN = '\u064e', '\u064f', '\u0650', '\u0651', '\u0652'
FATHATAN, DAMMATAN, KASRATAN, DAGGER, SMALL_WAW, SMALL_YEH = '\u064b', '\u064c', '\u064d', '\u0670', '\u06e5', '\u06e6'
MARKS = set(FATHA + DAMMA + KASRA + SHADDA + SUKUN + FATHATAN + DAMMATAN + KASRATAN + DAGGER + SMALL_WAW + SMALL_YEH
            + '\u0653\u06df\u06e2')
CONS = {'ب': 'b', 'ت': 't', 'ث': 'v', 'ج': 'j', 'ح': 'H', 'خ': 'x', 'د': 'd', 'ذ': '*', 'ر': 'r', 'ز': 'z', 'س': 's',
        'ش': '$', 'ص': 'S', 'ض': 'D', 'ط': 'T', 'ظ': 'Z', 'ع': 'E', 'غ': 'g', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l',
        'م': 'm', 'ن': 'n', 'ه': 'h', 'ء': "'", 'أ': "'", 'إ': "'", 'ؤ': "'", 'ئ': "'"}
VOWELS = 'aiuAIU'
LONG = {'a': 'A', 'i': 'I', 'u': 'U'}
# words the rules below would misread, by their spelling without marks: the name of God, and the silent
# alif of مائة
FIXED = {'الله': 'allAh', 'اللهم': 'allAhumma', 'مائة': "mi'ap"}


def _units(s):
    """The letters of a word, each with the marks written on it."""
    out = []
    for ch in s:
        if ch in MARKS:
            if out:
                out[-1][1] += ch
        else:
            out.append([ch, ''])
    return out


def _vowel(marks):
    if DAGGER in marks:
        return 'A'
    if FATHA in marks or FATHATAN in marks:
        return 'a'
    if DAMMA in marks or DAMMATAN in marks:
        return 'U' if SMALL_WAW in marks else 'u'
    if KASRA in marks or KASRATAN in marks:
        return 'I' if SMALL_YEH in marks else 'i'
    return ''


def sound(lemma, pos=''):
    """The sound of one voweled lemma, in the signs listed above."""
    if normalize(lemma) in FIXED:
        return FIXED[normalize(lemma)]
    U = _units(lemma)
    if len(U) > 2 and U[0][0] == 'ا' and U[1] == ['ل', ''] and SHADDA in U[2][1]:
        U = [['ا', FATHA]] + U[2:]              # the article's lam is not sounded before a doubled letter
    out = []                                   # signs so far
    last = lambda: out[-1] if out else ''
    def lengthen(v):                           # a long vowel: over the short one before it, or on its own
        if last() == v:
            out[-1] = LONG[v]
        elif last() != LONG[v]:
            out.append(LONG[v])
    for i, (ch, marks) in enumerate(U):
        v, dbl, still = _vowel(marks), SHADDA in marks, SUKUN in marks
        end = i == len(U) - 1
        if ch == 'ا':
            if i == 0:
                # an alif that only carries the first vowel: «al» before the article's lam, «i» otherwise
                nxt = U[1] if len(U) > 1 else ['', '']
                art = nxt[0] == 'ل' and (SHADDA in nxt[1] or (SUKUN in nxt[1] and pos != 'V'))
                out.append(v or ('a' if art else 'i'))
            elif i and FATHATAN in U[i - 1][1]:
                out.append('n')                # إِذًا: the alif after «an» is not sounded
            else:
                lengthen('a')
            continue
        if ch == 'آ':
            out += ["'", 'A']
            continue
        if ch == 'ة':
            if last() not in VOWELS or not last():
                out.append('a')
            out.append('p')
            continue
        if ch in 'وي' or ch == 'ى':
            w, short = ('w', 'u') if ch == 'و' else ('y', 'i')
            if v or dbl:                       # sounded as a consonant: وَ يَ وّ يّ
                out += [w] * (2 if dbl else 1) + ([v] if v else [])
            elif ch == 'ى' and not still:      # عَلَى مُوسَى هُدًى: a long a
                lengthen('a')
            elif i == 0 or last() in ('a', 'A') or (i + 1 < len(U) and U[i + 1][0] == 'ا'):
                out.append(w)                  # يَوْم خَيْر قِيامَة, and a word that begins with it
            elif last() == short or last() == LONG[short]:
                lengthen(short)                # رَسُول دِين: a long vowel
            else:
                lengthen(short)                # no mark before it: long (عافي, قاضي)
            continue
        c = CONS.get(ch)
        if not c:
            continue
        out += [c] * (2 if dbl else 1) + ([v] if v else [])
    s = ''.join(out)
    for a, b in (('uww', 'U'), ('iyy', 'I')):  # عَدُوّ نَبِيّ end in a long vowel
        if s.endswith(a):
            s = s[:-len(a)] + b
    return s


def build(words=None):
    words = words or load_words()
    by = defaultdict(Counter)
    pos = {}
    for w in words:
        lem = w['lemma']
        if not lem:
            continue
        by[normalize(lem)][lem] += 1
        pos.setdefault(lem, w.get('pos') or '')
    out = {}
    for bare, counts in sorted(by.items()):
        if len(bare) < 2:
            continue                           # و ف ب ل ك: joined letters, not words to look up
        seen = []
        for lem, _n in counts.most_common():
            s = sound(lem, pos[lem])
            if s and s not in seen:
                seen.append(s)
        if seen:
            out[bare] = ' '.join(seen)
    return out


if __name__ == '__main__':
    m = build()
    print('lemmas', len(m), '| sounds', sum(len(v.split()) for v in m.values()))
    for k in ('رحمة', 'يوم', 'صلاة', 'ايمان', 'قرءان', 'موسي', 'ملك', 'الله', 'الذي', 'نبي', 'شيء'):
        print(' ', k, m.get(k))
