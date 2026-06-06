# -*- coding: utf-8 -*-
"""Recompute every corpus-derived dataset the v1 analysis pages needed, on the
authoritative corpus. Everything here replaces a number that was wrong in v1
(which reported 6348 verses / 56108 words).

Feeds: Overview, Word Analysis, Mecca vs Medina, Letter Frequency, Divine
Pronouns, Data-Driven Insights, NLP Explorer, Waw Miracle.
"""
import os, json
from collections import Counter
from .corpus import normalize, _read_rows, CONTENT_POS

META = os.path.join(os.path.dirname(__file__), '..', 'sources', 'surah_meta.json')
ARABIC_LETTERS = set('ابتثجحخدذرزسشصضطظعغفقكلمنهويةءؤئى')

def _surah_meta():
    return {m['n']: m for m in json.load(open(META, encoding='utf-8'))}

def build(words, verses_display):
    meta = _surah_meta()

    # ---- per-surah correct counts joined to names + place ----
    per = {}
    for w in words:
        d = per.setdefault(w['sura'], {'verses': set(), 'words': 0})
        d['verses'].add(w['aya']); d['words'] += 1
    surah_meta = []
    for n in sorted(per):
        m = meta.get(n, {})
        surah_meta.append({'n': n, 'ar': m.get('ar', str(n)), 'en': m.get('en', str(n)),
                           'place': m.get('p', ''), 'verses': len(per[n]['verses']),
                           'words': per[n]['words']})

    # ---- Mecca vs Medina ----
    mecca = [s for s in surah_meta if s['place'] == 'Mecca']
    medina = [s for s in surah_meta if s['place'] == 'Medina']
    def agg(group):
        v = sum(s['verses'] for s in group); wd = sum(s['words'] for s in group)
        return {'surahs': len(group), 'verses': v, 'words': wd,
                'avgWordsPerVerse': round(wd / v, 2) if v else 0}
    mecca_medina = {'mecca': agg(mecca), 'medina': agg(medina)}

    # ---- word frequency (surface + lemma + root) ----
    surf = Counter(w['norm'] for w in words if w['norm'])
    lem = Counter(w['lemma'] for w in words if w['lemma'])
    root = Counter(w['root'] for w in words if w['root'])
    top_surface = [{'w': k, 'c': c} for k, c in surf.most_common(60)]
    top_lemma = [{'w': k, 'c': c} for k, c in lem.most_common(60)]
    top_roots = [{'w': k, 'c': c} for k, c in root.most_common(60)]

    # ---- unique words + hapax (distinct normalized surface forms) ----
    unique_words = len(surf)
    hapax = sum(1 for c in surf.values() if c == 1)
    distinct_lemmas = len(lem)
    distinct_roots = len(root)

    # ---- letter frequency (on de-diacritized text) ----
    letters = Counter()
    total_letters = 0
    for w in words:
        for ch in w['norm']:
            if ch in ARABIC_LETTERS:
                letters[ch] += 1; total_letters += 1
    letter_freq = [{'l': k, 'c': c} for k, c in letters.most_common()]

    # ---- n-grams on normalized words, within each verse ----
    bi = Counter(); tri = Counter()
    cur = None; seq = []
    for w in words:
        key = (w['sura'], w['aya'])
        if key != cur:
            cur = key; seq = []
        seq.append(w['norm'])
        if len(seq) >= 2: bi[seq[-2] + ' ' + seq[-1]] += 1
        if len(seq) >= 3: tri[seq[-3] + ' ' + seq[-2] + ' ' + seq[-1]] += 1
    bigrams = [{'w': k, 'c': c} for k, c in bi.most_common(40)]
    trigrams = [{'w': k, 'c': c} for k, c in tri.most_common(40)]

    # ---- Waw conjunction + huwa pronoun, from segment level (one pass) ----
    WAW = 'و'           # و
    HUWA = 'هو'    # هو
    waw = 0; pron_huwa = 0
    for r in _read_rows():
        nf = normalize(r['form'])
        if nf == WAW and 'CONJ' in r['feats']:
            waw += 1
        elif nf == HUWA:
            pron_huwa += 1

    return {
        'surahMeta': surah_meta,
        'meccaMedina': mecca_medina,
        'topWordsSurface': top_surface,
        'topWordsLemma': top_lemma,
        'topRoots': top_roots,
        'uniqueWords': unique_words,
        'hapax': hapax,
        'distinctLemmas': distinct_lemmas,
        'distinctRoots': distinct_roots,
        'letterFreq': letter_freq,
        'totalLetters': total_letters,
        'bigrams': bigrams,
        'trigrams': trigrams,
        'wawCount': waw,
        'huwaCount': pron_huwa,
    }
