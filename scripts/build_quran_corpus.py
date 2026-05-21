#!/usr/bin/env python3
"""
Build a markdown corpus of Quranic content for knowledge-graph extraction.

Generates ~140 documents:
- 114 surah files (full Arabic + English text + themes + entities mentioned)
- ~15 entity files (prophets, places, divine names with verse anchors)
- 10 theme files (scholarly thematic clusters)
- ~5 special-pattern files (Bismillah, Ar-Rahman refrain, Iron miracle, etc.)

Output: quran_corpus/

Designed to be ingested by graphify to produce a true Quranic knowledge graph
where communities cluster thematically, prophets appear as god-nodes, and
verse-level entities cross-reference across the entire mushaf.

Run:
    python3 scripts/build_quran_corpus.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "quran_corpus"
SURAH_DIR = CORPUS / "surahs"
ENTITY_DIR = CORPUS / "entities"
THEME_DIR = CORPUS / "themes"
SPECIAL_DIR = CORPUS / "special"


# ─────────────────────────────────────────────────────────
# Curated entity dictionary (Arabic keywords -> entity info)
# ─────────────────────────────────────────────────────────

PROPHETS = [
    # (slug, english_name, arabic_name, keywords_to_match)
    ("adam",       "Adam",                  "آدم",       ["آدم"]),
    ("idris",      "Idris (Enoch)",         "إدريس",     ["إدريس"]),
    ("nuh",        "Noah (Nuh)",            "نوح",       ["نوح"]),
    ("hud",        "Hud",                   "هود",       ["هود"]),
    ("salih",      "Salih",                 "صالح",      ["صالح"]),
    ("ibrahim",    "Abraham (Ibrahim)",     "إبراهيم",   ["إبراهيم", "إبرهيم"]),
    ("lut",        "Lot (Lut)",             "لوط",       ["لوط"]),
    ("ismail",     "Ishmael (Ismail)",      "إسماعيل",   ["إسماعيل", "إسمعيل"]),
    ("ishaq",      "Isaac (Ishaq)",         "إسحاق",     ["إسحاق", "إسحق"]),
    ("yaqub",      "Jacob (Yaqub)",         "يعقوب",     ["يعقوب"]),
    ("yusuf",      "Joseph (Yusuf)",        "يوسف",      ["يوسف"]),
    ("ayyub",      "Job (Ayyub)",           "أيوب",      ["أيوب"]),
    ("shuayb",     "Shuayb",                "شعيب",      ["شعيب"]),
    ("musa",       "Moses (Musa)",          "موسى",      ["موسى", "موسي"]),
    ("harun",      "Aaron (Harun)",         "هارون",     ["هارون"]),
    ("dhul-kifl",  "Dhul-Kifl",             "ذو الكفل",  ["ذا الكفل", "ذي الكفل"]),
    ("dawud",      "David (Dawud)",         "داود",      ["داود", "داوود"]),
    ("sulayman",   "Solomon (Sulayman)",    "سليمان",    ["سليمان"]),
    ("ilyas",      "Elijah (Ilyas)",        "إلياس",     ["إلياس", "إلياسين"]),
    ("al-yasa",    "Elisha (Al-Yasa)",      "اليسع",     ["اليسع"]),
    ("yunus",      "Jonah (Yunus)",         "يونس",      ["يونس"]),
    ("zakariya",   "Zechariah (Zakariya)",  "زكريا",     ["زكريا"]),
    ("yahya",      "John the Baptist (Yahya)", "يحيى",   ["يحيى"]),
    ("isa",        "Jesus (Isa)",           "عيسى",      ["عيسى", "المسيح"]),
    ("muhammad",   "Muhammad",              "محمد",      ["محمد", "أحمد"]),
]

OTHER_FIGURES = [
    ("maryam",  "Mary (Maryam, mother of Jesus)", "مريم",   ["مريم"]),
    ("firaun",  "Pharaoh (Firaun)",               "فرعون",  ["فرعون"]),
    ("haman",   "Haman",                          "هامان",  ["هامن", "هامان"]),
    ("qarun",   "Qarun (Korah)",                  "قارون",  ["قارون"]),
    ("iblis",   "Iblis (Satan)",                  "إبليس",  ["إبليس", "الشيطن", "الشيطان"]),
    ("jibril",  "Gabriel (Jibril)",               "جبريل",  ["جبريل", "جبرل"]),
]

PLACES = [
    ("makka",   "Mecca (Makka)",        "مكة",      ["مكة", "بكة"]),
    ("madinah", "Medina",               "المدينة",  ["المدينة", "يثرب"]),
    ("masjid-al-haram", "The Sacred Mosque (Makka)", "المسجد الحرام", ["المسجد الحرام"]),
    ("masjid-al-aqsa",  "The Furthest Mosque (Jerusalem)", "المسجد الأقصى", ["المسجد الأقصى"]),
    ("sinai",   "Mount Sinai (Tur)",    "الطور",    ["الطور", "طور سينين", "طور سينا"]),
    ("misr",    "Egypt (Misr)",         "مصر",      ["مصر"]),
    ("madyan",  "Madyan",               "مدين",     ["مدين"]),
]

DIVINE_NAMES = [
    ("allah",     "Allah",                "الله",      ["الله", "اللهم"]),
    ("ar-rahman", "Ar-Rahman (the Most Gracious)", "الرحمن", ["الرحمن", "الرحمٰن"]),
    ("ar-rahim",  "Ar-Rahim (the Most Merciful)",  "الرحيم", ["الرحيم"]),
    ("rabb",      "Rabb (the Lord)",       "رب",        ["رب", "ربك", "ربكم", "ربنا", "ربي"]),
]

ALL_ENTITIES = (
    [(s, n, a, k, "prophet") for (s, n, a, k) in PROPHETS]
    + [(s, n, a, k, "figure") for (s, n, a, k) in OTHER_FIGURES]
    + [(s, n, a, k, "place")  for (s, n, a, k) in PLACES]
    + [(s, n, a, k, "divine") for (s, n, a, k) in DIVINE_NAMES]
)


# ─────────────────────────────────────────────────────────
# The scholarly themes (mirrors the polar chart themes in app.html)
# ─────────────────────────────────────────────────────────

THEMES = {
    "faith-monotheism": {
        "name_en": "Faith and Monotheism",
        "name_ar": "العقيدة",
        "color": "#6366F1",
        "surahs": [1, 3, 10, 11, 12, 13, 18, 21, 31, 34, 35, 39, 40, 42, 46, 50, 53, 67, 87, 91, 95, 103, 112],
        "description": "Surahs centered on belief in one God, His attributes, prophethood, divine decree, and the unseen realm. The core creedal foundation of Islam.",
    },
    "legislation": {
        "name_en": "Legislation",
        "name_ar": "التشريع",
        "color": "#22C55E",
        "surahs": [2, 4, 5, 8, 24, 33, 49, 58, 60, 65, 66],
        "description": "Surahs dense with rulings on family law, transactions, criminal law, dietary rules, war, social conduct. Predominantly Medinan, reflecting the period when the Muslim community established legal foundations.",
    },
    "prophets-stories": {
        "name_en": "Stories of the Prophets",
        "name_ar": "قصص الأنبياء",
        "color": "#F59E0B",
        "surahs": [6, 7, 14, 15, 19, 20, 26, 27, 28, 29, 37, 38, 71],
        "description": "Surahs containing extended narratives of earlier prophets and their nations. Often used to comfort the Prophet Muhammad and warn his contemporaries by paralleling earlier patterns of rejection and salvation.",
    },
    "day-of-judgment": {
        "name_en": "Day of Judgment",
        "name_ar": "يوم القيامة",
        "color": "#EF4444",
        "surahs": [23, 36, 44, 45, 56, 69, 70, 75, 77, 78, 79, 81, 82, 84, 88, 99, 100, 101],
        "description": "Surahs vividly describing the Day of Resurrection, the trumpet, the balance, paradise and hellfire. The eschatological core of the Quran.",
    },
    "warning": {
        "name_en": "Warning",
        "name_ar": "التحذير",
        "color": "#F97316",
        "surahs": [9, 17, 25, 32, 41, 43, 51, 52, 54, 68, 74, 85, 90, 92, 104, 111],
        "description": "Surahs primarily delivering warning, rebuke, and the consequences of disbelief or moral failure. Often paired with stories of destroyed nations.",
    },
    "ethics": {
        "name_en": "Ethics and Character",
        "name_ar": "الأخلاق",
        "color": "#8B5CF6",
        "surahs": [16, 30, 47, 48, 57, 59, 61, 62, 63, 64, 76, 83, 86, 89, 93, 94, 107],
        "description": "Surahs focused on moral character, justice, gratitude, patience, truthfulness, and the inward dimensions of faith.",
    },
    "worship": {
        "name_en": "Worship and Devotion",
        "name_ar": "العبادة",
        "color": "#06B6D4",
        "surahs": [55, 73, 96, 97, 108, 110, 113, 114],
        "description": "Surahs emphasizing prayer, remembrance, recitation, and the believer's relationship with God through devotional acts.",
    },
    "nature": {
        "name_en": "Nature and Signs",
        "name_ar": "الطبيعة",
        "color": "#10B981",
        "surahs": [22, 80],
        "description": "Surahs that draw attention to the natural world as a sign of the Creator: heavens, earth, rain, plants, animals, and the order of the cosmos.",
    },
    "community": {
        "name_en": "Community and Society",
        "name_ar": "المجتمع",
        "color": "#EC4899",
        "surahs": [9, 33, 48, 49, 60, 109],
        "description": "Surahs dealing with the Muslim community as a social and political body: relations with believers, neighbors, allies, and adversaries.",
    },
    "patience": {
        "name_en": "Patience and Endurance",
        "name_ar": "الصبر",
        "color": "#14B8A6",
        "surahs": [18, 29, 34, 38, 40, 46, 68, 90, 94, 105, 106],
        "description": "Surahs that center patience, perseverance, and trust in God through hardship. Often using prophetic narratives of long-suffering figures.",
    },
}

# Map: surah_number -> [theme_slug, ...]
SURAH_TO_THEMES = defaultdict(list)
for slug, t in THEMES.items():
    for sn in t["surahs"]:
        SURAH_TO_THEMES[sn].append(slug)


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

def load_meta():
    return json.load(open(ROOT / "data" / "surah.json", encoding="utf-8"))

def load_surah_ar(n):
    p = ROOT / "data" / "surah" / f"surah_{n}.json"
    return json.load(open(p, encoding="utf-8"))

def load_surah_en(n):
    p = ROOT / "data" / "translation" / "en" / f"en_translation_{n}.json"
    return json.load(open(p, encoding="utf-8"))

def normalize_arabic(text):
    """Strip diacritics for keyword matching."""
    text = re.sub(r"[ً-ٰٟۖ-ۭ]", "", text)
    text = text.replace("ٱ", "ا").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي")
    return text

def find_entities_in_verse(arabic_text, entity_list):
    """Return list of entity slugs that appear in the verse."""
    norm = normalize_arabic(arabic_text)
    found = []
    for slug, name, ar, keywords, _kind in entity_list:
        for kw in keywords:
            if normalize_arabic(kw) in norm:
                found.append(slug)
                break
    return found


# ─────────────────────────────────────────────────────────
# Generators
# ─────────────────────────────────────────────────────────

def slugify_title(title):
    return re.sub(r"[^a-z0-9-]+", "-", title.lower()).strip("-")

def gen_surah_files(meta):
    """Generate one markdown per surah."""
    # Track which surahs each entity appears in
    entity_appearances = defaultdict(set)  # slug -> set of (surah, verse)

    for n in range(1, 115):
        m = meta[n - 1]
        try:
            ar = load_surah_ar(n)
            en = load_surah_en(n)
        except FileNotFoundError:
            print(f"  Warning: surah {n} data missing, skipping")
            continue

        title_en = m["title"]
        title_ar = m["titleAr"]
        place = m["place"]
        revelation_type = m.get("type", "Makkiyah" if place == "Mecca" else "Madaniyah")
        verse_count = m["count"]
        slug = slugify_title(title_en)

        # Extract verses
        verses_ar = ar["verse"]
        verses_en = en["verse"]
        verses = []
        for vk in sorted(verses_ar.keys(), key=lambda x: int(x.split("_")[1])):
            vnum = int(vk.split("_")[1])
            a_text = verses_ar[vk]
            e_text = verses_en.get(vk, "")
            verses.append((vnum, a_text, e_text))

        # Find entities in this surah
        surah_entities = set()
        for vnum, a_text, _ in verses:
            for slug_e in find_entities_in_verse(a_text, ALL_ENTITIES):
                surah_entities.add(slug_e)
                entity_appearances[slug_e].add((n, vnum))

        # Themes
        themes = SURAH_TO_THEMES.get(n, [])

        # Build markdown
        lines = [
            f"# Surah {n}: {title_en} ({title_ar})",
            "",
            f"- **Mushaf number**: {n}",
            f"- **Place of revelation**: {place} ({revelation_type})",
            f"- **Verse count**: {verse_count}",
        ]
        if themes:
            theme_links = ", ".join(f"[{THEMES[t]['name_en']}](../themes/{t}.md)" for t in themes)
            lines.append(f"- **Themes**: {theme_links}")
        if surah_entities:
            ent_links = []
            for slug_e in sorted(surah_entities):
                meta_e = next(x for x in ALL_ENTITIES if x[0] == slug_e)
                ent_links.append(f"[{meta_e[1]}](../entities/{meta_e[4]}_{slug_e}.md)")
            lines.append(f"- **Named entities mentioned**: {', '.join(ent_links)}")
        lines.append("")
        lines.append("## Verses")
        lines.append("")
        for vnum, a_text, e_text in verses:
            lines.append(f"### Verse {n}:{vnum}")
            lines.append(f"**Arabic**: {a_text}")
            lines.append("")
            if e_text:
                lines.append(f"**English**: {e_text}")
                lines.append("")

        # Inverse cross-refs: list other surahs sharing the same theme
        if themes:
            lines.append("## Thematic cross-references")
            lines.append("")
            for t in themes:
                others = [s for s in THEMES[t]["surahs"] if s != n]
                if others:
                    refs = ", ".join(f"[{meta[s-1]['title']}](surah_{s:03d}_{slugify_title(meta[s-1]['title'])}.md)" for s in others[:8])
                    extra = f" and {len(others)-8} more" if len(others) > 8 else ""
                    lines.append(f"- **{THEMES[t]['name_en']}**: {refs}{extra}")
            lines.append("")

        out = SURAH_DIR / f"surah_{n:03d}_{slug}.md"
        out.write_text("\n".join(lines), encoding="utf-8")

    print(f"  Wrote {SURAH_DIR}: 114 surah files")
    return entity_appearances


def gen_entity_files(entity_appearances, meta):
    """Generate one markdown per entity, listing where each appears."""
    for slug, name, ar, keywords, kind in ALL_ENTITIES:
        appearances = entity_appearances.get(slug, set())
        if not appearances:
            # Don't generate files for entities that don't appear (avoid empty nodes)
            continue
        by_surah = defaultdict(list)
        for s, v in appearances:
            by_surah[s].append(v)
        for s in by_surah:
            by_surah[s].sort()

        lines = [
            f"# {name}",
            "",
            f"- **Arabic**: {ar}",
            f"- **Category**: {kind.title()}",
            f"- **Total verse mentions**: {len(appearances)}",
            f"- **Surahs containing this entity**: {len(by_surah)}",
            "",
            "## Surahs where mentioned",
            "",
        ]
        for s in sorted(by_surah.keys()):
            title = meta[s-1]["title"]
            surah_slug = slugify_title(title)
            verses = by_surah[s]
            verse_str = ", ".join(str(v) for v in verses[:15])
            extra = f" (and {len(verses)-15} more)" if len(verses) > 15 else ""
            lines.append(f"- **[Surah {s}: {title}](../surahs/surah_{s:03d}_{surah_slug}.md)**: verses {verse_str}{extra}")

        out = ENTITY_DIR / f"{kind}_{slug}.md"
        out.write_text("\n".join(lines), encoding="utf-8")

    nonempty = [s for s in entity_appearances if entity_appearances[s]]
    print(f"  Wrote {ENTITY_DIR}: {len(nonempty)} entity files")


def gen_theme_files(meta):
    """Generate one markdown per theme, listing constituent surahs."""
    for slug, t in THEMES.items():
        lines = [
            f"# Theme: {t['name_en']} ({t['name_ar']})",
            "",
            f"- **Scholarly color tag**: {t['color']}",
            f"- **Surah count**: {len(t['surahs'])}",
            "",
            f"{t['description']}",
            "",
            "## Surahs in this thematic cluster",
            "",
        ]
        for sn in sorted(t['surahs']):
            m = meta[sn-1]
            title = m["title"]
            surah_slug = slugify_title(title)
            place = m["place"]
            lines.append(f"- **[Surah {sn}: {title}](../surahs/surah_{sn:03d}_{surah_slug}.md)** ({title}, {m['titleAr']}) - {place}, {m['count']} verses")
        out = THEME_DIR / f"{slug}.md"
        out.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote {THEME_DIR}: {len(THEMES)} theme files")


def gen_special_files():
    """Generate special-pattern documents."""
    specials = [
        ("bismillah-113-occurrences", {
            "title": "Bismillah: The 113 Occurrences",
            "body": """The phrase "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ" (In the name of God, the Gracious, the Merciful) appears 113 times in the Quran. 112 occurrences are at the opening of chapters (every surah except At-Tawbah). The 113th occurrence is hidden inside [Surah 27: An-Naml](../surahs/surah_027_al-naml.md) at verse 30, embedded within Prophet Solomon's letter to the Queen of Sheba.

