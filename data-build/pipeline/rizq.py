# -*- coding: utf-8 -*-
"""The verses of rizq (root ر ز ق) and a du'a built from them, phrase by phrase.

Every word whose root is ر ز ق in the Quranic Arabic Corpus: 123 words in 109 verses of 44 surahs
(72 Meccan, 37 Medinan). From the morphology the module reads who provides (the verb's subject),
which roots sit in the same verse far more often than in the rest of the Quran (log-odds with a
smoothing prior, as in Monroe, Colaresi and Quinn's "Fightin' Words"), and the Meccan or Medinan
period of each verse. The nine themes, the conditions the verses pair with provision and the three
prophetic du'as read span by span are hand labels, kept here so the page and the tests share them.

The du'a has two forms, long (six movements, 36 phrases) and short (15 phrases). Each phrase names
the verses it is taken from, and the Quranic phrase it is built on (q, or the whole phrase when it has
no q). The module checks every phrase against its verses: the mode is «text» when that Quranic phrase
is found word for word in a source verse and «shift» when it is not (the verse says of God "He
provides", the du'a says to Him "You provide", or the words were recast); «whole» says whether the
phrase exactly as shown stands in a source verse; and kw flags each shown word as standing in a source
verse as written (1) or adapted (0), which is what the page underlines solid or dotted. The lit words
of each source verse are computed here too, so the page only marks them.

The page's charts read three more things kept here: the standard Egyptian order of revelation (CHRONO,
position to surah), the macro group of each theme (God provides, what is asked of the servant, the
hereafter) that colours the verses, and the group of each associated root (God's act, the servant's act,
the provision itself) that colours the root network. The network's links are the verses two roots share,
which the page counts from each root's verse list.

The page reads the verse texts from corpus.js; this key holds positions, labels and the du'a.
"""
import collections, math, re
from .corpus import _read_rows, load_verses, load_words
from .datasets import _surah_meta

ROOT = 'رزق'

# ---------------------------------------------------------------- normalisation (Uthmani -> plain letters)
_MARKS = re.compile('[ؐ-ًؚ-ٟۖ-ۭـ࣓-ࣿ]')

def norm(s):
    """Plain letters from Uthmani text: wasla and dagger alif resolved, hamza seats, ة as ه, ى as ي."""
    s = s.replace('ٱ', 'ا')                              # alif wasla
    s = s.replace('وٰ', 'ا').replace('ىٰ', 'ي')     # Uthmani long vowels (ٱلصَّلَوٰةَ, عَلَىٰ)
    s = s.replace('ٰ', 'ا')                              # dagger alif elsewhere
    s = re.sub('ـ[ً-ْ]*ٔ[ً-ْ]*', 'ئ', s)   # hamza on a tatweel seat
    s = _MARKS.sub('', s)
    s = re.sub('[أإآ]', 'ا', s)
    s = s.replace('ءا', 'ا').replace('ة', 'ه').replace('ى', 'ي')
    for a, b in (('هاذ', 'هذ'), ('ذالك', 'ذلك'), ('اولائك', 'اولئك'), ('لاكن', 'لكن'),
                 ('الرحمان', 'الرحمن'), ('ابراهم', 'ابراهيم')):
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()

def _words(s):
    return [w for w in re.split(r'[\s،,.:؛]+', norm(s)) if w]

def _strip(w):
    return w[1:] if w[:1] in 'وف' else w

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

# the standard Egyptian order of revelation (the 1924 Cairo edition): position -> surah number; 86 Meccan, then 28 Medinan
CHRONO = [96, 68, 73, 74, 1, 111, 81, 87, 92, 89, 93, 94, 103, 100, 108, 102, 107, 109, 105, 113, 114, 112, 53, 80, 97, 91, 85, 95, 106, 101,
          75, 104, 77, 50, 90, 86, 54, 38, 7, 72, 36, 25, 35, 19, 20, 56, 26, 27, 28, 17, 10, 11, 12, 15, 6, 37, 31, 34, 39, 40,
          41, 42, 43, 44, 45, 46, 51, 88, 18, 16, 71, 14, 21, 23, 32, 52, 67, 69, 70, 78, 79, 82, 84, 30, 29, 83,
          2, 8, 3, 33, 60, 4, 99, 57, 47, 13, 55, 76, 65, 98, 59, 24, 22, 63, 58, 49, 66, 64, 61, 62, 48, 5, 9, 110]

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
NOUNS = [('rizq', 'رِزْق', 'rizq, provision'), ('raziq', 'رازِق', 'raziq, provider'), ('razzaq', 'الرَّزَّاق', 'ar-Razzaq, the Provider')]

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

