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
    # Bare theme names (without "Theme:" prefix)
    "Faith and Monotheism": "العقيدة والتوحيد",
    "Legislation": "التشريع",
    "Stories of the Prophets": "قصص الأنبياء",
    "Day of Judgment": "يوم القيامة",
    "Warning": "التحذير",
    "Ethics and Character": "الأخلاق",
    "Worship and Devotion": "العبادة",
    "Nature and Signs": "الطبيعة والآيات",
    "Community and Society": "المجتمع",
    "Community and Defence": "المجتمع والدفاع",
    "Patience and Endurance": "الصبر",
    "Tawhid (Monotheism)": "التوحيد",
    "Tawhid (oneness of God)": "التوحيد",
    "Hypocrisy (Nifaq)": "النفاق",
    "Repentance (Tawba)": "التوبة",
    "Jihad / Warfare Ethics": "أخلاق الجهاد والقتال",
    # Variant entity labels
    "Allah (God)": "الله",
    "Muhammad (the Prophet)": "محمد ﷺ",
    "Aisha (wife of Prophet)": "عائشة (زوج النبي)",
    "Hamaan (Pharaoh's minister)": "هامان (وزير فرعون)",
    "Abu Lahab (uncle of the Prophet)": "أبو لهب (عم النبي)",
    "Bilqis (Queen of Sheba)": "بلقيس (ملكة سبأ)",
    "Bani Israel (Children of Israel)": "بنو إسرائيل",
    "Jalut (Goliath)": "جالوت",
    "Talut (Saul)": "طالوت",
    "Nimrod (king who disputed with Ibrahim)": "النمرود",
    "Elias (Ilyas)": "إلياس",
    "Shuaib": "شعيب",
    "Shu'ayb": "شعيب",
    "Luqman the Wise": "لقمان الحكيم",
    "Zaynab bint Jahsh": "زينب بنت جحش",
    "Quraish tribe": "قبيلة قريش",
    "Blind Man incident (Abdullah ibn Umm Maktum)": "حادثة الأعمى (عبد الله بن أم مكتوم)",
    "Aad of Iram (the pillared)": "عاد إرم ذات العماد",
    "People of Thamood": "ثمود",
    "People of the Elephant (Year of the Elephant)": "أصحاب الفيل",
    "People of the Trench (Ashab al-Ukhdud)": "أصحاب الأخدود",
    "The People of the Heights (Al-A'raf)": "أصحاب الأعراف",
    "The Hypocrites (Munafiqun)": "المنافقون",
    "Saba (Sheba)": "سبأ",
    "Sacred Valley of Tuwa": "وادي طوى المقدس",
    # Phases (variants)
    "Late Meccan phase (619-622 CE)": "المرحلة المكية المتأخرة (619-622م)",
    "Late Medinan Phase (628-632 CE, Year 6-10 AH)": "المرحلة المدنية المتأخرة (628-632م، 6-10هـ)",
    "Late Medinan phase (628-632 CE)": "المرحلة المدنية المتأخرة (628-632م)",
    "Early Medinan Phase (622-628 CE, Year 1-6 AH)": "المرحلة المدنية المبكرة (622-628م، 1-6هـ)",
    "Phase: Late Meccan": "المرحلة المكية المتأخرة",
    # Events (variants)
    "Cave of Hira (absolute temporal origin of the Quran)": "غار حراء (الأصل الزماني للقرآن)",
    "First revelation: Cave of Hira": "الوحي الأول: غار حراء",
    "Public Preaching Begins (613 CE)": "بداية الدعوة الجهرية (613م)",
    "Migration to Abyssinia (615 CE)": "الهجرة إلى الحبشة (615م)",
    "First Migration to Abyssinia (615 CE)": "الهجرة الأولى إلى الحبشة (615م)",
    "Boycott of Banu Hashim (616-619 CE)": "مقاطعة بني هاشم (616-619م)",
    "Isra and Mi'raj (Night Journey)": "الإسراء والمعراج",
    "Isra and Mi'raj: Night Journey and Ascension (621 CE)": "الإسراء والمعراج (621م)",
    "Hijra (Emigration to Medina, 622 CE)": "الهجرة إلى المدينة (622م)",
    "Hijra: Migration to Medina (622 CE / Year 1 AH)": "الهجرة إلى المدينة (622م / 1هـ)",
    "Hijra and the Muhajirun/Ansar Alliance": "الهجرة وعهد المهاجرين والأنصار",
    "Tabuk Expedition (Rajab 9 AH / October 630 CE)": "غزوة تبوك (رجب 9هـ / أكتوبر 630م)",
    "The Tabuk Expedition Narrative (Year 9 AH)": "سيرة غزوة تبوك (9هـ)",
    "Farewell Pilgrimage (closing event of prophetic mission)": "حجة الوداع (ختام البعثة النبوية)",
    "Farewell Pilgrimage / Hajjat al-Wada (632 CE / 10 AH)": "حجة الوداع (632م / 10هـ)",
    "Event: Cave of Hira First Revelation": "حدث: غار حراء والوحي الأول",
    "Event: Conquest of Mecca": "حدث: فتح مكة",
    "Event: Year of Sorrow": "حدث: عام الحزن",
    "Year 1 of the Hijri Calendar (temporal pivot)": "السنة الأولى الهجرية (نقطة تحوّل زمنية)",
    # Asbab variants
    "Asbab al-Nuzul (Al-Wahidi)": "أسباب النزول (الواحدي)",
    "Asbab al-Nuzul (methodology)": "علم أسباب النزول (المنهج)",
    "Asbab: Abraham's Call to Pilgrimage (22:27)": "أسباب: دعوة إبراهيم للحج (22:27)",
    "Asbab: Ayat al-Kursi (2:255)": "أسباب: آية الكرسي (2:255)",
    "Asbab: Ayat an-Nur (24:35)": "أسباب: آية النور (24:35)",
    "Asbab: Change of Qibla (2:142-150)": "أسباب: تحويل القبلة (2:142-150)",
    "Asbab: Declaration of Immunity (9:1-29)": "أسباب: البراءة (9:1-29)",
    "Asbab: First Three Converts (9:100,117)": "أسباب: السابقون الأولون (9:100, 117)",
    "Asbab: Hijab Verses (33:53, 33:59, 24:31)": "أسباب: آيات الحجاب (33:53، 33:59، 24:31)",
    "Asbab: Inheritance Verses (4:11, 4:12, 4:176)": "أسباب: آيات المواريث (4:11، 4:12، 4:176)",
    "Asbab: Marriage to Zaynab": "أسباب: زواج زينب",
    "Asbab: Marriage to Zaynab bint Jahsh (33:37-40)": "أسباب: زواج زينب بنت جحش (33:37-40)",
    "Asbab: Orphans and Widows after Uhud (4:1-3, 4:127)": "أسباب: اليتامى والأرامل بعد أحد (4:1-3، 4:127)",
    "Asbab: Slander of Aisha (24:11-20)": "أسباب: حادثة الإفك (24:11-20)",
    "Asbab: The Pleading Woman": "أسباب: المجادِلة",
    "Asbab: The Pleading Woman (58:1-4)": "أسباب: المجادِلة (58:1-4)",
    "Asbab: The Slander of Aisha (Ifk)": "أسباب: حادثة الإفك",
    "Asbab: Three Who Stayed Behind from Tabuk (9:117-118)": "أسباب: الثلاثة المخلَّفون عن تبوك (9:117-118)",
    "Asbab: Verse of Light": "أسباب: آية النور",
    "Asbab: Verse of Mubahala (3:61)": "أسباب: آية المباهلة (3:61)",
    "Asbab: Verse of Perfection of Religion (5:3)": "أسباب: آية إكمال الدين (5:3)",
    "Asbab: Verses of Hijab": "أسباب: آيات الحجاب",
    "Asbab: Verses on marriage to Zaynab": "أسباب: زواج زينب",
    # Sciences variants
    "Asbab al-Nuzul: Occasions of Revelation": "علم أسباب النزول",
    "Nasikh wal-Mansukh": "الناسخ والمنسوخ",
    "Muhkam and Mutashabih": "المحكم والمتشابه",
    "Makki and Madani Classification": "المكي والمدني",
    "The Ten Qira'at (Canonical Readings)": "القراءات العشر",
    "I'jaz al-Quran (Inimitability)": "إعجاز القرآن",
    "Israiliyyat (Jewish/Christian narratives in tafsir)": "الإسرائيليات",
    # Tafsir approaches and works
    "Tafsir Adabi-Haraki (literary-activist)": "التفسير الأدبي الحركي",
    "Tafsir Bayani (rhetorical and linguistic precision)": "التفسير البياني",
    "Tafsir Fiqhi (jurisprudential tafsir)": "التفسير الفقهي",
    "Tafsir Khawatiri (devotional reflections)": "تفسير الخواطر",
    "Tafsir Lughawi-Balaghi (linguistic-rhetorical analysis)": "التفسير اللغوي البلاغي",
    "Tafsir Muyassar (accessible tafsir)": "التفسير الميسّر",
    "Tafsir bil-Mathur (interpretation through transmitted narration)": "التفسير بالمأثور",
    "Tafsir al-Quran al-Azim": "تفسير القرآن العظيم (ابن كثير)",
    "Al-Jami li-Ahkam al-Quran": "الجامع لأحكام القرآن (القرطبي)",
    "Al-Tahrir wa al-Tanwir": "التحرير والتنوير (ابن عاشور)",
    "Fi Zilal al-Quran (In the Shade of the Quran)": "في ظلال القرآن (سيد قطب)",
    "Khawatir al-Sha'rawi hawl al-Quran al-Karim": "خواطر الشعراوي حول القرآن الكريم",
    "Jami al-Bayan an Ta'wil ay al-Quran": "جامع البيان عن تأويل آي القرآن (الطبري)",
    "Lamasat Bayania (Linguistic Touches)": "لمسات بيانية (السامرائي)",
    "Taysir al-Karim al-Rahman": "تيسير الكريم الرحمن (السعدي)",
    "Maqasid al-Shari'ah": "مقاصد الشريعة",
    "Milestones (Ma'alim fi al-Tariq)": "معالم في الطريق (سيد قطب)",
    "Tarikh al-Rusul wal-Muluk": "تاريخ الرسل والملوك (الطبري)",
    "Lubab al-Nuqul fi Asbab al-Nuzul": "لباب النقول في أسباب النزول (السيوطي)",
    "Imam Suyuti": "الإمام السيوطي",
    # Special patterns variants
    "Special Feature: Absence of Bismillah in Surah 9 (At-Tawba)": "خاصية: غياب البسملة في سورة التوبة (9)",
    "Special: Ar-Rahman 31x refrain": "خاصية: لازمة الرحمن (31 مرة)",
    "Special: Iron Miracle (Al-Hadid)": "خاصية: معجزة الحديد (سورة 57)",
    "The People of the Cave: 309 Lunar = 300 Solar Years": "أصحاب الكهف: 309 سنوات قمرية = 300 شمسية",
    "Al-Mu'awwidhatan (the two protective surahs)": "المعوذتان",
    "Night of Decree (Laylat al-Qadr)": "ليلة القدر",
    "Divine Names of Bismillah": "أسماء الله في البسملة",
    "Quran's Length Arrangement: Longest to Shortest": "ترتيب القرآن: من الأطول إلى الأقصر",
    # Narratives and concepts
    "Abraham's Debate with the Idolaters (Stars, Moon, Sun)": "محاجة إبراهيم لقومه (النجم والقمر والشمس)",
    "Adam, Iblis and the Fall": "آدم وإبليس والهبوط",
    "Annunciation and Birth of Jesus (Isa) to Mary": "بشارة وميلاد عيسى لمريم",
    "Annunciation and Birth of John (Yahya) to Zechariah": "بشارة وميلاد يحيى لزكريا",
    "Ayat al-Kursi 2:255 (the Throne verse)": "آية الكرسي (2:255)",
    "Birth of Moses and Pharaoh's Persecution": "ولادة موسى واضطهاد فرعون",
    "Byzantine-Persian Prophecy": "نبوءة الروم وفارس",
    "Chain of prophets revelation (Noah to Muhammad)": "سلسلة الأنبياء (من نوح إلى محمد ﷺ)",
    "Change of qibla verses 2:142-150": "آيات تحويل القبلة (2:142-150)",
    "Children of Israel refuse to enter Holy Land; 40-year wandering": "رفض بني إسرائيل دخول الأرض المقدسة (التيه)",
    "Clarification of Jesus' nature (not God, not crucified)": "بيان طبيعة عيسى (ليس إلهاً ولم يُصلب)",
    "Closing verses 2:285-286 (the two final verses)": "خواتيم البقرة (2:285-286)",
    "Declaration of Immunity / Bara'a (9:1-29)": "البراءة (9:1-29)",
    "Dietary / food laws (lawful and prohibited)": "أحكام الأطعمة (الحلال والحرام)",
    "Disciples (Hawariyun) of Jesus declare allegiance": "الحواريون أنصار عيسى",
    "Election of the Family of Imran": "اصطفاء آل عمران",
    "Exposure of the Hypocrites (Tawba)": "فضح المنافقين (سورة التوبة)",
    "Hud and the People of 'Ad": "هود وقومه عاد",
    "Hudud punishments (theft and corruption on earth)": "الحدود (السرقة والفساد في الأرض)",
    "Ibrahim covenant verse 2:124 (Imam for mankind)": "آية عهد إبراهيم (2:124): إمام للناس",
    "Inheritance laws (fixed shares)": "أحكام المواريث (الفرائض)",
    "Jesus questioned on Day of Judgement about deification": "سؤال عيسى يوم القيامة عن ادعاء الألوهية",
    "Khilafah verse 2:30 (succession on earth)": "آية الخلافة (2:30)",
    "Longest verse 2:282 (debt and contract verse)": "أطول آية: آية الدَّين (2:282)",
    "Lot and the People of Sodom": "لوط وقومه",
    "Luqman's Counsel to His Son": "وصية لقمان لابنه",
    "Marriage and prohibited unions laws": "أحكام النكاح والمحرَّمات",
    "Middle nation verse 2:143": "آية الأمة الوسط (2:143)",
    "Moses-Pharaoh Extended Narrative (signs, plagues, exodus)": "قصة موسى وفرعون (الآيات والعذاب والخروج)",
    "Muhammad as messenger; mortality after Uhud rumour": "محمد رسول بعد إشاعة موته يوم أحد (3:144)",
    "Noah and the Flood": "نوح والطوفان",
    "Orphan rights and trustee duties": "حقوق اليتامى وواجبات الأوصياء",
    "Ramadan verse 2:185 (revelation of the Quran)": "آية رمضان (2:185)",
    "Rights and protections of women": "حقوق المرأة وحمايتها",
    "Ritual ablution (wudu) and tayammum prescription": "أحكام الوضوء والتيمم",
    "Scriptures of Abraham and Moses": "صحف إبراهيم وموسى",
    "Sheba's Dam Collapse Punishment": "انهيار سد مأرب (عذاب سبأ)",
    "Shu'ayb and the People of Madyan": "شعيب وأهل مدين",
    "Solomon and the Queen of Sheba": "سليمان وملكة سبأ",
    "Sons of Adam (Cain and Abel) story; first murder; raven": "ابنا آدم (قابيل وهابيل): أول قتل والغراب",
    "Table spread miracle (Ma'ida) requested by disciples of Jesus": "معجزة المائدة (طلب الحواريين)",
    "Tawaffa: Souls Taken at Death": "التوفّي: قبض الأرواح",
    "The Three Who Stayed Behind (9:117-118)": "الثلاثة الذين خُلِّفوا (9:117-118)",
    "The Three Who Stayed Behind (Ka'b ibn Malik et al.)": "الثلاثة الذين خُلِّفوا (كعب بن مالك وصاحباه)",
    "Verse of Mubahala (mutual cursing) with Christians of Najran": "آية المباهلة مع نصارى نجران",
    "Verse of Perfection of Religion (Farewell Pilgrimage)": "آية إكمال الدين (حجة الوداع)",
    "Ya-Sin Resurrection Emphasis": "تركيز سورة يس على البعث",
    "Narrative arc: Adam's creation and the angels' prostration": "قوس سردي: خلق آدم وسجود الملائكة",
    "Narrative arc: Bani Israel (covenant, exodus, golden calf, repentance)": "قوس سردي: بنو إسرائيل (الميثاق، الخروج، العجل، التوبة)",
    "Narrative arc: Ibrahim disputing with Nimrod over the Lord": "قوس سردي: محاجة إبراهيم النمرود",
    "Narrative arc: Ibrahim, Ismail and the building of the Kaaba": "قوس سردي: إبراهيم وإسماعيل وبناء الكعبة",
    "Narrative arc: Prohibition of riba (usury)": "قوس سردي: تحريم الربا",
    "Narrative arc: Talut and Jalut (Saul, David and Goliath)": "قوس سردي: طالوت وجالوت وداود",
    "Narrative arc: The Cow (sacrifice commanded to Bani Israel)": "قوس سردي: ذبح البقرة (الأمر لبني إسرائيل)",
    "Narrative arc: The Debt verse (longest verse, lending and witnesses)": "قوس سردي: آية الدَّين (أطول آية)",
    "Narrative arc: The traveller by the ruined town (death and resurrection)": "قوس سردي: المار على القرية الخاوية (الموت والبعث)",
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

    # Post-process: localize the graphify viewer UI chrome to Arabic
    localize_html_ui(output_path)
    print(f"Localized UI chrome to Arabic")
    print(f"File size: {Path(output_path).stat().st_size:,} bytes")


