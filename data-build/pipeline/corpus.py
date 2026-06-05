# -*- coding: utf-8 -*-
"""Authoritative corpus loader built on the Quranic Arabic Corpus morphology.

Source: data-build/sources/quran-morphology.txt
Each line: LOCATION<TAB>FORM<TAB>POS<TAB>FEATURES
  LOCATION = sura:aya:word:segment   FEATURES contains LEM:<lemma> and ROOT:<root>

Words are reconstructed by grouping segments on (sura, aya, word). The stem
segment (the one carrying ROOT, else a content lemma) supplies lemma/root/pos.
"""
import os, re

SRC = os.path.join(os.path.dirname(__file__), '..', 'sources', 'quran-morphology.txt')

# Diacritic stripper (vowel marks, maddah, hamza marks, dagger alif, small-high marks).
TASHKEEL = re.compile('[ؐ-ًؚ-ٰٟۖ-ۭ࣓-ٰٖࣿ]')
def normalize(s):
    s = s.replace('﻿', '')
    s = TASHKEEL.sub('', s)
    for a in ('ٱ', 'آ', 'أ', 'إ'):  # alif-wasla/madda/hamza variants -> bare alif
        s = s.replace(a, 'ا')
    s = s.replace('ى', 'ي')  # alif maqsura -> ya
    return s.strip()

CONTENT_POS = {'N', 'PN', 'V', 'ADJ', 'IMPN', 'NUM'}

def _read_rows():
    rows = []
    with open(SRC, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if not line or not line[0].isdigit():
                continue
            parts = line.split('\t')
            if len(parts) < 3 or ':' not in parts[0]:
                continue
            loc = parts[0].split(':')
            if len(loc) != 4:
                continue
            feats = parts[3] if len(parts) > 3 else ''
            rows.append({
                'sura': int(loc[0]), 'aya': int(loc[1]),
                'word': int(loc[2]), 'seg': int(loc[3]),
                'form': parts[1], 'pos': parts[2], 'feats': feats,
            })
    return rows

def _feat(feats, key):
    m = re.search(key + r':([^|]+)', feats)
    return m.group(1) if m else None

def load_words():
    """Return word-level tokens with lemma/root/pos and positions."""
    rows = _read_rows()
    groups = {}
    order = []
    for r in rows:
        k = (r['sura'], r['aya'], r['word'])
        if k not in groups:
            groups[k] = []
            order.append(k)
        groups[k].append(r)
    words = []
    for k in order:
        segs = sorted(groups[k], key=lambda x: x['seg'])
        surface = ''.join(s['form'] for s in segs)
        # choose stem: prefer a segment with ROOT, else content POS with LEM, else any LEM
        stem = next((s for s in segs if 'ROOT:' in s['feats']), None)
        if stem is None:
            stem = next((s for s in segs if s['pos'] in CONTENT_POS and 'LEM:' in s['feats']), None)
        if stem is None:
            stem = next((s for s in segs if 'LEM:' in s['feats']), segs[0])
        words.append({
            'sura': k[0], 'aya': k[1], 'word': k[2],
            'surface': surface,
            'norm': normalize(surface),
            'lemma': _feat(stem['feats'], 'LEM'),
            'lemma_norm': normalize(_feat(stem['feats'], 'LEM') or ''),
            'root': _feat(stem['feats'], 'ROOT'),
            'pos': stem['pos'],
        })
    return words

def load_verses(words=None):
    """Return {(sura,aya): verse_text} reconstructed from word surfaces."""
    words = words or load_words()
    verses = {}
    for w in words:
        verses.setdefault((w['sura'], w['aya']), []).append(w['surface'])
    return {k: ' '.join(v) for k, v in verses.items()}

if __name__ == '__main__':
    ws = load_words()
    suras = {w['sura'] for w in ws}
    ayas = {(w['sura'], w['aya']) for w in ws}
    print('words:', len(ws), '| suras:', len(suras), '| verses:', len(ayas))
