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

# Madani Mushaf 604-page layout (word -> page/line, QPC glyphs) for tawafuq explorer
echo "Downloading Madani Mushaf layout..."
curl -fSL "https://github.com/zonetecde/mushaf-layout/archive/refs/heads/main.tar.gz" -o /tmp/mushaf.tgz
mkdir -p mushaf && tar -xzf /tmp/mushaf.tgz -C /tmp
cp /tmp/mushaf-layout-main/mushaf/page-*.json mushaf/ && rm -rf /tmp/mushaf-layout-main /tmp/mushaf.tgz
echo "Mushaf layout: $(ls mushaf | wc -l) pages. Then run: python3 -m pipeline.mushaf"
