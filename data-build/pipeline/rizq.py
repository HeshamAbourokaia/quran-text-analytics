# -*- coding: utf-8 -*-
"""The verses of rizq (root ر ز ق) and a du'a built from them: the config of the first Name study.

Every word whose root is ر ز ق in the Quranic Arabic Corpus: 123 words in 109 verses of 44 surahs
(72 Meccan, 37 Medinan). pipeline/names.py reads the corpus and checks everything here against it;
this module holds what a person decided after reading the verses: the nine themes and their three
groups, the group of each root in the network, the conditions the verses pair with provision, the
three prophetic du'as read span by span, the du'a (long: six movements, 36 phrases; short: 15), and
the page's own sentences in both languages (COPY; a {placeholder} is filled by the build when it is a
count, and by the page otherwise).
"""
import sys
from . import names
from .names import norm, CHRONO   # noqa: F401  (the tests and other modules read them here)

SLUG = 'rizq'
ROOT = 'رزق'
NAME = ('الرزّاق', 'Ar-Razzaq')
TITLE = ('آيات الرزق ودعاؤها', 'Rizq Verses and Du’a')
SECTIONS = ['models', 'agents', 'assoc', 'net', 'conditions', 'grid', 'chrono']
NOUN = ('rizq', 'الرزق', 'm')     # the study's subject in a sentence, for the comparison of Names
# the hero: the verbs of rizq by who gives; these classes name God as the giver outright
HERO = {'type': 'agents', 'named': ['he', 'we', 'you']}
CTX_WINDOW = 1      # a du'a source may be the verse right beside a rizq verse
MIN_IN = 3          # a root must sit in three of the verses to be compared
NET_DEFAULT = None  # every shown root has its network group below

# ---------------------------------------------------------------- hand labels
# the nine themes, in the order the page shows them; every one of the 109 verses is in exactly one
THEMES = [
    ('الإنفاق مما رزق الله', 'Spending from what God provided',
     ['2:3', '2:254', '4:39', '8:3', '13:22', '14:31', '16:75', '22:35', '28:54', '32:16', '35:29', '36:47', '42:38', '63:10', '65:7', '34:39']),
    ('الله وحده الرازق', 'God alone provides',
     ['10:31', '15:20', '16:73', '23:72', '27:64', '29:17', '29:60', '30:40', '34:24', '35:3', '51:57', '51:58', '67:21', '11:6', '6:151', '17:31', '56:82']),
    ('بسط الرزق وتقديره', 'Provision widened and measured',
     ['13:26', '17:30', '28:82', '29:62', '30:37', '34:36', '39:52', '42:12', '42:19', '42:27', '16:71', '89:16', '2:212', '3:27', '24:38', '20:131']),
    ('كلوا من الطيبات واشكروا', 'Eat of the good things and give thanks',
     ['2:57', '2:60', '2:172', '5:88', '6:142', '7:160', '16:114', '20:81', '34:15', '67:15', '22:28', '22:34', '8:26', '16:72', '17:70', '40:64', '45:16', '10:93']),
    ('الرزق من السماء والأرض', 'Provision from the sky and the earth',
     ['2:22', '14:32', '40:13', '45:5', '50:11', '51:22']),
    ('تحريم الحلال والافتراء', 'Forbidding what God allowed',
     ['6:140', '7:32', '10:59', '16:56']),
    ('رزق الآخرة', 'Provision in the hereafter',
     ['2:25', '3:169', '8:4', '8:74', '19:62', '22:50', '22:58', '24:26', '33:31', '34:4', '37:41', '38:54', '40:40', '65:11', '7:50']),
    ('نماذج جلب الرزق في الدنيا', 'Seeking provision: the stories',
     ['2:126', '3:37', '5:114', '11:88', '14:37', '12:37', '18:19', '20:132', '28:57', '16:112', '65:3', '62:11', '16:67']),
    ('أحكام الرزق بين الناس', 'Provision between people: the rulings',
     ['2:233', '4:5', '4:8', '30:28']),
]

# the three macro groups the charts colour by, and the group of each of the nine themes (by its Arabic name)
GROUPS = [('الله هو الرازق', 'God provides'), ('ما يُطلب من العبد', 'What is asked of the servant'), ('رزق الآخرة', 'Provision in the hereafter')]
GROUP_OF_THEME = {'الله وحده الرازق': 0, 'بسط الرزق وتقديره': 0, 'الرزق من السماء والأرض': 0,
                  'الإنفاق مما رزق الله': 1, 'كلوا من الطيبات واشكروا': 1, 'أحكام الرزق بين الناس': 1,
                  'تحريم الحلال والافتراء': 1, 'نماذج جلب الرزق في الدنيا': 1, 'رزق الآخرة': 2}

