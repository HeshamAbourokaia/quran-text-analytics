# Quran Text Analytics - Product Redesign (v3)

Date: 2026-07-18
Goal: turn the app from a 33-page feature dump into a sellable product.

## Problems found in the audit

1. Sidebar: 33 flat pages, 6 group headers, 11 NEW badges, emoji icons. Reads as a lab notebook, not a product.
2. Duplicated content: Word Symmetries and Antonym Pairs cover the same pairs, and they contradict each other (symmetry shows cited 145=145 as fact, antonyms shows verified 3 vs 270).
3. Coursework leakage: every Analytics Lab page opens with a university unit banner (course code, unit name, "Taught in" topics). Kills product credibility.
4. No hero inside the app: app.html (the shared link) boots straight into the dense Overview page.
5. Landing page (index.html) is English-only, has no product screenshot, and its hero stats animate from wrong-looking intermediate values.
6. Arabic mode gaps: overview/symmetry/auditor/science charts keep English labels; Claim Auditor notes are English-only (note_en, no note_ar).
7. Thin orphan pages: Waw Miracle (one KPI), Data Insights (four cards), Abjad (a table).

## Design

### Information architecture: 33 pages -> 8 sidebar items with sub-tabs

- Home (new hero view, boots first)
- Claim Auditor (flagship, standalone)
- Explore: Overview (+ absorbed Data Insights cards), Word Analysis, Letter Frequency, Mecca vs Medina, Emotional Profile, Divine Pronouns, Scientific Refs, Big Picture (old Advanced Analytics)
- Search & NLP: Word Search, NLP Explorer
- Reader: Reader, Tawafuq Mushaf, Alifi Mushaf
- Patterns & Numbers: Word Pairs (merged Symmetries + Antonyms + Waw KPI), Abjad, Number 19, Structure
- Analytics Lab: BI Dashboard, Hifz Optimiser, Revelation Classifier, Statistical Tests, Clusters, Coincidence Lens
- Library: Stories, Lessons, Du'as, Scholarly Insights, Untranslatable Words, Knowledge Graph

Mechanism: sidebar lists hubs; a pill sub-tab bar renders at the top of main for the active hub. All existing view ids and templates are preserved except the three merged/removed views (antonyms, waw, insights).

### Product tone

- Remove every NEW badge (nav + h1).
- Remove the university unit/course banner from Analytics Lab; keep the plain-English "What is this / How to read" boxes.
- Rename "Meccan/Medinan ML" -> "Revelation Classifier".

### Home hero (in-app)

Brand mark, bilingual headline, one-line value prop, corpus stat band (114 / 6,236 / 77,429 / 1,651), six feature cards linking to the hubs, integrity line ("computed live from the Quranic Arabic Corpus, nothing hand-typed").

### Arabic parity

- Localize chart labels: overview (Mecca/Medina/Surah/Verses), symmetry pair labels, auditor x-axis, science categories.
- Arabic notes for the 12 auditor claims via an in-app map (claimNotesAr) so generated data.js stays untouched; same for science category names.

### Landing page

- Add real app screenshot to the hero (shot-app.png).
- Full Arabic version via the same lang toggle pattern as the app (?lang=ar + RTL), composed natively, not translated literally.
- Keep the claim-audit section; tighten copy.

## Out of scope

Payments/licensing mechanics (business decision), electron-app/ legacy build, og-image regeneration if time does not allow.

## Rollout

All work committed locally on main. NO push without Hesham's explicit approval (GitHub Pages deploys on push).
