# Quran Text Analytics v2 - Design Spec

- **Date:** 2026-06-06
- **Status:** Approved (pending written-spec review)
- **Owner:** Hesham Abourokaia
- **Supersedes:** the single-file `electron-app/app.html` (v1)

---

## 0. Context and problem

The current app (`electron-app/app.html`, ~5,160 lines, Vue 3 + Plotly, single file) cannot reproduce the famous Quran word-count claims when a user searches, and several of its core statistics are wrong. Root causes found during evaluation:

1. **Methodology gap.** The famous counts (day = 365, month = 12, devil = 88) are curated lemma counts with specific include/exclude rules. The v1 search is a literal substring / whole-word matcher, so searching `يوم` returns ~451 (substring) or 217 (whole word), never 365. The "Verify yourself" button can therefore never land on a claimed number.
2. **Data-correctness bugs.** The statistics layer is computed from a different, buggy source than the searchable text:
   - `totalVerses` shows **6,348**; the correct figure is **6,236** (per-surah basmalas counted as verses, inflating by 112).
   - `totalWords` shows **56,108**; the real figure is about **77,430** (an independent token count of the same text gave 77,878).
   - Per-surah verse counts are off by one (Al-Baqarah shows 287, correct is 286).
3. **Normalization gaps.** `normalizeSearch` strips the main vowel marks but misses the Quranic small-high marks (U+06D6-U+06ED, U+06E2/06E5/06E6), so some words do not reduce to a clean form.

A user-supplied YouTube video ("Quran's Miracle You'll Hear for the First Time", *Towards Eternity*, 1183s) adds a large set of new requirements: the visual / typographic alignment (tawafuq) phenomena of specific hand-written Mushafs, plus additional numeric claims. The user wants all of these ideas in the app, built on the real authoritative Quran and on the specific aligned Mushaf the video shows.

## 1. Goals and non-goals

**Goals**
- Rebuild on an authoritative, morphology-tagged corpus so counts are correct and reproducible.
- Make every famous claim verifiable: show **claimed vs verified vs raw** side by side, with a full audit trail.
- Add the video's ideas: the numeric word/surah claims AND an interactive Mushaf alignment explorer for the specific aligned copy the video discusses.
- Ship one codebase to two targets: a public website and the existing Mac Electron app, fully offline.
- Lock correctness with tests so numbers cannot silently drift again.

**Non-goals**
- No runtime network calls. All data is precomputed and bundled.
- Not attempting to reproduce manuscripts we cannot source as data at pixel fidelity; where exact layout data is unavailable (Hunsari, Alfi copies) we use reconstructed diagrams clearly labelled as illustrative.
- Not a theological argument engine. The app presents data honestly and reverently and lets the reader judge.

## 2. Locked decisions

| Decision | Choice |
|---|---|
| Scope | Full rebuild |
| Engine | Approach A: morphology-tagged corpus + build-time precomputation + declarative claim rules |
| Verification display | Claimed vs Verified vs Raw, side by side, with audit trail |
| Delivery | Web app + Electron from one source |
| Build shape | Python build pipeline -> precomputed data; component-based Vue frontend; test suite; ships as a bundled offline app |
| Visual alignment | Full interactive Mushaf explorer (real 604-page / 15-line Madani layout) |
| Honesty stance | Rigorous but reverent: celebrate the real patterns, stay honest about the shaky ones |

## 3. Architecture

Single repo, three parts:

```
quran-analytics/
  data-build/        # Python pipeline: fetch -> validate -> compute -> emit
    sources/         # downloaded source corpora (gitignored, checksummed)
    pipeline/        # python modules (corpus, morphology, layout, claims, stats)
    out/             # emitted versioned JSON + data-manifest.json
    tests/           # golden-file + invariant tests
  web/               # Vite + Vue 3 + Plotly/D3 frontend (consumes data-build/out)
    src/components/
    src/pages/
    src/engine/      # browser-side search over precomputed token index
    src/data/        # bundled precomputed JSON (copied from data-build/out at build)
    tests/
  electron/          # thin shell loading the built web assets
  docs/
```

