# -*- coding: utf-8 -*-
"""Build pipeline entry point.

Loads the authoritative morphology corpus, validates hard invariants, computes
statistics and claim audits, and emits versioned JSON + a provenance manifest to
data-build/out/. Prints a verified scorecard.

Run:  python3 build.py
"""
import os, json, hashlib, sys
from pipeline.corpus import load_words, load_verses, normalize, SRC
from pipeline import claims as claims_mod
from pipeline import datasets as datasets_mod
from pipeline import analytics as analytics_mod

OUT = os.path.join(os.path.dirname(__file__), 'out')
DATA_VERSION = '2.0.0'

# Hard invariants. Build fails loudly if the corpus is not the real Quran.
EXPECT = {'suras': 114, 'verses': 6236, 'words': 77429}

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    os.makedirs(OUT, exist_ok=True)
    words = load_words()

    suras = sorted({w['sura'] for w in words})
    verse_keys = {(w['sura'], w['aya']) for w in words}
    stats = {'suras': len(suras), 'verses': len(verse_keys), 'words': len(words)}

    # validate
    problems = [f"{k}: got {stats[k]} expected {v}" for k, v in EXPECT.items() if stats[k] != v]
    if problems:
        print('INVARIANT FAILURE:\n  ' + '\n  '.join(problems))
        sys.exit(1)

    verses_display = load_verses(words)                       # {(s,a): uthmani text}
    verses_norm = {f"{s}:{a}": normalize(t) for (s, a), t in verses_display.items()}

    # per-surah verse + word counts (correct, no basmala inflation)
    surah_stats = {}
    for w in words:
        d = surah_stats.setdefault(w['sura'], {'verses': set(), 'words': 0})
        d['verses'].add(w['aya']); d['words'] += 1
    surah_stats = {s: {'verses': len(d['verses']), 'words': d['words']} for s, d in surah_stats.items()}

    claim_rows = claims_mod.compute(words, verses_norm)
    datasets = datasets_mod.build(words, verses_display)
    analytics = analytics_mod.build(words, datasets['surahMeta'])

    # emit
    corpus_json = {f"{s}:{a}": t for (s, a), t in verses_display.items()}
    _write('corpus.json', corpus_json)
    _write('claims.json', claim_rows)
    _write('datasets.json', datasets)
    _write('analytics.json', analytics)
    _write('stats.json', {'totals': stats, 'surahStats': surah_stats})
    manifest = {
        'dataVersion': DATA_VERSION,
        'totals': stats,
        'sources': [{
            'name': 'Quranic Arabic Corpus morphology',
            'file': os.path.basename(SRC),
            'sha256': sha256(SRC),
            'license': 'GNU/CC-BY (attribution required)',
        }],
        'emitted': ['corpus.json', 'claims.json', 'stats.json'],
    }
    _write('manifest.json', manifest)

    # also emit an inlined data module the offline frontend can load with no server
    web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
    os.makedirs(web_dir, exist_ok=True)
    payload = {'stats': {'totals': stats, 'surahStats': surah_stats},
               'claims': claim_rows, 'datasets': datasets, 'analytics': analytics, 'manifest': manifest}
    with open(os.path.join(web_dir, 'data.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.QURAN_DATA = ')
        json.dump(payload, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write(';\n')

    # verse text for the Reader (Uthmani display) keyed "sura:aya"
    with open(os.path.join(web_dir, 'corpus.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.QURAN_VERSES = ')
        json.dump(corpus_json, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write(';\n')

    # compact word index for surface/lemma/root search (parallel arrays)
    widx = {'key': [], 'norm': [], 'lemma': [], 'root': [], 'surface': []}
    for w in words:
        widx['key'].append(f"{w['sura']}:{w['aya']}")
        widx['norm'].append(w['norm'])
        widx['lemma'].append(normalize(w['lemma']) if w['lemma'] else '')
        widx['root'].append(normalize(w['root']) if w['root'] else '')
        widx['surface'].append(w['surface'])
    with open(os.path.join(web_dir, 'words.js'), 'w', encoding='utf-8') as fh:
        fh.write('window.QURAN_WORDS = ')
        json.dump(widx, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write(';\n')

    _scorecard(stats, claim_rows)

def _write(name, obj):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
        json.dump(obj, fh, ensure_ascii=False, separators=(',', ':'))

def _scorecard(stats, rows):
    print('\nAUTHORITATIVE CORPUS  suras=%(suras)d  verses=%(verses)d  words=%(words)d' % stats)
    print('(v1 app showed verses=6348, words=56108 - both fixed)\n')
    head = '%-16s %8s %8s %8s %8s %8s  %s' % (
        'CLAIM', 'claimed', 'lemma', 'rule', 'rawSub', 'rawWord', 'verdict')
    print(head); print('-' * len(head))
    for r in rows:
        v = r['verifiedLemma']
        rule = '' if r['verifiedRule'] is None else str(r['verifiedRule'])
        if v == r['claimed']:
            verdict = 'EXACT by lemma'
        elif rule and int(rule) == r['claimed']:
            verdict = 'matches via rule'
        else:
            verdict = 'differs'
        print('%-16s %8d %8d %8s %8d %8d  %s' % (
            r['en'][:16], r['claimed'], v, rule, r['rawSubstring'], r['rawWholeWord'], verdict))

if __name__ == '__main__':
    main()