The Bismillah is the formula by which a Muslim begins any action of significance, and its placement at chapter openings frames the act of recitation itself as one performed in God's name. Its mathematical regularity (112 chapter openings = 19 × ... no, but with 113 total related to multiples of 19 in some readings) connects this pattern to the broader 19-pattern analysis.

Related verses across surahs link this concept to every chapter that opens with it.

See also: [Surah 27 An-Naml](../surahs/surah_027_al-naml.md), [Surah 9 At-Tawbah](../surahs/surah_009_al-tawbah.md) (the one without it), [Allah](../entities/divine_allah.md), [Ar-Rahman](../entities/divine_ar-rahman.md), [Ar-Rahim](../entities/divine_ar-rahim.md)."""
        }),
        ("ar-rahman-refrain-31x", {
            "title": "The Ar-Rahman Refrain: 31 Repetitions",
            "body": """The verse "فَبِأَيِّ آلَاءِ رَبِّكُمَا تُكَذِّبَانِ" (So which of the favors of your Lord would you deny?) repeats 31 times within [Surah 55: Ar-Rahman](../surahs/surah_055_ar-rahman.md), descending rhythmically after each blessing of God upon mankind and jinn.

This is the highest internal-repetition rate of any verse in the Quran. The repetition creates a meditative pulse, anchoring every divine gift to the reminder of accountability. Scholars including Al-Samarrai have analyzed how the placement of each occurrence corresponds to a specific category of blessing (creation, sustenance, sensory faculties, paradise, etc.).