# the root network: each associated root is God's act, the servant's act, or the provision itself
NET_GROUPS = [('فعل الله', 'God’s act'), ('فعل العبد', 'The servant’s act'), ('الرزق نفسه: صفته ومصدره', 'The provision itself: its quality and source')]
NET_GROUP_OF = {}
for _r in ('بسط', 'قدر', 'نزل', 'حسب', 'نعم', 'منن', 'خلف', 'فضل', 'أتي', 'خلق', 'ملك', 'حيي', 'موت', 'خرج', 'جزي', 'جعل'): NET_GROUP_OF[_r] = 0
for _r in ('نفق', 'أكل', 'شكر', 'صلو', 'عبد', 'صبر', 'وقي', 'وكل', 'علن', 'سرر', 'هجر', 'ذكر', 'كفر', 'قتل', 'فري', 'شرك', 'عمل', 'صلح', 'أمن', 'تجر'): NET_GROUP_OF[_r] = 1
for _r in ('طيب', 'كرم', 'حسن', 'حلل', 'حرم', 'ثمر', 'سمو', 'أرض', 'بلد', 'دبب', 'طعم', 'ضرب', 'موه', 'ولد', 'بحر', 'غفر', 'جنن', 'نهر', 'كسو', 'ذرر'): NET_GROUP_OF[_r] = 2

# what the verses pair with provision: name, the verses, and the words of the verse that say it
CONDITIONS = [
    ('التقوى', 'Taqwa, being mindful of God', ['65:3', '20:132', '5:88', '2:212'], 'ومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب'),
    ('التوكل', 'Reliance on God', ['65:3', '11:88'], 'ومن يتوكل على الله فهو حسبه'),
    ('إقامة الصلاة', 'Keeping up the prayer', ['2:3', '8:3', '13:22', '14:31', '22:35', '35:29', '42:38', '14:37', '20:132', '62:11'], 'وأمر أهلك بالصلاة واصطبر عليها لا نسألك رزقا نحن نرزقك'),
    ('الإنفاق مما رُزقوا', 'Spending from what they were given', ['2:3', '2:254', '4:39', '8:3', '13:22', '14:31', '16:75', '22:35', '28:54', '32:16', '35:29', '36:47', '42:38', '63:10', '65:7', '34:39'], 'وما أنفقتم من شيء فهو يخلفه وهو خير الرازقين'),
    ('الشكر', 'Gratitude', ['2:172', '8:26', '14:37', '16:114', '29:17', '34:15'], 'فابتغوا عند الله الرزق واعبدوه واشكروا له'),
    ('الإيمان والعمل الصالح', 'Faith and good works', ['2:25', '22:50', '34:4', '40:40', '65:11', '2:126', '8:4', '8:74', '33:31'], 'ومن يؤمن بالله ويعمل صالحا قد أحسن الله له رزقا'),
    ('الهجرة والجهاد في سبيل الله', 'Migration and striving in the way of God', ['22:58', '8:74', '3:169'], 'والذين هاجروا في سبيل الله ليرزقنهم الله رزقا حسنا'),
    ('السعي والابتغاء', 'Going out and seeking', ['67:15', '29:17', '18:19', '62:11'], 'فامشوا في مناكبها وكلوا من رزقه'),
    ('الأمن والاستقرار', 'Safety and a settled home', ['2:126', '16:112', '28:57'], 'رب اجعل هذا بلدا آمنا وارزق أهله من الثمرات'),
    ('الأكل من الحلال الطيب وترك التحريم', 'Eating what is lawful and good, forbidding none of it', ['2:172', '5:88', '16:114', '6:140', '7:32', '10:59', '2:57', '7:160', '20:81'], 'فكلوا مما رزقكم الله حلالا طيبا واشكروا نعمة الله'),
    ('الدعاء المباشر بصيغة ارزُق', 'Asking outright: provide for us', ['2:126', '5:114', '14:37'], 'وارزقنا وأنت خير الرازقين'),
    ('القناعة وعدم التطلع لما عند الناس', 'Contentment, not eyeing what others have', ['20:131', '51:57', '62:11', '23:72'], 'ولا تمدن عينيك إلى ما متعنا به أزواجا منهم ورزق ربك خير وأبقى'),
    ('الصبر', 'Patience', ['13:22', '22:35', '28:54', '20:132'], 'والذين صبروا ابتغاء وجه ربهم وأنفقوا مما رزقناهم'),
    ('ذكر الله', 'Remembering God', ['22:28', '22:34', '35:3', '32:16', '62:11'], 'ويذكروا اسم الله على ما رزقهم'),
    ('عدم الخوف من الفقر على الأولاد', 'No fear of poverty for the children', ['6:151', '17:31'], 'ولا تقتلوا أولادكم خشية إملاق نحن نرزقهم وإياكم'),
]

