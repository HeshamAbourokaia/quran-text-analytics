#!/usr/bin/env python3
"""
Enrich the Quranic corpus with historical, chronological, and scholarly layers.

Adds 5 new dimensions on top of the existing surahs/entities/themes/special corpus:
- timeline/         Revelation phases (Early/Middle/Late Mecca + Early/Late Medina)
- events/           Major historical events (Cave of Hira through Farewell Pilgrimage)
- asbab_nuzul/      Classical occasions of revelation
- tafsir_traditions/ The 8 scholarly tafsir schools cited in the app's insights
- sciences/         Ulum al-Quran (Sciences of the Quran)

Also adds revelation-phase + chronological-rank metadata to every existing surah file.

Run:
    python3 scripts/enrich_quran_corpus.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CORPUS = ROOT / "quran_corpus"

# ───────────────────────────────────────────────────────────
# Traditional revelation order (surah_number -> chronological rank 1..114)
# ───────────────────────────────────────────────────────────
REV_ORDER = {96:1,68:2,73:3,74:4,1:5,111:6,81:7,87:8,92:9,89:10,93:11,94:12,103:13,100:14,108:15,102:16,107:17,109:18,105:19,113:20,114:21,112:22,53:23,80:24,97:25,91:26,85:27,95:28,106:29,101:30,75:31,104:32,77:33,50:34,90:35,86:36,54:37,38:38,7:39,72:40,36:41,25:42,35:43,19:44,20:45,56:46,26:47,27:48,28:49,17:50,10:51,11:52,12:53,15:54,6:55,37:56,31:57,34:58,39:59,40:60,41:61,42:62,43:63,44:64,45:65,46:66,51:67,88:68,18:69,16:70,71:71,14:72,21:73,23:74,32:75,52:76,67:77,69:78,70:79,78:80,79:81,82:82,84:83,30:84,29:85,83:86,2:87,8:88,3:89,33:90,60:91,4:92,99:93,57:94,47:95,13:96,55:97,76:98,65:99,98:100,59:101,24:102,22:103,63:104,58:105,49:106,66:107,64:108,61:109,62:110,48:111,5:112,9:113,110:114}

# Phase boundaries on the chronological rank (1..114)
PHASE_BOUNDS = [
    ("early-mecca",  1, 50,  "Early Meccan", "610-615 CE", "Year 1-5 of Prophethood"),
    ("middle-mecca", 51, 75, "Middle Meccan", "615-619 CE", "Year 5-9 of Prophethood"),
    ("late-mecca",   76, 86, "Late Meccan", "619-622 CE", "Year 9-13 of Prophethood"),
    ("early-medina", 87, 100, "Early Medinan", "622-628 CE", "Year 1-6 AH"),
    ("late-medina",  101, 114, "Late Medinan", "628-632 CE", "Year 6-10 AH"),
]

def phase_for_rank(rank):
    for slug, lo, hi, name, ce, ah in PHASE_BOUNDS:
        if lo <= rank <= hi:
            return slug, name, ce, ah
    return None


# ───────────────────────────────────────────────────────────
# Surah index helpers
# ───────────────────────────────────────────────────────────
def slugify(s):
    return re.sub(r"[^a-z0-9-]+", "-", s.lower()).strip("-")

def find_surah_file(n):
    matches = list((CORPUS / "surahs").glob(f"surah_{n:03d}_*.md"))
    return matches[0] if matches else None


# ───────────────────────────────────────────────────────────
# Layer 1: Revelation timeline phase documents
# ───────────────────────────────────────────────────────────
def gen_timeline():
    out_dir = CORPUS / "timeline"
    out_dir.mkdir(exist_ok=True)
    surahs_by_phase = {slug: [] for slug, *_ in PHASE_BOUNDS}
    for sn, rank in REV_ORDER.items():
        slug, *_ = phase_for_rank(rank)
        surahs_by_phase[slug].append((rank, sn))
    for slug, surahs in surahs_by_phase.items():
        surahs.sort()

    phase_descriptions = {
        "early-mecca": """The earliest revelations, after the first encounter with Gabriel in the Cave of Hira in 610 CE. These surahs are characterized by:

- **Short, intense, rhythmic verses** with frequent oath structures ("By the dawn", "By the heavens", "By the soul")
- **Pure tawhid** (oneness of God) as the central message
- **Vivid eschatology** - cosmic dissolution imagery, the Day of Judgment, paradise and hellfire
- **Comfort and command to the Prophet** during the initial difficult years
- **No legislative content yet** - this comes much later in Medina

The first revelation was Surah 96 Al-Alaq verses 1-5, in the Cave of Hira at age 40 of the Prophet. Public preaching began around 613 CE after a three-year period of private dawah.""",

        "middle-mecca": """Surahs revealed during the period of intensifying conflict with Quraysh leadership, when the Prophet's message was openly preached and openly opposed. These surahs are characterized by:

- **Medium-length verses** transitioning from short to longer structures
- **Detailed prophet narratives** begin to appear (Moses, Joseph, Abraham as model figures)
- **Critique of polytheism** with sustained argumentation
- **Promise of help** to the believers and warning to the disbelievers
- **The Isra and Mi'raj** (Night Journey) occurred in this period (~621 CE, before the Hijra)

