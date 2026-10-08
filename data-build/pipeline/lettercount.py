# -*- coding: utf-8 -*-
"""How many letters are in the Quran? The same text counted under different rules.

The printed mushaf has 325,665 written letters (the letters of the Uthmani spelling, without vowel marks,
small signs or the tatweel stroke). The early counts recorded by al-Qurtubi are 321,180 (Mujahid),
323,015 (Ata ibn Yasar) and 340,740 (al-Hammani, from the reciters al-Hajjaj gathered). Each rule here
changes what counts as a letter:

  basmala     the Basmala (19 written letters) at the head of the 112 surahs where it is not a verse
  hamza       leave out the standalone hamza ء, a sign the first mushafs did not write          (fewer)
  smallAlif   the small (dagger) alif, read as a long a but written small: ٱلرَّحْمَٰنِ
  smallWawYa  the small waw and ya that mark a long vowel: بِهِۦ
  shadda      a doubled letter counted twice: ٱللَّه has two lams
  tanween     the n of tanween counted as a letter: أَحَدٌ ends in an n sound
  names       the opening letters read by their names: الٓمٓ is alif lam mim
The rules are counted letter by letter in each word, so they add. The Basmala itself has 3 doubled
letters and 1 small alif, which count at each of the 112 surah heads when those rules are on too.
"""
import collections, unicodedata
from .corpus import load_words, _read_rows

RULES = ['basmala', 'hamza', 'smallAlif', 'smallWawYa', 'shadda', 'tanween', 'names']
SHADDA, SMALL_ALIF, SMALL_WAW, SMALL_YA = 'ّ', 'ٰ', 'ۥ', 'ۦ'
TANWEEN = 'ًٌٍ'
BASMALA = 'بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ'
# the opening letters as they are read: alif, lam, mim ... (ra, ha, ya, ta and ha are read short)
NAMES = {'ا': 'الف', 'ل': 'لام', 'م': 'ميم', 'ص': 'صاد', 'ر': 'را', 'ك': 'كاف', 'ه': 'ها', 'ي': 'يا',
         'ع': 'عين', 'ط': 'طا', 'س': 'سين', 'ح': 'حا', 'ق': 'قاف', 'ن': 'نون'}
SAMPLES = ['1:1', '2:1', '2:2', '2:22', '112:1', '112:4']
REPORTED = [{'id': 'mujahid', 'n': 321180}, {'id': 'ata', 'n': 323015}, {'id': 'hammani', 'n': 340740}]

def _is_letter(ch):
    return unicodedata.category(ch) == 'Lo'

def tiles(surface, opening=False):
    """The word as letter tiles: [letter, rule]. rule '' is a written letter, 'hamza' a written ء the hamza
    rule leaves out, any other rule a letter that rule adds. The opening letters carry their names under
    'names' (shown in place of the written letters when that rule is on)."""
    out, last = [], ''
    for ch in surface:
        if _is_letter(ch):
            out.append([ch, 'hamza' if ch == 'ء' else '']); last = ch
        elif ch == SHADDA and last:
            out.append([last, 'shadda'])
        elif ch == SMALL_ALIF and last not in ('ى', 'ي'):     # on ى it only shows how the ى is read
            out.append(['ا', 'smallAlif'])
        elif ch in (SMALL_WAW, SMALL_YA):
            out.append(['و' if ch == SMALL_WAW else 'ي', 'smallWawYa'])
        elif ch in TANWEEN:
            out.append(['ن', 'tanween'])
    if opening:
        written = [t[0] for t in out if not t[1]]
        out += [[c, 'names'] for c in ''.join(NAMES[x] for x in written)]
    return out

def count(ts, on=()):
    """Letters in a tile list with the rules in `on` switched on."""
    on = set(on)
    names = 'names' in on and any(r == 'names' for _, r in ts)
    n = 0
    for _, r in ts:
        if names and r in ('', 'hamza'):
            continue                                   # the names stand in for the written letters
        if r == '' or (r == 'hamza' and 'hamza' not in on) or (r and r != 'hamza' and r in on):
            n += 1
    return n

def build():
    words = load_words()
    opening = {(r['sura'], r['aya'], r['word']) for r in _read_rows() if 'INL' in r['feats'].split('|')}
    base_by = [0] * 114
    delta = {r: 0 for r in RULES if r != 'basmala'}
    by = {r: [0] * 114 for r in RULES}
    seen = {r: collections.OrderedDict() for r in RULES if r != 'basmala'}
    samples = {k: [] for k in SAMPLES}; texts = {k: [] for k in SAMPLES}
    for w in words:
        s = w['sura']; key = f"{s}:{w['aya']}"
        ts = tiles(w['surface'], opening=(s, w['aya'], w['word']) in opening)
        b = count(ts); base_by[s - 1] += b
        for r in delta:
            d = count(ts, {r}) - b
            if d:
                delta[r] += d; by[r][s - 1] += d
                e = seen[r].setdefault(w['surface'], [0, key]); e[0] += d
        if key in samples:
            samples[key].append(ts); texts[key].append(w['surface'])
    bas = tiles(BASMALA.replace(' ', ''))
    bas_base = count(bas)
    bas_with = {r: count(bas, {r}) - bas_base for r in delta if count(bas, {r}) != bas_base}
    for s in range(2, 115):
        if s != 9:
            by['basmala'][s - 1] = bas_base
    n_bas = bas_base * 112
    base = sum(base_by)

    def examples(r, many=4):
        top = sorted(seen[r].items(), key=lambda kv: -abs(kv[1][0]))[:many]
        return [{'w': w, 'n': c, 'k': k} for w, (c, k) in top]

    rules = {r: {'n': delta[r], 'bySurah': by[r], 'ex': examples(r)} for r in delta}
    rules['basmala'] = {'n': n_bas, 'bySurah': by['basmala'], 'ex': [{'w': BASMALA, 'n': 112, 'k': '1:1'}],
                        'with': {r: v * 112 for r, v in bas_with.items()},   # the Basmala's own doubled letters and small alif
                        'tiles': [tiles(x) for x in BASMALA.split()]}
    return {
        'base': base,
        'baseBySurah': base_by,
        'rules': rules,
        'samples': [{'k': k, 'text': texts[k], 'words': samples[k]} for k in SAMPLES],
        'totals': {'printed': base, 'firstMushaf': base + delta['hamza']},
        'reported': REPORTED,
    }

def total(lc, on=()):
    """The whole Quran's letters with the rules in `on` switched on (the Basmala's own letters included)."""
    on = set(on); R = lc['rules']
    t = lc['base'] + sum(R[r]['n'] for r in on)
    if 'basmala' in on:
        t += sum(v for r, v in R['basmala']['with'].items() if r in on)
    return t

if __name__ == '__main__':
    lc = build()
    print('base', lc['base'])
    for r in RULES:
        print('  %-11s %+8d' % (r, lc['rules'][r]['n']), [e['w'] for e in lc['rules'][r]['ex'][:3]])
    print('basmala with', lc['rules']['basmala']['with'])
    print('totals', lc['totals'])