# the three du'as that ask for provision with the imperative ارزُق, read span by span (1-based word positions)
MODELS = [
    ('2:126', 'دعاء إبراهيم لمكة', 'Ibrahim’s prayer for Mecca',
     [(4, 4, 'النداء', 'the call'), (5, 8, 'طلب الأمن أولاً', 'safety asked for first'), (9, 12, 'طلب الرزق', 'then provision'), (13, 18, 'قيد الإيمان', 'tied to faith')]),
    ('14:37', 'دعاء إبراهيم لذرّيته', 'Ibrahim’s prayer for his family',
     [(1, 1, 'النداء', 'the call'), (2, 12, 'الإقرار بالحال', 'the situation, stated'), (13, 15, 'الغاية الدينية قبل الطلب', 'the religious aim before the request'), (16, 24, 'الطلب', 'the request'), (25, 26, 'الغاية: الشكر', 'the end: gratitude')]),
    ('5:114', 'دعاء عيسى للمائدة', 'Isa’s prayer for the table',
     [(5, 6, 'النداء', 'the call'), (7, 18, 'الطلب الأعلى: آية من الله', 'the higher request: a sign from God'), (19, 19, 'طلب الرزق', 'provision'), (20, 22, 'الثناء ختاماً', 'praise, to close')]),
]

