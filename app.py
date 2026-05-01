"""
القرآن الكريم — تحليل نصي | Quran Text Analytics
Bilingual Arabic/English NLP Dashboard
Master of Business Analytics Portfolio Project
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import re
from collections import Counter
from pathlib import Path
import numpy as np
# plotly_events removed — unstable with Streamlit 1.50+
# Using native st.plotly_chart + button grid instead

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Quran Text Analytics | تحليل القرآن",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"

# Arabic stop words (common prepositions, pronouns, particles)
# NOTE: These get normalized below via _normalize_stopword() so they match
# the same normalization applied to Quranic text (Uthmanic script).
_RAW_STOPWORDS = """
في من على إلى عن أن إن لا ما هو هي هم هن نحن أنا أنت أنتم
كان كانت يكون لم لن لو لي بل حتى ثم أو و ف ب ل ك
ذلك تلك هذا هذه الذي التي الذين هؤلاء أولئك ذا كل بعض
قد قال يا لك لكم إلا كما بين عند بعد قبل فوق تحت
لقد كانوا ليس ولا فإن وما ومن وقد ولم فلا بما لهم عليه
عليهم إليه إليهم فيه فيها منه منها منهم بها به لها له
يوم قل إذا إذ كلّ ذو أي ليست ولكن هل ألا
وهم وهي ولو وإن ولكنّ فلم فقد إنه إنها أنه أنها عنه عنها
لكن كأن فمن ومن فما وعن وإلى وعلى فعل ثمّ
""".split()

def _normalize_stopword(w):
    """Apply same normalization to stopwords so they match tokenized text."""
    w = re.sub(r'[إأآا]', 'ا', w)
    w = re.sub(r'[ىي]', 'ي', w)
    w = re.sub(r'ة', 'ه', w)
    w = re.sub(r'ّ', '', w)  # remove shadda
    return w

# NOTE: "الله" (God) and "رب" (Lord) removed from stopwords — they are
# content words essential to Quranic text analysis, not function words.
ARABIC_STOPWORDS = set(_normalize_stopword(w) for w in _RAW_STOPWORDS)

# Colors - warm, professional palette
COLORS = {
    "primary": "#1B4332",
    "secondary": "#2D6A4F",
    "accent": "#52B788",
    "gold": "#D4A574",
    "light": "#D8F3DC",
    "bg": "#FAFDF7",
    "text": "#1B4332",
    "mecca": "#B7094C",
    "medina": "#0091AD",
}

PALETTE = ["#1B4332", "#2D6A4F", "#40916C", "#52B788", "#74C69D",
           "#95D5B2", "#B7E4C7", "#D8F3DC", "#D4A574", "#C68B59"]


# ---------------------------------------------------------------------------
# DATA LOADING (cached)
# ---------------------------------------------------------------------------
@st.cache_data
def load_all_data():
    """Load and structure all Quran data into a single DataFrame."""
    surah_index = json.loads((DATA_DIR / "surah.json").read_text(encoding="utf-8"))
    rows = []
    for meta in surah_index:
        idx = int(meta["index"])
        # Arabic text
        ar_path = DATA_DIR / "surah" / f"surah_{idx}.json"
        ar_data = json.loads(ar_path.read_text(encoding="utf-8"))
        # English translation
        en_path = DATA_DIR / "translation" / "en" / f"en_translation_{idx}.json"
        en_data = json.loads(en_path.read_text(encoding="utf-8"))

        for key in ar_data.get("verse", {}):
            verse_num = int(key.replace("verse_", ""))
            ar_text = ar_data["verse"].get(key, "")
            en_text = en_data["verse"].get(key, "")
            # Clean BOM
            ar_text = ar_text.replace("\ufeff", "").strip()
            rows.append({
                "surah_num": idx,
                "surah_name_en": meta["title"],
                "surah_name_ar": meta["titleAr"],
                "verse_num": verse_num,
                "verse_key": f"{idx}:{verse_num}",
                "arabic": ar_text,
                "english": en_text,
                "place": meta["place"],  # Mecca or Medina
                "type": meta["type"],    # Makkiyah or Madaniyah
                "verse_count": meta["count"],
            })
    df = pd.DataFrame(rows)
    df.sort_values(["surah_num", "verse_num"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def normalize_arabic(text):
    """Remove diacritics (tashkeel) and normalize Arabic text for analysis.

    Handles Uthmanic script used in Quran JSON (alef wasla, small marks, etc.)
    """
    # Remove tashkeel (diacritical marks) - standard range
    text = re.sub(r'[\u0617-\u061A\u064B-\u0652\u0670]', '', text)
    # Remove Uthmanic small/subscript marks (U+06D6-U+06ED, U+08D3-U+08FF)
    text = re.sub(r'[\u06D6-\u06ED]', '', text)
    text = re.sub(r'[\u08D3-\u08FF]', '', text)
    # Remove superscript alef and other combining marks
    text = re.sub(r'[\u0610-\u0615\u0656-\u065F\u0670]', '', text)
    # Normalize alef wasla (ٱ) and hamza variants to plain alef
    text = re.sub(r'[ٱإأآا]', 'ا', text)
    # Normalize ya/alef maqsura
    text = re.sub(r'[ىي]', 'ي', text)
    # Normalize taa marbuta
    text = re.sub(r'ة', 'ه', text)
    # Remove tatweel
    text = re.sub(r'ـ', '', text)
    # Remove zero-width characters and other invisible marks
    text = re.sub(r'[\u200B-\u200F\u202A-\u202E\u2060-\u2064\uFEFF]', '', text)
    return text


def tokenize_arabic(text):
    """Tokenize Arabic text into words, removing stopwords."""
    normalized = normalize_arabic(text)
    # Match Arabic letter sequences only (U+0620-U+064A core letters)
    words = re.findall(r'[\u0620-\u064A]+', normalized)
    return [w for w in words if w not in ARABIC_STOPWORDS and len(w) > 1]


# Common Arabic prefixes and suffixes for stripping
_AR_PREFIXES = ['وال', 'فال', 'بال', 'كال', 'لل', 'ال', 'وب', 'ول', 'وف',
                'فب', 'فل', 'بي', 'لي', 'و', 'ف', 'ب', 'ل', 'ك', 'س']
_AR_SUFFIXES = ['كم', 'هم', 'هن', 'ها', 'نا', 'تم', 'تن', 'وا', 'ون', 'ين',
                'ات', 'ان', 'تا', 'يه', 'ته', 'ك', 'ه', 'ي', 'ا', 'ن', 'ت']

def strip_arabic_affixes(word):
    """Strip common Arabic prefixes and suffixes to find the core stem.

    This is a lightweight stemmer — not as precise as a full morphological
    analyzer, but good enough for search matching. Returns a set of possible
    stems (since stripping is ambiguous).
    """
    normalized = normalize_arabic(word)
    stems = {normalized}  # Always include the full word

    # Try stripping prefixes
    for prefix in _AR_PREFIXES:
        if normalized.startswith(prefix) and len(normalized) - len(prefix) >= 2:
            stem = normalized[len(prefix):]
            stems.add(stem)
            # Also try stripping suffixes from the prefix-stripped form
            for suffix in _AR_SUFFIXES:
                if stem.endswith(suffix) and len(stem) - len(suffix) >= 2:
                    stems.add(stem[:-len(suffix)])

    # Try stripping suffixes only
    for suffix in _AR_SUFFIXES:
        if normalized.endswith(suffix) and len(normalized) - len(suffix) >= 2:
            stems.add(normalized[:-len(suffix)])

    return stems


def fuzzy_arabic_match(query, text):
    """Check if query matches any word in text using root-aware matching.

    Normalizes both, then checks if the query (or any of its stems)
    appears as a substring of any word in the text (or vice versa).
    Returns True if a match is found.
    """
    norm_query = normalize_arabic(query)
    query_stems = strip_arabic_affixes(query)
    # Extract all words from text
    norm_text = normalize_arabic(text)
    text_words = re.findall(r'[\u0620-\u064A]+', norm_text)

    for tw in text_words:
        tw_stems = strip_arabic_affixes(tw)
        # Check if any query stem matches any text word stem
        if query_stems & tw_stems:
            return True
        # Also check substring containment (query root in word or word root in query)
        for qs in query_stems:
            if len(qs) >= 2:
                for ts in tw_stems:
                    if len(ts) >= 2 and (qs in ts or ts in qs):
                        return True
    return False


def highlight_word_in_verse(arabic_text, search_word):
    """Highlight occurrences of search_word in Arabic verse text.

    Matches by normalizing each word, but preserves the original
    Uthmanic script in the output with a highlight span around it.
    """
    if not search_word:
        return arabic_text
    normalized_search = normalize_arabic(search_word)
    # Split on word boundaries while keeping separators
    parts = re.split(r'(\s+)', arabic_text)
    result = []
    for part in parts:
        if part.strip():
            normalized_part = normalize_arabic(part)
            # Strip diacritics for matching
            clean_part = re.sub(r'[^\u0620-\u064A]', '', normalized_part)
            if clean_part == normalized_search:
                result.append(
                    f'<span style="background:linear-gradient(180deg, transparent 40%, #FFD700 40%);'
                    f'padding:2px 4px;border-radius:4px;font-weight:bold;">{part}</span>'
                )
            else:
                result.append(part)
        else:
            result.append(part)
    return ''.join(result)


def make_rtl_bar_chart(data_df, word_col, count_col, color_scale=None,
                       height=400, title=None):
    """Create a horizontal bar chart that reads naturally RTL.

    Words on the right y-axis, bars extending LEFT = natural Arabic reading.
    Sorted so highest count is at the top-right.
    """
    if color_scale is None:
        color_scale = ["#D8F3DC", "#1B4332"]
    # Sort ascending so highest ends up at top in horizontal layout
    plot_df = data_df.sort_values(count_col, ascending=True).reset_index(drop=True)

    fig = px.bar(plot_df, x=count_col, y=word_col, orientation="h",
                 color=count_col, color_continuous_scale=color_scale,
                 text=count_col)
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        yaxis=dict(
            tickfont=dict(size=16, family="Amiri"),
            side="right",  # Labels on RIGHT = RTL
            title="",
        ),
        xaxis=dict(
            title=L("frequency"),
            side="top",
        ),
        coloraxis_showscale=False,
        margin=dict(r=120, t=40, b=10),  # Extra right margin for Arabic labels
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(family="Amiri", size=16)))
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def arabic_keyboard(key_prefix="kb"):
    """Render an on-screen Arabic keyboard. Returns the typed text."""
    if f"{key_prefix}_text" not in st.session_state:
        st.session_state[f"{key_prefix}_text"] = ""

    # Arabic keyboard layout
    rows = [
        ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'د'],
        ['ش', 'س', 'ي', 'ب', 'ل', 'ا', 'ت', 'ن', 'م', 'ك', 'ط'],
        ['ئ', 'ء', 'ؤ', 'ر', 'لا', 'ى', 'ة', 'و', 'ز', 'ظ'],
        ['آ', 'أ', 'إ', 'ذ'],
    ]

    # Display current typed text
    current = st.session_state[f"{key_prefix}_text"]

    cols_display = st.columns([5, 1, 1])
    with cols_display[0]:
        st.markdown(f"""
        <div style="background:white; border:2px solid #D4A574; border-radius:10px; padding:12px 20px;
                    direction:rtl; text-align:right; font-family:Amiri; font-size:1.3rem;
                    min-height:45px; color:#1B4332;">
            {current if current else '<span style="color:#ccc;">⌨️</span>'}
        </div>
        """, unsafe_allow_html=True)
    with cols_display[1]:
        if st.button("⌫", key=f"{key_prefix}_bksp", use_container_width=True):
            st.session_state[f"{key_prefix}_text"] = current[:-1]
            st.rerun()
    with cols_display[2]:
        if st.button("✕", key=f"{key_prefix}_clear", use_container_width=True):
            st.session_state[f"{key_prefix}_text"] = ""
            st.rerun()

    # Render keyboard rows
    for row_idx, row in enumerate(rows):
        cols = st.columns(len(row))
        for col_idx, letter in enumerate(row):
            with cols[col_idx]:
                if st.button(letter, key=f"{key_prefix}_{row_idx}_{col_idx}", use_container_width=True):
                    st.session_state[f"{key_prefix}_text"] = current + letter
                    st.rerun()

    # Space bar
    if st.button("ـــــــ مسافة ـــــــ", key=f"{key_prefix}_space", use_container_width=True):
        st.session_state[f"{key_prefix}_text"] = current + " "
        st.rerun()

    return st.session_state[f"{key_prefix}_text"]


# ---------------------------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Inter:wght@300;400;600;700&display=swap');

    .main { background-color: #FAFDF7; }

    /* === RTL GLOBAL FOUNDATION === */
    /* All content areas default RTL for Arabic-first bilingual layout */
    [data-testid="stMainBlockContainer"] {
        direction: rtl;
    }
    /* Plotly charts and code stay LTR internally */
    .js-plotly-plot, .stCodeBlock, .stDataFrame, pre, code {
        direction: ltr !important;
    }
    /* Streamlit widgets stay LTR for functionality */
    .stSlider, .stNumberInput, .stCheckbox {
        direction: ltr;
    }
    /* Selectbox and multiselect labels RTL */
    .stSelectbox label, .stMultiSelect label, .stTextInput label,
    .stNumberInput label, .stSlider label {
        direction: rtl; text-align: right; font-family: 'Amiri', 'Inter', sans-serif;
    }

    .stMetric {
        background: linear-gradient(135deg, #1B4332, #2D6A4F);
        padding: 20px; border-radius: 12px; color: white;
        direction: rtl; text-align: center;
    }
    .stMetric label { color: #B7E4C7 !important; font-size: 0.85rem;
        font-family: 'Amiri', 'Inter', sans-serif; }
    .stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 2rem; }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B4332, #2D6A4F);
        direction: rtl;
    }
    div[data-testid="stSidebar"] * { color: #D8F3DC !important; }
    div[data-testid="stSidebar"] .stSelectbox label { color: #95D5B2 !important; }
    div[data-testid="stSidebar"] .stRadio label {
        font-family: 'Amiri', 'Inter', sans-serif; font-size: 0.95rem;
    }

    .arabic-text {
        font-family: 'Amiri', serif; font-size: 1.4rem;
        direction: rtl; text-align: right; line-height: 2.2;
        color: #1B4332; padding: 15px;
        background: linear-gradient(135deg, #f0f7f0, #e8f5e8);
        border-radius: 10px; border-right: 4px solid #D4A574;
        margin: 8px 0;
    }

    .section-header {
        font-size: 1.5rem; font-weight: 700; color: #1B4332;
        border-bottom: 3px solid #D4A574; padding-bottom: 8px;
        margin: 30px 0 15px 0;
        direction: rtl; text-align: right;
        font-family: 'Amiri', 'Inter', sans-serif;
    }

    .insight-box {
        background: linear-gradient(135deg, #D8F3DC, #B7E4C7);
        border-right: 5px solid #2D6A4F; padding: 20px;
        border-radius: 12px 0 0 12px; margin: 15px 0;
        font-size: 1rem; color: #1B4332;
        direction: rtl; text-align: right;
        font-family: 'Amiri', 'Inter', sans-serif;
        line-height: 1.9;
    }

    .verse-card {
        background: white; border: 1px solid #D8F3DC;
        border-radius: 10px; padding: 15px; margin: 8px 0;
        box-shadow: 0 2px 8px rgba(27,67,50,0.08);
        direction: rtl; text-align: right;
    }

    /* Page titles — bilingual, Arabic-first */
    .page-title {
        text-align: center; direction: rtl;
        font-family: 'Amiri', serif;
    }
    .page-title h1 { color: #1B4332; font-size: 2.2rem; margin-bottom: 5px; }
    .page-title p { color: #2D6A4F; font-size: 1.1rem; }

    /* Button grid flows RTL */
    [data-testid="stHorizontalBlock"] {
        direction: rtl;
    }
    /* But buttons inside keep text readable */
    .stButton button {
        font-family: 'Amiri', 'Inter', sans-serif;
        font-size: 0.95rem;
    }

    /* Fix tab overflow — make tabs scrollable when too many */
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
        gap: 0px !important;
    }
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap !important;
        flex-shrink: 0 !important;
        padding: 8px 16px !important;
    }

    /* Navigation buttons */
    .nav-btn {
        display: inline-block; padding: 6px 16px;
        background: linear-gradient(135deg, #2D6A4F, #40916C);
        color: white !important; border-radius: 20px;
        text-decoration: none; font-size: 0.85rem;
        margin: 3px; cursor: pointer;
        border: none; transition: all 0.2s;
    }
    .nav-btn:hover { background: linear-gradient(135deg, #1B4332, #2D6A4F); transform: scale(1.03); }

    .breadcrumb {
        font-size: 0.85rem; color: #95D5B2; padding: 8px 0;
        border-bottom: 1px solid #D8F3DC; margin-bottom: 15px;
    }
    .breadcrumb a { color: #2D6A4F; text-decoration: none; }

    /* Clickable word tags */
    .word-tag {
        display: inline-block; padding: 4px 12px; margin: 3px;
        background: #D8F3DC; color: #1B4332; border-radius: 15px;
        font-family: 'Amiri', serif; font-size: 1.1rem;
        cursor: pointer; transition: all 0.2s;
        border: 1px solid #B7E4C7;
    }
    .word-tag:hover { background: #B7E4C7; transform: scale(1.05); }

    .surah-chip {
        display: inline-block; padding: 5px 14px; margin: 3px;
        border-radius: 20px; font-size: 0.9rem;
        cursor: pointer; transition: all 0.2s;
        border: 1px solid;
    }
    .surah-chip-mecca { background: #fce4ec; color: #B7094C; border-color: #B7094C; }
    .surah-chip-medina { background: #e0f7fa; color: #0091AD; border-color: #0091AD; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE — Navigation & Cross-linking
# ---------------------------------------------------------------------------
if "nav_page" not in st.session_state:
    st.session_state.nav_page = None
if "explore_word" not in st.session_state:
    st.session_state.explore_word = ""
if "compare_surah_a" not in st.session_state:
    st.session_state.compare_surah_a = 1
if "compare_surah_b" not in st.session_state:
    st.session_state.compare_surah_b = 2
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "selected_surah" not in st.session_state:
    st.session_state.selected_surah = 1
if "nav_history" not in st.session_state:
    st.session_state.nav_history = []
if "global_place_filter" not in st.session_state:
    st.session_state.global_place_filter = ["Mecca", "Medina"]
if "lang" not in st.session_state:
    st.session_state.lang = "ar"  # Default Arabic

# ---------------------------------------------------------------------------
# LANGUAGE SYSTEM — Arabic / English / Bilingual
# ---------------------------------------------------------------------------
_LABELS = {
    # Page titles
    "app_title":       {"ar": "📖 القرآن الكريم — تحليل نصي",  "en": "📖 Quran Text Analytics",          "bi": "📖 القرآن الكريم — تحليل نصي"},
    "app_subtitle":    {"ar": "لوحة تحليل نصي بالذكاء الاصطناعي", "en": "NLP & Text Analytics Dashboard", "bi": "Quran Text Analytics · Bilingual NLP Dashboard"},
    "overview":        {"ar": "🏠 نظرة عامة",        "en": "🏠 Overview",            "bi": "🏠 Overview | نظرة عامة"},
    "word_analysis":   {"ar": "📝 تحليل الكلمات",    "en": "📝 Word Analysis",       "bi": "📝 Word Analysis | تحليل الكلمات"},
    "verse_structure": {"ar": "📏 بنية الآيات",       "en": "📏 Verse Structure",     "bi": "📏 Verse Structure | بنية الآيات"},
    "mecca_medina":    {"ar": "🗺️ مكية ومدنية",      "en": "🗺️ Mecca vs Medina",    "bi": "🗺️ Mecca vs Medina | مكية ومدنية"},
    "comparator":      {"ar": "⚖️ مقارنة السور",     "en": "⚖️ Surah Comparator",   "bi": "⚖️ Surah Comparator | مقارنة السور"},
    "word_explorer":   {"ar": "🔬 مستكشف الكلمات",   "en": "🔬 Word Explorer",      "bi": "🔬 Word Explorer | مستكشف الكلمات"},
    "topic_modeling":  {"ar": "🧠 نمذجة المواضيع",    "en": "🧠 Topic Modeling",     "bi": "🧠 Topic Modeling | نمذجة المواضيع"},
    "advanced":        {"ar": "📊 تحليل متقدم",      "en": "📊 Advanced Analysis",  "bi": "📊 Advanced Analysis | تحليل متقدم"},
    "structural":      {"ar": "🧩 الأنماط البنيوية",  "en": "🧩 Structural Patterns", "bi": "🧩 Structural Patterns | الأنماط البنيوية"},
    "scientific":      {"ar": "🔭 الإشارات العلمية", "en": "🔭 Scientific References", "bi": "🔭 Scientific References | الإشارات العلمية"},
    "linguistic":      {"ar": "🗣️ التحليل اللغوي",  "en": "🗣️ Linguistic Analysis",  "bi": "🗣️ Linguistic Analysis | التحليل اللغوي"},
    "search":          {"ar": "🔍 البحث",             "en": "🔍 Search",             "bi": "🔍 Search | البحث"},
    # KPI labels
    "surahs":          {"ar": "سور",    "en": "Surahs",        "bi": "سور | Surahs"},
    "verses":          {"ar": "آيات",   "en": "Verses",        "bi": "آيات | Verses"},
    "arabic_words":    {"ar": "كلمات عربية", "en": "Arabic Words", "bi": "كلمات | Arabic Words"},
    "english_words":   {"ar": "كلمات إنجليزية", "en": "English Words", "bi": "English Words"},
    "avg_words":       {"ar": "متوسط الكلمات/آية", "en": "Avg Words/Verse", "bi": "Avg Words/Verse"},
    # Common labels
    "frequency":       {"ar": "التكرار",  "en": "Frequency",     "bi": "التكرار | Frequency"},
    "word":            {"ar": "الكلمة",   "en": "Word",          "bi": "الكلمة | Word"},
    "verse_count":     {"ar": "عدد الآيات", "en": "Verse Count",  "bi": "عدد الآيات | Verse Count"},
    "surah_number":    {"ar": "رقم السورة", "en": "Surah Number", "bi": "رقم السورة | Surah Number"},
    "revelation":      {"ar": "مكان النزول", "en": "Revelation",  "bi": "مكان النزول | Revelation"},
    "mecca":           {"ar": "مكة",      "en": "Mecca",         "bi": "مكة | Mecca"},
    "medina":          {"ar": "المدينة",  "en": "Medina",        "bi": "المدينة | Medina"},
    "back":            {"ar": "⬅️ رجوع",  "en": "⬅️ Back",       "bi": "⬅️ Back | رجوع"},
    "select_surah":    {"ar": "اختر سورة", "en": "Select Surah", "bi": "Select Surah | اختر سورة"},
    "filters":         {"ar": "🎛️ فلاتر", "en": "🎛️ Filters",   "bi": "🎛️ Global Filters | فلاتر"},
    "explore_more":    {"ar": "🚀 استكشف المزيد", "en": "🚀 Explore Further", "bi": "🚀 Explore Further | استكشف المزيد"},
    "key_finding":     {"ar": "💡 نتيجة رئيسية:", "en": "💡 Key Finding:", "bi": "💡 Key Finding | نتيجة رئيسية:"},
    "longest_surahs":  {"ar": "📈 أطول السور",    "en": "📈 Longest Surahs",   "bi": "📈 Longest Surahs | أطول السور"},
    "shortest_surahs": {"ar": "📉 أقصر السور",    "en": "📉 Shortest Surahs",  "bi": "📉 Shortest Surahs | أقصر السور"},
    "click_explore":   {"ar": "🔬 اضغط على كلمة لاستكشافها", "en": "🔬 Click a Word to Explore", "bi": "🔬 Click a Word to Explore | اضغط على كلمة لاستكشافها"},
    "top_words":       {"ar": "🏆 الكلمات الأكثر تكراراً", "en": "🏆 Most Frequent Words", "bi": "🏆 Most Frequent Words | الكلمات الأكثر تكراراً"},
    "per_surah":       {"ar": "🔬 تحليل كل سورة", "en": "🔬 Per-Surah Analysis", "bi": "🔬 Per-Surah Analysis | تحليل كل سورة"},
    "search_label":    {"ar": "أدخل كلمة البحث", "en": "Enter search term", "bi": "Enter search term | أدخل كلمة البحث"},
    "type_word":       {"ar": "اكتب كلمة", "en": "Type a word", "bi": "Type a word | اكتب كلمة"},
    "pick_top50":      {"ar": "اختر من الأكثر تكراراً", "en": "Pick from top 50", "bi": "Pick from top 50 | اختر من الأكثر تكراراً"},
    "page_of":         {"ar": "صفحة {c} من {t}", "en": "Page {c} of {t}", "bi": "Page {c} of {t}"},
    "showing":         {"ar": "عرض {s}–{e} من {t}", "en": "Showing {s}–{e} of {t}", "bi": "Showing {s}–{e} of {t} | عرض {s}–{e} من {t}"},
    "verses_found":    {"ar": "{n} آية", "en": "{n} verses found", "bi": "{n} verses found | {n} آية"},
    "project_footer":  {"ar": "ماجستير تحليلات الأعمال\nمشروع NLP وتحليل النصوص", "en": "Master of Business Analytics\nNLP & Text Analytics Project", "bi": "Master of Business Analytics\nNLP & Text Analytics Project"},
}

def L(key, **kwargs):
    """Get localized label. Usage: L('surahs') or L('showing', s=1, e=50, t=100)"""
    lang = st.session_state.lang
    template = _LABELS.get(key, {}).get(lang, _LABELS.get(key, {}).get("en", key))
    if kwargs:
        return template.format(**kwargs)
    return template

def SH(ar_text, en_text):
    """Section Header — returns the right text based on current language."""
    lang = st.session_state.lang
    if lang == "ar":
        return ar_text
    elif lang == "en":
        return en_text
    else:
        return f"{en_text} | {ar_text}"

def section_header(ar_text, en_text):
    """Render a localized section header."""
    st.markdown(f'<div class="section-header">{SH(ar_text, en_text)}</div>',
                unsafe_allow_html=True)

def page_title(ar_title, en_title, ar_subtitle="", en_subtitle=""):
    """Render a localized page title."""
    lang = st.session_state.lang
    if lang == "ar":
        title, sub = ar_title, ar_subtitle
    elif lang == "en":
        title, sub = en_title, en_subtitle
    else:
        title = f"{ar_title}"
        sub = f"{en_subtitle}" if en_subtitle else ""
    st.markdown(f"""
    <div class="page-title">
        <h1>{title}</h1>
        <p>{sub}</p>
    </div>
    """, unsafe_allow_html=True)

def navigate_to(page_key, **kwargs):
    """Navigate to a page and set context variables."""
    st.session_state.nav_history.append(st.session_state.nav_page or "Overview")
    st.session_state.nav_page = page_key
    for k, v in kwargs.items():
        st.session_state[k] = v

def go_back():
    """Return to previous page."""
    if st.session_state.nav_history:
        st.session_state.nav_page = st.session_state.nav_history.pop()
    else:
        st.session_state.nav_page = None

# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
df = load_all_data()

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
# Build page map dynamically from language
_PAGE_KEYS = ["overview", "word_analysis", "verse_structure", "mecca_medina",
              "comparator", "word_explorer", "topic_modeling", "advanced", "structural", "scientific", "linguistic", "search"]
_PAGE_IDS  = ["Overview", "Word Analysis", "Verse Structure", "Mecca vs Medina",
              "Surah Comparator", "Word Explorer", "Topic Modeling", "Advanced Analysis", "Structural Patterns", "Scientific References", "Linguistic Analysis", "Search"]

def _build_page_map():
    return {L(k): pid for k, pid in zip(_PAGE_KEYS, _PAGE_IDS)}

PAGE_MAP = _build_page_map()
REVERSE_PAGE_MAP = {v: k for k, v in PAGE_MAP.items()}

with st.sidebar:
    # --- LANGUAGE TOGGLE (top of sidebar) ---
    lang_choice = st.radio(
        "🌐",
        ["عربي", "English", "Bilingual"],
        index=["ar", "en", "bi"].index(st.session_state.lang),
        horizontal=True,
        key="lang_toggle"
    )
    new_lang = {"عربي": "ar", "English": "en", "Bilingual": "bi"}[lang_choice]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.markdown("---")

    # Rebuild page map after language set
    PAGE_MAP = _build_page_map()
    REVERSE_PAGE_MAP = {v: k for k, v in PAGE_MAP.items()}

    # If navigated via button, sync radio
    default_idx = 0
    if st.session_state.nav_page and st.session_state.nav_page in REVERSE_PAGE_MAP:
        keys = list(PAGE_MAP.keys())
        target = REVERSE_PAGE_MAP[st.session_state.nav_page]
        if target in keys:
            default_idx = keys.index(target)

    page_label = st.radio(
        "📊",
        list(PAGE_MAP.keys()),
        index=default_idx,
        label_visibility="collapsed"
    )
    page = PAGE_MAP.get(page_label, "Overview")

    # Sync: if user clicks sidebar radio, clear nav override
    if st.session_state.nav_page and page != st.session_state.nav_page:
        st.session_state.nav_page = None

    # Use nav_page override if set (from button clicks)
    if st.session_state.nav_page:
        page = st.session_state.nav_page

    # --- GLOBAL FILTERS ---
    st.markdown("---")
    st.markdown(f"### {L('filters')}")
    _place_options = [L("mecca"), L("medina")]
    # Reset defaults to match current language options
    _valid_defaults = [p for p in _place_options if p in st.session_state.global_place_filter]
    if not _valid_defaults:
        _valid_defaults = _place_options  # show both if mismatch
    st.session_state.global_place_filter = st.multiselect(
        L("revelation"),
        _place_options,
        default=_valid_defaults,
        key="sidebar_place_filter"
    )

    st.markdown("---")
    footer = L("project_footer")
    st.markdown(f"""
    <div style='text-align:center; font-size:0.8rem; color:#95D5B2;'>
    {footer}<br><br>
    Data: semarketir/quranjson<br>
    6,236 verses · 114 surahs
    </div>
    """, unsafe_allow_html=True)

# Apply global filter — map localized names back to data values
_place_reverse = {L("mecca"): "Mecca", L("medina"): "Medina", "Mecca": "Mecca", "Medina": "Medina"}
_selected_places = [_place_reverse.get(p, p) for p in st.session_state.global_place_filter]
if _selected_places:
    df_filtered = df[df["place"].isin(_selected_places)]
else:
    df_filtered = df


# ---------------------------------------------------------------------------
# PAGE: OVERVIEW
# ---------------------------------------------------------------------------
if page == "Overview":
    page_title("📖 القرآن الكريم — تحليل نصي", "📖 Quran Text Analytics", "لوحة تحليل نصي بالذكاء الاصطناعي", "NLP & Text Analytics Dashboard")

    # KPI row
    total_words_ar = df["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x))).sum()
    total_words_en = df["english"].apply(lambda x: len(x.split())).sum()
    avg_verse_len = df["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x))).mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(L("surahs"), "114")
    c2.metric(L("verses"), f"{len(df):,}")
    c3.metric(L("arabic_words"), f"{total_words_ar:,}")
    c4.metric(L("english_words"), f"{total_words_en:,}")
    c5.metric(L("avg_words"), f"{avg_verse_len:.1f}")

    st.markdown("---")

    # Surah length distribution
    col1, col2 = st.columns(2)

    with col1:
        section_header("📊 عدد الآيات لكل سورة", "📊 Verse Count by Surah")
        surah_stats = df.groupby(["surah_num", "surah_name_ar", "surah_name_en", "place"]).size().reset_index(name="verses")
        fig = px.bar(
            surah_stats, x="surah_num", y="verses",
            color="place",
            color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
            hover_data={"surah_name_ar": True, "surah_name_en": True, "surah_num": False},
            labels={"surah_num": SH("رقم السورة", "Surah Number"), "verses": SH("عدد الآيات", "Verse Count"),
                    "place": SH("مكان النزول", "Revelation")},
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("🥧 توزيع مكان النزول", "🥧 Revelation Split")
        place_stats = surah_stats.groupby("place").agg(
            surahs=("surah_num", "count"),
            total_verses=("verses", "sum")
        ).reset_index()
        place_stats["label"] = place_stats.apply(
            lambda r: f"{r['place']}: {r['surahs']} surahs, {r['total_verses']:,} verses", axis=1)

        fig2 = px.pie(
            place_stats, values="total_verses", names="place",
            color="place",
            color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
            hole=0.45
        )
        fig2.update_traces(textinfo="percent+label", textfont_size=14)
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400, showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Insight box
    meccan = surah_stats[surah_stats["place"] == "Mecca"]
    medinan = surah_stats[surah_stats["place"] == "Medina"]
    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('💡 نتيجة رئيسية:', '💡 Key Finding:')}</strong><br>
        {SH(
            f'السور المكية ({len(meccan)} سورة) أقصر في المتوسط ({meccan["verses"].mean():.0f} آية) وتركز على العقيدة. السور المدنية ({len(medinan)} سورة) أطول ({medinan["verses"].mean():.0f} آية) وتتناول التشريعات.',
            f'Meccan surahs ({len(meccan)} surahs) tend to be shorter (avg {meccan["verses"].mean():.0f} verses), focusing on faith and belief. Medinan surahs ({len(medinan)} surahs) are longer (avg {medinan["verses"].mean():.0f} verses), dealing with legislation and community.'
        )}
    </div>
    """, unsafe_allow_html=True)

    # Top 10 longest and shortest surahs
    col3, col4 = st.columns(2)
    with col3:
        section_header("📈 أطول السور", "📈 Longest Surahs")
        top10 = surah_stats.nlargest(10, "verses")
        top10["label"] = top10["surah_name_ar"] + " | " + top10["surah_name_en"]
        fig3 = px.bar(top10, x="verses", y="label", orientation="h",
                      color="place",
                      color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                      text="verses")
        fig3.update_layout(yaxis=dict(autorange="reversed"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          height=380, showlegend=False,
                          xaxis_title=SH("آيات", "Verses"), yaxis_title="")
        fig3.update_traces(textposition="outside")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        section_header("📉 أقصر السور", "📉 Shortest Surahs")
        bot10 = surah_stats.nsmallest(10, "verses")
        bot10["label"] = bot10["surah_name_ar"] + " | " + bot10["surah_name_en"]
        fig4 = px.bar(bot10, x="verses", y="label", orientation="h",
                      color="place",
                      color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                      text="verses")
        fig4.update_layout(yaxis=dict(autorange="reversed"),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          height=380, showlegend=False,
                          xaxis_title=SH("آيات", "Verses"), yaxis_title="")
        fig4.update_traces(textposition="outside")
        st.plotly_chart(fig4, use_container_width=True)

    # Quick navigation buttons
    st.markdown("---")
    section_header("🚀 استكشف المزيد", "🚀 Explore Further")
    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)
    with nav_c1:
        if st.button(L('word_analysis'), use_container_width=True, key="ov_to_wa"):
            navigate_to("Word Analysis")
            st.rerun()
    with nav_c2:
        if st.button(L('mecca_medina'), use_container_width=True, key="ov_to_mm"):
            navigate_to("Mecca vs Medina")
            st.rerun()
    with nav_c3:
        if st.button(L('topic_modeling'), use_container_width=True, key="ov_to_tm"):
            navigate_to("Topic Modeling")
            st.rerun()
    with nav_c4:
        if st.button(L('search'), use_container_width=True, key="ov_to_search"):
            navigate_to("Search")
            st.rerun()