The Migration to Abyssinia happened during this phase (615 CE) as some Muslims sought refuge under the Christian king. The boycott of Banu Hashim (~616-619 CE) ended near the end of this period.""",

        "late-mecca": """The final years in Mecca before the Hijra (migration to Medina). The Year of Sorrow (619 CE) saw the deaths of Abu Talib (the Prophet's uncle and protector) and Khadijah (his wife). These surahs are characterized by:

- **Longer surahs** with sustained narrative arcs
- **Extended prophet stories** (Yusuf in 12, the Cave Sleepers in 18)
- **Comfort and consolation** to the bereaved Prophet
- **Preparation for migration** through hints and direct commands
- **First pledges of Aqaba** (~621 and 622 CE) where Medinans pledged allegiance to the Prophet

The Hijra itself occurred at the end of this phase, in September 622 CE, marking Year 1 of the Hijri calendar.""",

        "early-medina": """The first years after the Hijra, when the Muslim community was established as a polity in Medina. These surahs are characterized by:

- **Legislative content begins** - rules for prayer, fasting, hajj, charity, marriage, inheritance
- **Community building** - the relationship between Muhajirun (migrants) and Ansar (helpers)
- **Engagement with the People of the Book** - Jews of Medina and Christians of Najran
- **Major military engagements** - Battle of Badr (2 AH/624 CE), Uhud (3 AH/625 CE), Trench (5 AH/627 CE)
- **Treaty of Hudaybiyyah** (6 AH/628 CE), called a "clear victory" by Surah 48 despite appearing as a defeat

The change of qibla from Jerusalem to Mecca (2 AH) is captured in Surah 2 Al-Baqara verses 142-150.""",

        "late-medina": """The final years before the Prophet's death in 632 CE. These surahs are characterized by:

- **Conquest of Mecca** (8 AH/630 CE) and mass entry into Islam
- **Tabuk expedition** (9 AH/630 CE) and the famous three-who-stayed-behind verses
- **At-Tawba (Surah 9)** - the only surah without Bismillah, declaring immunity from treaties with idolaters
- **Final farewell** - Surah 5 Al-Maida verse 3 ("Today I have perfected your religion for you") is often considered the last legislative verse, revealed during the Farewell Pilgrimage in 10 AH/632 CE
- **An-Nasr (Surah 110)** - traditionally considered the very last revealed surah, signaling the completion of the prophetic mission

The Prophet died in 11 AH/632 CE shortly after the Farewell Pilgrimage."""
    }

    for slug, lo, hi, name, ce, ah in PHASE_BOUNDS:
        surahs = surahs_by_phase[slug]
        lines = [
            f"# Revelation Phase: {name}",
            "",
            f"- **Approximate dates**: {ce}",
            f"- **Islamic calendar**: {ah}",
            f"- **Revelation order range**: {lo}-{hi} (of 114)",
            f"- **Number of surahs revealed in this phase**: {len(surahs)}",
            "",
            phase_descriptions[slug],
            "",
            "## Surahs revealed in this phase (in chronological order)",
            "",
        ]
        for rank, sn in surahs:
            sf = find_surah_file(sn)
            if sf:
                surah_name = sf.stem.replace(f"surah_{sn:03d}_", "")
                lines.append(f"- Rank #{rank}: [Surah {sn} ({surah_name})](../surahs/{sf.name})")
        (out_dir / f"phase_{slug}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  timeline/: {len(PHASE_BOUNDS)} phase documents")


# ───────────────────────────────────────────────────────────
# Layer 2: Major historical events
# ───────────────────────────────────────────────────────────
EVENTS = [
    {
        "slug": "cave-of-hira-first-revelation",
        "title": "The Cave of Hira: First Revelation",
        "year": "610 CE / Year 1 of Prophethood",
        "surahs": [96],
        "body": """The Prophet Muhammad ﷺ, at age 40, was in spiritual retreat in the Cave of Hira on Mount Nur outside Mecca when the angel Gabriel appeared and commanded "Iqra!" (Read! / Recite!). The first five verses of [Surah 96 Al-Alaq](../surahs/surah_096_al-alaq.md) were revealed:

> Recite in the name of your Lord who created.
> Created man from a clinging substance.
> Recite, and your Lord is the most Generous.
> Who taught by the pen.
> Taught man that which he knew not.

This event is the temporal origin of the Quran. The Prophet returned to his wife Khadijah trembling, and she comforted him and took him to her cousin Waraqa ibn Nawfal, a Christian scholar, who confirmed this was the same revelation given to Moses.

The cave of Hira is still visible today on Jabal an-Nur (Mountain of Light) outside Mecca.""",
    },
    {
        "slug": "public-preaching-begins",
        "title": "Public Preaching Begins",
        "year": "613 CE / Year 3 of Prophethood",
        "surahs": [74, 26],
        "body": """After approximately three years of private dawah to family and close companions (the first being his wife Khadijah, his cousin Ali, his servant Zayd, and his close friend Abu Bakr), the Prophet was commanded to begin public preaching with verses from [Surah 74 Al-Muddathir](../surahs/surah_074_al-muddaththir.md) and [Surah 26 Ash-Shu'ara](../surahs/surah_026_ash-shu-ara.md) ("And warn your closest kin", 26:214).

He ascended Mount Safa near the Kaaba and addressed the Quraysh tribes by name. From this point on, opposition from Quraysh leaders intensified. The early converts faced persecution, particularly those without tribal protection.""",
    },
    {
        "slug": "migration-to-abyssinia",
        "title": "First Migration to Abyssinia (Habasha)",
        "year": "615 CE / Year 5 of Prophethood",
        "surahs": [19],
        "body": """To escape persecution, a group of early Muslims migrated to Abyssinia (modern Ethiopia) under the just rule of the Christian king Najashi (Negus). This first migration of about 80 Muslims is historically significant as the first hijra in Islam.

When Quraysh sent envoys to Najashi demanding the Muslims be returned, the Muslim spokesperson Ja'far ibn Abi Talib recited verses from [Surah 19 Maryam](../surahs/surah_019_maryam.md) describing the birth of Jesus and his mother Mary. The Christian king wept and refused to extradite the Muslims, declaring that the Muslims worshipped the same God as Christians.""",
    },
    {
        "slug": "boycott-of-banu-hashim",
        "title": "The Boycott of Banu Hashim",
        "year": "616-619 CE / Year 7-9 of Prophethood",
        "surahs": [],
        "body": """Quraysh imposed a comprehensive social and economic boycott on the Prophet's clan (Banu Hashim) and the related clan of Banu Muttalib. The boycott document was hung inside the Kaaba and forbade trade, marriage, and any social interaction.

The boycotted families were confined to a small valley (Shi'b Abi Talib) outside Mecca. The hardship was severe; children could be heard crying from hunger, and the Muslims survived on very little.

The boycott ended around 619 CE when several Quraysh leaders felt sympathy and discovered that the boycott document had been eaten by termites except for the words "In Your Name, O God". The Year of Sorrow followed shortly after.""",
    },
    {
        "slug": "year-of-sorrow",
        "title": "Year of Sorrow (Aam al-Huzn)",
        "year": "619 CE / Year 10 of Prophethood",
        "surahs": [93, 94],
        "body": """Within a few months of each other, the Prophet's protective uncle Abu Talib and his beloved wife Khadijah passed away. Abu Talib's protection had shielded the Prophet from physical harm from Quraysh, and Khadijah had been his closest emotional support and the first to believe in him.

[Surah 93 Ad-Duha](../surahs/surah_093_ad-duha.md) and [Surah 94 Ash-Sharh](../surahs/surah_094_ash-sharh.md) are widely associated with this period as direct divine comfort to the bereaved Prophet:

> Your Lord has not forsaken you, nor does He hate you.
> The future will be better for you than the past.

The Prophet also made the difficult journey to Ta'if seeking new tribal protection during this year, but was rejected and stoned by the people of Ta'if.""",
    },
    {
        "slug": "isra-and-miraj",
        "title": "The Night Journey and Ascension (Isra and Mi'raj)",
        "year": "621 CE / Year 11-12 of Prophethood",
        "surahs": [17, 53],
        "body": """In a single night, the Prophet was taken from the Sacred Mosque in Mecca to the Furthest Mosque (Al-Masjid Al-Aqsa) in Jerusalem (the Isra), and from there ascended through the seven heavens (the Mi'raj).

[Surah 17 Al-Israa](../surahs/surah_017_al-israa.md) verse 1 references the night journey:

> Exalted is He who took His Servant by night from al-Masjid al-Haram to al-Masjid al-Aqsa, whose surroundings We have blessed.

[Surah 53 An-Najm](../surahs/surah_053_an-najm.md) verses 1-18 describe the heavenly ascension and the Prophet's vision near the Lote Tree of the Furthest Boundary.

During this ascension, the obligation of the five daily prayers was established. Some Quraysh ridiculed the Prophet's account, but Abu Bakr believed without hesitation, earning him the title As-Siddiq (the Truthful).""",
    },
    {
        "slug": "hijra-to-medina",
        "title": "The Hijra: Migration to Medina",
        "year": "622 CE / Year 1 AH",
        "surahs": [9, 8],
        "body": """After the second Pledge of Aqaba in 622 CE, Muslims began secretly migrating to Yathrib (later renamed Madinat an-Nabi, "the City of the Prophet"). Quraysh leaders plotted to assassinate the Prophet before he could leave.

On the night of the planned assassination, Ali ibn Abi Talib slept in the Prophet's bed as a decoy while the Prophet and Abu Bakr escaped. They hid in the Cave of Thawr for three days, then traveled north to Medina.

[Surah 9 At-Tawba](../surahs/surah_009_al-tawba.md) verse 40 references the cave incident: "When the two were in the cave, when he said to his companion, 'Do not grieve; indeed Allah is with us.'"

The Hijra marks Year 1 of the Hijri calendar, instituted by Caliph Umar ibn al-Khattab decades later. It is the foundational moment of the Muslim community as a political and legal entity, not merely a religious one.""",
    },
    {
        "slug": "battle-of-badr",
        "title": "The Battle of Badr",
        "year": "624 CE / 17 Ramadan, 2 AH",
        "surahs": [8, 3],
        "body": """The first major military engagement between Muslims and Quraysh. The Muslim force of ~313 faced a Quraysh army of ~1,000. Against expectations, the Muslims won decisively. Many Quraysh notables were killed including Abu Jahl.

[Surah 8 Al-Anfal](../surahs/surah_008_al-anfal.md) is dedicated almost entirely to Badr and its aftermath, with rulings on spoils of war (the "anfal" of the surah's name), the conduct of battle, and the spiritual lessons.

Verse 8:9 references angelic reinforcements: "I will reinforce you with a thousand of the angels in succession."

Badr cemented the Muslim community's identity and authority. The 313 companions who fought there held a special honored status throughout Islamic history.""",
    },
    {
        "slug": "battle-of-uhud",
        "title": "The Battle of Uhud",
        "year": "625 CE / 7 Shawwal, 3 AH",
        "surahs": [3],
        "body": """A year after Badr, Quraysh returned with ~3,000 fighters to avenge their losses. The Muslim force of ~700 met them at Mount Uhud outside Medina. Initially the Muslims gained the upper hand, but the archers stationed on a hill abandoned their post to collect spoils, allowing Khalid ibn al-Walid (then still a Quraysh general) to counter-attack from behind.

Many companions were martyred including the Prophet's uncle Hamza. The Prophet himself was wounded; a tooth was broken and his cheek was cut. A rumor spread that he had been killed.

[Surah 3 Aal-Imran](../surahs/surah_003_aal-imran.md) verses 121-180 deal directly with Uhud: its lessons, the test of faith, the prohibition against despair, and the conduct of warfare. Verse 3:144 directly addresses the false rumor of the Prophet's death.""",
    },
    {
        "slug": "battle-of-the-trench",
        "title": "The Battle of the Trench (Al-Khandaq)",
        "year": "627 CE / Shawwal, 5 AH",
        "surahs": [33],
        "body": """A coalition (al-Ahzab, "the Clans") of Quraysh, Ghatafan, and Jewish tribes besieged Medina with ~10,000 fighters. On the advice of the Persian convert Salman al-Farisi, the Muslims dug a trench across the unprotected northern approach to Medina, neutralizing the cavalry advantage.

The siege lasted about a month. After unrest within the coalition and a fierce sandstorm, the besiegers withdrew without a major battle.

[Surah 33 Al-Ahzab](../surahs/surah_033_al-ahzab.md) (named after this coalition) covers the trench siege extensively, including verses on the conduct of believers under pressure (33:9-27), the exposure of hypocrites, and rulings related to the Prophet's wives.""",
    },
    {
        "slug": "treaty-of-hudaybiyyah",
        "title": "The Treaty of Hudaybiyyah",
        "year": "628 CE / Dhul Qa'dah, 6 AH",
        "surahs": [48],
        "body": """The Prophet and ~1,400 companions traveled toward Mecca to perform Umrah (lesser pilgrimage), unarmed except for travel weapons. Quraysh blocked them at Hudaybiyyah outside Mecca.

After negotiations, a treaty was signed with terms that appeared deeply unfavorable to the Muslims: they would return without performing Umrah that year, the treaty would last 10 years, anyone fleeing Quraysh to the Muslims would be returned, but not vice versa. Many companions were dismayed, especially Umar ibn al-Khattab.

[Surah 48 Al-Fath](../surahs/surah_048_al-fath.md) (The Victory) was revealed on the return journey, declaring the treaty a "clear victory" (fath mubin). The wisdom became apparent: the truce gave the Muslims breathing room to consolidate, dawah spread peacefully (more entered Islam in the two years of the truce than in the entire prior 19 years), and the eventual treaty violation by Quraysh allies provided the casus belli for the bloodless Conquest of Mecca two years later.

The treaty is the classic case study of "the defeat that was victory" in Islamic political thought.""",
    },
    {
        "slug": "conquest-of-mecca",
        "title": "The Conquest of Mecca (Fath Makka)",
        "year": "630 CE / Ramadan, 8 AH",
        "surahs": [110, 48],
        "body": """After Quraysh allies broke the Hudaybiyyah treaty by attacking a tribe allied with the Muslims, the Prophet marched on Mecca with ~10,000 companions. Mecca surrendered virtually without bloodshed.

The Prophet entered the Kaaba, destroyed the 360 idols around it, and proclaimed general amnesty. Almost all Quraysh accepted Islam at this point.

[Surah 110 An-Nasr](../surahs/surah_110_an-nasr.md) (The Help) was revealed in connection with this event:

> When the help of Allah has come and the conquest, and you see people entering the religion of Allah in multitudes, then exalt your Lord with praise and seek His forgiveness.

This is traditionally considered the last revealed surah (or one of the last), and the Prophet understood it as a signal of his approaching death. The conquest of Mecca is the political and spiritual climax of the prophetic mission.""",
    },
    {
        "slug": "tabuk-expedition",
        "title": "The Tabuk Expedition",
        "year": "630 CE / Rajab, 9 AH",
        "surahs": [9],
        "body": """The last major military expedition under the Prophet. He led ~30,000 Muslims to Tabuk in northern Arabia in response to rumors of a Byzantine military buildup. The Byzantine force did not appear, and the expedition returned without battle.

The expedition was significant for testing the sincerity of the community: it occurred during intense heat and harvest season. Hypocrites in Medina invented elaborate excuses to avoid the journey. Three sincere believers (Ka'b ibn Malik, Murara ibn al-Rabi, and Hilal ibn Umayyah) stayed behind without excuse and were later subjected to a 50-day social boycott as a corrective measure.

[Surah 9 At-Tawba](../surahs/surah_009_al-tawba.md) verses 117-118 directly address these three and their eventual forgiveness, providing one of the most personal asbab al-nuzul in the Quran. The surah as a whole is heavily focused on the Tabuk context and the exposure of hypocrites.""",
    },
    {
        "slug": "farewell-pilgrimage",
        "title": "The Farewell Pilgrimage (Hajjat al-Wada)",
        "year": "632 CE / Dhul Hijjah, 10 AH",
        "surahs": [5],
        "body": """The Prophet's only complete Hajj after the migration. He delivered the Farewell Sermon on the plain of Arafat, addressing ~100,000 companions on the equality of all believers, the inviolability of life and property, the rights of women, the prohibition of usury, and the completion of the religion.

[Surah 5 Al-Maida](../surahs/surah_005_al-ma-ida.md) verse 3 was revealed during this Hajj and is widely considered the last legislative verse:

> Today I have perfected for you your religion and completed My favor upon you and have approved for you Islam as your religion.

When Umar ibn al-Khattab heard this verse, he wept, recognizing that the perfection of the religion meant the approaching end of the Prophet's life.

The Prophet returned to Medina and passed away approximately three months later, in Rabi' al-Awwal 11 AH (June 632 CE), having completed the prophetic mission.""",
    },
]