# the du'a: t = the words as said, q = the Quranic core that must be found (defaults to t), src = its verses
FULL = [
    ('النداء', 'The call', [
        dict(t='اللَّهُمَّ رَبَّنَا', src=['5:114']),
    ]),
    ('الثناء بأسماء الرزق', 'Praise by the names of provision', [
        dict(t='أَنْتَ خَيْرُ الرَّازِقِينَ', src=['5:114', '22:58', '23:72', '34:39', '62:11']),
        dict(t='وَأَنْتَ الرَّزَّاقُ ذُو الْقُوَّةِ الْمَتِينُ', q='الرزاق ذو القوة المتين', src=['51:58']),
        dict(t='لَكَ مَقَالِيدُ السَّمَاوَاتِ وَالْأَرْضِ', q='مقاليد السماوات والأرض', src=['42:12']),
        dict(t='تَبْسُطُ الرِّزْقَ لِمَنْ تَشَاءُ وَتَقْدِرُ', src=['42:12', '13:26', '17:30', '29:62', '30:37', '34:36', '39:52']),
        dict(t='وَتَرْزُقُ مَنْ تَشَاءُ بِغَيْرِ حِسَابٍ', src=['3:27']),
        dict(t='لَطِيفٌ بِعِبَادِكَ، تَرْزُقُ مَنْ تَشَاءُ، وَأَنْتَ الْقَوِيُّ الْعَزِيزُ', src=['42:19']),
    ]),
    ('الإقرار: التوحيد والافتقار', 'Acknowledging: You alone, and our need', [
        dict(t='مَا مِنْ دَابَّةٍ فِي الْأَرْضِ إِلَّا عَلَيْكَ رِزْقُهَا', src=['11:6']),
        dict(t='وَكَأَيِّنْ مِنْ دَابَّةٍ لَا تَحْمِلُ رِزْقَهَا، أَنْتَ تَرْزُقُهَا وَإِيَّانَا', src=['29:60']),
        dict(t='وَفِي السَّمَاءِ رِزْقُنَا وَمَا نُوعَدُ', src=['51:22']),
        dict(t='لَا يَمْلِكُ لَنَا رِزْقًا أَحَدٌ مِنْ دُونِكَ، فَعِنْدَكَ نَبْتَغِي الرِّزْقَ، وَإِيَّاكَ نَعْبُدُ، وَلَكَ نَشْكُرُ، وَإِلَيْكَ نُرْجَعُ', src=['29:17']),
        dict(t='رَبَّنَا إِنْ قُدِرَ عَلَيْنَا رِزْقُنَا فَاجْعَلْ لَنَا بَعْدَ عُسْرٍ يُسْرًا', q='بعد عسر يسرا', src=['65:7']),
        dict(t='وَمَا تَوْفِيقُنَا إِلَّا بِكَ، عَلَيْكَ تَوَكَّلْنَا وَإِلَيْكَ نُنِيبُ', src=['11:88']),
    ]),
    ('الطلب بصيغ القرآن', 'The asking, in the Quran’s own words', [
        dict(t='رَبَّنَا اجْعَلْ بَلَدَنَا آمِنًا، وَارْزُقْ أَهْلَهُ مِنَ الثَّمَرَاتِ', q='وارزق أهله من الثمرات', src=['2:126']),
        dict(t='وَاجْعَلْ أَفْئِدَةً مِنَ النَّاسِ تَهْوِي إِلَيْنَا', q='اجعل أفئدة من الناس تهوي', src=['14:37']),
        dict(t='وَارْزُقْنَا وَأَنْتَ خَيْرُ الرَّازِقِينَ', src=['5:114']),
        dict(t='ارْزُقْنَا مِنْ لَدُنْكَ رِزْقًا حَسَنًا', q='رزقا حسنا', src=['22:58', '28:57', '16:75', '11:88']),
        dict(t='وَأَحْسِنْ لَنَا رِزْقًا', src=['65:11']),
        dict(t='وَارْزُقْنَا مِنَ السَّمَاوَاتِ وَالْأَرْضِ', q='من السماوات والأرض', src=['34:24', '16:73', '10:31']),
        dict(t='حَلَالًا طَيِّبًا', src=['5:88', '16:114']),
        dict(t='مِنْ حَيْثُ لَا نَحْتَسِبُ', src=['65:3']),
        dict(t='رَغَدًا مِنْ كُلِّ مَكَانٍ، وَنَحْنُ آمِنُونَ مُطْمَئِنُّونَ', q='رغدا من كل مكان', src=['16:112']),
        dict(t='وَاجْزِنَا أَحْسَنَ مَا عَمِلْنَا، وَزِدْنَا مِنْ فَضْلِكَ', src=['24:38']),
        dict(t='وَمَا أَنْفَقْنَا مِنْ شَيْءٍ فَأَخْلِفْهُ عَلَيْنَا', src=['34:39']),
        dict(t='وَارْزُقْنَا تِجَارَةً لَنْ تَبُورَ', q='تجارة لن تبور', src=['35:29']),
        dict(t='وَاجْعَلْ لَنَا مَغْفِرَةً وَرِزْقًا كَرِيمًا', src=['8:4', '22:50', '33:31', '34:4']),
    ]),
    ('العهد: ما قرنته الآيات بالرزق', 'The pledge: what the verses pair with provision', [
        dict(t='رَبَّنَا اجْعَلْنَا مِنَ الَّذِينَ يَتَّقُونَكَ، فَتَجْعَلْ لَنَا مَخْرَجًا', src=['65:2']),
        dict(t='وَمِمَّنْ يَتَوَكَّلُ عَلَيْكَ فَأَنْتَ حَسْبُهُ', src=['65:3']),
        dict(t='وَمِنَ الَّذِينَ يُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْتَهُمْ يُنْفِقُونَ، سِرًّا وَعَلَانِيَةً', q='سرا وعلانية', src=['2:3', '13:22', '14:31', '35:29']),
        dict(t='وَأَعِنَّا أَنْ نَأْمُرَ أَهْلَنَا بِالصَّلَاةِ وَنَصْطَبِرَ عَلَيْهَا، فَأَنْتَ تَرْزُقُنَا وَالْعَاقِبَةُ لِلتَّقْوَى', q='والعاقبة للتقوى', src=['20:132']),
        dict(t='وَاجْعَلْنَا نَأْكُلُ مِنْ طَيِّبَاتِ مَا رَزَقْتَنَا، وَنَشْكُرُ لَكَ، إِنَّا إِيَّاكَ نَعْبُدُ', src=['2:172', '16:114']),
        dict(t='وَاصْرِفْ أَعْيُنَنَا عَمَّا مَتَّعْتَ بِهِ غَيْرَنَا، فَرِزْقُكَ خَيْرٌ وَأَبْقَى', q='خير وأبقى', src=['20:131']),
        dict(t='وَمَا عِنْدَكَ خَيْرٌ لَنَا مِنَ اللَّهْوِ وَمِنَ التِّجَارَةِ', q='خير من اللهو ومن التجارة', src=['62:11']),
    ]),
    ('الغاية والختم', 'The purpose, and the close', [
        dict(t='رَبَّنَا وَاجْعَلْنَا لِنِعْمَتِكَ شَاكِرِينَ، لَا بِهَا كَافِرِينَ', src=['16:114', '16:72']),
        dict(t='رَبَّنَا تَقَبَّلْ مِنَّا إِنَّكَ أَنْتَ السَّمِيعُ الْعَلِيمُ', src=['2:127']),
        dict(t='إِنَّكَ تَرْزُقُ مَنْ تَشَاءُ بِغَيْرِ حِسَابٍ، وَأَنْتَ خَيْرُ الرَّازِقِينَ', q='ترزق من تشاء بغير حساب', src=['3:27', '5:114']),
    ]),
]