# ---------------------------------------------------------------------------
# PAGE: WORD ANALYSIS
# ---------------------------------------------------------------------------
elif page == "Word Analysis":
    page_title("📝 تحليل الكلمات", "📝 Word Analysis", "تكرار الكلمات العربية والمصطلحات الأكثر شيوعاً", "Arabic word frequency and TF-IDF analysis")

    # Compute word frequencies
    @st.cache_data
    def compute_word_frequencies(_df):
        all_words = []
        surah_words = {}
        for _, row in _df.iterrows():
            words = tokenize_arabic(row["arabic"])
            all_words.extend(words)
            sn = row["surah_num"]
            if sn not in surah_words:
                surah_words[sn] = []
            surah_words[sn].extend(words)
        return Counter(all_words), surah_words

    word_freq, surah_words = compute_word_frequencies(df)

    # Top words
    section_header("🏆 الكلمات الأكثر تكراراً", "🏆 Most Frequent Words")

    top_n = st.slider(SH("عدد الكلمات", "Number of words"), 10, 50, 25)
    top_words = word_freq.most_common(top_n)
    tw_df = pd.DataFrame(top_words, columns=["word", "count"])

    # RTL horizontal bar chart — words on RIGHT, bars extend LEFT — CLICKABLE
    make_rtl_bar_chart(tw_df, "word", "count", height=max(400, top_n * 22))

    # Word frequency table
    col1, col2 = st.columns([3, 2])
    with col1:
        section_header("📋 جدول تكرار الكلمات", "📋 Word Frequency Table")
        table_df = pd.DataFrame(word_freq.most_common(100), columns=[SH("الكلمة", "Word"), SH("التكرار", "Count")])
        table_df.index = range(1, len(table_df) + 1)
        table_df.index.name = SH("الترتيب", "Rank")
        st.dataframe(table_df, height=400, use_container_width=True)

    with col2:
        section_header("💡 ملاحظات", "💡 Insights")
        total_unique = len(word_freq)
        total_all = sum(word_freq.values())
        top5_pct = sum(c for _, c in word_freq.most_common(5)) / total_all * 100

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('إحصائيات المفردات:', 'Vocabulary Statistics:')}</strong><br><br>
            {SH(
                f'📚 الكلمات الفريدة: <strong>{total_unique:,}</strong><br><br>'
                f'📊 إجمالي الكلمات: <strong>{total_all:,}</strong><br><br>'
                f'🎯 أعلى 5 كلمات تغطي <strong>{top5_pct:.1f}%</strong> من النص',
                f'📚 Unique words (after normalization): <strong>{total_unique:,}</strong><br><br>'
                f'📊 Total word tokens: <strong>{total_all:,}</strong><br><br>'
                f'🎯 Top 5 words cover <strong>{top5_pct:.1f}%</strong> of all text'
            )}
        </div>
        """, unsafe_allow_html=True)

    # Clickable word explorer buttons
    st.markdown("---")
    section_header("🔬 اضغط على كلمة لاستكشافها", "🔬 Click a Word to Explore")
    st.markdown(SH("اختر أي كلمة أدناه للانتقال إلى **مستكشف الكلمات** مع تحليل كامل", "Select any word below to jump to the **Word Explorer** with full analysis"))

    # Show top 30 as clickable buttons
    word_btn_cols = st.columns(6)
    for i, (w, c) in enumerate(word_freq.most_common(30)):
        col_idx = i % 6
        with word_btn_cols[col_idx]:
            if st.button(f"{w} ({c})", key=f"wb_{i}", use_container_width=True):
                navigate_to("Word Explorer", explore_word=w)
                st.rerun()

    # Per-surah word analysis
    st.markdown("---")
    section_header("🔬 تحليل كل سورة", "🔬 Per-Surah Analysis")

    surah_options = df.groupby("surah_num").first().reset_index()
    surah_options["label"] = surah_options["surah_num"].astype(str) + ". " + \
                             surah_options["surah_name_ar"] + " | " + surah_options["surah_name_en"]
    selected = st.selectbox(SH("اختر سورة", "Select Surah"), surah_options["label"].tolist())
    sel_num = int(selected.split(".")[0])

    if sel_num in surah_words:
        sw_freq = Counter(surah_words[sel_num])
        sw_top = sw_freq.most_common(20)
        sw_df = pd.DataFrame(sw_top, columns=["word", "count"])

        # RTL horizontal bar chart — CLICKABLE
        make_rtl_bar_chart(sw_df, "word", "count",
                           color_scale=["#D4A574", "#B7094C"],
                           height=max(350, len(sw_df) * 22),
                           title=selected)


# ---------------------------------------------------------------------------
# PAGE: VERSE STRUCTURE
# ---------------------------------------------------------------------------
elif page == "Verse Structure":
    page_title("📏 تحليل بنية الآيات", "📏 Verse Structure", "أطوال الآيات وتوزيع الكلمات والأنماط البنيوية", "Verse lengths, distributions, and patterns")

    # Compute verse lengths
    df["word_count_ar"] = df["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))
    df["word_count_en"] = df["english"].apply(lambda x: len(x.split()))
    df["char_count_ar"] = df["arabic"].apply(len)

    col1, col2 = st.columns(2)

    with col1:
        section_header("📊 توزيع عدد الكلمات", "📊 Word Count Distribution")
        fig = px.histogram(df, x="word_count_ar", nbins=50,
                          color_discrete_sequence=[COLORS["secondary"]],
                          labels={"word_count_ar": SH("كلمات في الآية", "Words per Verse")})
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                         height=380, yaxis_title=SH("التكرار", "Frequency"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("📈 متوسط طول الآية", "📈 Average Verse Length by Surah")
        avg_by_surah = df.groupby(["surah_num", "place"])["word_count_ar"].mean().reset_index()
        fig2 = px.scatter(avg_by_surah, x="surah_num", y="word_count_ar",
                         color="place",
                         color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                         labels={"surah_num": SH("رقم السورة", "Surah Number"),
                                 "word_count_ar": SH("متوسط الكلمات", "Avg Words")},
                         trendline="lowess")
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          height=380)
        st.plotly_chart(fig2, use_container_width=True)

    # Longest and shortest verses
    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        section_header("📖 أطول الآيات", "📖 Longest Verses")
        longest = df.nlargest(5, "word_count_ar")[["verse_key", "surah_name_ar", "surah_name_en",
                                                    "word_count_ar", "arabic"]].reset_index(drop=True)
        for _, row in longest.iterrows():
            st.markdown(f"""
            <div class="verse-card">
                <strong>{row['verse_key']} — {row['surah_name_ar']} | {row['surah_name_en']}</strong>
                <span style='color:#2D6A4F;'> ({row['word_count_ar']} words)</span>
                <div class="arabic-text">{row['arabic'][:150]}...</div>
            </div>
            """, unsafe_allow_html=True)

    with col4:
        section_header("✨ أقصر الآيات", "✨ Shortest Verses")
        shortest = df.nsmallest(5, "word_count_ar")[["verse_key", "surah_name_ar", "surah_name_en",
                                                      "word_count_ar", "arabic"]].reset_index(drop=True)
        for _, row in shortest.iterrows():
            st.markdown(f"""
            <div class="verse-card">
                <strong>{row['verse_key']} — {row['surah_name_ar']} | {row['surah_name_en']}</strong>
                <span style='color:#2D6A4F;'> ({row['word_count_ar']} words)</span>
                <div class="arabic-text">{row['arabic']}</div>
            </div>
            """, unsafe_allow_html=True)

    # Insight
    median_len = df["word_count_ar"].median()
    max_len = df["word_count_ar"].max()
    _struct_ar = f'متوسط طول الآية <strong>{median_len:.0f} كلمة</strong>، لكن التباين كبير — أطول آية تحتوي على <strong>{max_len} كلمة</strong>. الآيات المدنية أطول عموماً لتناولها الأحكام التشريعية.'
    _struct_en = f"The median verse length is <strong>{median_len:.0f} words</strong>, but there is huge variation — the longest verse has <strong>{max_len} words</strong>. Medinan verses tend to be longer, reflecting their legislative content."
    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('💡 ملاحظة بنيوية:', '💡 Structural Insight:')}</strong><br>
        {SH(_struct_ar, _struct_en)}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PAGE: MECCA VS MEDINA
# ---------------------------------------------------------------------------
elif page == "Mecca vs Medina":
    page_title("🗺️ تحليل مكية ومدنية", "🗺️ Mecca vs Medina", "مقارنة فترات النزول من خلال تحليل النصوص", "Comparing revelation periods through text analytics")

    df["word_count_ar"] = df["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))

    mecca_df = df[df["place"] == "Mecca"]
    medina_df = df[df["place"] == "Medina"]

    # KPI comparison
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(SH("سور مكية", "Meccan Surahs"), mecca_df["surah_num"].nunique())
    c2.metric(SH("سور مدنية", "Medinan Surahs"), medina_df["surah_num"].nunique())
    c3.metric(SH("آيات مكية", "Meccan Verses"), f"{len(mecca_df):,}")
    c4.metric(SH("آيات مدنية", "Medinan Verses"), f"{len(medina_df):,}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        section_header("📊 مقارنة طول الكلمات", "📊 Word Length Comparison")
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=mecca_df["word_count_ar"], name=SH("مكة", "Mecca"),
                                   marker_color=COLORS["mecca"], opacity=0.7, nbinsx=40))
        fig.add_trace(go.Histogram(x=medina_df["word_count_ar"], name=SH("المدينة", "Medina"),
                                   marker_color=COLORS["medina"], opacity=0.7, nbinsx=40))
        fig.update_layout(barmode="overlay",
                         plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                         height=400, xaxis_title=SH("كلمات في الآية", "Words per Verse"),
                         yaxis_title=SH("العدد", "Count"),
                         legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("📦 مقارنة صندوقية", "📦 Box Plot Comparison")
        fig2 = px.box(df, x="place", y="word_count_ar",
                     color="place",
                     color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                     labels={"place": SH("مكان النزول", "Revelation Place"),
                             "word_count_ar": SH("كلمات في الآية", "Words per Verse")})
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # Top words comparison
    st.markdown("---")
    section_header("🔤 أكثر الكلمات: مكة مقابل المدينة", "🔤 Top Words: Mecca vs Medina")

    @st.cache_data
    def get_place_words(_df, place):
        words = []
        for text in _df[_df["place"] == place]["arabic"]:
            words.extend(tokenize_arabic(text))
        return Counter(words)

    mecca_words = get_place_words(df, "Mecca")
    medina_words = get_place_words(df, "Medina")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"**{SH('🔴 مكة — أكثر 15 كلمة', '🔴 Mecca — Top 15 words')}**")
        mw_df = pd.DataFrame(mecca_words.most_common(15), columns=[SH("الكلمة", "Word"), SH("العدد", "Count")])
        mw_df.index = range(1, 16)
        st.dataframe(mw_df, use_container_width=True)

    with col4:
        st.markdown(f"**{SH('🔵 المدينة — أكثر 15 كلمة', '🔵 Medina — Top 15 words')}**")
        md_df = pd.DataFrame(medina_words.most_common(15), columns=[SH("الكلمة", "Word"), SH("العدد", "Count")])
        md_df.index = range(1, 16)
        st.dataframe(md_df, use_container_width=True)

    # Distinctive words (TF-IDF style)
    st.markdown("---")
    section_header("🎯 كلمات مميزة", "🎯 Distinctive Words")
    st.markdown(SH("الكلمات التي تظهر بشكل غير متناسب في فترة مقابل الأخرى", "Words that appear disproportionately in one period vs the other"))

    # Calculate relative frequency difference
    all_mecca = sum(mecca_words.values())
    all_medina = sum(medina_words.values())
    all_words_set = set(list(mecca_words.keys()) + list(medina_words.keys()))

    distinctive = []
    for w in all_words_set:
        mc = mecca_words.get(w, 0)
        md = medina_words.get(w, 0)
        if mc + md < 10:
            continue
        mc_rate = mc / all_mecca if all_mecca else 0
        md_rate = md / all_medina if all_medina else 0
        if md_rate > 0:
            ratio = mc_rate / md_rate
        else:
            ratio = 99
        distinctive.append({"word": w, "mecca_count": mc, "medina_count": md,
                           "mecca_rate": mc_rate, "medina_rate": md_rate,
                           "ratio": ratio})

    dist_df = pd.DataFrame(distinctive)

    col5, col6 = st.columns(2)
    with col5:
        st.markdown(f"**{SH('🔴 كلمات مكية مميزة', '🔴 Distinctly Meccan')}**")
        meccan_distinct = dist_df.nlargest(10, "ratio")[["word", "mecca_count", "medina_count"]]
        meccan_distinct.columns = [SH("الكلمة", "Word"), SH("مكة", "Mecca"), SH("المدينة", "Medina")]
        meccan_distinct.index = range(1, 11)
        st.dataframe(meccan_distinct, use_container_width=True)

    with col6:
        st.markdown(f"**{SH('🔵 كلمات مدنية مميزة', '🔵 Distinctly Medinan')}**")
        medinan_distinct = dist_df.nsmallest(10, "ratio")[["word", "mecca_count", "medina_count"]]
        medinan_distinct.columns = [SH("الكلمة", "Word"), SH("مكة", "Mecca"), SH("المدينة", "Medina")]
        medinan_distinct.index = range(1, 11)
        st.dataframe(medinan_distinct, use_container_width=True)

    # Clickable explore buttons for distinctive words
    st.markdown("---")
    st.markdown(f"**{SH('🔬 اضغط لاستكشاف أي كلمة مميزة:', '🔬 Click to explore any distinctive word:')}**")
    meccan_words_list = dist_df.nlargest(10, "ratio")["word"].tolist()
    medinan_words_list = dist_df.nsmallest(10, "ratio")["word"].tolist()
    dw_cols = st.columns(5)
    for i, w in enumerate(meccan_words_list[:5]):
        with dw_cols[i]:
            if st.button(f"🔴 {w}", key=f"mec_dw_{i}", use_container_width=True):
                navigate_to("Word Explorer", explore_word=w)
                st.rerun()
    dw_cols2 = st.columns(5)
    for i, w in enumerate(medinan_words_list[:5]):
        with dw_cols2[i]:
            if st.button(f"🔵 {w}", key=f"med_dw_{i}", use_container_width=True):
                navigate_to("Word Explorer", explore_word=w)
                st.rerun()

    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('💡 تحليل الفترات:', '💡 Period Analysis:')}</strong><br>
        {SH(
            f'متوسط الآية المكية <strong>{mecca_df["word_count_ar"].mean():.1f}</strong> كلمة مقابل المدنية <strong>{medina_df["word_count_ar"].mean():.1f}</strong> كلمة. يعكس هذا التحول من الإعلانات القصيرة القوية (المكية) إلى التوجيهات القانونية والاجتماعية التفصيلية (المدنية).',
            f'Meccan surahs average <strong>{mecca_df["word_count_ar"].mean():.1f}</strong> words/verse vs Medinan <strong>{medina_df["word_count_ar"].mean():.1f}</strong> words/verse. This reflects the shift from short, powerful proclamations (Meccan) to detailed legal and social guidance (Medinan).'
        )}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PAGE: SURAH COMPARATOR
# ---------------------------------------------------------------------------
elif page == "Surah Comparator":
    if st.session_state.nav_history:
        if st.button(L('back'), key="sc_back"):
            go_back()
            st.rerun()

    page_title("⚖️ مقارنة السور", "⚖️ Surah Comparator", "مقارنة السور جنباً إلى جنب: تكرار الكلمات والبنية", "Compare surahs side-by-side")

    # Build surah options
    surah_opts = df.groupby("surah_num").first().reset_index()
    surah_opts["label"] = surah_opts["surah_num"].astype(str) + ". " + \
                          surah_opts["surah_name_ar"] + " | " + surah_opts["surah_name_en"]

    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        sel_a = st.selectbox(SH("📗 السورة الأولى", "📗 Surah A"), surah_opts["label"].tolist(), index=0)
    with col_sel2:
        sel_b = st.selectbox(SH("📘 السورة الثانية", "📘 Surah B"), surah_opts["label"].tolist(), index=1)

    num_a = int(sel_a.split(".")[0])
    num_b = int(sel_b.split(".")[0])
    df_a = df[df["surah_num"] == num_a]
    df_b = df[df["surah_num"] == num_b]

    # KPI comparison row
    st.markdown("---")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    name_a = df_a.iloc[0]["surah_name_ar"]
    name_b = df_b.iloc[0]["surah_name_ar"]

    wc_a = df_a["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))
    wc_b = df_b["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))

    _place_a = SH("مكة", "Mecca") if df_a.iloc[0]["place"] == "Mecca" else SH("المدينة", "Medina")
    _place_b = SH("مكة", "Mecca") if df_b.iloc[0]["place"] == "Mecca" else SH("المدينة", "Medina")

    c1.metric(f"📗 {name_a}", SH(f"{len(df_a)} آية", f"{len(df_a)} verses"))
    c2.metric(SH("متوسط الكلمات/آية", "Avg words/verse"), f"{wc_a.mean():.1f}")
    c3.metric(SH("مكان النزول", "Revelation"), _place_a)
    c4.metric(f"📘 {name_b}", SH(f"{len(df_b)} آية", f"{len(df_b)} verses"))
    c5.metric(SH("متوسط الكلمات/آية", "Avg words/verse"), f"{wc_b.mean():.1f}")
    c6.metric(SH("مكان النزول", "Revelation"), _place_b)

    st.markdown("---")

    # Word frequency comparison
    section_header("📊 مقارنة تكرار الكلمات", "📊 Word Frequency Comparison")

    words_a = Counter()
    for t in df_a["arabic"]:
        words_a.update(tokenize_arabic(t))
    words_b = Counter()
    for t in df_b["arabic"]:
        words_b.update(tokenize_arabic(t))

    # Get union of top words
    top_a = set(w for w, _ in words_a.most_common(15))
    top_b = set(w for w, _ in words_b.most_common(15))
    compare_words = list(top_a | top_b)

    comp_df = pd.DataFrame({
        "word": compare_words,
        name_a: [words_a.get(w, 0) for w in compare_words],
        name_b: [words_b.get(w, 0) for w in compare_words],
    }).sort_values(name_a, ascending=False).head(20)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=comp_df["word"], y=comp_df[name_a],
                              name=f"📗 {name_a}", marker_color=COLORS["mecca"]))
    fig_comp.add_trace(go.Bar(x=comp_df["word"], y=comp_df[name_b],
                              name=f"📘 {name_b}", marker_color=COLORS["medina"]))
    fig_comp.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=420, xaxis=dict(tickfont=dict(size=14, family="Amiri"), autorange="reversed"),
        legend=dict(orientation="h", y=1.1),
        yaxis_title=SH("التكرار", "Frequency")
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # Verse length distribution comparison
    section_header("📏 توزيع طول الآيات", "📏 Verse Length Distribution")

    fig_vl = go.Figure()
    fig_vl.add_trace(go.Histogram(x=wc_a, name=f"📗 {name_a}",
                                   marker_color=COLORS["mecca"], opacity=0.7, nbinsx=25))
    fig_vl.add_trace(go.Histogram(x=wc_b, name=f"📘 {name_b}",
                                   marker_color=COLORS["medina"], opacity=0.7, nbinsx=25))
    fig_vl.update_layout(
        barmode="overlay", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=350, xaxis_title=SH("كلمات في الآية", "Words per Verse"),
        yaxis_title=SH("العدد", "Count"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_vl, use_container_width=True)

    # Unique words comparison (Venn-style stats)
    section_header("🔤 تداخل المفردات", "🔤 Vocabulary Overlap")

    vocab_a = set(words_a.keys())
    vocab_b = set(words_b.keys())
    shared = vocab_a & vocab_b
    only_a = vocab_a - vocab_b
    only_b = vocab_b - vocab_a

    vc1, vc2, vc3 = st.columns(3)
    vc1.metric(SH(f"فقط في {name_a}", f"Only in {name_a}"), len(only_a))
    vc2.metric(SH("كلمات مشتركة", "Shared Words"), len(shared))
    vc3.metric(SH(f"فقط في {name_b}", f"Only in {name_b}"), len(only_b))

    jaccard = len(shared) / len(vocab_a | vocab_b) if (vocab_a | vocab_b) else 0
    _high_ar = "تداخل عالي يشير إلى مواضيع متشابهة"
    _low_ar = "تداخل منخفض يشير إلى مواضيع ومفردات مختلفة"
    _high_en = "High overlap suggests similar themes"
    _low_en = "Low overlap suggests different themes and vocabulary"
    _interp_ar = _high_ar if jaccard > 0.3 else _low_ar
    _interp_en = _high_en if jaccard > 0.3 else _low_en
    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('💡 درجة التشابه:', '💡 Similarity Score:')}</strong><br>
        {SH('معامل جاكارد', 'Jaccard similarity')}: <strong>{jaccard:.2%}</strong>
        — {SH(_interp_ar, _interp_en)}
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PAGE: WORD EXPLORER
# ---------------------------------------------------------------------------
elif page == "Word Explorer":
    # Back button
    if st.session_state.nav_history:
        if st.button(L('back'), key="we_back"):
            go_back()
            st.rerun()

    page_title("🔬 مستكشف الكلمات", "🔬 Word Explorer", "تعمق في أي كلمة عربية: أين تظهر وأنماط التكرار والسياق", "Deep-dive into any Arabic word")

    @st.cache_data
    def build_word_index(_df):
        """Build a reverse index: word -> list of (surah_num, verse_num, place)."""
        word_idx = {}
        for _, row in _df.iterrows():
            words = tokenize_arabic(row["arabic"])
            for w in set(words):  # unique per verse
                if w not in word_idx:
                    word_idx[w] = []
                word_idx[w].append({
                    "surah_num": row["surah_num"],
                    "surah_ar": row["surah_name_ar"],
                    "surah_en": row["surah_name_en"],
                    "verse_num": row["verse_num"],
                    "verse_key": row["verse_key"],
                    "place": row["place"],
                    "arabic": row["arabic"],
                    "english": row["english"],
                })
        return word_idx

    @st.cache_data
    def get_all_word_freqs(_df):
        freq = Counter()
        for text in _df["arabic"]:
            freq.update(tokenize_arabic(text))
        return freq

    word_index = build_word_index(df)
    all_freqs = get_all_word_freqs(df)

    # Word selection - top words as quick picks + free text
    section_header("🎯 اختر كلمة", "🎯 Select a Word")

    top_50 = [w for w, _ in all_freqs.most_common(50)]

    # Pre-fill from session state (when navigated from another page)
    default_word = st.session_state.get("explore_word", "")

    # Arabic virtual keyboard
    with st.expander(SH("⌨️ لوحة مفاتيح عربية", "⌨️ Arabic Keyboard"), expanded=False):
        kb_word = arabic_keyboard("explorer_kb")

    col_input, col_quick = st.columns([2, 3])
    with col_input:
        # Pre-fill from keyboard if used, otherwise from session state
        _kb_val = st.session_state.get("explorer_kb_text", "")
        _default = _kb_val if _kb_val else default_word
        typed_word = st.text_input(SH("اكتب كلمة", "Type a word"), value=_default, placeholder="الله")
    with col_quick:
        # Find default index for quick pick
        qp_default = 0
        if default_word and default_word in top_50:
            qp_default = top_50.index(default_word) + 1
        quick_pick = st.selectbox(SH("أو اختر من الأكثر تكراراً", "Or pick from top 50"),
                                  [""] + top_50,
                                  index=qp_default,
                                  format_func=lambda x: x if x else SH("— اختر —", "— Select —"))

    # Resolve which word to explore
    raw_word = typed_word.strip() if typed_word.strip() else quick_pick
    # Clear session state after using it
    if st.session_state.get("explore_word"):
        st.session_state.explore_word = ""
    if raw_word:
        # Normalize the input
        explore_word = normalize_arabic(raw_word)

        # ALWAYS do root-aware search: find all verses where the normalized
        # root appears as a substring of any word in the verse.
        # This catches ALL derived forms: الشهر, شهرين, بالشهر, أشهر, etc.
        root_occurrences = []
        matched_forms = Counter()
        for _, row in df.iterrows():
            norm_verse = normalize_arabic(row["arabic"])
            verse_words = re.findall(r'[\u0620-\u064A]+', norm_verse)
            found_in_verse = False
            for w in verse_words:
                if explore_word in w:
                    matched_forms[w] += 1
                    found_in_verse = True
            if found_in_verse:
                root_occurrences.append({
                    "surah_num": row["surah_num"],
                    "surah_ar": row["surah_name_ar"],
                    "surah_en": row["surah_name_en"],
                    "verse_num": row["verse_num"],
                    "verse_key": row["verse_key"],
                    "place": row["place"],
                    "arabic": row["arabic"],
                    "english": row["english"],
                })

        if root_occurrences:
            occurrences = root_occurrences
            occ_df = pd.DataFrame(occurrences)
            total_count = sum(matched_forms.values())

            # Show derived forms found
            if len(matched_forms) > 1 or (len(matched_forms) == 1 and list(matched_forms.keys())[0] != explore_word):
                forms_display = " · ".join(f"{w} ({c})" for w, c in matched_forms.most_common())
                st.markdown(f"""
                <div class="insight-box">
                    <strong>{SH('🔍 بحث بالجذر:', '🔍 Root search:')}</strong>
                    {SH(f'وجدنا {len(matched_forms)} صيغة مشتقة من "{raw_word}" في {len(occ_df)} آية ({total_count} تكرار):',
                        f'Found {len(matched_forms)} forms derived from "{raw_word}" in {len(occ_df)} verses ({total_count} occurrences):')}
                    <br>
                    <span style="font-family:Amiri; font-size:1.1rem;">{forms_display}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            occ_df = None
            total_count = 0

        if occ_df is not None and len(occ_df) > 0:

            st.markdown("---")

            # KPI row
            k1, k2, k3, k4 = st.columns(4)
            k1.metric(SH("إجمالي التكرار", "Total Occurrences"), f"{total_count:,}")
            k2.metric(SH("السور", "Surahs"), occ_df["surah_num"].nunique())
            mecca_pct = len(occ_df[occ_df["place"] == "Mecca"]) / len(occ_df) * 100
            k3.metric(SH("مكية", "Meccan"), f"{mecca_pct:.0f}%")
            k4.metric(SH("مدنية", "Medinan"), f"{100 - mecca_pct:.0f}%")

            # Distribution across surahs
            section_header("📊 التوزيع عبر السور", "📊 Distribution Across Surahs")

            surah_dist = occ_df.groupby(["surah_num", "surah_ar", "place"]).size().reset_index(name="count")
            surah_dist = surah_dist.sort_values("count", ascending=False).head(20)
            surah_dist["label"] = surah_dist["surah_ar"]

            # RTL horizontal bars — surah names on RIGHT
            surah_dist_sorted = surah_dist.sort_values("count", ascending=True)
            fig_wd = px.bar(surah_dist_sorted, x="count", y="label", orientation="h",
                           color="place",
                           color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                           text="count")
            fig_wd.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=max(350, len(surah_dist) * 25),
                yaxis=dict(tickfont=dict(size=14, family="Amiri"), side="right"),
                xaxis=dict(title=SH("التكرار", "Frequency"), side="top"),
                legend=dict(orientation="h", y=-0.1)
            )
            fig_wd.update_traces(textposition="outside")
            st.plotly_chart(fig_wd, use_container_width=True)

            # Mecca vs Medina split
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                section_header("🥧 توزيع النزول", "🥧 Revelation Split")
                place_counts = occ_df["place"].value_counts().reset_index()
                place_counts.columns = ["place", "count"]
                fig_pie = px.pie(place_counts, values="count", names="place",
                                color="place",
                                color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                                hole=0.4)
                fig_pie.update_traces(textinfo="percent+label")
                fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                     height=300, showlegend=False)
                st.plotly_chart(fig_pie, use_container_width=True)

            with col_m2:
                section_header("📈 التكرار عبر القرآن", "📈 Frequency Across Quran")
                # Heatmap-style: count by surah number
                all_surah_counts = occ_df.groupby("surah_num").size().reset_index(name="count")
                fig_scatter = px.scatter(all_surah_counts, x="surah_num", y="count",
                                        size="count", color="count",
                                        color_continuous_scale=["#D8F3DC", "#1B4332"],
                                        labels={"surah_num": SH("رقم السورة", "Surah #"), "count": SH("العدد", "Count")})
                fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                         height=300, coloraxis_showscale=False)
                st.plotly_chart(fig_scatter, use_container_width=True)

            # Show sample verses
            st.markdown("---")
            section_header(f"📖 آيات تحتوي الكلمة \"{explore_word}\"", f"📖 Sample Verses Containing \"{explore_word}\"")

            # Filter controls
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                place_filter = st.multiselect(SH("تصفية حسب المكان", "Filter by Place"),
                                              ["Mecca", "Medina"], default=["Mecca", "Medina"])
            with filter_col2:
                surah_filter_we = st.multiselect(SH("تصفية حسب السورة", "Filter by Surah"),
                                                  occ_df["surah_ar"].unique().tolist())

            filtered_occ = occ_df[occ_df["place"].isin(place_filter)]
            if surah_filter_we:
                filtered_occ = filtered_occ[filtered_occ["surah_ar"].isin(surah_filter_we)]

            total_filtered = len(filtered_occ)
            PAGE_SIZE = 50
            total_pages = max(1, (total_filtered + PAGE_SIZE - 1) // PAGE_SIZE)

            pag_col1, pag_col2, pag_col3 = st.columns([2, 3, 2])
            with pag_col1:
                st.markdown(f"**{L('verses_found', n=total_filtered)}**")
            with pag_col2:
                current_page = st.number_input(
                    SH(f"الصفحة (1–{total_pages})", f"Page (1–{total_pages})"),
                    min_value=1, max_value=total_pages, value=1, step=1,
                    key="word_explorer_page"
                )
            with pag_col3:
                st.markdown(f"**{SH(f'صفحة {current_page} من {total_pages}', f'Page {current_page} of {total_pages}')}**")

            start_idx = (current_page - 1) * PAGE_SIZE
            end_idx = min(start_idx + PAGE_SIZE, total_filtered)
            page_slice = filtered_occ.iloc[start_idx:end_idx]

            for _, row in page_slice.iterrows():
                highlighted_ar = highlight_word_in_verse(row['arabic'], explore_word)
                st.markdown(f"""
                <div class="verse-card">
                    <strong style='color:#2D6A4F;'>{row['verse_key']} — {row['surah_ar']} | {row['surah_en']}</strong>
                    <span style='color:#95D5B2; font-size:0.85rem;'> ({row['place']})</span>
                    <div class="arabic-text">{highlighted_ar}</div>
                    <div style='color:#555; padding:5px 15px; font-style:italic;'>{row['english']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center; color:#95D5B2; padding:10px;'>"
                        f"{SH(f'عرض {start_idx+1}–{end_idx} من {total_filtered}', f'Showing {start_idx+1}–{end_idx} of {total_filtered}')}</div>",
                        unsafe_allow_html=True)

        else:
            st.warning(SH(f"الكلمة '{raw_word}' غير موجودة حتى بعد البحث بالجذر. جرب كلمة أخرى.",
                          f"Word '{raw_word}' not found even with root search. Try a different word."))
    else:
        st.info(SH("👆 اكتب كلمة أو اختر من القائمة للاستكشاف", "👆 Type a word or select from the top 50 to explore"))


# ---------------------------------------------------------------------------
# PAGE: TOPIC MODELING
# ---------------------------------------------------------------------------
elif page == "Topic Modeling":
    if st.session_state.nav_history:
        if st.button(L('back'), key="tm_back"):
            go_back()
            st.rerun()

    page_title("🧠 نمذجة المواضيع", "🧠 Topic Modeling",
               "اكتشف المواضيع المخفية في القرآن باستخدام تخصيص ديريكليه الكامن",
               "Discover hidden themes using Latent Dirichlet Allocation")

    # Explanation box — make LDA understandable
    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('🎓 ما هي نمذجة المواضيع؟', '🎓 What is Topic Modeling?')}</strong><br><br>
        {SH(
            'تخيّل أنك تقرأ كل سور القرآن وتحاول تصنيفها حسب الموضوع يدوياً — هذا بالضبط ما يفعله الكمبيوتر هنا، لكن رياضياً.'
            '<br><br>'
            '<strong>كيف يعمل:</strong> النموذج يقرأ كلمات كل سورة ويبحث عن أنماط — أي كلمات تظهر معاً بشكل متكرر؟'
            ' مثلاً: إذا ظهرت كلمات "نار" و"عذاب" و"يوم" معاً كثيراً، يكتشف النموذج أن هناك "موضوعاً" عن اليوم الآخر.'
            '<br><br>'
            '<strong>النتيجة:</strong> كل سورة تحتوي على <em>مزيج</em> من المواضيع — مثلاً سورة البقرة قد تكون 30% أحكام + 25% قصص أنبياء + 20% عقيدة + 25% مواضيع أخرى.'
            '<br><br>'
            '<strong>الأهمية:</strong> هذا التحليل يكشف عن أنماط لا يمكن رؤيتها بالقراءة العادية — مثل أي المواضيع تتكرر أكثر في السور المكية مقابل المدنية.',
            'Imagine reading every surah and manually categorizing them by theme — that is exactly what the computer does here, but mathematically.'
            '<br><br>'
            '<strong>How it works:</strong> The model reads every word in each surah and looks for patterns — which words appear together frequently?'
            ' For example: if "fire", "punishment", and "day" appear together often, the model discovers a "topic" about the Day of Judgment.'
            '<br><br>'
            '<strong>Result:</strong> Each surah contains a <em>mix</em> of topics — e.g. Al-Baqara might be 30% rulings + 25% prophets stories + 20% belief + 25% other themes.'
            '<br><br>'
            '<strong>Why it matters:</strong> This analysis reveals patterns invisible to normal reading — like which themes are more common in Meccan vs Medinan surahs.'
        )}
    </div>
    """, unsafe_allow_html=True)

    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation

    @st.cache_data
    def run_topic_model(_df, n_topics=7, n_top_words=10):
        """Run LDA topic model on surah-level aggregated text."""
        # Aggregate text per surah (better topics than verse-level)
        surah_texts = []
        surah_meta = []
        for sn in sorted(_df["surah_num"].unique()):
            sdf = _df[_df["surah_num"] == sn]
            all_words = []
            for text in sdf["arabic"]:
                all_words.extend(tokenize_arabic(text))
            surah_texts.append(" ".join(all_words))
            surah_meta.append({
                "surah_num": sn,
                "surah_ar": sdf.iloc[0]["surah_name_ar"],
                "surah_en": sdf.iloc[0]["surah_name_en"],
                "place": sdf.iloc[0]["place"],
                "verse_count": len(sdf),
            })

        # Build document-term matrix
        # Remove very high-frequency words that appear in 80%+ of surahs
        # (they're too common to distinguish topics — e.g. الله, رب)
        # Also require min 5 surahs to avoid noise from rare words
        vectorizer = CountVectorizer(max_features=2000, min_df=5, max_df=0.80)
        dtm = vectorizer.fit_transform(surah_texts)
        feature_names = vectorizer.get_feature_names_out()

        # Fit LDA
        lda = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=50,
            learning_method="batch",
            doc_topic_prior=0.1,   # Sparser topic distribution per surah
            topic_word_prior=0.01,  # Sparser word distribution per topic
        )
        doc_topics = lda.fit_transform(dtm)

        # Extract top words per topic
        topics = []
        for idx, topic in enumerate(lda.components_):
            top_indices = topic.argsort()[-n_top_words:][::-1]
            top_words = [(feature_names[i], topic[i]) for i in top_indices]
            topics.append(top_words)

        # Dominant topic per surah
        meta_df = pd.DataFrame(surah_meta)
        meta_df["dominant_topic"] = doc_topics.argmax(axis=1)
        meta_df["topic_confidence"] = doc_topics.max(axis=1)

        return topics, doc_topics, meta_df

    # Interactive controls
    section_header("⚙️ معلمات النموذج", "⚙️ Model Parameters")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        n_topics = st.slider(SH("عدد المواضيع", "Number of Topics"), 3, 15, 7,
                            help=SH("مواضيع أكثر = تفاصيل أدق. 5-8 مناسب للتحليل الاستكشافي.",
                                    "More topics = more granular themes. 5-8 is typical for exploratory analysis."))
    with col_p2:
        n_words = st.slider(SH("كلمات لكل موضوع", "Words per Topic"), 5, 20, 10)

    topics, doc_topics, meta_df = run_topic_model(df, n_topics, n_words)

    # Auto-name topics based on top words
    # Map common Arabic roots to thematic names
    _TOPIC_THEMES = {
        "الله": ("التوحيد والإيمان", "Monotheism & Faith"),
        "الارض": ("الخلق والطبيعة", "Creation & Nature"),
        "الناس": ("المجتمع والبشر", "Society & Humanity"),
        "عذاب": ("التحذير والعقاب", "Warning & Punishment"),
        "ءامنوا": ("الإيمان والعمل", "Faith & Deeds"),
        "كفروا": ("الكفر والإنكار", "Disbelief & Denial"),
        "قالوا": ("الحوار والقصص", "Dialogue & Stories"),
        "ربك": ("العلاقة مع الله", "Relationship with God"),
        "السموت": ("الكون والسماوات", "Cosmos & Heavens"),
        "يوم": ("اليوم الآخر", "Day of Judgment"),
        "كنتم": ("المحاسبة", "Accountability"),
        "والذين": ("الأحكام والجماعة", "Rulings & Community"),
    }

    # Expanded theme dictionary for better naming
    _TOPIC_THEMES = {
        "الارض": ("الأرض والطبيعة", "Earth & Nature"),
        "الناس": ("المجتمع والبشر", "Society & Humanity"),
        "عذاب": ("التحذير والعقاب", "Warning & Punishment"),
        "ءامنوا": ("الإيمان والعمل", "Faith & Deeds"),
        "كفروا": ("الكفر والإنكار", "Disbelief & Denial"),
        "قالوا": ("الحوار والقصص", "Dialogue & Stories"),
        "السموت": ("الكون والسماوات", "Cosmos & Heavens"),
        "كنتم": ("المحاسبة والأعمال", "Accountability"),
        "والذين": ("الأحكام والجماعة", "Rulings & Community"),
        "نار": ("النار والعذاب", "Fire & Punishment"),
        "جنت": ("الجنة والثواب", "Paradise & Reward"),
        "اهل": ("أهل الكتاب", "People of the Book"),
        "بني": ("بنو إسرائيل", "Children of Israel"),
        "قوم": ("قصص الأقوام", "Stories of Nations"),
        "ايه": ("الآيات والعبر", "Signs & Lessons"),
        "موسي": ("قصة موسى", "Story of Moses"),
        "قالوا": ("الحوارات", "Dialogues"),
        "شيء": ("الخلق والقدرة", "Creation & Power"),
        "علم": ("العلم والمعرفة", "Knowledge"),
        "حق": ("الحق والعدل", "Truth & Justice"),
        "امر": ("الأوامر والتشريع", "Commands & Legislation"),
        "اموال": ("المال والإنفاق", "Wealth & Charity"),
        "صلوه": ("العبادة والصلاة", "Worship & Prayer"),
        "كتب": ("الكتاب والوحي", "Scripture & Revelation"),
    }

    def auto_name_topic(top_words_list):
        """Generate a thematic name from the most distinctive word."""
        # Try matching against theme dictionary
        for w, _ in top_words_list[:8]:
            if w in _TOPIC_THEMES:
                return _TOPIC_THEMES[w]
        # Fallback: use top 2 distinctive words as the name
        w1 = top_words_list[0][0] if top_words_list else "?"
        w2 = top_words_list[1][0] if len(top_words_list) > 1 else ""
        return (f"{w1} و {w2}", f"{w1} & {w2}")

    # Topic overview
    st.markdown("---")
    section_header("📋 المواضيع المكتشفة", "📋 Discovered Topics")

    st.markdown(f"""
    <div class="insight-box">
        {SH(
            '📌 <strong>كيف تقرأ هذا:</strong> كل "موضوع" أدناه هو مجموعة من الكلمات التي يظهرها الكمبيوتر معاً بشكل متكرر. '
            'أعطينا كل موضوع اسماً بناءً على كلماته الرئيسية. الأرقام بجانب كل كلمة تمثل "وزنها" — كلما زاد الرقم، كلما كانت الكلمة أكثر أهمية لهذا الموضوع.',
            '📌 <strong>How to read this:</strong> Each "topic" below is a group of words the computer found appearing together frequently. '
            'We named each topic based on its key words. The numbers next to each word represent its "weight" — higher means more important to that topic.'
        )}
    </div>
    """, unsafe_allow_html=True)

    topic_labels = []
    for i, topic_words in enumerate(topics):
        words_str = " · ".join([w for w, _ in topic_words[:5]])
        theme_ar, theme_en = auto_name_topic(topic_words)
        label = SH(f"{theme_ar}", f"{theme_en}")
        topic_labels.append(label)

        with st.expander(f"🏷️ {i+1}. {label}: {words_str}", expanded=(i < 3)):
            # Word weights chart
            _tw_word_col = SH("الكلمة", "word")
            _tw_weight_col = SH("الوزن", "weight")
            tw_data = pd.DataFrame(topic_words, columns=[_tw_word_col, _tw_weight_col])
            tw_data = tw_data.iloc[::-1]  # RTL
            fig_tw = px.bar(tw_data, x=_tw_weight_col, y=_tw_word_col, orientation="h",
                           color=_tw_weight_col, color_continuous_scale=["#D8F3DC", "#1B4332"],
                           text=tw_data[_tw_weight_col].apply(lambda x: f"{x:.1f}"))
            fig_tw.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                height=max(250, len(tw_data) * 28),
                yaxis=dict(tickfont=dict(size=15, family="Amiri"), title=""),
                coloraxis_showscale=False,
                xaxis_title=SH("الوزن", "Weight"), yaxis_title=""
            )
            fig_tw.update_traces(textposition="outside")
            fig_tw.update_layout(margin=dict(r=100, t=30, b=10))
            st.plotly_chart(fig_tw, use_container_width=True)
            # Word explore buttons
            tw_btn_cols = st.columns(min(5, len(topic_words)))
            for wi, (tw_word, _) in enumerate(topic_words[:5]):
                with tw_btn_cols[wi]:
                    if st.button(tw_word, key=f"tw_{i}_{wi}", use_container_width=True):
                        navigate_to("Word Explorer", explore_word=tw_word)
                        st.rerun()

            # Which surahs belong to this topic
            topic_surahs = meta_df[meta_df["dominant_topic"] == i].sort_values("topic_confidence", ascending=False)
            if len(topic_surahs) > 0:
                st.markdown(f"**{SH(f'السور في هذا الموضوع ({len(topic_surahs)}):', f'Surahs in this topic ({len(topic_surahs)}):')}**")
                lang = st.session_state.lang
                if lang == "ar":
                    surah_list = " · ".join(r['surah_ar'] for _, r in topic_surahs.iterrows())
                elif lang == "en":
                    surah_list = ", ".join(r['surah_en'] for _, r in topic_surahs.iterrows())
                else:
                    surah_list = " · ".join(f"{r['surah_ar']} ({r['surah_en']})" for _, r in topic_surahs.iterrows())
                st.markdown(f"<div style='direction:rtl; font-family:Amiri; font-size:1.1rem; line-height:2;'>{surah_list}</div>",
                           unsafe_allow_html=True)

    # Topic distribution heatmap
    st.markdown("---")
    section_header("🗺️ توزيع المواضيع عبر السور", "🗺️ Topic Distribution Across Surahs")

    # Create heatmap data
    heat_df = pd.DataFrame(
        doc_topics,
        columns=[SH(f"موضوع {i+1}", f"Topic {i+1}") for i in range(n_topics)]
    )
    heat_df["Surah"] = meta_df["surah_ar"] + " (" + meta_df["surah_num"].astype(str) + ")"

    fig_heat = px.imshow(
        doc_topics.T,
        labels=dict(x=SH("رقم السورة", "Surah Number"), y=SH("الموضوع", "Topic"), color=SH("الوزن", "Weight")),
        x=meta_df["surah_num"].tolist(),
        y=[SH(f"موضوع {i+1}", f"Topic {i+1}") for i in range(n_topics)],
        color_continuous_scale=["#FAFDF7", "#2D6A4F", "#1B4332"],
        aspect="auto"
    )
    fig_heat.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, n_topics * 45),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Mecca vs Medina topic breakdown
    st.markdown("---")
    section_header("🗺️ المواضيع حسب فترة النزول", "🗺️ Topics by Revelation Period")

    mecca_topics = doc_topics[meta_df["place"] == "Mecca"].mean(axis=0)
    medina_topics = doc_topics[meta_df["place"] == "Medina"].mean(axis=0)

    _mecca_col = SH("مكة", "Mecca")
    _medina_col = SH("المدينة", "Medina")
    topic_place = pd.DataFrame({
        "Topic": [SH(f"الموضوع {i+1}", f"Topic {i+1}") for i in range(n_topics)],
        _mecca_col: mecca_topics,
        _medina_col: medina_topics,
    })

    fig_tp = go.Figure()
    fig_tp.add_trace(go.Bar(x=topic_place["Topic"], y=topic_place[_mecca_col],
                            name=_mecca_col, marker_color=COLORS["mecca"]))
    fig_tp.add_trace(go.Bar(x=topic_place["Topic"], y=topic_place[_medina_col],
                            name=_medina_col, marker_color=COLORS["medina"]))
    fig_tp.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=380, yaxis_title=SH("متوسط وزن الموضوع", "Avg Topic Weight"),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_tp, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('💡 كيف تقرأ هذا:', '💡 How to Read This:')}</strong><br>
        {SH(
            f'يكتشف نموذج LDA <strong>{n_topics} مواضيع كامنة</strong> — موضوعات مخفية تتكرر عبر السور. كل سورة هي <em>مزيج</em> من المواضيع. تُظهر الخريطة الحرارية أقوى المواضيع في كل سورة. قارن بين الأعمدة المكية والمدنية لرؤية تحول المواضيع بين فترات النزول.',
            f'LDA discovers <strong>{n_topics} latent topics</strong> — hidden themes that co-occur across surahs. Each surah is a <em>mixture</em> of topics (not assigned to just one). The heatmap shows which topics are strongest in each surah. Compare Meccan vs Medinan bars to see how themes shift between revelation periods.'
        )}
    </div>
    """, unsafe_allow_html=True)

    # Interactive: explore a topic
    st.markdown("---")
    section_header("🔎 استكشف موضوعاً", "🔎 Explore a Topic")

    _topic_options = [SH(f"موضوع {i+1}", f"Topic {i+1}") for i in range(n_topics)]
    sel_topic = st.selectbox(SH("اختر موضوعاً", "Select Topic"), _topic_options)
    topic_idx = _topic_options.index(sel_topic)

    # Show top surahs for this topic
    topic_col = doc_topics[:, topic_idx]
    meta_df["this_topic_weight"] = topic_col
    top_surahs = meta_df.nlargest(10, "this_topic_weight")

    # RTL horizontal bars
    top_surahs_sorted = top_surahs.sort_values("this_topic_weight", ascending=True)
    fig_ts = px.bar(top_surahs_sorted, x="this_topic_weight", y="surah_ar", orientation="h",
                    color="place",
                    color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                    text=top_surahs_sorted["this_topic_weight"].apply(lambda x: f"{x:.2f}"))
    fig_ts.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=380,
        yaxis=dict(tickfont=dict(size=14, family="Amiri"), side="right"),
        xaxis=dict(title=SH("وزن الموضوع", "Topic Weight"), side="top"),
        showlegend=True, legend=dict(orientation="h", y=-0.1)
    )
    fig_ts.update_traces(textposition="outside")
    st.plotly_chart(fig_ts, use_container_width=True)


# ---------------------------------------------------------------------------
# PAGE: ADVANCED ANALYSIS
# ---------------------------------------------------------------------------
elif page == "Advanced Analysis":
    if st.session_state.nav_history:
        if st.button(L('back'), key="aa_back"):
            go_back()
            st.rerun()

    page_title("📊 تحليل متقدم", "📊 Advanced Analysis", "تحليلات إحصائية ولغوية متقدمة", "Zipf's Law, N-grams, Clustering, Sentiment")

    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import AgglomerativeClustering
    from scipy.cluster.hierarchy import linkage, dendrogram as scipy_dendrogram
    from scipy.spatial.distance import pdist

    # --- Tab-based sub-sections ---
    adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5, adv_tab6 = st.tabs([
        SH("📈 قانون زيبف", "📈 Zipf's Law"),
        SH("🔗 سلاسل كلمات", "🔗 N-Grams"),
        SH("🗺️ تصنيف السور", "🗺️ Surah Clustering"),
        SH("💬 تحليل المشاعر", "💬 Sentiment Analysis"),
        SH("🎭 البصمة العاطفية", "🎭 Emotional Profiling"),
        SH("💡 استنتاجات البيانات", "💡 Data-Driven Insights"),
    ])

    # ------------------------------------------------------------------
    # TAB 1: ZIPF'S LAW
    # ------------------------------------------------------------------
    with adv_tab1:
        section_header("📈 قانون زيبف", "📈 Zipf's Law")
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('ما هو قانون زيبف؟', "What is Zipf's Law?")}</strong><br>
            {SH(
                'تخيّل أن الكلمات مثل الموظفين في شركة — كلمة واحدة (مثل "الله") تعمل أكثر من الكل، بينما آلاف الكلمات تظهر مرة واحدة فقط. قانون زيبف يقول إن هذا النمط موجود في كل اللغات الطبيعية. إذا اتبع القرآن هذا القانون، فنصه يتصرف مثل أي نص بشري طبيعي من الناحية الإحصائية.',
                "Imagine words are like employees in a company — one word (like 'Allah') does more work than everyone else, while thousands of words appear only once. Zipf's Law says this pattern exists in ALL natural languages. If the Quran follows this law, its text behaves like any natural human text statistically."
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def compute_zipf(_df):
            all_words = []
            for text in _df["arabic"]:
                all_words.extend(tokenize_arabic(text))
            freq = Counter(all_words)
            ranked = freq.most_common()
            ranks = list(range(1, len(ranked) + 1))
            freqs = [c for _, c in ranked]
            words = [w for w, _ in ranked]
            return ranks, freqs, words

        ranks, freqs, zipf_words = compute_zipf(df)

        # Log-log plot
        fig_zipf = go.Figure()
        fig_zipf.add_trace(go.Scatter(
            x=ranks[:500], y=freqs[:500], mode='markers',
            name=SH('الفعلي', 'Actual'),
            marker=dict(color=COLORS["secondary"], size=5, opacity=0.6),
            text=zipf_words[:500], hovertemplate="Rank: %{x}<br>Freq: %{y}<br>Word: %{text}"
        ))
        # Ideal Zipf line
        C = freqs[0]
        ideal = [C / r for r in ranks[:500]]
        fig_zipf.add_trace(go.Scatter(
            x=ranks[:500], y=ideal, mode='lines',
            name=SH("زيبف المثالي", "Ideal Zipf"),
            line=dict(color=COLORS["gold"], width=2, dash="dash")
        ))
        fig_zipf.update_layout(
            xaxis=dict(type="log", title=SH("الترتيب (لوغاريتمي)", "Rank (log)")),
            yaxis=dict(type="log", title=SH("التكرار (لوغاريتمي)", "Frequency (log)")),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=450, legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_zipf, use_container_width=True)

        # Vocabulary richness metrics
        section_header("📚 مقاييس ثراء المفردات", "📚 Vocabulary Richness")

        total_tokens = sum(freqs)
        unique_types = len(freqs)
        ttr = unique_types / total_tokens  # Type-Token Ratio
        hapax = sum(1 for f in freqs if f == 1)  # Words appearing once
        hapax_pct = hapax / unique_types * 100

        vc1, vc2, vc3, vc4 = st.columns(4)
        vc1.metric(SH("نسبة النوع", "Type-Token Ratio"), f"{ttr:.4f}")
        vc2.metric(SH("كلمات فريدة", "Hapax Legomena"), f"{hapax:,}")
        vc3.metric(SH("% كلمات تُستخدم مرة", "% Single-use Words"), f"{hapax_pct:.1f}%")
        vc4.metric(SH("حجم المفردات", "Vocabulary Size"), f"{unique_types:,}")

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة:', '💡 Finding:')}</strong><br>
            {SH(
                f'<strong>{hapax_pct:.1f}%</strong> من الكلمات الفريدة تظهر مرة واحدة فقط. هذه النسبة العالية تدل على مفردات غنية ومتنوعة — تتسق مع النص الأدبي.',
                f'<strong>{hapax_pct:.1f}%</strong> of unique words appear only once (hapax legomena). This high proportion indicates rich, diverse vocabulary — consistent with literary text. The Type-Token Ratio of <strong>{ttr:.4f}</strong> {"is typical for a large corpus" if ttr < 0.1 else "indicates moderate repetition"}.'
            )}
        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # TAB 2: N-GRAMS
    # ------------------------------------------------------------------
    with adv_tab2:
        section_header("🔗 تحليل سلاسل الكلمات", "🔗 N-Gram Analysis")

        ngram_size = st.radio(SH("حجم السلسلة", "N-Gram Size"), [2, 3, 4], horizontal=True, index=0)
        top_ngrams_n = st.slider(SH("العدد", "Number to show"), 10, 40, 20, key="ngram_slider")

        @st.cache_data
        def compute_ngrams(_df, n):
            all_ngrams = []
            for text in _df["arabic"]:
                words = tokenize_arabic(text)
                for i in range(len(words) - n + 1):
                    ngram = " ".join(words[i:i+n])
                    all_ngrams.append(ngram)
            return Counter(all_ngrams)

        ngram_freq = compute_ngrams(df, ngram_size)
        top_ng = ngram_freq.most_common(top_ngrams_n)
        ng_df = pd.DataFrame(top_ng, columns=["ngram", "count"])

        fig_ng = px.bar(ng_df.iloc[::-1], x="count", y="ngram", orientation="h",
                       color="count", color_continuous_scale=["#D8F3DC", "#1B4332"],
                       text="count")
        fig_ng.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=max(400, top_ngrams_n * 28),
            yaxis=dict(tickfont=dict(size=14, family="Amiri")),
            coloraxis_showscale=False,
            xaxis_title=SH("التكرار", "Frequency"), yaxis_title=""
        )
        fig_ng.update_traces(textposition="outside")
        st.plotly_chart(fig_ng, use_container_width=True)

        # Clickable ngram words
        st.markdown(f"**{SH('🔬 اضغط لاستكشاف أي كلمة من أكثر السلاسل تكراراً:', '🔬 Click to explore any word from the top N-grams:')}**")
        ngram_words_set = set()
        for ng, _ in top_ng[:10]:
            for w in ng.split():
                ngram_words_set.add(w)
        ng_btn_cols = st.columns(min(6, len(ngram_words_set)))
        for i, w in enumerate(list(ngram_words_set)[:6]):
            with ng_btn_cols[i]:
                if st.button(w, key=f"ng_w_{i}", use_container_width=True):
                    navigate_to("Word Explorer", explore_word=w)
                    st.rerun()

        # Mecca vs Medina N-gram comparison
        st.markdown("---")
        section_header("⚖️ مقارنة N-Grams: مكة مقابل المدينة", "⚖️ N-Gram Comparison: Mecca vs Medina")

        mecca_ng = compute_ngrams(df[df["place"] == "Mecca"], ngram_size)
        medina_ng = compute_ngrams(df[df["place"] == "Medina"], ngram_size)

        col_ng1, col_ng2 = st.columns(2)
        with col_ng1:
            st.markdown(f"**{SH('🔴 مكة', '🔴 Mecca')}**")
            mng_df = pd.DataFrame(mecca_ng.most_common(10), columns=[SH("سلسلة كلمات", "N-Gram"), SH("العدد", "Count")])
            mng_df.index = range(1, 11)
            st.dataframe(mng_df, use_container_width=True)
        with col_ng2:
            st.markdown(f"**{SH('🔵 المدينة', '🔵 Medina')}**")
            dng_df = pd.DataFrame(medina_ng.most_common(10), columns=[SH("سلسلة كلمات", "N-Gram"), SH("العدد", "Count")])
            dng_df.index = range(1, 11)
            st.dataframe(dng_df, use_container_width=True)

    # ------------------------------------------------------------------
    # TAB 3: SURAH CLUSTERING
    # ------------------------------------------------------------------
    with adv_tab3:
        section_header("🗺️ تصنيف السور", "🗺️ Surah Clustering")
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('الفكرة:', 'The Idea:')}</strong><br>
            {SH(
                'تخيّل أنك وضعت 114 سورة على طاولة كبيرة وطلبت من شخص لا يعرف العربية أن يجمع المتشابهة منها — بناءً على الكلمات المستخدمة فقط. هذا بالضبط ما يفعله الكمبيوتر هنا. السور التي تستخدم كلمات متشابهة تُوضع في نفس المجموعة. كل نقطة في الرسم تمثل سورة — السور القريبة من بعضها تتشابه في مفرداتها.',
                "Imagine placing all 114 surahs on a big table and asking someone who doesn't know Arabic to group similar ones together — based only on the words used. That's exactly what the computer does here. Surahs using similar words get grouped together. Each dot on the chart represents a surah — surahs close together share similar vocabulary."
            )}
        </div>
        """, unsafe_allow_html=True)

        n_clusters = st.slider(SH("عدد المجموعات", "Number of Clusters"), 3, 15, 6, key="cluster_slider")

        @st.cache_data
        def cluster_surahs(_df, n_clust):
            surah_texts = []
            surah_labels = []
            surah_places = []
            for sn in sorted(_df["surah_num"].unique()):
                sdf = _df[_df["surah_num"] == sn]
                words = []
                for text in sdf["arabic"]:
                    words.extend(tokenize_arabic(text))
                surah_texts.append(" ".join(words))
                surah_labels.append(f"{sdf.iloc[0]['surah_name_ar']} ({sn})")
                surah_places.append(sdf.iloc[0]["place"])

            tfidf = TfidfVectorizer(max_features=2000)
            tfidf_matrix = tfidf.fit_transform(surah_texts)

            # Hierarchical clustering
            clustering = AgglomerativeClustering(n_clusters=n_clust)
            labels = clustering.fit_predict(tfidf_matrix.toarray())

            # Compute linkage for dendrogram
            dist_matrix = pdist(tfidf_matrix.toarray(), metric='cosine')
            Z = linkage(dist_matrix, method='ward')

            return labels, surah_labels, surah_places, Z, tfidf_matrix

        cluster_labels, s_labels, s_places, Z_link, tfidf_mat = cluster_surahs(df, n_clusters)

        # Scatter plot using first 2 components
        from sklearn.decomposition import TruncatedSVD
        svd = TruncatedSVD(n_components=2, random_state=42)
        coords = svd.fit_transform(tfidf_mat)

        clust_df = pd.DataFrame({
            "x": coords[:, 0], "y": coords[:, 1],
            "surah": s_labels, "cluster": [f"Cluster {c+1}" for c in cluster_labels],
            "place": s_places
        })

        fig_clust = px.scatter(
            clust_df, x="x", y="y", color="cluster",
            symbol="place", hover_data={"surah": True, "x": False, "y": False},
            color_discrete_sequence=PALETTE[:n_clusters],
            labels={"x": SH("المكون الأول", "Component 1"), "y": SH("المكون الثاني", "Component 2")}
        )
        fig_clust.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=500,
            legend=dict(font=dict(size=11)),
        )
        fig_clust.update_traces(marker=dict(size=10, line=dict(width=1, color="white")))
        st.plotly_chart(fig_clust, use_container_width=True)

        # Cluster summary
        section_header("📋 تفاصيل المجموعات", "📋 Cluster Details")

        for c in range(n_clusters):
            mask = [i for i, l in enumerate(cluster_labels) if l == c]
            cluster_surahs_list = [s_labels[i] for i in mask]
            cluster_places = [s_places[i] for i in mask]
            mecca_count = sum(1 for p in cluster_places if p == "Mecca")
            medina_count = sum(1 for p in cluster_places if p == "Medina")

            _cluster_label = SH(
                f"🏷️ المجموعة {c+1}: {len(mask)} سورة (🔴 {mecca_count} مكية، 🔵 {medina_count} مدنية)",
                f"🏷️ Cluster {c+1}: {len(mask)} surahs (🔴 {mecca_count} Meccan, 🔵 {medina_count} Medinan)"
            )
            with st.expander(_cluster_label, expanded=(c < 2)):
                st.markdown(
                    f"<div style='direction:rtl; font-family:Amiri; font-size:1.1rem; line-height:2;'>"
                    f"{' · '.join(cluster_surahs_list)}</div>",
                    unsafe_allow_html=True
                )

    # ------------------------------------------------------------------
    # TAB 4: SENTIMENT ANALYSIS
    # ------------------------------------------------------------------
    with adv_tab4:
        section_header("💬 تحليل المشاعر", "💬 Sentiment Analysis")
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('المنهجية:', 'Methodology:')}</strong><br>
            {SH(
                'يتم تحليل المشاعر على <strong>الترجمات الإنجليزية</strong> باستخدام قواميس لاهوتية متخصصة لالتقاط النبرة العاطفية: الرحمة، التحذير، الأمل، الخوف، الهداية.',
                'Sentiment analysis is performed on <strong>English translations</strong> using a keyword-based approach with curated theological lexicons. This captures the emotional tone: mercy, warning, hope, fear, guidance, etc.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Theological sentiment lexicons
        MERCY_WORDS = {'mercy', 'merciful', 'compassion', 'compassionate', 'forgive', 'forgiveness',
                       'forgiving', 'gracious', 'grace', 'kind', 'kindness', 'gentle', 'love',
                       'loving', 'pardon', 'bless', 'blessed', 'blessing', 'peace', 'peaceful'}
        WARNING_WORDS = {'punishment', 'punish', 'fire', 'hell', 'wrath', 'torment', 'doom',
                         'curse', 'cursed', 'destroy', 'destruction', 'perish', 'severe',
                         'painful', 'burn', 'burning', 'woe', 'terrible', 'dreadful'}
        GUIDANCE_WORDS = {'guide', 'guidance', 'path', 'straight', 'right', 'truth', 'true',
                          'wisdom', 'wise', 'knowledge', 'know', 'light', 'clear', 'sign',
                          'signs', 'evidence', 'proof', 'revelation', 'revealed'}
        HOPE_WORDS = {'paradise', 'garden', 'gardens', 'reward', 'rewarded', 'success',
                      'successful', 'prosper', 'joy', 'glad', 'tidings', 'promise',
                      'promised', 'eternal', 'everlasting', 'triumph', 'good'}

        @st.cache_data
        def sentiment_analysis(_df):
            results = []
            for _, row in _df.iterrows():
                words_en = set(re.findall(r'[a-zA-Z]+', row["english"].lower()))
                results.append({
                    "surah_num": row["surah_num"],
                    "surah_ar": row["surah_name_ar"],
                    "surah_en": row["surah_name_en"],
                    "verse_key": row["verse_key"],
                    "place": row["place"],
                    "mercy": len(words_en & MERCY_WORDS),
                    "warning": len(words_en & WARNING_WORDS),
                    "guidance": len(words_en & GUIDANCE_WORDS),
                    "hope": len(words_en & HOPE_WORDS),
                })
            return pd.DataFrame(results)

        sent_df = sentiment_analysis(df)

        # Overall sentiment distribution
        _mercy_label = SH("رحمة", "Mercy")
        _warning_label = SH("تحذير", "Warning")
        _guidance_label = SH("هداية", "Guidance")
        _hope_label = SH("أمل", "Hope")
        totals = {
            _mercy_label: sent_df["mercy"].sum(),
            _warning_label: sent_df["warning"].sum(),
            _guidance_label: sent_df["guidance"].sum(),
            _hope_label: sent_df["hope"].sum(),
        }
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric(_mercy_label, f"{totals[_mercy_label]:,}")
        sc2.metric(_warning_label, f"{totals[_warning_label]:,}")
        sc3.metric(_guidance_label, f"{totals[_guidance_label]:,}")
        sc4.metric(_hope_label, f"{totals[_hope_label]:,}")

        # Clickable sentiment categories
        sent_btn_cols = st.columns(4)
        _sent_search_words = {0: "mercy", 1: "punishment", 2: "guide", 3: "paradise"}
        for si, (sk, sv) in enumerate(_sent_search_words.items()):
            with sent_btn_cols[si]:
                if st.button(SH(f"🔍 استكشف", f"🔍 Explore"), key=f"sent_explore_{si}", use_container_width=True):
                    navigate_to("Search", search_query=sv)
                    st.rerun()

        # Pie chart
        sent_pie = pd.DataFrame(list(totals.items()), columns=[SH("الموضوع", "Theme"), SH("العدد", "Count")])
        fig_sp = px.pie(sent_pie, values=SH("العدد", "Count"), names=SH("الموضوع", "Theme"),
                       color_discrete_sequence=["#52B788", "#B7094C", "#D4A574", "#0091AD"],
                       hole=0.4)
        fig_sp.update_traces(textinfo="percent+label", textfont_size=13)
        fig_sp.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                            height=350, showlegend=False)
        st.plotly_chart(fig_sp, use_container_width=True)

        # Sentiment by surah
        st.markdown("---")
        section_header("📈 المشاعر حسب السورة", "📈 Sentiment by Surah")

        surah_sent = sent_df.groupby(["surah_num", "surah_ar", "place"]).agg({
            "mercy": "sum", "warning": "sum", "guidance": "sum", "hope": "sum"
        }).reset_index()

        fig_sent = go.Figure()
        fig_sent.add_trace(go.Bar(x=surah_sent["surah_num"], y=surah_sent["mercy"],
                                  name=_mercy_label, marker_color="#52B788"))
        fig_sent.add_trace(go.Bar(x=surah_sent["surah_num"], y=surah_sent["warning"],
                                  name=_warning_label, marker_color="#B7094C"))
        fig_sent.add_trace(go.Bar(x=surah_sent["surah_num"], y=surah_sent["guidance"],
                                  name=_guidance_label, marker_color="#D4A574"))
        fig_sent.add_trace(go.Bar(x=surah_sent["surah_num"], y=surah_sent["hope"],
                                  name=_hope_label, marker_color="#0091AD"))
        fig_sent.update_layout(
            barmode="stack", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=450, xaxis_title=SH("رقم السورة", "Surah Number"),
            yaxis_title=SH("عدد الكلمات", "Word Count"),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        # Mecca vs Medina sentiment comparison
        st.markdown("---")
        section_header("⚖️ مقارنة المشاعر: مكة مقابل المدينة", "⚖️ Sentiment Comparison: Mecca vs Medina")

        mecca_sent = sent_df[sent_df["place"] == "Mecca"][["mercy", "warning", "guidance", "hope"]].sum()
        medina_sent = sent_df[sent_df["place"] == "Medina"][["mercy", "warning", "guidance", "hope"]].sum()

        # Normalize to percentages
        mecca_pcts = mecca_sent / mecca_sent.sum() * 100
        medina_pcts = medina_sent / medina_sent.sum() * 100

        _theme_col = SH("الموضوع", "Theme")
        _mecca_pct_col = SH("مكة %", "Mecca %")
        _medina_pct_col = SH("المدينة %", "Medina %")
        comp_sent = pd.DataFrame({
            _theme_col: [_mercy_label, _warning_label, _guidance_label, _hope_label],
            _mecca_pct_col: [mecca_pcts["mercy"], mecca_pcts["warning"], mecca_pcts["guidance"], mecca_pcts["hope"]],
            _medina_pct_col: [medina_pcts["mercy"], medina_pcts["warning"], medina_pcts["guidance"], medina_pcts["hope"]],
        })

        fig_cs = go.Figure()
        fig_cs.add_trace(go.Bar(x=comp_sent[_theme_col], y=comp_sent[_mecca_pct_col],
                                name=SH("🔴 مكة", "🔴 Mecca"), marker_color=COLORS["mecca"]))
        fig_cs.add_trace(go.Bar(x=comp_sent[_theme_col], y=comp_sent[_medina_pct_col],
                                name=SH("🔵 المدينة", "🔵 Medina"), marker_color=COLORS["medina"]))
        fig_cs.update_layout(
            barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400, yaxis_title=SH("% من كلمات الموضوع", "% of Theme Words"),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_cs, use_container_width=True)

        mercy_dominant = "Mecca" if mecca_pcts["mercy"] > medina_pcts["mercy"] else "Medina"
        warning_dominant = "Mecca" if mecca_pcts["warning"] > medina_pcts["warning"] else "Medina"
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة المشاعر:', '💡 Sentiment Finding:')}</strong><br>
            {SH(
                f'لغة الرحمة أقوى نسبياً في السور <strong>{"المكية" if mercy_dominant == "Mecca" else "المدنية"}</strong>، بينما لغة التحذير أقوى في السور <strong>{"المكية" if warning_dominant == "Mecca" else "المدنية"}</strong>.',
                f'Mercy-related language is proportionally stronger in <strong>{mercy_dominant}</strong> surahs, while warning language is stronger in <strong>{warning_dominant}</strong> surahs. This aligns with the scholarly understanding that Meccan surahs emphasize divine attributes and eschatological warnings, while Medinan surahs focus more on community guidance.'
            )}
        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # TAB 5: EMOTIONAL PROFILING
    # ------------------------------------------------------------------
    with adv_tab5:
        section_header("🎭 البصمة العاطفية للقرآن", "🎭 Emotional Profiling of the Quran")

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('المنهجية:', 'Methodology:')}</strong><br>
            {SH(
                'نحلل الترجمة الإنجليزية باستخدام 8 قواميس عاطفية متخصصة لرسم البصمة العاطفية لكل سورة. '
                'هذا يشبه تحليل مشاعر العملاء — لكن مطبّق على النص الديني.',
                'We analyse English translations using 8 specialised emotional lexicons to map the emotional '
                'fingerprint of each surah. Think customer sentiment analysis — applied to scripture.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Expanded 8-dimension emotional lexicon
        # FIXED: Use stable English keys internally, translate only for display
        _EMOTION_DATA = {
            "Mercy":     {'mercy', 'merciful', 'compassion', 'compassionate', 'forgive', 'forgiveness',
                          'forgiving', 'gracious', 'grace', 'kind', 'kindness', 'gentle', 'pardon', 'bless', 'blessed'},
            "Fear":      {'fear', 'afraid', 'terror', 'terrify', 'dread', 'tremble', 'horror',
                          'frightened', 'alarmed', 'panic', 'awe', 'fearful', 'scared'},
            "Hope":      {'paradise', 'garden', 'gardens', 'reward', 'rewarded', 'success', 'glad',
                          'tidings', 'promise', 'promised', 'eternal', 'everlasting', 'triumph', 'prosper', 'joy'},
            "Justice":   {'justice', 'just', 'judge', 'judgment', 'fair', 'equitable', 'rights',
                          'balance', 'measure', 'weight', 'decree', 'ordained', 'lawful', 'unlawful', 'rule'},
            "Love":      {'love', 'loves', 'loving', 'beloved', 'affection', 'devotion', 'devoted',
                          'cherish', 'tender', 'intimate', 'near', 'close', 'friend', 'friendship', 'care'},
            "Warning":   {'punishment', 'punish', 'fire', 'hell', 'wrath', 'torment', 'doom',
                          'curse', 'destroy', 'destruction', 'perish', 'severe', 'painful', 'burn', 'woe'},
            "Guidance":  {'guide', 'guidance', 'path', 'straight', 'right', 'truth', 'true',
                          'wisdom', 'wise', 'knowledge', 'light', 'clear', 'sign', 'signs', 'revelation'},
            "Narrative": {'said', 'went', 'came', 'told', 'people', 'sent', 'moses',
                          'abraham', 'noah', 'pharaoh', 'children', 'story', 'before', 'after', 'town'},
        }
        _EMOTION_AR = {"Mercy": "رحمة", "Fear": "خوف", "Hope": "أمل", "Justice": "عدالة",
                       "Love": "حب", "Warning": "تحذير", "Guidance": "هداية", "Narrative": "سرد قصصي"}
        _EMO_KEYS = list(_EMOTION_DATA.keys())  # stable English keys for DataFrame
        # Display names for charts (language-aware)
        _emo_display = [SH(_EMOTION_AR[k], k) for k in _EMO_KEYS]

        @st.cache_data
        def emotional_profiling(_df):
            results = []
            for _, row in _df.iterrows():
                words_en = set(re.findall(r'[a-zA-Z]+', row["english"].lower()))
                scores = {}
                for emo_key, lexicon in _EMOTION_DATA.items():
                    scores[emo_key] = len(words_en & lexicon)
                scores["surah_num"] = row["surah_num"]
                scores["surah_ar"] = row["surah_name_ar"]
                scores["place"] = row["place"]
                results.append(scores)
            return pd.DataFrame(results)

        emo_df = emotional_profiling(df)
        emotion_names = _EMO_KEYS  # stable keys for DataFrame access

        # Radar chart: Mecca vs Medina emotional profile
        section_header("📊 مقارنة البصمة العاطفية: مكة مقابل المدينة",
                      "📊 Emotional Fingerprint: Mecca vs Medina")

        mecca_emo = emo_df[emo_df["place"] == "Mecca"][_EMO_KEYS].sum()
        medina_emo = emo_df[emo_df["place"] == "Medina"][_EMO_KEYS].sum()

        # Normalize to percentages for fair comparison
        mecca_pct = (mecca_emo / mecca_emo.sum() * 100).values
        medina_pct = (medina_emo / medina_emo.sum() * 100).values

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=list(mecca_pct) + [mecca_pct[0]],
            theta=_emo_display + [_emo_display[0]],
            fill='toself', name=SH("مكة", "Mecca"),
            line=dict(color=COLORS["mecca"]),
            fillcolor='rgba(183,9,76,0.15)'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=list(medina_pct) + [medina_pct[0]],
            theta=_emo_display + [_emo_display[0]],
            fill='toself', name=SH("المدينة", "Medina"),
            line=dict(color=COLORS["medina"]),
            fillcolor='rgba(0,145,173,0.15)'
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, max(max(mecca_pct), max(medina_pct)) * 1.1]),
                angularaxis=dict(tickfont=dict(size=14, family="Amiri"))
            ),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=500, showlegend=True,
            legend=dict(orientation="h", y=-0.1, font=dict(size=14))
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Per-surah emotion heatmap
        section_header("🌡️ الخريطة الحرارية العاطفية لكل سورة", "🌡️ Emotion Heatmap by Surah")

        surah_emo = emo_df.groupby(["surah_num", "surah_ar"])[_EMO_KEYS].sum().reset_index()
        # Normalize each surah's row to percentages
        emo_matrix = surah_emo[_EMO_KEYS].values
        row_sums = emo_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        emo_pct_matrix = emo_matrix / row_sums * 100

        fig_emo_heat = px.imshow(
            emo_pct_matrix.T,
            x=surah_emo["surah_num"].tolist(),
            y=_emo_display,
            labels=dict(x=SH("رقم السورة", "Surah Number"), y=SH("العاطفة", "Emotion"),
                       color=SH("النسبة %", "% Share")),
            color_continuous_scale=["#FAFDF7", "#D4A574", "#B7094C"],
            aspect="auto"
        )
        fig_emo_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=350,
            yaxis=dict(tickfont=dict(size=13, family="Amiri")),
        )
        st.plotly_chart(fig_emo_heat, use_container_width=True)

        # Top 5 surahs for each emotion
        section_header("🏆 أقوى السور في كل عاطفة", "🏆 Top Surahs per Emotion")

        # Map display names back to data keys
        _display_to_key = dict(zip(_emo_display, _EMO_KEYS))
        sel_emotion_display = st.selectbox(SH("اختر عاطفة", "Select Emotion"), _emo_display)
        sel_emotion = _display_to_key[sel_emotion_display]
        top5_emo = surah_emo.nlargest(10, sel_emotion)[["surah_ar", sel_emotion]].reset_index(drop=True)

        make_rtl_bar_chart(top5_emo, "surah_ar", sel_emotion,
                           color_scale=["#D4A574", "#B7094C"],
                           height=350)

        # Show sample verses for selected emotion
        st.markdown("---")
        section_header("📖 آيات تحتوي هذه العاطفة", "📖 Verses Containing This Emotion")

        # Get verses for the top surah of selected emotion
        top_surah_name = top5_emo.iloc[0]["surah_ar"] if len(top5_emo) > 0 else None
        if top_surah_name:
            top_sn = surah_emo[surah_emo["surah_ar"] == top_surah_name]["surah_num"].values
            if len(top_sn) > 0:
                sample_emo_verses = df[df["surah_num"] == top_sn[0]].head(5)
                for _, ev in sample_emo_verses.iterrows():
                    st.markdown(f"""
                    <div class="verse-card">
                        <strong style='color:#2D6A4F;'>{ev['verse_key']} — {ev['surah_name_ar']}</strong>
                        <div class="arabic-text">{ev['arabic']}</div>
                        <div style='color:#555; padding:5px 15px; font-style:italic;'>{ev['english']}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # TAB 6: DATA-DRIVEN INSIGHTS
    # ------------------------------------------------------------------
    with adv_tab6:
        section_header("💡 استنتاجات مبنية على البيانات", "💡 Data-Driven Insights")

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('المبدأ:', 'Principle:')}</strong><br>
            {SH(
                'هذه الصفحة تقدم استنتاجات إحصائية بحتة من البيانات — ليست تفسيرات دينية. '
                'نسأل: "ماذا تقول الأرقام عن النص؟" — كما تحلل بيانات العملاء، نحلل النص.',
                'This page presents purely statistical findings from the data — not theological interpretations. '
                'We ask: "What does the data say about the text?" — like analysing customer data, we analyse text.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Auto-compute insights
        @st.cache_data
        def compute_insights(_df):
            insights = []

            # 1. Word frequency insight
            all_words = []
            for text in _df["arabic"]:
                all_words.extend(tokenize_arabic(text))
            freq = Counter(all_words)
            top_word, top_count = freq.most_common(1)[0]
            total = sum(freq.values())
            insights.append({
                "icon": "📊",
                "ar": f'الكلمة الأكثر تكراراً هي "{top_word}" — تظهر {top_count:,} مرة ({top_count/total*100:.1f}% من كل الكلمات)',
                "en": f'The most frequent word is "{top_word}" — appearing {top_count:,} times ({top_count/total*100:.1f}% of all words)',
                "category_ar": "تكرار الكلمات",
                "category_en": "Word Frequency",
            })

            # 2. Verse length comparison
            _df_copy = _df.copy()
            _df_copy["wc"] = _df_copy["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))
            mecca_avg = _df_copy[_df_copy["place"] == "Mecca"]["wc"].mean()
            medina_avg = _df_copy[_df_copy["place"] == "Medina"]["wc"].mean()
            ratio = medina_avg / mecca_avg
            insights.append({
                "icon": "📏",
                "ar": f'الآيات المدنية أطول بمعدل {ratio:.1f}x من المكية ({medina_avg:.1f} مقابل {mecca_avg:.1f} كلمة/آية). يعكس التحول من الإعلانات القصيرة إلى التشريعات التفصيلية.',
                "en": f'Medinan verses are {ratio:.1f}x longer than Meccan ({medina_avg:.1f} vs {mecca_avg:.1f} words/verse). This reflects the shift from short proclamations to detailed legislation.',
                "category_ar": "بنية الآيات",
                "category_en": "Verse Structure",
            })

            # 3. Vocabulary richness
            unique = len(freq)
            hapax = sum(1 for f_val in freq.values() if f_val == 1)
            insights.append({
                "icon": "📚",
                "ar": f'القرآن يحتوي على {unique:,} كلمة فريدة. منها {hapax:,} ({hapax/unique*100:.0f}%) تظهر مرة واحدة فقط — مما يدل على ثراء لغوي استثنائي.',
                "en": f'The Quran contains {unique:,} unique words. Of these, {hapax:,} ({hapax/unique*100:.0f}%) appear only once — indicating exceptional linguistic richness.',
                "category_ar": "ثراء المفردات",
                "category_en": "Vocabulary Richness",
            })

            # 4. Emotional tone
            mercy_words = {'mercy', 'merciful', 'compassion', 'forgive', 'forgiveness', 'gracious', 'grace', 'kind', 'pardon', 'bless'}
            warning_words = {'punishment', 'punish', 'fire', 'hell', 'wrath', 'torment', 'doom', 'destroy', 'severe', 'painful'}
            mercy_count = sum(1 for _, r in _df.iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in mercy_words)
            warning_count = sum(1 for _, r in _df.iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in warning_words)
            mercy_ratio = mercy_count / (mercy_count + warning_count) * 100 if (mercy_count + warning_count) > 0 else 50
            insights.append({
                "icon": "💬",
                "ar": f'لغة الرحمة تفوق لغة التحذير بنسبة {mercy_ratio:.0f}% مقابل {100-mercy_ratio:.0f}%. البيانات تُظهر أن النبرة الغالبة هي الرحمة والمغفرة.',
                "en": f'Mercy language outweighs warning language {mercy_ratio:.0f}% vs {100-mercy_ratio:.0f}%. The data shows the dominant tone is compassion and forgiveness.',
                "category_ar": "النبرة العاطفية",
                "category_en": "Emotional Tone",
            })

            # 5. Surah length distribution
            surah_counts = _df.groupby("surah_num").size()
            median_len = surah_counts.median()
            longest = _df.groupby(["surah_num", "surah_name_ar"]).size().reset_index(name="count").nlargest(1, "count")
            shortest_count = surah_counts.min()
            insights.append({
                "icon": "📐",
                "ar": f'متوسط طول السورة {median_len:.0f} آية، لكن التباين ضخم — أطول سورة ({longest.iloc[0]["surah_name_ar"]}) تحتوي {longest.iloc[0]["count"]} آية بينما أقصرها {shortest_count} آيات فقط.',
                "en": f'Median surah length is {median_len:.0f} verses, but variation is huge — longest ({longest.iloc[0]["surah_name_ar"]}) has {longest.iloc[0]["count"]} verses while shortest has just {shortest_count}.',
                "category_ar": "توزيع السور",
                "category_en": "Surah Distribution",
            })

            # 6. Arabic vs English word ratio
            ar_total = _df["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x))).sum()
            en_total = _df["english"].apply(lambda x: len(x.split())).sum()
            ratio_ae = en_total / ar_total
            insights.append({
                "icon": "🌐",
                "ar": f'كل كلمة عربية تحتاج {ratio_ae:.1f} كلمة إنجليزية في المتوسط للترجمة. هذا يعكس كثافة اللغة العربية الصرفية.',
                "en": f'Each Arabic word requires {ratio_ae:.1f} English words on average to translate. This reflects the morphological density of Arabic.',
                "category_ar": "كثافة اللغة",
                "category_en": "Language Density",
            })

            # 7. Guidance vs Law — thematic shift
            guidance_w = {'guide', 'guidance', 'path', 'straight', 'truth', 'light', 'sign', 'signs', 'wisdom'}
            law_w = {'lawful', 'unlawful', 'forbidden', 'permitted', 'ordained', 'decree', 'obligatory', 'inherit', 'inheritance', 'dowry', 'contract', 'witness', 'oath'}
            mecca_guide = sum(1 for _, r in _df[_df["place"]=="Mecca"].iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in guidance_w)
            medina_law = sum(1 for _, r in _df[_df["place"]=="Medina"].iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in law_w)
            medina_guide = sum(1 for _, r in _df[_df["place"]=="Medina"].iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in guidance_w)
            mecca_law = sum(1 for _, r in _df[_df["place"]=="Mecca"].iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in law_w)
            insights.append({
                "icon": "⚖️",
                "ar": f'السور المكية تركز على الهداية ({mecca_guide} إشارة) أكثر من التشريع ({mecca_law}). السور المدنية تزيد فيها لغة التشريع ({medina_law}) مع الحفاظ على الهداية ({medina_guide}). تحول واضح من "لماذا نؤمن" إلى "كيف نعيش".',
                "en": f'Meccan surahs focus on guidance ({mecca_guide} references) over legislation ({mecca_law}). Medinan surahs increase legal language ({medina_law}) while maintaining guidance ({medina_guide}). A clear shift from "why believe" to "how to live".',
                "category_ar": "الهداية مقابل التشريع",
                "category_en": "Guidance vs Legislation",
            })

            # 8. Narrative density — prophets and stories
            prophet_names = {'moses', 'abraham', 'noah', 'jesus', 'david', 'solomon', 'joseph', 'adam', 'pharaoh', 'mary', 'lot', 'aaron', 'jacob', 'ishmael', 'isaac', 'jonah', 'elijah'}
            prophet_count = sum(1 for _, r in _df.iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in prophet_names)
            top_prophet = Counter(w for _, r in _df.iterrows() for w in re.findall(r'[a-zA-Z]+', r["english"].lower()) if w in prophet_names).most_common(3)
            top3_str_ar = "، ".join(f"{w} ({c})" for w, c in top_prophet)
            top3_str_en = ", ".join(f"{w} ({c})" for w, c in top_prophet)
            insights.append({
                "icon": "📖",
                "ar": f'أسماء الأنبياء تظهر في {prophet_count:,} موضع. الأكثر ذكراً: {top3_str_ar}. القصص النبوي يشكّل ركيزة رئيسية في البناء القرآني.',
                "en": f'Prophet names appear in {prophet_count:,} locations. Most mentioned: {top3_str_en}. Prophetic narrative forms a major structural pillar of the Quran.',
                "category_ar": "السرد القصصي",
                "category_en": "Narrative Density",
            })

            # 9. Question rhetorical device
            q_count = sum(1 for _, r in _df.iterrows() if '?' in r["english"])
            q_pct = q_count / len(_df) * 100
            mecca_q = sum(1 for _, r in _df[_df["place"]=="Mecca"].iterrows() if '?' in r["english"])
            medina_q = sum(1 for _, r in _df[_df["place"]=="Medina"].iterrows() if '?' in r["english"])
            insights.append({
                "icon": "❓",
                "ar": f'{q_count:,} آية ({q_pct:.1f}%) تحتوي على سؤال. السور المكية تحتوي {mecca_q:,} سؤال مقابل {medina_q:,} في المدنية. الأسلوب الاستفهامي أداة إقناع رئيسية في الخطاب المكي.',
                "en": f'{q_count:,} verses ({q_pct:.1f}%) contain a question. Meccan surahs have {mecca_q:,} questions vs {medina_q:,} Medinan. Rhetorical questioning is a major persuasion tool in Meccan discourse.',
                "category_ar": "الأسلوب البلاغي",
                "category_en": "Rhetorical Style",
            })

            # 10. Repetition patterns (most repeated phrases)
            bigrams = Counter()
            for _, r in _df.iterrows():
                words = tokenize_arabic(r["arabic"])
                for i in range(len(words) - 1):
                    bigrams[f"{words[i]} {words[i+1]}"] += 1
            top_bigram, bg_count = bigrams.most_common(1)[0]
            insights.append({
                "icon": "🔁",
                "ar": f'أكثر زوج كلمات تكراراً هو "{top_bigram}" — يظهر {bg_count} مرة. التكرار في القرآن ليس عشوائياً بل يخدم التأكيد والإيقاع.',
                "en": f'The most repeated word pair is "{top_bigram}" — appearing {bg_count} times. Repetition in the Quran is not random but serves emphasis and rhythm.',
                "category_ar": "أنماط التكرار",
                "category_en": "Repetition Patterns",
            })

            # 11. Verse complexity spectrum
            _df_copy2 = _df.copy()
            _df_copy2["wc"] = _df_copy2["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))
            short_verses = len(_df_copy2[_df_copy2["wc"] <= 5])
            long_verses = len(_df_copy2[_df_copy2["wc"] >= 30])
            short_pct = short_verses / len(_df) * 100
            long_pct = long_verses / len(_df) * 100
            insights.append({
                "icon": "📊",
                "ar": f'{short_pct:.1f}% من الآيات قصيرة (5 كلمات أو أقل) و{long_pct:.1f}% طويلة (30+ كلمة). هذا التباين يخلق إيقاعاً ديناميكياً — آيات قصيرة مؤثرة تليها آيات تفصيلية.',
                "en": f'{short_pct:.1f}% of verses are short (5 words or less) and {long_pct:.1f}% are long (30+ words). This variation creates a dynamic rhythm — impactful short verses followed by detailed ones.',
                "category_ar": "طيف التعقيد",
                "category_en": "Complexity Spectrum",
            })

            # 12. Temporal themes — afterlife vs worldly
            afterlife_w = {'paradise', 'hell', 'hereafter', 'resurrection', 'judgment', 'eternal', 'immortal', 'garden', 'fire', 'doom', 'angels', 'trumpet'}
            worldly_w = {'trade', 'wealth', 'money', 'house', 'family', 'marriage', 'food', 'drink', 'land', 'earth', 'sea', 'mountain', 'rain'}
            afterlife_c = sum(1 for _, r in _df.iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in afterlife_w)
            worldly_c = sum(1 for _, r in _df.iterrows() for w in set(re.findall(r'[a-zA-Z]+', r["english"].lower())) if w in worldly_w)
            ratio_aw = afterlife_c / worldly_c if worldly_c > 0 else 0
            insights.append({
                "icon": "⏳",
                "ar": f'مفردات الآخرة ({afterlife_c:,} إشارة) تفوق مفردات الدنيا ({worldly_c:,}) بنسبة {ratio_aw:.1f}x. النص يركز على المنظور الأخروي كإطار لفهم الحياة الدنيوية.',
                "en": f'Afterlife vocabulary ({afterlife_c:,} references) outweighs worldly vocabulary ({worldly_c:,}) by {ratio_aw:.1f}x. The text frames worldly life through an eschatological lens.',
                "category_ar": "الآخرة مقابل الدنيا",
                "category_en": "Afterlife vs Worldly",
            })

            # 13. Divine attributes focus
            divine_attr = {'merciful', 'gracious', 'mighty', 'wise', 'knowing', 'forgiving', 'seeing', 'hearing', 'powerful', 'great', 'exalted', 'supreme'}
            attr_counts = Counter(w for _, r in _df.iterrows() for w in re.findall(r'[a-zA-Z]+', r["english"].lower()) if w in divine_attr)
            top_attr = attr_counts.most_common(5)
            top_attr_ar = "، ".join(f"{w} ({c})" for w, c in top_attr)
            top_attr_en = ", ".join(f"{w} ({c})" for w, c in top_attr)
            insights.append({
                "icon": "✨",
                "ar": f'أكثر الصفات الإلهية ذكراً: {top_attr_ar}. تركيز النص على صفات الرحمة والحكمة يفوق صفات القوة والعظمة.',
                "en": f'Most mentioned divine attributes: {top_attr_en}. The text emphasizes mercy and wisdom attributes over power and might.',
                "category_ar": "الصفات الإلهية",
                "category_en": "Divine Attributes",
            })

            return insights

        insights = compute_insights(df)

        # Display as numbered insight cards
        for idx, ins in enumerate(insights, 1):
            lang = st.session_state.lang
            cat = ins.get(f"category_{lang}", ins.get("category_en", ""))
            text = ins.get(lang, ins.get("en", ""))
            st.markdown(f"""
            <div style="background:white; border:1px solid #D8F3DC; border-radius:12px;
                        padding:20px; margin:12px 0; direction:rtl; text-align:right;
                        box-shadow: 0 2px 8px rgba(27,67,50,0.08);">
                <div style="display:flex; justify-content:space-between; align-items:center; direction:rtl;">
                    <span style="font-size:2rem;">{ins['icon']}</span>
                    <span style="background:#D8F3DC; color:#1B4332; padding:4px 12px; border-radius:15px;
                                font-size:0.85rem; font-family:Amiri;">{cat}</span>
                </div>
                <p style="font-family:Amiri; font-size:1.15rem; line-height:2; color:#1B4332;
                          margin-top:10px;">{text}</p>
            </div>
            """, unsafe_allow_html=True)

        # Summary KPIs
        st.markdown("---")
        section_header("📊 ملخص الأرقام", "📊 Numbers Summary")

        all_w = []
        for text in df["arabic"]:
            all_w.extend(tokenize_arabic(text))
        total_tokens = len(all_w)
        unique_tokens = len(set(all_w))

        sk1, sk2, sk3, sk4, sk5 = st.columns(5)
        sk1.metric(SH("إجمالي الآيات", "Total Verses"), f"{len(df):,}")
        sk2.metric(SH("إجمالي الكلمات", "Total Words"), f"{total_tokens:,}")
        sk3.metric(SH("كلمات فريدة", "Unique Words"), f"{unique_tokens:,}")
        sk4.metric(SH("السور المكية", "Meccan Surahs"), df[df["place"]=="Mecca"]["surah_num"].nunique())
        sk5.metric(SH("السور المدنية", "Medinan Surahs"), df[df["place"]=="Medina"]["surah_num"].nunique())


# ---------------------------------------------------------------------------
# PAGE: STRUCTURAL PATTERNS
# ---------------------------------------------------------------------------
elif page == "Structural Patterns":
    if st.session_state.nav_history:
        if st.button(L('back'), key="sp_back"):
            go_back()
            st.rerun()

    page_title("🧩 الأنماط البنيوية في القرآن", "🧩 Structural Patterns in the Quran",
               "اكتشف الروابط المخفية والأنماط العددية والتناظرات عبر السور",
               "Discover hidden cross-references, numerical patterns, and symmetries across surahs")

    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('🎯 ما نبحث عنه:', '🎯 What we are looking for:')}</strong><br>
        {SH(
            'هذه الصفحة تبحث عن أنماط في القرآن تبدو <em>مقصودة وليست عشوائية</em>. '
            'تخيل أنك تبني أحجية من 6000+ قطعة على مدى 23 سنة — ثم عندما تجمعها تجد أن كل شيء يتناسب بدقة. '
            'نستخدم البيانات للبحث عن: كلمات نادرة تربط بين سور مختلفة، أنماط عددية في أطوال السور والآيات، '
            'وتناظرات موضوعية بين بداية القرآن ونهايته.',
            'This page searches for patterns in the Quran that appear <em>deliberate rather than random</em>. '
            'Imagine building a 6000+ piece puzzle over 23 years — then when assembled, everything fits precisely. '
            'We use data to search for: rare words linking different surahs, numerical patterns in surah/verse lengths, '
            'and thematic symmetries between the beginning and end of the Quran.'
        )}
    </div>
    """, unsafe_allow_html=True)

    sp_tab1, sp_tab2, sp_tab3, sp_tab4, sp_tab5 = st.tabs([
        SH("🔗 الروابط المتقاطعة", "🔗 Cross-References"),
        SH("🔢 الأنماط العددية", "🔢 Numerical Patterns"),
        SH("🪞 التناظر البنيوي", "🪞 Structural Symmetry"),
        SH("🌉 الجسور الموضوعية", "🌉 Thematic Bridges"),
        SH("🔬 التحقق من الأنماط العددية", "🔬 Numerical Claims Verifier"),
    ])

    # ==================================================================
    # TAB 1: CROSS-REFERENCES (Linked Verses)
    # ==================================================================
    with sp_tab1:
        section_header("🔗 آيات مترابطة عبر السور", "🔗 Linked Verses Across Chapters")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>الفكرة:</strong> نبحث عن كلمات <em>نادرة</em> (تظهر في 2-5 سور فقط) تربط بين سور مختلفة. '
                'هذه ليست كلمات شائعة مثل "الله" أو "قال" — بل كلمات متخصصة تظهر في مواضع قليلة جداً، '
                'مما يشير إلى رابط موضوعي مقصود بين تلك السور.',
                '<strong>The idea:</strong> We search for <em>rare</em> words (appearing in only 2-5 surahs) that link different chapters. '
                'These are not common words like "God" or "said" — but specialised words appearing in very few places, '
                'suggesting an intentional thematic link between those surahs.'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def find_cross_references(_df):
            """Find rare words that link different surahs."""
            # Build word → set of surahs mapping
            word_surahs = {}
            word_verses = {}
            for _, row in _df.iterrows():
                words = set(tokenize_arabic(row["arabic"]))
                for w in words:
                    if w not in word_surahs:
                        word_surahs[w] = set()
                        word_verses[w] = []
                    word_surahs[w].add(row["surah_num"])
                    word_verses[w].append({
                        "surah_num": row["surah_num"],
                        "surah_ar": row["surah_name_ar"],
                        "surah_en": row["surah_name_en"],
                        "verse_key": row["verse_key"],
                        "arabic": row["arabic"],
                        "english": row["english"],
                        "place": row["place"],
                    })

            # Find rare linking words (appear in 2-5 surahs only)
            links = []
            for w, surahs in word_surahs.items():
                if 2 <= len(surahs) <= 5:
                    links.append({
                        "word": w,
                        "num_surahs": len(surahs),
                        "surahs": sorted(surahs),
                        "total_verses": len(word_verses[w]),
                        "verses": word_verses[w],
                    })

            # Sort by rarity (fewer surahs = more interesting link)
            links.sort(key=lambda x: (x["num_surahs"], -x["total_verses"]))
            return links

        cross_refs = find_cross_references(df)

        # Summary
        c1, c2, c3 = st.columns(3)
        links_2 = sum(1 for x in cross_refs if x["num_surahs"] == 2)
        links_3 = sum(1 for x in cross_refs if x["num_surahs"] == 3)
        links_45 = sum(1 for x in cross_refs if x["num_surahs"] >= 4)
        c1.metric(SH("كلمات تربط سورتين فقط", "Words linking exactly 2 surahs"), f"{links_2:,}")
        c2.metric(SH("كلمات تربط 3 سور", "Words linking 3 surahs"), f"{links_3:,}")
        c3.metric(SH("كلمات تربط 4-5 سور", "Words linking 4-5 surahs"), f"{links_45:,}")

        # Let user explore
        rarity_filter = st.radio(
            SH("مستوى الندرة", "Rarity Level"),
            [SH("نادرة جداً (سورتان فقط)", "Very rare (2 surahs only)"),
             SH("نادرة (3 سور)", "Rare (3 surahs)"),
             SH("متوسطة (4-5 سور)", "Medium (4-5 surahs)")],
            horizontal=True
        )

        if "سورتان" in rarity_filter or "2 surahs" in rarity_filter:
            filtered_links = [x for x in cross_refs if x["num_surahs"] == 2]
        elif "3" in rarity_filter:
            filtered_links = [x for x in cross_refs if x["num_surahs"] == 3]
        else:
            filtered_links = [x for x in cross_refs if x["num_surahs"] >= 4]

        st.markdown(f"**{SH(f'وُجدت {len(filtered_links)} كلمة رابطة', f'Found {len(filtered_links)} linking words')}**")

        # Show top linking words with expandable verse cards
        for idx, link in enumerate(filtered_links[:30]):
            surah_names = []
            for v in link["verses"]:
                name = v["surah_ar"]
                if name not in surah_names:
                    surah_names.append(name)

            with st.expander(
                f"🔗 **{link['word']}** → {' ↔ '.join(surah_names)} ({link['total_verses']} {SH('آيات', 'verses')})",
                expanded=(idx < 3)
            ):
                for v in link["verses"][:6]:
                    st.markdown(f"""
                    <div class="verse-card">
                        <strong style='color:#2D6A4F;'>{v['verse_key']} — {v['surah_ar']}</strong>
                        <span style='color:#95D5B2;'> ({v['place']})</span>
                        <div class="arabic-text">{highlight_word_in_verse(v['arabic'], link['word'])}</div>
                        <div style='color:#555; padding:5px 15px; font-style:italic;'>{v['english']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                if link["total_verses"] > 6:
                    if st.button(SH(f"🔬 استكشف كل {link['total_verses']} آية", f"🔬 Explore all {link['total_verses']} verses"),
                                key=f"xref_{idx}"):
                        navigate_to("Word Explorer", explore_word=link["word"])
                        st.rerun()

    # ==================================================================
    # TAB 2: NUMERICAL PATTERNS
    # ==================================================================
    with sp_tab2:
        section_header("🔢 الأنماط العددية", "🔢 Numerical Patterns")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>الفكرة:</strong> نبحث عن أنماط في الأرقام — عدد الآيات، عدد الكلمات، مواضع السور. '
                'هل هناك تناظرات عددية؟ هل بعض الأرقام تتكرر بشكل غير عشوائي؟',
                '<strong>The idea:</strong> We search for patterns in numbers — verse counts, word counts, surah positions. '
                'Are there numerical symmetries? Do certain numbers recur non-randomly?'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def compute_numerical_patterns(_df):
            results = {}

            # Surah-level stats
            surah_stats = []
            for sn in sorted(_df["surah_num"].unique()):
                sdf = _df[_df["surah_num"] == sn]
                word_count = sum(len(re.findall(r'[\u0600-\u06FF]+', t)) for t in sdf["arabic"])
                surah_stats.append({
                    "surah_num": sn,
                    "name_ar": sdf.iloc[0]["surah_name_ar"],
                    "verse_count": len(sdf),
                    "word_count": word_count,
                    "place": sdf.iloc[0]["place"],
                })
            stats_df = pd.DataFrame(surah_stats)

            # 1. Total verses and surahs
            results["total_verses"] = len(_df)
            results["total_surahs"] = 114

            # 2. Odd/even verse count surahs
            results["odd_verse_surahs"] = len(stats_df[stats_df["verse_count"] % 2 == 1])
            results["even_verse_surahs"] = len(stats_df[stats_df["verse_count"] % 2 == 0])

            # 3. First half vs second half symmetry
            first_half = stats_df[stats_df["surah_num"] <= 57]
            second_half = stats_df[stats_df["surah_num"] > 57]
            results["first_half_verses"] = first_half["verse_count"].sum()
            results["second_half_verses"] = second_half["verse_count"].sum()
            results["first_half_words"] = first_half["word_count"].sum()
            results["second_half_words"] = second_half["word_count"].sum()

            # 4. Verse count frequency — which verse counts are most common
            vc_freq = stats_df["verse_count"].value_counts().head(10)
            results["common_verse_counts"] = vc_freq

            # 5. Word-per-verse ratio progression
            stats_df["words_per_verse"] = stats_df["word_count"] / stats_df["verse_count"]
            results["stats_df"] = stats_df

            return results

        num_patterns = compute_numerical_patterns(df)
        stats_df = num_patterns["stats_df"]

        # KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(SH("إجمالي السور", "Total Surahs"), 114)
        k2.metric(SH("سور بآيات فردية", "Odd-verse Surahs"), num_patterns["odd_verse_surahs"])
        k3.metric(SH("سور بآيات زوجية", "Even-verse Surahs"), num_patterns["even_verse_surahs"])
        k4.metric(SH("إجمالي الآيات", "Total Verses"), f"{num_patterns['total_verses']:,}")

        # First half vs second half
        section_header("⚖️ النصف الأول مقابل الثاني", "⚖️ First Half vs Second Half")

        h1, h2 = st.columns(2)
        with h1:
            st.markdown(f"""
            <div style="background:#fce4ec; border-radius:12px; padding:20px; text-align:center;">
                <h3 style="color:#B7094C;">{SH('السور 1-57', 'Surahs 1-57')}</h3>
                <p style="font-size:1.5rem; font-weight:bold; color:#B7094C;">{num_patterns['first_half_verses']:,} {SH('آية', 'verses')}</p>
                <p style="color:#B7094C;">{num_patterns['first_half_words']:,} {SH('كلمة', 'words')}</p>
            </div>
            """, unsafe_allow_html=True)
        with h2:
            st.markdown(f"""
            <div style="background:#e0f7fa; border-radius:12px; padding:20px; text-align:center;">
                <h3 style="color:#0091AD;">{SH('السور 58-114', 'Surahs 58-114')}</h3>
                <p style="font-size:1.5rem; font-weight:bold; color:#0091AD;">{num_patterns['second_half_verses']:,} {SH('آية', 'verses')}</p>
                <p style="color:#0091AD;">{num_patterns['second_half_words']:,} {SH('كلمة', 'words')}</p>
            </div>
            """, unsafe_allow_html=True)

        ratio_v = num_patterns['first_half_verses'] / num_patterns['second_half_verses'] if num_patterns['second_half_verses'] > 0 else 0
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 ملاحظة:', '💡 Finding:')}</strong><br>
            {SH(
                f'النصف الأول يحتوي {ratio_v:.1f}x آيات أكثر من النصف الثاني. لكن السور الـ57 الأخيرة أقصر بكثير — '
                f'هذا يعني أن القرآن ينتقل تدريجياً من السور الطويلة التفصيلية إلى السور القصيرة المركزة.',
                f'The first half contains {ratio_v:.1f}x more verses than the second half. But the last 57 surahs are much shorter — '
                f'meaning the Quran gradually transitions from long detailed surahs to short focused ones.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Verse count progression chart
        section_header("📈 تطور طول السور", "📈 Surah Length Progression")

        fig_prog = px.scatter(stats_df, x="surah_num", y="verse_count",
                             color="place",
                             color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                             size="word_count", hover_data={"name_ar": True},
                             labels={"surah_num": SH("رقم السورة", "Surah #"),
                                     "verse_count": SH("عدد الآيات", "Verse Count")})
        fig_prog.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              height=400)
        st.plotly_chart(fig_prog, use_container_width=True)

    # ==================================================================
    # TAB 3: STRUCTURAL SYMMETRY
    # ==================================================================
    with sp_tab3:
        section_header("🪞 التناظر البنيوي", "🪞 Structural Symmetry")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>الفكرة:</strong> نقارن بين السور المتناظرة — السورة الأولى مع الأخيرة، الثانية مع ما قبل الأخيرة، وهكذا. '
                'هل هناك تشابه موضوعي أو لغوي بين السور المتقابلة؟ هذا يشبه "المرآة" — هل يعكس نهاية القرآن بدايته؟',
                '<strong>The idea:</strong> We compare mirror surahs — first with last, second with second-to-last, etc. '
                'Is there thematic or linguistic similarity between paired surahs? Like a mirror — does the end of the Quran reflect its beginning?'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def compute_mirror_pairs(_df):
            """Compare surah pairs: (1,114), (2,113), (3,112), etc."""
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # Build surah texts
            surah_texts = {}
            surah_meta = {}
            for sn in sorted(_df["surah_num"].unique()):
                sdf = _df[_df["surah_num"] == sn]
                words = []
                for text in sdf["arabic"]:
                    words.extend(tokenize_arabic(text))
                surah_texts[sn] = " ".join(words)
                surah_meta[sn] = {
                    "name_ar": sdf.iloc[0]["surah_name_ar"],
                    "name_en": sdf.iloc[0]["surah_name_en"],
                    "place": sdf.iloc[0]["place"],
                    "verses": len(sdf),
                }

            # TF-IDF for all surahs
            all_surahs = sorted(surah_texts.keys())
            texts = [surah_texts[s] for s in all_surahs]
            tfidf = TfidfVectorizer(max_features=2000)
            tfidf_matrix = tfidf.fit_transform(texts)

            # Compute mirror pairs
            pairs = []
            n = len(all_surahs)
            for i in range(n // 2):
                s1 = all_surahs[i]
                s2 = all_surahs[n - 1 - i]
                sim = cosine_similarity(tfidf_matrix[i:i+1], tfidf_matrix[n-1-i:n-i])[0][0]
                pairs.append({
                    "surah_a": s1, "surah_b": s2,
                    "name_a_ar": surah_meta[s1]["name_ar"],
                    "name_b_ar": surah_meta[s2]["name_ar"],
                    "name_a_en": surah_meta[s1]["name_en"],
                    "name_b_en": surah_meta[s2]["name_en"],
                    "place_a": surah_meta[s1]["place"],
                    "place_b": surah_meta[s2]["place"],
                    "similarity": sim,
                    "verses_a": surah_meta[s1]["verses"],
                    "verses_b": surah_meta[s2]["verses"],
                })

            return pd.DataFrame(pairs)

        mirror_df = compute_mirror_pairs(df)

        # Similarity distribution
        avg_sim = mirror_df["similarity"].mean()
        high_sim = len(mirror_df[mirror_df["similarity"] > 0.3])

        k1, k2, k3 = st.columns(3)
        k1.metric(SH("متوسط التشابه", "Avg Similarity"), f"{avg_sim:.3f}")
        k2.metric(SH("أزواج متشابهة (>30%)", "High Similarity Pairs (>30%)"), high_sim)
        k3.metric(SH("إجمالي الأزواج", "Total Pairs"), len(mirror_df))

        # Chart: mirror similarity
        mirror_sorted = mirror_df.sort_values("similarity", ascending=False)
        mirror_sorted["pair_label"] = mirror_sorted.apply(
            lambda r: f"{r['name_a_ar']} ↔ {r['name_b_ar']}", axis=1)

        fig_mirror = px.bar(mirror_sorted.head(20), x="similarity", y="pair_label",
                           orientation="h", color="similarity",
                           color_continuous_scale=["#D8F3DC", "#B7094C"],
                           text=mirror_sorted.head(20)["similarity"].apply(lambda x: f"{x:.2%}"))
        fig_mirror.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=500,
            yaxis=dict(tickfont=dict(size=13, family="Amiri"), side="right", title=""),
            xaxis=dict(title=SH("درجة التشابه", "Similarity Score"), side="top"),
            coloraxis_showscale=False
        )
        fig_mirror.update_traces(textposition="outside")
        st.plotly_chart(fig_mirror, use_container_width=True)

        # Highlight most interesting pairs
        top_pairs = mirror_sorted.head(5)
        section_header("🌟 أكثر الأزواج تشابهاً", "🌟 Most Similar Mirror Pairs")

        for _, pair in top_pairs.iterrows():
            st.markdown(f"""
            <div class="verse-card">
                <div style="display:flex; justify-content:space-between; direction:rtl;">
                    <div style="text-align:center; flex:1;">
                        <strong style="color:#B7094C;">📗 {pair['name_a_ar']}</strong><br>
                        <span style="color:#888;">{SH(f'سورة {pair["surah_a"]}', f'Surah {pair["surah_a"]}')} · {pair['place_a']} · {pair['verses_a']} {SH('آية', 'verses')}</span>
                    </div>
                    <div style="text-align:center; padding:10px;">
                        <span style="font-size:1.5rem; color:#D4A574;">↔</span><br>
                        <strong style="color:#2D6A4F;">{pair['similarity']:.1%}</strong>
                    </div>
                    <div style="text-align:center; flex:1;">
                        <strong style="color:#0091AD;">📘 {pair['name_b_ar']}</strong><br>
                        <span style="color:#888;">{SH(f'سورة {pair["surah_b"]}', f'Surah {pair["surah_b"]}')} · {pair['place_b']} · {pair['verses_b']} {SH('آية', 'verses')}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================================
    # TAB 4: THEMATIC BRIDGES
    # ==================================================================
    with sp_tab4:
        section_header("🌉 الجسور الموضوعية", "🌉 Thematic Bridges")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>الفكرة:</strong> نبحث عن سور تتشابه موضوعياً رغم أنها نزلت في أوقات وأماكن مختلفة. '
                'إذا وجدنا سورة مكية تتشابه بقوة مع سورة مدنية — فهذا يشير إلى رابط عبر فترات النزول.',
                '<strong>The idea:</strong> We search for surahs that are thematically similar despite being revealed at different times and places. '
                'If we find a Meccan surah strongly similar to a Medinan one — this suggests a bridge across revelation periods.'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def find_thematic_bridges(_df):
            """Find the most similar Meccan-Medinan surah pairs."""
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            mecca_surahs = []
            medina_surahs = []
            all_texts = []
            all_meta = []

            for sn in sorted(_df["surah_num"].unique()):
                sdf = _df[_df["surah_num"] == sn]
                words = []
                for text in sdf["arabic"]:
                    words.extend(tokenize_arabic(text))
                text_joined = " ".join(words)
                meta = {
                    "surah_num": sn,
                    "name_ar": sdf.iloc[0]["surah_name_ar"],
                    "name_en": sdf.iloc[0]["surah_name_en"],
                    "place": sdf.iloc[0]["place"],
                    "verses": len(sdf),
                }
                all_texts.append(text_joined)
                all_meta.append(meta)
                if meta["place"] == "Mecca":
                    mecca_surahs.append(len(all_meta) - 1)
                else:
                    medina_surahs.append(len(all_meta) - 1)

            tfidf = TfidfVectorizer(max_features=2000)
            tfidf_matrix = tfidf.fit_transform(all_texts)

            # Compare every Meccan with every Medinan
            bridges = []
            for mi in mecca_surahs:
                for di in medina_surahs:
                    sim = cosine_similarity(tfidf_matrix[mi:mi+1], tfidf_matrix[di:di+1])[0][0]
                    if sim > 0.1:  # Only interesting pairs
                        bridges.append({
                            "mecca_idx": mi, "medina_idx": di,
                            "mecca_ar": all_meta[mi]["name_ar"],
                            "medina_ar": all_meta[di]["name_ar"],
                            "mecca_en": all_meta[mi]["name_en"],
                            "medina_en": all_meta[di]["name_en"],
                            "mecca_num": all_meta[mi]["surah_num"],
                            "medina_num": all_meta[di]["surah_num"],
                            "similarity": sim,
                        })

            return sorted(bridges, key=lambda x: -x["similarity"])

        bridges = find_thematic_bridges(df)

        st.markdown(f"**{SH(f'وُجد {len(bridges)} جسر موضوعي بين السور المكية والمدنية', f'Found {len(bridges)} thematic bridges between Meccan and Medinan surahs')}**")

        # Network visualization
        section_header("🕸️ شبكة الروابط الموضوعية", "🕸️ Thematic Link Network")

        # Show top bridges as a scatter plot (similarity vs surah distance)
        top_bridges = bridges[:50]
        br_df = pd.DataFrame(top_bridges)

        if len(br_df) > 0:
            br_df["distance"] = abs(br_df["mecca_num"] - br_df["medina_num"])
            br_df["label"] = br_df["mecca_ar"] + " ↔ " + br_df["medina_ar"]

            fig_br = px.scatter(br_df, x="distance", y="similarity",
                               hover_data={"label": True, "distance": False, "similarity": False},
                               size="similarity",
                               color="similarity",
                               color_continuous_scale=["#D8F3DC", "#B7094C"],
                               labels={"distance": SH("المسافة بين السورتين", "Distance Between Surahs"),
                                       "similarity": SH("درجة التشابه", "Similarity")})
            fig_br.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                height=450)
            fig_br.update_traces(marker=dict(line=dict(width=1, color="white")))
            st.plotly_chart(fig_br, use_container_width=True)

            st.markdown(f"""
            <div class="insight-box">
                <strong>{SH('💡 كيف تقرأ هذا:', '💡 How to read this:')}</strong><br>
                {SH(
                    'كل نقطة تمثل زوجاً من سورة مكية وسورة مدنية. المحور الأفقي يمثل المسافة بينهما (عدد السور الفاصلة). '
                    'المحور العمودي يمثل درجة التشابه. النقاط في الزاوية العلوية اليمنى هي الأكثر إثارة — '
                    'سور متباعدة جداً لكنها متشابهة موضوعياً.',
                    'Each dot represents a Meccan-Medinan pair. The horizontal axis shows the distance between them (number of surahs apart). '
                    'The vertical axis shows similarity. Dots in the upper-right corner are most interesting — '
                    'surahs far apart but thematically similar.'
                )}
            </div>
            """, unsafe_allow_html=True)

            # Top 10 bridges
            section_header("🏆 أقوى الجسور الموضوعية", "🏆 Strongest Thematic Bridges")

            for idx, br in enumerate(top_bridges[:10]):
                st.markdown(f"""
                <div class="verse-card">
                    <div style="display:flex; justify-content:space-between; direction:rtl; align-items:center;">
                        <div style="text-align:center; flex:1;">
                            <span style="background:#fce4ec; padding:3px 10px; border-radius:10px; color:#B7094C; font-size:0.8rem;">
                                {SH('مكية', 'Meccan')}
                            </span><br>
                            <strong style="font-family:Amiri; font-size:1.2rem;">{br['mecca_ar']}</strong><br>
                            <span style="color:#888; font-size:0.85rem;">{SH(f'سورة {br["mecca_num"]}', f'Surah {br["mecca_num"]}')}</span>
                        </div>
                        <div style="text-align:center; padding:10px;">
                            <span style="font-size:2rem;">🌉</span><br>
                            <strong style="color:#2D6A4F; font-size:1.3rem;">{br['similarity']:.1%}</strong><br>
                            <span style="color:#888; font-size:0.8rem;">{SH('تشابه', 'similarity')}</span>
                        </div>
                        <div style="text-align:center; flex:1;">
                            <span style="background:#e0f7fa; padding:3px 10px; border-radius:10px; color:#0091AD; font-size:0.8rem;">
                                {SH('مدنية', 'Medinan')}
                            </span><br>
                            <strong style="font-family:Amiri; font-size:1.2rem;">{br['medina_ar']}</strong><br>
                            <span style="color:#888; font-size:0.85rem;">{SH(f'سورة {br["medina_num"]}', f'Surah {br["medina_num"]}')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Compare button
            if len(top_bridges) > 0:
                st.markdown("---")
                comp_cols = st.columns(3)
                with comp_cols[1]:
                    if st.button(SH("⚖️ قارن أقوى زوج في مقارنة السور", "⚖️ Compare top pair in Surah Comparator"),
                                key="bridge_compare", use_container_width=True):
                        navigate_to("Surah Comparator",
                                   compare_surah_a=top_bridges[0]["mecca_num"],
                                   compare_surah_b=top_bridges[0]["medina_num"])
                        st.rerun()

    # ==================================================================
    # TAB 5: NUMERICAL CLAIMS VERIFIER
    # ==================================================================
    with sp_tab5:
        section_header("🔬 التحقق من الادعاءات العددية", "🔬 Numerical Claims Verifier")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>ما هذا؟</strong> هناك ادعاءات شائعة عن "معجزات عددية" في القرآن — مثل أن كلمة "يوم" تظهر 365 مرة '
                'أو أن "الحياة" و"الموت" يظهران بنفس العدد. بدلاً من تصديق هذه الادعاءات أو تكذيبها، '
                '<strong>نتحقق منها بالبيانات</strong>. نعد الكلمات فعلياً في مجموعة البيانات ونرى النتائج.',
                '<strong>What is this?</strong> There are popular claims about "numerical miracles" in the Quran — like "day" appearing 365 times '
                'or "life" and "death" appearing equally. Instead of accepting or rejecting these claims, '
                '<strong>we verify them with data</strong>. We actually count the words in our dataset and see the results.'
            )}
            <br><br>
            {SH(
                '⚠️ <strong>ملاحظة مهمة:</strong> النتائج تعتمد على طريقة العد (مع/بدون التشكيل، المشتقات، الجذور). '
                'قد تختلف الأرقام عن المصادر الأخرى حسب المنهجية المستخدمة. هذا تحليل بيانات، ليس فتوى دينية.',
                '⚠️ <strong>Important note:</strong> Results depend on counting methodology (with/without diacritics, derivatives, roots). '
                'Numbers may differ from other sources depending on methodology. This is data analysis, not religious ruling.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # ---- ANTONYM PAIR CLAIMS ----
        section_header("⚖️ التوازن بين الأضداد", "⚖️ Antonym Pair Balance")

        st.markdown(f"""
        {SH(
            'الادعاء: كلمات متضادة تظهر بنفس العدد في القرآن. هل هذا صحيح؟ لنتحقق...',
            'The claim: Antonym words appear the same number of times in the Quran. Is this true? Let us verify...'
        )}
        """)

        # Define the claimed pairs with Arabic search terms
        ANTONYM_CLAIMS = [
            {"ar_a": "حياة", "ar_b": "موت", "en_a": "life", "en_b": "death", "claimed": 145,
             "label_ar": "الحياة والموت", "label_en": "Life & Death"},
            {"ar_a": "دنيا", "ar_b": "آخرة", "en_a": "world", "en_b": "hereafter", "claimed": 115,
             "label_ar": "الدنيا والآخرة", "label_en": "Worldly & Afterlife"},
            {"ar_a": "ملائكة", "ar_b": "شياطين", "en_a": "angels", "en_b": "demons", "claimed": 88,
             "label_ar": "الملائكة والشياطين", "label_en": "Angels & Demons"},
            {"ar_a": "رجل", "ar_b": "امرأة", "en_a": "man", "en_b": "woman", "claimed": 24,
             "label_ar": "الرجل والمرأة", "label_en": "Man & Woman"},
            {"ar_a": "نفع", "ar_b": "فساد", "en_a": "benefit", "en_b": "corruption", "claimed": 50,
             "label_ar": "النفع والفساد", "label_en": "Benefit & Corruption"},
        ]

        @st.cache_data
        def verify_antonym_pairs(_df, pairs):
            results = []
            for pair in pairs:
                # Count in Arabic text (normalized)
                norm_a = normalize_arabic(pair["ar_a"])
                norm_b = normalize_arabic(pair["ar_b"])
                count_a = sum(1 for _, r in _df.iterrows()
                             if norm_a in normalize_arabic(r["arabic"]))
                count_b = sum(1 for _, r in _df.iterrows()
                             if norm_b in normalize_arabic(r["arabic"]))
                # Also count in English for comparison
                en_a = sum(1 for _, r in _df.iterrows()
                          if pair["en_a"] in r["english"].lower())
                en_b = sum(1 for _, r in _df.iterrows()
                          if pair["en_b"] in r["english"].lower())

                match = count_a == count_b
                results.append({
                    **pair,
                    "found_a": count_a,
                    "found_b": count_b,
                    "en_found_a": en_a,
                    "en_found_b": en_b,
                    "match": match,
                    "diff": abs(count_a - count_b),
                })
            return results

        pair_results = verify_antonym_pairs(df, ANTONYM_CLAIMS)

        # Display results as cards
        for pr in pair_results:
            label = SH(pr["label_ar"], pr["label_en"])
            if pr["match"]:
                status_icon = "✅"
                status_color = "#2D6A4F"
                status_text = SH("متطابق!", "MATCH!")
            elif pr["diff"] <= 3:
                status_icon = "🟡"
                status_color = "#D4A574"
                status_text = SH(f"قريب جداً (فرق {pr['diff']})", f"Very close (diff {pr['diff']})")
            else:
                status_icon = "❌"
                status_color = "#B7094C"
                status_text = SH(f"غير متطابق (فرق {pr['diff']})", f"No match (diff {pr['diff']})")

            st.markdown(f"""
            <div style="background:white; border:1px solid #D8F3DC; border-radius:12px;
                        padding:15px; margin:10px 0; direction:rtl;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="font-family:Amiri; font-size:1.2rem; color:#1B4332;">{status_icon} {label}</strong>
                    </div>
                    <div style="color:{status_color}; font-weight:bold;">{status_text}</div>
                </div>
                <div style="display:flex; justify-content:space-around; margin-top:12px; text-align:center;">
                    <div style="background:#f0f7f0; padding:10px 20px; border-radius:8px;">
                        <div style="font-family:Amiri; font-size:1.1rem; color:#1B4332;">"{pr['ar_a']}"</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:#2D6A4F;">{pr['found_a']}</div>
                        <div style="font-size:0.8rem; color:#888;">{SH('آية تحتوي الكلمة', 'verses containing word')}</div>
                    </div>
                    <div style="display:flex; align-items:center; font-size:1.5rem; color:#D4A574;">
                        {'=' if pr['match'] else '≠'}
                    </div>
                    <div style="background:#f0f7f0; padding:10px 20px; border-radius:8px;">
                        <div style="font-family:Amiri; font-size:1.1rem; color:#1B4332;">"{pr['ar_b']}"</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:#2D6A4F;">{pr['found_b']}</div>
                        <div style="font-size:0.8rem; color:#888;">{SH('آية تحتوي الكلمة', 'verses containing word')}</div>
                    </div>
                    <div style="background:#e8e8e8; padding:10px 15px; border-radius:8px;">
                        <div style="font-size:0.8rem; color:#888;">{SH('المُدّعى', 'Claimed')}</div>
                        <div style="font-size:1.2rem; font-weight:bold; color:#888;">{pr['claimed']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Summary insight
        matches = sum(1 for r in pair_results if r["match"])
        close = sum(1 for r in pair_results if not r["match"] and r["diff"] <= 3)
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة التحقق:', '💡 Verification Result:')}</strong><br>
            {SH(
                f'من {len(pair_results)} زوج تم اختباره: <strong>{matches} متطابق تماماً</strong>، '
                f'{close} قريب جداً، {len(pair_results) - matches - close} غير متطابق. '
                f'النتائج تعتمد على المنهجية — هل نعد الكلمة الجذرية أم المشتقات أم الآيات التي تحتوي الكلمة؟ '
                f'كل منهجية قد تعطي نتائج مختلفة.',
                f'Of {len(pair_results)} pairs tested: <strong>{matches} exact match</strong>, '
                f'{close} very close, {len(pair_results) - matches - close} no match. '
                f'Results depend on methodology — do we count root words, derivatives, or verses containing the word? '
                f'Each methodology may yield different results.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # ---- CALENDAR WORD CLAIMS ----
        st.markdown("---")
        section_header("📅 ادعاءات الكلمات التقويمية", "📅 Calendar Word Claims")

        CALENDAR_CLAIMS = [
            {"ar": "يوم", "en": "day", "claimed": 365, "label_ar": "يوم (مفرد)", "label_en": "Day (singular)",
             "note_ar": "يُدّعى أنها تظهر 365 مرة = أيام السنة", "note_en": "Claimed to appear 365 times = days in a year"},
            {"ar": "شهر", "en": "month", "claimed": 12, "label_ar": "شهر", "label_en": "Month",
             "note_ar": "يُدّعى أنها تظهر 12 مرة = أشهر السنة", "note_en": "Claimed to appear 12 times = months in a year"},
            {"ar": "صلاة", "en": "prayer", "claimed": 5, "label_ar": "صلاة/صلوات", "label_en": "Prayer/Prayers",
             "note_ar": "يُدّعى أنها تظهر 5 مرات = الصلوات الخمس", "note_en": "Claimed to appear 5 times = five daily prayers"},
        ]

        @st.cache_data
        def verify_calendar_claims(_df, claims):
            results = []
            for claim in claims:
                norm_word = normalize_arabic(claim["ar"])
                query_stems = strip_arabic_affixes(claim["ar"])
                # Count verses containing the word (exact match)
                verse_count = sum(1 for _, r in _df.iterrows()
                                 if norm_word in normalize_arabic(r["arabic"]))
                # Count with root-aware matching (finds all derivatives)
                root_verse_count = sum(1 for _, r in _df.iterrows()
                                      if fuzzy_arabic_match(claim["ar"], r["arabic"]))
                # Count total occurrences (word may appear multiple times in one verse)
                total_count = 0
                for _, r in _df.iterrows():
                    normalized = normalize_arabic(r["arabic"])
                    words = re.findall(r'[\u0620-\u064A]+', normalized)
                    total_count += sum(1 for w in words if norm_word in w)

                results.append({
                    **claim,
                    "verse_count": verse_count,
                    "root_verse_count": root_verse_count,
                    "total_count": total_count,
                    "verse_match": verse_count == claim["claimed"],
                    "total_match": total_count == claim["claimed"],
                    "root_match": root_verse_count == claim["claimed"],
                })
            return results

        cal_results = verify_calendar_claims(df, CALENDAR_CLAIMS)

        for cr in cal_results:
            label = SH(cr["label_ar"], cr["label_en"])
            note = SH(cr["note_ar"], cr["note_en"])

            if cr["verse_match"] or cr["total_match"]:
                bg = "#e8f5e9"
                icon = "✅"
            else:
                bg = "#fff3e0"
                icon = "🔍"

            st.markdown(f"""
            <div style="background:{bg}; border-radius:12px; padding:15px; margin:10px 0; direction:rtl;">
                <strong style="font-family:Amiri; font-size:1.2rem;">{icon} {label}</strong>
                <span style="color:#888; font-size:0.9rem;"> — {note}</span>
                <div style="display:flex; justify-content:space-around; margin-top:12px; text-align:center; flex-wrap:wrap; gap:8px;">
                    <div style="background:white; padding:10px 15px; border-radius:8px; min-width:100px;">
                        <div style="font-size:0.75rem; color:#888;">{SH('المُدّعى', 'Claimed')}</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:#888;">{cr['claimed']}</div>
                    </div>
                    <div style="background:white; padding:10px 15px; border-radius:8px; min-width:100px;">
                        <div style="font-size:0.75rem; color:#888;">{SH('مطابقة تامة', 'Exact match')}</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:{'#2D6A4F' if cr['verse_match'] else '#B7094C'};">{cr['verse_count']}</div>
                    </div>
                    <div style="background:white; padding:10px 15px; border-radius:8px; min-width:100px; border:2px solid #D4A574;">
                        <div style="font-size:0.75rem; color:#D4A574; font-weight:bold;">{SH('بحث بالجذر 🔍', 'Root search 🔍')}</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:{'#2D6A4F' if cr['root_match'] else '#D4A574'};">{cr['root_verse_count']}</div>
                    </div>
                    <div style="background:white; padding:10px 15px; border-radius:8px; min-width:100px;">
                        <div style="font-size:0.75rem; color:#888;">{SH('إجمالي التكرار', 'Total count')}</div>
                        <div style="font-size:1.8rem; font-weight:bold; color:{'#2D6A4F' if cr['total_match'] else '#888'};">{cr['total_count']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 لماذا تختلف الأرقام؟', '💡 Why do numbers differ?')}</strong><br>
            {SH(
                'الادعاءات العددية تعتمد على منهجية العد. هل نعد:<br>'
                '• الكلمة الجذرية فقط (يوم)؟<br>'
                '• كل المشتقات (يوم، أيام، يومئذ)؟<br>'
                '• عدد الآيات التي تحتوي الكلمة؟<br>'
                '• عدد مرات ظهور الكلمة حتى لو تكررت في آية واحدة؟<br><br>'
                'كل منهجية تعطي رقماً مختلفاً. هذا لا يعني أن الادعاء "خاطئ" — بل يعني أن المنهجية مهمة. '
                'هذا هو جوهر تحليل البيانات: <strong>السؤال ليس فقط "ما الرقم؟" بل "كيف وصلنا إليه؟"</strong>',
                'Numerical claims depend on counting methodology. Do we count:<br>'
                '• The root word only (day)?<br>'
                '• All derivatives (day, days, that day)?<br>'
                '• Number of verses containing the word?<br>'
                '• Number of times the word appears even if repeated in one verse?<br><br>'
                'Each methodology gives a different number. This does not mean the claim is "wrong" — it means methodology matters. '
                'This is the essence of data analysis: <strong>the question is not just "what is the number?" but "how did we get it?"</strong>'
            )}
        </div>
        """, unsafe_allow_html=True)

        # ---- YOUR OWN WORD COUNTER ----
        st.markdown("---")
        section_header("🔍 عدّاد الكلمات الخاص بك", "🔍 Your Own Word Counter")

        st.markdown(SH(
            "اكتب أي كلمة عربية وسنعد تكرارها في القرآن بطريقتين: عدد الآيات وعدد التكرار الكلي.",
            "Type any Arabic word and we will count it in the Quran two ways: verse count and total occurrences."
        ))

        custom_word = st.text_input(SH("اكتب كلمة للعد", "Type a word to count"), placeholder="رحمة", key="custom_counter")
        if custom_word:
            norm_cw = normalize_arabic(custom_word)
            cw_verse = sum(1 for _, r in df.iterrows() if norm_cw in normalize_arabic(r["arabic"]))
            cw_total = 0
            for _, r in df.iterrows():
                normalized = normalize_arabic(r["arabic"])
                cw_words = re.findall(r'[\u0620-\u064A]+', normalized)
                cw_total += sum(1 for w in cw_words if norm_cw in w)

            cc1, cc2 = st.columns(2)
            cc1.metric(SH("آيات تحتوي الكلمة", "Verses containing word"), f"{cw_verse:,}")
            cc2.metric(SH("إجمالي التكرار", "Total occurrences"), f"{cw_total:,}")

            if st.button(SH("🔬 استكشف هذه الكلمة بالتفصيل", "🔬 Explore this word in detail"), key="counter_explore"):
                navigate_to("Word Explorer", explore_word=custom_word)
                st.rerun()


# ---------------------------------------------------------------------------
# PAGE: SCIENTIFIC REFERENCES
# ---------------------------------------------------------------------------
elif page == "Scientific References":
    if st.session_state.nav_history:
        if st.button(L('back'), key="sci_back"):
            go_back()
            st.rerun()

    page_title("🔭 الإشارات العلمية في القرآن", "🔭 Scientific References in the Quran",
               "آيات تتوافق مع اكتشافات علمية حديثة — حقائق لم تكن معروفة قبل 1400 سنة",
               "Verses aligning with modern scientific discoveries — facts unknown 1400 years ago")

    # Scientific references database
    SCIENTIFIC_REFS = [
        # ═══════════════ COSMOLOGY ═══════════════
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 51, "verse": 47, "topic_ar": "توسع الكون", "topic_en": "Universe Expansion",
         "science_ar": "اكتشف إدوين هابل عام 1929 أن الكون يتوسع باستمرار.", "science_en": "Edwin Hubble discovered in 1929 that the universe is continuously expanding."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 21, "verse": 30, "topic_ar": "الانفجار الكبير", "topic_en": "Big Bang — Heaven and Earth Were Joined",
         "science_ar": "نظرية الانفجار الكبير تقول إن الكون بدأ من نقطة واحدة متناهية الكثافة ثم انفصلت.", "science_en": "The Big Bang theory states the universe began from a single, infinitely dense point that then separated."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 21, "verse": 33, "topic_ar": "المدارات الفلكية", "topic_en": "Celestial Orbits",
         "science_ar": "كل الأجرام السماوية تسبح في مدارات محددة.", "science_en": "All celestial bodies swim in defined orbits."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 21, "verse": 104, "topic_ar": "الانسحاق الكبير", "topic_en": "Big Crunch Theory",
         "science_ar": "بعض النظريات الكونية تتوقع أن الكون سينكمش على نفسه في النهاية.", "science_en": "Some cosmological theories predict the universe will eventually collapse back on itself."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 41, "verse": 11, "topic_ar": "الكون كان دخاناً", "topic_en": "Universe Was Smoke/Gas",
         "science_ar": "يؤكد العلم الحديث أن الكون المبكر كان سحابة غازية ساخنة (سديم) قبل تكوّن النجوم.", "science_en": "Modern science confirms the early universe was a hot gaseous cloud (nebula) before stars formed."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 36, "verse": 40, "topic_ar": "الليل والنهار لا يسبق أحدهما الآخر", "topic_en": "Day and Night — Neither Overtakes the Other",
         "science_ar": "دوران الأرض يجعل الليل والنهار يتعاقبان بانتظام دون أن يسبق أحدهما الآخر.", "science_en": "Earth's rotation causes day and night to alternate regularly without one overtaking the other."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 39, "verse": 5, "topic_ar": "تكوير الليل على النهار", "topic_en": "Night Wraps Around Day (Spherical Earth)",
         "science_ar": "كلمة 'يكوّر' تعني اللف حول شكل كروي — مما يشير إلى كروية الأرض.", "science_en": "The word 'yukawwir' means to wrap around a sphere — suggesting the Earth is round."},
        {"category_ar": "🌌 علم الكونيات", "category_en": "🌌 Cosmology",
         "surah": 86, "verse": 11, "topic_ar": "السماء ذات الرجع", "topic_en": "Sky That Returns (Atmospheric Reflection)",
         "science_ar": "الغلاف الجوي يعيد الأشعة والموجات — يعكس موجات الراديو ويعيد بخار الماء كمطر.", "science_en": "The atmosphere returns radiation and waves — reflects radio waves and returns water vapor as rain."},

        # ═══════════════ EMBRYOLOGY ═══════════════
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 23, "verse": 14, "topic_ar": "مراحل تطور الجنين", "topic_en": "Stages of Embryonic Development",
         "science_ar": "يتطور الجنين عبر مراحل: نطفة، علقة، مضغة، ثم عظام ولحم — بدقة تطابق علم الأجنة.", "science_en": "The embryo develops through stages: drop, clinging clot, chewed-like lump, then bones and flesh — matching embryology."},
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 39, "verse": 6, "topic_ar": "ثلاث ظلمات", "topic_en": "Three Layers of Darkness",
         "science_ar": "الجنين محاط بثلاث طبقات: جدار البطن، جدار الرحم، والغشاء الأمنيوسي.", "science_en": "The embryo is surrounded by three layers: abdominal wall, uterine wall, and amniotic membrane."},
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 76, "verse": 2, "topic_ar": "الأمشاج — سوائل مختلطة", "topic_en": "Mixed Fluids (Gametes)",
         "science_ar": "الإنسان يُخلق من نطفة أمشاج — أي سوائل مختلطة. يتطابق مع اتحاد الحيوان المنوي والبويضة.", "science_en": "Humans are created from mixed fluids (nutfatin amshaj) — matching the union of sperm and egg."},
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 22, "verse": 5, "topic_ar": "مراحل الخلق من تراب", "topic_en": "Creation Stages from Dust",
         "science_ar": "العناصر الكيميائية في جسم الإنسان (كربون، حديد، كالسيوم) موجودة في التربة.", "science_en": "The chemical elements in the human body (carbon, iron, calcium) are found in soil."},
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 86, "verse": 6, "topic_ar": "ماء دافق", "topic_en": "Gushing Fluid — Reproductive Fluid",
         "science_ar": "يصف القرآن السائل المنوي بأنه 'ماء دافق' — وهو وصف دقيق لطبيعة القذف.", "science_en": "The Quran describes reproductive fluid as 'gushing water' — an accurate description of ejaculation."},
        {"category_ar": "🧬 علم الأجنة", "category_en": "🧬 Embryology",
         "surah": 71, "verse": 14, "topic_ar": "الخلق أطواراً", "topic_en": "Creation in Stages",
         "science_ar": "التطور الجنيني يمر بمراحل متعاقبة — مطابق لعلم الأجنة الحديث.", "science_en": "Embryonic development progresses through successive stages — matching modern embryology."},

        # ═══════════════ GEOLOGY ═══════════════
        {"category_ar": "⛰️ علم الجيولوجيا", "category_en": "⛰️ Geology",
         "surah": 78, "verse": 7, "topic_ar": "الجبال كأوتاد", "topic_en": "Mountains as Stakes/Pegs",
         "science_ar": "الجبال لها جذور عميقة (مبدأ التوازن الأيزوستاتي) — كالأوتاد المثبتة.", "science_en": "Mountains have deep roots (isostasy principle) — like pegs anchoring the crust."},
        {"category_ar": "⛰️ علم الجيولوجيا", "category_en": "⛰️ Geology",
         "surah": 27, "verse": 88, "topic_ar": "حركة الجبال", "topic_en": "Mountains Appear Stationary But Move",
         "science_ar": "الجبال تتحرك مع الصفائح التكتونية — تبدو ثابتة لكنها تمر كالسحاب.", "science_en": "Mountains move with tectonic plates — they appear stationary but pass like clouds."},
        {"category_ar": "⛰️ علم الجيولوجيا", "category_en": "⛰️ Geology",
         "surah": 79, "verse": 30, "topic_ar": "دحو الأرض", "topic_en": "Earth Spread Out (Geological Expansion)",
         "science_ar": "القشرة الأرضية انبسطت وامتدت عبر النشاط التكتوني على مدى مليارات السنين.", "science_en": "The Earth's crust spread and extended through tectonic activity over billions of years."},

        # ═══════════════ OCEANOGRAPHY ═══════════════
        {"category_ar": "🌊 علم المحيطات", "category_en": "🌊 Oceanography",
         "surah": 55, "verse": 20, "topic_ar": "الحاجز بين البحرين", "topic_en": "Barrier Between Two Seas",
         "science_ar": "عند التقاء بحرين مختلفين في الملوحة والحرارة، يتشكل حاجز طبيعي يمنع اختلاطهما.", "science_en": "When two seas of different salinity and temperature meet, a natural barrier prevents mixing."},
        {"category_ar": "🌊 علم المحيطات", "category_en": "🌊 Oceanography",
         "surah": 24, "verse": 40, "topic_ar": "الأمواج الداخلية والظلمات", "topic_en": "Internal Waves and Deep Sea Darkness",
         "science_ar": "أعماق المحيطات مظلمة تماماً وفيها أمواج داخلية — لم تُكتشف إلا بالغواصات.", "science_en": "Ocean depths are completely dark with internal waves — only discovered by submarines."},
        {"category_ar": "🌊 علم المحيطات", "category_en": "🌊 Oceanography",
         "surah": 25, "verse": 53, "topic_ar": "الحاجز بين العذب والمالح", "topic_en": "Freshwater-Saltwater Barrier",
         "science_ar": "عند مصبات الأنهار يوجد حاجز بين الماء العذب والمالح — منطقة انتقالية.", "science_en": "At river mouths there is a barrier between fresh and salt water — a transitional zone."},

        # ═══════════════ ATMOSPHERIC SCIENCE ═══════════════
        {"category_ar": "🛡️ علم الغلاف الجوي", "category_en": "🛡️ Atmospheric Science",
         "surah": 21, "verse": 32, "topic_ar": "السماء كسقف محفوظ", "topic_en": "Sky as Protected Ceiling",
         "science_ar": "الغلاف الجوي يحمي الأرض من الإشعاع الكوني والنيازك.", "science_en": "The atmosphere protects Earth from cosmic radiation and meteoroids."},
        {"category_ar": "🛡️ علم الغلاف الجوي", "category_en": "🛡️ Atmospheric Science",
         "surah": 30, "verse": 48, "topic_ar": "تكوين السحب والمطر", "topic_en": "Cloud Formation and Rain",
         "science_ar": "الرياح تبعثر السحب وتدفعها ثم يتراكم الماء ويتجمع حتى ينزل المطر.", "science_en": "Winds scatter and push clouds, then water accumulates until rain falls."},
        {"category_ar": "🛡️ علم الغلاف الجوي", "category_en": "🛡️ Atmospheric Science",
         "surah": 15, "verse": 22, "topic_ar": "الرياح لواقح", "topic_en": "Winds as Pollinators",
         "science_ar": "الرياح تحمل حبوب اللقاح لتلقيح النباتات — دور تلقيحي أساسي.", "science_en": "Winds carry pollen to pollinate plants — an essential pollination role."},

        # ═══════════════ HYDROLOGY ═══════════════
        {"category_ar": "💧 علم المياه", "category_en": "💧 Hydrology",
         "surah": 39, "verse": 21, "topic_ar": "دورة المياه الكاملة", "topic_en": "Complete Water Cycle",
         "science_ar": "الماء ينزل من السماء، يتسرب في الأرض، يخرج كينابيع — الدورة الكاملة.", "science_en": "Water descends from sky, seeps into earth, emerges as springs — the complete cycle."},
        {"category_ar": "💧 علم المياه", "category_en": "💧 Hydrology",
         "surah": 23, "verse": 18, "topic_ar": "تخزين المياه الجوفية", "topic_en": "Groundwater Storage",
         "science_ar": "المياه الجوفية تُخزن في طبقات تحت الأرض — يمكن أن تُفقد إذا نضبت.", "science_en": "Groundwater is stored in underground layers — can be lost if depleted."},
        {"category_ar": "💧 علم المياه", "category_en": "💧 Hydrology",
         "surah": 50, "verse": 9, "topic_ar": "الماء المبارك من السماء", "topic_en": "Blessed Water from the Sky",
         "science_ar": "مياه الأمطار نقية وتنعش الأرض الميتة — دورة المياه كمصدر للحياة.", "science_en": "Rainwater is pure and revives dead earth — the water cycle as a source of life."},

        # ═══════════════ METALLURGY ═══════════════
        {"category_ar": "🧪 علم المعادن", "category_en": "🧪 Metallurgy",
         "surah": 57, "verse": 25, "topic_ar": "الحديد من الفضاء الخارجي", "topic_en": "Iron from Outer Space",
         "science_ar": "الحديد لم يتكون على الأرض — جاء من انفجارات نجمية عبر النيازك. رقم سورة الحديد = 57، والنظير الأكثر شيوعاً للحديد هو Fe-57.", "science_en": "Iron did not form on Earth — it came from stellar explosions via meteorites. Surah Al-Hadid is chapter 57, and the most common iron isotope is Fe-57."},

        # ═══════════════ NEUROSCIENCE ═══════════════
        {"category_ar": "🧠 علم الأعصاب", "category_en": "🧠 Neuroscience",
         "surah": 96, "verse": 16, "topic_ar": "الناصية — الفص الجبهي", "topic_en": "Forelock — Frontal Lobe Function",
         "science_ar": "الفص الجبهي مسؤول عن اتخاذ القرار والتخطيط والكذب.", "science_en": "The frontal lobe is responsible for decision-making, planning, and lying."},
        {"category_ar": "🧠 علم الأعصاب", "category_en": "🧠 Neuroscience",
         "surah": 4, "verse": 56, "topic_ar": "مستقبلات الألم في الجلد", "topic_en": "Pain Receptors in Skin",
         "science_ar": "مستقبلات الألم في الجلد — عندما يحترق الجلد بالكامل يتوقف الألم.", "science_en": "Pain receptors are in the skin — when skin burns completely, pain stops."},

        # ═══════════════ BOTANY ═══════════════
        {"category_ar": "🌱 علم النبات", "category_en": "🌱 Botany",
         "surah": 36, "verse": 36, "topic_ar": "الأزواج في كل الخلق", "topic_en": "Pairs in All Creation",
         "science_ar": "النباتات لها تكاثر جنسي (ذكر وأنثى) — لم يُعرف إلا حديثاً.", "science_en": "Plants have sexual reproduction (male and female) — only recently discovered."},
        {"category_ar": "🌱 علم النبات", "category_en": "🌱 Botany",
         "surah": 51, "verse": 49, "topic_ar": "كل شيء خُلق زوجين", "topic_en": "Everything Created in Pairs",
         "science_ar": "المادة والمادة المضادة، الشحنة الموجبة والسالبة — الازدواجية في كل شيء.", "science_en": "Matter and antimatter, positive and negative charge — duality in everything."},

        # ═══════════════ BIOLOGY ═══════════════
        {"category_ar": "🔬 علم الأحياء", "category_en": "🔬 Biology",
         "surah": 21, "verse": 30, "topic_ar": "الماء أصل كل حي", "topic_en": "Water as Origin of All Life",
         "science_ar": "كل الكائنات الحية تتكون أساساً من الماء — الخلايا تحتوي 70-90% ماء.", "science_en": "All living things are fundamentally made from water — cells contain 70-90% water."},
        {"category_ar": "🔬 علم الأحياء", "category_en": "🔬 Biology",
         "surah": 24, "verse": 45, "topic_ar": "كل دابة خُلقت من ماء", "topic_en": "Every Creature Created from Water",
         "science_ar": "البيولوجيا تؤكد أن الماء أساس كل حياة على الأرض.", "science_en": "Biology confirms water is the basis of all life on Earth."},

        # ═══════════════ ZOOLOGY ═══════════════
        {"category_ar": "🐝 علم الحيوان", "category_en": "🐝 Zoology",
         "surah": 16, "verse": 68, "topic_ar": "النحلة أنثى", "topic_en": "Worker Bees Are Female",
         "science_ar": "القرآن يستخدم صيغة المؤنث للنحل العامل — وعلم الأحياء يؤكد أن كل النحل العامل إناث.", "science_en": "The Quran uses feminine form for worker bees — biology confirms all worker bees are female."},
        {"category_ar": "🐝 علم الحيوان", "category_en": "🐝 Zoology",
         "surah": 16, "verse": 66, "topic_ar": "إنتاج الحليب", "topic_en": "Milk Production from Between Blood and Digestion",
         "science_ar": "الحليب يُنتج في الغدد الثديية من مكونات الدم بعد الهضم — بين فرث ودم.", "science_en": "Milk is produced in mammary glands from blood components after digestion — between excretion and blood."},
        {"category_ar": "🐝 علم الحيوان", "category_en": "🐝 Zoology",
         "surah": 6, "verse": 38, "topic_ar": "الحيوانات أمم أمثالكم", "topic_en": "Animals Are Communities Like You",
         "science_ar": "علم السلوك الحيواني يؤكد أن الحيوانات تعيش في مجتمعات منظمة.", "science_en": "Ethology confirms animals live in organized communities with social structures."},
        {"category_ar": "🐝 علم الحيوان", "category_en": "🐝 Zoology",
         "surah": 27, "verse": 18, "topic_ar": "النمل يتواصل", "topic_en": "Ants Communicate",
         "science_ar": "النمل يتواصل عبر الفيرومونات والأصوات — اكتُشف ذلك حديثاً.", "science_en": "Ants communicate through pheromones and sounds — discovered recently."},
        {"category_ar": "🐝 علم الحيوان", "category_en": "🐝 Zoology",
         "surah": 29, "verse": 41, "topic_ar": "بيت العنكبوت أوهن البيوت", "topic_en": "Spider's Web — Weakest Home",
         "science_ar": "خيوط العنكبوت قوية جداً لكن 'البيت' (الحياة الاجتماعية) ضعيف — الأنثى تأكل الذكر.", "science_en": "Spider silk is strong but the 'home' (social life) is weak — the female often eats the male."},

        # ═══════════════ MEDICINE ═══════════════
        {"category_ar": "⚕️ الطب", "category_en": "⚕️ Medicine",
         "surah": 16, "verse": 69, "topic_ar": "العسل شفاء", "topic_en": "Honey as Medicine",
         "science_ar": "العسل له خصائص مضادة للبكتيريا والفيروسات — يُستخدم في الطب الحديث لعلاج الجروح.", "science_en": "Honey has antibacterial and antiviral properties — used in modern medicine for wound healing."},
        {"category_ar": "⚕️ الطب", "category_en": "⚕️ Medicine",
         "surah": 2, "verse": 219, "topic_ar": "أضرار الخمر", "topic_en": "Harms of Alcohol",
         "science_ar": "الطب الحديث يؤكد أن الكحول يسبب تليف الكبد وأمراض القلب والإدمان.", "science_en": "Modern medicine confirms alcohol causes liver cirrhosis, heart disease, and addiction."},

        # ═══════════════ ASTRONOMY ═══════════════
        {"category_ar": "✨ علم الفلك", "category_en": "✨ Astronomy",
         "surah": 86, "verse": 3, "topic_ar": "النجم الثاقب", "topic_en": "Pulsating Star (Pulsar)",
         "science_ar": "النجوم النابضة (Pulsars) تصدر إشعاعات ثاقبة — اكتُشفت عام 1967.", "science_en": "Pulsars emit piercing radiation — discovered in 1967."},
        {"category_ar": "✨ علم الفلك", "category_en": "✨ Astronomy",
         "surah": 55, "verse": 33, "topic_ar": "السفر عبر الفضاء", "topic_en": "Space Travel Possible with Authority/Knowledge",
         "science_ar": "الآية تشير إلى إمكانية اختراق أقطار السماوات والأرض بسلطان (علم وتكنولوجيا).", "science_en": "The verse suggests penetrating the regions of heavens and earth is possible with authority (science and technology)."},
        {"category_ar": "✨ علم الفلك", "category_en": "✨ Astronomy",
         "surah": 81, "verse": 1, "topic_ar": "انطفاء الشمس", "topic_en": "Sun Will Burn Out",
         "science_ar": "الشمس ستستنفد وقودها النووي وتنطفئ بعد حوالي 5 مليارات سنة.", "science_en": "The Sun will exhaust its nuclear fuel and burn out in about 5 billion years."},
        {"category_ar": "✨ علم الفلك", "category_en": "✨ Astronomy",
         "surah": 25, "verse": 61, "topic_ar": "القمر نور منعكس", "topic_en": "Moon Reflects Light",
         "science_ar": "القرآن يميز بين 'سراج' (الشمس — مصدر ضوء) و'نور' (القمر — ضوء منعكس).", "science_en": "The Quran distinguishes between 'siraj' (Sun — light source) and 'noor' (Moon — reflected light)."},

        # ═══════════════ PHYSICS ═══════════════
        {"category_ar": "⚛️ الفيزياء", "category_en": "⚛️ Physics",
         "surah": 57, "verse": 4, "topic_ar": "النسبية — اليوم عند الله", "topic_en": "Relativity of Time",
         "science_ar": "نظرية النسبية لأينشتاين تؤكد أن الزمن نسبي ويتغير حسب السرعة والجاذبية.", "science_en": "Einstein's relativity confirms time is relative, changing with speed and gravity."},
        {"category_ar": "⚛️ الفيزياء", "category_en": "⚛️ Physics",
         "surah": 10, "verse": 61, "topic_ar": "مثقال ذرة", "topic_en": "Weight of an Atom (Smallest Particle)",
         "science_ar": "مفهوم الذرة كأصغر وحدة لم يُعرف علمياً حتى القرن التاسع عشر.", "science_en": "The concept of the atom as the smallest unit was not scientifically known until the 19th century."},

        # ═══════════════ GEOGRAPHY ═══════════════
        {"category_ar": "🗺️ الجغرافيا", "category_en": "🗺️ Geography",
         "surah": 30, "verse": 3, "topic_ar": "أخفض منطقة على الأرض", "topic_en": "Lowest Point on Earth (Dead Sea)",
         "science_ar": "المنطقة حول البحر الميت هي أخفض نقطة على سطح الأرض (427م تحت سطح البحر).", "science_en": "The Dead Sea area is the lowest point on Earth's surface (427m below sea level)."},
    ]

    # Category colors
    _CAT_COLORS = {
        "🌌": "#1a237e", "🧬": "#b71c1c", "⛰️": "#795548",
        "🌊": "#0091AD", "🛡️": "#2196f3", "💧": "#00838f",
        "🧪": "#455a64", "🧠": "#7b1fa2", "🌱": "#2e7d32",
    }

    st.markdown(f"""
    <div class="insight-box">
        <strong>{SH('📌 عن هذه الصفحة:', '📌 About this page:')}</strong><br>
        {SH(
            'هذه الصفحة تعرض آيات قرآنية تتوافق مع اكتشافات علمية حديثة. '
            'نعرض الآية الأصلية والترجمة والحقيقة العلمية المقابلة. '
            'الهدف ليس إثبات أو نفي — بل عرض البيانات وترك الاستنتاج للقارئ. '
            'هذه حقائق لم تكن معروفة قبل 1400 سنة عندما نزل القرآن.',
            'This page presents Quranic verses that align with modern scientific discoveries. '
            'We show the original verse, translation, and the corresponding scientific fact. '
            'The goal is not to prove or disprove — but to present data and let the reader conclude. '
            'These are facts unknown 1400 years ago when the Quran was revealed.'
        )}
    </div>
    """, unsafe_allow_html=True)

    # Category distribution chart
    section_header("📊 توزيع الإشارات العلمية حسب المجال", "📊 Scientific References by Category")

    cat_counts = Counter(r[f"category_{st.session_state.lang}" if st.session_state.lang != "bi" else "category_en"]
                        for r in SCIENTIFIC_REFS)
    cat_df = pd.DataFrame(list(cat_counts.items()), columns=["category", "count"])
    cat_df = cat_df.sort_values("count", ascending=True)

    fig_cat = px.bar(cat_df, x="count", y="category", orientation="h",
                    color="count", color_continuous_scale=["#D8F3DC", "#1B4332"],
                    text="count")
    fig_cat.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=max(300, len(cat_df) * 40),
        yaxis=dict(tickfont=dict(size=14, family="Amiri"), side="right", title=""),
        xaxis=dict(title=SH("عدد الآيات", "Number of verses"), side="top"),
        coloraxis_showscale=False
    )
    fig_cat.update_traces(textposition="outside")
    st.plotly_chart(fig_cat, use_container_width=True)

    # KPIs
    k1, k2, k3 = st.columns(3)
    k1.metric(SH("إجمالي الإشارات", "Total References"), len(SCIENTIFIC_REFS))
    k2.metric(SH("المجالات العلمية", "Scientific Fields"), len(cat_counts))
    k3.metric(SH("السور المشار إليها", "Surahs Referenced"), len(set(r["surah"] for r in SCIENTIFIC_REFS)))

    # Interactive explorer by category
    st.markdown("---")
    section_header("🔍 استكشف حسب المجال العلمي", "🔍 Explore by Scientific Field")

    categories = list(dict.fromkeys(
        SH(r["category_ar"], r["category_en"]) for r in SCIENTIFIC_REFS
    ))
    sel_cat = st.selectbox(SH("اختر مجالاً", "Select a field"), categories)

    # Filter references
    filtered_refs = [r for r in SCIENTIFIC_REFS
                     if SH(r["category_ar"], r["category_en"]) == sel_cat]

    for ref in filtered_refs:
        # Get the actual verse from our data
        verse_data = df[(df["surah_num"] == ref["surah"]) & (df["verse_num"] == ref["verse"])]

        topic = SH(ref["topic_ar"], ref["topic_en"])
        science = SH(ref["science_ar"], ref["science_en"])
        sci_label = SH('🔬 الحقيقة العلمية:', '🔬 Scientific Fact:')

        # Use expander for each reference — cleaner and avoids HTML rendering issues
        with st.expander(f"📖 {topic} — {ref['surah']}:{ref['verse']}", expanded=True):
            if len(verse_data) > 0:
                v = verse_data.iloc[0]
                st.markdown(f'<div class="arabic-text">{v["arabic"]}</div>', unsafe_allow_html=True)
                st.markdown(f"*{v['english']}*")

            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #f0f7f0, #e8f5e8); padding:15px;
                       border-radius:8px; margin-top:10px; direction:rtl; text-align:right;">
                <strong style="color:#2D6A4F;">{sci_label}</strong><br>
                <span style="font-family:Amiri; line-height:1.8;">{science}</span>
            </div>
            """, unsafe_allow_html=True)

    # Word search in scientific verses
    st.markdown("---")
    section_header("🔗 كلمات علمية في القرآن", "🔗 Scientific Keywords in the Quran")

    st.markdown(SH(
        "ابحث عن كلمات علمية وشاهد أين تظهر في القرآن:",
        "Search for scientific keywords and see where they appear in the Quran:"
    ))

    sci_keywords = {
        SH("ماء", "water"): "ماء",
        SH("أرض", "earth"): "ارض",
        SH("سماء", "sky/heaven"): "سماء",
        SH("نجم", "star"): "نجم",
        SH("قمر", "moon"): "قمر",
        SH("شمس", "sun"): "شمس",
        SH("جبال", "mountains"): "جبل",
        SH("بحر", "sea"): "بحر",
        SH("رياح", "winds"): "ريح",
        SH("نور", "light"): "نور",
        SH("حديد", "iron"): "حديد",
        SH("نطفة", "sperm-drop"): "نطف",
    }

    sci_cols = st.columns(4)
    for i, (display, root) in enumerate(sci_keywords.items()):
        col_idx = i % 4
        with sci_cols[col_idx]:
            if st.button(display, key=f"sci_kw_{i}", use_container_width=True):
                navigate_to("Word Explorer", explore_word=root)
                st.rerun()


# ---------------------------------------------------------------------------
# PAGE: LINGUISTIC ANALYSIS
# ---------------------------------------------------------------------------
elif page == "Linguistic Analysis":
    if st.session_state.nav_history:
        if st.button(L('back'), key="ling_back"):
            go_back()
            st.rerun()

    page_title("🗣️ التحليل اللغوي للقرآن", "🗣️ Linguistic Analysis of the Quran",
               "تحليل الضمائر والأساليب البلاغية والأنماط اللغوية",
               "Pronoun patterns, rhetorical devices, and linguistic structures")

    ling_tab1, ling_tab2, ling_tab3, ling_tab4 = st.tabs([
        SH("👑 ضمائر الذات الإلهية", "👑 Divine Pronouns"),
        SH("❓ الأساليب البلاغية", "❓ Rhetorical Devices"),
        SH("🔤 تحليل الحروف", "🔤 Letter Analysis"),
        SH("📊 إحصائيات لغوية", "📊 Linguistic Statistics"),
    ])

    # ==================================================================
    # TAB 1: DIVINE PRONOUNS — Why does Allah use "We"?
    # ==================================================================
    with ling_tab1:
        section_header("👑 لماذا يستخدم الله ضمير 'نحن'؟", "👑 Why Does Allah Use 'We' (نحن)?")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                '<strong>السؤال الشهير:</strong> لماذا يتحدث الله عن نفسه بصيغة الجمع "نحن" و"نا" أحياناً، '
                'وبصيغة المفرد "أنا" و"إني" أحياناً أخرى؟ هذا يُعرف في اللغة العربية بـ"ضمير التعظيم" — '
                'مثل "نحن" الملكية في الإنجليزية (Royal We). نستخدم البيانات لمعرفة: متى يُستخدم كل ضمير؟ '
                'هل هناك نمط بين السور المكية والمدنية؟',
                '<strong>The famous question:</strong> Why does God refer to Himself as "We" (نحن/نا) sometimes, '
                'and "I" (أنا/إني) other times? This is known in Arabic as the "Majestic Plural" — '
                'like the Royal We in English. We use data to find: when is each pronoun used? '
                'Is there a pattern between Meccan and Medinan surahs?'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Divine pronoun patterns to search for
        # "We" forms: نحن، إنا، نا (suffix)، أنزلنا، خلقنا، جعلنا
        # "I" forms: أنا، إني، إنني
        # "He" forms: هو، إنه
        @st.cache_data
        def analyze_divine_pronouns(_df):
            we_markers = ['انا', 'نحن', 'انزلنا', 'خلقنا', 'جعلنا', 'كتبنا',
                          'ارسلنا', 'اوحينا', 'اعطينا', 'رزقنا', 'هدينا', 'نزلنا',
                          'فتحنا', 'احيينا', 'بعثنا', 'اخرجنا', 'انشانا', 'صرفنا']
            i_markers = ['اني', 'انني']
            he_markers = ['انه', 'هو', 'سبحنه', 'الله']

            results = []
            for _, row in _df.iterrows():
                norm = normalize_arabic(row["arabic"])
                words = re.findall(r'[\u0620-\u064A]+', norm)

                we_count = sum(1 for w in words if any(m in w for m in we_markers))
                i_count = sum(1 for w in words if any(w == m or w.endswith(m) for m in i_markers))
                # Only count "هو" when it's likely referring to God (near الله)
                he_count = sum(1 for w in words if w in ('هو', 'انه'))

                results.append({
                    "surah_num": row["surah_num"],
                    "surah_ar": row["surah_name_ar"],
                    "verse_num": row["verse_num"],
                    "place": row["place"],
                    "we": we_count,
                    "i": i_count,
                    "he": he_count,
                    "arabic": row["arabic"],
                    "english": row["english"],
                })
            return pd.DataFrame(results)

        pronoun_df = analyze_divine_pronouns(df)

        # Overall distribution
        total_we = pronoun_df["we"].sum()
        total_i = pronoun_df["i"].sum()
        total_he = pronoun_df["he"].sum()

        k1, k2, k3 = st.columns(3)
        k1.metric(SH("نحن / نا (الجمع)", "We/Our (Plural)"), f"{total_we:,}")
        k2.metric(SH("أنا / إني (المفرد)", "I/My (Singular)"), f"{total_i:,}")
        k3.metric(SH("هو / إنه (الغائب)", "He/His (Third person)"), f"{total_he:,}")

        # Pie chart
        pron_totals = pd.DataFrame({
            SH("الضمير", "Pronoun"): [SH("نحن (تعظيم)", "We (Majestic)"),
                                       SH("أنا (مفرد)", "I (Singular)"),
                                       SH("هو (غائب)", "He (3rd person)")],
            SH("العدد", "Count"): [total_we, total_i, total_he]
        })
        fig_pron = px.pie(pron_totals, values=SH("العدد", "Count"), names=SH("الضمير", "Pronoun"),
                         color_discrete_sequence=["#2D6A4F", "#D4A574", "#0091AD"],
                         hole=0.4)
        fig_pron.update_traces(textinfo="percent+label", textfont_size=14)
        fig_pron.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              height=350, showlegend=False)
        st.plotly_chart(fig_pron, use_container_width=True)

        # Mecca vs Medina comparison
        st.markdown("---")
        section_header("⚖️ الضمائر: مكة مقابل المدينة", "⚖️ Pronouns: Mecca vs Medina")

        mecca_pron = pronoun_df[pronoun_df["place"] == "Mecca"][["we", "i", "he"]].sum()
        medina_pron = pronoun_df[pronoun_df["place"] == "Medina"][["we", "i", "he"]].sum()
        # Normalize
        mecca_total = mecca_pron.sum()
        medina_total = medina_pron.sum()
        mecca_pct = mecca_pron / mecca_total * 100 if mecca_total > 0 else mecca_pron
        medina_pct = medina_pron / medina_total * 100 if medina_total > 0 else medina_pron

        pron_labels = [SH("نحن", "We"), SH("أنا", "I"), SH("هو", "He")]
        fig_pron_comp = go.Figure()
        fig_pron_comp.add_trace(go.Bar(x=pron_labels, y=mecca_pct.values,
                                       name=SH("مكة", "Mecca"), marker_color=COLORS["mecca"]))
        fig_pron_comp.add_trace(go.Bar(x=pron_labels, y=medina_pct.values,
                                       name=SH("المدينة", "Medina"), marker_color=COLORS["medina"]))
        fig_pron_comp.update_layout(barmode="group",
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                    height=350, yaxis_title=SH("النسبة %", "% Share"),
                                    legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_pron_comp, use_container_width=True)

        # Per-surah pronoun heatmap
        st.markdown("---")
        section_header("🌡️ توزيع الضمائر عبر السور", "🌡️ Pronoun Distribution Across Surahs")

        surah_pron = pronoun_df.groupby(["surah_num", "surah_ar"])[["we", "i", "he"]].sum().reset_index()
        # Normalize per surah
        pron_matrix = surah_pron[["we", "i", "he"]].values
        row_sums = pron_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        pron_pct = pron_matrix / row_sums * 100

        fig_pron_heat = px.imshow(
            pron_pct.T,
            x=surah_pron["surah_num"].tolist(),
            y=pron_labels,
            labels=dict(x=SH("رقم السورة", "Surah #"), y=SH("الضمير", "Pronoun"),
                       color=SH("النسبة %", "% Share")),
            color_continuous_scale=["#FAFDF7", "#2D6A4F", "#1B4332"],
            aspect="auto"
        )
        fig_pron_heat.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                    height=250)
        st.plotly_chart(fig_pron_heat, use_container_width=True)

        # Insight
        we_dominant = "Mecca" if mecca_pct["we"] > medina_pct["we"] else "Medina"
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة:', '💡 Finding:')}</strong><br>
            {SH(
                f'ضمير التعظيم "نحن/نا" يُستخدم بنسبة أعلى في السور {"المكية" if we_dominant == "Mecca" else "المدنية"}. '
                f'هذا يتوافق مع طبيعة الخطاب — السور المكية تركز على عظمة الله وقدرته (لذا يناسبها ضمير التعظيم)، '
                f'بينما السور المدنية تتضمن أحكاماً وتشريعات أكثر تفصيلاً.',
                f'The Majestic Plural "We/Our" is used more in {"Meccan" if we_dominant == "Mecca" else "Medinan"} surahs. '
                f'This aligns with the nature of discourse — Meccan surahs focus on Gods greatness and power '
                f'(fitting the Majestic Plural), while Medinan surahs contain more detailed rulings and legislation.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Sample verses for each pronoun type
        st.markdown("---")
        section_header("📖 أمثلة من الآيات", "📖 Example Verses")

        pron_type = st.radio(
            SH("اختر نوع الضمير", "Select Pronoun Type"),
            [SH("نحن/نا — ضمير التعظيم", "We/Our — Majestic Plural"),
             SH("أنا/إني — المفرد", "I/My — Singular"),
             SH("هو/إنه — الغائب", "He/His — Third Person")],
            horizontal=True, key="pron_sample_radio"
        )

        # Filter verses with the selected pronoun type
        if "نحن" in pron_type or "We" in pron_type:
            sample_verses = pronoun_df[pronoun_df["we"] > 0].head(10)
            highlight_key = "نحن"
        elif "أنا" in pron_type or "I/" in pron_type:
            sample_verses = pronoun_df[pronoun_df["i"] > 0].head(10)
            highlight_key = "اني"
        else:
            sample_verses = pronoun_df[pronoun_df["he"] > 0].head(10)
            highlight_key = "هو"

        st.markdown(f"**{SH(f'وُجدت {len(sample_verses)} آية تحتوي هذا الضمير', f'Found {len(sample_verses)} verses with this pronoun')}**")

        for _, sv in sample_verses.iterrows():
            highlighted = highlight_word_in_verse(sv["arabic"], highlight_key)
            st.markdown(f"""
            <div class="verse-card">
                <strong style='color:#2D6A4F;'>{sv['surah_num']}:{sv['verse_num']} — {sv['surah_ar']}</strong>
                <span style='color:#95D5B2;'> ({sv['place']})</span>
                <div class="arabic-text">{highlighted}</div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================================
    # TAB 2: RHETORICAL DEVICES
    # ==================================================================
    with ling_tab2:
        section_header("❓ الأساليب البلاغية في القرآن", "❓ Rhetorical Devices in the Quran")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                'القرآن يستخدم أساليب بلاغية متنوعة — أسئلة استفهامية، أقسام، أوامر ونواهٍ، تشبيهات. '
                'نحلل الترجمة الإنجليزية لاكتشاف هذه الأنماط كمياً.',
                'The Quran uses diverse rhetorical devices — rhetorical questions, oaths, commands/prohibitions, similes. '
                'We analyse the English translation to detect these patterns quantitatively.'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def analyze_rhetoric(_df):
            results = {
                SH("❓ أسئلة استفهامية", "❓ Rhetorical Questions"): 0,
                SH("⚡ أوامر (قل/افعل)", "⚡ Commands (Say/Do)"): 0,
                SH("🚫 نواهٍ (لا تفعل)", "🚫 Prohibitions (Do not)"): 0,
                SH("🌟 تشبيهات (مثل/كأن)", "🌟 Similes (Like/As)"): 0,
                SH("📢 أقسام (والله/والسماء)", "📢 Oaths (By God/By the sky)"): 0,
                SH("📣 نداءات (يا أيها)", "📣 Vocatives (O you who)"): 0,
            }
            mecca_results = dict.fromkeys(results, 0)
            medina_results = dict.fromkeys(results, 0)

            q_key = SH("❓ أسئلة استفهامية", "❓ Rhetorical Questions")
            cmd_key = SH("⚡ أوامر (قل/افعل)", "⚡ Commands (Say/Do)")
            proh_key = SH("🚫 نواهٍ (لا تفعل)", "🚫 Prohibitions (Do not)")
            sim_key = SH("🌟 تشبيهات (مثل/كأن)", "🌟 Similes (Like/As)")
            oath_key = SH("📢 أقسام (والله/والسماء)", "📢 Oaths (By God/By the sky)")
            voc_key = SH("📣 نداءات (يا أيها)", "📣 Vocatives (O you who)")

            for _, row in _df.iterrows():
                en = row["english"].lower()
                target = mecca_results if row["place"] == "Mecca" else medina_results

                if "?" in row["english"]:
                    results[q_key] += 1
                    target[q_key] += 1
                if any(en.startswith(w) for w in ("say,", "say:", "say ", "say!")):
                    results[cmd_key] += 1
                    target[cmd_key] += 1
                if "do not" in en or "don't" in en or "never" in en:
                    results[proh_key] += 1
                    target[proh_key] += 1
                if " like " in en or " as if " in en or "example" in en or "similitude" in en:
                    results[sim_key] += 1
                    target[sim_key] += 1
                if en.startswith("by ") or en.startswith("by the") or "i swear" in en:
                    results[oath_key] += 1
                    target[oath_key] += 1
                if "o you who" in en or "o mankind" in en or "o people" in en or "o children" in en:
                    results[voc_key] += 1
                    target[voc_key] += 1

            return results, mecca_results, medina_results

        rhet_all, rhet_mecca, rhet_medina = analyze_rhetoric(df)

        # Bar chart
        rhet_df = pd.DataFrame({
            SH("الأسلوب", "Device"): list(rhet_all.keys()),
            SH("العدد", "Count"): list(rhet_all.values())
        }).sort_values(SH("العدد", "Count"), ascending=True)

        count_col = SH("العدد", "Count")
        device_col = SH("الأسلوب", "Device")
        fig_rhet = px.bar(rhet_df, x=count_col, y=device_col, orientation="h",
                         color=count_col, color_continuous_scale=["#D8F3DC", "#1B4332"],
                         text=count_col)
        fig_rhet.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              height=350, coloraxis_showscale=False,
                              yaxis=dict(tickfont=dict(size=13), side="right", title=""),
                              xaxis=dict(title=SH("عدد الآيات", "Verse Count"), side="top"),
                              margin=dict(r=180))
        fig_rhet.update_traces(textposition="outside")
        st.plotly_chart(fig_rhet, use_container_width=True)

        # Mecca vs Medina
        section_header("⚖️ الأساليب: مكة مقابل المدينة", "⚖️ Rhetoric: Mecca vs Medina")

        comp_devices = list(rhet_all.keys())
        fig_rhet_comp = go.Figure()
        fig_rhet_comp.add_trace(go.Bar(y=comp_devices, x=[rhet_mecca[d] for d in comp_devices],
                                       name=SH("مكة", "Mecca"), marker_color=COLORS["mecca"],
                                       orientation="h"))
        fig_rhet_comp.add_trace(go.Bar(y=comp_devices, x=[rhet_medina[d] for d in comp_devices],
                                       name=SH("المدينة", "Medina"), marker_color=COLORS["medina"],
                                       orientation="h"))
        fig_rhet_comp.update_layout(barmode="group",
                                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                    height=350,
                                    yaxis=dict(side="right", tickfont=dict(size=12), title=""),
                                    xaxis=dict(title=SH("العدد", "Count"), side="top"),
                                    margin=dict(r=180),
                                    legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_rhet_comp, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة:', '💡 Finding:')}</strong><br>
            {SH(
                'الأسئلة الاستفهامية أكثر في السور المكية — أداة إقناع وتحدٍ. '
                'النداءات ("يا أيها") أكثر في السور المدنية — لأنها تخاطب المجتمع المسلم المتشكّل. '
                'هذا يعكس التحول من الدعوة الفردية (مكة) إلى بناء المجتمع (المدينة).',
                'Rhetorical questions are more frequent in Meccan surahs — a tool for persuasion and challenge. '
                'Vocatives ("O you who") are more common in Medinan surahs — addressing the forming Muslim community. '
                'This reflects the shift from individual calling (Mecca) to community building (Medina).'
            )}
        </div>
        """, unsafe_allow_html=True)

    # ==================================================================
    # TAB 3: LETTER ANALYSIS — معجزة الواو
    # ==================================================================
    with ling_tab3:
        section_header("🔤 تحليل حروف القرآن", "🔤 Quran Letter Analysis")

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('📌 ما هذا؟', '📌 What is this?')}</strong><br>
            {SH(
                'كل كلمة تتكون من حروف. نحسب كل حرف في القرآن الكريم لنرى: أي حرف هو الأكثر استخداماً؟ '
                'أي حرف هو الأقل؟ وما قصة حرف الواو (و) الذي يربط بين الكلمات والجمل والأفكار؟ '
                'حرف الواو ليس مجرد "و" عادية — بل هو أداة ربط تخلق معنى وتسلسلاً.',
                'Every word is made of letters. We count every letter in the Quran to see: which is most used? '
                'Which is least? And what is the story of the letter Waw (و) that connects words, sentences, and ideas? '
                'The Waw is not just an ordinary "and" — it is a linking tool that creates meaning and flow.'
            )}
        </div>
        """, unsafe_allow_html=True)

        @st.cache_data
        def analyze_letters(_df):
            """Count every Arabic letter across the entire Quran."""
            # Arabic alphabet (28 letters)
            letter_counts = Counter()
            letter_per_surah = {}
            waw_verses = []

            for _, row in _df.iterrows():
                text = row["arabic"]
                # Count only Arabic letters (no diacritics, no spaces)
                for ch in text:
                    if '\u0620' <= ch <= '\u064A' or ch == '\u0671':  # Arabic letter range
                        letter_counts[ch] += 1

                # Track Waw specifically
                waw_count_in_verse = text.count('و')
                if waw_count_in_verse > 0:
                    sn = row["surah_num"]
                    if sn not in letter_per_surah:
                        letter_per_surah[sn] = 0
                    letter_per_surah[sn] += waw_count_in_verse

                # Find verses that START with Waw
                stripped = text.strip()
                if stripped and stripped[0] == 'و':
                    waw_verses.append({
                        "surah_num": row["surah_num"],
                        "surah_ar": row["surah_name_ar"],
                        "verse_num": row["verse_num"],
                        "verse_key": row["verse_key"],
                        "place": row["place"],
                        "arabic": row["arabic"],
                        "english": row["english"],
                    })

            return letter_counts, letter_per_surah, waw_verses

        letter_counts, waw_per_surah, waw_start_verses = analyze_letters(df)

        # Overall letter frequency chart
        section_header("📊 تكرار كل حرف في القرآن", "📊 Frequency of Every Letter")

        total_letters = sum(letter_counts.values())
        top_letters = letter_counts.most_common()
        letter_df = pd.DataFrame(top_letters, columns=[SH("الحرف", "Letter"), SH("التكرار", "Count")])

        # KPIs
        most_letter, most_count = top_letters[0]
        least_letter, least_count = top_letters[-1]
        waw_count = letter_counts.get('و', 0)
        waw_pct = waw_count / total_letters * 100

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(SH("إجمالي الحروف", "Total Letters"), f"{total_letters:,}")
        k2.metric(SH("الحرف الأكثر", "Most Common"), f"{most_letter} ({most_count:,})")
        k3.metric(SH("حرف الواو (و)", "Letter Waw (و)"), f"{waw_count:,}")
        k4.metric(SH("نسبة الواو", "Waw %"), f"{waw_pct:.1f}%")

        # Bar chart of all letters
        fig_letters = px.bar(letter_df, x=SH("الحرف", "Letter"), y=SH("التكرار", "Count"),
                            color=SH("التكرار", "Count"),
                            color_continuous_scale=["#D8F3DC", "#1B4332"],
                            text=SH("التكرار", "Count"))
        fig_letters.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            height=400,
            xaxis=dict(tickfont=dict(size=20, family="Amiri"), title=""),
            yaxis=dict(title=SH("التكرار", "Frequency")),
            coloraxis_showscale=False,
        )
        fig_letters.update_traces(textposition="outside", textfont_size=9)
        st.plotly_chart(fig_letters, use_container_width=True)

        # ---- SPECIAL FOCUS: THE LETTER WAW (و) ----
        st.markdown("---")
        section_header("✨ معجزة الواو — حرف الربط", "✨ The Miracle of Waw — The Linking Letter")

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('لماذا الواو مميزة؟', 'Why is Waw special?')}</strong><br>
            {SH(
                'حرف الواو (و) في العربية ليس مجرد حرف عطف ("و" بمعنى "and"). في القرآن، الواو تأتي بأنواع مختلفة:<br><br>'
                '• <strong>واو العطف:</strong> تربط بين شيئين (السماوات <strong>و</strong>الأرض)<br>'
                '• <strong>واو الحال:</strong> تصف الحالة (<strong>و</strong>هم يعلمون)<br>'
                '• <strong>واو القسم:</strong> للقسم (<strong>و</strong>الفجر، <strong>و</strong>الشمس)<br>'
                '• <strong>واو الاستئناف:</strong> تبدأ جملة جديدة مرتبطة بما قبلها<br><br>'
                'كل هذه الأنواع تخلق نسيجاً مترابطاً يجعل النص يتدفق بسلاسة.',
                'The letter Waw (و) in Arabic is not just a conjunction ("and"). In the Quran, Waw comes in different types:<br><br>'
                '• <strong>Conjunctive Waw:</strong> connects two things (heavens <strong>and</strong> earth)<br>'
                '• <strong>Circumstantial Waw:</strong> describes a state (<strong>while</strong> they know)<br>'
                '• <strong>Oath Waw:</strong> for swearing (<strong>By</strong> the dawn, <strong>By</strong> the sun)<br>'
                '• <strong>Resumptive Waw:</strong> starts a new connected sentence<br><br>'
                'All these types create an interconnected fabric that makes the text flow seamlessly.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # Waw distribution across surahs
        section_header("📈 توزيع الواو عبر السور", "📈 Waw Distribution Across Surahs")

        waw_surah_df = pd.DataFrame([
            {"surah_num": sn, "waw_count": wc}
            for sn, wc in sorted(waw_per_surah.items())
        ])
        if len(waw_surah_df) > 0:
            # Merge with surah names
            surah_names = df.groupby("surah_num").first()[["surah_name_ar", "place"]].reset_index()
            waw_surah_df = waw_surah_df.merge(surah_names, on="surah_num")

            fig_waw = px.bar(waw_surah_df, x="surah_num", y="waw_count",
                            color="place",
                            color_discrete_map={"Mecca": COLORS["mecca"], "Medina": COLORS["medina"]},
                            hover_data={"surah_name_ar": True, "surah_num": False},
                            labels={"surah_num": SH("رقم السورة", "Surah #"),
                                    "waw_count": SH("عدد الواو", "Waw Count")})
            fig_waw.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 height=350, legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig_waw, use_container_width=True)

        # Verses starting with Waw (oath verses)
        st.markdown("---")
        section_header("📖 آيات تبدأ بحرف الواو", "📖 Verses Beginning with Waw")

        st.markdown(f"**{SH(f'{len(waw_start_verses):,} آية تبدأ بالواو', f'{len(waw_start_verses):,} verses start with Waw')}**")
        waw_pct_verses = len(waw_start_verses) / len(df) * 100
        st.markdown(f"**{SH(f'({waw_pct_verses:.1f}% من كل الآيات)', f'({waw_pct_verses:.1f}% of all verses)')}**")

        # Show samples
        waw_sample = waw_start_verses[:10]
        for wv in waw_sample:
            highlighted = highlight_word_in_verse(wv["arabic"], "و")
            st.markdown(f"""
            <div class="verse-card">
                <strong style='color:#2D6A4F;'>{wv['verse_key']} — {wv['surah_ar']}</strong>
                <span style='color:#95D5B2;'> ({wv['place']})</span>
                <div class="arabic-text">{highlighted}</div>
                <div style='color:#555; padding:5px 15px; font-style:italic;'>{wv['english']}</div>
            </div>
            """, unsafe_allow_html=True)

        if len(waw_start_verses) > 10:
            st.info(SH(f"عرض 10 من {len(waw_start_verses)} آية", f"Showing 10 of {len(waw_start_verses)} verses"))

        # Insight
        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة:', '💡 Finding:')}</strong><br>
            {SH(
                f'حرف الواو يظهر {waw_count:,} مرة في القرآن — يشكّل {waw_pct:.1f}% من كل الحروف. '
                f'{len(waw_start_verses):,} آية ({waw_pct_verses:.1f}%) تبدأ بالواو. '
                f'هذا يعكس طبيعة النص القرآني المترابطة — كل آية مرتبطة بما قبلها وما بعدها بحرف واحد.',
                f'The letter Waw appears {waw_count:,} times in the Quran — making up {waw_pct:.1f}% of all letters. '
                f'{len(waw_start_verses):,} verses ({waw_pct_verses:.1f}%) start with Waw. '
                f'This reflects the interconnected nature of Quranic text — each verse linked to what comes before and after by a single letter.'
            )}
        </div>
        """, unsafe_allow_html=True)

        # ═══════════════════════════════════════════════════════════
        # THE REAL WAW MIRACLE — الواو بعد السابعة
        # ═══════════════════════════════════════════════════════════
        st.markdown("---")
        section_header("🌟 معجزة الواو: القاعدة بعد السابعة", "🌟 The Waw Miracle: The Rule After the 7th")

        st.markdown(f"""
        <div class="insight-box" style="border-right:5px solid #D4A574;">
            <strong>{SH('🔑 القاعدة:', '🔑 The Rule:')}</strong><br><br>
            {SH(
                'في اللغة العربية: <strong>الواو لا تُذكر إلا بعد السابعة</strong>.<br><br>'
                'عند عدّ الأشياء بالعربية: واحد، اثنان، ثلاثة، أربعة، خمسة، ستة، سبعة <strong>و</strong>ثمانية.<br>'
                'الواو تأتي فقط بعد العدد السابع. القرآن يطبق هذه القاعدة بدقة مذهلة!',
                'In Arabic: <strong>the Waw (and) is only mentioned after the 7th item</strong>.<br><br>'
                'When counting in Arabic: one, two, three, four, five, six, seven <strong>and</strong> eight.<br>'
                'The Waw comes only after the 7th number. The Quran applies this rule with stunning precision!'
            )}
        </div>
        """, unsafe_allow_html=True)

        # ---- EXAMPLE 1: Hell (7 gates) vs Paradise (8 gates) ----
        section_header("🔥 المثال الأول: أبواب النار والجنة", "🔥 Example 1: Gates of Hell vs Paradise")

        # Fetch the actual verses
        hell_verse = df[(df["surah_num"] == 39) & (df["verse_num"] == 71)]
        paradise_verse = df[(df["surah_num"] == 39) & (df["verse_num"] == 73)]

        col_hell, col_para = st.columns(2)

        with col_hell:
            st.markdown(f"""
            <div style="background:#fce4ec; border-radius:12px; padding:20px; direction:rtl; text-align:right;
                        border:2px solid #B7094C;">
                <h3 style="color:#B7094C; text-align:center;">🔥 {SH('أبواب النار = 7', 'Gates of Hell = 7')}</h3>
                <p style="text-align:center; color:#B7094C; font-weight:bold;">{SH('بدون واو ❌', 'NO Waw ❌')}</p>
                <p style="text-align:center; color:#888; font-size:0.85rem;">39:71</p>
            </div>
            """, unsafe_allow_html=True)
            if len(hell_verse) > 0:
                v = hell_verse.iloc[0]
                # Highlight the key phrase WITHOUT waw
                st.markdown(f'<div class="arabic-text" style="font-size:1.3rem;">{v["arabic"]}</div>', unsafe_allow_html=True)
                st.markdown(f"*{v['english']}*")

            st.markdown(f"""
            <div style="background:#ffebee; padding:12px; border-radius:8px; direction:rtl; text-align:center;
                        font-family:Amiri; font-size:1.2rem; color:#B7094C;">
                حتى إذا جاؤوها <strong style="font-size:1.5rem;">فُتحت</strong> أبوابها
                <br><span style="font-size:0.9rem; color:#888;">{SH('← لا يوجد واو قبل "فُتحت"', '← No Waw before "فُتحت"')}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_para:
            st.markdown(f"""
            <div style="background:#e8f5e9; border-radius:12px; padding:20px; direction:rtl; text-align:right;
                        border:2px solid #2D6A4F;">
                <h3 style="color:#2D6A4F; text-align:center;">🌴 {SH('أبواب الجنة = 8', 'Gates of Paradise = 8')}</h3>
                <p style="text-align:center; color:#2D6A4F; font-weight:bold;">{SH('مع واو ✅', 'WITH Waw ✅')}</p>
                <p style="text-align:center; color:#888; font-size:0.85rem;">39:73</p>
            </div>
            """, unsafe_allow_html=True)
            if len(paradise_verse) > 0:
                v = paradise_verse.iloc[0]
                st.markdown(f'<div class="arabic-text" style="font-size:1.3rem;">{v["arabic"]}</div>', unsafe_allow_html=True)
                st.markdown(f"*{v['english']}*")

            st.markdown(f"""
            <div style="background:#e8f5e9; padding:12px; border-radius:8px; direction:rtl; text-align:center;
                        font-family:Amiri; font-size:1.2rem; color:#2D6A4F;">
                حتى إذا جاؤوها <strong style="font-size:1.5rem; color:#D4A574;">وَ</strong><strong style="font-size:1.5rem;">فُتحت</strong> أبوابها
                <br><span style="font-size:0.9rem; color:#888;">{SH('← الواو موجودة قبل "فُتحت" = بعد السابعة (الباب الثامن)', '← Waw present before "فُتحت" = after the 7th (8th gate)')}</span>
            </div>
            """, unsafe_allow_html=True)

        # ---- EXAMPLE 2: People of the Cave (18:22) ----
        st.markdown("---")
        section_header("🕌 المثال الثاني: أصحاب الكهف", "🕌 Example 2: People of the Cave (18:22)")

        cave_verse = df[(df["surah_num"] == 18) & (df["verse_num"] == 22)]

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                'في سورة الكهف، عند ذكر عدد أصحاب الكهف — القرآن يطبق نفس القاعدة:',
                'In Surah Al-Kahf, when mentioning the number of sleepers — the Quran applies the same rule:'
            )}
        </div>
        """, unsafe_allow_html=True)

        if len(cave_verse) > 0:
            v = cave_verse.iloc[0]
            st.markdown(f'<div class="arabic-text" style="font-size:1.3rem;">{v["arabic"]}</div>', unsafe_allow_html=True)
            st.markdown(f"*{v['english']}*")

        st.markdown(f"""
        <div style="background:white; border:1px solid #D8F3DC; border-radius:12px; padding:20px; margin:15px 0;
                    direction:rtl; text-align:right;">
            <table style="width:100%; font-family:Amiri; font-size:1.1rem; border-collapse:collapse;">
                <tr style="background:#f0f7f0;">
                    <th style="padding:8px; border:1px solid #D8F3DC;">{SH('العدد', 'Count')}</th>
                    <th style="padding:8px; border:1px solid #D8F3DC;">{SH('النص القرآني', 'Quranic Text')}</th>
                    <th style="padding:8px; border:1px solid #D8F3DC;">{SH('واو؟', 'Waw?')}</th>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center;">3</td>
                    <td style="padding:8px; border:1px solid #D8F3DC;">ثلاثة <strong>رابعهم</strong> كلبهم</td>
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center;">5</td>
                    <td style="padding:8px; border:1px solid #D8F3DC;">خمسة <strong>سادسهم</strong> كلبهم</td>
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td>
                </tr>
                <tr style="background:#e8f5e9;">
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center; font-weight:bold;">7</td>
                    <td style="padding:8px; border:1px solid #D8F3DC;">سبعة <strong style="color:#D4A574; font-size:1.3rem;">وَ</strong><strong>ثامنهم</strong> كلبهم</td>
                    <td style="padding:8px; border:1px solid #D8F3DC; text-align:center; color:#2D6A4F; font-size:1.3rem;">✅</td>
                </tr>
            </table>
            <p style="text-align:center; color:#2D6A4F; margin-top:10px; font-weight:bold;">
                {SH('← الواو ظهرت فقط بعد السابعة!', '← The Waw appeared only after the 7th!')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ---- EXAMPLE 3: Attributes in 9:112 ----
        st.markdown("---")
        section_header("📿 المثال الثالث: صفات المؤمنين", "📿 Example 3: Attributes of Believers (9:112)")

        attr_verse = df[(df["surah_num"] == 9) & (df["verse_num"] == 112)]

        if len(attr_verse) > 0:
            v = attr_verse.iloc[0]
            st.markdown(f'<div class="arabic-text" style="font-size:1.3rem;">{v["arabic"]}</div>', unsafe_allow_html=True)
            st.markdown(f"*{v['english']}*")

        st.markdown(f"""
        <div style="background:white; border:1px solid #D8F3DC; border-radius:12px; padding:20px; margin:15px 0;
                    direction:rtl; text-align:right;">
            <table style="width:100%; font-family:Amiri; font-size:1.05rem; border-collapse:collapse;">
                <tr style="background:#f0f7f0;">
                    <th style="padding:6px; border:1px solid #D8F3DC;">#</th>
                    <th style="padding:6px; border:1px solid #D8F3DC;">{SH('الصفة', 'Attribute')}</th>
                    <th style="padding:6px; border:1px solid #D8F3DC;">{SH('واو؟', 'Waw?')}</th>
                </tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">1</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">التائبون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">—</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">2</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">العابدون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">3</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">الحامدون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">4</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">السائحون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">5</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">الراكعون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">6</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">الساجدون</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr><td style="padding:6px; border:1px solid #D8F3DC; text-align:center;">7</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;">الآمرون بالمعروف</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#B7094C;">❌</td></tr>
                <tr style="background:#e8f5e9;">
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; font-weight:bold;">8</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;"><strong style="color:#D4A574; font-size:1.3rem;">وَ</strong>الناهون عن المنكر</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#2D6A4F; font-size:1.2rem;">✅</td></tr>
                <tr style="background:#e8f5e9;">
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; font-weight:bold;">9</td>
                    <td style="padding:6px; border:1px solid #D8F3DC;"><strong style="color:#D4A574; font-size:1.3rem;">وَ</strong>الحافظون لحدود الله</td>
                    <td style="padding:6px; border:1px solid #D8F3DC; text-align:center; color:#2D6A4F; font-size:1.2rem;">✅</td></tr>
            </table>
            <p style="text-align:center; color:#2D6A4F; margin-top:10px; font-weight:bold;">
                {SH('← 7 صفات بدون واو، ثم الواو تظهر من الصفة الثامنة!', '← 7 attributes without Waw, then Waw appears from the 8th!')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Final insight
        st.markdown(f"""
        <div class="insight-box" style="border-right:5px solid #D4A574; background:linear-gradient(135deg, #FFF8E1, #FFF3E0);">
            <strong style="font-size:1.2rem;">{SH('🌟 لماذا هذا مذهل؟', '🌟 Why is this remarkable?')}</strong><br><br>
            {SH(
                'هذه القاعدة اللغوية (الواو بعد السابعة) مطبقة بدقة في كل القرآن. '
                'المذهل أن هذه الواو الصغيرة تكشف معلومات مخفية — مثل عدد أبواب الجنة (8) وأبواب النار (7) — '
                'بمجرد وجود أو غياب حرف واحد. كتاب أُحكمت آياته.',
                'This linguistic rule (Waw after the 7th) is applied precisely throughout the entire Quran. '
                'What is remarkable is that this tiny letter reveals hidden information — like the number of gates '
                'of Paradise (8) vs Hell (7) — by the mere presence or absence of a single letter. '
                'A book whose verses are perfected.'
            )}
        </div>
        """, unsafe_allow_html=True)

    # ==================================================================
    # TAB 4: LINGUISTIC STATISTICS
    # ==================================================================
    with ling_tab4:
        section_header("📊 إحصائيات لغوية شاملة", "📊 Comprehensive Linguistic Statistics")

        @st.cache_data
        def compute_ling_stats(_df):
            stats = {}
            # Unique words
            all_words = []
            for text in _df["arabic"]:
                all_words.extend(tokenize_arabic(text))
            freq = Counter(all_words)

            stats["total_tokens"] = len(all_words)
            stats["unique_words"] = len(freq)
            stats["hapax"] = sum(1 for c in freq.values() if c == 1)

            # Average word length (characters)
            word_lengths = [len(w) for w in all_words]
            stats["avg_word_len"] = np.mean(word_lengths)

            # Longest word
            longest_word = max(freq.keys(), key=len)
            stats["longest_word"] = longest_word
            stats["longest_word_len"] = len(longest_word)

            # Find verse reference for longest word
            longest_word_verse = ""
            for _, row in _df.iterrows():
                norm = normalize_arabic(row["arabic"])
                words = re.findall(r'[\u0620-\u064A]+', norm)
                if longest_word in words:
                    longest_word_verse = row["verse_key"]
                    break
            stats["longest_word_verse"] = longest_word_verse

            # Most common word lengths
            len_freq = Counter(len(w) for w in all_words)
            stats["len_distribution"] = len_freq

            # Verse lengths
            _df_copy = _df.copy()
            _df_copy["wc"] = _df_copy["arabic"].apply(lambda x: len(re.findall(r'[\u0600-\u06FF]+', x)))
            stats["avg_verse_len"] = _df_copy["wc"].mean()
            stats["median_verse_len"] = _df_copy["wc"].median()
            stats["max_verse_len"] = _df_copy["wc"].max()
            stats["min_verse_len"] = _df_copy["wc"].min()

            # Sentences ending with common patterns (rhyme-like endings)
            endings = Counter()
            for text in _df["arabic"]:
                norm = normalize_arabic(text)
                words = re.findall(r'[\u0620-\u064A]+', norm)
                if words:
                    last = words[-1]
                    if len(last) >= 2:
                        endings[last[-2:]] += 1
            stats["top_endings"] = endings.most_common(15)

            return stats

        ling_stats = compute_ling_stats(df)

        # KPI grid
        k1, k2, k3, k4 = st.columns(4)
        k1.metric(SH("إجمالي الكلمات", "Total Words"), f"{ling_stats['total_tokens']:,}")
        k2.metric(SH("كلمات فريدة", "Unique Words"), f"{ling_stats['unique_words']:,}")
        k3.metric(SH("متوسط طول الكلمة", "Avg Word Length"), f"{ling_stats['avg_word_len']:.1f}")
        k4.metric(SH("أطول كلمة", "Longest Word"), f"{ling_stats['longest_word_len']} {SH('حرف', 'chars')}")
        st.markdown(f"""<div class="arabic-text" style="text-align:center; font-size:1.1rem; margin-top:-10px;">
            {ling_stats['longest_word']}
            <span style="color:#95D5B2; font-size:0.85rem;"> ({ling_stats['longest_word_verse']})</span>
        </div>""", unsafe_allow_html=True)

        k5, k6, k7, k8 = st.columns(4)
        k5.metric(SH("متوسط طول الآية", "Avg Verse Length"), f"{ling_stats['avg_verse_len']:.1f}")
        k6.metric(SH("وسيط طول الآية", "Median Verse Length"), f"{ling_stats['median_verse_len']:.0f}")
        k7.metric(SH("أطول آية (كلمات)", "Longest Verse"), f"{ling_stats['max_verse_len']}")
        k8.metric(SH("أقصر آية (كلمات)", "Shortest Verse"), f"{ling_stats['min_verse_len']}")

        # Word length distribution
        st.markdown("---")
        section_header("📏 توزيع أطوال الكلمات", "📏 Word Length Distribution")

        len_data = pd.DataFrame(list(ling_stats["len_distribution"].items()),
                               columns=[SH("طول الكلمة", "Word Length"), SH("العدد", "Count")])
        len_data = len_data.sort_values(SH("طول الكلمة", "Word Length"))

        fig_len = px.bar(len_data, x=SH("طول الكلمة", "Word Length"), y=SH("العدد", "Count"),
                        color=SH("العدد", "Count"), color_continuous_scale=["#D8F3DC", "#1B4332"],
                        text=SH("العدد", "Count"))
        fig_len.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                             height=350, coloraxis_showscale=False)
        fig_len.update_traces(textposition="outside")
        st.plotly_chart(fig_len, use_container_width=True)

        # Verse ending patterns (rhyme analysis)
        st.markdown("---")
        section_header("🎵 أنماط نهايات الآيات (الفواصل)", "🎵 Verse Ending Patterns (Rhyme)")

        st.markdown(f"""
        <div class="insight-box">
            {SH(
                'الفواصل القرآنية هي الحروف الأخيرة من كل آية — تشبه القافية في الشعر. '
                'هذا الجدول يُظهر أكثر أنماط النهايات تكراراً.',
                'Quranic verse endings (Fawasil) are the last letters of each verse — similar to rhyme in poetry. '
                'This table shows the most common ending patterns.'
            )}
        </div>
        """, unsafe_allow_html=True)

        endings_df = pd.DataFrame(ling_stats["top_endings"],
                                 columns=[SH("النهاية", "Ending"), SH("التكرار", "Count")])
        endings_df.index = range(1, len(endings_df) + 1)

        col_end1, col_end2 = st.columns([2, 3])
        with col_end1:
            st.dataframe(endings_df, use_container_width=True)
        with col_end2:
            fig_end = px.bar(endings_df.iloc[::-1],
                            x=SH("التكرار", "Count"), y=SH("النهاية", "Ending"),
                            orientation="h", color=SH("التكرار", "Count"),
                            color_continuous_scale=["#D4A574", "#B7094C"])
            fig_end.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                 height=400, coloraxis_showscale=False,
                                 yaxis=dict(tickfont=dict(size=18, family="Amiri"), side="right", title=""),
                                 xaxis=dict(title=SH("التكرار", "Count"), side="top"),
                                 margin=dict(r=80))
            fig_end.update_traces(textposition="outside")
            st.plotly_chart(fig_end, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
            <strong>{SH('💡 نتيجة:', '💡 Finding:')}</strong><br>
            {SH(
                'النهايات الأكثر شيوعاً تعكس أنماطاً صوتية متناسقة — '
                'مما يخلق إيقاعاً موسيقياً عند التلاوة. هذا الإيقاع ليس عشوائياً بل يتبع قواعد بلاغية دقيقة.',
                'The most common endings reflect harmonious sound patterns — '
                'creating a musical rhythm during recitation. This rhythm is not random but follows precise rhetorical rules.'
            )}
        </div>
        """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# PAGE: SEARCH
# ---------------------------------------------------------------------------
elif page == "Search":
    page_title("🔍 البحث في الآيات", "🔍 Verse Search", "البحث في النص العربي والترجمات الإنجليزية", "Search across Arabic text and English translations")

    search_lang = st.radio(SH("البحث في", "Search in"), [SH("عربي", "Arabic"), SH("إنجليزي", "English")],
                           horizontal=True)

    is_arabic_search = search_lang in ("Arabic", "عربي")

    if is_arabic_search:
        # Show Arabic virtual keyboard
        with st.expander(SH("⌨️ لوحة مفاتيح عربية", "⌨️ Arabic Keyboard"), expanded=False):
            kb_text = arabic_keyboard("search_kb")
        query = st.text_input(SH("🔍 أدخل كلمة البحث", "🔍 Enter search term"),
                             value=st.session_state.get("search_kb_text", ""),
                             placeholder="الرحمة")
    else:
        query = st.text_input(SH("🔍 أدخل كلمة البحث", "🔍 Enter search term"),
                             placeholder="mercy")

    if query:
        if search_lang in ("Arabic", "عربي"):
            # Root-aware Arabic search — matches derived forms
            search_mode = st.radio(
                SH("نوع البحث", "Search Mode"),
                [SH("🔍 بحث بالجذر (يجد كل المشتقات)", "🔍 Root search (finds all derivatives)"),
                 SH("🎯 بحث مطابق (الكلمة بالضبط)", "🎯 Exact match")],
                horizontal=True, key="search_mode_radio"
            )
            is_root_search = "جذر" in search_mode or "Root" in search_mode

            normalized_query = normalize_arabic(query)
            if is_root_search:
                # Root search: check if the normalized query is a SUBSTRING of any word
                def _root_match(verse_text):
                    norm = normalize_arabic(verse_text)
                    words = re.findall(r'[\u0620-\u064A]+', norm)
                    return any(normalized_query in w for w in words)
                mask = df["arabic"].apply(_root_match)
            else:
                mask = df["arabic"].apply(lambda x: normalized_query in normalize_arabic(x))
        else:
            mask = df["english"].str.contains(query, case=False, na=False)

        results = df[mask]
        st.markdown(f"**{SH(f'وُجدت {len(results)} آية', f'Found {len(results)} verses')}**")

        # Filter by surah
        if len(results) > 0:
            surah_filter = st.multiselect(
                SH("تصفية حسب السورة", "Filter by Surah"),
                options=results["surah_name_ar"].unique().tolist(),
                default=None
            )
            if surah_filter:
                results = results[results["surah_name_ar"].isin(surah_filter)]

            # Distribution chart
            if len(results) > 1:
                dist = results.groupby(["surah_num", "surah_name_ar"]).size().reset_index(name="count")
                dist = dist.nlargest(20, "count")
                make_rtl_bar_chart(dist, "surah_name_ar", "count",
                                  height=max(350, len(dist) * 25))

            # Paginated results
            st.markdown("---")
            total_results = len(results)
            SEARCH_PAGE_SIZE = 50
            total_search_pages = max(1, (total_results + SEARCH_PAGE_SIZE - 1) // SEARCH_PAGE_SIZE)

            sp_col1, sp_col2, sp_col3 = st.columns([2, 3, 2])
            with sp_col1:
                st.markdown(f"**{SH(f'{total_results} نتيجة', f'{total_results} results')}**")
            with sp_col2:
                search_page = st.number_input(
                    SH(f"الصفحة (1–{total_search_pages})", f"Page (1–{total_search_pages})"),
                    min_value=1, max_value=total_search_pages, value=1, step=1,
                    key="search_page"
                )
            with sp_col3:
                st.markdown(f"**{SH(f'صفحة {search_page} من {total_search_pages}', f'Page {search_page} of {total_search_pages}')}**")

            s_start = (search_page - 1) * SEARCH_PAGE_SIZE
            s_end = min(s_start + SEARCH_PAGE_SIZE, total_results)

            for _, row in results.iloc[s_start:s_end].iterrows():
                st.markdown(f"""
                <div class="verse-card">
                    <strong style='color:#2D6A4F;'>{row['verse_key']} — {row['surah_name_ar']} | {row['surah_name_en']}</strong>
                    <span style='color:#95D5B2; font-size:0.85rem;'> ({row['place']})</span>
                    <div class="arabic-text">{row['arabic']}</div>
                    <div style='color:#555; padding:5px 15px; font-style:italic;'>{row['english']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(f"<div style='text-align:center; color:#95D5B2; padding:10px;'>"
                        f"{SH(f'عرض {s_start+1}–{s_end} من {total_results}', f'Showing {s_start+1}–{s_end} of {total_results}')}</div>",
                        unsafe_allow_html=True)