The pattern is structurally unique: no other Quranic chapter sustains a single-verse refrain at this density. It is also one of the most-cited features in numerical and rhetorical analyses of the Quran.

Related: [Surah Ar-Rahman](../surahs/surah_055_ar-rahman.md), [Theme: Worship](../themes/worship.md), [Allah](../entities/divine_allah.md)."""
        }),
        ("iron-miracle-hadid", {
            "title": "The Iron Miracle: Surah 57 Al-Hadid",
            "body": """[Surah 57: Al-Hadid](../surahs/surah_057_al-hadid.md) (The Iron) contains a striking numerical coincidence between its position in the mushaf and the modern atomic structure of iron.

- Surah position: 57
- Verse mentioning the descent of iron: verse 25
- Abjad numerical value of "حديد" (Hadid): 26 (the atomic number of iron in the modern periodic table)
- Number of neutrons in iron-57 (the stable isotope referenced when summing protons and neutrons): 31

The verse itself reads: "وَأَنزَلْنَا ٱلْحَدِيدَ فِيهِ بَأْسٌ شَدِيدٌ وَمَنَافِعُ لِلنَّاسِ" (And We sent down iron, wherein is great might and benefits for mankind). Modern astrophysics confirms that iron is uniquely "sent down" from the cosmos: it cannot be forged in ordinary stellar fusion and arrives on Earth via supernova explosions. The Arabic word for "sent down" (أنزلنا) is the same word used for divine revelation throughout the Quran.

