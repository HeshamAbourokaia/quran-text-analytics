# -*- coding: utf-8 -*-
"""The verses of hiba, the gift (root و ه ب), and a du'a in the name of al-Wahhab built from them:
the config of the second Name study.

Every word whose root is و ه ب in the Quranic Arabic Corpus: 25 words in 22 verses of 12 surahs
(19 Meccan, 3 Medinan). The Name al-Wahhab itself comes three times (3:8, 38:9, 38:35), and seven
verses ask with «grant me» (هَبْ لي). pipeline/names.py reads the corpus and checks everything here
against it; this module holds what a person decided after reading the verses, in both languages:
five themes in three groups, fourteen conditions, five notes on receiving a gift, what is given in
each verse, the seven «grant me» du'as read span by span, the du'a (long: five movements, 32 phrases;
short: 9) with a plain English meaning under each phrase, ten findings, and the page's own sentences.

A du'a source may sit up to four verses from a verse of giving (CTX_WINDOW), because the «grant me»
du'as and their answers run over several verses (19:2 to 19:9, 21:89 and 21:90, 26:83 to 26:85).
With only 22 verses a root is compared once it sits in two of them (MIN_IN).
"""
import sys
from . import names
from .names import norm, CHRONO   # noqa: F401

SLUG = 'wahhab'
ROOT = 'وهب'
NAME = ('الوهّاب', 'Al-Wahhab')
TITLE = ('آيات الهبة ودعاؤها', 'Hiba Verses and Du’a')
SECTIONS = ['models', 'sankey', 'findings', 'agents', 'assoc', 'objects', 'net', 'forms', 'formulas', 'themes', 'matrix',
            'conditions', 'adab', 'mushaf', 'grid', 'chrono']
TRANS = True
NOUN = ('hiba', 'الهبة', 'f')
# the hero: the «grant me» du'as and what follows each within two verses. A verse with one of these roots answers it
# (glad tidings, reward, made subject, answered); a verse opening with «rabb» or asking again goes on with the du'a.
HERO = {'type': 'duas', 'window': 2, 'answer_roots': ['بشر', 'جزي', 'سخر', 'جوب']}        # in English the verse cards show Pickthall's translation under the Arabic
CTX_WINDOW = 4
MIN_IN = 2
N_ASSOC = 13        # the roots with a z score of 2 or more
NET_DEFAULT = 2     # a root not named below is part of the gift and its circumstances

# ---------------------------------------------------------------- hand labels
# the five themes: Arabic, English, verses, and the short names the matrix uses
THEMES = [
    ('أدعية «هب لي» السبعة', 'The seven «grant me» du’as',
     ['3:8', '3:38', '19:5', '25:74', '26:83', '37:100', '38:35'], 'أدعية هب لي', 'The du’as'),
    ('الإجابة: «وهبنا له»', 'The answer: «We gave him»',
     ['6:84', '19:49', '19:50', '19:53', '21:72', '21:90', '29:27', '38:30', '38:43'], 'وهبنا له', 'The answers'),
    ('إقرار العبد بالهبة', 'The servant acknowledges the gift', ['14:39', '26:21'], 'إقرار العبد', 'Acknowledged'),
    ('الاسم وصفة الهبة الإلهية', 'The Name, and how God gives', ['38:9', '42:49'], 'الاسم والصفة', 'The Name'),
    ('هبة بين المخلوقين', 'Giving between creatures', ['19:19', '33:50'], 'بين المخلوقين', 'Between creatures'),
]
GROUPS = [('الله يَهَب', 'God gives'), ('العبد يطلب ويُقرّ', 'The servant asks and acknowledges'), ('بين المخلوقين', 'Between creatures')]
GROUP_OF_THEME = {'أدعية «هب لي» السبعة': 1, 'الإجابة: «وهبنا له»': 0, 'إقرار العبد بالهبة': 1, 'الاسم وصفة الهبة الإلهية': 0, 'هبة بين المخلوقين': 2}

# the root network: God's act, the servant's act, or the gift and its circumstances (the default)
NET_GROUPS = [('فعل الله', 'God’s act'), ('فعل العبد', 'The servant’s act'), ('الموهوب وحاله', 'The gift and its circumstances')]
NET_GROUP_OF = {}
for _r in ('رحم', 'بشر', 'جوب', 'خلق', 'نبأ', 'جزي', 'سمع', 'عزز', 'خزن', 'ملك', 'أنث', 'ذكر', 'نفل'): NET_GROUP_OF[_r] = 0
for _r in ('دعو', 'حمد', 'صبر', 'أوب', 'سرع', 'رغب', 'رهب', 'خشع', 'عزل', 'غفر', 'وقي', 'صلح', 'حسن', 'عبد', 'هدي', 'خوف', 'زيغ', 'لقي'): NET_GROUP_OF[_r] = 1

GLOSS = {'ذرر': ('الذرية', 'offspring'), 'لدن': ('من لدنك', 'from Your presence'), 'صلح': ('الصالحين', 'the righteous'),
         'زوج': ('الأزواج', 'spouses'), 'مرأ': ('امرأة', 'a wife, a woman'), 'رحم': ('الرحمة', 'mercy'), 'نبأ': ('نبيًّا', 'a prophet'),
         'دعو': ('الدعاء', 'prayer'), 'أجر': ('الأجر', 'reward, dues'), 'ملك': ('الملك', 'a kingdom'), 'خوف': ('الخوف', 'fear'),
         'سمع': ('سميع الدعاء', 'He hears prayer'), 'حكم': ('حكمًا', 'wisdom'), 'غفر': ('اغفر لي', 'forgive me'), 'عبد': ('العبد', 'the servant'),
         'ذكر': ('الذكور، ذكرى', 'males, a reminder'), 'هدي': ('هديتنا', 'You guided us'), 'رسل': ('رسول', 'a messenger')}
GENERIC = {'أله', 'شيأ', 'قوم', 'كون', 'قول', 'علم', 'ربب', 'أيي', 'نفس', 'كلل', 'يوم', 'أخر', 'دنو', 'جعل', 'غير', 'عقل', 'موت', 'بني',
           'بين', 'أمر', 'قبل', 'عند', 'كثر', 'حقق', 'جيأ', 'أتي', 'ردد', 'أحد', 'بعد', 'مثل', 'أمم', 'دون'}

