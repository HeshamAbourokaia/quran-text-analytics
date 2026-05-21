# Quran Corpus for Knowledge Graph

Source documents for a graphify-based knowledge graph of the Quran itself (not the code). Generated from the canonical Madani text + Sahih International English translation + scholarly thematic classification + curated named entity dictionary.

## Structure

- `surahs/` - 114 documents, one per surah, with full Arabic + English verse text and links to themes and entities
- `entities/` - One document per major named figure (25 prophets), place (7 places), and divine name (4 attributes), with verse anchors
- `themes/` - 10 documents, one per scholarly thematic cluster
- `special/` - 6 documents on distinctive structural patterns (Bismillah occurrences, Ar-Rahman refrain, Iron miracle, etc.)

## Regenerate

```bash
python3 scripts/build_quran_corpus.py
```

Re-running is idempotent (overwrites files in place). Source data lives in `data/surah/`, `data/translation/en/`, and `data/surah.json`.

## Ingest into graphify

```bash
cd quran_corpus
/graphify .
```

This produces `graphify-out/` containing the interactive graph, audit report, and raw JSON.