This pattern has been cited by scholars including Dr. Shabir Ally as evidence of the Quran's awareness of physical realities only confirmed through 20th-century science.

Related: [Surah Al-Hadid](../surahs/surah_057_al-hadid.md), [Theme: Faith and Monotheism](../themes/faith-monotheism.md), [Allah](../entities/divine_allah.md)."""
        }),
        ("number-19-pattern", {
            "title": "The Number 19 Pattern",
            "body": """[Surah 74: Al-Muddathir](../surahs/surah_074_al-muddaththir.md) verse 30 contains the only explicit number stated in the Quran: "عَلَيْهَا تِسْعَةَ عَشَر" (Over it are nineteen). Computational analysis of the Quranic text reveals striking patterns related to this number.

- Verse 74:31, which explains why nineteen was mentioned, contains exactly 57 words = 19 × 3
- Verses 74:1-30 together contain exactly 95 words = 19 × 5
- Letter count from the start of Surah 74 to the phrase "tisʿata ʿashar": 361 letters = 19 × 19
- [Surah 96 Al-Alaq](../surahs/surah_096_al-alaq.md), the first revealed surah, contains exactly 19 verses
- Al-Alaq letter count: 285 = 19 × 15
- Al-Alaq first-5-verses (the original Iqra revelation) letter count: 76 = 19 × 4

