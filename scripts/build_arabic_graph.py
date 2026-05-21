#!/usr/bin/env python3
"""
Build an Arabic-labeled version of the Quranic knowledge graph.

Loads quran_corpus/graphify-out/graph.json, translates every node label
to Arabic via a comprehensive translation map + pattern matching, then
re-exports as graph_ar.html using graphify's to_html function.

Output: quran_corpus/graphify-out/quran_graph_ar.html

This is then bundled into the Electron asar alongside the English version
so the app can swap based on the lang toggle.

Run:
    python3 scripts/build_arabic_graph.py
"""

import json
import re
from pathlib import Path
from networkx.readwrite import json_graph

ROOT = Path(__file__).parent.parent
GRAPH_DIR = ROOT / "quran_corpus" / "graphify-out"

# ──────────────────────────────────────────────────────────
# Translation: community labels (28)
# ──────────────────────────────────────────────────────────
COMMUNITY_LABELS_AR = {
    0:  "مدنية متأخرة: الحجاب وزينب وأسماء الله",
    1:  "محور أسماء الله (الله، الرحمن، الرحيم)",
    2:  "المجادلة وحجة الوداع",
    3:  "غزوة أحد والمباهلة وآدم",
    4:  "البقرة: بني إسرائيل وآدم وإبراهيم",
    5:  "علم أسباب النزول",
    6:  "إسكاتولوجيا مكية متأخرة",
    7:  "قصص العقوبة التاريخية (أبو لهب، الفيل، الأخدود)",
    8:  "مدارس التفسير المنهجية (المأثور، الميسّر)",
    9:  "عام الحزن والأمم المهلكة (عاد، ثمود)",
    10: "حجة الوداع والتوحيد",
    11: "مكة المبكرة: غار حراء والمقاطعة",
    12: "مدرسة السامرائي البيانية اللغوية",
    13: "الأنماط الخاصة (المعوذتان، اللازمة، ليلة القدر)",
    14: "أسماء الله ونمط البسملة",
    15: "محور عائشة (الإفك، آية النور)",
    16: "مدرسة سيد قطب في ظلال القرآن",
    17: "خواطر الشعراوي",
    18: "فقه القرطبي في الأحكام",
    19: "حادثة الأعمى (سورة عبس ٨٠)",
}