def gen_events():
    out_dir = CORPUS / "events"
    out_dir.mkdir(exist_ok=True)
    for ev in EVENTS:
        lines = [
            f"# {ev['title']}",
            "",
            f"- **Date**: {ev['year']}",
        ]
        if ev["surahs"]:
            surah_links = []
            for sn in ev["surahs"]:
                sf = find_surah_file(sn)
                if sf:
                    surah_links.append(f"[Surah {sn}](../surahs/{sf.name})")
            lines.append(f"- **Surahs revealed in connection with this event**: {', '.join(surah_links)}")
        lines.append("")
        lines.append(ev["body"])
        (out_dir / f"event_{ev['slug']}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  events/: {len(EVENTS)} historical event documents")


# ───────────────────────────────────────────────────────────
# Layer 3: Asbab al-Nuzul (occasions of revelation)
# ───────────────────────────────────────────────────────────
ASBAB = [
    {
        "slug": "change-of-qibla",
        "title": "The Change of Qibla from Jerusalem to Mecca",
        "verses": "2:142-150",
        "context": "Approximately 16 months after the Hijra (2 AH / 624 CE), the Prophet was praying in the mosque of Bani Salamah in Medina facing Jerusalem when verse 2:144 was revealed commanding the shift to face the Kaaba in Mecca. The mosque is still called Masjid al-Qiblatayn (the Mosque of Two Qiblas) because the Prophet completed the prayer in two directions. The Jews of Medina had been critical of the Muslims for not having their own qibla, and this change established the independent identity of the Muslim community."
    },
    {
        "slug": "verses-of-hijab",
        "title": "The Hijab Verses",
        "verses": "33:53, 33:59, 24:31",
        "context": "Verse 33:53 was revealed at the wedding feast of the Prophet's marriage to Zaynab bint Jahsh (5 AH), when some guests lingered after the meal causing discomfort. The verse established etiquette for entering the Prophet's homes and instituted the hijab for his wives. Verse 33:59 extends similar dignity-protective dress to all believing women. Verse 24:31 establishes modesty rules for all believers."
    },
    {
        "slug": "the-slander-of-aisha",
        "title": "The Slander of Aisha (Al-Ifk)",
        "verses": "24:11-20",
        "context": "Returning from an expedition (5 AH), Aisha was accidentally left behind by the caravan after retrieving a lost necklace. A young companion named Safwan ibn al-Mu'attal escorted her back to Medina. The hypocrites led by Abdullah ibn Ubayy spread slanderous rumors. For about a month the Prophet was uncertain and Aisha was deeply distressed. Verses 24:11-20 then declared her innocence and rebuked those who spread slander, establishing the legal requirement of four witnesses for accusations of unchastity and the punishment for false accusation. This case became the foundational legal precedent for protecting reputation."
    },
    {
        "slug": "the-three-who-stayed-behind",
        "title": "The Three Who Stayed Behind from Tabuk",
        "verses": "9:117-118",
        "context": "Three sincere companions (Ka'b ibn Malik, Murara ibn al-Rabi, and Hilal ibn Umayyah) did not join the Tabuk expedition in 9 AH despite having no real excuse. Upon the Prophet's return, they refused to invent excuses and confessed their failure. The Prophet ordered the community to socially boycott them for 50 days. They were finally forgiven when verses 9:117-118 were revealed: 'And [He turned] to the three who were left behind...' Ka'b's own narration of this incident is one of the longest first-person testimonies in the hadith collections, preserved as a model of sincere repentance."
    },
    {
        "slug": "ayat-al-kursi",
        "title": "Ayat al-Kursi: The Throne Verse",
        "verses": "2:255",
        "context": "Verse 2:255, the most famous single verse in the Quran, declares God's absolute sovereignty, knowledge, and power. The Prophet described it as the greatest verse in the Quran. While not tied to a specific narrative occasion, scholars classify it as part of the late Medinan teaching on creed (aqidah), revealed during the establishment of the Muslim community when articulating the doctrine of God against pagan, Christian, and Jewish theological positions was central."
    },
    {
        "slug": "verse-of-mubahala",
        "title": "The Verse of Mubahala (Mutual Imprecation)",
        "verses": "3:61",
        "context": "A Christian delegation from Najran came to Medina (9 AH or 10 AH) to debate the nature of Jesus. After theological discussion failed to convince either side, the Prophet proposed mubahala: each side would bring their closest family members and invoke God's curse on the lying party. The Prophet brought Ali, Fatima, Hassan, and Hussein. The Christians declined the mubahala and instead negotiated a peace treaty paying jizya."
    },
    {
        "slug": "the-three-companions",
        "title": "Verses Praising the First Three Converts",
        "verses": "9:100, 9:117",
        "context": "Verse 9:100 honors 'the first forerunners from among the Muhajirun and the Ansar and those who followed them in good conduct.' This was understood by the early community to refer particularly to the earliest converts: Khadijah (first overall), Ali (first young male), Zayd ibn Haritha (first freed slave), Abu Bakr (first non-family adult male), and the small circle of original Meccan believers who endured the boycott and early persecution."
    },
    {
        "slug": "verse-of-perfection",
        "title": "The Verse of Perfection of Religion",
        "verses": "5:3",
        "context": "Revealed during the Farewell Pilgrimage (10 AH / 632 CE) at Arafat on a Friday. When the Prophet recited this verse on his camel, the camel had to kneel because the weight of revelation was so heavy. Umar ibn al-Khattab and several companions wept upon hearing it, recognizing it as a sign of the Prophet's approaching death. The Prophet died approximately three months later. The verse is the latest legislative verse in the Quran and seals the canonical body of Islamic law."
    },
    {
        "slug": "verses-of-marriage-to-zaynab",
        "title": "Verses on the Marriage to Zaynab bint Jahsh",
        "verses": "33:37-40",
        "context": "Zaynab was the Prophet's cousin who had married his adopted son Zayd ibn Haritha. The marriage was unhappy and ended in divorce. Adoption in pre-Islamic Arabia created kinship that prohibited marriage between the adopting father and the adopted son's ex-wife. Verses 33:37-40 abolished this aspect of adoption law, commanded the Prophet to marry Zaynab, and clarified that adoption does not create biological kinship (5 AH). This is one of the only places in the Quran where a verse names a Muslim (Zayd) directly."
    },
    {
        "slug": "the-pleading-woman",
        "title": "The Pleading Woman (Al-Mujadila)",
        "verses": "58:1-4",
        "context": "Khawla bint Tha'laba came to the Prophet complaining that her husband Aws ibn al-Samit had pronounced zihar against her (a pre-Islamic divorce formula equating her to his mother's back). She argued and pleaded with the Prophet who initially had no ruling to give her. She continued arguing while raising her hands in dua to God. [Surah 58 Al-Mujadila](../surahs/surah_058_al-mujadilah.md) (named after her) was revealed in response, opening with: 'Allah has heard the speech of the one who pleaded with you concerning her husband.' The verses prohibited zihar and prescribed expiation. Khawla is one of the rare individuals whose argument God directly responds to in the Quran."
    },
    {
        "slug": "verses-of-bara-immunity",
        "title": "The Declaration of Immunity",
        "verses": "9:1-29",
        "context": "Revealed in 9 AH after multiple violations of treaties by Arabian polytheist tribes. The opening verses of [Surah 9 At-Tawba](../surahs/surah_009_al-tawba.md) (the only surah without Bismillah) declared the end of all treaties with idolaters who had violated their terms, gave them four months to either accept Islam or face military consequences. Ali ibn Abi Talib was sent to publicly proclaim these verses during the Hajj season, marking a strategic shift in the Muslim community's policy toward continuing polytheism in Arabia."
    },
    {
        "slug": "verses-on-orphans-after-uhud",
        "title": "Verses on Orphans and Widows after Uhud",
        "verses": "4:1-3, 4:127",
        "context": "After the Battle of Uhud (3 AH), many companions were martyred, leaving widows and orphans. [Surah 4 An-Nisa](../surahs/surah_004_an-nisaa.md) verses 1-3 establish family law to protect orphans' property and regulate marriage (including the rules around plural marriage in the context of orphan welfare). Verse 4:127 returns to the same theme later, ensuring orphans' rights were not exploited through manipulative marriage arrangements. The wartime context of these revelations is crucial for understanding their original purpose: protection of vulnerable dependents."
    },
    {
        "slug": "verse-of-light",
        "title": "Ayat an-Nur: The Light Verse",
        "verses": "24:35",
        "context": "Verse 24:35 is the most poetic theological verse in the Quran, comparing God's light to a niche containing a lamp inside a glass like a brilliant star, lit from a blessed olive tree neither of the east nor the west whose oil would almost glow without fire. Classical scholars (Ghazali wrote 'Mishkat al-Anwar' on this single verse) and Sufi tradition have produced extensive commentary on its layered meaning. Revealed in the late Medinan period as part of the broader Surah An-Nur which deals primarily with social ethics, the Light Verse stands out as a metaphysical centerpiece."
    },
    {
        "slug": "verses-of-inheritance",
        "title": "The Inheritance Verses",
        "verses": "4:11, 4:12, 4:176",
        "context": "Revealed in the early-to-middle Medinan period, these three verses establish the foundational Quranic inheritance law (mirath), one of the most mathematically detailed legal frameworks in any scripture. The 'fara'id' (fixed shares) ensured that women, children, parents, and spouses all had defined inheritance rights at a time when pre-Islamic Arab practice often denied inheritance to women and minor children. The Islamic inheritance system based on these three verses became the foundation of one of the major branches of classical Islamic jurisprudence, with entire treatises devoted to its mathematical applications."
    },
    {
        "slug": "verse-of-pilgrimage-call",
        "title": "Abraham's Call to Pilgrimage",
        "verses": "22:27",
        "context": "Verse 22:27 in [Surah 22 Al-Hajj](../surahs/surah_022_al-hajj.md) records the divine command to Abraham (Ibrahim) to proclaim the pilgrimage to humanity: 'And proclaim to the people the Hajj; they will come to you on foot and on every lean camel; they will come from every distant pass.' Classical tradition holds that Abraham stood on a high rock and called out, and God caused his voice to reach every soul that would ever live, every person who would respond to the call across generations and continents. This is the founding charter of the Hajj rite that connects every Muslim's annual pilgrimage to its Abrahamic origin."
    },
]