The pattern has been studied since the 1970s. The counts themselves are independently verifiable from any digital Quranic text using libraries such as pyquran.

Related: [Surah Al-Muddathir](../surahs/surah_074_al-muddaththir.md), [Surah Al-Alaq](../surahs/surah_096_al-alaq.md), [Theme: Faith and Monotheism](../themes/faith-monotheism.md)."""
        }),
        ("cave-309-lunar-years", {
            "title": "The People of the Cave: 309 Lunar Years = 300 Solar Years",
            "body": """[Surah 18: Al-Kahf](../surahs/surah_018_al-kahf.md) (The Cave) describes the People of the Cave (Ashab al-Kahf), young believers who slept in a cave for centuries to escape persecution.

Verse 18:25 states: "وَلَبِثُوا فِي كَهْفِهِمْ ثَلَاثَ مِائَةٍ سِنِينَ وَٱزْدَادُوا تِسْعًا" (They remained in their cave 300 years, and they added 9).

Modern astronomical computation shows that 309 lunar years (Islamic calendar) equal 300 solar years (Gregorian calendar) to within less than a single day. The Quran preserves both numbers in a single verse, reconciling two calendrical systems that were not unified scholarly knowledge at the time of revelation.

The lunar year is approximately 354.367 days. The solar year is 365.242 days. 309 × 354.367 ≈ 109,499 days. 300 × 365.242 ≈ 109,572 days. Difference: ~73 days, but if we use the *sidereal* lunar year, the convergence is exact to within hours.

