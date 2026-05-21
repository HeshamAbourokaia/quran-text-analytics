# Roadmap

Where the project is going. Phase 1 (current release) ships descriptive analytics, scholarly content, and the experimental autoresearch loop. Phase 2 extends into applied NLP and machine learning.

## Phase 2: Applied NLP (in progress)

### 2.1 Semantic verse search

**Goal**: type a natural-language query in Arabic or English, get the K most semantically similar verses ranked.

**Approach**: pre-compute embeddings for all 6,236 verses offline, bundle them, do cosine similarity in pure JavaScript at query time.

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Embedding model | `intfloat/multilingual-e5-large` | Best open-source multilingual quality on Arabic; runs locally via sentence-transformers; no API cost |
| Dimensions | 1024 | e5-large output |
| Storage format | Float32Array binary, base64 in JSON | ~25 MB total, browser-loadable |
| Similarity | Pure JS cosine | 6,236 × 1024 dot products = ~6.4M floats per query, well under 100 ms |
| Query embedding | Same model via transformers.js OR small Python helper | Open design question, see ROADMAP.md#open-questions |
| Index | None, linear scan | 6,236 vectors is well below the threshold where an ANN index helps |

**Deliverables**:
- `scripts/embed_quran.py`, offline embedding pipeline
- `electron-app/data/embeddings.bin`, bundled vector store
- New app page: `pages/semantic-search.vue` (or inline section in `app.html`)
- README "Live demo" section update

**Estimated effort**: 1-2 days

### 2.2 Topic clustering with BERTopic

**Goal**: discover latent topics across the corpus without hand-labeling, visualize them as an interactive map.

**Approach**: BERTopic combines embeddings + UMAP dimensionality reduction + HDBSCAN clustering + c-TF-IDF topic representation. Run offline, ship the results.

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Topic model | BERTopic (default config) | Standard pipeline, well-documented, reproducible |
| Embedding base | Same e5-large vectors from §2.1 | Reuse work |
| Number of topics | Auto-detected by HDBSCAN | Avoid arbitrary K choice |
| Output | `topics.json` with topic → verses mapping + top words per topic | Single static file |
| Visualization | Plotly 2D scatter (UMAP coords) colored by topic | Click point → reveal verse |

**Deliverables**:
- `scripts/cluster_topics.py`, offline pipeline
- `electron-app/data/topics.json`
- New "Topic Map" section in the app
- 5-10 most coherent topics surfaced as a "Topics to explore" list

**Estimated effort**: 1 day

### 2.3 RAG Q&A

**Goal**: natural-language question → grounded answer citing specific verses.

**Architecture**: query → embed (via §2.1 model) → top-K verse retrieval → LLM with retrieved context → answer with citations.

| Component | Electron (local) | Web demo |
|-----------|-----------------|----------|
| Retrieval | Bundled embeddings, cosine in JS | Same |
| LLM | Ollama (`llama3.1:8b` or `gemma2:9b`), user installs locally | Anthropic Claude Sonnet via Vercel edge function (hidden API key, small budget) |
| Latency | 2-5 s on M-series Mac | 1-2 s |
| Privacy | 100% local | Server-relayed query (no storage) |

**Output format**: structured answer with `<cite verse="3:55">...</cite>` tags that the UI converts to clickable verse links.

**Disclaimers**: every RAG response will be tagged as "AI-generated, not religious authority" with a prominent UI badge. Theological caution is non-negotiable.

**Deliverables**:
- `electron-app/lib/rag.js`, retrieval + LLM call
- `api/rag.ts`, Vercel edge function for web demo
- New "Ask the Quran" page
- Disclaimer modal on first use

**Estimated effort**: 2-3 days

### 2.4 Public web demo

**Goal**: a clickable demo link in the README so recruiters never have to download anything.

**Approach**: same `app.html` deployed as a static site. Strip Electron-specific code (file system, IPC) behind feature flags. Bundle embeddings + topics. Wire RAG to the Vercel edge function.

**Hosting**: Vercel free tier (more generous than Netlify for static + edge functions).

**Estimated effort**: 1 day

## Open questions

1. **Query embedding strategy for web demo**: three options:
   - (a) Ship transformers.js + the e5 model (~500 MB browser download, prohibitive)
   - (b) Use OpenAI/Cohere embedding API for queries only (cheap, but loses "fully local")
   - (c) Pre-embed a fixed query bank (e.g., 1,000 common Quranic questions) and approximate-match new queries to the nearest bank entry
   - **Current lean**: (b) for web demo, (a) for desktop if user opts in

2. **Arabic vs English semantic alignment**: does e5-large produce comparable embeddings for "mercy" and "رحمة"? Needs empirical test on a held-out set of paraphrase pairs.

3. **Topic labeling language**: BERTopic gives English keyword labels by default. Worth running through a second LLM pass to generate descriptive bilingual topic names?

4. **RAG hallucination guard**: should the LLM be instructed to refuse questions it can't ground in retrieved verses, or to explicitly say "the retrieved context doesn't cover this"? The former is safer for religious content; the latter is more useful as a tool.

## Phase 3: Speculative

Things worth considering after Phase 2 ships:

- **Cross-translation comparison**: line up Sahih International, Yusuf Ali, Pickthall side-by-side for any verse, with semantic-similarity scoring
- **Recitation audio**: Plotly waveform aligned to verses, jump-to-time-by-click
- **Verse-of-the-day**: daily push notification via the Electron menu bar
- **Mobile app**: Capacitor wrapper around the same Vue codebase
- **Concept ontology graph**: D3 force-directed network of Quranic concepts and their co-occurrence in verses (the competitor's killer feature at qurananalysis.com)
- **Knowledge graph**: entities (prophets, places, events) as nodes, relationships as edges, with verse anchors

## Non-goals

What this project deliberately won't try to do:

- **Issue fatwas or religious rulings**: this is an analytics tool, not a substitute for scholarship
- **Replace tafsir books**: the tafsir insights page surfaces existing scholarly work, not new theological positions
- **Support every translation and qira'ah**: Hafs/Madani only for v1; Warsh, Qalun, etc. out of scope
- **Real-time collaborative features**: single-user app, no accounts, no server state