def gen_asbab():
    out_dir = CORPUS / "asbab_nuzul"
    out_dir.mkdir(exist_ok=True)
    for a in ASBAB:
        lines = [
            f"# Asbab al-Nuzul: {a['title']}",
            "",
            f"- **Quranic reference**: {a['verses']}",
            "",
            "## Occasion of Revelation",
            "",
            a["context"],
            "",
            "## Scholarly significance",
            "",
            "Asbab al-Nuzul (occasions of revelation) is one of the core disciplines of [Ulum al-Quran](../sciences/asbab-al-nuzul-methodology.md). Understanding the historical occasion sharpens the interpretive meaning of a verse without restricting its general applicability. The primary classical source for asbab al-nuzul is the work of Al-Wahidi (d. 1076 CE) titled 'Asbab al-Nuzul'.",
        ]
        (out_dir / f"asbab_{a['slug']}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  asbab_nuzul/: {len(ASBAB)} occasion documents")


# ───────────────────────────────────────────────────────────
# Layer 4: Tafsir traditions / scholars
# ───────────────────────────────────────────────────────────
TAFSIR_SCHOLARS = [
    {
        "slug": "al-tabari",
        "name": "Imam Al-Tabari",
        "arabic": "أبو جعفر محمد بن جرير الطبري",
        "dates": "224-310 AH / 838-923 CE",
        "school": "Jami al-Bayan an Ta'wil ay al-Quran (the foundational Sunni tafsir)",
        "approach": "Tafsir bil-Mathur (interpretation through transmitted narration)",
        "body": """Al-Tabari is regarded as the father of Quranic exegesis. His monumental tafsir, often simply called 'Tafsir al-Tabari', is the earliest complete surviving Sunni exegesis and the source for virtually all subsequent classical tafsirs. He systematically gathered all available reports from the Prophet, the Companions, and the Tabi'un on each verse, organized them by chain of transmission, and offered his own judgment after presenting the evidence.

His method established the genre of tafsir bil-mathur (interpretation through transmitted narration), which prioritizes the historical understanding of the earliest Muslim generations over later speculation. Al-Tabari was also a major historian and jurist; his historical work 'Tarikh al-Rusul wal-Muluk' is among the most important sources for early Islamic history.

Approximately 30 volumes in modern editions. Foundational for any classical study of the Quran."""
    },
    {
        "slug": "ibn-kathir",
        "name": "Ibn Kathir",
        "arabic": "إسماعيل بن عمر بن كثير",
        "dates": "701-774 AH / 1300-1373 CE",
        "school": "Tafsir al-Quran al-Azim",
        "approach": "Tafsir bil-Mathur (transmitted) with critical sifting of weak narrations",
        "body": """Ibn Kathir is the most widely-read tafsir in modern Sunni circles. A student of Ibn Taymiyyah, he applied stricter criteria for hadith authenticity than Al-Tabari, weeding out weak and fabricated narrations that had accumulated in the tradition.

His method: explain a verse with other verses first (Quran interpreted by Quran), then with authenticated hadith, then with sayings of the Companions, then judiciously with sayings of the Tabi'un. He was particularly cautious about Israiliyyat (Jewish/Christian narratives that had entered tafsir traditions).

Tafsir Ibn Kathir is the recommended classical tafsir for general Muslims today. It is widely translated into English, Urdu, and dozens of other languages, and is the default Sunni reference in mainstream religious education."""
    },
    {
        "slug": "al-qurtubi",
        "name": "Al-Qurtubi",
        "arabic": "أبو عبد الله محمد بن أحمد القرطبي",
        "dates": "600-671 AH / 1204-1273 CE",
        "school": "Al-Jami li-Ahkam al-Quran (focus on legal rulings)",
        "approach": "Tafsir Fiqhi (jurisprudential tafsir)",
        "body": """Al-Qurtubi was a Maliki jurist from Cordoba (later moved to Egypt). His tafsir specializes in extracting legal rulings (ahkam) from verses, making it the primary reference for Maliki jurisprudence applied to Quranic interpretation.

For verses with jurisprudential content (marriage, divorce, inheritance, transactions, criminal law, etc.) he typically presents the positions of the four Sunni madhabs (Hanafi, Maliki, Shafi'i, Hanbali) along with their evidence, then weighs the strongest position.

He balances his legal focus with linguistic analysis, hadith citations, asbab al-nuzul, and ethical reflection. Approximately 20 volumes. Essential reference for any study of Islamic law as derived from the Quran."""
    },
    {
        "slug": "al-sadi",
        "name": "Al-Sa'di",
        "arabic": "عبد الرحمن بن ناصر السعدي",
        "dates": "1307-1376 AH / 1889-1956 CE",
        "school": "Taysir al-Karim al-Rahman fi Tafsir Kalam al-Mannan (the simplified tafsir)",
        "approach": "Tafsir Muyassar (accessible tafsir for general audiences)",
        "body": """Al-Sa'di was a modern Saudi scholar whose tafsir achieves a remarkable balance: scholarly accurate but written in accessible, contemporary Arabic suitable for educated general readers (not just specialists).

His method strips away the long chains of narration that make classical tafsirs daunting and presents the meaning directly with brief supporting evidence. The result is a single-volume work (or two compact volumes) that covers the entire Quran in approximately 1000 pages.

Highly recommended for new students of tafsir and for anyone seeking a sound, mainstream Sunni reading of the Quran without committing to the multi-volume classical works. Widely translated."""
    },
    {
        "slug": "ibn-ashur",
        "name": "Ibn Ashur",
        "arabic": "محمد الطاهر بن عاشور",
        "dates": "1296-1393 AH / 1879-1973 CE",
        "school": "Al-Tahrir wa al-Tanwir (the comprehensive modern tafsir)",
        "approach": "Tafsir Lughawi-Balaghi (linguistic-rhetorical analysis)",
        "body": """Ibn Ashur was a Tunisian Maliki scholar, Sheikh al-Islam of Tunisia, and a major figure in modern Islamic thought. His 30-volume tafsir 'Al-Tahrir wa al-Tanwir' (Liberation and Enlightenment) is considered one of the great Arabic scholarly achievements of the 20th century.

His distinctive contribution: sustained attention to Arabic linguistic and rhetorical sciences (balagha, fasaha, eloquence) to derive deeper interpretive insight. He treats every surah as a coherent literary unit with internal thematic structure, an approach he pioneered systematically. He also incorporates modern scientific knowledge where relevant and addresses contemporary intellectual challenges.

His other major work 'Maqasid al-Shari'ah' helped revive the science of higher objectives of Islamic law in modern times. Major influence on contemporary academic and reformist Islamic scholarship."""
    },
    {
        "slug": "al-sharawi",
        "name": "Sheikh Al-Sha'rawi",
        "arabic": "محمد متولي الشعراوي",
        "dates": "1329-1419 AH / 1911-1998 CE",
        "school": "Khawatir al-Sha'rawi hawl al-Quran al-Karim (Reflections)",
        "approach": "Tafsir Khawatiri (devotional reflections)",
        "body": """Sheikh Al-Sha'rawi was an Egyptian scholar whose televised Quran reflections reached tens of millions across the Arab world from the 1980s through the 1990s. His tafsir is technically a transcription of his television series, not a written work composed for publication.

His method is conversational and reflective rather than systematic. He pauses on individual phrases or single words and unfolds layers of meaning, often using everyday examples, simple analogies, and emotional resonance to convey deep spiritual points. His ability to make a tafsir lesson feel like an intimate conversation about life's questions made him uniquely beloved.

Approximately 20 volumes covering the entire Quran (with some surahs treated more fully than others). Essential for understanding 20th-century Arab popular Quranic spirituality."""
    },
    {
        "slug": "sayyid-qutb",
        "name": "Sayyid Qutb",
        "arabic": "سيد قطب",
        "dates": "1324-1386 AH / 1906-1966 CE",
        "school": "Fi Zilal al-Quran (In the Shade of the Quran)",
        "approach": "Tafsir Adabi-Haraki (literary-activist)",
        "body": """Sayyid Qutb was an Egyptian writer, literary critic, and Islamic thinker. He composed 'Fi Zilal al-Quran' primarily during years of imprisonment under Nasser's regime, completing the final volumes shortly before his execution in 1966.

His tafsir is distinguished by literary sensitivity (he was a published literary critic before turning to religious scholarship), thematic coherence (treating each surah as a unified message), and an emphasis on the Quran as a movement-shaping text rather than merely a source of legal rulings or theological propositions. His introductions to each surah, summarizing its central themes and contemporary relevance, are particularly admired.

His broader Islamist political ideas (especially in later works like 'Milestones') are controversial and contested. But 'Fi Zilal al-Quran' as a literary-spiritual reading of the Quran is widely respected even among scholars who reject his political views. Approximately 8 large volumes."""
    },
    {
        "slug": "al-samarrai",
        "name": "Dr. Fadel Al-Samarrai",
        "arabic": "فاضل صالح السامرائي",
        "dates": "1352 AH-present / 1933-present",
        "school": "Lamasat Bayania (Linguistic Touches) and related works",
        "approach": "Tafsir Bayani (rhetorical and linguistic precision)",
        "body": """Dr. Al-Samarrai is an Iraqi scholar specializing in Arabic grammar and Quranic rhetoric. His work focuses on precise linguistic analysis: why does the Quran use this particular word and not its near-synonym? Why this verb form and not that one? Why this word order? Why singular here and plural there?

His most popular work is the television series and book 'Lamasat Bayania fi Nusus min al-Tanzil' (Linguistic Touches in Quranic Texts), where he treats individual verses as case studies in Arabic eloquence. He has also published books on Quranic word choice, the structure of specific surahs, and the rhetorical patterns of the Quran.

Modern, currently active scholar. Several of his linguistic insights are captured in the app's Tafsir Insights page, including the analysis of 'tawaffa' across verses 39:42 and 3:55. His YouTube and television lectures have introduced precise rhetorical reading of the Quran to a contemporary Arab-speaking audience."""
    },
]