# ──────────────────────────────────────────────────────────
# Translation: explicit entity translations
# ──────────────────────────────────────────────────────────
EXPLICIT = {
    # Divine names
    "Allah": "الله",
    "Ar-Rahman (the Most Gracious)": "الرحمن",
    "Ar-Rahim (the Most Merciful)": "الرحيم",
    "Rabb (the Lord)": "الرب",
    # Prophets
    "Adam": "آدم",
    "Idris (Enoch)": "إدريس",
    "Noah (Nuh)": "نوح",
    "Hud": "هود",
    "Salih": "صالح",
    "Abraham (Ibrahim)": "إبراهيم",
    "Ibrahim (Abraham)": "إبراهيم",
    "Lot (Lut)": "لوط",
    "Ishmael (Ismail)": "إسماعيل",
    "Isaac (Ishaq)": "إسحاق",
    "Jacob (Yaqub)": "يعقوب",
    "Joseph (Yusuf)": "يوسف",
    "Job (Ayyub)": "أيوب",
    "Shuayb": "شعيب",
    "Moses (Musa)": "موسى",
    "Aaron (Harun)": "هارون",
    "Dhul-Kifl": "ذو الكفل",
    "David (Dawud)": "داود",
    "Solomon (Sulayman)": "سليمان",
    "Elijah (Ilyas)": "إلياس",
    "Elisha (Al-Yasa)": "اليسع",
    "Jonah (Yunus)": "يونس",
    "Zechariah (Zakariya)": "زكريا",
    "John the Baptist (Yahya)": "يحيى",
    "Jesus (Isa)": "عيسى",
    "Muhammad": "محمد",
    # Other figures
    "Mary (Maryam, mother of Jesus)": "مريم",
    "Mary (Maryam)": "مريم",
    "Pharaoh (Firaun)": "فرعون",
    "Haman": "هامان",
    "Qarun (Korah)": "قارون",
    "Iblis (Satan)": "إبليس",
    "Gabriel (Jibril)": "جبريل",
    "Aisha": "عائشة",
    "Khadijah": "خديجة",
    "Abu Bakr": "أبو بكر",
    "Umar ibn al-Khattab": "عمر بن الخطاب",
    "Ali ibn Abi Talib": "علي بن أبي طالب",
    "Khawla bint Tha'laba": "خولة بنت ثعلبة",
    "Ja'far ibn Abi Talib": "جعفر بن أبي طالب",
    "Najashi (Negus)": "النجاشي",
    # Places
    "Mecca (Makka)": "مكة",
    "Medina": "المدينة",
    "The Sacred Mosque (Makka)": "المسجد الحرام",
    "Sacred Mosque": "المسجد الحرام",
    "Masjid al-Haram": "المسجد الحرام",
    "The Furthest Mosque (Jerusalem)": "المسجد الأقصى",
    "Mount Sinai (Tur)": "جبل الطور",
    "Egypt (Misr)": "مصر",
    "Madyan": "مدين",
    "Cave of Hira": "غار حراء",
    # Revelation phases
    "Revelation Phase: Early Meccan": "مرحلة الوحي: مكية مبكرة",
    "Revelation Phase: Middle Meccan": "مرحلة الوحي: مكية وسطى",
    "Revelation Phase: Late Meccan": "مرحلة الوحي: مكية متأخرة",
    "Revelation Phase: Early Medinan": "مرحلة الوحي: مدنية مبكرة",
    "Revelation Phase: Late Medinan": "مرحلة الوحي: مدنية متأخرة",
    "Early Meccan Phase (610-615 CE)": "المرحلة المكية المبكرة (610-615م)",
    "Middle Meccan Phase (615-619 CE)": "المرحلة المكية الوسطى (615-619م)",
    "Late Meccan Phase (619-622 CE)": "المرحلة المكية المتأخرة (619-622م)",
    "Early Medinan Phase (622-628 CE)": "المرحلة المدنية المبكرة (622-628م)",
    "Late Medinan Phase (628-632 CE)": "المرحلة المدنية المتأخرة (628-632م)",
    # Events
    "The Cave of Hira: First Revelation": "غار حراء: الوحي الأول",
    "Public Preaching Begins": "بداية الدعوة الجهرية",
    "First Migration to Abyssinia (Habasha)": "الهجرة الأولى إلى الحبشة",
    "The Boycott of Banu Hashim": "مقاطعة بني هاشم",
    "Year of Sorrow (Aam al-Huzn)": "عام الحزن",
    "The Night Journey and Ascension (Isra and Mi'raj)": "الإسراء والمعراج",
    "The Hijra: Migration to Medina": "الهجرة إلى المدينة",
    "The Battle of Badr": "غزوة بدر",
    "The Battle of Uhud": "غزوة أحد",
    "The Battle of the Trench (Al-Khandaq)": "غزوة الخندق",
    "The Treaty of Hudaybiyyah": "صلح الحديبية",
    "The Conquest of Mecca (Fath Makka)": "فتح مكة",
    "The Tabuk Expedition": "غزوة تبوك",
    "The Farewell Pilgrimage (Hajjat al-Wada)": "حجة الوداع",
    # Asbab al-Nuzul
    "Asbab al-Nuzul: The Change of Qibla from Jerusalem to Mecca": "أسباب النزول: تحويل القبلة",
    "Asbab al-Nuzul: The Hijab Verses": "أسباب النزول: آيات الحجاب",
    "Asbab al-Nuzul: The Slander of Aisha (Al-Ifk)": "أسباب النزول: حادثة الإفك",
    "Asbab al-Nuzul: The Three Who Stayed Behind from Tabuk": "أسباب النزول: الثلاثة الذين خُلِّفوا",
    "Asbab al-Nuzul: Ayat al-Kursi: The Throne Verse": "أسباب النزول: آية الكرسي",
    "Asbab al-Nuzul: The Verse of Mubahala (Mutual Imprecation)": "أسباب النزول: آية المباهلة",
    "Asbab al-Nuzul: Verses Praising the First Three Converts": "أسباب النزول: السابقون الأولون",
    "Asbab al-Nuzul: The Verse of Perfection of Religion": "أسباب النزول: آية إكمال الدين",
    "Asbab al-Nuzul: Verses on the Marriage to Zaynab bint Jahsh": "أسباب النزول: زواج زينب بنت جحش",
    "Asbab al-Nuzul: The Pleading Woman (Al-Mujadila)": "أسباب النزول: المجادِلة (خولة)",
    "Asbab al-Nuzul: The Declaration of Immunity": "أسباب النزول: البراءة",
    "Asbab al-Nuzul: Verses on Orphans and Widows after Uhud": "أسباب النزول: آيات اليتامى والأرامل بعد أحد",
    "Asbab al-Nuzul: Ayat an-Nur: The Light Verse": "أسباب النزول: آية النور",
    "Asbab al-Nuzul: The Inheritance Verses": "أسباب النزول: آيات المواريث",
    "Asbab al-Nuzul: Abraham's Call to Pilgrimage": "أسباب النزول: دعوة إبراهيم للحج",
    # Tafsir scholars
    "Imam Al-Tabari": "الإمام الطبري",
    "Ibn Kathir": "ابن كثير",
    "Al-Qurtubi": "القرطبي",
    "Al-Sa'di": "السعدي",
    "Ibn Ashur": "ابن عاشور",
    "Sheikh Al-Sha'rawi": "الشيخ الشعراوي",
    "Sayyid Qutb": "سيد قطب",
    "Dr. Fadel Al-Samarrai": "د. فاضل السامرائي",
    "Al-Wahidi (d. 1076 CE)": "الواحدي (ت 468هـ)",
    "Imam Al-Suyuti": "الإمام السيوطي",
    "Ibn Taymiyyah": "ابن تيمية",
    # Sciences
    "Asbab al-Nuzul: Occasions of Revelation": "علم أسباب النزول",
    "Nasikh wal-Mansukh: Abrogating and Abrogated Verses": "الناسخ والمنسوخ",
    "Muhkam and Mutashabih: Clear and Allegorical Verses": "المحكم والمتشابه",
    "Makki and Madani: Meccan and Medinan Classification": "المكي والمدني",
    "The Ten Qira'at: Canonical Readings of the Quran": "القراءات العشر",
    "I'jaz al-Quran: The Inimitability of the Quran": "إعجاز القرآن",
    # Special patterns
    "Bismillah: The 113 Occurrences": "البسملة: المائة وثلاث عشرة مرة",
    "The Ar-Rahman Refrain: 31 Repetitions": "لازمة الرحمن: ٣١ تكراراً",
    "The Iron Miracle: Surah 57 Al-Hadid": "معجزة الحديد: سورة ٥٧",
    "The Number 19 Pattern": "نمط الرقم ١٩",
    "The People of the Cave: 309 Lunar Years = 300 Solar Years": "أصحاب الكهف: ٣٠٩ سنة قمرية = ٣٠٠ سنة شمسية",
    "The Quran's Length Arrangement: Longest to Shortest": "ترتيب السور من الأطول إلى الأقصر",
    # Themes
    "Theme: Faith and Monotheism (Tawhid)": "العقيدة والتوحيد",
    "Theme: Faith and Monotheism": "العقيدة والتوحيد",
    "Theme: Legislation": "التشريع",
    "Theme: Stories of the Prophets": "قصص الأنبياء",
    "Theme: Day of Judgment": "يوم القيامة",
    "Theme: Warning": "التحذير",
    "Theme: Ethics and Character": "الأخلاق",
    "Theme: Worship and Devotion": "العبادة",
    "Theme: Nature and Signs": "الطبيعة والآيات",
    "Theme: Community and Society": "المجتمع",
    "Theme: Community and Defence": "المجتمع والدفاع",
    "Theme: Patience and Endurance": "الصبر",
}