- **Build flow:** `data-build` downloads sources once (cached, checksummed), validates invariants, computes the token table, statistics, claim audits, and alignment indexes, then emits versioned JSON plus a provenance manifest. `web` bundles that JSON. `vite build` produces the website; `electron` wraps the identical built output.
- **Offline-first:** everything needed at runtime is in the bundle. No API calls.
- **Data contract:** the frontend depends only on the emitted JSON schema, not on the Python internals. The schema is versioned in `data-manifest.json`.

## 4. Data foundation

Two distinct things the user asked for: **the real Quran** (authoritative reference text + morphology) and **the video's Quran** (the specific aligned Mushaf layout).

### 4.1 The real Quran (authoritative reference)
- **Text:** Tanzil Uthmani (Hafs) for display, Tanzil simple-clean for search. Canonical 6,236 verses, 114 surahs. This is the reference "real Quran" for all counting and reading.
- **Morphology:** the Quranic Arabic Corpus (QAC) morphology dataset. Every word carries location, surface form, lemma, root, and part of speech. This is what makes lemma and root counting possible and what separates `malak` (angel) from `malik` (king) and `mulk` (dominion).

### 4.2 The video's Quran (the aligned Mushaf)
- **Primary text-grid (interactive):** the canonical 604-page, 15-line Madani Mushaf in the Hafiz Osman hattat layout, which is the copy whose word alignments the video and Bediuzzaman describe (the "tawafuqlu" Mushaf). We source the word-to-(page, line) mapping from the QUL / QPC (King Fahd Complex) Madani Mushaf layout data. This drives the alignment explorer.
- **Quran Majeed Alfi (the "Alifi" Mushaf) - first-class visual viewer.** The Lahore copy where every line of every page begins with the letter Alif (21 lines per page; the video cites 221 pages, a Super Big large-format edition). Its all-Alif effect is a property of the calligrapher's exact line-breaking and cannot be reconstructed from open text data, so it is realized as a **page-image viewer with an Alif-column highlight overlay**: actual scanned pages rendered in a flip viewer, with the leading-Alif of every line highlighted and an optional guide-line drawn down the right margin to show the alignment. Sourced from a legal scan of the matching edition (Internet Archive has full scans; exact edition to be pinned at build). See 4.4 for sourcing and licensing.
- **Hafiz Hunsari (11-line palindrome) - explainer.** The 11-line Mushaf whose first letters read symmetrically top-to-bottom (Fa, Alif, Lam, Lam, Alif ... and mirrored). Realized as a narrative page with a reconstructed, clearly-labelled diagram of the letter symmetry, upgraded to a page-image viewer if a legal scan of that specific copy can be sourced.

### 4.3 Alifi Mushaf image sourcing and licensing
- **Images:** scanned pages of the matching edition (e.g. the Internet Archive "Alifi / Ali Fil Quran" scan, or a cleaner scan of the 21-line Super Big edition if found). Pinned and checksummed like other sources. We confirm the edition matches the video before use.
- **Overlay data:** because every line starts with Alif by construction, the overlay does not need per-word OCR; the Alif column is the page's right margin (RTL). A light per-page calibration (top/bottom margin, line pitch) lets the overlay draw the highlight and guide-line accurately. This calibration is stored as small JSON, not derived from the publisher's text.
- **Licensing:** these are a publisher's print with no clear open license. Policy: **full page-image viewer in the offline Electron app** (personal, educational, non-redistributing); on the **public website, show a curated set of annotated sample pages with attribution and a link to the source/seller**, not the full Mushaf, unless a clearly-licensed or public-domain scan is secured. This is a deliberate, reversible default the owner can change.