# ---------------------------------------------------------------- the corpus
def _read():
    """Verse texts in mushaf order, the roots in each verse, and every ر ز ق token with its word position."""
    verses = {f'{s}:{a}': t for (s, a), t in load_verses(load_words()).items()}
    roots = collections.defaultdict(list)
    tokens = collections.defaultdict(list)
    for r in _read_rows():
        key = f"{r['sura']}:{r['aya']}"
        feats = r['feats'].split('|')
        root = next((p[5:] for p in feats if p.startswith('ROOT:')), None)
        if root:
            roots[key].append(root)
        if root == ROOT:
            lem = next((p[4:] for p in feats if p.startswith('LEM:')), None)
            tokens[key].append({'w': r['word'], 'form': r['form'], 'pos': r['pos'], 'lemma': lem,
                                'tags': {p for p in feats if not p.startswith(('ROOT:', 'LEM:'))}})
    return verses, roots, tokens

def _agent(tok):
    t = tok['tags']
    if tok['pos'] != 'V':
        return {'رَزّاق': 'razzaq', 'رازِق': 'raziq'}.get(tok['lemma'], 'rizq')
    if 'PASS' in t: return 'passive'
    if 'IMPV' in t and '2MS' in t: return 'ask'
    if 'IMPV' in t and '2MP' in t: return 'people'
    if '1P' in t: return 'we'
    if '3MS' in t: return 'he'
    if '2MS' in t: return 'you'
    return 'other'

def _association(all_keys, roots, target):
    """Which roots come in the target verses more than in the rest: log-odds with a Dirichlet prior (alpha 0.5) and its z."""
    a, b = collections.Counter(), collections.Counter()
    for k in all_keys:
        (a if k in target else b).update(set(roots[k]) - {ROOT})
    n1, n2, n = len(target), len(all_keys) - len(target), len(all_keys)
    rows = []
    for r in set(a) | set(b):
        x, y = a[r], b[r]
        if x < 3:
            continue
        d = math.log((x + .5) / (n1 - x + .5)) - math.log((y + .5) / (n2 - y + .5))
        var = 1 / (x + .5) + 1 / (n1 - x + .5) + 1 / (y + .5) + 1 / (n2 - y + .5)
        rows.append({'root': r, 'n': x, 'rest': y, 'pct': round(100 * x / n1, 1), 'pctAll': round(100 * (x + y) / n, 1),
                     'lift': round((x / n1) / ((x + y) / n), 2), 'z': round(d / math.sqrt(var), 2)})
    rows.sort(key=lambda r: (-r['z'], r['root']))
    return rows

# ---------------------------------------------------------------- the du'a against its verses
def _span_core(words, core):
    """1-based positions of the core phrase inside the verse, or of it with a joined و / ف allowed on the first word."""
    ws = [norm(w) for w in words]
    target = norm(core).split()
    n = len(target)
    for strip in (False, True):
        for i in range(len(ws) - n + 1):
            seg = ws[i:i + n]
            if strip:
                seg, tgt = [_strip(x) for x in seg], [_strip(x) for x in target]
            else:
                tgt = target
            if seg == tgt:
                return list(range(i + 1, i + n + 1))
    return []

def _span_shift(words, text):
    """For a phrase with a changed pronoun: the verse words that the du'a kept (three letters or more)."""
    bag = {_strip(x) for x in _words(text)}
    return [i for i, w in enumerate(words, 1) if _strip(norm(w)) in bag and len(_strip(norm(w))) > 2]

_PUNCT = re.compile('[،,.:؛]')