# who gives: the verb's subject from the tags; two subjects only this root has, by their person tag
AGENTS = [
    ('we', 'الله متكلّمًا: وَهَبْنا', 'God speaking: We gave (وَهَبْنا)'),
    ('ask', 'دعاءٌ إلى الله: هَبْ لي', 'A prayer to God: grant me (هَبْ لي)'),
    ('he', 'الله بضمير الغائب: وَهَبَ، يَهَبُ', 'God, spoken of: He gave, He grants (وَهَبَ، يَهَبُ)'),
    ('jibril', 'رسولٌ بإذن الله: لِأَهَبَ لكِ', 'A messenger, by God’s leave: to give you (لِأَهَبَ)'),
    ('woman', 'بين الناس: امرأةٌ وهبت نفسها', 'Between people: a woman offers herself (وَهَبَتْ)'),
]
AGENT_TAGS = {'1S': 'jibril', '3FS': 'woman'}
NOUNS = [('wahhab', 'الوهّاب', 'al-Wahhab, the Giver', ('وَهّاب',))]

CONDITIONS = [
    ('«من لدنك»: الطلب من عند الله لا من الأسباب', '«From Your presence»: asking of God, not of the means', ['3:8', '3:38', '19:5'], 'هب لي من لدنك'),
    ('الهبة مقرونة بالرحمة', 'The gift joined to mercy', ['3:8', '19:50', '19:53', '38:43', '38:9'], 'ووهبنا لهم من رحمتنا'),
    ('انقطاع الأسباب: الكِبَر والعقم', 'When the means run out: old age and barrenness', ['14:39', '19:5', '3:38'], 'وهب لي على الكبر إسماعيل وإسحاق'),
    ('الغاية: الصلاح والإمامة للمتقين', 'The aim: righteousness, and leading the God-fearing', ['25:74', '26:83', '37:100'], 'وألحقني بالصالحين، واجعلنا للمتقين إمامًا'),
    ('النداء الخفي والافتقار', 'The quiet call, and need', ['19:5', '3:38', '21:90'], 'إذ نادى ربه نداءً خفيًّا … فهب لي'),
    ('الإنابة والصبر', 'Turning back to God, and patience', ['38:30', '38:43', '38:35'], 'نعم العبد إنه أوّاب، إنا وجدناه صابرًا'),
    ('الختم باسم الوهاب', 'Closing with the Name al-Wahhab', ['3:8', '38:35'], 'إنك أنت الوهاب'),
    ('الاستغفار قبل الطلب', 'Asking forgiveness before asking', ['38:35'], 'رب اغفر لي وهب لي'),
    ('الثبات على الهداية قبل الطلب', 'Asking to stay guided before asking', ['3:8'], 'لا تزغ قلوبنا بعد إذ هديتنا وهب لنا'),
    ('اعتزال الباطل', 'Leaving what is false', ['19:49'], 'فلما اعتزلهم وما يعبدون من دون الله وهبنا له'),
    ('الإحسان', 'Doing good', ['6:84'], 'وكذلك نجزي المحسنين'),
    ('المسارعة في الخيرات والدعاء رغبًا ورهبًا', 'Hastening to good, and praying in hope and in awe', ['21:90'], 'كانوا يسارعون في الخيرات ويدعوننا رغبًا ورهبًا وكانوا لنا خاشعين'),
    ('الخوف من العدو ثم الهبة', 'Fear of an enemy, then the gift', ['26:21'], 'ففررت منكم لما خفتكم فوهب لي ربي حكمًا'),
    ('الحمد بعد الهبة', 'Praise after the gift', ['14:39'], 'الحمد لله الذي وهب لي على الكبر'),
]

# how a gift is asked for and received: title, verses, and the words that say it
ADAB = [
    ('الهبة مشيئة لا استحقاق', 'The gift is His will, not a due', ['42:49'],
     'يهب لمن يشاء إناثًا ويهب لمن يشاء الذكور، ويجعل من يشاء عقيمًا (الشورى 42:49 و42:50)',
     '«He gives daughters to whom He wills, and sons to whom He wills», «and He makes barren whom He wills» (42:49, 42:50)'),
    ('العطاء الموهوب بغير حساب', 'What is given, without reckoning', ['38:35'],
     'هذا عطاؤنا فامنن أو أمسك بغير حساب (ص 38:39، بعد دعاء سليمان بأربع آيات)',
     '«This is Our gift: so bestow or withhold, without reckoning» (38:39, four verses after Sulayman’s prayer)'),
    ('الاستبعاد البشري لا يمنع الهبة', 'Human doubt does not hold back the gift', ['3:38', '19:5'],
     'أنّى يكون لي غلامٌ وقد بلغني الكبر … قال كذلك الله يفعل ما يشاء (آل عمران 3:40)',
     '«How can I have a son when old age has reached me?» «So God does what He wills» (3:40)'),
    ('الموهوب يُردّ إلى الله بالحمد', 'The gift is returned to God with praise', ['14:39', '26:21'],
     'الحمد لله الذي وهب لي، فوهب لي ربي حكمًا',
     '«Praise be to God, who gave me», «so my Lord gave me wisdom»'),
    ('لا تطلب الهبة وحدها: اقرنها بالغاية', 'Do not ask for the gift alone: tie it to its aim', ['25:74', '26:83'],
     'قرة أعين واجعلنا للمتقين إمامًا، حكمًا وألحقني بالصالحين',
     '«the comfort of our eyes, and make us leaders for the God-fearing»; «wisdom, and join me with the righteous»'),
]

# what is given in each verse; every one of the 22 is placed exactly once
OBJECTS = [
    ('الذرية والولد', 'Children and offspring', ['3:38', '19:5', '25:74', '37:100', '6:84', '14:39', '19:19', '19:49', '21:72', '21:90', '29:27', '38:30', '42:49']),
    ('الرحمة', 'Mercy', ['3:8', '19:50', '38:9']),
    ('الحكم والنبوة', 'Wisdom and prophethood', ['26:21', '26:83']),
    ('الأهل والعون', 'Family, and a helper', ['38:43', '19:53']),
    ('الملك', 'A kingdom', ['38:35']),
    ('بين الناس: امرأةٌ تهب نفسها', 'Between people: a woman offers herself', ['33:50']),
]

