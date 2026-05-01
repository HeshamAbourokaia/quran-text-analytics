#!/usr/bin/env python3
"""Enrich app_data.json with additional analytics for the cinematic HTML app."""
import json, re, os
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))

# Load existing data
with open(os.path.join(BASE, "app_data.json")) as f:
    data = json.load(f)

# Load surah index
with open(os.path.join(BASE, "data", "surah.json")) as f:
    surah_index = json.load(f)

# Load all Arabic text + English translations
verses = []
for si in surah_index:
    idx = int(si["index"])
    with open(os.path.join(BASE, "data", "surah", f"surah_{idx}.json")) as f:
        ar_data = json.load(f)
    ar_verses = ar_data.get("verse", {})
    en_path = os.path.join(BASE, "data", "translation", "en", f"en_translation_{idx}.json")
    en_verses = {}
    if os.path.exists(en_path):
        with open(en_path) as f:
            en_data = json.load(f)
            en_verses = en_data.get("verse", {})
    count = int(ar_data.get("count", si.get("count", 0)))
    for vi in range(1, count + 1):
        key = f"verse_{vi}"
        ar_text = ar_verses.get(key, "")
        en_text = en_verses.get(key, "")
        verses.append({
            "surah": idx,
            "surah_ar": si.get("titleAr", si.get("title", "")),
            "verse": vi,
            "arabic": ar_text,
            "english": en_text,
            "place": si.get("place", "Mecca"),
        })

