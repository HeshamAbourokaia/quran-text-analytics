# Quran Corpus for Knowledge Graph

Source documents for a graphify-based knowledge graph of the Quran itself (not the code).

## Structure

- `surahs/` (114) - one per surah, with full Arabic + English verse text, themes, entities, and revelation phase
- `entities/` (36) - one per major named figure (25 prophets), other figures (Mary, Pharaoh, Iblis, Gabriel), place (7), and divine name (4)
- `themes/` (10) - one per scholarly thematic cluster
- `special/` (6) - distinctive structural patterns
- `timeline/` (5) - the five revelation phases (Early/Middle/Late Mecca + Early/Late Medina)
- `events/` (15) - major historical events from Cave of Hira through the Farewell Pilgrimage
- `asbab_nuzul/` (15) - classical occasions of revelation (change of qibla, slander of Aisha, etc.)
- `tafsir_traditions/` (8) - the major tafsir scholars referenced in the app
- `sciences/` (6) - Ulum al-Quran (sciences of the Quran)

Total: ~215 markdown documents covering text, history, scholarship, and structural patterns.

## Regenerate

```bash
python3 scripts/build_quran_corpus.py    # base layer (surahs, entities, themes, special)
python3 scripts/enrich_quran_corpus.py   # adds timeline, events, asbab_nuzul, tafsir_traditions, sciences
```

Re-running is idempotent (overwrites files in place).

## Ingest into graphify

```bash
cd quran_corpus
/graphify .
```
