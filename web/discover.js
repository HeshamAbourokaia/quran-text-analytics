// Daleel's Discoveries: the texts of the nine pre-registered studies (web/app.html reads window.DALEEL_DISCOVER).
// The results are in web/discoveries.js (written by data-build/pipeline/discoveries.py). A text that quotes a
// number is a function of those results D and of number formatters F for the page's language, and returns
// [English, Arabic]; a text without numbers is just [English, Arabic]. As in explain.js, [[key]] or
// [[key|shown words]] is a term you can open, and `...` a formula.
// The plan every study follows is data-build/discover/PREREGISTRATION.md, published before any study was run.
window.DALEEL_DISCOVER = (function () {
  'use strict';
  const REPO = 'https://github.com/HeshamAbourokaia/quran-text-analytics';
  const PREREG = REPO + '/blob/1a7b768/data-build/discover/PREREGISTRATION.md';
  const COMMIT = REPO + '/commit/1a7b768';
  const ORDER = ['d-endings', 'd-rings', 'd-rhyme', 'd-stories', 'd-themes', 'd-companions', 'd-letters', 'd-repeats', 'd-chrono'];
  const VERDICT = { holds: ['Holds', 'ثبتت'], no: ['Does not hold', 'لم تثبت'], mixed: ['Mixed', 'نتيجة مختلطة'], map: ['A map, not a test', 'خريطة لا اختبار'] };
  const vkey = v => (v === 'holds' ? 'holds' : v === 'mixed' ? 'mixed' : 'no');
  // how many shuffles did at least as well as the text itself
  const ge = s => (s && s.ge != null ? s.ge : 0);

  const INTRO = ['Can careful counting find something new in the Quran? We put nine questions to the text. Before running a single test we wrote down how each one would be run and what would count as a yes, and published it. Every answer is here, including the no\'s.',
    'هل يستطيع العدّ الدقيق أن يكشف جديدًا في القرآن؟ طرحنا على النص تسعة أسئلة، وقبل أن نُجري أي اختبارٍ كتبنا كيف سيُجرى كلٌّ منها وما الذي يُعَدّ جوابًا بـ«نعم»، ونشرنا ذلك. وكل الأجوبة هنا، ومنها أجوبة «لا».'];

  // the overview's «how we keep ourselves honest»
  const HOW = [
    { t: ['Write the test down first', 'كتابة الاختبار أولًا'],
      x: ['The nine studies, their data, their tests and the bar for a yes (5%) were published in the project\'s public history before any was run: a [[prereg|pre-registration]]. One change, found before running, is logged there with its reason.',
        'نُشرت الدراسات التسع وبياناتها واختباراتها وحدُّ القبول (٥٪) في السجل العام للمشروع قبل تشغيل أيٍّ منها: وهذا هو [[prereg|التسجيل المسبق]]. وتغييرٌ واحد اكتُشف قبل التشغيل مدوَّنٌ هناك مع سببه.'] },
    { t: ['Compare with chance', 'المقارنة بالمصادفة'],
      x: ['Each test asks how often a shuffled copy of the text does as well: the endings swapped between verses, the rhyme marks moved, the surah turned like a wheel. If shuffled copies often do as well, the pattern is nothing special. This is a [[shuffle|shuffle test]].',
        'يسأل كل اختبار: كم مرةً تبلغ نسخةٌ مخلوطةٌ من النص الحدَّ نفسه؟ تُبدَّل الخواتيم بين الآيات، وتُنقل مواضع تغيّر الفاصلة، وتُدار السورة كالعجلة. فإن بلغته النسخ المخلوطة كثيرًا فليس في النمط ما يميّزه. وهذا هو [[shuffle|اختبار الخلط]].'] },
    { t: ['Count every try', 'عدّ كل محاولة'],
      x: ['Look in enough places and a surprise turns up somewhere ([[lookelsewhere|the look-elsewhere effect]]). Where a study makes several tests, the bar for each is raised ([[multiple|correcting for many tests]]).',
        'إن بحثت في أماكن كثيرة بما يكفي ظهرت مفاجأةٌ في مكانٍ ما ([[lookelsewhere|أثر البحث في كل مكان]]). وحيث تُجري الدراسة اختباراتٍ عدة يُرفع الحدّ لكلٍّ منها ([[multiple|تصحيح تعدّد الاختبارات]]).'] },
    { t: ['Keep the no\'s', 'إبقاء أجوبة «لا»'],
      x: ['Two tests failed. They stay on the site with the same space as the rest: a method that can say no is what makes its yes worth something.',
        'أخفق اختباران، ويبقيان في الموقع بالمساحة نفسها: فالمنهج القادر على قول «لا» هو ما يمنح «نعم» قيمتها.'] },
    { t: ['Say what was known', 'بيان ما كان معروفًا'],
      x: ['Each study says what scholars had found or held before, so that confirming a known result is not sold as a discovery.',
        'تذكر كل دراسةٍ ما وجده العلماء أو قالوه من قبل، كي لا يُقدَّم تأكيدُ نتيجةٍ معروفة على أنه اكتشاف.'] },
  ];

  // the themes of study 5, by their top words (names only for the stable ones, as pre-registered)
  const THEMES = [
    ['Stories and dialogue', 'القصص والحوار'],
    ['The Lord\'s mercy and praise', 'الربّ ورحمته وحمده'],
    ['Believers, disbelievers and their reward', 'المؤمنون والكافرون وجزاؤهم'],
    ['God, His Messenger and obedience', 'الله ورسوله والطاعة'],
    ['What each soul does', 'ما تعمله كل نفس'],
    ['The Book and its signs', 'الكتاب وآياته'],
    ['The Day of Judgement', 'يوم القيامة'],
    ['How past nations ended', 'عاقبة الأمم السابقة'],
    ['Creation: the heavens and the earth', 'الخلق: السماوات والأرض'],
    ['Denying the messengers and the signs', 'تكذيب الرسل والآيات'],
    null, null,
  ];

  const STUDIES = {
    // ---------------------------------------------------------------- 1
    'd-endings': {
      n: 1, short: ['Verse endings', 'خواتيم الآيات'],
      card: ['Yes, modestly: the rest of a verse points to its closing names more often than chance.', 'نعم، بقدرٍ متواضع: بقية الآية تدلّ على الاسمين الخاتمين أكثر مما تقتضيه المصادفة.'],
      q: ['Do the divine names that close a verse fit what the verse says?', 'هل تلائم الأسماءُ الحسنى في ختام الآية ما تقوله الآية؟'],
      verdicts: D => [{ v: vkey(D.endings.verdict) }],
      lede: (D, F) => { const e = D.endings;
        return [`Yes, though the signal is modest. From the rest of the verse alone, a model trained on other surahs named the closing pair ${F.pc(e.accuracy)} of the time, against ${F.pc(e.baseline)} for always guessing the commonest pair. Endings shuffled at random did as well in ${F.n(ge(e.nullAll))} of ${F.n(e.nullAll.n)} tries, and endings shuffled only within each surah in ${F.n(ge(e.nullWithin))} of ${F.n(e.nullWithin.n)}.`,
          `نعم، وإن كانت الإشارة متواضعة. فمن بقية الآية وحدها أصاب نموذجٌ تدرّب على سورٍ أخرى زوجَ الأسماء الخاتم في ${F.pc(e.accuracy)} من المرات، مقابل ${F.pc(e.baseline)} لمن يخمّن دائمًا الزوج الأكثر ورودًا. ولم تبلغ الخواتيمُ المخلوطة عشوائيًّا هذا الحدَّ إلا في ${F.n(ge(e.nullAll))} من ${F.n(e.nullAll.n)} محاولة، والخواتيمُ المخلوطة داخل كل سورةٍ وحدها إلا في ${F.n(ge(e.nullWithin))} من ${F.n(e.nullWithin.n)}.`]; },
      metrics: (D, F) => { const e = D.endings; return [
        { v: F.pc(e.accuracy), k: ['right guesses', 'نسبة الإصابة'] },
        { v: F.pc(e.baseline), k: ['always guessing the commonest pair', 'لو خمّنّا الزوج الأكثر دائمًا'] },
        { v: F.pc(e.nullWithin.mean), k: ['on average, endings shuffled within surahs', 'متوسط الخلط داخل السور'] },
        { v: F.n(e.nVerses), k: [`verses, from ${e.nSurahs} surahs`, `آيةً من ${F.n(e.nSurahs)} سورة`] }]; },
      simple: {
        asked: ['Many verses end with a pair of God\'s names: «Forgiving, Merciful», «Mighty, Wise», «Hearing, Knowing». Scholars of the Quran\'s style have long held that the pair is chosen to fit what the verse says. We asked whether a computer can see that fit: can the rest of a verse tell which pair will close it?',
          'تُختم آياتٌ كثيرة بزوجٍ من الأسماء الحسنى: «غفور رحيم»، «عزيز حكيم»، «سميع عليم». ويرى علماء البلاغة القرآنية منذ القدم أن الزوج يُختار ليلائم ما تقوله الآية. فسألنا: هل يرى الحاسوب هذه الملاءمة؟ هل تدلّ بقية الآية على الزوج الذي سيختمها؟'],
        how: (D, F) => { const e = D.endings; return [
          `We took the ${F.n(e.nVerses)} verses that end with one of the ${F.n(e.pairs.length)} commonest pairs. We hid the ending, and also removed every word from the same root as its names, so that «forgive» cannot simply point to «Forgiving». A [[logreg|model]] learned from the verses of some surahs and guessed the endings in the others ([[cv|cross-validation]]). To see whether it beat chance we shuffled the endings 2,000 times, retraining each time ([[shuffle|a shuffle test]]); then again, shuffling only within each surah, since a surah may simply have favourite endings.`,
          `أخذنا الآيات الـ${F.n(e.nVerses)} التي تُختم بأحد الأزواج الـ${F.n(e.pairs.length)} الأكثر ورودًا، وأخفينا الخاتمة، وحذفنا كذلك كل كلمةٍ من جذر اسمَيها، كي لا تدلّ «يغفر» على «غفور» دلالةً مباشرة. ثم تعلّم [[logreg|نموذجٌ]] من آيات بعض السور وخمّن الخواتيم في غيرها ([[cv|التحقق المتقاطع]]). ولنعرف هل يتفوّق على المصادفة خلطنا الخواتيم ٢٬٠٠٠ مرة وأعدنا التدريب في كل مرة ([[shuffle|اختبار الخلط]])، ثم كررنا ذلك بالخلط داخل كل سورةٍ وحدها، لأن السورة قد تؤثر خواتيم بعينها.`]; },
        found: (D, F) => { const e = D.endings, p0 = e.pairs[0]; return [
          `It picked the right pair ${F.pc(e.accuracy)} of the time, against ${F.pc(e.baseline)} for always guessing «Forgiving, Merciful», and both shuffle tests pass. It knows «Forgiving, Merciful» best (${F.pc(p0.recall)} of those verses), which tends to follow words of repentance, sin and punishment. For most of the rarer pairs it could not tell.`,
          `أصاب الزوجَ الصحيح في ${F.pc(e.accuracy)} من المرات، مقابل ${F.pc(e.baseline)} لمن يخمّن «غفور رحيم» دائمًا، واجتاز اختبارَي الخلط كليهما. وأحسنُ ما يعرفه «غفور رحيم» (${F.pc(p0.recall)} من آياته)، وهو يأتي في الغالب بعد ألفاظ التوبة والذنب والعقاب. أما أكثر الأزواج الأقل ورودًا فلم يستطع تمييزها.`]; },
        means: ['The fit that scholars described is there in the words themselves, strongly enough to measure: a verse\'s content leans towards its closing names. But it is a lean, not a rule a computer can read off, and most endings stayed hard to predict. Two verses show why: in 5:38 and 5:118 the model expected «Forgiving, Merciful» and the text says «Mighty, Wise». Of 5:118 («if You forgive them»), al-Suyūṭī notes that a reader expects «Forgiving, Merciful» and explains why «Mighty, Wise» is the fitting close: the model stopped at the first reading.',
          'فالملاءمة التي وصفها العلماء حاضرةٌ في الألفاظ نفسها، بقدرٍ يمكن قياسه: مضمون الآية يميل نحو الاسمين اللذين يختمانها. لكنه ميلٌ لا قاعدةٌ يقرؤها الحاسوب، وظلّت أكثر الخواتيم عصيّةً على التنبؤ. وآيتان تبيّنان السبب: في ٥:٣٨ و٥:١١٨ توقّع النموذج «غفور رحيم» والنص يقول «عزيز حكيم». وفي ٥:١١٨ («وإن تغفر لهم») ينبّه السيوطي إلى أن القارئ يتوقع «الغفور الرحيم»، ثم يبيّن لماذا كان «العزيز الحكيم» هو الختام اللائق: فالنموذج وقف عند القراءة الأولى.'],
      },
      sci: {
        purpose: ['Test whether a verse\'s content predicts its closing divine-name pair beyond chance, and beyond its surah\'s own mix of endings.',
          'اختبار ما إذا كان مضمون الآية يتنبأ بزوج الأسماء الحسنى الذي يختمها فوق مستوى المصادفة، وفوق ما تفسّره خواتيم سورتها.'],
        data: (D, F) => { const e = D.endings; return [
          `${F.n(e.nVerses)} verses in ${F.n(e.nSurahs)} surahs (at least 4 words) whose last two words are nouns from two different divine-name roots, the first not قوم, in the ${F.n(e.pairs.length)} ending pairs (ordered root pairs) with at least 8 verses. ${F.n(e.nAllNameEndings)} verses end in such a pair in all.`,
          `${F.n(e.nVerses)} آيةً في ${F.n(e.nSurahs)} سورة (أربع كلماتٍ فأكثر) آخر كلمتين فيها اسمان من جذرين مختلفين من جذور الأسماء الحسنى، أولهما ليس «قوم»، في أزواج الخواتيم الـ${F.n(e.pairs.length)} (أزواج جذورٍ مرتبة) التي لكلٍّ منها ٨ آياتٍ على الأقل. ومجموع الآيات المختومة بزوجٍ كهذا ${F.n(e.nAllNameEndings)}.`]; },
        method: ['Features: the lemmas before the last two words, leaving out the ending\'s two roots; TF-IDF (`min_df = 2`) and multinomial logistic regression (`C = 3`), scored by accuracy under 5-fold cross-validation grouped by surah. Test A: endings permuted across all verses, 2,000 times (seed 7). Test B: permuted within surah, 2,000 times (seed 8). `p = (#{null ≥ obs} + 1) / (B + 1)`, Holm-adjusted over the two.',
          'الخصائص: المداخل المعجمية لما قبل الكلمتين الأخيرتين، دون جذرَي الخاتمة؛ وTF-IDF ‏(`min_df = 2`) مع انحدارٍ لوجستي متعدد الفئات (`C = 3`)، يُقاس بالدقة في تحقّقٍ متقاطعٍ خماسي مجمّعٍ حسب السورة. الاختبار (أ): تبديل الخواتيم بين كل الآيات ٢٬٠٠٠ مرة (البذرة ٧). الاختبار (ب): التبديل داخل السورة ٢٬٠٠٠ مرة (البذرة ٨). `p = (#{null ≥ obs} + 1) / (B + 1)` مع تصحيح هولم للاختبارين.'],
        result: (D, F) => { const e = D.endings, A = e.nullAll, B = e.nullWithin; return [
          `Accuracy ${F.d(e.accuracy, 3)}, baseline ${F.d(e.baseline, 3)}. Test A: null mean ${F.d(A.mean, 3)} (SD ${F.d(A.sd, 3)}, max ${F.d(A.max, 3)}), p = ${F.p(e.pAll)}. Test B: null mean ${F.d(B.mean, 3)} (SD ${F.d(B.sd, 3)}, max ${F.d(B.max, 3)}), p = ${F.p(e.pWithin)}. Holm: ${F.p(e.pHolm[0])} and ${F.p(e.pHolm[1])}, both below 0.05: «holds». Recall by pair: ${e.pairs.map(p => p.en + ' ' + F.d(p.recall, 2)).join('; ')}.`,
          `الدقة ${F.d(e.accuracy, 3)} وخط الأساس ${F.d(e.baseline, 3)}. الاختبار (أ): متوسط التوزيع الصفري ${F.d(A.mean, 3)} (الانحراف المعياري ${F.d(A.sd, 3)}، الأقصى ${F.d(A.max, 3)})، `+'`p = '+F.pl(e.pAll)+'`'+`. الاختبار (ب): المتوسط ${F.d(B.mean, 3)} (الانحراف ${F.d(B.sd, 3)}، الأقصى ${F.d(B.max, 3)})، `+'`p = '+F.pl(e.pWithin)+'`'+`. وبتصحيح هولم: ${F.p(e.pHolm[0])} و${F.p(e.pHolm[1])}، وكلاهما دون ٠٫٠٥: «ثبتت». والاستدعاء لكل زوج: ${e.pairs.map(p => p.ar + ' ' + F.d(p.recall, 2)).join('، ')}.`]; },
        limits: ['The effect is small and carried mostly by one pair; the rarer pairs are close to unpredictable. The TF-IDF weights are fitted on all 230 verses before cross-validation (unsupervised, and the same under every permutation). Refrains repeat one verse (8 times in ash-Shu\'ara), and the grouped folds keep a surah\'s copies together. The closing pair must also fit the surah\'s rhyme (-īm, -īr and so on), which limits the choice; shuffling within surahs keeps each surah\'s mix of endings and so partly allows for this. The model sees words, not meaning.',
          'الأثر صغير، ويحمله زوجٌ واحدٌ في الغالب، والأزواج الأقل ورودًا تكاد لا يُتنبأ بها. وأوزان TF-IDF تُحسب على الآيات الـ٢٣٠ كلها قبل التحقق المتقاطع (دون إشراف، وهي هي في كل تبديل). واللوازم تكرر آيةً واحدة (٨ مرات في الشعراء)، والطيّات المجمّعة تبقي نسخ السورة الواحدة معًا. ويجب أن يوافق الزوجُ الخاتم فاصلةَ السورة أيضًا (ـيم، ـير، وهكذا)، وهذا يضيّق الاختيار، والخلط داخل السورة يحفظ مزيج خواتيمها فيراعي ذلك جزئيًّا. والنموذج يرى الألفاظ لا المعاني.'],
      },
    },

    // ---------------------------------------------------------------- 2
    'd-rings': {
      n: 2, short: ['Mirrors', 'البناء الدائري'],
      card: ['Not in its words: verses at mirror positions are no more alike than chance allows.', 'ليس في ألفاظها: الآيات المتناظرة ليست أشدّ تشابهًا مما تقتضيه المصادفة.'],
      q: ['Is al-Baqarah built as a mirror?', 'هل بُنيت سورة البقرة بناءً دائريًّا متناظرًا؟'],
      verdicts: D => [{ v: vkey(D.rings.baqara.verdict) }],
      lede: (D, F) => { const b = D.rings.baqara, sc = D.rings.scan; return [
        `Not in its words, as far as this test can see. Verses at mirror positions are no more alike than when the surah is turned to start anywhere else (${F.n(ge(b.null))} of ${F.n(b.rotations)} turns did as well; p = ${F.p(b.p)}), and the mirror is strongest around verse ${F.n(Math.round(b.peak[0]))}, not 2:143. None of the ${F.n(sc.length)} long surahs passes the same test.`,
        `ليس في ألفاظها، بقدر ما يرى هذا الاختبار. فالآيات في المواضع المتناظرة ليست أشدّ تشابهًا منها حين تُدار السورة لتبدأ من أي موضعٍ آخر (بلغت ${F.n(ge(b.null))} من ${F.n(b.rotations)} إدارةً هذا الحدّ؛ القيمة الاحتمالية ${F.p(b.p)})، وأقوى التناظر حول الآية ${F.n(Math.round(b.peak[0]))} لا عند ٢:١٤٣. ولم تجتز أيٌّ من السور الطويلة الـ${F.n(sc.length)} الاختبار نفسه.`]; },
      metrics: (D, F) => { const b = D.rings.baqara, sc = D.rings.scan; return [
        { v: F.p(b.p), k: ['p-value (5% needed)', 'القيمة الاحتمالية (المطلوب ٥٪)'] },
        { v: F.k('2:' + Math.round(b.peak[0])), k: ['where the mirror is strongest', 'أقوى موضعٍ للتناظر'] },
        { v: F.n(sc.filter(r => r.bh).length) + ' / ' + F.n(sc.length), k: ['long surahs that pass', 'سورٌ طويلة تجتاز الاختبار'] }]; },
      simple: {
        asked: ['Some scholars read al-Baqarah as a ring: its sections answer each other in mirror order around a centre, the change of the qibla and «a middle nation» (2:143), so that the first part answers the last, the second the second-to-last, and so on. If the wording were built that way, verses at mirror positions should share more words than chance allows.',
          'يقرأ بعض الباحثين سورة البقرة بناءً دائريًّا: تتجاوب أقسامها في ترتيبٍ متناظر حول مركز، هو تحويل القبلة و«أمةً وسطًا» (٢:١٤٣)، فيجاوب الجزءُ الأول الأخير، والثاني ما قبل الأخير، وهكذا. ولو بُنيت ألفاظها على هذا لوجب أن تشترك الآيات في المواضع المتناظرة في ألفاظٍ أكثر مما تسمح به المصادفة.'],
        how: ['We measured how alike every two verses are in their words ([[cosine|cosine similarity]]), took out the plain fact that nearby verses are alike, and averaged the likeness of the mirror pairs: first and last, second and second-to-last, and so on. For chance, we turned the surah like a wheel, starting it at each of its other 285 verses: this moves the mirror\'s centre while every verse keeps its neighbours.',
          'قسنا تشابه كل آيتين في ألفاظهما ([[cosine|تشابه جيب التمام]])، وأزلنا أثر أن الآيات المتجاورة متشابهةٌ أصلًا، ثم أخذنا متوسط التشابه بين الأزواج المتناظرة: الأولى والأخيرة، والثانية وما قبل الأخيرة، وهكذا. وللمقارنة بالمصادفة أدرنا السورة كالعجلة، فبدأناها بكل آيةٍ من آياتها الـ٢٨٥ الأخرى: وهذا ينقل مركز التناظر مع بقاء كل آيةٍ بجوار جاراتها.'],
        found: (D, F) => { const b = D.rings.baqara, sc = D.rings.scan; return [
          `The mirror pairs are a little more alike than average, but a quarter of the turned surahs do as well. The strongest mirror centre falls near verse ${F.n(Math.round(b.peak[0]))}, in the rulings on divorce, not in 130 to 160. Of all ${F.n(sc.length)} surahs of 60 verses or more, none holds once we allow for testing ${F.n(sc.length)} of them.`,
          `الأزواج المتناظرة أشدّ تشابهًا من المتوسط قليلًا، لكن ربع السور المُدارة يبلغ ذلك أيضًا. وأقوى مركزٍ للتناظر يقع قرب الآية ${F.n(Math.round(b.peak[0]))} في أحكام الطلاق، لا بين ١٣٠ و١٦٠. ومن السور الـ${F.n(sc.length)} التي تبلغ آياتها ٦٠ فأكثر لم تثبت النتيجة في أيٍّ منها بعد احتساب أنّا اختبرنا ${F.n(sc.length)} سورة.`]; },
        means: ['The wording of al-Baqarah is not arranged verse by verse as a mirror. That does not rule out a ring of themes: the ring readings pair sections of different lengths by what they are about, and two sections can match in theme while sharing few words. This test sees only the simplest, word-level form of a ring.',
          'فألفاظ البقرة لم تُرتَّب آيةً مقابل آيةٍ ترتيبًا متناظرًا. ولا ينفي هذا تناظرًا في الموضوعات: فالقراءات الدائرية تقابل بين أقسامٍ مختلفة الطول بحسب مضمونها، وقد يتقابل قسمان في الموضوع وهما لا يشتركان إلا في قليلٍ من الألفاظ. وهذا الاختبار لا يرى إلا أبسط صور التناظر، على مستوى الألفاظ.'],
      },
      sci: {
        purpose: ['A pre-registered test of verse-level lexical mirror symmetry in al-Baqarah (after the ring reading with its centre at 2:142–152), with an exploratory scan of every surah of at least 60 verses.',
          'اختبارٌ مسجَّلٌ مسبقًا للتناظر اللفظي على مستوى الآيات في سورة البقرة (بعد القراءة الدائرية التي تجعل مركزها ٢:١٤٢–١٥٢)، مع مسحٍ استكشافي لكل سورةٍ تبلغ آياتها ٦٠ فأكثر.'],
        data: ['Verse vectors: TF-IDF over the lemmas of content words (N, V), `min_df = 2`, sublinear tf, unit rows, fitted on all 6,236 verses; similarity is their cosine.',
          'متجهات الآيات: TF-IDF لمداخل كلمات المضمون (الأسماء والأفعال)، `min_df = 2`، مع تكرارٍ لوغاريتمي وتطبيعٍ للصفوف، على الآيات الـ٦٬٢٣٦ كلها؛ والتشابه جيب التمام بينها.'],
        method: ['Residual similarity `r(i, j) = s(i, j) − e(|i − j|)`, with `e(d)` the mean similarity at distance d for d ≤ 20, and the mean beyond 20 otherwise. Statistic: mean r over the mirror pairs `(i, n + 1 − i)` at distance ≥ 2. Null: all n − 1 cyclic rotations of the verse order, `p = (#{null ≥ obs} + 1) / n`. Scan: the same test per surah, Benjamini–Hochberg at q = 0.10.',
          'التشابه المتبقّي `r(i, j) = s(i, j) − e(|i − j|)`، حيث `e(d)` متوسط التشابه عند المسافة d إذا كانت ٢٠ فأقل، والمتوسط فيما وراء ٢٠ فيما سوى ذلك. الإحصاءة: متوسط r على الأزواج المتناظرة `(i, n + 1 − i)` التي بينها آيتان فأكثر. التوزيع الصفري: الإدارات الدائرية كلها (n − 1) لترتيب الآيات، و`p = (#{null ≥ obs} + 1) / n`. والمسح: الاختبار نفسه لكل سورة، مع بنجاميني–هوخبرغ عند `q = 0.10`.'],
        result: (D, F) => { const b = D.rings.baqara, sc = D.rings.scan, lo = sc.reduce((a, r) => (r.p < a.p ? r : a), sc[0]); return [
          `Statistic ${F.d(b.stat, 4)} (rotations: mean ${F.d(b.null.mean, 4)}, SD ${F.d(b.null.sd, 4)}; z = ${F.d(b.null.z, 1)}); p = ${F.p(b.p)}. The profile over centres with at least 30 pairs peaks at verse ${F.n(Math.round(b.peak[0]))}, outside 130–160. Scan: the lowest p is surah ${lo.n} (${F.p(lo.p)}); none survives Benjamini–Hochberg.`,
          `الإحصاءة ${F.d(b.stat, 4)} (الإدارات: المتوسط ${F.d(b.null.mean, 4)}، الانحراف ${F.d(b.null.sd, 4)}؛ `+'`z = '+F.dl(b.null.z, 1)+'`'+`)، والقيمة الاحتمالية ${F.p(b.p)}. ومنحنى المراكز التي لها ٣٠ زوجًا فأكثر يبلغ ذروته عند الآية ${F.n(Math.round(b.peak[0]))}، خارج ١٣٠–١٦٠. وفي المسح أدنى قيمةٍ احتمالية للسورة ${F.n(lo.n)} (${F.p(lo.p)})، ولا يصمد شيءٌ بعد تصحيح بنجاميني–هوخبرغ.`]; },
        limits: ['Verse-for-verse mirroring assumes sections of equal length on both sides of the centre; ring readings pair sections of unequal length by theme. Shared vocabulary is a narrow stand-in for thematic correspondence. Rotations keep local structure but not the surah\'s own beginning and end.',
          'التناظر آيةً مقابل آية يفترض أقسامًا متساوية الطول على جانبي المركز، والقراءات الدائرية تقابل أقسامًا غير متساوية بحسب الموضوع. والألفاظ المشتركة مقياسٌ ضيّقٌ للتقابل في المعنى. والإدارات تحفظ البنية المحلية لكنها لا تحفظ بداية السورة ونهايتها.'],
      },
    },

    // ---------------------------------------------------------------- 3
    'd-rhyme': {
      n: 3, short: ['Rhyme', 'الفواصل'],
      card: ['Yes: where the rhyme changes, the subject tends to move on.', 'نعم: حيث تتغيّر الفاصلة يميل الموضوع إلى الانتقال.'],
      q: ['Does the rhyme change where the topic changes?', 'هل تتغيّر الفاصلة حيث يتغيّر الموضوع؟'],
      verdicts: D => [{ v: vkey(D.rhyme.verdict) }],
      lede: (D, F) => { const r = D.rhyme; return [
        `Yes. Where the verse-end rhyme changes, the verses that follow move further from the words before than where the rhyme carries on. The gap is small, but ${ge(r.null) ? F.n(ge(r.null)) + ' of' : 'none of'} ${F.n(r.null.n)} shuffles produced one as big (p = ${F.p(r.p)}).`,
        `نعم. حيث تتغيّر الفاصلة في أواخر الآيات تبتعد ألفاظ ما بعدها عن ألفاظ ما قبلها أكثر مما تبتعد حيث تستمر الفاصلة. والفرق صغير، لكن ${ge(r.null) ? F.n(ge(r.null)) + ' فقط' : 'لا شيء'} من ${F.n(r.null.n)} خلطةً بلغ مثله (القيمة الاحتمالية ${F.p(r.p)}).`]; },
      metrics: (D, F) => { const r = D.rhyme; return [
        { v: F.d(r.meanChanged, 3), k: ['topic change where the rhyme changes', 'تغيّر الموضوع حيث تتغيّر الفاصلة'] },
        { v: F.d(r.meanSame, 3), k: ['where the rhyme carries on', 'حيث تستمر الفاصلة'] },
        { v: F.n(r.changes), k: [`rhyme changes, of ${F.n(r.boundaries)} places`, `تغيّرًا في الفاصلة من ${F.n(r.boundaries)} موضعًا`] },
        { v: F.p(r.p), k: ['p-value', 'القيمة الاحتمالية'] }]; },
      simple: {
        asked: ['Verses end in rhyme, the fāṣila: long runs ending in -ūn and -īn, in -ā, in -īm and so on. Scholars have used changes of rhyme to divide surahs into sections. We asked whether the rhyme really follows the subject: when the rhyme changes, does the topic change too?',
          'تنتهي الآيات بالفاصلة: سلاسل طويلة تنتهي بـ«ـون» و«ـين»، أو بالألف، أو بـ«ـيم»، وهكذا. واستعان الباحثون بتغيّر الفاصلة لتقسيم السور إلى مقاطع. فسألنا: هل تتبع الفاصلة الموضوع حقًّا؟ إذا تغيّرت الفاصلة، هل يتغيّر الموضوع أيضًا؟'],
        how: ['At each place between two verses of a surah we measured how much the words change: the three verses before against the three after, from 0 (the same words) to 1 (none shared). Then we compared the places where the rhyme changes with those where it carries on. For chance, we shuffled which places count as rhyme changes, within each surah, 2,000 times.',
          'عند كل موضعٍ بين آيتين من سورةٍ قسنا مقدار تغيّر الألفاظ: الآيات الثلاث قبله مقابل الثلاث بعده، من ٠ (الألفاظ نفسها) إلى ١ (لا شيء مشترك). ثم قارنّا المواضع التي تتغيّر فيها الفاصلة بالتي تستمر فيها. وللمقارنة بالمصادفة خلطنا المواضع التي تُعَدّ تغيّرًا في الفاصلة، داخل كل سورة، ٢٬٠٠٠ مرة.'],
        found: (D, F) => { const r = D.rhyme; return [
          `Where the rhyme changes the topic change is ${F.d(r.meanChanged, 3)}, against ${F.d(r.meanSame, 3)} where it carries on. That is small, yet the shuffles never came close: the real gap sits ${F.d(r.null.z, 1)} typical steps above their average. It holds in both Meccan and Medinan surahs, and with two or four verses on each side instead of three.`,
          `حيث تتغيّر الفاصلة يبلغ تغيّر الموضوع ${F.d(r.meanChanged, 3)}، مقابل ${F.d(r.meanSame, 3)} حيث تستمر. وهو فرقٌ صغير، لكن الخلطات لم تقترب منه: فالفرق الحقيقي يعلو متوسطها بـ${F.d(r.null.z, 1)} من خطواتها المعتادة. ويثبت في السور المكية والمدنية معًا، وبآيتين أو أربعٍ على كل جانبٍ بدل ثلاث.`]; },
        means: ['The rhyme works a little like a paragraph mark: when the sound changes, the subject tends to move on. It is a tendency, not a rule: many topic shifts keep the rhyme, and many rhyme changes are small steps. It gives numbers to the practice of reading rhyme changes as section breaks.',
          'فالفاصلة تعمل عملَ علامة الفقرة بعض الشيء: إذا تغيّر الصوت مال الموضوع إلى الانتقال. وهو ميلٌ لا قاعدة: فتحوّلاتٌ كثيرة في الموضوع تبقى على الفاصلة نفسها، وتغيّراتٌ كثيرة في الفاصلة خطواتٌ صغيرة. وهذا يمنح أرقامًا لعادة قراءة تغيّر الفاصلة حدًّا بين المقاطع.'],
      },
      sci: {
        purpose: ['A pre-registered test of whether changes of rhyme (fāṣila) coincide with lexical topic shifts inside surahs.',
          'اختبارٌ مسجَّلٌ مسبقًا لتزامن تغيّر الفاصلة مع التحوّل اللفظي في الموضوع داخل السور.'],
        data: (D, F) => { const r = D.rhyme; return [
          `Rhyme from the verse's last word, normalized: a long vowel (ا, or و and ي counted as one) with the final consonant, else the final letter. ${F.n(r.boundaries)} boundaries with 3 verses on each side inside a surah; ${F.n(r.changes)} are rhyme changes.`,
          `الفاصلة من آخر كلمةٍ في الآية بعد التطبيع: حرف مدّ (الألف، أو الواو والياء معدودتين واحدًا) مع الحرف الأخير، وإلا فالحرف الأخير وحده. ${F.n(r.boundaries)} موضعًا لكلٍّ منها ثلاث آياتٍ على كل جانبٍ داخل السورة، منها ${F.n(r.changes)} تتغيّر فيها الفاصلة.`]; },
        method: ['Topic change at a boundary: `1 − cos(Σ v₍b−2..b₎, Σ v₍b+1..b+3₎)` over the verse TF-IDF vectors. Statistic: mean change where the rhyme changes minus mean where it stays. Null: the rhyme-change labels permuted within each surah (keeping its count), 2,000 times, seed 11; one-sided p.',
          'تغيّر الموضوع عند الموضع: `1 − cos(Σ v₍b−2..b₎, Σ v₍b+1..b+3₎)` على متجهات TF-IDF للآيات. الإحصاءة: متوسط التغيّر حيث تتغيّر الفاصلة ناقص متوسطه حيث تبقى. التوزيع الصفري: تبديل علامات تغيّر الفاصلة داخل كل سورة (مع حفظ عددها) ٢٬٠٠٠ مرة، البذرة ١١؛ قيمةٌ احتمالية من طرفٍ واحد.'],
        result: (D, F) => { const r = D.rhyme, w = r.robust; return [
          `Difference ${F.d(r.stat, 4)} (null mean ${F.d(r.null.mean, 4)}, SD ${F.d(r.null.sd, 4)}, max ${F.d(r.null.max, 4)}; z = ${F.d(r.null.z, 1)}); p = ${F.p(r.p)}. Meccan ${F.d(r.split.Mecca.diff, 4)} (${F.n(r.split.Mecca.boundaries)} boundaries), Medinan ${F.d(r.split.Medina.diff, 4)} (${F.n(r.split.Medina.boundaries)}). Exploratory: windows of ${w.map(x => x.window).join(' and ')} verses give ${w.map(x => F.d(x.stat, 4) + ' (p = ' + F.p(x.p) + ')').join(' and ')}, 1,000 permutations each.`,
          `الفرق ${F.d(r.stat, 4)} (متوسط التوزيع الصفري ${F.d(r.null.mean, 4)}، الانحراف ${F.d(r.null.sd, 4)}، الأقصى ${F.d(r.null.max, 4)}؛ `+'`z = '+F.dl(r.null.z, 1)+'`'+`)، والقيمة الاحتمالية ${F.p(r.p)}. المكي ${F.d(r.split.Mecca.diff, 4)} (${F.n(r.split.Mecca.boundaries)} موضعًا)، والمدني ${F.d(r.split.Medina.diff, 4)} (${F.n(r.split.Medina.boundaries)}). واستكشافيًّا: نافذتا ${w.map(x => F.n(x.window)).join(' و')} آيات تعطيان ${w.map(x => F.d(x.stat, 4) + ' (' + F.p(x.p) + ')').join(' و')}، بألف تبديلٍ لكلٍّ منهما.`]; },
        limits: ['A small effect on a 0–1 scale, found by averaging thousands of boundaries. The rhyme rule simplifies the fāṣila. Topic change here is lexical: synonyms and pronouns are invisible to it. Within-surah permutation keeps each surah\'s number of rhyme changes, not their spacing. Verse ends follow the Kufan count (the standard mushaf\'s); another count moves some of them.',
          'أثرٌ صغيرٌ على مقياسٍ من ٠ إلى ١، ظهر بأخذ المتوسط على آلاف المواضع. وقاعدة الفاصلة هنا تبسيطٌ لها. وتغيّر الموضوع هنا لفظي: لا يرى المترادفات ولا الضمائر. والتبديل داخل السورة يحفظ عدد تغيّرات الفاصلة فيها لا تباعدها. ونهايات الآيات على العدّ الكوفي (عدّ المصحف المعتاد)، وعدٌّ آخر ينقل بعضها.'],
      },
    },

    // ---------------------------------------------------------------- 4
    'd-stories': {
      n: 4, short: ['Retold stories', 'القصص المكررة'],
      card: ['Yes: each telling shares more words with its own surah than with the others that tell the story.', 'نعم: كل روايةٍ تشارك سورتها في الألفاظ أكثر مما تشارك السور الأخرى التي تروي القصة.'],
      q: ['Is each retelling of a prophet\'s story tuned to its own surah?', 'هل تُصاغ كل روايةٍ لقصة نبيٍّ على مقاس سورتها؟'],
      verdicts: D => [{ v: vkey(D.retellings.verdict) }],
      lede: (D, F) => { const t = D.retellings, own = t.each.filter(x => x.own > x.others).length; return [
        `Yes. A retelling shares more words with the rest of its own surah than with the other surahs that tell the same story: in ${F.n(own)} of the ${F.n(t.tellings)} tellings, and on average far beyond chance (${ge(t.null) ? F.n(ge(t.null)) + ' of' : 'none of'} ${F.n(t.null.n)} random reassignments did as well; p = ${F.p(t.p)}).`,
        `نعم. تشترك الرواية مع بقية سورتها في ألفاظٍ أكثر مما تشترك مع السور الأخرى التي تروي القصة نفسها: في ${F.n(own)} من ${F.n(t.tellings)} رواية، وبمتوسطٍ يتجاوز المصادفة بكثير (${ge(t.null) ? 'بلغته ' + F.n(ge(t.null)) + ' فقط' : 'لم تبلغه أيٌّ'} من ${F.n(t.null.n)} إعادة توزيعٍ عشوائية؛ القيمة الاحتمالية ${F.p(t.p)}).`]; },
      metrics: (D, F) => { const t = D.retellings, own = t.each.filter(x => x.own > x.others).length; return [
        { v: F.n(own) + ' / ' + F.n(t.tellings), k: ['tellings closer to their own surah', 'روايةً أقرب إلى سورتها'] },
        { v: F.n(t.prophets.Moses.n), k: ['surahs that tell Moses\'s story', 'سورةً تروي قصة موسى'] },
        { v: F.n(t.prophets.Abraham.n), k: ['surahs that tell Abraham\'s', 'سورٍ تروي قصة إبراهيم'] },
        { v: F.p(t.p), k: ['p-value', 'القيمة الاحتمالية'] }]; },
      simple: {
        asked: ['The Quran tells the stories of the prophets many times: Moses\'s in more than a dozen surahs, Abraham\'s in nine. Readers have long noted that each telling brings out the details that serve its surah. We asked whether that shows in the words: does a telling sound more like its own surah than like the other surahs that tell the same story?',
          'يروي القرآن قصص الأنبياء مراتٍ كثيرة: قصة موسى في أكثر من اثنتي عشرة سورة، وقصة إبراهيم في تسع. ولاحظ القرّاء منذ القدم أن كل روايةٍ تُبرز من التفاصيل ما يخدم سورتها. فسألنا: هل يظهر هذا في الألفاظ؟ هل تشبه الرواية سورتها أكثر مما تشبه السور الأخرى التي تروي القصة نفسها؟'],
        how: ['A telling is the verses of one surah that name the prophet (at least three of them). We compared its words with the rest of its own surah, leaving out three verses on each side so the story does not meet itself, and with the rest of each other surah that tells the story. For chance, we gave each telling to another surah at random, 5,000 times.',
          'الرواية هي آيات السورة التي تذكر النبي باسمه (ثلاثٌ على الأقل). قارنّا ألفاظها ببقية سورتها، بعد ترك ثلاث آياتٍ على كل جانبٍ كي لا تلقى القصة نفسها، وببقية كل سورةٍ أخرى تروي القصة. وللمقارنة بالمصادفة أعطينا كل روايةٍ لسورةٍ أخرى عشوائيًّا، ٥٬٠٠٠ مرة.'],
        found: (D, F) => { const t = D.retellings, own = t.each.filter(x => x.own > x.others).length, ab = t.robust[0]; return [
          `In ${F.n(own)} of ${F.n(t.tellings)} tellings the telling is closer to its own surah (Moses: ${F.n(t.prophets.Moses['own>others'])} of ${F.n(t.prophets.Moses.n)}; Abraham: ${F.n(t.prophets.Abraham['own>others'])} of ${F.n(t.prophets.Abraham.n)}). The average gap is ${F.d(t.stat, 3)}; the random reassignments averaged ${F.d(t.null.mean, 3)} and never reached it. Abraham's tellings alone pass too (p = ${F.p(ab.p)}).`,
          `في ${F.n(own)} من ${F.n(t.tellings)} روايةً تكون الرواية أقرب إلى سورتها (موسى: ${F.n(t.prophets.Moses['own>others'])} من ${F.n(t.prophets.Moses.n)}، وإبراهيم: ${F.n(t.prophets.Abraham['own>others'])} من ${F.n(t.prophets.Abraham.n)}). ومتوسط الفرق ${F.d(t.stat, 3)}، ومتوسط إعادات التوزيع العشوائية ${F.d(t.null.mean, 3)} ولم تبلغه قط. وروايات إبراهيم وحدها تجتاز الاختبار أيضًا (القيمة الاحتمالية ${F.p(ab.p)}).`]; },
        means: ['The stories are not copies dropped into different places: each telling shares the vocabulary of the surah around it. That is a measurable trace of what commentators describe as each retelling serving its surah. What we measure is shared words; whether they carry the surah\'s theme is for a reader to judge, and the lists below help.',
          'فالقصص ليست نسخًا أُسقطت في مواضع مختلفة، بل تشارك كل روايةٍ السورةَ التي حولها في معجمها. وهذا أثرٌ قابلٌ للقياس لما يصفه المفسرون من أن كل روايةٍ تخدم سورتها. والذي نقيسه هو الألفاظ المشتركة، أما حملها لموضوع السورة فحكمه للقارئ، والقوائم أدناه تعينه.'],
      },
      sci: {
        purpose: ['A pre-registered test of surah-specific lexical adaptation in retold prophetic narratives.',
          'اختبارٌ مسجَّلٌ مسبقًا لتكيّف ألفاظ القصص النبوية المكررة مع سورها.'],
        data: (D, F) => { const t = D.retellings; return [
          `A telling: in one surah, the verses that name the prophet as a proper noun (the corpus's PN tag; for Moses also Pharaoh), at least 3 verses; prophets with tellings in at least 5 surahs: Moses (${F.n(t.prophets.Moses.n)}) and Abraham (${F.n(t.prophets.Abraham.n)}), ${F.n(t.tellings)} tellings. The rest of a surah: its other verses, leaving out 3 verses on each side of every telling verse.`,
          `الرواية: آيات السورة الواحدة التي تذكر النبي علَمًا (وسم PN في المدونة، ولموسى يُضاف فرعون)، ثلاث آياتٍ على الأقل. والأنبياء الذين لهم رواياتٌ في ٥ سورٍ فأكثر: موسى (${F.n(t.prophets.Moses.n)}) وإبراهيم (${F.n(t.prophets.Abraham.n)})، أي ${F.n(t.tellings)} رواية. وبقية السورة: آياتها الأخرى بعد ترك ثلاث آياتٍ على جانبي كل آيةٍ من الرواية.`]; },
        method: ['Per telling: `cos(T_s, R_s) − mean₍o≠s₎ cos(T_s, R_o)` over summed TF-IDF verse vectors; the statistic is the mean over tellings. Null: random derangements of the surahs within each prophet, 5,000, seed 13; one-sided p.',
          'لكل رواية: `cos(T_s, R_s) − mean₍o≠s₎ cos(T_s, R_o)` على مجاميع متجهات TF-IDF للآيات، والإحصاءة متوسطها على الروايات. التوزيع الصفري: تباديل عشوائية بلا نقاطٍ ثابتة للسور داخل كل نبي، ٥٬٠٠٠ مرة، البذرة ١٣؛ من طرفٍ واحد.'],
        result: (D, F) => { const t = D.retellings, ab = t.robust[0]; return [
          `Statistic ${F.d(t.stat, 4)} (null mean ${F.d(t.null.mean, 4)}, SD ${F.d(t.null.sd, 4)}, max ${F.d(t.null.max, 4)}; z = ${F.d(t.null.z, 1)}); p = ${F.p(t.p)}. Moses: mean ${F.d(t.prophets.Moses.mean, 4)}; Abraham: ${F.d(t.prophets.Abraham.mean, 4)}. Exploratory, Abraham alone (${F.n(ab.tellings)} tellings): ${F.d(ab.stat, 4)}, p = ${F.p(ab.p)}.`,
          `الإحصاءة ${F.d(t.stat, 4)} (متوسط التوزيع الصفري ${F.d(t.null.mean, 4)}، الانحراف ${F.d(t.null.sd, 4)}، الأقصى ${F.d(t.null.max, 4)}؛ `+'`z = '+F.dl(t.null.z, 1)+'`'+`)، والقيمة الاحتمالية ${F.p(t.p)}. موسى: المتوسط ${F.d(t.prophets.Moses.mean, 4)}، وإبراهيم: ${F.d(t.prophets.Abraham.mean, 4)}. واستكشافيًّا، إبراهيم وحده (${F.n(ab.tellings)} روايات): ${F.d(ab.stat, 4)}، والقيمة الاحتمالية ${F.p(ab.p)}.`]; },
        limits: ['Only two prophets qualify, so the result speaks of Moses and Abraham. Nearby verses were left out, but surah-wide style (rhyme words, recurring formulas) still counts as shared vocabulary. Tellings found by the name miss verses that tell the story without it.',
          'لا يستوفي الشرط إلا نبيّان، فالنتيجة عن موسى وإبراهيم. وقد تُركت الآيات المجاورة، لكن أسلوب السورة العام (ألفاظ الفواصل والعبارات المتكررة) ما زال يُحسب ألفاظًا مشتركة. والروايات المحددة بالاسم تفوتها آياتٌ تروي القصة دون ذكره.'],
      },
    },

    // ---------------------------------------------------------------- 5
    'd-themes': {
      n: 5, short: ['Themes', 'الموضوعات'], map: true,
      card: ['Ten stable themes, found from the words alone and mapped verse by verse.', 'عشرة موضوعاتٍ ثابتة، استُخرجت من الألفاظ وحدها ورُسمت آيةً آية.'],
      q: ['What are the Quran\'s main themes, and where do they run?', 'ما الموضوعات الكبرى في القرآن، وأين تجري؟'],
      verdicts: () => [{ v: 'map' }],
      lede: (D, F) => { const t = D.themes, named = t.themes.filter(x => x.named).length; return [
        `A map of ${F.n(t.k)} themes, found from the words alone. ${F.n(named)} of them come back every time the method is rerun from a different start, and are named here; the other ${F.n(t.k - named)} are less stable and are shown without a name. Pick a theme to light its verses.`,
        `خريطةٌ لـ${F.n(t.k)} موضوعًا استُخرجت من الألفاظ وحدها. ${F.n(named)} منها تعود في كل مرةٍ يُعاد فيها تشغيل الطريقة من بدايةٍ مختلفة، وقد سمّيناها هنا، ${t.k - named === 2 ? 'والاثنان الباقيان أقل ثباتًا فعرضناهما' : 'والباقية (' + F.n(t.k - named) + ') أقل ثباتًا فعرضناها'} بلا اسم. اختر موضوعًا لتضيء آياته.`]; },
      metrics: (D, F) => { const t = D.themes, named = t.themes.filter(x => x.named); return [
        { v: F.n(t.k), k: ['themes', 'موضوعًا'] },
        { v: F.n(named.length), k: ['stable enough to name', 'ثابتة بما يكفي لتسميتها'] },
        { v: F.pc(Math.max(...named.map(x => x.share))), k: ['of verses in the largest theme', 'من الآيات في أكبرها'] }]; },
      simple: {
        asked: ['Without telling the computer what the themes are, can it find the Quran\'s recurring subjects from which words come together in the same verses, and show where each one runs?',
          'دون أن نخبر الحاسوب بالموضوعات، هل يستطيع أن يجد موضوعات القرآن المتكررة من الألفاظ التي تجتمع في الآيات نفسها، وأن يبيّن أين يجري كلٌّ منها؟'],
        how: ['A method called [[nmf|NMF]] looked at all 6,236 verses and found 12 groups of words that tend to appear together. Each verse is then a mix of the groups, and we colour it by its largest. We reran the method five times from random starts and kept a name only for the themes that came back each time.',
          'نظرت طريقةٌ اسمها [[nmf|NMF]] في الآيات الـ٦٬٢٣٦ كلها ووجدت ١٢ مجموعةً من الألفاظ تميل إلى الاجتماع. فتصير كل آيةٍ مزيجًا من المجموعات، ونلوّنها بأكبرها. وأعدنا تشغيل الطريقة خمس مراتٍ من بداياتٍ عشوائية، ولم نُبقِ اسمًا إلا للموضوعات التي عادت في كل مرة.'],
        found: ['The ten stable themes: stories and dialogue; the Lord\'s mercy and praise; believers, disbelievers and their reward; God, His Messenger and obedience; what each soul does; the Book and its signs; the Day of Judgement; how past nations ended; the creation of the heavens and the earth; and denying the messengers and the signs.',
          'الموضوعات العشرة الثابتة: القصص والحوار؛ والربّ ورحمته وحمده؛ والمؤمنون والكافرون وجزاؤهم؛ والله ورسوله والطاعة؛ وما تعمله كل نفس؛ والكتاب وآياته؛ ويوم القيامة؛ وعاقبة الأمم السابقة؛ وخلق السماوات والأرض؛ وتكذيب الرسل والآيات.'],
        means: ['It is a map, not a test: the themes summarize patterns of words, and the names are our reading of each theme\'s words, which are shown beside them so you can judge. Use it to see where subjects gather and how the surahs mix them.',
          'هذه خريطةٌ لا اختبار: فالموضوعات تلخيصٌ لأنماط الألفاظ، والأسماء قراءتنا لألفاظ كل موضوع، وهي معروضةٌ بجانبها لتحكم بنفسك. استعملها لترى أين تجتمع الموضوعات وكيف تمزجها السور.'],
      },
      sci: {
        purpose: ['A descriptive topic map, with its settings fixed in the pre-registration.', 'خريطةٌ وصفية للموضوعات، إعداداتها محددةٌ في التسجيل المسبق.'],
        data: ['The verse × lemma TF-IDF matrix (content lemmas, `min_df = 2`, sublinear tf, unit rows), 6,236 verses.', 'مصفوفة TF-IDF للآيات × المداخل (مداخل كلمات المضمون، `min_df = 2`، تكرارٌ لوغاريتمي، صفوفٌ مطبّعة)، ٦٬٢٣٦ آية.'],
        method: ['NMF with 12 components (`init = nndsvda`, `random_state = 0`, `max_iter = 800`, Frobenius loss). A verse\'s theme is the largest weight in its row of W, if above zero. Stability: the mean best-match cosine between the rows of H and those of 5 refits with `init = random`, seeds 1–5 (deviation 1: nndsvda is deterministic, so refits with it would be identical); a theme is named if it is at least 0.8.',
          'NMF بـ١٢ مكوّنًا (`init = nndsvda`، `random_state = 0`، `max_iter = 800`، خسارة فروبينيوس). موضوع الآية أكبر وزنٍ في صفّها من W إن كان فوق الصفر. الثبات: متوسط أعلى تشابه جيب تمامٍ بين صفوف H وصفوف ٥ إعادات بـ`init = random` والبذور ١–٥ (الانحراف ١: nndsvda حتمية، فإعاداتها متطابقة)، ويُسمّى الموضوع إذا بلغ ٠٫٨.'],
        result: (D, F) => { const t = D.themes, none = (t.perVerse || []).filter(x => x < 0).length; return [
          `Stability by theme: ${t.themes.map(x => F.d(x.stability, 2)).join(', ')}; ${F.n(t.themes.filter(x => x.named).length)} of ${F.n(t.k)} reach 0.8. Shares of verses: ${t.themes.map(x => F.pc(x.share, 1)).join(', ')}; ${F.n(none)} verses have no theme (all weights zero).`,
          `الثبات لكل موضوع: ${t.themes.map(x => F.d(x.stability, 2)).join('، ')}، ويبلغ ٠٫٨ منها ${F.n(t.themes.filter(x => x.named).length)} من ${F.n(t.k)}. وحصص الآيات: ${t.themes.map(x => F.pc(x.share, 1)).join('، ')}، و${F.n(none)} آيةً بلا موضوع (أوزانها كلها صفر).`]; },
        limits: ['The number of themes (12) was fixed in advance, not chosen as the «best»; another number would split or merge themes. A bag of lemmas ignores word order and negation. The names are interpretations.',
          'عدد الموضوعات (١٢) محدَّدٌ مسبقًا لا مختارٌ على أنه «الأفضل»، وعددٌ آخر كان سيقسم الموضوعات أو يدمجها. وحقيبة المداخل تتجاهل ترتيب الكلمات والنفي. والأسماء تفسيرات.'],
      },
    },

    // ---------------------------------------------------------------- 6
    'd-companions': {
      n: 6, short: ['Word companions', 'الكلمات المتصاحبة'], map: true,
      card: (D, F) => [`${F.n(D.companions.significant)} pairs of words that share verses far more often than chance.`, `${F.n(D.companions.significant)} زوجًا من الكلمات يجتمع في الآيات أكثر بكثيرٍ مما تقتضيه المصادفة.`],
      q: ['Which words travel together?', 'أيّ الكلمات تتصاحب في القرآن؟'],
      verdicts: () => [{ v: 'map' }],
      lede: (D, F) => { const c = D.companions; return [
        `Of the ${F.n(c.pairsTested)} possible pairs among the ${F.n(c.lemmas)} commonest words, ${F.n(c.significant)} share verses far more often than chance allows. Pick a word to see its companions, and a companion to follow the trail.`,
        `من بين ${F.n(c.pairsTested)} زوجًا ممكنًا بين أكثر الكلمات ورودًا (${F.n(c.lemmas)} كلمة) يجتمع ${F.n(c.significant)} زوجًا في الآيات أكثر بكثيرٍ مما تسمح به المصادفة. اختر كلمةً لترى صاحباتها، وصاحبةً لتتبّع الأثر.`]; },
      metrics: (D, F) => { const c = D.companions; return [
        { v: F.n(c.significant), k: ['pairs that pass', 'زوجًا يجتاز الاختبار'] },
        { v: F.n(c.pairsTested), k: ['pairs tested', 'زوجًا مختبَرًا'] },
        { v: F.n(c.lemmas), k: ['words, each in at least 20 verses', 'كلمةً، لكلٍّ منها ٢٠ آيةً فأكثر'] }]; },
      simple: {
        asked: ['Some words keep company: prayer and zakat, night and day, the heavens and the earth. We asked which pairs of words share verses more often than chance, across the Quran\'s commonest words.',
          'بعض الكلمات تتصاحب: الصلاة والزكاة، والليل والنهار، والسماوات والأرض. فسألنا: أيّ أزواج الكلمات تجتمع في الآيات أكثر مما تقتضيه المصادفة، بين أكثر كلمات القرآن ورودًا؟'],
        how: (D, F) => { const c = D.companions; return [
          `For every pair of the ${F.n(c.lemmas)} words found in at least 20 verses, we counted the verses that have both, and asked how surprising that count would be if the words were scattered at random (a Fisher test), allowing for the ${F.n(c.pairsTested)} pairs tested ([[multiple|Benjamini–Hochberg]] at 1%). A pair\'s strength is its [[pmi|PMI]]: how many times more often than chance the two meet.`,
          `لكل زوجٍ من الكلمات الـ${F.n(c.lemmas)} التي ترد في ٢٠ آيةً فأكثر عددنا الآيات التي تجمعهما، وسألنا: كم يكون هذا العدد مفاجئًا لو تبعثرت الكلمتان عشوائيًّا؟ (اختبار فيشر)، مع احتساب الأزواج الـ${F.n(c.pairsTested)} المختبَرة ([[multiple|بنجاميني–هوخبرغ]] عند ١٪). وقوة الزوج [[pmi|PMI]]: كم مرةً يلتقي الزوج أكثر من المصادفة.`]; },
        found: ['The classic pairs come out on top: صلاة with زكاة (26 verses, about 65 times chance), ليل with نهار (42 verses, about 70 times), شمس with قمر (18, about 135 times), نور with ظلمة (13, about 117 times), حياة with دنيا (65, about 50 times), مال with ولد (16, about 27 times).',
          'تتصدّر الأزواج المعروفة: الصلاة مع الزكاة (٢٦ آية، نحو ٦٥ ضعف المصادفة)، والليل مع النهار (٤٢ آية، نحو ٧٠ ضعفًا)، والشمس مع القمر (١٨، نحو ١٣٥ ضعفًا)، والنور مع الظلمة (١٣، نحو ١١٧ ضعفًا)، والحياة مع الدنيا (٦٥، نحو ٥٠ ضعفًا)، والمال مع الولد (١٦، نحو ٢٧ ضعفًا).'],
        means: ['These are the Quran\'s fixed partnerships of vocabulary: pairs a reader half-expects, now with a measure of how tight each one is, and many less obvious ones to explore. It is a map, not a claim: strength here means sharing verses, not sharing meaning.',
          'هذه شراكات المعجم الثابتة في القرآن: أزواجٌ يتوقعها القارئ بعض التوقع، ومعها الآن مقياسٌ لمدى تلازم كلٍّ منها، وأزواجٌ أخرى أخفى تنتظر من يستكشفها. وهي خريطةٌ لا دعوى: فالقوة هنا اجتماعٌ في الآيات لا اشتراكٌ في المعنى.'],
      },
      sci: {
        purpose: ['A descriptive co-occurrence map with a significance filter, as pre-registered.', 'خريطةٌ وصفية للتلازم مع مرشّح دلالة، كما سُجّلت مسبقًا.'],
        data: (D, F) => { const c = D.companions; return [
          `Content lemmas with a root, in at least ${F.n(c.minVerses)} verses: ${F.n(c.lemmas)}. Pairs with different roots: ${F.n(c.pairsTested)}.`,
          `مداخل كلمات المضمون ذات الجذر التي ترد في ${F.n(c.minVerses)} آيةً فأكثر: ${F.n(c.lemmas)}. والأزواج المختلفة الجذر: ${F.n(c.pairsTested)}.`]; },
        method: ['Verse co-occurrence count c; the one-sided hypergeometric (Fisher) test against independence, given each word\'s number of verses; Benjamini–Hochberg at q = 0.01, and c ≥ 3. `PMI = log₂(c · N / (n_a · n_b))`, N = 6,236.',
          'عدد الآيات المشتركة c؛ واختبار فوق الهندسي (فيشر) من طرفٍ واحد ضد الاستقلال، بمعلومية عدد آيات كل كلمة؛ وبنجاميني–هوخبرغ عند `q = 0.01` مع `c ≥ 3`. و`PMI = log₂(c · N / (n_a · n_b))` حيث `N = 6,236`.'],
        result: (D, F) => { const c = D.companions; return [`${F.n(c.significant)} of ${F.n(c.pairsTested)} pairs pass.`, `يجتاز ${F.n(c.significant)} من ${F.n(c.pairsTested)} زوجًا.`]; },
        limits: ['Sharing a verse ignores distance and order. Set phrases («those who believe and do good deeds») produce several pairs at once. Verses are not independent (refrains, neighbouring verses), so the p-values are approximate.',
          'الاجتماع في آيةٍ يتجاهل المسافة والترتيب. والعبارات الثابتة («الذين آمنوا وعملوا الصالحات») تنتج أزواجًا عدةً دفعةً واحدة. والآيات ليست مستقلة (اللوازم، والآيات المتجاورة)، فالقيم الاحتمالية تقريبية.'],
      },
    },

    // ---------------------------------------------------------------- 7
    'd-letters': {
      n: 7, short: ['Opening letters', 'الحروف المقطعة'],
      card: ['(a) No: the letters are not, as a rule, more common in their surahs. (b) Yes: surahs that share an opening share vocabulary.', '(أ) لا: الحروف المقطعة لا تكثر في سورها قاعدةً عامة. (ب) نعم: السور المشتركة في الفاتحة تشترك في معجمها.'],
      q: ['Do the opening letters mark anything we can measure?', 'هل تدلّ الحروف المقطعة على شيءٍ يمكن قياسه؟'],
      verdicts: D => [{ v: vkey(D.letters.verdict), t: ['a', 'أ'] }, { v: vkey(D.families.verdict), t: ['b', 'ب'] }],
      lede: (D, F) => [
        `Two tests, two answers. (a) A surah's opening letters are not, as a rule, more common inside it (p = ${F.p(D.letters.p)}); the famous cases, like ق in Surah Qaf, are real but exceptions. (b) Surahs that share an opening do share vocabulary more than matched surahs (p = ${F.p(D.families.p)}), though partly because they sit side by side.`,
        `اختباران وجوابان. (أ) حروف السورة المقطعة ليست في الغالب أكثر ورودًا فيها (القيمة الاحتمالية ${F.p(D.letters.p)})، والحالات المشهورة مثل القاف في سورة ق حقيقية لكنها استثناء. (ب) السور التي تشترك في فاتحتها تشترك فعلًا في معجمها أكثر من سورٍ مماثلة لها (القيمة الاحتمالية ${F.p(D.families.p)})، وإن كان ذلك يعود جزئيًّا إلى تجاورها.`],
      metrics: (D, F) => [
        { v: F.n(Math.round(D.letters.meanPct * 100)), k: ['(a) average rank of the letters, out of 100 (50 = typical)', '(أ) متوسط رتبة الحروف من ١٠٠ (٥٠ = المعتاد)'] },
        { v: F.p(D.letters.p), k: ['(a) p-value', '(أ) القيمة الاحتمالية'] },
        { v: F.p(D.families.p), k: ['(b) p-value', '(ب) القيمة الاحتمالية'] }],
      simple: {
        asked: ['Twenty-nine surahs open with separate letters, like الم, حم or ق. Two ideas are often heard: that a surah\'s opening letters are unusually common inside it (ق in Surah Qaf, ص in Surah Sad), and that surahs sharing an opening form a family with shared themes.',
          'تُفتتح تسعٌ وعشرون سورةً بحروفٍ مقطعة، مثل «الم» و«حم» و«ق». ويُسمع كثيرًا قولان: أن حروف السورة المقطعة تكثر فيها على غير العادة (القاف في سورة ق، والصاد في سورة ص)، وأن السور التي تشترك في فاتحتها أسرةٌ تجمعها موضوعاتٌ مشتركة.'],
        how: ['(a) For each lettered surah and each of its opening letters, we ranked the letter\'s share in that surah among all 114 surahs (a [[percentile]]: 50 is typical), averaged over all 78 cases, and compared with 10,000 random reassignments of the letter sets to surahs. (b) For the four families (الم, الر, حم, طسم), we measured how alike their surahs are in words, against 10,000 random families of surahs matched for Meccan or Medinan and for length.',
          '(أ) لكل سورةٍ ذات حروفٍ ولكل حرفٍ من حروفها رتّبنا نصيب الحرف فيها بين السور الـ١١٤ كلها ([[percentile|المئين]]: ٥٠ هو المعتاد)، وأخذنا المتوسط على الحالات الـ٧٨، وقارنّاه بـ١٠٬٠٠٠ توزيعٍ عشوائي لمجموعات الحروف على السور. (ب) للأسر الأربع (الم، الر، حم، طسم) قسنا تشابه سورها في الألفاظ، مقابل ١٠٬٠٠٠ أسرةٍ عشوائية من سورٍ مماثلةٍ في المكي والمدني وفي الطول.'],
        found: (D, F) => { const L = D.letters, fz = D.families.families, c = D.families.consecutive, pk = (s, l) => { const x = L.perCase.find(r => r.s === s && r.letter === l); return x ? F.n(Math.round(x.pct * 100)) : '–'; }; return [
          `(a) The average rank is ${F.n(Math.round(L.meanPct * 100))}, against 50 for chance, and random reassignments did as well ${F.pc(L.p)} of the time: it does not pass. ق in Qaf (${pk(50, 'ق')}), ن in al-Qalam (${pk(68, 'ن')}) and ص in Sad (${pk(38, 'ص')}) rank high, but many others rank low: ر sits below the middle in four of the six surahs whose opening has it. (b) The families are more alike than matched random surahs, most of all حم (z = ${F.d(fz['حم'].z, 1)}) and الم (${F.d(fz['الم'].z, 1)}). But حم and طسم are runs of neighbouring surahs, and neighbours are alike anyway: ${F.n(c['حم'].rank - 1)} of the ${F.n(c['حم'].of)} runs of seven neighbouring surahs are more alike than the حم run.`,
          `(أ) متوسط الرتبة ${F.n(Math.round(L.meanPct * 100))} مقابل ٥٠ للمصادفة، وبلغت التوزيعات العشوائية ذلك في ${F.pc(L.p)} من المرات: فلا يجتاز الاختبار. القاف في ق (${pk(50, 'ق')})، والنون في القلم (${pk(68, 'ن')})، والصاد في ص (${pk(38, 'ص')}) رتبها عالية، لكن كثيرًا غيرها رتبها منخفضة: فالراء دون الوسط في أربعٍ من السور الست التي في فاتحتها راء. (ب) الأسر أشدّ تشابهًا من سورٍ عشوائيةٍ مماثلة، وأكثرها «حم» (`+'`z = '+F.dl(fz['حم'].z, 1)+'`'+`) و«الم» (${F.d(fz['الم'].z, 1)}). لكن «حم» و«طسم» سلسلتان من سورٍ متجاورة، والمتجاورات متشابهةٌ أصلًا: فمن بين ${F.n(c['حم'].of)} سلسلةً من سبع سورٍ متجاورة، ${F.n(c['حم'].rank - 1)} سلسلةً أشدّ تشابهًا من سلسلة «حم».`]; },
        means: ['The popular claim about letter counts does not hold as a pattern across the 29 surahs; a few striking cases are what one would expect by chance among 78. The family idea has support in the vocabulary, but we cannot separate it from the mushaf\'s habit of placing related surahs together.',
          'فالقول الشائع عن كثرة الحروف لا يثبت نمطًا عامًّا في السور التسع والعشرين، وبضع حالاتٍ لافتة هي ما يُتوقع مصادفةً بين ٧٨ حالة. أما فكرة الأسر فلها سندٌ في المعجم، لكنّا لا نستطيع فصلها عن عادة المصحف في وضع السور المتقاربة متجاورة.'],
      },
      sci: {
        purpose: ['Two pre-registered tests: (a) over-representation of the opening letters in their own surahs; (b) lexical cohesion of the letter families.', 'اختباران مسجّلان مسبقًا: (أ) زيادة ورود الحروف المقطعة في سورها؛ (ب) التماسك اللفظي لأسر الحروف.'],
        data: ['Openings tagged INL in the corpus (29 surahs). Letters counted on the normalized text, the opening letters themselves left out. For (b), surah-level TF-IDF vectors of lemmas (the classifier\'s).',
          'الفواتح الموسومة INL في المدونة (٢٩ سورة). تُعَدّ الحروف في النص المطبَّع دون الحروف المقطعة نفسها. وفي (ب) متجهات TF-IDF لمداخل كل سورة (متجهات المصنِّف).'],
        method: ['(a) The percentile (mid-rank) of each letter\'s share among the 114 surahs; mean over 78 (surah, letter) cases; null: the 29 letter sets reassigned to 29 surahs drawn without replacement, 10,000 times, seed 17. (b) Each family\'s mean pairwise cosine as a z-score against draws matched on place and word-count quartile; statistic: the mean z of the four families, against 10,000 simultaneous draws, seed 19. Secondary: the family\'s rank among all runs of the same number of consecutive surahs.',
          '(أ) مئين نصيب كل حرفٍ (بالرتبة الوسطى) بين السور الـ١١٤، ومتوسطه على ٧٨ حالة (سورة، حرف)؛ والتوزيع الصفري: إعادة توزيع مجموعات الحروف الـ٢٩ على ٢٩ سورةً تُسحب دون إرجاع، ١٠٬٠٠٠ مرة، البذرة ١٧. (ب) متوسط جيب التمام بين أزواج كل أسرة درجةً معيارية مقابل سحوباتٍ مماثلة في المكان وربيع عدد الكلمات؛ والإحصاءة متوسط درجات الأسر الأربع مقابل ١٠٬٠٠٠ سحبٍ متزامن، البذرة ١٩. وثانويًّا: رتبة الأسرة بين كل سلاسل السور المتتالية بالطول نفسه.'],
        result: (D, F) => { const L = D.letters, Fm = D.families, fz = Fm.families; return [
          `(a) Mean percentile ${F.d(L.meanPct, 3)} (null ${F.d(L.null.mean, 3)}, SD ${F.d(L.null.sd, 3)}), p = ${F.p(L.p)}: does not hold. (b) z: ${Object.keys(fz).map(k => k + ' ' + F.d(fz[k].z, 2)).join(', ')}; mean ${F.d(Fm.meanZ, 2)}, p = ${F.p(Fm.p)}: holds. Consecutive runs: حم ${F.n(Fm.consecutive['حم'].rank)} of ${F.n(Fm.consecutive['حم'].of)}, طسم ${F.n(Fm.consecutive['طسم'].rank)} of ${F.n(Fm.consecutive['طسم'].of)}.`,
          `(أ) متوسط المئين ${F.d(L.meanPct, 3)} (الصفري ${F.d(L.null.mean, 3)}، الانحراف ${F.d(L.null.sd, 3)})، والقيمة الاحتمالية ${F.p(L.p)}: لم تثبت. (ب) الدرجات المعيارية: ${Object.keys(fz).map(k => k + ' ' + F.d(fz[k].z, 2)).join('، ')}، ومتوسطها ${F.d(Fm.meanZ, 2)}، والقيمة الاحتمالية ${F.p(Fm.p)}: ثبتت. وبين السلاسل المتتالية: «حم» ${F.n(Fm.consecutive['حم'].rank)} من ${F.n(Fm.consecutive['حم'].of)}، و«طسم» ${F.n(Fm.consecutive['طسم'].rank)} من ${F.n(Fm.consecutive['طسم'].of)}.`]; },
        limits: ['(a) pools very different letters, and a letter\'s share depends on vocabulary (م is common everywhere). (b)\'s matching does not control for being neighbours in the mushaf. Family membership (طس for surah 27) follows the pre-registration.',
          '(أ) يجمع حروفًا مختلفةً جدًّا، ونصيب الحرف يتبع المعجم (فالميم كثيرةٌ في كل مكان). ومماثلة (ب) لا تضبط التجاور في المصحف. وعضوية الأسر (طس للسورة ٢٧) كما في التسجيل المسبق.'],
      },
    },

    // ---------------------------------------------------------------- 8
    'd-repeats': {
      n: 8, short: ['Near-repeats', 'المتشابه اللفظي'], map: true,
      card: (D, F) => [`${F.n(D.repeats.nRefrains)} verses repeated word for word, and ${F.n(D.repeats.nPairs)} near-repeats with their differences marked.`, `${F.n(D.repeats.nRefrains)} آيةً تتكرر بلفظها، و${F.n(D.repeats.nPairs)} زوجًا متشابهًا مع تعليم ما يختلف.`],
      q: ['Which verses nearly repeat, and what changes between them?', 'ما الآيات التي تكاد تتكرر، وما الذي يتغيّر بينها؟'],
      verdicts: () => [{ v: 'map' }],
      lede: (D, F) => { const r = D.repeats; return [
        `${F.n(r.nRefrains)} verses are repeated word for word, filling ${F.n(r.refrainVerses)} places in all, and ${F.n(r.nPairs)} pairs of verses are alike in at least 80% of their words. Each pair is listed with the words that differ.`,
        `${F.n(r.nRefrains)} آيةً تتكرر بلفظها وتشغل ${F.n(r.refrainVerses)} موضعًا في المجموع، و${F.n(r.nPairs)} زوجًا من الآيات تتشابه في ٨٠٪ من ألفاظها فأكثر. وكل زوجٍ معروضٌ مع الكلمات التي تختلف.`]; },
      metrics: (D, F) => { const r = D.repeats; return [
        { v: F.n(r.nRefrains), k: ['verses repeated word for word', 'آيةً تتكرر بلفظها'] },
        { v: F.n(r.nPairs), k: ['near-repeat pairs', 'زوجًا متشابهًا'] },
        { v: F.n(r.refrains[0].n), k: ['times the most repeated verse comes', 'مرةً ترد أكثر الآيات تكرارًا'] }]; },
      simple: {
        asked: ['Some verses come back word for word, and some come back almost the same, with a word or two changed. Classical scholars wrote whole books on why each small difference fits its place (al-mutashābih al-lafẓī). We asked the computer to find every such pair.',
          'تعود بعض الآيات بلفظها، ويعود بعضها شبه مطابق مع تغيّر كلمةٍ أو كلمتين. وألّف العلماء قديمًا كتبًا كاملةً في علّة كل فرقٍ صغيرٍ في موضعه (المتشابه اللفظي). فطلبنا من الحاسوب أن يجد كل زوجٍ من هذا النوع.'],
        how: ['We compared every two verses of at least four words by the sequence of their dictionary forms ([[lemma|lemmas]]) and kept the pairs alike by 80% or more. Verses repeated exactly are grouped as refrains.',
          'قارنّا كل آيتين من أربع كلماتٍ فأكثر بتسلسل مداخلهما المعجمية ([[lemma|المداخل]])، وأبقينا الأزواج التي يبلغ تشابهها ٨٠٪ فأكثر. والآيات المكررة بلفظها مجموعةٌ لوازمَ.'],
        found: (D, F) => { const r = D.repeats; return [
          `The most repeated verse is «فبأي آلاء ربكما تكذبان», ${F.n(r.refrains[0].n)} times in ar-Rahman. Ash-Shu'ara repeats «وإن ربك لهو العزيز الرحيم» ${F.n(r.refrains[1].n)} times, and other lines five or six times: the refrains of its prophet stories. Of the ${F.n(r.nPairs)} near pairs, many differ by a single word.`,
          `أكثر الآيات تكرارًا «فبأي آلاء ربكما تكذبان»، ${F.n(r.refrains[0].n)} مرةً في سورة الرحمن. وتكرر الشعراء «وإن ربك لهو العزيز الرحيم» ${F.n(r.refrains[1].n)} مرات، وآياتٍ أخرى خمس مراتٍ أو ستًّا: لوازم قصص الأنبياء فيها. ومن الأزواج المتشابهة الـ${F.n(r.nPairs)} يختلف كثيرٌ منها في كلمةٍ واحدة.`]; },
        means: ['A finding aid for a classical field: every near-repeat in one place, with the differing words marked, for a reader to study why each difference fits. It makes no claim by itself.',
          'أداةٌ مساعدةٌ لعلمٍ قديم: كل المتشابهات في مكانٍ واحد، والكلمات المختلفة معلَّمة، ليدرس القارئ علّة كل فرق. ولا تدّعي بذاتها شيئًا.'],
      },
      sci: {
        purpose: ['A descriptive list (pre-registered as a map, not a test).', 'قائمةٌ وصفية (سُجّلت مسبقًا خريطةً لا اختبارًا).'],
        data: ['Verses of at least 4 words; each word as its lemma, or its normalized form when it has no lemma.', 'الآيات ذات الكلمات الأربع فأكثر، وكل كلمةٍ بمدخلها المعجمي، أو بصورتها المطبَّعة إن لم يكن لها مدخل.'],
        method: ['`difflib.SequenceMatcher` ratio `2M / (|a| + |b|)` on the lemma sequences, kept at ≥ 0.8; candidates pre-filtered by a length ratio of at least 2/3 and a bound from shared lemmas. The differences are shown on the normalized written words. Verses with identical normalized text are refrains.',
          'نسبة `difflib.SequenceMatcher` أي `2M / (|a| + |b|)` على تسلسل المداخل، ويُبقى ما بلغ ٠٫٨؛ مع ترشيحٍ مسبق بنسبة طولٍ لا تقل عن الثلثين وحدٍّ من المداخل المشتركة. وتُعرض الفروق على الكلمات المكتوبة بعد التطبيع. والآيات المتطابقة نصًّا بعد التطبيع لوازم.'],
        result: (D, F) => { const r = D.repeats, same = r.pairs.filter(p => p.ratio === 1).length; return [
          `${F.n(r.nRefrains)} refrains (${F.n(r.refrainVerses)} verses); ${F.n(r.nPairs)} near pairs, ${F.n(same)} of them with identical lemma sequences that differ only in written form (a suffix, a particle joined on).`,
          `${F.n(r.nRefrains)} لازمة (${F.n(r.refrainVerses)} آية)؛ و${F.n(r.nPairs)} زوجًا متشابهًا، منها ${F.n(same)} تتطابق مداخلها وتختلف في الرسم وحده (لاحقةٌ أو حرفٌ متصل).`]; },
        limits: ['Lemma matching misses synonyms and paraphrase; the 80% cut-off is a choice; verses under four words are left out.', 'مطابقة المداخل تفوتها المترادفات وإعادة الصياغة، وحدّ ٨٠٪ اختيار، والآيات دون أربع كلماتٍ متروكة.'],
      },
    },

    // ---------------------------------------------------------------- 9
    'd-chrono': {
      n: 9, short: ['Revelation order', 'ترتيب النزول'],
      card: ['Yes: later surahs have longer verses, as scholars have long observed.', 'نعم: الآيات أطول في السور المتأخرة، كما لاحظ العلماء منذ زمن.'],
      q: ['Does the style change over the order of revelation?', 'هل يتغيّر الأسلوب مع ترتيب النزول؟'],
      verdicts: D => [{ v: vkey(D.chronology.verdict) }],
      lede: (D, F) => { const c = D.chronology; return [
        `Yes: in the traditional order of revelation, later surahs have longer verses (rank correlation ${F.d(c.rho, 2)}; no shuffled order of 10,000 came close), and it holds within the Meccan surahs alone (${F.d(c.rhoMeccan, 2)}). This confirms what scholars have long observed, and shows the tools find what is known.`,
        `نعم: في ترتيب النزول المأثور تطول الآيات في السور المتأخرة (معامل ارتباط الرتب ${F.d(c.rho, 2)}، ولم يقترب منه أيٌّ من ١٠٬٠٠٠ ترتيبٍ مخلوط)، ويثبت ذلك في السور المكية وحدها (${F.d(c.rhoMeccan, 2)}). وهذا يؤكد ما لاحظه العلماء منذ زمن، ويبيّن أن الأدوات تجد ما هو معروف.`]; },
      metrics: (D, F) => { const c = D.chronology; return [
        { v: F.d(c.rho, 2), k: ['rank correlation, all surahs', 'ارتباط الرتب، كل السور'] },
        { v: F.d(c.rhoMeccan, 2), k: ['Meccan surahs alone', 'السور المكية وحدها'] },
        { v: F.p(c.p), k: ['p-value', 'القيمة الاحتمالية'] }]; },
      simple: {
        asked: ['Muslim tradition has kept an order in which the surahs were revealed, and scholars have long noted that early surahs have short, rhythmic verses and later ones longer verses. We checked this with the traditional order printed in the standard Egyptian edition of the mushaf.',
          'حفظت الرواية الإسلامية ترتيبًا لنزول السور، ولاحظ العلماء منذ زمنٍ أن السور الأولى قصيرة الآيات موقَّعة، وأن اللاحقة أطول آيات. فتحققنا من ذلك بترتيب النزول المأثور المطبوع في مصحف القاهرة المعياري.'],
        how: ['We ranked the surahs by that order and asked whether their average verse length rises with it ([[spearman|rank correlation]]), comparing with 10,000 shuffled orders; then again within the Meccan surahs alone.',
          'رتّبنا السور بهذا الترتيب وسألنا: هل يرتفع متوسط طول آياتها معه؟ ([[spearman|ارتباط الرتب]])، وقارنّا بـ١٠٬٠٠٠ ترتيبٍ مخلوط، ثم كررنا ذلك في السور المكية وحدها.'],
        found: (D, F) => { const c = D.chronology, e = c.phases[0]; return [
          `The correlation is ${F.d(c.rho, 2)} (0 is no link, 1 a perfect one), far beyond any shuffled order; among the Meccan surahs alone it is ${F.d(c.rhoMeccan, 2)}. Also, the earliest period has the most words of its own: ${F.pc(e.share)} of the different words it uses appear in no later period.`,
          `معامل الارتباط ${F.d(c.rho, 2)} (الصفر لا علاقة، والواحد علاقةٌ تامة)، وهو أبعد بكثيرٍ من أي ترتيبٍ مخلوط، وفي السور المكية وحدها ${F.d(c.rhoMeccan, 2)}. كما أن المرحلة الأولى أكثر المراحل ألفاظًا خاصة بها: ${F.pc(e.share)} من الكلمات المختلفة التي تستعملها لا ترد في أي مرحلةٍ بعدها.`]; },
        means: ['Verse length rises with the traditional order: a known result, found again. It is also a check on the tools: a method that finds what is well established earns more trust when it finds something new. On its own it cannot date a surah.',
          'فطول الآيات يرتفع مع الترتيب المأثور: نتيجةٌ معروفة وُجدت من جديد. وهو أيضًا فحصٌ للأدوات: فالمنهج الذي يجد الثابت المعروف أجدر بالثقة حين يجد جديدًا. ولا يستطيع وحده أن يؤرخ سورة.'],
      },
      sci: {
        purpose: ['A pre-registered test of a stylistic trend (mean verse length) over the traditional revelation order.', 'اختبارٌ مسجّلٌ مسبقًا لاتجاهٍ أسلوبي (متوسط طول الآية) عبر ترتيب النزول المأثور.'],
        data: ['The traditional order of the Egyptian standard edition (the table in scripts/enrich_quran_corpus.py), checked to be a permutation of 1–114 whose ranks 87–114 are exactly the 28 Medinan surahs. Mean verse length = words / verses.',
          'ترتيب النزول في مصحف القاهرة المعياري (الجدول في scripts/enrich_quran_corpus.py)، وقد تُحقِّق من أنه تبديلٌ للأعداد ١–١١٤ وأن رتبه ٨٧–١١٤ هي السور المدنية الـ٢٨ بعينها. ومتوسط طول الآية = الكلمات ÷ الآيات.'],
        method: ['Spearman\'s ρ between rank and mean verse length; p from 10,000 permutations (seed 23), two-sided; again for the 86 Meccan surahs.', 'معامل سبيرمان ρ بين الرتبة ومتوسط طول الآية، والقيمة الاحتمالية من ١٠٬٠٠٠ تبديل (البذرة ٢٣) من طرفين، ثم للسور المكية الـ٨٦.'],
        result: (D, F) => { const c = D.chronology; return [
          `ρ = ${F.d(c.rho, 3)}, p = ${F.p(c.p)}; Meccan only: ρ = ${F.d(c.rhoMeccan, 3)}, p = ${F.p(c.pMeccan)}. Exploratory, share of each period's lemmas used in no other period: ${c.phases.map(ph => ph.name + ' ' + F.pc(ph.share, 1)).join(', ')}.`,
          '`ρ = '+F.dl(c.rho, 3)+'`'+` والقيمة الاحتمالية ${F.p(c.p)}؛ والمكي وحده: `+'`ρ = '+F.dl(c.rhoMeccan, 3)+'`'+` والقيمة الاحتمالية ${F.p(c.pMeccan)}. واستكشافيًّا، حصة مداخل كل مرحلةٍ التي لا ترد في غيرها: ${c.phases.map(ph => F.pc(ph.share, 1)).join('، ')}.`]; },
        limits: ['The traditional order is itself partly built on style and reports, so agreement with it is not independent confirmation, and it dates a surah by its opening verses. Verse length is one marker among many, and it depends on the verse count (Kufan here).',
          'الترتيب المأثور مبنيٌّ هو نفسه جزئيًّا على الأسلوب والروايات، فموافقته ليست تأكيدًا مستقلًّا، وهو يؤرخ السورة بمطلعها. وطول الآية علامةٌ واحدة من علاماتٍ كثيرة، ويتبع عدّ الآي (الكوفي هنا).'],
      },
    },
  };

  // What scholars had found or held before each study, and what the study adds. Only sources whose title, author,
  // venue and year we could confirm are listed; «we found no earlier test» means none turned up in our search.
  const KNOWN = {
    'd-endings': {
      items: [
        { t: ['al-Suyūṭī, al-Itqān fī ʿulūm al-Qurʾān, the chapter on verse endings: on 5:118, «if You forgive them» leads a reader to expect «Forgiving, Merciful», yet «Mighty, Wise» is right, since only One whom none can overrule forgives those who deserve punishment.',
            'السيوطي، الإتقان في علوم القرآن، باب الفواصل: في ٥:١١٨ يوهم «وإن تغفر لهم» أن الختام «الغفور الرحيم»، لكن «العزيز الحكيم» هو الصواب، إذ لا يغفر لمن استحق العقاب إلا من لا يُعقَّب على حكمه.'], u: 'https://shamela.ws/book/11728/1096' },
        { t: ['al-Saʿdī, al-Qawāʿid al-ḥisān, rule 19: when a verse ends with a divine name, its ruling is tied to that name.',
            'السعدي، القواعد الحسان، القاعدة ١٩: إذا خُتمت الآية باسمٍ من الأسماء الحسنى دلّ ذلك على تعلّق حكمها بذلك الاسم.'], u: 'https://shamela.ws/book/9077/48' },
        { t: ['Devin Stewart, «Divine Epithets and the Dibacchius: Clausulae and Qur\'anic Rhythm», Journal of Qur\'anic Studies 15/2 (2013): the rhythm of a verse\'s end also shapes which epithets close it.',
            'ديفن ستيوارت، «الأسماء الإلهية والتفعيلة الختامية: خواتيم الآيات وإيقاع القرآن»، مجلة الدراسات القرآنية ١٥/٢ (٢٠١٣): إيقاع خاتمة الآية يؤثر أيضًا في الأسماء التي تختمها.'], u: 'https://doi.org/10.3366/jqs.2013.0095' },
        { t: ['We found no earlier statistical test of the fit. The nearest quantitative work compares kinds of divine attributes between Meccan and Medinan surahs (Liu, Mahmoudi and Abasalizadeh, Digital Scholarship in the Humanities, 2020).',
            'لم نجد اختبارًا إحصائيًّا سابقًا لهذه الملاءمة. وأقرب عملٍ كمّي يقارن أنواع الصفات الإلهية بين السور المكية والمدنية (Liu وMahmoudi وAbasalizadeh، مجلة Digital Scholarship in the Humanities، ‏٢٠٢٠).'], u: 'https://doi.org/10.1093/llc/fqz051' },
      ],
      adds: ['A test of the classical claim against chance: it supports it, modestly. And on 5:118, the verse al-Suyūṭī discusses, the model makes exactly the first reading he warns against.',
        'اختبارٌ للقول القديم في مواجهة المصادفة: يؤيده تأييدًا متواضعًا. وفي ٥:١١٨، الآية التي يناقشها السيوطي، يقع النموذج في القراءة الأولى نفسها التي ينبّه عليها.'],
    },
    'd-rings': {
      items: [
        { t: ['Raymond Farrin, «Surat al-Baqara: A Structural Analysis», The Muslim World 100/1 (2010): a ring whose centre is the qibla passage, 2:142–152.',
            'ريموند فارين، «سورة البقرة: تحليلٌ بنيوي»، مجلة العالم الإسلامي ١٠٠/١ (٢٠١٠): بناءٌ دائري مركزه آيات القبلة ٢:١٤٢–١٥٢.'], u: 'https://www.researchgate.net/publication/230522741_Surat_al-Baqara_A_Structural_Analysis' },
        { t: ['Michel Cuypers, The Banquet (2009), on al-Māʾida, and The Composition of the Qur\'an (2015), on rhetorical analysis.',
            'ميشيل كويبرس، «المائدة» (٢٠٠٩)، و«نظم القرآن: التحليل البلاغي» (٢٠١٥).'], u: 'https://www.bloomsburycollections.com/book/the-composition-of-the-quran-rhetorical-analysis/' },
        { t: ['Critical reviews: Nicolai Sinai, «Going Round in Circles», Journal of Qur\'anic Studies 19/2 (2017); Marianna Klar compares five structural analyses of al-Baqara in the same journal, 19/1 (2017).',
            'مراجعاتٌ نقدية: نيكولاي سيناي، «الدوران في حلقات»، مجلة الدراسات القرآنية ١٩/٢ (٢٠١٧)؛ وتقارن مريانا كلار خمسة تحليلاتٍ بنيوية لسورة البقرة في المجلة نفسها ١٩/١ (٢٠١٧).'], u: 'https://doi.org/10.3366/jqs.2017.0285' },
        { t: ['We found no earlier test of a ring against a chance baseline.', 'لم نجد اختبارًا سابقًا لبناءٍ دائري في مواجهة خط أساسٍ من المصادفة.'] },
      ],
      adds: ['A first chance-based test of the simplest, word-level form of the ring. It does not hold, which leaves the ring of themes open, for a test that pairs sections by what they are about.',
        'أول اختبارٍ في مواجهة المصادفة لأبسط صور البناء الدائري، على مستوى الألفاظ. ولم يثبت، فيبقى التناظر في الموضوعات مفتوحًا لاختبارٍ يقابل بين الأقسام بمضامينها.'],
    },
    'd-rhyme': {
      items: [
        { t: ['Angelika Neuwirth, Studien zur Komposition der mekkanischen Suren (1981; 2nd ed. 2007): with other markers, a change of rhyme sets off the verse groups of Meccan surahs.',
            'أنجيليكا نويفرت، «دراساتٌ في تأليف السور المكية» (١٩٨١، ط٢ ٢٠٠٧): تغيّر الفاصلة، مع علاماتٍ أخرى، يفصل بين مجموعات الآيات في السور المكية.'], u: 'https://www.degruyterbrill.com/document/doi/10.1515/9783110920383/html' },
        { t: ['Devin Stewart, «Saj\' in the Qur\'an: Prosody and Structure», Journal of Arabic Literature 21 (1990); Marianna Klar (ed.), Structural Dividers in the Qur\'an (2021).',
            'ديفن ستيوارت، «السجع في القرآن: العروض والبنية»، مجلة الأدب العربي ٢١ (١٩٩٠)؛ ومريانا كلار (محرّرة)، «الفواصل البنيوية في القرآن» (٢٠٢١).'] },
        { t: ['We found no earlier test of whether rhyme changes coincide with changes of topic.', 'لم نجد اختبارًا سابقًا لتزامن تغيّر الفاصلة مع تغيّر الموضوع.'] },
      ],
      adds: ['Numbers for a working assumption of structural readings: a change of rhyme does tend to come with a change of subject, in Medinan surahs as well as Meccan ones.',
        'أرقامٌ لافتراضٍ تعمل به القراءات البنيوية: تغيّر الفاصلة يأتي فعلًا مع تغيّر الموضوع في الغالب، في السور المدنية كما في المكية.'],
    },
    'd-stories': {
      items: [
        { t: ['The classical books on near-repeated verses, such as al-Kirmānī\'s al-Burhān fī tawjīh mutashābih al-Qurʾān, explain the differences between parallel passages by their context.',
            'كتب المتشابه اللفظي، ككتاب الكرماني «البرهان في توجيه متشابه القرآن»، تعلّل الفروق بين المواضع المتشابهة بسياقها.'], u: 'https://archive.org/details/Burhan_tawjeeh' },
        { t: ['A. C. Smith, on the four tellings of Moses and Pharaoh\'s magicians, Journal of Qur\'anic Studies 20/1 (2018); Marianna Klar, on words of the Adam story recurring across al-Baqara, 17/2 (2015).',
            'أ. سي. سميث عن الروايات الأربع لموسى وسحرة فرعون، مجلة الدراسات القرآنية ٢٠/١ (٢٠١٨)؛ ومريانا كلار عن ألفاظ قصة آدم التي تتردد في سورة البقرة، ١٧/٢ (٢٠١٥).'], u: 'https://doi.org/10.3366/jqs.2018.0321' },
        { t: ['Andrew Bannister, An Oral-Formulaic Study of the Qur\'an (2014), compares the tellings of the story of Iblis and Adam by computer. We found no computational comparison of the Moses tellings.',
            'أندرو بانيستر، «دراسةٌ شفاهية-صيغية للقرآن» (٢٠١٤)، يقارن روايات قصة إبليس وآدم حاسوبيًّا. ولم نجد مقارنةً حاسوبية لروايات قصة موسى.'] },
      ],
      adds: ['A test across the 23 tellings of Moses and Abraham, against chance: each telling is closer in its words to its own surah.',
        'اختبارٌ على روايات موسى وإبراهيم الثلاث والعشرين في مواجهة المصادفة: كل روايةٍ أقرب في ألفاظها إلى سورتها.'],
    },
    'd-themes': {
      items: [
        { t: ['Topic models of the Quran have been built before: surahs clustered by their words (Thabet, 2005), LDA over surahs (Siddiqui, Faraz and Sattar, 2013), and BERTopic compared with LDA and NMF (Zafar and others, 2024). A survey: Bashir and others, Artificial Intelligence Review (2023).',
            'بُنيت نماذج موضوعاتٍ للقرآن من قبل: تجميع السور بألفاظها (Thabet، ‏٢٠٠٥)، وLDA على السور (Siddiqui وFaraz وSattar، ‏٢٠١٣)، ومقارنة BERTopic بـLDA وNMF (Zafar وآخرون، ٢٠٢٤). ومسحٌ لها: Bashir وآخرون، مجلة Artificial Intelligence Review ‏(٢٠٢٣).'], u: 'https://doi.org/10.1007/s10462-022-10313-2' },
      ],
      adds: ['Not a new method. It adds a check of which themes are stable, a verse-by-verse map in reading order, and names shown beside the words they come from.',
        'ليست طريقةً جديدة. وتضيف فحصًا لثبات الموضوعات، وخريطةً آيةً آيةً بترتيب القراءة، وأسماءً معروضةً بجانب الألفاظ التي أُخذت منها.'],
    },
    'd-companions': {
      items: [
        { t: ['Toshihiko Izutsu, God and Man in the Koran (1964): the Quran\'s key words form fields of related meaning. Nicolai Sinai, Key Terms of the Qur\'an (2023).',
            'توشيهيكو إيزوتسو، «الله والإنسان في القرآن» (١٩٦٤): الألفاظ المفتاحية في القرآن تؤلف حقولًا دلالية. ونيكولاي سيناي، «المصطلحات المفتاحية في القرآن» (٢٠٢٣).'] },
        { t: ['Computational collocation studies: Alrabiah and others (2014), with distributional models; Bentrcia, Zidat and Marir (2018), on the order of words in «X and Y» pairs.',
            'دراساتٌ حاسوبية في التلازم: Alrabiah وآخرون (٢٠١٤) بالنماذج التوزيعية، وBentrcia وZidat وMarir ‏(٢٠١٨) في ترتيب اللفظين في أزواج «كذا وكذا».'], u: 'https://eprints.whiterose.ac.uk/81839/' },
      ],
      adds: ['Every pair among the commonest words, with its strength and a significance filter corrected for all the pairs tested, open to explore.',
        'كل زوجٍ بين أكثر الكلمات ورودًا، بقوته ومرشّحٍ للدلالة مصحَّحٍ لكل الأزواج المختبرة، مفتوحًا للاستكشاف.'],
    },
    'd-letters': {
      items: [
        { t: ['al-Suyūṭī, in al-Itqān, reports al-Zarkashī\'s view that a surah opening with a letter is built largely on words with that letter, so ق could not stand where ن stands.',
            'ينقل السيوطي في الإتقان رأي الزركشي أن السورة المفتتحة بحرفٍ تُبنى في أكثرها على كلماتٍ فيها ذلك الحرف، فلا يصلح أن تقع القاف موضع النون.'], u: 'https://www.islamicbook.ws/qbook/alom/alitqan-006.html' },
        { t: ['Rashad Khalifa (1973) built numerical claims on the counts of these letters, for example ق 57 times in both surah 42 and surah 50; they have been rebutted (e.g., Philips, 1987).',
            'بنى رشاد خليفة (١٩٧٣) دعاوى عددية على إحصاء هذه الحروف، كورود القاف ٥٧ مرة في السورتين ٤٢ و٥٠، ورُدّت عليه (مثل فيليبس، ١٩٨٧).'] },
        { t: ['Islam Dayeh, «Al-Ḥawāmīm: Intertextuality and Coherence in Meccan Surahs», in The Qur\'an in Context (2010): the Ḥā-Mīm surahs are linked in form, set phrases and themes.',
            'إسلام دية، «الحواميم: التناص والتماسك في السور المكية»، في كتاب «القرآن في سياقه» (٢٠١٠): سور «حم» مترابطةٌ في الشكل والعبارات الثابتة والموضوعات.'], u: 'https://www.academia.edu/8297605/Al_Hawamim_Intertextuality_and_Coherence_in_Meccan_Suras' },
        { t: ['We found no earlier statistical test of the letters being over-represented in their surahs.', 'لم نجد اختبارًا إحصائيًّا سابقًا لكثرة الحروف المقطعة في سورها.'] },
      ],
      adds: ['(a) A test of the classical and popular claim across all 78 cases: it does not hold as a rule. (b) Support in the vocabulary for the Ḥā-Mīm family and its kin, with the caveat that neighbouring surahs are alike anyway.',
        '(أ) اختبارٌ للقول القديم والشائع على الحالات الـ٧٨ كلها: لا يثبت قاعدةً عامة. (ب) سندٌ من المعجم لأسرة «حم» وأخواتها، مع التنبيه إلى أن السور المتجاورة متشابهةٌ أصلًا.'],
    },
    'd-repeats': {
      items: [
        { t: ['The classical books: al-Iskāfī (d. 420/1029), Durrat al-tanzīl; al-Kirmānī (d. about 505/1111), al-Burhān fī tawjīh mutashābih al-Qurʾān; Ibn al-Zubayr al-Gharnāṭī (d. 708/1308), Milāk al-taʾwīl.',
            'الكتب القديمة: الإسكافي (ت ٤٢٠هـ)، «درة التنزيل»؛ والكرماني (ت نحو ٥٠٥هـ)، «البرهان في توجيه متشابه القرآن»؛ وابن الزبير الغرناطي (ت ٧٠٨هـ)، «ملاك التأويل».'], u: 'https://archive.org/details/Burhan_tawjeeh' },
        { t: ['Computational work: repeated text found with a suffix tree in five surahs (Oktaviani and others, 2019), and a hand-curated list of near-repeats published as open data.',
            'أعمالٌ حاسوبية: كشف النص المكرر بشجرة اللواحق في خمس سور (Oktaviani وآخرون، ٢٠١٩)، وقائمةٌ للمتشابهات أُعدّت يدويًّا ونُشرت بياناتٍ مفتوحة.'], u: 'https://github.com/Waqar144/Quran_Mutashabihat_Data' },
      ],
      adds: ['A list over the whole Quran with the differing words marked, to set beside the classical books.', 'قائمةٌ تشمل القرآن كله والكلمات المختلفة معلَّمة، توضع بجانب الكتب القديمة.'],
    },
    'd-chrono': {
      items: [
        { t: ['Nöldeke and Schwally, The History of the Qur\'an (English translation, 2013), divides the Meccan surahs into periods partly by style.',
            'نولدكه وشفالي، «تاريخ القرآن» (الترجمة الإنجليزية ٢٠١٣)، يقسّم السور المكية إلى مراحل بحسب أسلوبها في جملة ما يعتمده.'] },
        { t: ['Behnam Sadeghi, «The Chronology of the Qur\'an: A Stylometric Research Program», Arabica 58 (2011): verse length and the frequencies of common words change smoothly together. Nicolai Sinai (2017) and Raymond Farrin (2019) use mean verse length to order the surahs.',
            'بهنام صادقي، «تأريخ القرآن: برنامجٌ بحثيٌّ في قياس الأسلوب»، مجلة أرابيكا ٥٨ (٢٠١١): طول الآية وتكرارات الكلمات الشائعة تتغيّر معًا تغيّرًا متصلًا. ويستعمل نيكولاي سيناي (٢٠١٧) وريموند فارين (٢٠١٩) متوسط طول الآية لترتيب السور.'] },
        { t: ['Mahmoudi and Abbasalizadeh (Digital Scholarship in the Humanities, 2019) compare 13 proposed revelation orders and find them closely related.',
            'قارن Mahmoudi وAbbasalizadeh ‏(مجلة Digital Scholarship in the Humanities، ‏٢٠١٩) ثلاثة عشر ترتيبًا مقترحًا للنزول فوجدوها متقاربة.'], u: 'https://academic.oup.com/dsh/article-abstract/34/1/152/5068353' },
      ],
      adds: ['Nothing new, and that is its use: a known result, found again with the same tools as the other studies.', 'لا جديد فيه، وهذه فائدته: نتيجةٌ معروفة وُجدت من جديد بالأدوات نفسها التي استُعملت في الدراسات الأخرى.'],
    },
  };

  return { REPO, PREREG, COMMIT, ORDER, VERDICT, INTRO, HOW, THEMES, STUDIES, KNOWN };
})();