SHORT = [
    dict(t='اللَّهُمَّ رَبَّنَا، أَنْتَ خَيْرُ الرَّازِقِينَ', q='أنت خير الرازقين', src=['5:114']),
    dict(t='تَرْزُقُ مَنْ تَشَاءُ بِغَيْرِ حِسَابٍ', src=['3:27']),
    dict(t='وَمَا مِنْ دَابَّةٍ فِي الْأَرْضِ إِلَّا عَلَيْكَ رِزْقُهَا', src=['11:6']),
    dict(t='رَبَّنَا اجْعَلْ بَلَدَنَا آمِنًا', q='بلدا آمنا', src=['2:126']),
    dict(t='وَاجْعَلْ أَفْئِدَةً مِنَ النَّاسِ تَهْوِي إِلَيْنَا', q='اجعل أفئدة من الناس تهوي', src=['14:37']),
    dict(t='وَارْزُقْنَا وَأَنْتَ خَيْرُ الرَّازِقِينَ', src=['5:114']),
    dict(t='رِزْقًا حَسَنًا', src=['22:58']),
    dict(t='حَلَالًا طَيِّبًا', src=['5:88', '16:114']),
    dict(t='مِنَ السَّمَاوَاتِ وَالْأَرْضِ', src=['34:24']),
    dict(t='مِنْ حَيْثُ لَا نَحْتَسِبُ', src=['65:3']),
    dict(t='رَغَدًا مِنْ كُلِّ مَكَانٍ', src=['16:112']),
    dict(t='وَاجْعَلْنَا نُقِيمُ الصَّلَاةَ وَمِمَّا رَزَقْتَنَا نُنْفِقُ', src=['2:3', '8:3']),
    dict(t='وَمَا أَنْفَقْنَا مِنْ شَيْءٍ فَأَخْلِفْهُ عَلَيْنَا', src=['34:39']),
    dict(t='وَاجْعَلْنَا لَكَ شَاكِرِينَ', src=['2:172', '29:17']),
    dict(t='رَبَّنَا تَقَبَّلْ مِنَّا إِنَّكَ أَنْتَ السَّمِيعُ الْعَلِيمُ', src=['2:127']),
]

# who provides: the verb's subject from the morphology tags (nouns are counted apart)
AGENTS = [
    ('he', 'الله بضمير الغائب: يَرزُق', 'God, spoken of: He provides (يَرزُق)'),
    ('we', 'الله متكلّماً: نحن نَرزُق', 'God speaking: We provide (نَرزُق)'),
    ('passive', 'مبني للمجهول: يُرزَقون', 'Passive: they are provided for (يُرزَقون)'),
    ('ask', 'دعاء إلى الله: ارزُقْنا', 'A prayer to God: provide for us (ارزُقْنا)'),
    ('people', 'أمر للناس: ارزُقوهم', 'A command to people: provide for them (ارزُقوهم)'),
    ('you', 'خطاب لله: تَرزُق من تشاء', 'Addressed to God: You provide (تَرزُق)'),
]
# the nouns, by lemma
NOUNS = [('rizq', 'رِزْق', 'rizq, provision', ('رِزْق',)), ('raziq', 'رازِق', 'raziq, provider', ('رازِق',)), ('razzaq', 'الرَّزَّاق', 'ar-Razzaq, the Provider', ('رَزّاق',))]

