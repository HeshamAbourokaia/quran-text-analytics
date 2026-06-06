# -*- coding: utf-8 -*-
"""Compile the 604-page Madani Mushaf layout (zonetecde/mushaf-layout) into a
compact structure joined to morphology lemmas, for the tawafuq explorer.

Output (web/content/mushaf.json): { "<page>": [ {n,type,text?,words:[{loc,t,l}]} ] }
  loc = sura:aya:word   t = Uthmani word text   l = normalized lemma (for highlight)

Run:  python3 -m pipeline.mushaf      (from data-build/)
"""
import os, json, glob
from .corpus import load_words, normalize

SRC_DIR = os.path.join(os.path.dirname(__file__), '..', 'sources', 'mushaf')
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'content', 'mushaf.json')

def loc_to_lemma():
    m = {}
    for w in load_words():
        m[f"{w['sura']}:{w['aya']}:{w['word']}"] = normalize(w['lemma']) if w['lemma'] else ''
    return m

def build():
    lem = loc_to_lemma()
    pages = {}
    joined = total = 0
    for f in sorted(glob.glob(os.path.join(SRC_DIR, 'page-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        lines = []
        for ln in d['lines']:
            row = {'n': ln.get('line'), 'type': ln.get('type')}
            if ln.get('type') in ('surah-header', 'basmala'):
                row['text'] = ln.get('text', '')
                if ln.get('surah'):
                    row['surah'] = ln['surah']
            words = []
            for w in ln.get('words', []):
                loc = w.get('location', '')
                l = lem.get(loc, '')
                words.append({'loc': loc, 't': w.get('word', ''), 'l': l})
                total += 1
                if l:
                    joined += 1
            if words:
                row['words'] = words
            lines.append(row)
        pages[str(d['page'])] = lines
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(pages, fh, ensure_ascii=False, separators=(',', ':'))
    size = os.path.getsize(OUT) // 1024
    print(f"pages: {len(pages)} | words: {total} | lemma-joined: {joined} "
          f"({100*joined//total}%) | mushaf.json: {size} KB")
    return pages

if __name__ == '__main__':
    build()