# ──────────────────────────────────────────────────────────
# Surah Arabic titles (load from source data)
# ──────────────────────────────────────────────────────────
def load_surah_titles_ar():
    meta = json.load(open(ROOT / "data" / "surah.json", encoding="utf-8"))
    return {int(m["index"]): m["titleAr"] for m in meta}

SURAH_AR = load_surah_titles_ar()

# Eastern Arabic digits
def to_ar_digits(s):
    table = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    return s.translate(table)

# ──────────────────────────────────────────────────────────
# Translation engine
# ──────────────────────────────────────────────────────────
def translate_surah_label(label):
    """E.g. 'Surah 2: Al-Baqara (The Cow)' -> 'سورة ٢: البقرة'"""
    m = re.match(r"^Surah (\d+): (.+?)( \(.+\))?$", label)
    if not m:
        return None
    n = int(m.group(1))
    ar = SURAH_AR.get(n)
    if ar:
        return f"سورة {to_ar_digits(str(n))}: {ar}"
    return None


def translate_label(label):
    """Translate a single node label to Arabic."""
    if not label:
        return label
    # 1. Explicit lookup
    if label in EXPLICIT:
        return EXPLICIT[label]
    # 2. Surah pattern
    surah = translate_surah_label(label)
    if surah:
        return surah
    # 3. Common patterns
    # "<Name> (<Arabic>)" pattern: if the parenthesized text is Arabic, use it
    m = re.match(r"^(.+?) \(([؀-ۿ].+?)\)$", label)
    if m:
        return m.group(2)
    # "Asbab al-Nuzul: <topic>" pattern
    m = re.match(r"^Asbab al-Nuzul: (.+)$", label)
    if m:
        return f"أسباب النزول: {m.group(1)}"
    # "Theme: <name>" pattern
    m = re.match(r"^Theme: (.+)$", label)
    if m:
        return f"موضوع: {m.group(1)}"
    # "Revelation Phase: <phase>" pattern
    m = re.match(r"^Revelation Phase: (.+)$", label)
    if m:
        return f"مرحلة الوحي: {m.group(1)}"
    # Battle/Treaty patterns
    label = label.replace("Battle of ", "غزوة ").replace("Treaty of ", "صلح ")
    # Fallback: keep original (mark with [EN] prefix so user can spot untranslated)
    return label