def _check(seg, verses, rizq, ctx, vocab):
    q = seg.get('q', seg['t'])
    nq = norm(q)
    hits = [k for k in seg['src'] if nq in norm(verses[k])]
    mode = 'text' if hits else 'shift'
    shown = seg['t'].split(' ')
    bag, bag_s = set(), set()
    for k in seg['src']:
        if k not in rizq and k not in ctx:
            raise ValueError(f'du\'a source {k} is neither a rizq verse nor next to one')
        for w in _words(verses[k]):
            bag.add(w); bag_s.add(_strip(w))
    def kept(w):
        n = norm(_PUNCT.sub('', w))
        return 1 if (n in bag or _strip(n) in bag_s) else 0
    kw = [kept(w) for w in shown]
    whole = any(_span_core(verses[k].split(), _PUNCT.sub(' ', seg['t'])) for k in seg['src'])
    src = []
    for k in seg['src']:
        words = verses[k].split()
        hi = set(_span_shift(words, seg['t']))
        if mode == 'text' and k in hits:
            hi |= set(_span_core(words, q))
        src.append({'k': k, 'ctx': k not in rizq, 'hi': sorted(hi)})
    ws = _words(seg['t'])
    def tier(w):
        for cand in (w, _strip(w) if w[:1] in 'وف' else None):
            if cand:
                for name in ('rizq', 'ctx', 'quran'):
                    if cand in vocab[name]:
                        return name
        return 'shift'
    return {'t': seg['t'], 'mode': mode, 'whole': whole, 'kw': kw, 'src': src}, [tier(w) for w in ws]

def _summary(segs, tiers):
    n = len(segs)
    exact = sum(1 for s in segs if s['mode'] == 'text')
    tot = len(tiers)
    c = collections.Counter(tiers)
    shown = sum(len(s['kw']) for s in segs)
    kept = sum(sum(s['kw']) for s in segs)
    return {'segments': n, 'text': exact, 'shift': n - exact, 'whole': sum(1 for s in segs if s['whole']),
            'words': shown, 'kept': kept, 'pctKept': round(100 * kept / shown),
            'pctRizq': round(100 * c['rizq'] / tot), 'pctQuran': round(100 * (tot - c['shift']) / tot),
            'ctx': sorted({s['k'] for seg in segs for s in seg['src'] if s['ctx']}, key=_order)}

def _order(k):
    s, a = k.split(':')
    return int(s), int(a)