# the seven «grant me» du'as, read span by span (1-based word positions)
MODELS = [
    ('3:8', 'دعاء الراسخين في العلم', 'The prayer of those firm in knowledge',
     [(1, 1, 'النداء', 'the call'), (2, 7, 'طلب الثبات أولًا', 'to stay guided, first'), (8, 12, 'الهبة من لدنك', 'the gift, from Your presence'), (13, 15, 'الختم بالاسم', 'closing with the Name')]),
    ('3:38', 'دعاء زكريا', 'Zakariya’s prayer',
     [(6, 6, 'النداء', 'the call'), (7, 12, 'الهبة من لدنك', 'the gift, from Your presence'), (13, 15, 'الختم بالثناء', 'closing with praise')]),
    ('19:5', 'دعاء زكريا، النداء الخفي', 'Zakariya’s quiet call',
     [(1, 8, 'الإقرار بالحال', 'the situation, stated'), (9, 13, 'الهبة من لدنك', 'the gift, from Your presence')]),
    ('25:74', 'دعاء عباد الرحمن', 'The prayer of the servants of the Merciful',
     [(3, 3, 'النداء', 'the call'), (4, 10, 'الهبة', 'the gift'), (11, 13, 'الغاية', 'the aim')]),
    ('26:83', 'دعاء إبراهيم', 'Ibrahim’s prayer',
     [(1, 1, 'النداء', 'the call'), (2, 4, 'الهبة', 'the gift'), (5, 6, 'الغاية', 'the aim')]),
    ('37:100', 'دعاء إبراهيم للذرية', 'Ibrahim’s prayer for a child',
     [(1, 1, 'النداء', 'the call'), (2, 5, 'الهبة', 'the gift')]),
    ('38:35', 'دعاء سليمان', 'Sulayman’s prayer',
     [(2, 2, 'النداء', 'the call'), (3, 4, 'الاستغفار أولًا', 'forgiveness, first'), (5, 12, 'الهبة', 'the gift'), (13, 15, 'الختم بالاسم', 'closing with the Name')]),
]

# the du'a: t = the words as said, q = the Quranic phrase it is built on (defaults to t), src = its verses,
# en = a plain meaning in English (shown as a meaning, not as a translation of the Quran)
FULL = [
    ('النداء والتمهيد', 'The call, and what comes before asking', [
        dict(t='رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا', src=['3:8'], en='Our Lord, do not let our hearts swerve after You have guided us'),
        dict(t='رَبَّنَا اغْفِرْ لَنَا', src=['38:35'], en='Our Lord, forgive us'),
        dict(t='إِنَّا نَدْعُوكَ نِدَاءً خَفِيًّا', q='نداء خفيا', src=['19:3'], en='we call on You with a quiet call'),
        dict(t='وَلَمْ نَكُنْ بِدُعَائِكَ رَبَّنَا أَشْقِيَاءَ', src=['19:4'], en='and never, our Lord, have we been let down in calling on You'),
        dict(t='رَبَّنَا لَا تَذَرْنَا فُرَادَى وَأَنْتَ خَيْرُ الْوَارِثِينَ', q='وأنت خير الوارثين', src=['21:89'], en='Our Lord, do not leave us alone, and You are the best of heirs'),
    ]),
    ('الثناء بالاسم', 'Praise by the Name', [
        dict(t='إِنَّكَ أَنْتَ الْوَهَّابُ', src=['3:8', '38:35'], en='truly You are the Giver'),
        dict(t='عِنْدَكَ خَزَائِنُ رَحْمَتِكَ، وَأَنْتَ الْعَزِيزُ الْوَهَّابُ', q='العزيز الوهاب', src=['38:9'], en='with You are the treasures of Your mercy, and You are the Mighty, the Giver'),
        dict(t='لَكَ مُلْكُ السَّمَاوَاتِ وَالْأَرْضِ، تَخْلُقُ مَا تَشَاءُ، وَتَهَبُ لِمَنْ تَشَاءُ', q='ملك السماوات والأرض', src=['42:49'], en='Yours is the kingdom of the heavens and the earth; You create what You will, and give to whom You will'),
        dict(t='إِنَّكَ سَمِيعُ الدُّعَاءِ', src=['3:38'], en='truly You hear prayer'),
        dict(t='وَذَلِكَ عَلَيْكَ هَيِّنٌ', src=['19:9'], en='and that is easy for You'),
    ]),
    ('الطلب بصيغ القرآن', 'The asking, in the Quran’s own words', [
        dict(t='فَهَبْ لَنَا مِنْ لَدُنْكَ رَحْمَةً', q='هب لنا من لدنك رحمة', src=['3:8'], en='so grant us mercy from Your presence'),
        dict(t='وَهَبْ لَنَا مِنْ لَدُنْكَ ذُرِّيَّةً طَيِّبَةً', q='من لدنك ذرية طيبة', src=['3:38'], en='and grant us from Your presence good offspring'),
        dict(t='وَهَبْ لَنَا مِنْ لَدُنْكَ وَلِيًّا، وَاجْعَلْهُ رَبَّنَا رَضِيًّا', q='من لدنك وليا', src=['19:5', '19:6'], en='and grant us from Your presence an heir, and make him, our Lord, well pleasing'),
        dict(t='هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ', src=['25:74'], en='grant us in our spouses and our children the comfort of our eyes'),
        dict(t='وَهَبْ لَنَا مِنَ الصَّالِحِينَ', q='من الصالحين', src=['37:100'], en='and grant us children who are among the righteous'),
        dict(t='وَهَبْ لَنَا حُكْمًا وَأَلْحِقْنَا بِالصَّالِحِينَ', src=['26:83'], en='and grant us wisdom, and join us with the righteous'),
        dict(t='وَاجْعَلْ لَنَا لِسَانَ صِدْقٍ فِي الْآخِرِينَ', q='لسان صدق في الآخرين', src=['26:84'], en='and give us an honest name among those who come after'),
        dict(t='وَاجْعَلْنَا مِنْ وَرَثَةِ جَنَّةِ النَّعِيمِ', q='من ورثة جنة النعيم', src=['26:85'], en='and make us among the heirs of the Garden of Bliss'),
        dict(t='وَهَبْ لَنَا مِنْ رَحْمَتِكَ، وَاجْعَلْ لَنَا لِسَانَ صِدْقٍ عَلِيًّا', q='لسان صدق عليا', src=['19:50'], en='and grant us of Your mercy, and give us an honest and lofty name'),
        dict(t='وَأَصْلِحْ لَنَا أَزْوَاجَنَا', src=['21:90'], en='and set our spouses right for us'),
        dict(t='وَهَبْ لَنَا أَهْلَنَا وَمِثْلَهُمْ مَعَهُمْ رَحْمَةً مِنْكَ', q='ومثلهم معهم رحمة', src=['38:43'], en='and give us our families, and as many again with them, as a mercy from You'),
        dict(t='وَاجْعَلْ عَطَاءَكَ لَنَا بِغَيْرِ حِسَابٍ', q='بغير حساب', src=['38:39'], en='and make Your gift to us beyond reckoning'),
    ]),
    ('العهد: ما قرنته الآيات بالهبة', 'The pledge: what the verses pair with the gift', [
        dict(t='رَبَّنَا اجْعَلْنَا نُسَارِعُ فِي الْخَيْرَاتِ، وَنَدْعُوكَ رَغَبًا وَرَهَبًا، وَنَكُونُ لَكَ خَاشِعِينَ', q='رغبا ورهبا', src=['21:90'], en='Our Lord, make us hasten to good deeds, call on You in hope and in awe, and be humble before You'),
        dict(t='وَاجْعَلْنَا مِنَ الْمُحْسِنِينَ', q='المحسنين', src=['6:84'], en='and make us among those who do good'),
        dict(t='وَاجْعَلْنَا نَعْتَزِلُ مَا يُعْبَدُ مِنْ دُونِكَ', src=['19:49'], en='and make us turn away from what is worshipped besides You'),
        dict(t='وَاجْعَلْنَا عِبَادًا أَوَّابِينَ صَابِرِينَ', src=['38:30', '38:44'], en='and make us servants who turn back to You, and are patient'),
        dict(t='وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا', src=['25:74'], en='and make us leaders for the God-fearing'),
        dict(t='رَبَّنَا اجْعَلْنَا مُقِيمِي الصَّلَاةِ وَمِنْ ذُرِّيَّاتِنَا', src=['14:40'], en='Our Lord, make us keep up the prayer, and our children too'),
    ]),
    ('الحمد والختم', 'Praise, and the close', [
        dict(t='رَبَّنَا فَاسْتَجِبْ لَنَا', src=['21:90'], en='Our Lord, answer us'),
        dict(t='وَالْحَمْدُ لَكَ عَلَى مَا وَهَبْتَ لَنَا عَلَى الْكِبَرِ، إِنَّكَ لَسَمِيعُ الدُّعَاءِ', q='لسميع الدعاء', src=['14:39'], en='and praise be to You for what You have given us in old age; truly You hear prayer'),
        dict(t='رَبَّنَا وَتَقَبَّلْ دُعَاءَ', src=['14:40'], en='Our Lord, and accept the prayer'),
        dict(t='إِنَّكَ أَنْتَ الْوَهَّابُ', src=['3:8', '38:35'], en='truly You are the Giver'),
    ]),
]
SHORT = [
    dict(t='رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا، وَهَبْ لَنَا مِنْ لَدُنْكَ رَحْمَةً، إِنَّكَ أَنْتَ الْوَهَّابُ', src=['3:8'],
         en='Our Lord, do not let our hearts swerve after You have guided us, and grant us mercy from Your presence; truly You are the Giver'),
    dict(t='رَبَّنَا اغْفِرْ لَنَا', src=['38:35'], en='Our Lord, forgive us'),
    dict(t='وَهَبْ لَنَا مِنْ لَدُنْكَ ذُرِّيَّةً طَيِّبَةً', q='من لدنك ذرية طيبة', src=['3:38'], en='and grant us from Your presence good offspring'),
    dict(t='هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا', src=['25:74'],
         en='grant us in our spouses and our children the comfort of our eyes, and make us leaders for the God-fearing'),
    dict(t='وَهَبْ لَنَا حُكْمًا وَأَلْحِقْنَا بِالصَّالِحِينَ', src=['26:83'], en='and grant us wisdom, and join us with the righteous'),
    dict(t='وَهَبْ لَنَا مِنَ الصَّالِحِينَ', q='من الصالحين', src=['37:100'], en='and grant us children who are among the righteous'),
    dict(t='وَهَبْ لَنَا مِنْ رَحْمَتِكَ', src=['19:50'], en='and grant us of Your mercy'),
    dict(t='إِنَّكَ سَمِيعُ الدُّعَاءِ', src=['3:38'], en='truly You hear prayer'),
    dict(t='إِنَّكَ أَنْتَ الْوَهَّابُ', src=['38:35'], en='truly You are the Giver'),
]

