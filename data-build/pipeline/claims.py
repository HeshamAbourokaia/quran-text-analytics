# -*- coding: utf-8 -*-
"""Declarative claim registry + engine.

Design note: we never hardcode fully-voweled Arabic lemma literals (they are
fragile to copy correctly). Instead each claim names a bare consonant skeleton,
and the engine selects the target lemma at runtime as the most frequent distinct
lemma whose normalized form equals that skeleton. This both avoids literal
corruption and inherently picks the right homograph (angel malak 88 outranks
dominion mulk 48 and king malik 15 under the same skeleton ملك).

Per claim we compute:
  claimed        - the figure as stated by the source (video / Bediuzzaman)
  verifiedLemma  - words whose stem-lemma is the selected target lemma
  verifiedRule   - optional curated count (singular-only) reproducing the figure
  rawSubstring   - substring hits of the surface skeleton in verse text
  rawWholeWord   - whole-word hits of the surface skeleton
All shown side by side. Nothing hidden.
"""
from collections import Counter
from .corpus import normalize

# Bare skeletons via the actual letters (these are de-voweled, so safe to write).
# 'lem' = skeleton of the dictionary lemma; 'surf' = skeleton as written in the
# Uthmani verse text (differs only where the rasm is defective, e.g. shaytan).
REGISTRY = [
    dict(id='day-365', en='Day (yawm)', key='day', lem='يوم', surf='يوم',
         claimed=365, pair=None, rule='singular',
         note_en='Lemma counts every form. The traditional 365 is the singular noun only, dropping the dual, the fused "that-day" word, and possessive forms.'),
    dict(id='month-12', en='Month (shahr)', key='month', lem='شهر', surf='شهر',
         claimed=12, pair=None, rule='singular-noplural',
         note_en='Lemma counts all forms. The traditional 12 is the singular noun only, dropping the plural "ashhur" and the dual.'),
    dict(id='devil-88', en='Devil (shaytan)', key='devil', lem='شيطان', surf='شيطن',
         claimed=88, pair='angel-88', rule=None,
         note_en='Exact by lemma: singular and plural share the lemma and total 88. Note a naive text search for شيطان finds 0 because the Uthmani rasm writes it شيطن.'),
    dict(id='angel-88', en='Angel (malak)', key='angel', lem='ملك', surf='ملك',
         claimed=88, pair='devil-88', rule=None,
         note_en='Exact by lemma. Morphology separates malak (angel, 88) from mulk (dominion) and malik (king); a plain text search cannot, which is why a naive count looks wrong.'),
    dict(id='hell-77', en='Hell (jahannam)', key='hell', lem='جهنم', surf='جهنم',
         claimed=77, pair='paradise-77', rule=None,
         note_en='Exact by lemma. Jahannam is an unambiguous proper noun for Hell.'),
    dict(id='paradise-77', en='Paradise (jannah)', key='paradise', lem='جنة', surf='جنة',
         claimed=77, pair='hell-77', rule=None,
         note_en='Lemma jannah also means "garden(s)", so it totals far above 77. The 77 figure counts only the Paradise sense, which needs meaning-level tagging.'),
    dict(id='man-24', en='Man (rajul)', key='man', lem='رجل', surf='رجل',
         claimed=24, pair='woman-24', rule=None,
         note_en='Lemma rajul (man), separated from rijl (foot). The man=woman=24 pairing does not hold under lemma counting.'),
    dict(id='woman-24', en="Woman (imra'a)", key='woman', lem='امرات', surf='امرات',
         claimed=24, pair='man-24', rule=None,
         note_en="Lemma imra'a. Not equal to man, and not 24."),
    dict(id='jesus-24', en='Jesus (Isa)', key='jesus', lem='عيسي', surf='عيسي',
         claimed=24, pair='adam-24', rule=None,
         note_en='Lemma Isa equals Adam. The parity holds; the figure is 25, not 24.'),
    dict(id='adam-24', en='Adam', key='adam', lem='ادم', surf='ادم',
         claimed=24, pair='jesus-24', rule=None,
         note_en='Lemma Adam equals Isa. The parity holds; the figure is 25, not 24.'),
    dict(id='allah-2806', en='Allah', key='allah', lem='الله', surf='الله',
         claimed=2806, pair=None, rule=None,
         note_en='Standard count of the name Allah is 2699 (this corpus). Bediuzzaman\'s 2806 uses a wider convention.'),
    dict(id='rabb-846', en='Lord (Rabb)', key='rabb', lem='رب', surf='رب',
         claimed=846, pair=None, rule=None,
         note_en='Lemma Rabb includes possessive forms (rabbi, rabbuka, rabbihim). The 846 figure counts a narrower set.'),
]

def _select_lemma(words, lem_skeleton):
    """Most frequent distinct lemma whose normalized form == skeleton."""
    counts = Counter()
    for w in words:
        if w['lemma'] and normalize(w['lemma']) == lem_skeleton:
            counts[w['lemma']] += 1
    if not counts:
        return None, 0
    lemma, n = counts.most_common(1)[0]
    return lemma, n

def _lemma_locs(words, lemma):
    return [[w['sura'], w['aya']] for w in words if w['lemma'] == lemma]

def _raw(verses_norm, skeleton):
    sub = whole = 0
    for t in verses_norm.values():
        i = 0
        while True:
            i = t.find(skeleton, i)
            if i < 0:
                break
            sub += 1
            i += len(skeleton)
        for tok in t.split():
            if tok == skeleton:
                whole += 1
    return sub, whole

_POSS = ('كم', 'هم', 'ها', 'نا', 'كن', 'هن')
def _singular_core(words, lemma, drop_plural_prefix=None):
    locs = []
    for w in words:
        if w['lemma'] != lemma:
            continue
        n = w['norm']
        if 'ئذ' in n:            # yawma'idhin compound
            continue
        if n.endswith('ين'):     # dual
            continue
        if n.endswith(_POSS):    # plural possessive
            continue
        if drop_plural_prefix and ('اشهر' in n):  # plural ashhur for month
            continue
        locs.append([w['sura'], w['aya']])
    return locs

def compute(words, verses_norm):
    out = []
    for c in REGISTRY:
        lem_skel = normalize(c['lem'])
        surf_skel = normalize(c['surf'])
        lemma, n = _select_lemma(words, lem_skel)
        sub, whole = _raw(verses_norm, surf_skel)
        rule_val = None
        if c['rule'] == 'singular' and lemma:
            rule_val = len(_singular_core(words, lemma))
        elif c['rule'] == 'singular-noplural' and lemma:
            rule_val = len(_singular_core(words, lemma, drop_plural_prefix=True))
        out.append({
            'id': c['id'], 'en': c['en'], 'ar': lemma or c['lem'], 'pair': c['pair'],
            'claimed': c['claimed'],
            'verifiedLemma': n,
            'verifiedRule': rule_val,
            'rawSubstring': sub,
            'rawWholeWord': whole,
            'lemma': lemma,
            'note_en': c['note_en'],
            'audit': _lemma_locs(words, lemma) if lemma else [],
        })
    return out