def localize_html_ui(html_path):
    """Replace English UI strings in the generated graphify HTML with Arabic.

    Targets the viewer chrome (search box, node info panel, communities header)
    that graphify hard-codes in English. Pure string replacement, no DOM parsing.
    """
    p = Path(html_path)
    text = p.read_text(encoding="utf-8")

    # UI string replacements
    replacements = [
        # Search box
        ('placeholder="Search nodes..."', 'placeholder="ابحث في العقد..." dir="rtl"'),
        # Node Info panel
        ('>Node Info<', '>معلومات العقدة<'),
        ('NODE INFO', 'معلومات العقدة'),
        ("<span class=\"empty\">Click a node to inspect it</span>",
         "<span class=\"empty\">انقر على عقدة للاطلاع عليها</span>"),
        # Communities panel
        ('>Communities<', '>المجموعات<'),
        ('COMMUNITIES', 'المجموعات'),
        ('>Select All<', '>تحديد الكل<'),
        # Per-node info template fields (template literals, replaced inline)
        ('Community: ${esc(n._community_name)}',
         'المجموعة: ${esc(n._community_name)}'),
        ('Source: ${esc(n._source_file || \'-\')}',
         'المصدر: ${esc(n._source_file || \'-\')}'),
        ('Degree: ${n._degree}', 'الدرجة: ${n._degree}'),
        ('Neighbors (${neighborIds.length})',
         'الجوار (${neighborIds.length})'),
        # Edge labels
        ('>EXTRACTED<', '>صريح<'),
        ('>INFERRED<', '>مستنبط<'),
        ('>AMBIGUOUS<', '>مبهم<'),
        # Direction (most important for an RTL Arabic experience)
        ('<html lang="en">', '<html lang="ar" dir="rtl">'),
        ('<html>', '<html lang="ar" dir="rtl">'),
    ]

    replaced_count = 0
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            replaced_count += 1

    p.write_text(text, encoding="utf-8")
    print(f"  Replaced {replaced_count}/{len(replacements)} UI strings")


if __name__ == "__main__":
    main()
