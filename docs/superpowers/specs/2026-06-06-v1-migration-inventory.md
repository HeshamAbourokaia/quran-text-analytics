# v1 -> v2 Migration Inventory

Master checklist. v2 must be a **superset** of v1: every v1 page and content asset
carries over (rebuilt on the corrected corpus where its numbers came from the buggy
data), plus the new features we designed. Nothing is dropped.

Status legend: `done` shipped in v2 | `port` move over, content unchanged |
`recompute` rebuild its numbers on the authoritative corpus | `new` net-new feature.

## Pages (24 in v1)

| # | Page | Section | Status | Notes |
|---|------|---------|--------|-------|
| 0 | Overview | quran | recompute | KPIs + surah chart on corrected 6,236 verses / 77,429 words |
| 1 | Word Analysis | stats | recompute | top words by surface AND by lemma (new) |
| 2 | Mecca vs Medina | stats | recompute | verse/word splits on corrected counts |
| 3 | Emotional Profiling | linguistics | port + recompute | keep lexicon; recompute frequencies |
| 4 | Waw Miracle | miracles | port | structural feature, presentation refresh |
| 5 | Letter Frequency | stats | recompute | per-letter counts from corpus |
| 6 | Divine Pronouns | linguistics | recompute | pronoun-of-Allah counts via morphology |
| 7 | Antonym Pairs | linguistics | done (merge) | folded into Claim Auditor (claimed vs verified) |
| 8 | Calendar Claims | stats | done (merge) | day=365 / month=12 now in Claim Auditor |
| 9 | Abjad Numerals | miracles | port | calculator logic is self-contained |
| 10 | Scientific References | linguistics | port | curated content list |
| 11 | Data-Driven Insights | stats | recompute | the `insights` cards recomputed on corpus |
| 12 | Word Symmetries | stats | done (merge) | pair symmetries now in Claim Auditor |
| 13 | Number 19 Miracle | miracles | port | self-contained computation, verify on corpus |
| 14 | Structural Miracles | miracles | recompute | surah/verse structure facts on corrected data |
| 15 | Word Search | quran | new (upgrade) | add lemma + root search to surface search |
| 16 | Quran Reader | quran | port + corrected text | Uthmani from corpus, tashkeel display |
| 17 | Advanced Analytics | linguistics | recompute | PCA / revelation-order views on corpus |
| 18 | NLP Explorer | linguistics | recompute | word cloud, n-grams, concordance on corpus |
| 19 | Stories Index | library | port (verbatim) | ~69 stories, content carried to web/content/ |
| 20 | Lessons Index | library | port (verbatim) | ~76 lessons |
| 21 | Du'a Index | library | port (verbatim) | ~151 du'as |
| 22 | Scholarly Insights (Tafsir) | library | port (verbatim) | tafsir insights, 113 KB |
| 23 | Knowledge Graph | library | port | node/edge data still inline in v1 app.html; extract during port |

## New features (designed, not in v1)

| Feature | Status | Notes |
|---|---|---|
| Claim Auditor | done | claimed vs verified vs raw for every word-count claim |
| Tawafuq Mushaf Explorer | new | 604-page / 15-line Madani page grid, alignment highlights |
| Alifi Mushaf Viewer | new | scanned pages, Alif-column highlight overlay |

## Data assets to carry or recompute

| Asset | Source in v1 | Plan |
|---|---|---|
| Verse text (Uthmani + tashkeel) | VERSES_DATA, QURAN_TASHKEEL (inline) | replace with corpus-derived text (correct 6,236) |
| Surah stats | DATA.surahStats (inflated) | recomputed, correct (done in stats.json) |
| Top words | DATA.topWords | recompute by surface + lemma |
| Letter frequency | DATA.letterFreq | recompute |
| Antonym / symmetry pairs | DATA.antonymPairs | merged into claims registry |
| Emotion lexicon | inline | carry lexicon, recompute counts |
| Abjad values | inline | carry (static mapping) |
| Insights cards | `insights` array | recompute numbers |
| NLP (cloud / n-gram / concordance) | computed inline | recompute on corpus |
| Stories / Lessons / Du'as / Tafsir | 4 JS files | carried verbatim to web/content/ |
| Knowledge graph | inline in app.html | extract + carry |
| Advanced analytics (PCA, revelation order) | inline | recompute |

## Build order (revised)

- Phase 1 (done): corpus + Claim Auditor.
- Phase 2a: recompute all corpus-derived datasets in data-build (top words by lemma + surface, letter freq, Mecca/Medina, insights, NLP inputs) and emit to web data.
- Phase 2b: word search (surface/lemma/root) + Quran Reader on corrected text.
- Phase 2c: port the analysis/miracle pages (0-14, 17, 18) onto the recomputed data.
- Phase 2d: port the library pages (19-23) verbatim with the new shell.
- Phase 3: tawafuq Mushaf explorer + Alifi viewer; web + Electron packaging.
