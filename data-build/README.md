# data-build

Python pipeline that turns the authoritative Quran corpus into the precomputed
JSON the frontend consumes. No network access at runtime; everything is built here.

## Usage
```
./fetch_sources.sh        # download the morphology corpus into sources/
python3 build.py          # validate + emit out/*.json + print the scorecard
python3 tests/test_counts.py   # golden-file tests pin every number
```

## What it produces (out/)
- `corpus.json`   verses keyed "sura:aya" in Uthmani text (6,236 verses)
- `claims.json`   every claim with claimed vs verified-by-lemma vs raw counts + audit trail
- `stats.json`    correct totals and per-surah verse/word counts
- `manifest.json` data version + source provenance (sha256) + license

## Source
Quranic Arabic Corpus morphology (lemma + root + POS per word). Attribution
required; recorded in `manifest.json`. This single source gives the canonical
114 surahs / 6,236 verses / 77,429 words and the lemma layer that separates
homographs such as malak (angel) from mulk (dominion) and malik (king).