# the roots that sit with rizq: shown with the word they usually come as; roots too common to say anything are left out
GLOSS = {'طيب': ('الطيّبات', 'the good things'), 'نفق': ('الإنفاق', 'spending'), 'بسط': ('يبسط الرزق', 'He widens'), 'ثمر': ('الثمرات', 'fruits'),
         'قدر': ('ويَقدِر', 'He measures'), 'أكل': ('كُلوا', 'eat'), 'كرم': ('رزق كريم', 'generous'), 'صلو': ('الصلاة', 'the prayer'),
         'حرم': ('التحريم', 'forbidding'), 'طعم': ('الطعام', 'food'), 'عبد': ('العبادة', 'worship'), 'حسن': ('رزقاً حسناً', 'good, fine'),
         'علن': ('سراً وعلانية', 'openly'), 'شكر': ('الشكر', 'thanks'), 'بلد': ('بلداً آمناً', 'a land'), 'حيي': ('يُحيي', 'life'),
         'ضرب': ('ضرب مثلاً', 'a parable'), 'حسب': ('بغير حساب', 'reckoning'), 'نعم': ('النعمة', 'blessing'), 'جعل': ('جعل لكم', 'made for you'),
         'منن': ('المَنّ', 'manna'), 'حلل': ('حلالاً', 'lawful'), 'سمو': ('السماء', 'the sky'), 'أرض': ('الأرض', 'the earth'), 'كفر': ('الكفر', 'denial'),
         'أمن': ('الأمن', 'safety, faith'), 'غفر': ('مغفرة', 'forgiveness'), 'عمل': ('عملوا', 'did'), 'صلح': ('الصالحات', 'good works'),
         'ولد': ('الأولاد', 'children'), 'سرر': ('سراً', 'in secret'), 'صبر': ('الصبر', 'patience'), 'تجر': ('التجارة', 'trade'), 'خلف': ('يُخلِفه', 'He replaces'),
         'فضل': ('الفضل', 'grace'), 'وكل': ('التوكل', 'reliance'), 'وقي': ('التقوى', 'taqwa'), 'هجر': ('الهجرة', 'migration'), 'خرج': ('مخرج', 'a way out'),
         'نزل': ('أنزل', 'sent down'), 'موه': ('ماء', 'water'), 'دبب': ('دابّة', 'creature'), 'كسو': ('الكسوة', 'clothing'), 'ذرر': ('الذرّية', 'offspring'),
         'كون': ('كان', 'to be'), 'شيأ': ('شيء', 'thing'), 'ذكر': ('الذكر', 'remembrance'), 'أتي': ('يأتي', 'comes')}
GENERIC = {'أله', 'شيأ', 'قوم', 'كون', 'قول', 'علم', 'ربب', 'أيي', 'نفس', 'كلل', 'يوم', 'أخر', 'دنو'}
N_ASSOC = 16