# the written forms, grouped by lemma: (Arabic, English, colour group)
LEMMA_GROUPS = {'وَهَبَ': ('الفعل وَهَبَ', 'The verb wahaba, to give', 0), 'وَهّاب': ('الاسم الوهّاب', 'The Name al-Wahhab', 2)}

# the formulas table: phrases repeated word for word; a phrase made only of these words is left out
FORMULA_STOP = {'من', 'ما', 'في', 'ان', 'الله', 'الذين', 'و', 'لهم', 'لكم', 'به', 'على', 'الا', 'لا', 'الذي', 'هو', 'ذلك', 'قل', 'قال',
                'له', 'لي', 'لنا', 'انك', 'انت', 'رب', 'ربنا', 'ربي', 'كل', 'كلا', 'وكلا', 'دون'}
N_FORMULAS = 12

# ten findings: title, body, the verses they rest on (a verse beside a verse of giving may be cited)
FINDINGS = [
    ('كل ما طُلب بـ«هب لي» لا يُكتسب بعمل', 'Everything asked for with «grant me» is beyond effort',
     'في الأدعية السبعة المطلوب هو: رحمة، وذرية طيبة، ووليّ، وقرة أعين من الأزواج والذريات، وحكم، وصالحون، وملك. لا مال ولا طعام ولا نصر. وهنا الفرق في النص بين «ارزق» و«هب»: الرزق يُسعى إليه، والهبة تُعطى.',
     'In the seven du’as what is asked for is mercy, good offspring, an heir, the comfort of spouses and children, wisdom, righteous children and a kingdom. Never wealth, food or victory. That is the difference in the text between «provide» and «grant»: provision is sought, a gift is given.',
     ['3:8', '3:38', '19:5', '25:74', '26:83', '37:100', '38:35']),
    ('«من لدنك» ثلاث مرات، والإجابة «من رحمتنا»', '«From Your presence» three times, and the answer «of Our mercy»',
     'ثلاثة من الأدعية السبعة تقول «هب لي من لدنك»، أي من عندك أنت لا من الأسباب. وفي الإجابة يأتي «ووهبنا لهم من رحمتنا» مرتين (مريم 19:50 و19:53)، و«رحمةً منّا» مرة (ص 38:43). الهبة في القرآن عطاءٌ من عند الله لا ثمرة سبب.',
     'Three of the seven du’as say «grant me from Your presence»: from You, not from the means. In the answers, «We gave them of Our mercy» comes twice (19:50, 19:53) and «as a mercy from Us» once (38:43). In the Quran a gift comes from God, not as the fruit of a cause.',
     ['3:8', '3:38', '19:5', '19:50', '19:53', '38:43']),
    ('خمسة من السبعة تُجاب في الآية التالية أو التي بعدها', 'Five of the seven are answered in the next verse or the one after',
     'زكريا (آل عمران 3:38) تناديه الملائكة في 3:39، وزكريا (مريم 19:5) يُبشَّر في 19:7، وعباد الرحمن (الفرقان 25:74) يُجزون الغرفة في 25:75، وإبراهيم (الصافات 37:100) يُبشَّر في 37:101، وسليمان (ص 38:35) تُسخَّر له الريح في 38:36. النص نفسه يعرض الإجابة بجوار الطلب.',
     'Zakariya (3:38) is called by the angels in 3:39; Zakariya again (19:5) is given the good news in 19:7; the servants of the Merciful (25:74) are rewarded with the high chamber in 25:75; Ibrahim (37:100) is given the good news in 37:101; Sulayman (38:35) has the wind made subject to him in 38:36. The text sets the answer right beside the asking.',
     ['3:38', '19:5', '25:74', '37:100', '38:35']),
    ('الاسم يختم الدعاء', 'The Name closes the du’a',
     'ورد «الوهاب» ثلاث مرات فقط، اثنتان منها خاتمة دعاء: «إنك أنت الوهاب» (آل عمران 3:8، ص 38:35). والثالثة سؤالٌ يردّ خزائن الرحمة إلى الله: «أم عندهم خزائن رحمة ربك العزيز الوهاب» (ص 38:9). فالطلب بالهبة يُختم بالاسم ذاته.',
     'The Name al-Wahhab comes only three times, and twice it closes a du’a: «truly You are the Giver» (3:8, 38:35). The third time is a question that returns the treasures of mercy to God: «or do they hold the treasures of your Lord’s mercy, the Mighty, the Giver?» (38:9). Asking for a gift is closed with the Name itself.',
     ['3:8', '38:35', '38:9']),
    ('الهبة في القرآن ولدٌ قبل كل شيء', 'In the Quran a gift is first of all a child',
     'ثلاث عشرة آيةً من الـ22 عن الذرية والولد: إسحاق ويعقوب، وإسماعيل، ويحيى، وسليمان، وغلامٌ زكي. ثم الرحمة والحكم والأهل والملك. ولذلك جاء قلب الدعاء في الذرية والأزواج.',
     'Thirteen of the 22 verses are about children and offspring: Ishaq and Yaqub, Ismail, Yahya, Sulayman, a pure boy. Then mercy, wisdom, family and a kingdom. That is why the heart of the du’a is about children and spouses.',
     ['3:38', '19:5', '25:74', '37:100', '6:84', '14:39', '19:19', '19:49', '21:72', '21:90', '29:27', '38:30', '42:49']),
    ('الهبة تأتي عند انقطاع الأسباب', 'The gift comes when the means have run out',
     'إبراهيم «على الكبر» (إبراهيم 14:39)، وزكريا «وكانت امرأتي عاقرًا» (مريم 19:5)، وموسى «ففررت منكم لما خفتكم» (الشعراء 26:21)، وأيوب بعد البلاء (ص 38:43). الاسم يُدعى به حين لا يبقى سبب.',
     'Ibrahim «in old age» (14:39), Zakariya «and my wife is barren» (19:5), Musa «so I fled from you when I feared you» (26:21), Ayyub after his trial (38:43). The Name is called on when no means are left.',
     ['14:39', '19:5', '26:21', '38:43']),
    ('ما يسبق «هب لي» في النص', 'What comes before «grant me» in the text',
     'استغفار (ص 38:35)، وثباتٌ على الهداية (آل عمران 3:8)، ونداءٌ خفي (مريم 19:3)، واعتزال الباطل (مريم 19:49)، وإنابة (ص 38:34 ثم 38:35)، وإحسان (الأنعام 6:84). وهذه حركتا التمهيد والعهد في الدعاء.',
     'Asking forgiveness (38:35), asking to stay guided (3:8), a quiet call (19:3), leaving what is false (19:49), turning back to God (38:34, then 38:35), doing good (6:84). These are the du’a’s opening and its pledge.',
     ['38:35', '3:8', '19:3', '19:49', '38:34', '6:84']),
    ('دعاءٌ واحد لعامة المؤمنين', 'One du’a is given to every believer',
     'خمسةٌ من الأدعية السبعة على ألسنة الأنبياء، وواحدٌ على لسان الراسخين في العلم (آل عمران 3:8)، وواحدٌ لـ«عباد الرحمن» عامة: «ربنا هب لنا من أزواجنا وذرياتنا قرة أعين» (الفرقان 25:74). هو الدعاء الذي جعله القرآن للناس كلهم، ولذلك هو عمود الصيغة المختصرة.',
     'Five of the seven du’as are on prophets’ lips, one on the lips of those firm in knowledge (3:8), and one belongs to «the servants of the Merciful» at large: «our Lord, grant us in our spouses and our children the comfort of our eyes» (25:74). It is the du’a the Quran gives to everyone, so it is the spine of the short form.',
     ['25:74', '3:8']),
    ('الهبة مشيئة لا استحقاق', 'The gift is His will, not a due',
     '«يهب لمن يشاء إناثًا ويهب لمن يشاء الذكور» (الشورى 42:49)، ثم في الآية التالية «ويجعل من يشاء عقيمًا». الآيتان معًا تضعان الهبة في المشيئة لا في الاستحقاق، وهذا أقرب ما في النص إلى معنى أن الوهاب يعطي ما لا يُستحق.',
     '«He gives daughters to whom He wills, and sons to whom He wills» (42:49), and in the next verse «He makes barren whom He wills». Together the two verses place the gift in His will, not in what anyone is owed: the nearest the text comes to saying that the Giver gives what is not earned.',
     ['42:49', '42:50']),
    ('الرزاق والوهاب في النص', 'Ar-Razzaq and al-Wahhab in the text',
     'الرزق في 109 آيات أكثرها عن الطعام والمال والإنفاق، والهبة في 22 آية أكثرها عن الولد والحكم والرحمة. ويجمعهما لفظٌ واحد: «بغير حساب»، يأتي مع الرزق خمس مرات، ومع عطاء سليمان بعد دعائه بالوهاب: «هذا عطاؤنا فامنن أو أمسك بغير حساب» (ص 38:39).',
     'Provision fills 109 verses, mostly about food, wealth and spending; the gift fills 22, mostly about children, wisdom and mercy. One phrase joins them: «without reckoning», five times with provision, and once with what Sulayman was given after he called on the Giver: «this is Our gift, so bestow or withhold, without reckoning» (38:39).',
     ['38:35', '38:39']),
]