def translate_graph(graph_data):
    """Translate all node labels in the graph data in place."""
    for n in graph_data.get("nodes", []):
        original = n.get("label", "")
        n["label"] = translate_label(original)
        # Also translate norm_label for search consistency
        if "norm_label" in n:
            n["norm_label"] = n["label"].lower()
    return graph_data


# ──────────────────────────────────────────────────────────
# Main: load, translate, re-export HTML
# ──────────────────────────────────────────────────────────
def main():
    graph_json_path = GRAPH_DIR / "graph.json"
    if not graph_json_path.exists():
        print(f"ERROR: {graph_json_path} not found. Run graphify first.")
        return

    # Load graph data
    data = json.loads(graph_json_path.read_text(encoding="utf-8"))
    print(f"Loaded graph: {len(data.get('nodes', []))} nodes, {len(data.get('links', []))} edges")

    # Build NetworkX graph (older networkx uses no 'edges' kwarg)
    try:
        G = json_graph.node_link_graph(data, edges="links")
    except TypeError:
        # Older networkx: links are expected under 'links' key by default
        G = json_graph.node_link_graph(data)
    print(f"NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    # Translate labels in node attributes
    translated_count = 0
    for n, attrs in G.nodes(data=True):
        orig = attrs.get("label", "")
        new = translate_label(orig)
        if new != orig:
            attrs["label"] = new
            translated_count += 1
    print(f"Translated {translated_count} of {G.number_of_nodes()} node labels")

    # Reconstruct communities dict from node attrs
    communities = {}
    for n, attrs in G.nodes(data=True):
        cid = attrs.get("community")
        if cid is None:
            continue
        communities.setdefault(int(cid), []).append(n)

    # Translate community labels
    community_labels = {}
    for cid in communities:
        community_labels[cid] = COMMUNITY_LABELS_AR.get(cid, f"مجموعة {to_ar_digits(str(cid))}")

    # Use graphify's to_html to render
    from graphify.export import to_html
    output_path = str(GRAPH_DIR / "quran_graph_ar.html")
    to_html(G, communities, output_path, community_labels=community_labels)
    print(f"Wrote Arabic graph: {output_path}")
    print(f"File size: {Path(output_path).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
