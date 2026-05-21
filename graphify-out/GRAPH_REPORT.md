# Graph Report - /Users/Hesham/Documents/quran-analytics  (2026-05-21)

## Corpus Check
- Large corpus: 40 files · ~578,855 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 631 nodes · 749 edges · 63 communities (39 shown, 24 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.84)
- Token cost: 361,468 input · 120,489 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Vue App Structure (app.html)|Vue App Structure (app.html)]]
- [[_COMMUNITY_Python Data Pipeline|Python Data Pipeline]]
- [[_COMMUNITY_Plotly Chart Visualizations|Plotly Chart Visualizations]]
- [[_COMMUNITY_Radar Baseline Config|Radar Baseline Config]]
- [[_COMMUNITY_Radar Current Config|Radar Current Config]]
- [[_COMMUNITY_AutoResearch Mutation Engine|AutoResearch Mutation Engine]]
- [[_COMMUNITY_App UI Components|App UI Components]]
- [[_COMMUNITY_Phase 2 Roadmap (RAGBERTopicEmbeddings)|Phase 2 Roadmap (RAG/BERTopic/Embeddings)]]
- [[_COMMUNITY_AutoResearch Orchestrator|AutoResearch Orchestrator]]
- [[_COMMUNITY_Claude Vision Judge|Claude Vision Judge]]
- [[_COMMUNITY_Bilingual UI Screenshots|Bilingual UI Screenshots]]
- [[_COMMUNITY_Quran Analytics UI Layer|Quran Analytics UI Layer]]
- [[_COMMUNITY_Quran Analytics Computation|Quran Analytics Computation]]
- [[_COMMUNITY_Radar Polar Baseline|Radar Polar Baseline]]
- [[_COMMUNITY_Radar Polar Current|Radar Polar Current]]
- [[_COMMUNITY_Electron Build Config|Electron Build Config]]
- [[_COMMUNITY_AutoResearch Git Ops|AutoResearch Git Ops]]
- [[_COMMUNITY_AutoResearch Plotly Renderer|AutoResearch Plotly Renderer]]
- [[_COMMUNITY_AutoResearch Loop Concepts|AutoResearch Loop Concepts]]
- [[_COMMUNITY_Arabic Text Processing|Arabic Text Processing]]
- [[_COMMUNITY_Concordance Search UI|Concordance Search UI]]
- [[_COMMUNITY_Heuristic Chart Evaluator|Heuristic Chart Evaluator]]
- [[_COMMUNITY_NLP Concepts & Data Sources|NLP Concepts & Data Sources]]
- [[_COMMUNITY_External Data File Bindings|External Data File Bindings]]
- [[_COMMUNITY_Tafsir Scholars Registry|Tafsir Scholars Registry]]
- [[_COMMUNITY_Quran Analytics Electron Applicatio...|Quran Analytics Electron Applicatio...]]
- [[_COMMUNITY_Raise if repo's working tree isn't ...|Raise if repo's working tree isn't ...]]
- [[_COMMUNITY_Bilingual Everywhere Principle|Bilingual Everywhere Principle]]
- [[_COMMUNITY_page_errors()|page_errors()]]
- [[_COMMUNITY_Madani Mushaf  Hafs Riwayah|Madani Mushaf / Hafs Riwayah]]
- [[_COMMUNITY_Page 17 Render Lifecycle|Page 17 Render Lifecycle]]
- [[_COMMUNITY__build_page_map()|_build_page_map()]]
- [[_COMMUNITY_analyze_rhetoric()|analyze_rhetoric()]]
- [[_COMMUNITY_find_block()|find_block()]]
- [[_COMMUNITY_enrich_data.py|enrich_data.py]]
- [[_COMMUNITY_main()|main()]]
- [[_COMMUNITY_eval_heuristic.py (Plotly heuristic...|eval_heuristic.py (Plotly heuristic...]]
- [[_COMMUNITY_quran_duas.js|quran_duas.js]]
- [[_COMMUNITY_quran_lessons.js|quran_lessons.js]]
- [[_COMMUNITY_quran_stories_data.js|quran_stories_data.js]]
- [[_COMMUNITY_quran_tafsir_insights.js|quran_tafsir_insights.js]]
- [[_COMMUNITY_go_back()|go_back()]]
- [[_COMMUNITY_auto_name_topic()|auto_name_topic()]]
- [[_COMMUNITY_find_thematic_bridges()|find_thematic_bridges()]]
- [[_COMMUNITY_load_all_data()|load_all_data()]]
- [[_COMMUNITY_Serif English Display Typography (p...|Serif English Display Typography (p...]]
- [[_COMMUNITY_Electron main.js|Electron main.js]]
- [[_COMMUNITY_HeuristicResult dataclass|HeuristicResult dataclass]]
- [[_COMMUNITY_VisionResult dataclass|VisionResult dataclass]]
- [[_COMMUNITY_git_ops.py (project-local git wrapp...|git_ops.py (project-local git wrapp...]]
- [[_COMMUNITY_Electron package.json (universal Ma...|Electron package.json (universal Ma...]]
- [[_COMMUNITY_app.py (Python preprocessing pipeli...|app.py (Python preprocessing pipeli...]]
- [[_COMMUNITY_transformers.js (query embeddings o...|transformers.js (query embeddings o...]]
- [[_COMMUNITY_initParticles(), background partic...|initParticles(), background partic...]]
- [[_COMMUNITY_toggleSection(key), sidebar collap...|toggleSection(key), sidebar collap...]]
- [[_COMMUNITY_mode prop (communityexpert)|mode prop (community|expert)]]
- [[_COMMUNITY_chart-galaxy (Plotly)|chart-galaxy (Plotly)]]
- [[_COMMUNITY_chart-correlation (Plotly)|chart-correlation (Plotly)]]

## God Nodes (most connected - your core abstractions)
1. `run()` - 27 edges
2. `Vue 3 Root Component` - 26 edges
3. `app.html (Vue 3, ~9,900 lines)` - 17 edges
4. `tokenize_arabic()` - 16 edges
5. `RadarRenderer` - 14 edges
6. `renderAdvancedCharts()` - 13 edges
7. `normalize_arabic()` - 11 edges
8. `HttpServer` - 11 edges
9. `Page 14 Tafsir Insights` - 10 edges
10. `Hero Overview Screenshot (Arabic)` - 10 edges

## Surprising Connections (you probably didn't know these)
- `build_cinematic.py (HTML app builder)` --semantically_similar_to--> `app.html (single-file Vue 3 + Plotly app)`  [INFERRED] [semantically similar]
  build_cinematic.py → electron-app/app.html
- `update_all.py (HTML patcher)` --semantically_similar_to--> `app.html (single-file Vue 3 + Plotly app)`  [INFERRED] [semantically similar]
  update_all.py → electron-app/app.html
- `verses_compact.json (~747KB)` --shares_data_with--> `app.html (Vue 3, ~9,900 lines)`  [EXTRACTED]
  verses_compact.json → electron-app/app.html
- `surah_extended.json (~31KB)` --shares_data_with--> `app.html (Vue 3, ~9,900 lines)`  [EXTRACTED]
  surah_extended.json → electron-app/app.html
- `quran_madani.json (~1.4MB)` --shares_data_with--> `app.html (Vue 3, ~9,900 lines)`  [EXTRACTED]
  quran_madani.json → electron-app/app.html

## Hyperedges (group relationships)
- **AutoResearch chart-radar optimization loop**, autoresearch_orchestrator_run, autoresearch_mutate_propose, autoresearch_render_reload_config, autoresearch_eval_heuristic_run, autoresearch_eval_vision_judge, autoresearch_git_ops_commit_all, autoresearch_git_ops_reset_hard [EXTRACTED 1.00]
- **Quran data modules loaded by app.html**, electron_app_quran_duas, electron_app_quran_lessons, electron_app_quran_stories_data, electron_app_quran_tafsir_insights, electron_app_app_html [EXTRACTED 1.00]
- **app_data.json builder/enricher/patcher pipeline**, build_cinematic_app, enrich_data_pipeline, update_all_html_patcher, concept_app_data_json [INFERRED 0.95]
- **AutoResearch Iteration Pipeline**, autoresearch_mutate_py, autoresearch_render_py, autoresearch_eval_heuristic_py, autoresearch_eval_vision_py, autoresearch_git_ops_py [EXTRACTED 1.00]
- **Phase 2 Applied NLP Stack**, roadmap_phase2_semantic_search, roadmap_phase2_topic_clustering, roadmap_phase2_rag_qa, roadmap_phase2_web_demo [EXTRACTED 1.00]
- **Scholarly Tafsir Source Set (8 scholars)**, scholar_al_samarrai, scholar_ibn_kathir, scholar_al_tabari, scholar_al_qurtubi, scholar_al_sadi, scholar_ibn_ashur, scholar_al_sharawi, scholar_sayyid_qutb [EXTRACTED 1.00]
- **Sunburst Visualisation Trio (Page 14)**, electron_app_app_chart_sunburst, electron_app_app_chart_sunburst_juz, electron_app_app_chart_sunburst_theme [EXTRACTED 1.00]
- **Tafsir Insight System (Page 22, 73-74 insights with categories + scholars)**, electron_app_app_page22, electron_app_app_const_tafsir_categories, electron_app_app_const_tafsir_scholars, electron_app_app_external_quran_tafsir_insights_js, electron_app_app_data_tafsirdata [EXTRACTED 1.00]
- **Page 17 Hero Dashboard Stack (KPIs + DYK + Revelation Pulse)**, electron_app_app_page17, electron_app_app_data_herostats, electron_app_app_data_didyouknow, electron_app_app_method_animateherostats, electron_app_app_method_renderrevelationpulse, electron_app_app_chart_revelation_pulse [EXTRACTED 1.00]
- **Arabic UI Design System (RTL + Emerald + Amiri)**, screenshots_hero_overview_rtl_layout, screenshots_shared_dark_emerald_palette, screenshots_hero_overview_amiri_typography, screenshots_shared_bilingual_implementation_ar [INFERRED 0.85]
- **Visual Hierarchy via Colored KPI Cards**, screenshots_hero_overview_kpi_cards_arabic, screenshots_tafsir_insights_kpi_trio, screenshots_tafsir_insights_color_coded_stats [INFERRED 0.85]
- **Concordance Search Pattern (Box + Chips + Hints)**, screenshots_concordance_search_box_pill, screenshots_concordance_match_mode_chips, screenshots_concordance_example_prompt [EXTRACTED 1.00]
- **Four EN Screenshots Demonstrating Bilingual Implementation**, screenshots_hero_overview_en_page, screenshots_nlp_explorer_en_page, screenshots_concordance_en_page, screenshots_tafsir_insights_en_page, screenshots_en_pattern_bilingual_implementation [INFERRED 0.95]
- **Shared EN Visual Design Language (LTR, serif titles, dark-green sidebar, cream body)**, screenshots_en_pattern_ltr_layout, screenshots_en_pattern_serif_english_typography, screenshots_en_pattern_dark_green_sidebar_palette, screenshots_hero_overview_en_sidebar_navigation [INFERRED 0.85]
- **Overview Data Storytelling Stack (stat cards + carousel insight + bar chart + sunburst)**, screenshots_hero_overview_en_stat_cards_grid, screenshots_hero_overview_en_carousel_juz_card, screenshots_hero_overview_en_pulse_revelation_bar_chart, screenshots_hero_overview_en_sunburst_quran_structure [EXTRACTED 1.00]

## Communities (63 total, 24 thin omitted)

### Community 0 - "Vue App Structure (app.html)"
Cohesion: 0.05
Nodes (46): Quran Analytics Electron App (app.html), chart-radar (Plotly), chart-revelation-pulse (Plotly), TAFSIR_CATEGORIES (8 categories: wisdom, linguistic, scientific, historical, rhetorical, theological, ethical, recitation), TAFSIR_SCHOLARS (10 scholars: classical + modern), didYouKnow[] array (Page 17 carousel), duasData (QURAN_DUAS), heroStats object (Page 17 KPIs) (+38 more)

### Community 1 - "Python Data Pipeline"
Cohesion: 0.05
Nodes (39): _normalize_stopword(), app.py (Streamlit dashboard), render.py (Playwright renderer), HttpServer, smoke_test_app.py (patch verifier), build_cinematic.py (HTML app builder), configurations, version (+31 more)

### Community 2 - "Plotly Chart Visualizations"
Cohesion: 0.06
Nodes (37): chart-area-length (Plotly), chart-boxplot (Plotly), chart-heatmap (Plotly), chart-letters (Plotly), chart-ngram (Plotly), chart-parallel (Plotly), chart-polar-theme (Plotly), chart-pronouns (Plotly) (+29 more)

### Community 3 - "Radar Baseline Config"
Cohesion: 0.06
Nodes (35): family, size, fill, line, marker_size, opacity, id, layout (+27 more)

### Community 4 - "Radar Current Config"
Cohesion: 0.06
Nodes (35): family, size, fill, line, marker_size, opacity, id, layout (+27 more)

### Community 5 - "AutoResearch Mutation Engine"
Cohesion: 0.08
Nodes (30): apply(), _get_path(), _hex_to_hsl(), _hsl_to_hex(), load_space(), Mutation, _mutation_from_knob(), _pick_index() (+22 more)

### Community 6 - "App UI Components"
Cohesion: 0.08
Nodes (32): app.html Concordance Search Component, app.html Hero Stats Dashboard Component, app.html NLP Word Cloud Component, app.html RTL + i18n Layer (lang/dir toggle), app.html Tafsir/Structural Insights Component, Example Prompt Hints (مثال: رحمة، جنة، يوم، الله), Footer Attribution (Master of Business Analytics), Match Mode Chips (كلمة كاملة / بداية كلمة / حرفي بالتشكيل) (+24 more)

### Community 7 - "Phase 2 Roadmap (RAG/BERTopic/Embeddings)"
Cohesion: 0.13
Nodes (19): Competitor: qurananalysis.com, RAG Hallucination Guard, Project Non-Goals, Phase 2.3 RAG Q&A, Phase 2.1 Semantic Verse Search, Phase 2.2 Topic Clustering (BERTopic), Phase 2.4 Public Web Demo, Phase 3 Concept Ontology Graph (+11 more)

### Community 8 - "AutoResearch Orchestrator"
Cohesion: 0.16
Nodes (17): run_heuristics(), append_log(), Best, combined_score(), main(), AutoResearch loop orchestrator for chart-radar.  Main loop:     while not stoppi, Render + heuristic + vision (or stub vision), returning everything., run() (+9 more)

### Community 9 - "Claude Vision Judge"
Cohesion: 0.13
Nodes (17): _cache_key(), judge(), Claude-vision aesthetic judge for chart-radar.  Sends the screenshot + rubric to, Claude usually obeys 'strict JSON' but may wrap in ```json fences., _strict_json_extract(), VisionResult, Vision-judge Rubric, Vision Judge (Claude Sonnet 4.6) (+9 more)

### Community 10 - "Bilingual UI Screenshots"
Cohesion: 0.11
Nodes (19): app.html Language Toggle / i18n Logic, app.html Overview Component (hero stats + carousel + sunburst), app.html Structural Miracles Component, Dark Green Sidebar / Cream Body Palette, LTR English Layout with Right-Side Sidebar, Hero Overview Page (AR counterpart), Carousel Card: Hidden Balance of the 30 Juz, Community / Academic Mode Tabs (+11 more)

### Community 11 - "Quran Analytics UI Layer"
Cohesion: 0.12
Nodes (13): analyze_letters(), arabic_keyboard(), navigate_to(), _normalize_stopword(), page_title(), القرآن الكريم, تحليل نصي | Quran Text Analytics Bilingual Arabic/English NLP Da, Render an on-screen Arabic keyboard. Returns the typed text., # NOTE: These get normalized below via _normalize_stopword() so they match (+5 more)

### Community 12 - "Quran Analytics Computation"
Cohesion: 0.12
Nodes (17): build_word_index(), cluster_surahs(), compute_insights(), compute_mirror_pairs(), compute_ngrams(), compute_word_frequencies(), compute_zipf(), find_cross_references() (+9 more)

### Community 13 - "Radar Polar Baseline"
Cohesion: 0.15
Nodes (15): direction, rotation, tickfont, polar, angularaxis, bgcolor, radialaxis, gridcolor (+7 more)

### Community 14 - "Radar Polar Current"
Cohesion: 0.15
Nodes (15): direction, rotation, tickfont, polar, angularaxis, bgcolor, radialaxis, gridcolor (+7 more)

### Community 15 - "Electron Build Config"
Cohesion: 0.13
Nodes (15): build, appId, dmg, files, icon, mac, productName, win (+7 more)

### Community 16 - "AutoResearch Git Ops"
Cohesion: 0.15
Nodes (13): commit_all(), commit_count_on_branch(), DirtyTreeError, ensure_branch(), open_repo(), Project-local git wrappers for the AutoResearch loop.  Hard-checks that we're op, Switch to branch; create from current HEAD if it doesn't exist., Stage all changes (respecting .gitignore) and commit. Returns sha. (+5 more)

### Community 17 - "AutoResearch Plotly Renderer"
Cohesion: 0.19
Nodes (7): page(), RadarRenderer, Re-fetch radar.json (cache-busted) and re-render., One-shot render. Used by the smoke test., Long-lived browser/page for rendering chart-radar repeatedly.      Workflow:, render_once(), RuntimeError

### Community 18 - "AutoResearch Loop Concepts"
Cohesion: 0.16
Nodes (14): mutate.py (config mutation logic), orchestrator.py (AutoResearch loop), autoresearch/README.md, search_space.json (mutation knobs), AutoResearch chart-radar optimization loop, Branch Isolation (autoresearch/radar), Combined Score = 0.4 heuristic + 0.6 vision, Karpathy AutoResearch Pattern (Mar 2026) (+6 more)

### Community 19 - "Arabic Text Processing"
Cohesion: 0.19
Nodes (13): analyze_divine_pronouns(), compute_ling_stats(), fuzzy_arabic_match(), highlight_word_in_verse(), normalize_arabic(), Remove diacritics (tashkeel) and normalize Arabic text for analysis.      Handle, Strip common Arabic prefixes and suffixes to find the core stem.      This is a, Check if query matches any word in text using root-aware matching.      Normaliz (+5 more)

### Community 20 - "Concordance Search UI"
Cohesion: 0.17
Nodes (13): app.html NLP Explorer Component (word cloud + n-gram), app.html Word Search / Concordance Component, Word Search Page (AR counterpart), MBA Project Credit Footer (semaketir/quranjson), Match Mode Pills (Literal with tashkeel / Ends with / Starts with / Whole word / Free), Word Search / Concordance Page (EN), Search Input Field (LTR placeholder), Bilingual Implementation (English chrome, preserved Arabic verse text) (+5 more)

### Community 21 - "Heuristic Chart Evaluator"
Cohesion: 0.21
Nodes (9): from_raw(), HeuristicResult, Cheap heuristic evaluators that gate the vision-LLM judge.  5 checks, run as a s, run_heuristics(), smoke(), State, HttpServer, Serves electron-app/ on 127.0.0.1:PORT in a daemon thread. (+1 more)

### Community 22 - "NLP Concepts & Data Sources"
Cohesion: 0.18
Nodes (10): KWIC (Key Word In Context), N-gram Explorer (bigrams to 5-grams), Tashkeel-aware Arabic Search, Word Cloud, Sahih International Translation, Yusuf Ali Translation, 19 Interactive Pages, Bilingual-by-Design Pattern (+2 more)

### Community 23 - "External Data File Bindings"
Cohesion: 0.25
Nodes (11): radar.baseline.json (immutable reference), radar.json (mutated config), app.html (Vue 3, ~9,900 lines), quran_duas.js (~114KB), quran_lessons.js (~46KB), quran_stories_data.js (~52KB), Chart Rendering Test Page, QuranAnalytics.html (standalone) (+3 more)

### Community 24 - "Tafsir Scholars Registry"
Cohesion: 0.20
Nodes (10): quran_tafsir_insights.js (~108KB), Page 14 Tafsir Insights, Al-Qurtubi (Tafsir), Al-Sa'di (Tafsir), Fadel Al-Samarrai (Lamasat Bayania), Al-Sha'rawi (Tafsir), Al-Tabari (Tafsir), Ibn Ashur (Tafsir) (+2 more)

### Community 25 - "Quran Analytics Electron Applicatio..."
Cohesion: 0.36
Nodes (9): Quran Analytics Electron Application, Quran Analytics Brand Identity, Concentric Circle Motif, Dark Teal Outer Ring (#0E2530 approx), Minimalist Islamic-Calm Design Language, Electron App Icon (icon.png), Mint Pale Green Inner Disc, QA Monogram Typography (+1 more)

### Community 26 - "Raise if repo's working tree isn't ..."
Cohesion: 0.25
Nodes (6): Raise if repo's working tree isn't the expected project-local one.      Defends, verify_repo(), WrongRepoError, { app, BrowserWindow, Menu }, path, Refuse operating on parent home repo

### Community 27 - "Bilingual Everywhere Principle"
Cohesion: 0.29
Nodes (7): Bilingual Everywhere Principle, Computed Once, Rendered Many, DATA Inline Object (~50KB precomputed JSON), Offline-first Data Principle, Performance Budget Notes, Single-file Frontend Principle, Why Electron rather than Pure Web

### Community 29 - "Madani Mushaf / Hafs Riwayah"
Cohesion: 0.33
Nodes (5): Madani Mushaf / Hafs Riwayah, semarketir/quranjson, quran_madani.json (~1.4MB), surah_extended.json (~31KB), verses_compact.json (~747KB)

### Community 30 - "Page 17 Render Lifecycle"
Cohesion: 0.33
Nodes (6): Page 17 Render Lifecycle, Hijra Dashed Line (Meccan→Medinan shift), Animated Hero Stats Dashboard, Did-You-Know Carousel (10 insights), Page 17 Advanced Analytics, Revelation Pulse Chart

### Community 31 - "_build_page_map()"
Cohesion: 0.40
Nodes (5): _build_page_map(), L(), make_rtl_bar_chart(), Create a horizontal bar chart that reads naturally RTL.      Words on the right, Get localized label. Usage: L('surahs') or L('showing', s=1, e=50, t=100)

### Community 32 - "analyze_rhetoric()"
Cohesion: 0.40
Nodes (5): analyze_rhetoric(), Section Header, returns the right text based on current language., Render a localized section header., section_header(), SH()

### Community 33 - "find_block()"
Cohesion: 0.67
Nodes (3): find_block(), main(), Return (start_idx, end_idx_exclusive) of `const VAR = [...];` block, or None.

### Community 34 - "enrich_data.py"
Cohesion: 0.67
Nodes (3): abjad_value(), normalize_arabic(), Calculate the Abjad numerical value of an Arabic word.

## Knowledge Gaps
- **261 isolated node(s):** `version`, `description`, `knobs`, `palette_min_size`, `min_plot_height` (+256 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **24 thin communities (<3 nodes) omitted from report**, run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run()` connect `AutoResearch Orchestrator` to `Python Data Pipeline`, `AutoResearch Mutation Engine`, `Claude Vision Judge`, `AutoResearch Git Ops`, `AutoResearch Plotly Renderer`, `Heuristic Chart Evaluator`, `Raise if repo's working tree isn't ...`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Why does `app.html (single-file Vue 3 + Plotly app)` connect `Python Data Pipeline` to `AutoResearch Orchestrator`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `RadarRenderer` connect `AutoResearch Orchestrator` to `Python Data Pipeline`, `AutoResearch Loop Concepts`, `Claude Vision Judge`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `run()` (e.g. with `HttpServer` and `RadarRenderer`) actually correct?**
  _`run()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `app.html (Vue 3, ~9,900 lines)` (e.g. with `QuranAnalytics.html (standalone)` and `Chart Rendering Test Page`) actually correct?**
  _`app.html (Vue 3, ~9,900 lines)` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `RadarRenderer` (e.g. with `HeuristicResult` and `Best`) actually correct?**
  _`RadarRenderer` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Calculate the Abjad numerical value of an Arabic word.`, `القرآن الكريم, تحليل نصي | Quran Text Analytics Bilingual Arabic/English NLP Da`, `Apply same normalization to stopwords so they match tokenized text.` to the rest of the system?**
  _327 weakly-connected nodes found - possible documentation gaps or missing edges._