# ---------------------------------------------------------------- the page's own sentences, [English, Arabic]
COPY = {
    'heroLine': ('The Quran has {n_duas} du’as that ask «grant me». {n_answered} are answered within the next two verses; {n_open} go on as du’a and are left open.',
                 'في القرآن {n_duas} أدعيةٍ تقول «هب لي». {n_answered} منها تُجاب في الآيتين التاليتين، و{n_open} تمضي دعاءً وتبقى مفتوحة.'),
    'heroBig': ('of the {n_duas} «grant me» du’as are answered within two verses', 'من أدعية «هب لي» الـ{n_duas} تُجاب في الآيتين التاليتين'),
    'heroAria': ('The {n_duas} «grant me» du’as, each joined to its answer or left open', 'أدعية «هب لي» الـ{n_duas}، كلٌّ موصولٌ بإجابته أو مفتوح'),
    'heroForms': ('Every form: وهب, يهب, هب لي, الوهّاب.', 'بكل صيغها: وهب، يهب، هب لي، الوهّاب.'),
    'lead': ('Two forms: a full du’a in five movements that follow the seven «grant me» du’as of the Quran, and a short one to learn by heart. Every phrase is taken from one of the 22 verses, or from a verse near one (up to four verses away, because the «grant me» du’as and their answers run over several verses). Under each word, a solid line means it stands in the verse as written, a dotted line that it was adapted. In English a plain meaning sits under each phrase.',
             'صيغتان: كاملةٌ في خمس حركاتٍ تتبع أدعية «هب لي» السبعة في القرآن، ومختصرةٌ للحفظ. كل مقطعٍ مأخوذٌ من إحدى الآيات الـ22 أو من آيةٍ قريبةٍ منها (حتى أربع آيات، لأن أدعية «هب لي» وإجاباتها تمتدّ على آياتٍ متتابعة). وتحت كل كلمةٍ خطٌّ: متصلٌ إن كانت في الآية كما هي، ومنقّطٌ إن كانت محوّلة.'),
    'ctxTag': ('a verse near a verse of giving', 'آيةٌ قريبة من آية هبة'),
    'sumWords': ('of its words stand in their verses as written; {pctQuran}% occur somewhere in the Quran, {pctTarget}% in the verses of giving',
                 'من كلماته كما هي في آياتها؛ و{pctQuran}٪ وردت في القرآن في موضعٍ ما، و{pctTarget}٪ في آيات الهبة'),
    'ctxNote': ('Every source is one of the 22 verses of giving, or a verse no more than four away from one: {ctx}. Nothing from outside them.',
                'كل مصادر الدعاء من آيات الهبة الـ22، أو من آيةٍ لا تبعد عن إحداها أكثر من أربع آيات: {ctx}. ولا شيء من خارجها.'),
    'modelsLead': ('The Quran has seven du’as that ask with «grant me» or «grant us» (هَبْ لي، هَبْ لنا): five on prophets’ lips, one on the lips of those firm in knowledge, and one given to the servants of the Merciful. Read span by span they share one shape, and the du’a above follows it: a call to «my Lord» or «our Lord»; something said before the asking (to stay guided, forgiveness, the situation stated); then «grant me», three times with «from Your presence»; then an aim, or the Name to close: «truly You are the Giver», «truly You hear prayer». What is asked for with «grant» is always something no effort earns: offspring, an heir, mercy, wisdom, a kingdom.',
                   'في القرآن سبعة أدعيةٍ بصيغة «هَبْ لي» أو «هَبْ لنا»: خمسةٌ على ألسنة الأنبياء، وواحدٌ على لسان الراسخين في العلم، وواحدٌ لعباد الرحمن. قُرئ بناؤها كلمةً كلمة فخرج نمطٌ واحد، وعليه بُني الدعاء أعلاه: النداء بـ«ربّ» أو «ربّنا»؛ ثم تمهيدٌ قبل الطلب (ثباتٌ على الهداية، أو استغفار، أو إقرارٌ بالحال)؛ ثم «هَبْ لي»، وثلاث مراتٍ معها «من لدنك»؛ ثم غايةٌ أو ختمٌ بالاسم: «إنك أنت الوهاب»، «إنك سميع الدعاء». وما يُطلب بـ«هب» دائمًا شيءٌ لا يُكتسب بعمل: ذرية، ووليّ، ورحمة، وحكم، وملك.'),
    'modelsNote': [
        ('The verses of giving also show how the one who receives answers: Ibrahim praises, «praise be to God, who gave me in old age Ismail and Ishaq» (14:39), and Musa returns wisdom to its Giver, «so my Lord gave me wisdom» (26:21). The du’a’s opening and its praise come from there.',
         'وفي آيات الهبة أدب الموهوب له: إبراهيم يحمد «الحمد لله الذي وهب لي على الكبر إسماعيل وإسحاق» (إبراهيم 14:39)، وموسى يردّ الحكم إلى ربه «فوهب لي ربي حكمًا» (الشعراء 26:21). ومن هنا جاءت حركتا التمهيد والحمد في الدعاء.'),
    ],
    'agentsH': ('Who gives?', 'من يَهَب؟'),
    'agentsSub': ('The verb وهب comes {verbs} times. Its subject, from the morphology:', 'يرد الفعل «وهب» {verbs} مرة. وفاعله بحسب الصرف:'),
    'nounsLine': ('And as a noun only the Name itself: al-Wahhab, {n_wahhab} times (3:8, 38:9, 38:35).',
                  'وبالاسم لا يرد إلا الاسم نفسه: «الوهّاب» {n_wahhab} مرات (آل عمران 3:8، ص 38:9، ص 38:35).'),
    'agentsAha': ('In {allah} of the {verbs} verbs the giver is God, by name or by pronoun, and {a_ask} more are «grant me» addressed to Him: a third of all the verbs are a plea, against 3 of 61 for provision. Only two gifts in the Quran come from anyone else: the angel who gives Maryam a son, by God’s leave (19:19), and a woman who offers herself in marriage (33:50).',
                  'في {allah} من الأفعال الـ{verbs} الواهب هو الله، باسمه أو بضميره، و{a_ask} أخرى «هب لي» موجّهةٌ إليه: ثلث الأفعال كلها دعاء، مقابل 3 من 61 في الرزق. ولا تأتي في القرآن هبةٌ من غير الله إلا مرتين: الملَك الذي يهب لمريم غلامًا بإذن الله (مريم 19:19)، وامرأةٌ تهب نفسها للنبي (الأحزاب 33:50).'),
    'assocH': ('What sits with the gift in the same verse?', 'ما الذي يلازم الهبة في الآية نفسها؟'),
    'assocSub': ('For each root: the bar is its share of the 22 verses of giving, the white mark its share of the whole Quran. Ranked by the strength of the evidence; with 22 verses the shares move quickly, but the order is clear. Tap a root to see its verses below.',
                 'لكل جذر: الشريط نسبة آيات الهبة الـ22 التي يرد فيها، والعلامة البيضاء نسبته في القرآن كله. مرتّبةٌ بقوة الدليل؛ والعيّنة 22 آية فالنِّسب تتحرك بسرعة، لكن الترتيب واضح. انقر جذرًا لترى آياته في الأسفل.'),
    'assocAha': ('What clings to the gift in the Quran is offspring, the phrase «from Your presence», the righteous and spouses, then mercy. The gift is asked for from God, mostly for one’s children, and its aim is righteousness. These are the spine of the du’a.',
                 'ما يلتصق بالهبة في القرآن هو الذرية، وعبارة «من لدنك»، والصالحون، والأزواج، ثم الرحمة. فالهبة تُطلب من عند الله، للذرية غالبًا، وغايتها الصلاح. وهذه عمود الدعاء.'),
    'netSub': ('The same thirteen roots, drawn as a ring around the gift. A line between two roots means they share at least two of the 22 verses, and the thicker it is the more verses they share. Point at a root to see its companions; tap it to list its verses below.',
               'الجذور الثلاثة عشر نفسها، حلقةً حول الهبة. الخطّ بين جذرَين يعني أنهما يجتمعان في آيتَين أو أكثر من الآيات الـ22، وكلما غلُظ كثُرت الآيات المشتركة. أشر إلى جذرٍ لترى ما يجاوره، وانقره لتظهر آياته في الأسفل.'),
    'netAria': ('The thirteen roots that sit with the gift, joined where they share verses', 'الجذور الثلاثة عشر التي تجاور الهبة، موصولةٌ حيث تشترك في آيات'),
    'netIn': (' sits in {n} of the 22 verses.', ' في {n} من آيات الهبة الـ22.'),
    'condH': ('What the verses pair with the gift', 'ما الذي قرنته الآيات بالهبة؟'),
    'condSub': ('The conditions as the verses themselves name them, ordered by how many verses say each one together with the gift. Under each is the verse’s own wording. Tap one to see its verses below.',
                'الشروط كما تذكرها الآيات نفسها، مرتّبةً بعدد الآيات التي تذكر كل شرطٍ مع الهبة. وتحت كل شرطٍ الشاهد من الآية. انقر شرطًا لترى آياته في الأسفل.'),
    'versesSub': ('The word of giving is lit in every verse, with Pickthall’s English beneath it. Above the list are a strip of the whole mushaf, a grid of the 114 surahs and a row of dots in the order of revelation; tap a surah in any of them to keep only its verses. Then sift by theme (the line under a theme is its Meccan share in gold and its Medinan share in green), by Mecca or Medina, or search any word. Tap a reference to read the verse in the mushaf.',
                  'كلمة الهبة مضاءةٌ في كل آية. وفوق القائمة شريطُ المصحف كله، وشبكةُ السور الـ114، وصفُّ نقاطٍ على ترتيب النزول؛ انقر سورةً في أيٍّ منها لتبقى آياتها وحدها. ثم رشّح بالموضوع (الخطّ تحت الموضوع نصيبه المكي بالذهبي والمدني بالأخضر)، أو بالمكي والمدني، أو ابحث بأي كلمة. وانقر رقم الآية لتقرأها في المصحف.'),
    'gridSub': ('Each cell is a surah, in mushaf order; the brighter it is, the more verses of giving it holds. Tap a lit surah to keep only its verses.',
                'كل خليةٍ سورة بترتيب المصحف؛ وكلما أضاءت كثُرت آيات الهبة فيها. انقر سورةً مضاءة لتبقى آياتها وحدها.'),
    'gridAria': ('The 114 surahs, each shaded by how many verses of giving it holds', 'السور الـ114، كلٌّ ملوّنة بعدد آيات الهبة فيها'),
    'gridTop': ('{top} hold most of the 22 verses; {none} of the 114 surahs have none.', '{top} فيها أكثر الآيات الـ22؛ و{none} سورةً من 114 ليس فيها آية هبة.'),
    'gridHas': ('{cnt} of its {m} verses speak of giving. Tap to keep only them.', '{cnt} من آياتها الـ{m} تذكر الهبة. انقر لإبقائها وحدها.'),
    'gridNone': ('none of its {m} verses speaks of giving.', 'لا تذكر الهبة آيةٌ من آياتها الـ{m}.'),
    'chronoSub': ('The 22 verses in the order of revelation, one dot each, stacked by surah. The colour is the verse’s theme group. Dots fade when a filter leaves them out, so a chosen theme shows where it sits in time.',
                  'الآيات الـ22 على ترتيب النزول، نقطةٌ لكل آية متراكمةً بالسورة. واللون مجموعةُ موضوع الآية. وتخفت النقاط التي يُخرجها الترشيح، فيظهر موضع كل موضوعٍ في الزمن.'),
    'chronoAha': ('The first verse of giving to come down, in this order, is {first}, and it is the Name itself: «the Mighty, the Giver». Surah Sad, which also holds Sulayman’s prayer, comes before all the others. All but three of the verses are Meccan; the last is {last}, a ruling about a woman who offers herself in marriage to the Prophet.',
                  'أول ما نزل في الهبة، على هذا الترتيب، {first}، وهي الاسم نفسه: «العزيز الوهاب». فسورة ص، وفيها دعاء سليمان، تسبق السور الأخرى كلها. والآيات كلها مكية إلا ثلاثًا، وآخرها {last}، حكمٌ في امرأةٍ تهب نفسها للنبي.'),
    'sankeyH': ('Where each part of the du’a comes from', 'من أين جاء كل جزء من الدعاء؟'),
    'sankeySub': ('The du’a’s five movements on one side, the surahs whose words they use on the other. The width of a band is how many references run between them. Point at a band to see its phrases; tap a surah to keep only its verses below.',
                  'حركات الدعاء الخمس في جانب، والسور التي أُخذت منها ألفاظها في الجانب الآخر. وعرض الشريط عدد الإحالات بينهما. أشر إلى شريطٍ لترى مقاطعه، وانقر سورةً لتبقى آياتها وحدها في الأسفل.'),
    'sankeyAria': ('The five movements of the du’a, joined to the surahs their words come from', 'حركات الدعاء الخمس، موصولةً بالسور التي جاءت منها ألفاظها'),
    'sankeyAha': ('{n_dua_surahs} surahs feed the du’a. Sad gives the most (8 references), then Maryam (7) and Al Imran (6): the three together give more than half.',
                  '{n_dua_surahs} سور تُغذّي الدعاء. أكثرها ص (8 إحالات)، ثم مريم (7) وآل عمران (6)، والثلاث معًا أكثر من نصف الإحالات.'),
    'findingsH': ('What the verses show', 'أهم النتائج'),
    'findingsSub': ('Ten findings from reading the 22 verses and their numbers. Tap a card to see its verses below.',
                    'عشر ملاحظاتٍ خرجت من قراءة الآيات الـ22 وأرقامها. انقر أي بطاقةٍ لترى آياتها في الأسفل.'),
    'objectsH': ('What is given?', 'ماذا يُوهَب في القرآن؟'),
    'objectsSub': ('Each of the 22 verses placed by what is given in it. Tap a bar to see its verses below.', 'كل آيةٍ من الآيات الـ22 مصنّفةٌ بما وُهب فيها. انقر شريطًا لترى آياته في الأسفل.'),
    'objectsAha': ('Thirteen of the 22 are about children and offspring, and not one is about wealth or food. The gifts the Quran names with this word are things no effort earns: a child, mercy, wisdom, a kingdom.',
                   'ثلاث عشرة آيةً من الـ22 عن الذرية والولد، ولا آية واحدة عن مالٍ أو طعام. فما يسمّيه القرآن هبةً بهذا اللفظ لا يُكتسب بسعي: ولد، ورحمة، وحكم، وملك.'),
    'formsH': ('The word’s {n_forms} forms, in {tokens} places', 'أشكال الكلمة الـ{n_forms} في {tokens} موضعًا'),
    'formsSub': ('Each box is one written form of the root, sized by how often it comes: the verb {fg_0} times, the Name al-Wahhab {fg_2} times. Tap a form to see its verses below.',
                 'كل خانةٍ شكلٌ مكتوب من أشكال الجذر، ومساحتها عدد مرات وروده: الفعل {fg_0} مرة، والاسم «الوهّاب» {fg_2} مرات. انقر شكلًا لترى آياته في الأسفل.'),
    'formsAria': ('The written forms of the root, sized by how often each comes', 'الأشكال المكتوبة للجذر، كلٌّ بمساحة عدد وروده'),
    'formulasH': ('Phrases the Quran repeats in the verses of giving', 'الصيغ التي يكرّرها القرآن في آيات الهبة'),
    'formulasSub': ('Phrases found word for word in two or more of the 22 verses: the Quran’s own patterns for giving, and where the du’a’s words come from. Tap a row to see its verses below.',
                    'عباراتٌ تتكرر بلفظها في آيتين أو أكثر من الآيات الـ22: قوالب الهبة القرآنية، ومنها أُخذت ألفاظ الدعاء. انقر صفًّا لترى آياته في الأسفل.'),
    'themesH': ('How the verses spread over the themes', 'كيف تتوزّع الآيات على الموضوعات؟'),
    'themesSub': ('Each verse was labelled by hand after reading it; gold for Meccan verses, green for Medinan. Tap a theme to keep only its verses.',
                  'تصنيفٌ يدويٌّ لكل آيةٍ بعد قراءتها؛ الذهبي للمكي والأخضر للمدني. انقر موضوعًا لتبقى آياته وحدها.'),
    'themesAha': ('The seven du’as and the nine answers make three quarters of the verses: the text sets the asking and the answer side by side.',
                  'الأدعية السبعة والإجابات التسع ثلاثة أرباع الآيات: النص يعرض الطلب والإجابة معًا.'),
    'matrixH': ('What the verses pair with the gift, theme by theme', 'ما قرنته الآيات بالهبة، موضوعًا موضوعًا'),
    'matrixSub': ('Rows are what the verses pair with the gift; columns are the themes. A number is how many verses say both. Tap a number to see those verses below.',
                  'الصفوف ما قرنته الآيات بالهبة، والأعمدة موضوعات الآيات. والرقم عدد الآيات التي تجمع الاثنين. انقر رقمًا لترى تلك الآيات في الأسفل.'),
    'matrixAha': ('Most of what the verses pair with the gift sits in the column of the seven du’as: in the Quran the condition is named inside the du’a itself.',
                  'معظم ما قرنته الآيات بالهبة يقع في عمود الأدعية السبعة: الشرط في القرآن يُذكر داخل الدعاء نفسه.'),
    'adabH': ('What the text teaches about a gift', 'وما الذي يعلّمه النص عن أدب الهبة؟'),
    'adabSub': ('The verses do not only describe how a gift is asked for, but how it is received. Tap a card to see its verses below.',
                'الآيات لا تصف طريق الهبة فقط، بل تصف كيف تُطلب وكيف تُستقبل. انقر بطاقةً لترى آياتها في الأسفل.'),
    'mushafH': ('The whole mushaf', 'المصحف كله'),
    'mushafSub': ('Each tick is a verse of giving in its place among the 6,236, from al-Fatiha to an-Nas; the bands behind them are the surahs. The colour is the verse’s theme group. Tap a band to keep only that surah’s verses.',
                  'كل خطٍّ آيةُ هبةٍ في موضعها بين الآيات الـ6236، من الفاتحة إلى الناس؛ والأشرطة خلفها السور. واللون مجموعة موضوع الآية. انقر شريطًا لتبقى آيات سورته وحدها.'),
    'mushafAria': ('The 22 verses of giving in their places in the mushaf', 'آيات الهبة الـ22 في مواضعها من المصحف'),
}

def build():
    return names.build(sys.modules[__name__])

if __name__ == '__main__':
    import json
    R = build()
    print(json.dumps(R['totals'], ensure_ascii=False))
    print('agents', [(a['id'], a['n']) for a in R['agents']], 'nouns', [(a['id'], a['n']) for a in R['nouns']])
    print('assoc', [(r['root'], r['n'], r['z'], r['g']) for r in R['assoc']])
    print('dua', R['dua']['sum'])
    print('forms', [(f['u'], f['n'], f['g']) for f in R['forms']])
    print('formulas', [(f['u'], f['n']) for f in R['formulas']])
    print('bytes', len(json.dumps(R, ensure_ascii=False, separators=(',', ':')).encode()))
