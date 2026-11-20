# Architecture

How Quran Insights is built. For what is on the site, see the [README](README.md).

```
web/            the site: landing page, the app, generated data files, library content
data-build/     the Python pipeline that writes web's data files, its tests, the knowledge-graph builder
api/            one optional Vercel function (Jev)
vercel.json     serves web/ and api/, and sends the short links to the app
```

## The site (`web/`)

| File | What it is |
|---|---|
| `index.html` | The landing page: a scrolling story with WebGL scenes, and the claim cards |
| `app.html` | The app. One Vue 3 file with no build step: every page is a `<section v-if="view==='…'">`, and the interactive pieces are components registered at the end of the file |
| `sky.js` | The WebGL star field behind every page. On "staged" pages (`STAGED` in `app.html`) it also draws the page's main chart |
| `lookup.js` | Finds a verse or a surah from what a reader types: numbers (2:255), a surah's name in Arabic or English in the spellings people use, a name with a verse (Baqarah 255), a verse known by a name (Ayat al-Kursi), or a juz, a hizb or a printed page (juz 30, page 255; it reads where they begin from `marks` in `data.js`). Used by Search, the Reader's Go to box and the home ask box. To add a spelling or a named verse, add it to `NAMES` or `NAMED` there |
| `translit.js` | Finds an Arabic word typed in English letters (rahma, ra7ma, al-kitab) by its sound, and a few phrases known by their sound (alhamdulillah). It reads how each dictionary word sounds from `roman.js`. Used by Search and by the search box on every page. A typed word is only replaced by the Arabic word when it sounds exactly like one and is not an English word of the translation or a surah's name; a looser fit is offered, never chosen |
| `study.js` | What one verse shares with the rest of the Quran, for the study panel that opens from any verse number in the Reader or in Search: the verses that say it again word for word, the verses nearest to it by the dictionary words they share (each word weighted by how few verses hold it, scored by cosine, and offered only on two shared words or one rare one), and its own words from the rarest. It tells words that share a spelling apart (the garden and the jinn are both written جنة) with the two tables in `lemma-variants.js`. The panel itself (`VerseStudy` in `app.html`) adds the verse's place, and the Library cards and pages that cite it. Each verse opened is a step in the browser's history, and `?study=2-255` opens the panel from a link |
| `spelling.js` | How a word or a phrase typed in today's spelling is found in the mushaf's own. The mushaf leaves out alifs that today's spelling writes, writes the long alif as a hamza and an alif, writes some long vowels as small letters, and joins the calling «يا» to the word it calls, so every word of the text is also kept in today's spelling (`tables()`), and what is typed is compared with both (`asWritten()` for a word, `phrase()` for a phrase, `today()` for the dictionary word behind a spelling). A typed hamza keeps its seat and typed vowel marks are exact. It also holds the reading helpers the whole app uses (`normalize`, `surfTest`) |
| `place.js` | What the browser keeps for a reader, in its own storage (`localStorage`) and nowhere else: the latest place read in each of the last six surahs, and the verses they saved (up to 500). There is no account and nothing is sent anywhere. Everything read back is checked against the surahs' lengths, and where the browser keeps nothing (some private windows) `canKeep()` says so and the site offers none of it. Used by the Reader, the study panel and Home |
| `card.js` | A verse as an image card to share or keep: the Arabic with its number between the mushaf's ornate brackets, the English translation if wanted, where the verse is, and the site's name, in the site's night look or a paper look. Laid out and drawn on a canvas 1080 pixels wide in the browser; the card is square when the verse fits and grows taller for a long verse instead of shrinking the text past what a phone can read, and the lines are balanced so none is left with one word. Used by the share sheet of the verse study panel |
| `recite.js` | Hearing a verse recited: the five reciters offered (Alafasy, al-Husary, al-Minshawi, Abdul Basit, al-Muaiqly), each at the lightest quality the library keeps for them, where each verse's recording is, the reciter picked, and the order of recitations when a passage is repeated to memorise it (each verse so many times, the passage so many times, a silence to say it back), with the repeat choices; both kept in the browser's own storage, a key each. The recordings stream from AlQuran Cloud's open audio library (Islamic Network, `cdn.islamic.network`), free with no account or key for personal and educational use; each verse is its own file, numbered through the Quran from 1 to 6236. Used by the Reader, its side rail and the study panel |
| `explain.js` | Each page's explanation for scientists, and the glossary of terms (each term links to the page where it is at work) |
| `discover.js`, `discoveries.js` | The nine studies: their texts, and the results the pipeline computed |
| `data.js`, `words.js`, `corpus.js`, `translation_en.js`, `lemma-variants.js`, `roman.js`, `phrases.js` | Data written by `data-build/`. Do not edit them by hand |
| `content/` | Library content (stories, lessons, du'as, insights, untranslatable words, history claims), the knowledge-graph pages, the mushaf layout, the Alifi pages, Jev's batch answers |
| `config.js` | Where the Jev endpoint is set |
| `vendor/` | Vue's global build. Plotly loads from a CDN when a page first needs a chart |

### Pages, the menu and addresses

- **The menu** is the `nav` array in `app.html`: five sections, each with its pages. A page's menu name is the same as its title.
- **A page** is a view id (`overview`, `mecca`, `n19` ...). `go(id)` opens it; `NEEDS` lists the data files it needs; `realViews` lists every page.
- **Short links.** `window.QI_SLUG`, in the head of `app.html`, gives every page a one-word address (`n19` is `/19`, `mecca` is `/mecca-medina`). `vercel.json` sends those addresses to `app.html`. On the live site the address bar shows `/19`; locally, where there are no rewrites, it shows `app.html?view=n19`.
- **Old addresses.** `VIEW_ALIAS` sends the ids of pages that were merged into others to the page and section that hold them now: `stats` and `classifier` to `mecca`, `nlp` to `word`, `dashboard` and `advanced` to `overview`, `pronouns` to `emotion`, `alifi` to `tawafuq`.
- **Merged pages.** `MERGED` lists each section a page took in. The section shows the old page's plain explanation (`plainOf(key)`), and the page's scientific layer adds that section's method and result.

To add a page: a `<section>` in `app.html`, an item in `nav`, its id in `realViews`, a slug in `QI_SLUG` and in `vercel.json`, its plain text in `PLAIN`, and its scientific text in `explain.js`.

### Explanations

Each page explains itself in two layers that the reader switches between. The plain layer (`PLAIN` in `app.html`) says what the page is, how to read it and what it tells us. The scientific layer (`SCI` in `explain.js`) gives purpose, data, method, result and limits. Terms in either layer open glossary cards (`GLOSS` in `explain.js`).

## The data (`data-build/`)

`build.py` reads the Quranic Arabic Corpus morphology (`sources/quran-morphology.txt`), stops if the totals are not 114 surahs, 6,236 verses and 77,429 words, and writes `web/data.js`, `words.js`, `corpus.js`, `lemma-variants.js` and `roman.js`.

| Module (`pipeline/`) | What it computes |
|---|---|
| `corpus.py` | Words rebuilt from the corpus's segments, with lemma, root and form |
| `claims.py` | The claim registry: each claim's word, its own counting rule, and where it counts |
| `datasets.py`, `analytics.py` | Surah figures, Mecca and Medina tests, the classifier, the clusters |
| `optimisation.py`, `montecarlo.py` | The Hifz planner's plan and its simulations |
| `wordcount.py`, `lettercount.py` | The rules behind *How many words?* and *How many letters?* |
| `discoveries.py` | The nine studies (`python3 -m pipeline.discoveries --write`; slow) |
| `names.py` with `rizq.py`, `wahhab.py` | The Name studies (*Rizq Verses and Du'a*, *Hiba Verses and Du'a*): one engine, and one config per Name holding its hand labels, its du'a and the page's sentences |
| `mushaf.py`, `lemma_variants.py` | The mushaf page layout, and the homograph tables the claim checker uses: the dictionary words behind each shared spelling, and for every word of the text which of them it is |
| `marks.py` | Where each juz, hizb quarter and printed page begins (`marks` in `data.js`): pages and quarter signs read from the mushaf layout, and checked so that eight quarters make each juz |
| `roman.py` | How each dictionary word sounds (`web/roman.js`), read from the vowel marks of its lemma, so a word can be found when typed in English letters |
| `phrases.py` | The repeated phrases (`web/phrases.js`; `python3 -m pipeline.phrases`): every run of three words or more inside a verse that comes at least three times, kept when it is not only a piece of a longer one, when two of its words carry meaning by the corpus's fine tags, and when it does not end on a word that leaves it hanging. It writes only its own file, never `data.js` |

- `tests/test_lookup.js` checks `web/lookup.js` against the site's own surah list: `node data-build/tests/test_lookup.js`.
- `tests/test_translit.js` checks `web/translit.js` against the site's own word index (about 150 spellings people type): `node data-build/tests/test_translit.js`.
- `tests/test_study.js` checks `web/study.js` the same way (repeats, nearest verses, same-spelling words): `node data-build/tests/test_study.js`.
- `tests/test_spelling.js` checks `web/spelling.js` the same way: everyday spellings of words and phrases count what the mushaf's own spelling counts, a hamza keeps its seat (faith is not oaths), and every word of the text typed in today's spelling finds itself: `node data-build/tests/test_spelling.js`.
- `tests/test_place.js` checks `web/place.js` with a stand-in for the browser's storage: one place a surah with the latest first, saving twice takes a verse off, broken or edited entries are dropped, a browser that refuses storage throws nothing, days are counted by the calendar, and the site keeps nothing else behind the reader's back: `node data-build/tests/test_place.js`.
- `tests/test_card.js` checks `web/card.js` with a stand-in for the canvas's text measuring: every verse of the Quran fits its card with and without the translation, no word is lost, no block runs into the next, lines are balanced, and a long verse grows the card: `node data-build/tests/test_card.js`.
- `tests/test_recite.js` checks `web/recite.js`: every verse has its own recording in reading order (6,236), the numbers agree with the library's own, a verse that does not exist gets none, each reciter's quality is right, stepping stays inside the surah, the Basmala comes first except in al-Fatiha and at-Tawbah, a repeated passage plays in the right order and stops after its last round, a passage is made safe before it plays, and only the reciter and the repeat choices are kept: `node data-build/tests/test_recite.js`.
- `tests/test_no_dashes.js` fails if any file of the site holds an em dash, an en dash or a minus sign: `node data-build/tests/test_no_dashes.js`. Ranges and negative numbers use a plain hyphen; a dash the code must recognise when a visitor types it is written as an escape.
- `tests/test_phrases.py` checks `pipeline/phrases.py` and `web/phrases.js`: every place points at the phrase's own words inside one verse, a plain scan finds every count again, no phrase is only a piece of a longer one, the rules that keep a phrase hold, the best-known phrases have their counts, and the explanations quote the build's numbers.
- `tests/` pin every number the site publishes. Run them with a Python that has a working scikit-learn; on this Mac that is `/usr/bin/python3`.
- `discover/PREREGISTRATION.md` is the plan written before the studies ran.
- `jev/` holds the Jev batch jobs and a stand-in for developing without a key.
- `knowledge-graph/` builds the Knowledge Graph page: `scripts/` turn `quranjson/` (surah texts and translations) into a corpus of notes (`corpus/`), graphify draws the graph in `corpus/graphify-out/`, and its pages are copied to `web/content/quran_graph.html` and `quran_graph_ar.html`.

`web/data.js` is a single line. When two branches change it, rebuild it on top of the other change instead of merging the two lines.

## Deploying

Vercel deploys `web/` and `api/` from `main` about a minute after a merge. The GitHub Pages workflow in `.github/` publishes a copy whose landing page forwards visitors to quraninsights.vercel.app.

Design notes from the rebuild are in `docs/superpowers/specs/`.

## Jev (optional)

The site is a static page, and everything below works with plain matching in the browser. When a Jev endpoint is configured, a few judgement calls also go to [TypeSafe's Jev](https://typesafe.ai), which answers typed questions (yes/no, pick one) about a piece of text with probabilities instead of prose. Every number the site shows still comes from the corpus; Jev only decides things like which word a claim means.

| Feature | Where | Without Jev | With Jev |
|---|---|---|---|
| **Check any claim** | Word Counts | Finds the word in an English or Arabic claim (modern or mushaf spelling) and counts it three ways: exactly as written, all forms of the word, the whole root. Says which count, if any, gives the claimed number, and how many "as written" hits are other words with the same spelling | Also decides which word the claim means when a spelling covers several (ملك: angel, king, dominion) and which way of counting it implies |
| **Search hints** | Search | Each mode button shows its count; a word or phrase typed in today's spelling finds the mushaf's own (العالمين finds ٱلْعَٰلَمِينَ, آمنوا finds ءَامَنُوا۟, and «يا» goes with the word it calls, as the mushaf joins them), because every word is also compared in today's spelling (`spelling.js`): with the hamzas on the seats that were typed, or without them when no word is written that way; a line says how the mushaf writes it. Typed vowel marks still mean exactly as written. A phrase is counted as exact words, and when it comes more often with a letter joined to it (واليوم الآخر) the page offers that count; where one spelling covers several dictionary words (جنة is the garden and the jinn), asks which is meant and counts only that one, using the per-word tags in `lemma-variants.js`. The choice is made for the reader when the typing says it: the sound of a word typed in English letters (malik is the king, malak the angel), or an Arabic form only one of the words takes. It travels in the address as `sense=` (0 is all of them together), and the study panel, the word card, the search box on every page and the home ask box pass it on | No Jev call |
| **A word through time** | Search | Under the juz chart: how often the word comes in the surahs revealed in Mecca and in Medina (counts, and the rate in every 1,000 words, since the two differ in length), then twenty bars in the traditional order of revelation, twelve parts of about equal length for Mecca and eight for Medina. A bar shows only that part's verses. The order is the list of the standard Egyptian edition that the Name studies already carry in `data.js` (`rizq.chrono`); `eraParts()` in `app.html` cuts it into the parts | No Jev call |
| **Continue reading and saved verses** | Home, Reader, study panel | The Reader keeps the verse at its reading line once the reader scrolls through the text themselves (a verse opened from a search or a link is not taken for reading until they do, and scrolling up to the controls keeps the place). Home then offers "Continue reading", the Reader offers to go back to where the reader was, and lists the surahs read lately and the saved verses. A verse is saved from its study panel; saved verse numbers carry a star in the Reader, and the list steps through them in the order of the mushaf. Kept in this browser only (`place.js`) | No Jev call |
| **Share a verse as an image** | Study panel | "Share as an image" opens a sheet with the card drawn in the browser (`card.js`): night or paper, with or without the translation. Share hands the image and a link to the verse to the phone's own share sheet where the browser can; Download saves a PNG; Copy puts the image on the clipboard where the browser allows it. Nothing is sent anywhere | No Jev call |
| **Listen to a verse or a surah** | Reader, its side rail, study panel | "Listen to the surah" and the rail's play button recite the surah verse after verse from the verse at the reading line (or from the top with the Basmala first), light the verse being recited and keep it on screen unless the reader has just moved the page. "Listen" in the study panel plays that one verse. A bar at the foot of every page pauses, names the verse (tap it to go there), changes the reciter and stops; the phone's lock screen shows it too. The recordings come from AlQuran Cloud (`recite.js`) | No Jev call |
| **Repeated Phrases** | Its own page (Explore), linked from Words | Four figures, then the phrases as bars that grow in, each split between Meccan and Medinan surahs; a word box (Arabic, or English letters through `roman.js`), a length and an order. The phrase picked shows on a strip of the 114 surahs and in each of its verses, its words marked; a verse number opens the study panel (`phrases.js`) | No Jev call |
| **Repeat to memorise** | Player bar, study panel, Hifz Planner | A sheet picks a passage of one surah, how many times each verse plays, how many times the passage plays (or until stopped) and what follows each verse: nothing, a short pause, or a silence as long as the verse to say it back. It says in a sentence what will be heard and how many recitations that makes, then plays it in the Reader. The repeat button on the bar counts the times and opens the sheet to change or stop it; the choices are remembered for the next visit (`recite.js`) | No Jev call |
| **Ask the site** | Home | Surah names, claims and single words go straight to their page; other questions are matched by keywords | Picks the page for open questions, and says when a question isn't about the Quran |
| **A du'a or lesson for how you feel** | Du'as, Lessons | Keyword matching to a category | Picks the category from a description in your own words |
| **Second opinions** | Mecca and Medina, Tone and Voice | Hidden | Jev's Meccan/Medinan and tone judgements for the opening of every surah, from a batch run |
| **Library tag review** | `data-build/reports/` | Not available | A maintainer report of du'as and lessons whose category Jev disagrees with. Nothing on the site changes from it |

Jev replaces what plain matching found only when the two agree, when plain matching found nothing, or when Jev is reasonably sure (confidence 0.5 or more); otherwise its pick is offered as an alternative. If Jev can't be reached or refuses a call, the box shows the plain-matching result as if Jev were off, and the rest of the visit doesn't ask it again.

**Privacy and safety.** With Jev on, the text typed into the claim, ask and situation boxes is sent to the site's `/api/decide` function on Vercel and from there to TypeSafe's Jev (through Vercel's AI Gateway, unless a TypeSafe key is set); each box says so. A description that mentions self-harm is never sent anywhere: the page shows a note with a link to [find a helpline](https://findahelpline.com) instead. With `jevEndpoint` empty (the default), nothing leaves the browser.

### Turning it on

1. Import this repository as a project on [Vercel](https://vercel.com), with the framework preset **Other**. `vercel.json` serves `web/` as the site and `api/decide.js` as the function; there is no build step and no key to add.
2. On Vercel the function reaches Jev through [Vercel's AI Gateway](https://vercel.com/docs/ai-gateway/sdks-and-apis/typesafe), signed in with the project's own OIDC token, so calls are billed to the Vercel account as AI Gateway usage. Jev isn't covered by the gateway's free monthly credit (its free launch promotion ended on 26 September 2026), so it answers only once the account has paid AI Gateway credit. Until then the gateway refuses every call and the site quietly carries on with plain matching, without a message, and stops asking Jev for the rest of the visit. With credit, set an [AI Gateway budget](https://vercel.com/docs/ai-gateway/observability-and-spend/budgets): the per-IP rate limit is kept per serverless instance, so it is a speed bump, not a cap.
3. `web/config.js` already points pages served by the Vercel project at their own function, and the GitHub Pages copy at the production one. Change it only to use a different endpoint, for example `window.QTA_CONFIG = { jevEndpoint: 'https://your-project.vercel.app/api/decide' };`.

Optional settings, in the Vercel project's **Settings → Environment Variables**:

| Variable | Default | What it does |
|---|---|---|
| `TYPESAFE_API_KEY` | not set | A key from a TypeSafe account ([console.typesafe.ai](https://console.typesafe.ai), Settings → Keys). When set, Jev is asked on TypeSafe's own API instead of the gateway, and billed there. |
| `AI_GATEWAY_API_KEY` | not set | An AI Gateway key, for running the function or the batch jobs outside Vercel |
| `ALLOWED_ORIGINS` | `https://heshamabourokaia.github.io` | The sites allowed to call the function, separated by commas |
| `RATE_LIMIT_PER_MINUTE` | 30 | Requests per IP address per minute |
| `JEV_MODEL` | `typesafe-ai/jev` on the gateway, `jev-latest` on TypeSafe | Which Jev model to ask |

Keep any key there only: never commit it or paste it anywhere else.

The endpoint can only ask the three fixed kinds of question in `api/_jev.js` (claim, route, situation), rejects other origins, caps the text length, and answers only "off topic" for text that isn't about the Quran, so it can't be used as a general-purpose classifier. The request and answer shapes follow TypeSafe's documentation, which the gateway serves unchanged; `parseAnswer` in `api/_jev.js` is the one place to adjust if the live API differs.

### Batch jobs

```bash
node data-build/jev/run-batch.js --dry-run            # how many Jev calls a run needs (341 for everything)
AI_GATEWAY_API_KEY=... node data-build/jev/run-batch.js # surahs + tags (or TYPESAFE_API_KEY=...)
```

This writes `web/content/jev-data.js` (shown on Mecca and Medina, and on Tone and Voice) and `data-build/reports/jev-tag-review.md`. Each surah is one call that asks both questions. Answers are cached in `data-build/jev/cache/` (gitignored), so a re-run only pays for new questions. Use `--jobs surahs` or `--jobs tags` for one job and `--limit N` for a sample.

### Developing without a key

```bash
node data-build/jev/mock-jev.js &     # a stand-in for Jev on :8788
JEV_URL=http://127.0.0.1:8788/v1/systemone TYPESAFE_API_KEY=test node data-build/jev/dev-server.js
# open http://localhost:8000/app.html: config.js is served with the endpoint switched on
node data-build/jev/test-client.js && node data-build/jev/test-endpoint.js
node data-build/jev/run-batch.js --mock   # writes under data-build/jev/cache/mock only
```

The mock answers by keyword overlap and labels itself `jev-mock`; its output is refused anywhere under `web/` or `data-build/reports/`.
