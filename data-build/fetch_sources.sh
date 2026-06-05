#!/usr/bin/env bash
# Fetch authoritative source corpora into data-build/sources/.
# Quranic Arabic Corpus morphology (word-level lemma + root + POS, 6236 verses).
set -euo pipefail
cd "$(dirname "$0")/sources"
URL="https://raw.githubusercontent.com/mustafa0x/quran-morphology/master/quran-morphology.txt"
echo "Downloading QAC morphology..."
curl -fSL "$URL" -o quran-morphology.txt
shasum -a 256 quran-morphology.txt
echo "Done. Expected sha256: 742bfac59941b2cb09736d5b7aae694af50792261fb8450cbf6afafcc340645f"