def gen_tafsir_traditions():
    out_dir = CORPUS / "tafsir_traditions"
    out_dir.mkdir(exist_ok=True)
    for t in TAFSIR_SCHOLARS:
        lines = [
            f"# {t['name']} ({t['arabic']})",
            "",
            f"- **Dates**: {t['dates']}",
            f"- **Major work**: {t['school']}",
            f"- **Methodological approach**: {t['approach']}",
            "",
            t["body"],
        ]
        (out_dir / f"scholar_{t['slug']}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"  tafsir_traditions/: {len(TAFSIR_SCHOLARS)} scholar documents")


# ───────────────────────────────────────────────────────────
# Layer 5: Ulum al-Quran (Sciences of the Quran)
# ───────────────────────────────────────────────────────────
SCIENCES = [
    {
        "slug": "asbab-al-nuzul-methodology",
        "title": "Asbab al-Nuzul: Occasions of Revelation",
        "body": """Asbab al-Nuzul (literally 'reasons for revelation') is the science of identifying the historical occasions surrounding the revelation of specific verses. It is one of the core disciplines of Ulum al-Quran.

The classical rule articulated by Al-Wahidi (the genre's founding author) is: 'The lessons drawn from a verse depend on the generality of its words, not on the specificity of its occasion.' That is, even when we know the precise event a verse was revealed about, the verse's binding meaning applies to all comparable situations forever.

The primary classical work is Al-Wahidi's 'Asbab al-Nuzul' (d. 1076 CE). Imam Suyuti later wrote 'Lubab al-Nuqul fi Asbab al-Nuzul' which became the standard reference. Not every verse has an identified occasion; many were revealed as general principles without a specific narrative context. The asbab tradition only addresses verses where authentic narration links them to identifiable events.

See: [Asbab al-Nuzul examples](../asbab_nuzul/) for specific cases."""
    },
    {
        "slug": "nasikh-mansukh",
        "title": "Nasikh wal-Mansukh: Abrogating and Abrogated Verses",
        "body": """Nasikh wal-Mansukh is the science studying which Quranic rulings supersede earlier rulings revealed during the gradual unfolding of the legal framework. The verses revealed earlier on the same subject are described as 'mansukh' (abrogated), and the later replacing verses are 'nasikh' (abrogating).

The clearest classical example: the prohibition of alcohol. Three stages of revelation:
1. Surah 2:219 - 'They ask you about wine and gambling. Say, in them is great sin and some benefit, but their sin is greater than their benefit.'
2. Surah 4:43 - 'Do not approach prayer while in a drunken state.'
3. Surah 5:90-91 - 'O you who believe, intoxicants and gambling and idols and divining arrows are an abomination of Satan's handiwork; so avoid them.'

The earliest two verses are considered abrogated by the third, which establishes complete prohibition.

Major scholarly disagreement exists on the SCOPE of abrogation. Classical scholars identified anywhere from ~5 to ~250 cases of abrogation. Modern scholarship tends toward the minimal end, holding that many alleged 'abrogations' are better understood as different applications to different circumstances, not actual cancellation."""
    },
    {
        "slug": "muhkam-mutashabih",
        "title": "Muhkam and Mutashabih: Clear and Allegorical Verses",
        "body": """Surah 3 (Aal-Imran) verse 7 establishes that the Quran contains two types of verses:

- **Muhkam**: clear, decisive, unambiguous verses that form the 'mother of the book' (umm al-kitab). These are the foundation of doctrine and law.
- **Mutashabih**: verses whose meaning admits multiple possibilities, often dealing with the metaphysical or eschatological - God's attributes (His 'hand', His 'face', His 'establishment' on the throne), the realities of paradise and hellfire, the broken letters at the start of 29 surahs (alif lam mim, etc.).

The verse warns: those with deviation in their hearts pursue what is mutashabih seeking discord and seeking its [hidden] interpretation. But no one knows its true interpretation except Allah.

Three classical positions emerged on mutashabih:
1. **Tafwid** (consignment): accept the literal words and consign true meaning to God; do not interpret further.
2. **Ta'wil** (interpretation): interpret metaphorically (God's 'hand' means His power; His 'establishment' means His sovereignty).
3. **Ithbat bila kayf** (affirmation without 'how'): affirm the attributes as the text states without specifying how or comparing to creation.

These three positions correspond roughly to the Atharis (literalists), Ash'aris/Maturidis (interpretive theologians), and the Salafi position respectively. Disagreement between these schools continues to shape modern Sunni theological discourse."""
    },
    {
        "slug": "makki-madani-classification",
        "title": "Makki and Madani: Meccan and Medinan Classification",
        "body": """Every surah is traditionally classified as either Meccan (revealed before the Hijra in 622 CE) or Medinan (revealed after). The classification typically uses revelation circumstance, not geographic location: a verse revealed during the Tabuk expedition (in northern Arabia) but after the Hijra is Medinan; a verse revealed during the Conquest of Mecca (in Mecca itself) but after the Hijra is also Medinan.

Total counts: 86 surahs are Meccan, 28 are Medinan, with widely shared scholarly agreement.

Classical scholars identified distinguishing literary features:

**Meccan features**:
- Short, rhythmic verses with frequent oaths
- Pure tawhid (oneness of God), eschatology, prophet stories
- 'Kalla' particle (used for emphatic refutation, common in early Meccan)
- 'Ya ayyuha al-nas' (O mankind, addressing all humanity)
- The broken letters at chapter openings appear mostly in Meccan surahs
- Reference to earlier prophets and their nations

**Medinan features**:
- Longer verses with sustained argumentation
- Legislation and detailed legal rulings
- Discussion of the People of the Book (Jews and Christians)
- 'Ya ayyuha alladhina amanu' (O you who believe, addressing the believing community)
- References to the hypocrites, the battles, and the community of Medina

The Meccan-Madani distinction is foundational for understanding the historical-theological context of any verse and is a prerequisite for serious tafsir."""
    },
    {
        "slug": "qiraat-readings",
        "title": "The Ten Qira'at: Canonical Readings of the Quran",
        "body": """The Quranic text was orally transmitted from the Prophet to the Companions in slightly varying recitation patterns called qira'at (readings). The Prophet authorized seven 'ahruf' (modes) of recitation, which evolved into ten canonical qira'at attributed to specific imams.

The seven canonical readers were established by Ibn Mujahid in the 10th century CE:
- Nafi of Medina
- Ibn Kathir of Mecca (different person from the tafsir author)
- Abu Amr of Basra
- Ibn Amir of Damascus
- Asim of Kufa
- Hamza of Kufa
- Al-Kisai of Kufa

Three more were added later by Ibn al-Jazari: Abu Ja'far of Medina, Yaqub of Basra, Khalaf of Kufa.

Each reader has two main 'rawis' (transmitters). The most widespread reading today is **Hafs from Asim** (used in printed Saudi mushafs and most of the Muslim world). The second most common is **Warsh from Nafi** (used in much of North and West Africa). Other readings remain in use in specific regions.

Differences between qira'at are usually minor: vowel marks, pronunciation features, occasionally word forms. They never differ on doctrine, law, or essential meaning. The existence of multiple authentic qira'at is itself a sign of authenticity, since they were preserved through independent oral chains and corroborate each other.

The science of qira'at is one of the most technically demanding fields of Islamic studies."""
    },
    {
        "slug": "i-jaz-al-quran",
        "title": "I'jaz al-Quran: The Inimitability of the Quran",
        "body": """I'jaz (literally 'incapacitation' or 'rendering unable') refers to the Quran's challenge to humanity to produce something comparable, and the inability of any attempt to match it. The challenge is articulated several times within the Quran itself:

- Surah 17 Al-Israa verse 88: 'If mankind and jinn gathered to produce the like of this Quran, they could not produce the like of it, even if they backed each other up.'
- Surah 11 Hud verse 13: 'Bring ten surahs the like thereof...'
- Surah 2 Al-Baqara verse 23: 'Bring a single surah like it...'

Classical scholars identified several dimensions of i'jaz:

1. **Linguistic/rhetorical i'jaz** (al-Khattabi, al-Jurjani, al-Baqillani): the Quran's unique combination of brevity and depth, its musical prose, its untranslatable nazm (word arrangement). This is the primary classical understanding.

2. **Scientific i'jaz** (modern): the Quran's references to natural phenomena that align with later scientific discoveries (embryology in 23:14, expanding universe in 51:47, mountains as pegs in 78:7, iron as 'sent down' in 57:25 echoing modern astrophysics).

3. **Predictive i'jaz**: prophecies of historical events fulfilled after revelation (the Byzantine-Persian war outcome predicted in 30:2-5, the conquest of Mecca predicted in 48:27).

4. **Numerical i'jaz** (modern): the 19-pattern, word-pair frequency symmetries, the chapter-verse parity balance, the Bismillah occurrences. Most controversial among scholars; some accept it, others view it skeptically.

5. **Legislative i'jaz**: the comprehensive social and legal system derived from a relatively small body of text.

6. **Eschatological/spiritual i'jaz**: the unique impact of recitation on the heart and the inability to imitate its emotional-spiritual power."""
    },
]

def gen_sciences():
    out_dir = CORPUS / "sciences"
    out_dir.mkdir(exist_ok=True)
    for s in SCIENCES:
        (out_dir / f"{s['slug']}.md").write_text(f"# {s['title']}\n\n{s['body']}", encoding="utf-8")
    print(f"  sciences/: {len(SCIENCES)} Ulum al-Quran documents")


# ───────────────────────────────────────────────────────────
# Augment surah files with revelation-phase metadata
# ───────────────────────────────────────────────────────────
def augment_surahs():
    augmented = 0
    for n in range(1, 115):
        sf = find_surah_file(n)
        if not sf:
            continue
        text = sf.read_text(encoding="utf-8")
        if "**Revelation order**" in text:
            continue  # already augmented
        rank = REV_ORDER.get(n)
        if not rank:
            continue
        slug, name, ce, ah = phase_for_rank(rank)
        # Find the metadata block (lines starting with "- **") and inject before "## Verses"
        injection = (
            f"- **Revelation order (chronological)**: #{rank} of 114\n"
            f"- **Revelation phase**: [{name}](../timeline/phase_{slug}.md) ({ce}, {ah})\n"
        )
        text = text.replace("## Verses", injection + "\n## Verses", 1)
        sf.write_text(text, encoding="utf-8")
        augmented += 1
    print(f"  surahs/: augmented {augmented} files with revelation-phase metadata")


def update_corpus_readme():
    body = """# Quran Corpus for Knowledge Graph

Source documents for a graphify-based knowledge graph of the Quran itself (not the code).

## Structure

- `surahs/` (114) - one per surah, with full Arabic + English verse text, themes, entities, and revelation phase
- `entities/` (36) - one per major named figure (25 prophets), other figures (Mary, Pharaoh, Iblis, Gabriel), place (7), and divine name (4)
- `themes/` (10) - one per scholarly thematic cluster
- `special/` (6) - distinctive structural patterns
- `timeline/` (5) - the five revelation phases (Early/Middle/Late Mecca + Early/Late Medina)
- `events/` (15) - major historical events from Cave of Hira through the Farewell Pilgrimage
- `asbab_nuzul/` (15) - classical occasions of revelation (change of qibla, slander of Aisha, etc.)
- `tafsir_traditions/` (8) - the major tafsir scholars referenced in the app
- `sciences/` (6) - Ulum al-Quran (sciences of the Quran)

Total: ~215 markdown documents covering text, history, scholarship, and structural patterns.

## Regenerate

```bash
python3 scripts/build_quran_corpus.py    # base layer (surahs, entities, themes, special)
python3 scripts/enrich_quran_corpus.py   # adds timeline, events, asbab_nuzul, tafsir_traditions, sciences
```

Re-running is idempotent (overwrites files in place).

## Ingest into graphify

```bash
cd quran_corpus
/graphify .
```
"""
    (CORPUS / "README.md").write_text(body, encoding="utf-8")
    print(f"  README.md updated")


def main():
    print(f"Enriching corpus at {CORPUS}/")
    gen_timeline()
    gen_events()
    gen_asbab()
    gen_tafsir_traditions()
    gen_sciences()
    augment_surahs()
    update_corpus_readme()
    print("\nDone.")


if __name__ == "__main__":
    main()