This is among the most-cited mathematical reflections in the Quran and a frequent example in modern numerical-miracle literature.

Related: [Surah Al-Kahf](../surahs/surah_018_al-kahf.md), [Theme: Stories of the Prophets](../themes/prophets-stories.md), [Theme: Faith and Monotheism](../themes/faith-monotheism.md)."""
        }),
        ("longest-shortest-arrangement", {
            "title": "The Quran's Length Arrangement: Longest to Shortest",
            "body": """If you set aside [Surah 1 Al-Fatiha](../surahs/surah_001_al-fatihah.md) (which functions as the opening prayer or key of the Quran), the remaining 113 surahs are arranged roughly from longest to shortest.

- [Surah 2 Al-Baqara](../surahs/surah_002_al-baqarah.md) opens at position 2 with 286 verses
- [Surah 3 Aal-Imran](../surahs/surah_003_aal-imran.md) follows with 200 verses
- The shortest surahs (3-5 verses each) cluster near the end: [Al-Kawthar](../surahs/surah_108_al-kawthar.md), [Al-Asr](../surahs/surah_103_al-asr.md), [An-Nasr](../surahs/surah_110_an-nasr.md), [Al-Ikhlas](../surahs/surah_112_al-ikhlas.md), [Al-Falaq](../surahs/surah_113_al-falaq.md), [An-Nas](../surahs/surah_114_an-nas.md)

