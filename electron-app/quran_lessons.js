const QURAN_LESSONS = [
  // ═══════════════════════════════════════════════════════════
  // FAITH (إيمان) — 12 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 1,
    ar: 'التوحيد',
    en: 'Monotheism (Tawheed)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'الإيمان بوحدانية الله تعالى هو أساس الدين كله. لا إله إلا الله وحده لا شريك له في ربوبيته وألوهيته وأسمائه وصفاته.',
    desc_en: 'Belief in the absolute oneness of God is the foundation of the entire faith. There is no deity worthy of worship except Allah alone, without any partner in His lordship, divinity, or attributes.',
    refs: ['112:1-4', '2:163', '2:255', '21:22', '23:91', '16:51'],
    story: ''
  },
  {
    id: 2,
    ar: 'التوكل على الله',
    en: 'Trust in God (Tawakkul)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'التوكل على الله يعني الاعتماد الكامل عليه سبحانه مع الأخذ بالأسباب. من يتوكل على الله فهو حسبه.',
    desc_en: 'Placing complete reliance upon God while taking practical measures. Whoever puts their trust in God, He will be sufficient for them.',
    refs: ['65:3', '3:159', '8:2', '12:67', '14:12'],
    story: 'إبراهيم'
  },
  {
    id: 3,
    ar: 'الإيمان بالغيب',
    en: 'Belief in the Unseen',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'الإيمان بما غاب عن الحواس من أمور الآخرة والملائكة والقدر هو صفة المتقين التي بدأ بها القرآن وصف المؤمنين.',
    desc_en: 'Believing in what lies beyond sensory perception — the Hereafter, angels, and divine decree — is the defining quality of the God-conscious, the very first attribute the Quran ascribes to the believers.',
    refs: ['2:3', '67:12', '21:49', '36:11', '50:33'],
    story: ''
  },
  {
    id: 4,
    ar: 'الإخلاص',
    en: 'Sincerity (Ikhlas)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'الإخلاص لله في العبادة والعمل شرط لقبول الأعمال. على المؤمن أن يجعل كل عمله خالصًا لوجه الله تعالى.',
    desc_en: 'Sincerity toward God in worship and deeds is a prerequisite for their acceptance. The believer must dedicate every action purely to God.',
    refs: ['98:5', '39:2-3', '7:29', '4:146', '112:1'],
    story: ''
  },
  {
    id: 5,
    ar: 'تقوى الله',
    en: 'God-consciousness (Taqwa)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'التقوى هي أن يجعل العبد بينه وبين غضب الله وقاية بفعل أوامره واجتناب نواهيه. وهي خير الزاد ليوم المعاد.',
    desc_en: 'Taqwa is to place a shield between oneself and God\'s displeasure by obeying His commands and avoiding His prohibitions. It is the best provision for the Day of Return.',
    refs: ['2:197', '3:102', '49:13', '65:2-3', '2:177'],
    story: ''
  },
  {
    id: 6,
    ar: 'الرجاء في رحمة الله',
    en: 'Hope in God\'s Mercy',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'رحمة الله وسعت كل شيء ولا يقنط من رحمته إلا القوم الضالون. على المؤمن أن يكون بين الخوف والرجاء.',
    desc_en: 'God\'s mercy encompasses all things, and none despairs of it except those who are astray. The believer should live between hope and reverent awe.',
    refs: ['39:53', '7:156', '12:87', '15:56', '40:7'],
    story: 'يعقوب'
  },
  {
    id: 7,
    ar: 'ذكر الله',
    en: 'Remembrance of God (Dhikr)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'بذكر الله تطمئن القلوب وتسكن النفوس. والذاكرين الله كثيرًا والذاكرات أعدّ الله لهم مغفرة وأجرًا عظيمًا.',
    desc_en: 'Through the remembrance of God hearts find tranquility and souls find peace. God has prepared forgiveness and a great reward for those who remember Him abundantly.',
    refs: ['13:28', '33:41-42', '2:152', '3:191', '7:205'],
    story: ''
  },
  {
    id: 8,
    ar: 'الشكر لله',
    en: 'Gratitude to God (Shukr)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'شكر الله على نعمه سبب لزيادتها وكفرها سبب لزوالها. والشكر يكون بالقلب واللسان والجوارح.',
    desc_en: 'Thanking God for His blessings causes them to increase, while ingratitude causes them to be taken away. Gratitude is expressed through the heart, tongue, and actions.',
    refs: ['14:7', '2:152', '31:12', '27:40', '34:13'],
    story: 'سليمان'
  },
  {
    id: 9,
    ar: 'التوبة',
    en: 'Repentance (Tawbah)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'باب التوبة مفتوح دائمًا والله يحب التوابين ويحب المتطهرين. التوبة النصوح تمحو الذنوب وتبدل السيئات حسنات.',
    desc_en: 'The door of repentance is always open; God loves those who turn back to Him and purify themselves. Sincere repentance erases sins and transforms misdeeds into good deeds.',
    refs: ['66:8', '2:222', '25:70', '39:53', '4:17-18'],
    story: 'آدم'
  },
  {
    id: 10,
    ar: 'اليقين',
    en: 'Certainty of Faith (Yaqeen)',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'اليقين هو أعلى درجات الإيمان وبه يصل العبد إلى الطمأنينة والسكينة. واعبد ربك حتى يأتيك اليقين.',
    desc_en: 'Certainty is the highest degree of faith, through which the servant attains tranquility and inner peace. Worship your Lord until certainty comes to you.',
    refs: ['15:99', '2:4', '27:82', '51:20', '102:5-7'],
    story: 'إبراهيم'
  },
  {
    id: 11,
    ar: 'التسليم لأمر الله',
    en: 'Submission to God\'s Will',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'الإسلام الحقيقي هو التسليم الكامل لله في السراء والضراء والرضا بقضائه وقدره مع السعي والعمل.',
    desc_en: 'True Islam is complete submission to God in times of ease and hardship, accepting His decree and destiny while continuing to strive and act.',
    refs: ['2:131', '3:83', '6:162', '22:34', '33:36'],
    story: 'إبراهيم'
  },
  {
    id: 12,
    ar: 'الاستعداد ليوم القيامة',
    en: 'Day of Judgment Awareness',
    cat: 'faith',
    cat_ar: 'إيمان',
    desc_ar: 'الإيمان بيوم القيامة يدفع المؤمن للعمل الصالح ويمنعه من الظلم. يوم لا ينفع فيه مال ولا بنون إلا من أتى الله بقلب سليم.',
    desc_en: 'Belief in the Day of Judgment motivates righteous action and deters injustice. A day when neither wealth nor children avail — only a sound heart before God.',
    refs: ['26:88-89', '99:6-8', '82:17-19', '101:6-11', '84:6'],
    story: ''
  },

  // ═══════════════════════════════════════════════════════════
  // ETHICS (أخلاق) — 12 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 13,
    ar: 'الصدق والأمانة',
    en: 'Honesty & Truthfulness',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الصدق يهدي إلى البر والبر يهدي إلى الجنة. أمر الله المؤمنين أن يكونوا مع الصادقين في كل أحوالهم.',
    desc_en: 'Truthfulness leads to righteousness and righteousness leads to Paradise. God commands the believers to be among the truthful in all their affairs.',
    refs: ['9:119', '33:70-71', '5:119', '3:17', '39:33'],
    story: ''
  },
  {
    id: 14,
    ar: 'العدل والإنصاف',
    en: 'Justice & Fairness',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'العدل فريضة حتى مع الأعداء. أمر الله بالقسط في الشهادة ولو على النفس أو الوالدين أو الأقربين.',
    desc_en: 'Justice is obligatory even toward enemies. God commands equity in testimony, even if it is against oneself, one\'s parents, or close relatives.',
    refs: ['4:135', '5:8', '16:90', '4:58', '49:9'],
    story: ''
  },
  {
    id: 15,
    ar: 'التواضع',
    en: 'Humility',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'عباد الرحمن يمشون على الأرض هونًا. التواضع خلق الأنبياء وصفة المؤمنين الحقيقيين.',
    desc_en: 'The servants of the Most Merciful walk upon the earth in humility. Humility is the character of the prophets and the hallmark of true believers.',
    refs: ['25:63', '31:18-19', '17:37', '26:215', '15:88'],
    story: ''
  },
  {
    id: 16,
    ar: 'الرحمة واللين',
    en: 'Kindness & Compassion',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الرحمة صفة من صفات الله العظمى وأمر بها عباده. فبما رحمة من الله لنت لهم ولو كنت فظًّا غليظ القلب لانفضوا من حولك.',
    desc_en: 'Mercy is one of God\'s supreme attributes and He commands it of His servants. It was by God\'s mercy that the Prophet was gentle; had he been harsh, people would have dispersed from around him.',
    refs: ['3:159', '21:107', '6:12', '6:54', '48:29'],
    story: 'محمد'
  },
  {
    id: 17,
    ar: 'العفو والصفح',
    en: 'Forgiveness',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'العفو عند المقدرة من أعظم الأخلاق. والذين يعفون عن الناس والله يحب المحسنين.',
    desc_en: 'Pardoning when one has the power to retaliate is among the noblest of traits. Those who pardon people — God loves those who do good.',
    refs: ['3:134', '42:40', '42:43', '7:199', '24:22'],
    story: 'يوسف'
  },
  {
    id: 18,
    ar: 'الوفاء بالعهود',
    en: 'Keeping Promises',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الوفاء بالعهد من صفات المؤمنين وأمر إلهي مؤكد. إن العهد كان مسؤولًا يُسأل عنه الإنسان يوم القيامة.',
    desc_en: 'Honoring covenants is a defining trait of believers and a firm divine command. Every covenant will be questioned on the Day of Judgment.',
    refs: ['17:34', '2:177', '5:1', '23:8', '16:91'],
    story: ''
  },
  {
    id: 19,
    ar: 'حسن القول',
    en: 'Good Speech',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'أمر الله بقول الأحسن والكلمة الطيبة كشجرة طيبة أصلها ثابت وفرعها في السماء.',
    desc_en: 'God commands the best of speech. A good word is like a good tree whose root is firm and whose branches reach the sky.',
    refs: ['14:24-26', '17:53', '2:83', '4:148', '33:70'],
    story: ''
  },
  {
    id: 20,
    ar: 'تحريم الغيبة والنميمة',
    en: 'Avoiding Backbiting',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'حرّم الله الغيبة وشبّهها بأكل لحم الأخ الميت. والتجسس والنميمة من كبائر الذنوب التي تفسد المجتمع.',
    desc_en: 'God forbids backbiting and likens it to eating the flesh of one\'s dead brother. Spying and tale-bearing are major sins that destroy social fabric.',
    refs: ['49:12', '104:1', '68:10-11', '24:19'],
    story: ''
  },
  {
    id: 21,
    ar: 'تحريم الحسد',
    en: 'Avoiding Envy',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الحسد يأكل الحسنات ويهلك صاحبه. أمر الله بالاستعاذة من شر الحاسد وبالرضا بما قسمه الله.',
    desc_en: 'Envy consumes good deeds and destroys its bearer. God commands seeking refuge from the evil of the envier and being content with what He has apportioned.',
    refs: ['113:5', '4:54', '2:109', '4:32', '20:131'],
    story: 'يوسف'
  },
  {
    id: 22,
    ar: 'الحياء',
    en: 'Modesty',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الحياء خلق رفيع يدعو إلى غض البصر وحفظ الفرج والتعامل بأدب مع الآخرين.',
    desc_en: 'Modesty is a noble character trait that calls for lowering the gaze, guarding chastity, and treating others with propriety.',
    refs: ['24:30-31', '33:53', '28:25', '7:26'],
    story: 'موسى'
  },
  {
    id: 23,
    ar: 'الكرم والجود',
    en: 'Generosity',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الإنفاق في سبيل الله من أعظم القربات. مثل الذين ينفقون أموالهم كمثل حبة أنبتت سبع سنابل.',
    desc_en: 'Spending in God\'s cause is among the greatest acts of devotion. The parable of those who spend is like a grain that sprouts seven ears, each bearing a hundred grains.',
    refs: ['2:261', '2:267', '3:92', '76:8-9', '92:5-7'],
    story: ''
  },
  {
    id: 24,
    ar: 'تحريم الكبر',
    en: 'Avoiding Arrogance',
    cat: 'ethics',
    cat_ar: 'أخلاق',
    desc_ar: 'الكبر أول ذنب عُصي الله به حين أبى إبليس السجود لآدم. لا يدخل الجنة من كان في قلبه مثقال ذرة من كبر.',
    desc_en: 'Arrogance was the first sin committed against God when Iblis refused to bow to Adam. Paradise is barred from anyone who harbors even an atom\'s weight of pride.',
    refs: ['2:34', '31:18', '7:13', '39:72', '16:23'],
    story: 'إبليس'
  },

  // ═══════════════════════════════════════════════════════════
  // SOCIAL (مجتمع) — 10 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 25,
    ar: 'وحدة الأمة',
    en: 'Unity of the Ummah',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'الاعتصام بحبل الله جميعًا وعدم التفرق أساس قوة الأمة. إنما المؤمنون إخوة فأصلحوا بين أخويكم.',
    desc_en: 'Holding firmly to God\'s rope together and avoiding division is the foundation of the community\'s strength. The believers are but brothers, so reconcile between them.',
    refs: ['3:103', '49:10', '8:46', '6:159', '21:92'],
    story: ''
  },
  {
    id: 26,
    ar: 'الشورى',
    en: 'Consultation (Shura)',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'الشورى مبدأ أساسي في الحكم والتعامل بين المسلمين. وأمرهم شورى بينهم من صفات المؤمنين.',
    desc_en: 'Mutual consultation is a fundamental principle of governance and dealings among Muslims. Conducting affairs through consultation is a hallmark of believers.',
    refs: ['42:38', '3:159'],
    story: ''
  },
  {
    id: 27,
    ar: 'مقاومة الظلم',
    en: 'Standing Up Against Oppression',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'القيام في وجه الظلم واجب والقعود عنه إثم. أذن الله للمظلومين بالدفاع عن أنفسهم ووعد بنصرهم.',
    desc_en: 'Standing against oppression is a duty and passivity toward it is sinful. God permits the oppressed to defend themselves and promises them His support.',
    refs: ['22:39-40', '4:75', '42:39-42', '28:5', '2:193'],
    story: 'موسى'
  },
  {
    id: 28,
    ar: 'مساعدة المحتاجين',
    en: 'Helping the Needy',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'إطعام الطعام وإعانة المحتاج من أفضل الأعمال عند الله. ويطعمون الطعام على حبه مسكينًا ويتيمًا وأسيرًا.',
    desc_en: 'Feeding the hungry and aiding the needy are among the best deeds before God. They give food, despite their love for it, to the poor, the orphan, and the captive.',
    refs: ['76:8-9', '107:1-7', '90:12-16', '2:177', '69:34'],
    story: ''
  },
  {
    id: 29,
    ar: 'الوفاء بالعقود',
    en: 'Fulfilling Contracts',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'أمر الله بالوفاء بالعقود والمواثيق وعدم نقضها. يا أيها الذين آمنوا أوفوا بالعقود.',
    desc_en: 'God commands the fulfillment of contracts and covenants and forbids their violation. O you who believe, fulfill your contracts.',
    refs: ['5:1', '16:91', '17:34', '13:20'],
    story: ''
  },
  {
    id: 30,
    ar: 'التجارة العادلة',
    en: 'Fair Trade',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'أمر الله بالعدل في الميزان والمكيال وحرّم الغش والتطفيف. ويل للمطففين الذين إذا اكتالوا على الناس يستوفون.',
    desc_en: 'God commands fairness in weights and measures and forbids fraud and cheating. Woe to the defrauders who demand full measure from others but give less themselves.',
    refs: ['83:1-3', '55:9', '6:152', '11:84-85', '17:35'],
    story: 'شعيب'
  },
  {
    id: 31,
    ar: 'حماية الضعفاء',
    en: 'Protecting the Vulnerable',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'حماية الضعفاء واليتامى والمساكين مسؤولية المجتمع المسلم. وما لكم لا تقاتلون في سبيل الله والمستضعفين.',
    desc_en: 'Protecting the vulnerable — orphans, the poor, and the oppressed — is a collective responsibility. Why should you not fight in the cause of God and the oppressed?',
    refs: ['4:75', '4:127', '93:9-10', '89:17-20', '2:220'],
    story: ''
  },
  {
    id: 32,
    ar: 'الأمر بالمعروف والنهي عن المنكر',
    en: 'Enjoining Good & Forbidding Evil',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'الأمة المسلمة خير أمة أخرجت للناس لأنها تأمر بالمعروف وتنهى عن المنكر وتؤمن بالله.',
    desc_en: 'The Muslim community is the best community raised for humanity because it enjoins good, forbids evil, and believes in God.',
    refs: ['3:110', '3:104', '9:71', '7:157', '22:41'],
    story: ''
  },
  {
    id: 33,
    ar: 'الإصلاح بين الناس',
    en: 'Reconciliation',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'الإصلاح بين المتخاصمين من أفضل الأعمال. لا خير في كثير من نجواهم إلا من أمر بصدقة أو معروف أو إصلاح بين الناس.',
    desc_en: 'Reconciling between people in conflict is among the best of deeds. There is no good in most secret talk except for that which enjoins charity, good conduct, or reconciliation.',
    refs: ['4:114', '49:9-10', '8:1', '2:224'],
    story: ''
  },
  {
    id: 34,
    ar: 'العدالة الاجتماعية',
    en: 'Social Justice',
    cat: 'social',
    cat_ar: 'مجتمع',
    desc_ar: 'الله يأمر بالعدل والإحسان ويريد ألا يكون المال دولة بين الأغنياء فقط. الزكاة والفيء يحققان التوازن الاجتماعي.',
    desc_en: 'God commands justice and excellence and does not want wealth to circulate only among the rich. Zakah and public funds achieve social balance.',
    refs: ['16:90', '59:7', '4:135', '5:8', '57:25'],
    story: ''
  },

  // ═══════════════════════════════════════════════════════════
  // WORSHIP (عبادة) — 8 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 35,
    ar: 'الصلاة',
    en: 'Prayer (Salah)',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الصلاة عماد الدين وأول ما يحاسب عليه العبد. إن الصلاة تنهى عن الفحشاء والمنكر ولذكر الله أكبر.',
    desc_en: 'Prayer is the pillar of the faith and the first thing a person will be held accountable for. Indeed prayer prevents immorality and wrongdoing, and the remembrance of God is greater.',
    refs: ['29:45', '2:238', '4:103', '11:114', '20:14'],
    story: ''
  },
  {
    id: 36,
    ar: 'الزكاة',
    en: 'Charity (Zakah)',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الزكاة تطهر المال والنفس وتحقق التكافل الاجتماعي. وأقيموا الصلاة وآتوا الزكاة أمر متكرر في القرآن.',
    desc_en: 'Zakah purifies wealth and the soul and achieves social solidarity. "Establish prayer and give zakah" is one of the most repeated commands in the Quran.',
    refs: ['9:103', '2:43', '2:277', '9:60', '23:4'],
    story: ''
  },
  {
    id: 37,
    ar: 'الصيام',
    en: 'Fasting',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الصيام فُرض على المؤمنين لتحقيق التقوى. شهر رمضان الذي أنزل فيه القرآن هدى للناس.',
    desc_en: 'Fasting was prescribed for believers to attain God-consciousness. Ramadan is the month in which the Quran was revealed as guidance for humanity.',
    refs: ['2:183', '2:185', '2:187'],
    story: ''
  },
  {
    id: 38,
    ar: 'الحج',
    en: 'Pilgrimage (Hajj)',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الحج ركن من أركان الإسلام فرضه الله على المستطيع. وأذّن في الناس بالحج يأتوك رجالًا وعلى كل ضامر.',
    desc_en: 'Hajj is a pillar of Islam, obligatory upon those who are able. Proclaim the pilgrimage to the people — they will come on foot and on every lean camel.',
    refs: ['3:97', '22:27-28', '2:196-197', '22:36-37'],
    story: 'إبراهيم'
  },
  {
    id: 39,
    ar: 'الدعاء',
    en: 'Supplication (Du\'a)',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الدعاء مخ العبادة والله قريب يجيب دعوة الداعي إذا دعاه. ادعوني أستجب لكم.',
    desc_en: 'Supplication is the essence of worship. God is near and responds to the call of the caller when they call upon Him. Call upon Me and I will respond.',
    refs: ['40:60', '2:186', '27:62', '7:55-56', '25:77'],
    story: 'زكريا'
  },
  {
    id: 40,
    ar: 'تلاوة القرآن',
    en: 'Reciting the Quran',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'تلاوة القرآن وتدبر آياته عبادة عظيمة. إن هذا القرآن يهدي للتي هي أقوم ويبشر المؤمنين.',
    desc_en: 'Reciting the Quran and reflecting on its verses is a great act of worship. This Quran guides to what is most upright and gives glad tidings to the believers.',
    refs: ['17:9', '73:4', '56:77-80', '35:29', '7:204'],
    story: ''
  },
  {
    id: 41,
    ar: 'قيام الليل',
    en: 'Night Prayer (Qiyam)',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'قيام الليل أقرب وقت للعبد من ربه. تتجافى جنوبهم عن المضاجع يدعون ربهم خوفًا وطمعًا.',
    desc_en: 'The night prayer is the closest a servant can be to their Lord. Their sides forsake their beds, calling upon their Lord in fear and hope.',
    refs: ['32:16', '73:1-4', '51:17-18', '39:9', '17:79'],
    story: ''
  },
  {
    id: 42,
    ar: 'الأضحية والتقرب',
    en: 'Sacrifice',
    cat: 'worship',
    cat_ar: 'عبادة',
    desc_ar: 'الذبح والنحر عبادة لله وحده. لن ينال الله لحومها ولا دماؤها ولكن يناله التقوى منكم.',
    desc_en: 'Ritual sacrifice is an act of worship for God alone. It is not their meat or blood that reaches God, but your piety that reaches Him.',
    refs: ['22:36-37', '108:2', '6:162', '37:102-107'],
    story: 'إبراهيم'
  },

  // ═══════════════════════════════════════════════════════════
  // CHARACTER (شخصية) — 10 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 43,
    ar: 'الصبر',
    en: 'Patience (Sabr)',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'الصبر مفتاح الفرج وقد ذُكر في القرآن أكثر من تسعين مرة. إنما يوفّى الصابرون أجرهم بغير حساب.',
    desc_en: 'Patience is the key to relief and is mentioned in the Quran over ninety times. The patient will be given their reward without measure.',
    refs: ['39:10', '2:153', '2:155-157', '3:200', '103:3'],
    story: 'أيوب'
  },
  {
    id: 44,
    ar: 'المثابرة',
    en: 'Perseverance',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'النجاح يتطلب المثابرة والاستمرار في العمل. إن مع العسر يسرًا وعدٌ من الله أن الفرج يأتي مع الجهد.',
    desc_en: 'Success requires perseverance and continued effort. "With hardship comes ease" is God\'s promise that relief accompanies every struggle.',
    refs: ['94:5-6', '29:69', '47:31', '13:11', '8:66'],
    story: 'نوح'
  },
  {
    id: 45,
    ar: 'الشجاعة',
    en: 'Courage',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'الشجاعة في قول الحق ومواجهة الباطل من صفات الأنبياء والمؤمنين. لا تخافوهم وخافون إن كنتم مؤمنين.',
    desc_en: 'Courage in speaking the truth and confronting falsehood is a trait of prophets and believers. Do not fear them, but fear Me if you are true believers.',
    refs: ['3:175', '9:13', '33:39', '2:249-250', '8:15-16'],
    story: 'داود'
  },
  {
    id: 46,
    ar: 'الحكمة',
    en: 'Wisdom',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'الحكمة هبة عظيمة من الله ومن يؤتَ الحكمة فقد أوتي خيرًا كثيرًا. ادع إلى سبيل ربك بالحكمة والموعظة الحسنة.',
    desc_en: 'Wisdom is a great gift from God; whoever is granted wisdom has been given abundant good. Call to the way of your Lord with wisdom and good instruction.',
    refs: ['2:269', '16:125', '31:12-13', '38:20', '4:113'],
    story: 'لقمان'
  },
  {
    id: 47,
    ar: 'ضبط النفس',
    en: 'Self-restraint',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'كظم الغيظ والتحكم في الانفعالات من صفات المتقين. والكاظمين الغيظ والعافين عن الناس والله يحب المحسنين.',
    desc_en: 'Suppressing anger and controlling emotions are qualities of the God-conscious. Those who restrain their anger and pardon people — God loves those who do good.',
    refs: ['3:134', '7:199-200', '41:34-36', '23:96'],
    story: ''
  },
  {
    id: 48,
    ar: 'القناعة',
    en: 'Contentment',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'القناعة كنز لا يفنى والرضا بما قسم الله أساس السعادة. ولا تمدن عينيك إلى ما متعنا به أزواجًا منهم.',
    desc_en: 'Contentment is an inexhaustible treasure, and being pleased with what God has apportioned is the foundation of happiness. Do not extend your eyes toward what We have given some to enjoy.',
    refs: ['20:131', '15:88', '4:32', '16:53', '9:59'],
    story: ''
  },
  {
    id: 49,
    ar: 'الثبات على الحق',
    en: 'Steadfastness',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'الثبات على الحق في وجه الفتن والمحن من أعظم صفات المؤمنين. يثبت الله الذين آمنوا بالقول الثابت.',
    desc_en: 'Standing firm upon the truth in the face of trials and tribulations is among the greatest qualities of believers. God keeps firm those who believe with the firm word.',
    refs: ['14:27', '41:30-32', '46:13-14', '11:112', '3:8'],
    story: 'أصحاب الأخدود'
  },
  {
    id: 50,
    ar: 'الاستعانة بالله',
    en: 'Reliance on God',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'الاستعانة بالله وحده في كل الأمور أصل من أصول العبادة. إياك نعبد وإياك نستعين.',
    desc_en: 'Seeking help from God alone in all matters is a fundamental principle of worship. You alone we worship and You alone we ask for help.',
    refs: ['1:5', '2:45', '7:128', '8:2-4', '12:18'],
    story: ''
  },
  {
    id: 51,
    ar: 'المسؤولية والمحاسبة',
    en: 'Accountability',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'كل إنسان مسؤول عن أعماله وسيحاسب عليها. ولا تزر وازرة وزر أخرى وأن ليس للإنسان إلا ما سعى.',
    desc_en: 'Every person is responsible for their own deeds and will be held accountable. No bearer of burdens bears the burden of another, and a person gets only what they strive for.',
    refs: ['53:38-39', '17:36', '6:164', '99:7-8', '74:38'],
    story: ''
  },
  {
    id: 52,
    ar: 'محاسبة النفس',
    en: 'Self-reflection',
    cat: 'character',
    cat_ar: 'شخصية',
    desc_ar: 'مراقبة النفس ومحاسبتها أساس التزكية والإصلاح. يا أيها الذين آمنوا اتقوا الله ولتنظر نفس ما قدمت لغد.',
    desc_en: 'Monitoring and evaluating oneself is the basis of spiritual purification and reform. O you who believe, be mindful of God and let every soul consider what it has sent forth for tomorrow.',
    refs: ['59:18', '91:7-10', '75:2', '50:21', '89:27-30'],
    story: ''
  },

  // ═══════════════════════════════════════════════════════════
  // CONSEQUENCES (عواقب) — 10 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 53,
    ar: 'عاقبة الكفر',
    en: 'Consequences of Disbelief',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الكفر بالله وآياته يؤدي إلى الخسران في الدنيا والآخرة. قصص الأمم السابقة عبرة لمن يعتبر.',
    desc_en: 'Denying God and His signs leads to ruin in this world and the Hereafter. The stories of past nations serve as lessons for those who reflect.',
    refs: ['7:96-99', '30:9-10', '35:44', '40:82-85', '47:10'],
    story: 'قوم نوح'
  },
  {
    id: 54,
    ar: 'عاقبة التكبر',
    en: 'Consequences of Arrogance',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'التكبر سبب لهلاك الأمم والأفراد. فرعون تكبّر في الأرض فأغرقه الله وجعله عبرة للعالمين.',
    desc_en: 'Arrogance is a cause of the destruction of nations and individuals. Pharaoh was arrogant on earth, so God drowned him and made him a lesson for all people.',
    refs: ['28:39-40', '40:35', '10:90-92', '2:87', '7:133-136'],
    story: 'فرعون'
  },
  {
    id: 55,
    ar: 'عاقبة الظلم',
    en: 'Consequences of Injustice',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الظلم ظلمات يوم القيامة ولا يفلح الظالمون. أهلك الله قومًا بظلمهم وجعل ديارهم خاوية.',
    desc_en: 'Injustice will be layers of darkness on the Day of Judgment, and the wrongdoers will never prosper. God destroyed peoples for their injustice and left their dwellings desolate.',
    refs: ['11:102', '22:45', '3:140', '14:42', '42:42'],
    story: 'قوم لوط'
  },
  {
    id: 56,
    ar: 'ثواب الصبر',
    en: 'Reward of Patience',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الصبر على البلاء يُكافأ بأجر عظيم في الدنيا والآخرة. أيوب صبر فآتاه الله أهله ومثلهم معهم رحمة.',
    desc_en: 'Patience through affliction is rewarded greatly in this life and the next. Job was patient, so God restored his family and doubled their number as a mercy.',
    refs: ['21:83-84', '38:41-44', '39:10', '16:96', '76:12'],
    story: 'أيوب'
  },
  {
    id: 57,
    ar: 'ثواب الإيمان',
    en: 'Reward of Faith',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الإيمان والعمل الصالح مفتاح السعادة في الدارين. من عمل صالحًا من ذكر أو أنثى وهو مؤمن فلنحيينه حياة طيبة.',
    desc_en: 'Faith coupled with righteous deeds is the key to happiness in both worlds. Whoever does good, male or female, while being a believer — We will grant them a good life.',
    refs: ['16:97', '10:62-64', '41:30-32', '13:28-29', '65:2-3'],
    story: ''
  },
  {
    id: 58,
    ar: 'عاقبة نقض العهود',
    en: 'Consequences of Breaking Covenants',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'نقض العهود والمواثيق يجلب اللعنة والطرد من رحمة الله. فبما نقضهم ميثاقهم لعنّاهم وجعلنا قلوبهم قاسية.',
    desc_en: 'Breaking covenants and pacts brings curse and banishment from God\'s mercy. Because of their breaking of their covenant, We cursed them and hardened their hearts.',
    refs: ['5:13', '2:27', '13:25', '4:155', '7:102'],
    story: 'بنو إسرائيل'
  },
  {
    id: 59,
    ar: 'عاقبة اتباع الهوى',
    en: 'Consequences of Following Desires',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'اتباع الهوى يضل الإنسان عن سبيل الله ويهلكه. أرأيت من اتخذ إلهه هواه أفأنت تكون عليه وكيلًا.',
    desc_en: 'Following whims leads a person astray from God\'s path and to their ruin. Have you seen one who takes their own desire as their god? Would you then be a guardian over them?',
    refs: ['25:43', '45:23', '28:50', '47:14', '79:40-41'],
    story: 'السامري'
  },
  {
    id: 60,
    ar: 'ثواب الحسنات',
    en: 'Reward of Good Deeds',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الحسنات تضاعف والله لا يضيع أجر المحسنين. من جاء بالحسنة فله عشر أمثالها ومن جاء بالسيئة فلا يجزى إلا مثلها.',
    desc_en: 'Good deeds are multiplied and God never wastes the reward of those who do good. Whoever brings a good deed shall have ten times its like, and whoever brings an evil deed shall only be recompensed its equal.',
    refs: ['6:160', '2:261', '4:40', '99:7-8', '28:84'],
    story: ''
  },
  {
    id: 61,
    ar: 'عاقبة الفساد',
    en: 'Consequences of Corruption',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'الفساد في الأرض يجلب العذاب والدمار. ظهر الفساد في البر والبحر بما كسبت أيدي الناس ليذيقهم بعض الذي عملوا.',
    desc_en: 'Corruption on earth brings punishment and destruction. Corruption has appeared on land and sea because of what people\'s hands have earned, so that He may let them taste some of what they have done.',
    refs: ['30:41', '2:205', '5:64', '7:56', '28:77'],
    story: 'قارون'
  },
  {
    id: 62,
    ar: 'التحذير من النفاق',
    en: 'Warning Against Hypocrisy',
    cat: 'consequences',
    cat_ar: 'عواقب',
    desc_ar: 'المنافقون في الدرك الأسفل من النار. يخادعون الله والذين آمنوا وما يخدعون إلا أنفسهم.',
    desc_en: 'The hypocrites will be in the lowest depths of the Fire. They try to deceive God and the believers, but they only deceive themselves.',
    refs: ['4:145', '2:8-10', '63:1-4', '9:67-68', '33:73'],
    story: ''
  },

  // ═══════════════════════════════════════════════════════════
  // KNOWLEDGE (علم) — 6 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 63,
    ar: 'طلب العلم',
    en: 'Seeking Knowledge',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'أول كلمة نزلت من القرآن "اقرأ" مما يدل على أهمية العلم. يرفع الله الذين أوتوا العلم درجات.',
    desc_en: 'The first word revealed of the Quran was "Read," indicating the paramount importance of knowledge. God raises those who are given knowledge by many degrees.',
    refs: ['96:1-5', '58:11', '20:114', '39:9', '35:28'],
    story: 'موسى'
  },
  {
    id: 64,
    ar: 'التفكر في الخلق',
    en: 'Reflecting on Creation',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'التفكر في خلق السماوات والأرض عبادة عقلية يدعو إليها القرآن. إن في خلق السماوات والأرض واختلاف الليل والنهار لآيات.',
    desc_en: 'Reflecting on the creation of the heavens and earth is an intellectual act of worship the Quran invites. In the creation of the heavens and earth and the alternation of night and day are signs.',
    refs: ['3:190-191', '88:17-20', '10:101', '30:20-25', '2:164'],
    story: ''
  },
  {
    id: 65,
    ar: 'الاعتبار بالتاريخ',
    en: 'Learning from History',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'قصص الأمم السابقة في القرآن ليست للتسلية بل للعبرة والاتعاظ. لقد كان في قصصهم عبرة لأولي الألباب.',
    desc_en: 'The stories of past nations in the Quran are not entertainment but lessons and admonitions. In their stories there is a lesson for people of understanding.',
    refs: ['12:111', '7:176', '11:120', '28:58', '30:9'],
    story: ''
  },
  {
    id: 66,
    ar: 'الحكمة من التجربة',
    en: 'Wisdom of Experience',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'الابتلاءات تصقل الإنسان وتعلمه ما لا تعلمه الكتب. علّم الله آدم الأسماء كلها وكرّمه بالعلم.',
    desc_en: 'Trials refine a person and teach what books cannot. God taught Adam all the names and honored him through knowledge.',
    refs: ['2:31-33', '18:66-82', '2:102', '27:15-16'],
    story: 'الخضر'
  },
  {
    id: 67,
    ar: 'تعليم الآخرين',
    en: 'Teaching Others',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'نشر العلم وتعليم الناس أمانة وواجب. من كتم علمًا ألجمه الله بلجام من نار يوم القيامة.',
    desc_en: 'Spreading knowledge and teaching people is a trust and obligation. The Quran condemns those who conceal the knowledge and guidance that God has revealed.',
    refs: ['2:159', '3:187', '2:42', '5:67', '16:43-44'],
    story: ''
  },
  {
    id: 68,
    ar: 'تدبر القرآن',
    en: 'Pondering the Quran',
    cat: 'knowledge',
    cat_ar: 'علم',
    desc_ar: 'القرآن أنزل للتدبر والعمل لا للقراءة فقط. أفلا يتدبرون القرآن أم على قلوب أقفالها.',
    desc_en: 'The Quran was revealed to be pondered and acted upon, not merely recited. Do they not reflect upon the Quran, or are there locks upon their hearts?',
    refs: ['47:24', '4:82', '38:29', '23:68', '54:17'],
    story: ''
  },

  // ═══════════════════════════════════════════════════════════
  // FAMILY (أسرة) — 8 lessons
  // ═══════════════════════════════════════════════════════════
  {
    id: 69,
    ar: 'بر الوالدين',
    en: 'Honoring Parents',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'بر الوالدين قرنه الله بعبادته. وقضى ربك ألا تعبدوا إلا إياه وبالوالدين إحسانًا ولا تقل لهما أف.',
    desc_en: 'Honoring parents is paired by God with His own worship. Your Lord has decreed that you worship none but Him and that you be excellent to parents — do not even say "uff" to them.',
    refs: ['17:23-24', '31:14-15', '46:15', '29:8', '2:83'],
    story: ''
  },
  {
    id: 70,
    ar: 'صلة الرحم',
    en: 'Kindness to Relatives',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'صلة الرحم واجب شرعي وقطيعتها من الكبائر. واتقوا الله الذي تساءلون به والأرحام.',
    desc_en: 'Maintaining family ties is a religious obligation and severing them is a major sin. Be mindful of God, by whose name you ask one another, and of family bonds.',
    refs: ['4:1', '47:22-23', '2:177', '13:21', '16:90'],
    story: ''
  },
  {
    id: 71,
    ar: 'الزواج والشراكة',
    en: 'Marriage & Partnership',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'الزواج آية من آيات الله وسكن ومودة ورحمة بين الزوجين. هن لباس لكم وأنتم لباس لهن.',
    desc_en: 'Marriage is one of God\'s signs — tranquility, affection, and mercy between spouses. They are a garment for you and you are a garment for them.',
    refs: ['30:21', '2:187', '4:19', '2:228', '4:34'],
    story: ''
  },
  {
    id: 72,
    ar: 'تربية الأبناء',
    en: 'Raising Children',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'تربية الأولاد على الإيمان والأخلاق مسؤولية عظيمة. وصية لقمان لابنه نموذج قرآني في التربية الإيمانية.',
    desc_en: 'Raising children upon faith and good character is a tremendous responsibility. Luqman\'s advice to his son is a Quranic model of faith-based upbringing.',
    refs: ['31:13-19', '66:6', '25:74', '37:100-102', '14:40'],
    story: 'لقمان'
  },
  {
    id: 73,
    ar: 'حقوق اليتامى',
    en: 'Rights of Orphans',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'رعاية اليتامى وحفظ أموالهم واجب مؤكد. إن الذين يأكلون أموال اليتامى ظلمًا إنما يأكلون في بطونهم نارًا.',
    desc_en: 'Caring for orphans and safeguarding their property is a firm obligation. Those who unjustly consume the wealth of orphans are only consuming fire in their bellies.',
    refs: ['4:10', '4:2-6', '93:9', '2:220', '89:17'],
    story: ''
  },
  {
    id: 74,
    ar: 'حقوق الجار',
    en: 'Rights of Neighbors',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'الإحسان إلى الجار قريبًا كان أو بعيدًا من الأوامر الإلهية. واعبدوا الله ولا تشركوا به شيئًا وبالوالدين إحسانًا وبذي القربى واليتامى والمساكين والجار.',
    desc_en: 'Being kind to neighbors, whether near or distant, is a divine command. Worship God, associate nothing with Him, and be excellent to parents, relatives, orphans, the needy, and neighbors.',
    refs: ['4:36', '2:83'],
    story: ''
  },
  {
    id: 75,
    ar: 'تماسك الأسرة',
    en: 'Family Unity',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'الأسرة المتماسكة أساس المجتمع السليم. الدعاء بصلاح الذرية والأزواج من صفات عباد الرحمن.',
    desc_en: 'A cohesive family is the foundation of a healthy society. Praying for the righteousness of one\'s spouse and children is a quality of the servants of the Most Merciful.',
    refs: ['25:74', '3:38', '14:40', '46:15', '66:11'],
    story: ''
  },
  {
    id: 76,
    ar: 'رعاية كبار السن',
    en: 'Caring for the Elderly',
    cat: 'family',
    cat_ar: 'أسرة',
    desc_ar: 'الإحسان إلى الوالدين عند الكبر واجب عظيم. إما يبلغن عندك الكبر أحدهما أو كلاهما فلا تقل لهما أف ولا تنهرهما.',
    desc_en: 'Being good to elderly parents is a paramount duty. If one or both of them reach old age with you, do not say to them a word of disrespect and do not repel them.',
    refs: ['17:23-24', '46:15-18', '31:14', '29:8'],
    story: ''
  }
];