### 4.4 Provenance, licensing, validation
- Each source is pinned to a specific version and checksummed at download. `data-manifest.json` records source name, version, URL, checksum, and license.
- Licensing: QAC morphology (GNU / CC-BY style, requires attribution), Tanzil (its stated terms), QUL/QPC layout (open). Attribution surfaced in an in-app credits page.
- **Hard invariants (build fails if any is false):** 114 surahs; 6,236 verses; total words within tolerance of ~77,430; 604 Mushaf pages; basmala handled once (no inflation); every token maps to a valid (page, line); morphology coverage = 100% of tokens. These gates directly prevent the v1 6,348 / 56,108 bugs.

## 5. Counting and claim engine

### 5.1 Token table
One canonical table; every word row carries: surah, verse, wordIndex, page, line, surfaceForm, normalizedForm, lemma, root, pos.

### 5.2 Search and counting
- Surface-form match: substring, whole-word, prefix, suffix.
- Lemma match and root match (from morphology).
- Correct Unicode normalization, including the small-high marks v1 missed.

### 5.3 Claims registry (declarative)
Each claim is a rule object computed at build time into: `claimed`, `verified` (per rule), `rawSubstring`, `rawWholeWord`, and `auditTrail` (the exact counted and excluded token locations). The UI renders all four numbers and a drill-down to every verse.

Claims to implement (all from the video, plus the pairs the user already raised):

| id | Claim | Claimed | Verification approach | Early finding |
|---|---|---|---|---|
| day-365 | yawm (day), singular | 365 | lemma yawm, singular, exclude dual / yawma'idhin / possessive forms; drop al-Qayyum false match | Verified 365 under this rule |
| month-12 | shahr (month), singular | 12 | lemma shahr, singular, exclude plural ashhur and dual | Verified 12 |
| devil-88 | shaytan (devil) | 88 | lemma shaytan, singular + plural | Verified 88 (70 + 18) |
| angel-88 | malak (angel) | 88 | lemma malak (morphology separates malik/mulk) | Surface plural = 73; lemma count to be confirmed by morphology |
| paradise-hell-77 | Jannah / Jahannam | 77 / 77 | lemma counts | To verify in build |
| man-woman-24 | rajul / imra'a | 24 / 24 | lemma counts | To verify in build |
| jesus-adam-24 | Isa / Adam | 24 / 24 | lemma counts | To verify in build |
| baqarah-286 | Al-Baqarah: Allah 282 + huwa(->Allah) 4 = 286 verses | 286 | count "Allah" in surah 2 + the 4 pronoun-of-Allah cases; compare to verse count 286 | To verify in build |
| allah-464-triple | An-Nisa + Ma'idah + An'am: verses 464 = "Allah" 464 | 464 | sum verse counts of surahs 4,5,6; count "Allah" across them | To verify in build |
| allah-doubling | "Allah" in surahs 2-6 = 2x surahs 7-11 = 2x surahs 12-16 | doubling | count "Allah" in each group; report ratios | To verify in build |
| bediuzzaman-totals | Allah 2,806 / Rabb 846 / Rahim 220 / Rahman 156 | as stated | count by the definition Bediuzzaman used (attached forms) and by lemma; show both | To verify in build |

Where a claim does not reproduce exactly, the card shows the honest verified number and a one-line note on why (counting method, homograph, attached forms). This is the point of the side-by-side design.

## 6. Mushaf alignment explorer

Real page-grid renderer for the 604-page, 15-line Madani layout, right-to-left, Uthmani script (QCF / Amiri font).