# ---------------------------------------------------------------- the page's own sentences, [English, Arabic]
COPY = {
    'heroLine': ('Of the {verbs} verbs of rizq, {allah} name God as the giver, as He or as We, and {a_you} more addresses Him as You: {named} in all. {a_passive} are passive, with Him understood; {a_ask} are du’as to Him; and only {a_people} tell people to provide.',
                 'من أفعال الرزق الـ{verbs}، في {allah} الله هو الرازق بضمير الغائب أو المتكلم، وفي {a_you} آخر يُخاطَب هو: «ترزق»، فالمجموع {named}. و{a_passive} مبنيةٌ للمجهول والمراد هو، و{a_ask} أدعيةٌ إليه، ولا يُؤمر الناس أن يرزقوا إلا في {a_people}.'),
    'heroBig': ('of the {verbs} verbs of rizq name God as the giver', 'من أفعال الرزق الـ{verbs} تجعل الله هو الرازق صراحةً'),
    'heroAria': ('The {verbs} verbs of rizq, by who gives', 'أفعال الرزق الـ{verbs}، بحسب من يرزق'),
    'heroForms': ('Every form: رزق, يرزق, الرازقين, الرزّاق.',
        'بكل صيغها: رزق، يرزق، الرازقين، الرزّاق.'),
    'lead': ('Two forms: a full du’a in six movements that follow the order of the prophets’ du’as in the rizq verses, and a short one to learn by heart. Every phrase is taken from one of the 109 verses, or from the verse right beside one. Under each word, a solid line means it stands in the verse as written, a dotted line that it was adapted.',
        'صيغتان: كاملةٌ في ست حركاتٍ تتبع ترتيب أدعية الأنبياء في آيات الرزق، ومختصرةٌ للحفظ. كل مقطعٍ مأخوذٌ من إحدى الآيات الـ١٠٩ أو من آيةٍ مجاورةٍ لها مباشرة. وتحت كل كلمةٍ خطٌّ: متصلٌ إن كانت في الآية كما هي، ومنقّطٌ إن كانت محوّلة.'),
    'ctxTag': ('the verse beside a rizq verse',
        'الآية المجاورة لآية رزق'),
    'sumWords': ('of its words stand in their verses as written; {pctQuran}% occur somewhere in the Quran, {pctTarget}% in the rizq verses',
        'من كلماته كما هي في آياتها؛ و{pctQuran}٪ وردت في القرآن في موضعٍ ما، و{pctTarget}٪ في آيات الرزق'),
    'ctxNote': ('Every source is one of the 109 rizq verses, except the verse right beside one: {ctx}. Nothing from outside them.',
        'كل مصادر الدعاء من آيات الرزق الـ١٠٩، عدا آيةٍ مجاورةٍ لها مباشرة: {ctx}. ولا شيء من خارجها.'),
    'modelsLead': ('Only three du’as in the Quran ask for provision with the imperative «provide» (ارزُق), all on prophets’ lips. Read span by span they share one shape, and the du’a above follows it: a call; a request higher than provision first (safety, prayer, a sign from God); then provision for one’s people rather than oneself; then thanks or praise to close. Provision is never asked for alone.',
        'في القرآن ثلاثة أدعيةٍ فقط يُطلب فيها الرزق بصيغة الأمر «ارزُقْ»، كلها على ألسنة الأنبياء. قُرئ بناؤها كلمةً كلمة فخرج نمطٌ واحد، وعليه بُني الدعاء أعلاه: النداء؛ ثم طلبٌ أعلى من الرزق يسبقه (الأمن، أو الصلاة، أو آيةٌ من الله)؛ ثم طلب الرزق للأهل والجماعة لا للنفس وحدها؛ ثم شكرٌ أو ثناءٌ يُختم به. الرزق في هذه الأدعية لا يُطلب وحده أبدًا.'),
    'modelsNote': [
        ('The rizq verses also show how the one provided for answers: Maryam returns her provision to its source, «it is from God» (3:37), and Shu’ayb ties a good provision to reliance, «on Him I rely and to Him I turn» (11:88). The du’a’s «acknowledging» and «pledge» movements come from there.',
         'وفي آيات الرزق أيضًا أدب المرزوق: مريم تردّ الرزق إلى مصدره «هو من عند الله» (آل عمران ٣:٣٧)، وشعيب يقرن الرزق الحسن بالتوكل «عليه توكلت وإليه أنيب» (هود ١١:٨٨). ومن هنا جاءت حركتا الإقرار والعهد في الدعاء.'),
    ],
    'agentsH': ('Who provides?',
        'من يرزق؟'),
    'agentsSub': ('The verb رزق comes {verbs} times. Its subject, from the morphology:',
        'يرد الفعل «رزق» {verbs} مرة. وفاعله بحسب الصرف:'),
    'nounsLine': ('And as a noun: rizq {n_rizq} times, raziq (provider) {n_raziq}, ar-Razzaq once (51:58).',
        'وبالاسم: «رزق» {n_rizq} مرة، و«رازق» {n_raziq}، و«الرزّاق» مرةً واحدة (الذاريات ٥١:٥٨).'),
    'agentsAha': ('In 50 of the 61 the provider is God, by name or by pronoun. The 5 passive verbs leave Him understood, the 3 pleas are addressed to Him, and the only 2 that command people are about providing for orphans and the weak from His wealth (4:5, 4:8). No verb has anyone providing for themselves: provision is always given, which is why the du’a opens with praise of the Provider rather than a list of needs.',
        'في ٥٠ من الأفعال الـ٦١ الفاعل هو الله، باسمه أو بضميره. والأفعال الخمسة المبنية للمجهول فاعلها محذوفٌ والمراد هو، والثلاثة الدعائية موجّهةٌ إليه، والموضعان الوحيدان اللذان يُؤمر فيهما البشر أن يرزقوا هما إرزاق اليتامى والسفهاء والمساكين من مال الله (النساء ٤:٥ و٤:٨). ولا فعلٌ فيها فاعله مخلوقٌ يرزق نفسه: الرزق دائمًا يُعطى، ولذلك افتُتح الدعاء بالثناء على الرازق لا بتعداد الحاجات.'),
    'assocH': ('What sits with provision in the same verse?',
        'ما الذي يلازم الرزق في الآية نفسها؟'),
    'assocSub': ('For each root: the bar is its share of the 109 rizq verses, the white mark its share of the whole Quran. Ranked by the strength of the evidence. Tap a root to see its verses below.',
        'لكل جذر: الشريط نسبة آيات الرزق الـ١٠٩ التي يرد فيها، والعلامة البيضاء نسبته في القرآن كله. مرتّبةٌ بقوة الدليل. انقر جذرًا لترى آياته في الأسفل.'),
    'assocAha': ('What clings to provision most in the Quran is not asking but four acts of the servant: eating of the good things and not forbidding them, spending from what was given, keeping the prayer, and giving thanks; and one act of God: He widens and He measures. These five are the spine of the du’a’s «pledge».',
        'أكثر ما يلتصق بالرزق في القرآن ليس الدعاء، بل أربعة أفعالٍ من العبد: يأكل من الطيّبات ولا يحرّمها، ويُنفق مما رُزق، ويُقيم الصلاة، ويشكر. وفعلٌ واحد من الله: يبسط ويَقدِر بحكمته. وهذه الخمسة عمود حركة «العهد» في الدعاء.'),
    'netSub': ('The same sixteen roots, drawn as a ring around provision. A line between two roots means they share at least two of the 109 verses, and the thicker it is the more verses they share. Point at a root to see its companions; tap it to list its verses below.',
        'الجذور الستة عشر نفسها، حلقةً حول الرزق. الخطّ بين جذرَين يعني أنهما يجتمعان في آيتَين أو أكثر من الآيات الـ١٠٩، وكلما غلُظ كثُرت الآيات المشتركة. أشر إلى جذرٍ لترى ما يجاوره، وانقره لتظهر آياته في الأسفل.'),
    'netAria': ('The sixteen roots that sit with provision, joined where they share verses',
        'الجذور الستة عشر التي تجاور الرزق، موصولةٌ حيث تشترك في آيات'),
    'netIn': (' sits in {n} of the 109 verses.',
        ' في {n} آية من آيات الرزق الـ109.'),
    'condH': ('What the verses pair with provision',
        'ما الذي قرنته الآيات بالرزق؟'),
    'condSub': ('The conditions as the verses themselves name them, ordered by how many verses say each one together with provision. Under each is the verse’s own wording. Tap one to see its verses below.',
        'الشروط كما تذكرها الآيات نفسها، مرتّبةً بعدد الآيات التي تذكر كل شرطٍ مع الرزق. وتحت كل شرطٍ الشاهد من الآية. انقر شرطًا لترى آياته في الأسفل.'),
    'versesSub': ('The word of provision is lit in every verse. Above the list, a grid of the 114 surahs says where the verses sit in the mushaf and a row of dots says when each came down; tap a surah in either to keep only its verses. Then sift by theme (the line under a theme is its Meccan share in gold and its Medinan share in green), by Mecca or Medina, or search any word. Tap a reference to read the verse in the mushaf.',
        'كلمة الرزق مضاءةٌ في كل آية. وفوق القائمة شبكةُ السور الـ١١٤ تقول أين تقع الآيات في المصحف، وصفُّ نقاطٍ يقول متى نزلت كل آية؛ انقر سورةً في أيٍّ منهما لتبقى آياتها وحدها. ثم رشّح بالموضوع (الخطّ تحت الموضوع نصيبه المكي بالذهبي والمدني بالأخضر)، أو بالمكي والمدني، أو ابحث بأي كلمة. وانقر رقم الآية لتقرأها في المصحف.'),
    'gridSub': ('Each cell is a surah, in mushaf order; the brighter it is, the more verses of provision it holds. Tap a lit surah to keep only its verses.',
        'كل خليةٍ سورة بترتيب المصحف؛ وكلما أضاءت كثُرت آيات الرزق فيها. انقر سورةً مضاءة لتبقى آياتها وحدها.'),
    'gridAria': ('The 114 surahs, each shaded by how many verses of provision it holds',
        'السور الـ١١٤، كلٌّ ملوّنة بعدد آيات الرزق فيها'),
    'gridTop': ('{top} hold most of the 109 verses; {none} of the 114 surahs have none.',
        '{top} فيها أكثر الآيات الـ109؛ و{none} سورةً من 114 ليس فيها آية رزق.'),
    'gridHas': ('{cnt} of its {m} verses name provision. Tap to keep only them.',
        '{cnt} من آياتها الـ{m} تذكر الرزق. انقر لإبقائها وحدها.'),
    'gridNone': ('none of its {m} verses names provision.',
        'لا تذكر الرزق آيةٌ من آياتها الـ{m}.'),
    'chronoSub': ('The 109 verses in the order of revelation, one dot each, stacked by surah. The colour is the verse’s theme group. Dots fade when a filter leaves them out, so a chosen theme shows where it sits in time.',
        'الآيات الـ١٠٩ على ترتيب النزول، نقطةٌ لكل آية متراكمةً بالسورة. واللون مجموعةُ موضوع الآية. وتخفت النقاط التي يُخرجها الترشيح، فيظهر موضع كل موضوعٍ في الزمن.'),
    'chronoAha': ('The first verse of provision to come down, in this order, is {first}: «He measured his provision, so he says: my Lord has humiliated me», a correction of how a narrowed provision is read, before any promise of widening. The last is {last}, Isa’s prayer: «provide for us, You are the best of providers».',
        'أول ما نزل في الرزق، على هذا الترتيب، {first}: «فقدر عليه رزقه فيقول ربي أهانن»، تصحيحٌ لفهم التضييق قبل أي وعدٍ بالتوسعة. وآخرها {last}، دعاء عيسى: «وارزقنا وأنت خير الرازقين».'),
}

def build():
    return names.build(sys.modules[__name__])

if __name__ == '__main__':
    import json
    R = build()
    print(json.dumps(R['totals'], ensure_ascii=False))
    print('dua', R['dua']['sum'])
    print('bytes', len(json.dumps(R, ensure_ascii=False, separators=(',', ':')).encode()))