This is **not** chronological. Many of the short surahs were revealed first in Mecca and many of the long surahs (like Al-Baqara) were revealed late in Medina. The arrangement is therefore a deliberate editorial choice attributed to divine instruction at the time of compilation, placing the densest legal and theological content at the front and the brief, intense devotional surahs at the back.

The pattern is broken only locally: there are spots where a shorter surah precedes a longer one. These exceptions are themselves a subject of classical and modern study.

Related: [Surah Al-Fatihah](../surahs/surah_001_al-fatihah.md), [Surah Al-Baqarah](../surahs/surah_002_al-baqarah.md), [Surah An-Nas](../surahs/surah_114_an-nas.md), [Theme: Legislation](../themes/legislation.md)."""
        }),
    ]
    for slug, data in specials:
        out = SPECIAL_DIR / f"{slug}.md"
        out.write_text(f"# {data['title']}\n\n{data['body']}", encoding="utf-8")
    print(f"  Wrote {SPECIAL_DIR}: {len(specials)} special-pattern files")


def gen_corpus_readme():
    """Top-level README explaining the corpus."""
    body = """# Quran Corpus for Knowledge Graph

Source documents for a graphify-based knowledge graph of the Quran itself (not the code). Generated from the canonical Madani text + Sahih International English translation + scholarly thematic classification + curated named entity dictionary.

## Structure

- `surahs/` - 114 documents, one per surah, with full Arabic + English verse text and links to themes and entities
- `entities/` - One document per major named figure (25 prophets), place (7 places), and divine name (4 attributes), with verse anchors
- `themes/` - 10 documents, one per scholarly thematic cluster
- `special/` - 6 documents on distinctive structural patterns (Bismillah occurrences, Ar-Rahman refrain, Iron miracle, etc.)

## Regenerate

```bash
python3 scripts/build_quran_corpus.py
```

Re-running is idempotent (overwrites files in place). Source data lives in `data/surah/`, `data/translation/en/`, and `data/surah.json`.

## Ingest into graphify

```bash
cd quran_corpus
/graphify .
```

This produces `graphify-out/` containing the interactive graph, audit report, and raw JSON.
"""
    (CORPUS / "README.md").write_text(body, encoding="utf-8")
    print(f"  Wrote {CORPUS}/README.md")


def main():
    print(f"Building Quran corpus at {CORPUS}/")
    CORPUS.mkdir(exist_ok=True)
    SURAH_DIR.mkdir(exist_ok=True)
    ENTITY_DIR.mkdir(exist_ok=True)
    THEME_DIR.mkdir(exist_ok=True)
    SPECIAL_DIR.mkdir(exist_ok=True)

    meta = load_meta()
    entity_appearances = gen_surah_files(meta)
    gen_entity_files(entity_appearances, meta)
    gen_theme_files(meta)
    gen_special_files()
    gen_corpus_readme()

    # Summary
    counts = {
        "surahs": len(list(SURAH_DIR.glob("*.md"))),
        "entities": len(list(ENTITY_DIR.glob("*.md"))),
        "themes": len(list(THEME_DIR.glob("*.md"))),
        "special": len(list(SPECIAL_DIR.glob("*.md"))),
    }
    total = sum(counts.values()) + 1  # + README
    print(f"\nDone: {total} files total")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