- **Vertical alignment ("beads on a fiber"):** select a word, highlight every occurrence on the page and draw alignment guides. Reproduces p35 Rabb x5, p62-63 Allah x9 each, p259 Rabb x9, **p422 Allah x15** (call out its verse 33:41 "remember Allah much"), and prophet-name stacks p327 (Sulayman/Dawud), p449 (Musa/Harun/Ishaq), p19 (Ibrahim x3), p235 (Yusuf x4).
- **Facing-page mode:** two pages side by side, cross-page matches highlighted (p82-83 Allah x4 each).
- **Sheet front/back mode:** overlay recto and verso of one physical sheet (p289-290 "Quran"; p235 Yusuf aligns with Jamil/beautiful on the reverse).
- **Long-range horizontal alignment:** the Qitmir example (p294 "and their dog" on line 7 aligns with "Qitmir" 141 pages later on line 7), with an edge-on closed-Mushaf schematic.
- **Facing-page meaning answer:** Ashab al-Kahf "a day or part of a day" answered by "300 years and 9 more" on the opposite page (p294).
- **Verse-pair gallery:** the four distant similar-meaning alignments p342/489, p71/511, p112/286, p219/415, each rendered with both pages and the aligned line highlighted.
- **Alifi Mushaf visual viewer:** a dedicated page for the Quran Majeed Alfi. Real scanned pages in a flip viewer, every line's leading Alif highlighted and a right-margin guide-line drawn to show the all-Alif alignment, plus the story (21-line, all-Alif, Lahore, 12 years, continuous fasting). Full pages offline; curated annotated sample pages on the public website (see 4.3).
- **Three-Mushaf context:** Hafiz Osman (15-line, the shortest-surah-as-line / longest-verse-as-page measurement story, 600 pages, no verse split across pages), Hunsari (11-line palindrome of first letters, diagram or scan), and the Alifi viewer above, tied together as one "aligned Mushafs" section.
- **Reverent honesty layer:** a standing note that these alignments are a property of this specific calligraphic Mushaf, beautifully realized, which is a different category of claim from the abstract-text counts. Framed respectfully.

## 7. Frontend structure

Component-based Vue. Shared components: `PageGrid`, `AlignmentOverlay`, `ClaimCard` (claimed/verified/raw), `AuditTrail`, `WordSearch` (form/lemma/root toggle), `Concordance`, chart wrappers. Bilingual Arabic / English with runtime toggle, RTL-correct. Bright, polished, executive-ready aesthetic. Worthwhile v1 pages (reader, surah stats, knowledge graph, stories, duas, lessons, tafsir) are kept but rebuilt on the corrected data.

## 8. Error handling and validation

- **Build:** checksums on sources; invariant assertions that fail the build; `data-manifest.json` with versions and provenance.
- **Runtime:** single versioned data bundle; graceful loading and empty states; debounced search; virtualized long lists for concordance and audit trails.

## 9. Testing

- **Python golden-file tests** pin every claim's verified number and the global totals (6,236 verses, ~77,430 words, day-singular = 365 under its rule, 604 pages). Numbers cannot drift silently.
- **Frontend:** component tests for `ClaimCard` and `PageGrid`; a smoke test that every route renders; the visual audit checklist.

## 10. Phasing

- **Phase 0** - data pipeline + validation (authoritative corpus + the Madani layout, all bugs fixed).
- **Phase 1** - counting / claim engine + numerical auditor UI (all word and surah claims, verified).
- **Phase 2** - Mushaf alignment explorer (page grid, highlights, the specific examples).
- **Phase 3** - three-Mushaf explainers, polish, port remaining pages, web + Electron packaging.

## 11. Open questions and risks

- Exact open dataset for word-level (page, line) positions in the 15-line Madani Mushaf must be pinned; if line-level granularity is partial, the alignment guides may need a one-time manual correction pass for the showcased pages.
- Hunsari layout may not exist as open data; fallback is a reconstructed diagram labelled illustrative.
- The Alifi Mushaf is realized via page images (no open text layout reproduces the all-Alif effect). The exact edition matching the video (21-line, ~221-page Super Big) must be pinned; the Internet Archive scan found so far is 568 pages, a different edition. Scan licensing is unclear, so the public website ships curated annotated sample pages plus attribution rather than the full Mushaf unless a clearly-licensed scan is secured.
- Bediuzzaman's totals use a specific counting definition (attached pronominal forms); we show both his definition and the strict lemma count to stay honest.

## 12. Attribution and licensing

In-app credits page lists every source (Tanzil, Quranic Arabic Corpus, QUL/QPC Madani layout) with version and license. The morphology corpus attribution requirement is honored.