# ---------------------------------------------------------------- build
def build():
    verses, roots, tokens = _read()
    all_keys = list(verses)
    rizq_keys = [k for k in all_keys if k in tokens]
    rizq = set(rizq_keys)
    meta = _surah_meta()
    period = lambda k: 'm' if meta[int(k.split(':')[0])]['p'] == 'Mecca' else 'd'

    if sorted(CHRONO) != list(range(1, 115)):
        raise ValueError('the order of revelation is not a permutation of the 114 surahs')
    theme_of = {}
    for i, (ar, _, ks) in enumerate(THEMES):
        if ar not in GROUP_OF_THEME: raise ValueError(f'theme {ar} has no group')
        for k in ks:
            if k not in rizq: raise ValueError(f'theme verse {k} has no ر ز ق word')
            if k in theme_of: raise ValueError(f'theme verse {k} labelled twice')
            theme_of[k] = i
    if set(theme_of) != rizq:
        raise ValueError(f'unlabelled rizq verses: {sorted(rizq - set(theme_of), key=_order)}')

    ctx = set()
    for k in rizq_keys:
        s, a = _order(k)
        for d in (-1, 1):
            kk = f'{s}:{a + d}'
            if kk in verses and kk not in rizq:
                ctx.add(kk)
    vocab = {'rizq': {w for k in rizq for w in _words(verses[k])},
             'ctx': {w for k in ctx for w in _words(verses[k])},
             'quran': {w for k in verses for w in _words(verses[k])}}

    # the du'a, each phrase checked
    full, tiers_f = [], []
    for ar, en, segs in FULL:
        out = []
        for seg in segs:
            s, t = _check(seg, verses, rizq, ctx, vocab)
            out.append(s); tiers_f += t
        full.append({'ar': ar, 'en': en, 'segs': out})
    short, tiers_s = [], []
    for seg in SHORT:
        s, t = _check(seg, verses, rizq, ctx, vocab)
        short.append(s); tiers_s += t
    flat_full = [s for p in full for s in p['segs']]

    # who provides
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    for k in rizq_keys:
        for tok in tokens[k]:
            lab = _agent(tok)
            counts[lab] += 1
            if len(examples[lab]) < 4:
                examples[lab].append(k)
    if counts['other']:
        raise ValueError('a ر ز ق verb with no subject tag')
    agents = [{'id': i, 'ar': ar, 'en': en, 'n': counts[i], 'ex': examples[i]} for i, ar, en in AGENTS]
    nouns = [{'id': i, 'ar': ar, 'en': en, 'n': counts[i], 'ex': examples[i]} for i, ar, en in NOUNS]

    # what sits with rizq in the same verse
    assoc = []
    for r in _association(all_keys, roots, rizq):
        if r['root'] in GENERIC:
            continue
        g = GLOSS.get(r['root'], (r['root'], r['root']))
        if r['root'] not in NET_GROUP_OF: raise ValueError(f"root {r['root']} has no network group")
        r.update({'ar': g[0], 'en': g[1], 'g': NET_GROUP_OF[r['root']], 'verses': [k for k in rizq_keys if r['root'] in roots[k]]})
        if len(r['verses']) != r['n']:
            raise ValueError(f"root {r['root']}: {len(r['verses'])} verses listed, {r['n']} counted")
        assoc.append(r)
        if len(assoc) == N_ASSOC:
            break

    models = []
    for k, ar, en, spans in MODELS:
        n = len(verses[k].split())
        if spans[-1][1] > n:
            raise ValueError(f'{k} has {n} words, span to {spans[-1][1]}')
        models.append({'k': k, 'ar': ar, 'en': en, 'spans': [list(s) for s in spans]})

    conditions = []
    for ar, en, ks, ev in CONDITIONS:
        for k in ks:
            if k not in rizq: raise ValueError(f'condition verse {k} has no ر ز ق word')
        conditions.append({'ar': ar, 'en': en, 'n': len(ks), 'verses': sorted(ks, key=_order), 'ev': ev})

    vs = [{'k': k, 'p': period(k), 't': theme_of[k], 'w': [t['w'] for t in tokens[k]]} for k in rizq_keys]
    surahs = {int(k.split(':')[0]) for k in rizq_keys}
    return {
        'totals': {'tokens': sum(len(v) for v in tokens.values()), 'verses': len(rizq_keys), 'surahs': len(surahs),
                   'mecca': sum(1 for v in vs if v['p'] == 'm'), 'medina': sum(1 for v in vs if v['p'] == 'd'),
                   'verbs': sum(a['n'] for a in agents), 'nouns': sum(x['n'] for x in nouns), 'quran': len(all_keys)},
        'themes': [{'ar': ar, 'en': en, 'n': len(ks), 'mecca': sum(1 for k in ks if period(k) == 'm'), 'g': GROUP_OF_THEME[ar]} for ar, en, ks in THEMES],
        'groups': [{'ar': ar, 'en': en} for ar, en in GROUPS],
        'netGroups': [{'ar': ar, 'en': en} for ar, en in NET_GROUPS],
        'chrono': list(CHRONO),
        'verses': vs,
        'agents': agents, 'nouns': nouns,
        'assoc': assoc,
        'conditions': conditions,
        'models': models,
        'dua': {'full': full, 'short': short,
                'sum': {'full': _summary(flat_full, tiers_f), 'short': _summary(short, tiers_s)}},
    }

if __name__ == '__main__':
    import json
    R = build()
    print(json.dumps(R['totals'], ensure_ascii=False))
    print('themes', [(t['ar'], t['n'], t['mecca']) for t in R['themes']])
    print('agents', [(a['id'], a['n']) for a in R['agents']], 'nouns', [(a['id'], a['n']) for a in R['nouns']])
    print('assoc', [(r['root'], r['n'], r['rest'], r['z']) for r in R['assoc']])
    print('dua', R['dua']['sum'])
    for p in R['dua']['full']:
        for s in p['segs']:
            print(' ', s['mode'], s['t'], [(x['k'], x['hi']) for x in s['src']])
    print('bytes', len(json.dumps(R, ensure_ascii=False, separators=(',', ':')).encode()))