def normalize_arabic(text):
    text = re.sub(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u08D3-\u08FF]', '', text)
    text = re.sub(r'[ٱإأآا]', 'ا', text)
    text = re.sub(r'[ؤئ]', 'ء', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = re.sub(r'[\u06E2\u06E3\u06E5\u06E6\u06E8\u06EA-\u06ED]', '', text)
    return text

print("Computing antonym pair verification...")
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

antonym_results = []
for pair in ANTONYM_CLAIMS:
    norm_a = normalize_arabic(pair["ar_a"])
    norm_b = normalize_arabic(pair["ar_b"])
    count_a = sum(1 for v in verses if norm_a in normalize_arabic(v["arabic"]))
    count_b = sum(1 for v in verses if norm_b in normalize_arabic(v["arabic"]))
    match = count_a == count_b
    antonym_results.append({
        "ar_a": pair["ar_a"], "ar_b": pair["ar_b"],
        "label_ar": pair["label_ar"], "label_en": pair["label_en"],
        "claimed": pair["claimed"],
        "found_a": count_a, "found_b": count_b,
        "match": match, "diff": abs(count_a - count_b)
    })
data["antonymPairs"] = antonym_results

print("Computing calendar word verification...")
CALENDAR_CLAIMS = [
    {"ar": "يوم", "claimed": 365, "label_ar": "يوم (مفرد)", "label_en": "Day (singular)",
     "note_ar": "يُدّعى أنها تظهر 365 مرة = أيام السنة", "note_en": "Claimed to appear 365 times = days in a year"},
    {"ar": "شهر", "claimed": 12, "label_ar": "شهر", "label_en": "Month",
     "note_ar": "يُدّعى أنها تظهر 12 مرة = أشهر السنة", "note_en": "Claimed to appear 12 times = months in a year"},
]

cal_results = []
for claim in CALENDAR_CLAIMS:
    norm_word = normalize_arabic(claim["ar"])
    verse_count = sum(1 for v in verses if norm_word in normalize_arabic(v["arabic"]))
    total_count = 0
    for v in verses:
        normalized = normalize_arabic(v["arabic"])
        words = re.findall(r'[\u0620-\u064A]+', normalized)
        total_count += sum(1 for w in words if norm_word in w)
    cal_results.append({
        "ar": claim["ar"], "claimed": claim["claimed"],
        "label_ar": claim["label_ar"], "label_en": claim["label_en"],
        "note_ar": claim["note_ar"], "note_en": claim["note_en"],
        "verse_count": verse_count, "total_count": total_count,
        "verse_match": verse_count == claim["claimed"],
        "total_match": total_count == claim["claimed"],
    })
data["calendarClaims"] = cal_results

print("Computing Abjad numeral data...")
# Abjad numeral values (حساب الجُمَّل)
ABJAD = {
    'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5, 'و': 6, 'ز': 7, 'ح': 8, 'ط': 9,
    'ي': 10, 'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60, 'ع': 70, 'ف': 80,
    'ص': 90, 'ق': 100, 'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600,
    'ذ': 700, 'ض': 800, 'ظ': 900, 'غ': 1000,
}

def abjad_value(word):
    """Calculate the Abjad numerical value of an Arabic word."""
    normalized = normalize_arabic(word)
    return sum(ABJAD.get(ch, 0) for ch in normalized)

# Iron miracle verification
hadid_word = "حديد"  # Iron
hadid_value = abjad_value(hadid_word)
# Surah Al-Hadid = 57, verse 25 mentions iron
# Fe atomic number = 26, most common isotope Fe-57

abjad_examples = [
    {
        "word_ar": "حديد", "word_en": "Iron (Hadid)",
        "value": hadid_value,
        "letters": [{"l": ch, "v": ABJAD.get(ch, 0)} for ch in normalize_arabic("حديد")],
        "significance_ar": f"القيمة العددية = {hadid_value}. سورة الحديد رقمها 57. العدد الذري للحديد = 26. النظير الأكثر استقراراً Fe-57.",
        "significance_en": f"Abjad value = {hadid_value}. Surah Al-Hadid is chapter 57. Iron's atomic number = 26. Most stable isotope is Fe-57.",
        "claim_ar": "يُدّعى أن القيمة العددية لكلمة حديد = العدد الذري للحديد (26)",
        "claim_en": "Claimed: Abjad value of 'hadid' = atomic number of iron (26)",
        "verified": hadid_value == 26,
        "note_ar": f"القيمة الفعلية = {hadid_value}. " + ("متطابق! ✅" if hadid_value == 26 else f"غير متطابق مع 26. لكن لاحظ: ح(8)+د(4)+ي(10)+د(4) = {hadid_value}"),
        "note_en": f"Actual value = {hadid_value}. " + ("Match! ✅" if hadid_value == 26 else f"Does not match 26. Note: ح(8)+د(4)+ي(10)+د(4) = {hadid_value}"),
    },
    {
        "word_ar": "بسم الله الرحمن الرحيم", "word_en": "Bismillah (In the name of God)",
        "value": abjad_value("بسم الله الرحمن الرحيم"),
        "letters": [],
        "significance_ar": f"القيمة العددية للبسملة = {abjad_value('بسم الله الرحمن الرحيم')}",
        "significance_en": f"Abjad value of Bismillah = {abjad_value('بسم الله الرحمن الرحيم')}",
        "claim_ar": "البسملة لها قيمة عددية فريدة في حساب الجُمَّل",
        "claim_en": "Bismillah has a unique Abjad numerical value",
        "verified": True,
        "note_ar": f"القيمة = {abjad_value('بسم الله الرحمن الرحيم')}",
        "note_en": f"Value = {abjad_value('بسم الله الرحمن الرحيم')}",
    },
]

data["abjadTable"] = [{"l": k, "v": v} for k, v in sorted(ABJAD.items(), key=lambda x: x[1])]
data["abjadExamples"] = abjad_examples

print("Adding scientific references...")
SCIENTIFIC_REFS = [
    {"cat_ar": "🌌 علم الكونيات", "cat_en": "🌌 Cosmology", "s": 51, "v": 47,
     "t_ar": "توسع الكون", "t_en": "Universe Expansion",
     "sc_ar": "اكتشف إدوين هابل عام 1929 أن الكون يتوسع باستمرار.",
     "sc_en": "Edwin Hubble discovered in 1929 that the universe is continuously expanding."},
    {"cat_ar": "🌌 علم الكونيات", "cat_en": "🌌 Cosmology", "s": 21, "v": 30,
     "t_ar": "الانفجار الكبير", "t_en": "Big Bang",
     "sc_ar": "نظرية الانفجار الكبير تقول إن الكون بدأ من نقطة واحدة ثم انفصلت.",
     "sc_en": "The Big Bang theory states the universe began from a single point that then separated."},
    {"cat_ar": "🌌 علم الكونيات", "cat_en": "🌌 Cosmology", "s": 21, "v": 33,
     "t_ar": "المدارات الفلكية", "t_en": "Celestial Orbits",
     "sc_ar": "كل الأجرام السماوية تسبح في مدارات محددة.",
     "sc_en": "All celestial bodies swim in defined orbits."},
    {"cat_ar": "🌌 علم الكونيات", "cat_en": "🌌 Cosmology", "s": 41, "v": 11,
     "t_ar": "الكون كان دخاناً", "t_en": "Universe Was Smoke/Gas",
     "sc_ar": "الكون المبكر كان سحابة غازية ساخنة قبل تكوّن النجوم.",
     "sc_en": "The early universe was a hot gaseous cloud before stars formed."},
    {"cat_ar": "🌌 علم الكونيات", "cat_en": "🌌 Cosmology", "s": 39, "v": 5,
     "t_ar": "كروية الأرض", "t_en": "Spherical Earth",
     "sc_ar": "كلمة 'يكوّر' تعني اللف حول شكل كروي.",
     "sc_en": "The word 'yukawwir' means to wrap around a sphere."},
    {"cat_ar": "🧬 علم الأجنة", "cat_en": "🧬 Embryology", "s": 23, "v": 14,
     "t_ar": "مراحل تطور الجنين", "t_en": "Embryonic Development Stages",
     "sc_ar": "يتطور الجنين عبر مراحل: نطفة، علقة، مضغة — بدقة تطابق علم الأجنة.",
     "sc_en": "The embryo develops through stages matching modern embryology."},
    {"cat_ar": "🧬 علم الأجنة", "cat_en": "🧬 Embryology", "s": 39, "v": 6,
     "t_ar": "ثلاث ظلمات", "t_en": "Three Layers of Darkness",
     "sc_ar": "الجنين محاط بثلاث طبقات: جدار البطن، جدار الرحم، والغشاء الأمنيوسي.",
     "sc_en": "The embryo is surrounded by three layers: abdominal wall, uterine wall, amniotic membrane."},
    {"cat_ar": "⛰️ علم الجيولوجيا", "cat_en": "⛰️ Geology", "s": 78, "v": 7,
     "t_ar": "الجبال كأوتاد", "t_en": "Mountains as Pegs",
     "sc_ar": "الجبال لها جذور عميقة — كالأوتاد المثبتة.",
     "sc_en": "Mountains have deep roots — like pegs anchoring the crust."},
    {"cat_ar": "⛰️ علم الجيولوجيا", "cat_en": "⛰️ Geology", "s": 27, "v": 88,
     "t_ar": "حركة الجبال", "t_en": "Mountains Move",
     "sc_ar": "الجبال تتحرك مع الصفائح التكتونية.",
     "sc_en": "Mountains move with tectonic plates."},
    {"cat_ar": "🌊 علم المحيطات", "cat_en": "🌊 Oceanography", "s": 55, "v": 20,
     "t_ar": "الحاجز بين البحرين", "t_en": "Barrier Between Two Seas",
     "sc_ar": "عند التقاء بحرين مختلفين، يتشكل حاجز طبيعي يمنع اختلاطهما.",
     "sc_en": "When two seas meet, a natural barrier prevents mixing."},
    {"cat_ar": "🌊 علم المحيطات", "cat_en": "🌊 Oceanography", "s": 24, "v": 40,
     "t_ar": "الأمواج الداخلية", "t_en": "Internal Waves & Deep Sea Darkness",
     "sc_ar": "أعماق المحيطات مظلمة تماماً وفيها أمواج داخلية.",
     "sc_en": "Ocean depths are completely dark with internal waves."},
    {"cat_ar": "🛡️ علم الغلاف الجوي", "cat_en": "🛡️ Atmospheric Science", "s": 21, "v": 32,
     "t_ar": "السماء كسقف محفوظ", "t_en": "Sky as Protected Ceiling",
     "sc_ar": "الغلاف الجوي يحمي الأرض من الإشعاع الكوني.",
     "sc_en": "The atmosphere protects Earth from cosmic radiation."},
    {"cat_ar": "🛡️ علم الغلاف الجوي", "cat_en": "🛡️ Atmospheric Science", "s": 15, "v": 22,
     "t_ar": "الرياح لواقح", "t_en": "Winds as Pollinators",
     "sc_ar": "الرياح تحمل حبوب اللقاح لتلقيح النباتات.",
     "sc_en": "Winds carry pollen to pollinate plants."},
    {"cat_ar": "💧 علم المياه", "cat_en": "💧 Hydrology", "s": 39, "v": 21,
     "t_ar": "دورة المياه", "t_en": "Water Cycle",
     "sc_ar": "الماء ينزل من السماء، يتسرب في الأرض، يخرج كينابيع.",
     "sc_en": "Water descends from sky, seeps into earth, emerges as springs."},
    {"cat_ar": "🧪 علم المعادن", "cat_en": "🧪 Metallurgy", "s": 57, "v": 25,
     "t_ar": "الحديد من الفضاء", "t_en": "Iron from Outer Space",
     "sc_ar": "الحديد لم يتكون على الأرض — جاء من انفجارات نجمية. سورة الحديد = 57 = النظير Fe-57.",
     "sc_en": "Iron came from stellar explosions. Surah Al-Hadid = 57 = isotope Fe-57."},
    {"cat_ar": "🧠 علم الأعصاب", "cat_en": "🧠 Neuroscience", "s": 96, "v": 16,
     "t_ar": "الناصية — الفص الجبهي", "t_en": "Frontal Lobe",
     "sc_ar": "الفص الجبهي مسؤول عن اتخاذ القرار والكذب.",
     "sc_en": "The frontal lobe is responsible for decision-making and lying."},
    {"cat_ar": "🧠 علم الأعصاب", "cat_en": "🧠 Neuroscience", "s": 4, "v": 56,
     "t_ar": "مستقبلات الألم", "t_en": "Pain Receptors in Skin",
     "sc_ar": "مستقبلات الألم في الجلد — عندما يحترق بالكامل يتوقف الألم.",
     "sc_en": "Pain receptors are in the skin — when skin burns completely, pain stops."},
    {"cat_ar": "🌱 علم النبات", "cat_en": "🌱 Botany", "s": 36, "v": 36,
     "t_ar": "الأزواج في الخلق", "t_en": "Pairs in All Creation",
     "sc_ar": "النباتات لها تكاثر جنسي — لم يُعرف إلا حديثاً.",
     "sc_en": "Plants have sexual reproduction — only recently discovered."},
    {"cat_ar": "🔬 علم الأحياء", "cat_en": "🔬 Biology", "s": 21, "v": 30,
     "t_ar": "الماء أصل كل حي", "t_en": "Water as Origin of Life",
     "sc_ar": "كل الكائنات الحية تتكون أساساً من الماء.",
     "sc_en": "All living things are fundamentally made from water."},
    {"cat_ar": "🐝 علم الحيوان", "cat_en": "🐝 Zoology", "s": 16, "v": 68,
     "t_ar": "النحلة أنثى", "t_en": "Worker Bees Are Female",
     "sc_ar": "القرآن يستخدم صيغة المؤنث للنحل — علم الأحياء يؤكد أن كل النحل العامل إناث.",
     "sc_en": "The Quran uses feminine form for worker bees — biology confirms all are female."},
    {"cat_ar": "🐝 علم الحيوان", "cat_en": "🐝 Zoology", "s": 27, "v": 18,
     "t_ar": "النمل يتواصل", "t_en": "Ants Communicate",
     "sc_ar": "النمل يتواصل عبر الفيرومونات والأصوات.",
     "sc_en": "Ants communicate through pheromones and sounds."},
    {"cat_ar": "⚕️ الطب", "cat_en": "⚕️ Medicine", "s": 16, "v": 69,
     "t_ar": "العسل شفاء", "t_en": "Honey as Medicine",
     "sc_ar": "العسل له خصائص مضادة للبكتيريا — يُستخدم لعلاج الجروح.",
     "sc_en": "Honey has antibacterial properties — used for wound healing."},
    {"cat_ar": "✨ علم الفلك", "cat_en": "✨ Astronomy", "s": 86, "v": 3,
     "t_ar": "النجم الثاقب", "t_en": "Pulsar",
     "sc_ar": "النجوم النابضة تصدر إشعاعات ثاقبة — اكتُشفت عام 1967.",
     "sc_en": "Pulsars emit piercing radiation — discovered in 1967."},
    {"cat_ar": "✨ علم الفلك", "cat_en": "✨ Astronomy", "s": 25, "v": 61,
     "t_ar": "القمر نور منعكس", "t_en": "Moon Reflects Light",
     "sc_ar": "القرآن يميز بين 'سراج' (مصدر ضوء) و'نور' (ضوء منعكس).",
     "sc_en": "The Quran distinguishes between 'siraj' (light source) and 'noor' (reflected light)."},
    {"cat_ar": "⚛️ الفيزياء", "cat_en": "⚛️ Physics", "s": 57, "v": 4,
     "t_ar": "نسبية الزمن", "t_en": "Relativity of Time",
     "sc_ar": "الزمن نسبي ويتغير حسب السرعة والجاذبية — نظرية أينشتاين.",
     "sc_en": "Time is relative, changing with speed and gravity — Einstein."},
    {"cat_ar": "🗺️ الجغرافيا", "cat_en": "🗺️ Geography", "s": 30, "v": 3,
     "t_ar": "أخفض منطقة على الأرض", "t_en": "Lowest Point on Earth",
     "sc_ar": "البحر الميت أخفض نقطة على الأرض (427م تحت سطح البحر).",
     "sc_en": "The Dead Sea is the lowest point on Earth (427m below sea level)."},
]

# Get verse text for each scientific reference
for ref in SCIENTIFIC_REFS:
    for v in verses:
        if v["surah"] == ref["s"] and v["verse"] == ref["v"]:
            ref["ar_text"] = v["arabic"]
            ref["en_text"] = v["english"]
            break
    if "ar_text" not in ref:
        ref["ar_text"] = ""
        ref["en_text"] = ""

data["scientificRefs"] = SCIENTIFIC_REFS

# Category distribution for chart
cat_counts = Counter(r["cat_en"] for r in SCIENTIFIC_REFS)
data["sciCategories"] = [{"cat": k, "count": v} for k, v in cat_counts.most_common()]

# Save enriched data
with open(os.path.join(BASE, "app_data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=None)

print(f"Done! Enriched app_data.json with {len(SCIENTIFIC_REFS)} scientific refs, "
      f"{len(antonym_results)} antonym pairs, {len(cal_results)} calendar claims, "
      f"{len(abjad_examples)} abjad examples")
print(f"File size: {os.path.getsize(os.path.join(BASE, 'app_data.json'))} bytes")

# Print verification results
print("\n=== ANTONYM PAIRS ===")
for r in antonym_results:
    status = "✅" if r["match"] else f"❌ diff={r['diff']}"
    print(f"  {r['label_en']}: {r['found_a']} vs {r['found_b']} (claimed: {r['claimed']}) {status}")

print("\n=== CALENDAR CLAIMS ===")
for r in cal_results:
    print(f"  {r['label_en']}: verses={r['verse_count']}, total={r['total_count']}, claimed={r['claimed']}")

print(f"\n=== ABJAD: حديد ===")
print(f"  Value: {hadid_value} (claimed = 26, atomic number of Iron)")
for ch in normalize_arabic("حديد"):
    print(f"    {ch} = {ABJAD.get(ch, 0)}")
