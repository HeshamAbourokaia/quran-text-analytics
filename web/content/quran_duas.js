const QURAN_DUAS = [
  // ═══════════════════════════════════════════════════════════════
  // PROPHET DUAS - أدعية الأنبياء (Supplications of the Prophets)
  // ═══════════════════════════════════════════════════════════════

  // ── Adam (آدم) ──
  {
    id: 1,
    ar: 'دعاء آدم وحواء',
    en: 'Prayer of Adam and Eve',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ',
    desc_en: 'Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.',
    refs: ['7:23'],
    context_ar: 'دعاء آدم وحواء بعد أن أكلا من الشجرة المحرمة',
    context_en: 'Adam and Eve\'s prayer after eating from the forbidden tree'
  },

  // ── Nuh (نوح) ──
  {
    id: 2,
    ar: 'دعاء نوح للمغفرة',
    en: 'Nuh\'s prayer for forgiveness',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ وَلِمَن دَخَلَ بَيْتِيَ مُؤْمِنًا وَلِلْمُؤْمِنِينَ وَالْمُؤْمِنَاتِ وَلَا تَزِدِ الظَّالِمِينَ إِلَّا تَبَارًا',
    desc_en: 'My Lord, forgive me and my parents and whoever enters my house a believer, and the believing men and believing women. And do not increase the wrongdoers except in destruction.',
    refs: ['71:28'],
    context_ar: 'دعاء نوح عليه السلام في آخر دعوته لقومه',
    context_en: 'Nuh\'s prayer at the conclusion of his call to his people'
  },
  {
    id: 3,
    ar: 'دعاء نوح للنجاة',
    en: 'Nuh\'s prayer for salvation',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي أَعُوذُ بِكَ أَنْ أَسْأَلَكَ مَا لَيْسَ لِي بِهِ عِلْمٌ ۖ وَإِلَّا تَغْفِرْ لِي وَتَرْحَمْنِي أَكُن مِّنَ الْخَاسِرِينَ',
    desc_en: 'My Lord, I seek refuge in You from asking that of which I have no knowledge. And unless You forgive me and have mercy upon me, I will be among the losers.',
    refs: ['11:47'],
    context_ar: 'دعاء نوح بعد أن عاتبه الله على سؤاله بشأن ابنه',
    context_en: 'Nuh\'s prayer after God admonished him for asking about his son'
  },
  {
    id: 4,
    ar: 'دعاء نوح عند ركوب السفينة',
    en: 'Nuh\'s prayer upon boarding the Ark',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'بِسْمِ اللَّهِ مَجْرَاهَا وَمُرْسَاهَا ۚ إِنَّ رَبِّي لَغَفُورٌ رَّحِيمٌ',
    desc_en: 'In the name of Allah is its course and its anchorage. Indeed, my Lord is Forgiving and Merciful.',
    refs: ['11:41'],
    context_ar: 'دعاء نوح عند ركوب السفينة وقت الطوفان',
    context_en: 'Nuh\'s invocation when boarding the Ark during the Flood'
  },
  {
    id: 5,
    ar: 'دعاء نوح بعد النزول من السفينة',
    en: 'Nuh\'s prayer upon disembarking',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ أَنزِلْنِي مُنزَلًا مُّبَارَكًا وَأَنتَ خَيْرُ الْمُنزِلِينَ',
    desc_en: 'My Lord, let me land at a blessed landing place, and You are the best to accommodate us.',
    refs: ['23:29'],
    context_ar: 'دعاء نوح عند النزول من السفينة',
    context_en: 'Nuh\'s prayer asking for a blessed landing place'
  },
  {
    id: 6,
    ar: 'استنصار نوح',
    en: 'Nuh\'s cry for help',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي مَغْلُوبٌ فَانتَصِرْ',
    desc_en: 'My Lord, indeed I am overpowered, so help me.',
    refs: ['54:10'],
    context_ar: 'نداء نوح لله لما كذّبه قومه واستكبروا',
    context_en: 'Nuh\'s desperate cry to God when his people rejected and overpowered him'
  },
  {
    id: 7,
    ar: 'دعاء نوح على الكافرين',
    en: 'Nuh\'s prayer against the disbelievers',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَّبِّ لَا تَذَرْ عَلَى الْأَرْضِ مِنَ الْكَافِرِينَ دَيَّارًا',
    desc_en: 'My Lord, do not leave upon the earth from among the disbelievers an inhabitant.',
    refs: ['71:26'],
    context_ar: 'دعاء نوح بعد يأسه من إيمان قومه',
    context_en: 'Nuh\'s prayer after losing hope in his people\'s faith'
  },
  {
    id: 8,
    ar: 'دعاء نوح بالنصر',
    en: 'Nuh\'s prayer for victory',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'أَنِّي مَغْلُوبٌ فَانتَصِرْ',
    desc_en: 'Indeed, I am overcome, so help.',
    refs: ['54:10'],
    context_ar: 'دعاء نوح ربه مستنصرًا على قومه',
    context_en: 'Nuh calling upon his Lord seeking victory over his people'
  },

  // ── Ibrahim (إبراهيم) ──
  {
    id: 9,
    ar: 'دعاء إبراهيم لجعل مكة آمنة',
    en: 'Ibrahim\'s prayer for Makkah\'s security',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اجْعَلْ هَٰذَا الْبَلَدَ آمِنًا وَاجْنُبْنِي وَبَنِيَّ أَن نَّعْبُدَ الْأَصْنَامَ',
    desc_en: 'My Lord, make this city secure and keep me and my sons away from worshipping idols.',
    refs: ['14:35'],
    context_ar: 'دعاء إبراهيم بعد أن أسكن ذريته بمكة',
    context_en: 'Ibrahim\'s prayer after settling his family in Makkah'
  },
  {
    id: 10,
    ar: 'دعاء إبراهيم لإقامة الصلاة',
    en: 'Ibrahim\'s prayer to establish prayer',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اجْعَلْنِي مُقِيمَ الصَّلَاةِ وَمِن ذُرِّيَّتِي ۚ رَبَّنَا وَتَقَبَّلْ دُعَاءِ',
    desc_en: 'My Lord, make me an establisher of prayer, and from my descendants. Our Lord, and accept my supplication.',
    refs: ['14:40'],
    context_ar: 'دعاء إبراهيم أن يجعله الله ممن يقيمون الصلاة هو وذريته',
    context_en: 'Ibrahim\'s prayer for himself and his descendants to maintain prayer'
  },
  {
    id: 11,
    ar: 'دعاء إبراهيم للمغفرة يوم الحساب',
    en: 'Ibrahim\'s prayer for forgiveness on the Day of Judgment',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا اغْفِرْ لِي وَلِوَالِدَيَّ وَلِلْمُؤْمِنِينَ يَوْمَ يَقُومُ الْحِسَابُ',
    desc_en: 'Our Lord, forgive me and my parents and the believers the Day the account is established.',
    refs: ['14:41'],
    context_ar: 'دعاء إبراهيم بالمغفرة له ولوالديه وللمؤمنين',
    context_en: 'Ibrahim\'s prayer for forgiveness for himself, his parents, and the believers'
  },
  {
    id: 12,
    ar: 'دعاء إبراهيم وإسماعيل عند بناء الكعبة',
    en: 'Ibrahim and Ismail\'s prayer while building the Ka\'bah',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا تَقَبَّلْ مِنَّا ۖ إِنَّكَ أَنتَ السَّمِيعُ الْعَلِيمُ',
    desc_en: 'Our Lord, accept this from us. Indeed You are the All-Hearing, the All-Knowing.',
    refs: ['2:127'],
    context_ar: 'دعاء إبراهيم وإسماعيل أثناء رفع قواعد الكعبة',
    context_en: 'Ibrahim and Ismail\'s prayer while raising the foundations of the Ka\'bah'
  },
  {
    id: 13,
    ar: 'دعاء إبراهيم وإسماعيل بالإسلام',
    en: 'Ibrahim and Ismail\'s prayer for submission',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا وَاجْعَلْنَا مُسْلِمَيْنِ لَكَ وَمِن ذُرِّيَّتِنَا أُمَّةً مُّسْلِمَةً لَّكَ وَأَرِنَا مَنَاسِكَنَا وَتُبْ عَلَيْنَا ۖ إِنَّكَ أَنتَ التَّوَّابُ الرَّحِيمُ',
    desc_en: 'Our Lord, and make us Muslims in submission to You and from our descendants a Muslim nation in submission to You. And show us our rites and accept our repentance. Indeed, You are the Accepting of Repentance, the Merciful.',
    refs: ['2:128'],
    context_ar: 'دعاء إبراهيم وإسماعيل بأن يكونا مسلمين وأن تكون ذريتهما أمة مسلمة',
    context_en: 'Ibrahim and Ismail\'s prayer for themselves and their descendants to be a submissive nation'
  },
  {
    id: 14,
    ar: 'دعاء إبراهيم وإسماعيل ببعث النبي',
    en: 'Ibrahim and Ismail\'s prayer for a Messenger',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا وَابْعَثْ فِيهِمْ رَسُولًا مِّنْهُمْ يَتْلُو عَلَيْهِمْ آيَاتِكَ وَيُعَلِّمُهُمُ الْكِتَابَ وَالْحِكْمَةَ وَيُزَكِّيهِمْ ۚ إِنَّكَ أَنتَ الْعَزِيزُ الْحَكِيمُ',
    desc_en: 'Our Lord, and send among them a messenger from themselves who will recite to them Your verses and teach them the Book and wisdom and purify them. Indeed, You are the Exalted in Might, the Wise.',
    refs: ['2:129'],
    context_ar: 'دعاء إبراهيم وإسماعيل بأن يبعث الله رسولاً في ذريتهما',
    context_en: 'Ibrahim and Ismail\'s prayer for God to send a messenger from their descendants'
  },
  {
    id: 15,
    ar: 'دعاء إبراهيم أن يريه كيف يحيي الموتى',
    en: 'Ibrahim\'s request to see resurrection',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ أَرِنِي كَيْفَ تُحْيِي الْمَوْتَىٰ',
    desc_en: 'My Lord, show me how You give life to the dead.',
    refs: ['2:260'],
    context_ar: 'طلب إبراهيم من ربه أن يريه كيف يحيي الموتى ليطمئن قلبه',
    context_en: 'Ibrahim asking God to show him how the dead are revived, to reassure his heart'
  },
  {
    id: 16,
    ar: 'دعاء إبراهيم بالحكمة',
    en: 'Ibrahim\'s prayer for wisdom',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ هَبْ لِي حُكْمًا وَأَلْحِقْنِي بِالصَّالِحِينَ ۝ وَاجْعَل لِّي لِسَانَ صِدْقٍ فِي الْآخِرِينَ ۝ وَاجْعَلْنِي مِن وَرَثَةِ جَنَّةِ النَّعِيمِ',
    desc_en: 'My Lord, grant me wisdom and join me with the righteous. And grant me a reputation of honor among later generations. And place me among the inheritors of the Garden of Pleasure.',
    refs: ['26:83-85'],
    context_ar: 'دعاء إبراهيم بأن يرزقه الله الحكمة وحسن السمعة والجنة',
    context_en: 'Ibrahim\'s prayer for wisdom, a good reputation, and Paradise'
  },
  {
    id: 17,
    ar: 'دعاء إبراهيم للرزق',
    en: 'Ibrahim\'s prayer for provision',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اجْعَلْ هَٰذَا بَلَدًا آمِنًا وَارْزُقْ أَهْلَهُ مِنَ الثَّمَرَاتِ مَنْ آمَنَ مِنْهُم بِاللَّهِ وَالْيَوْمِ الْآخِرِ',
    desc_en: 'My Lord, make this a secure city and provide its people with fruits - whoever of them believes in Allah and the Last Day.',
    refs: ['2:126'],
    context_ar: 'دعاء إبراهيم أن يجعل الله مكة بلدًا آمنًا ويرزق أهلها',
    context_en: 'Ibrahim\'s prayer for Makkah to be a secure city with provision for its believing people'
  },
  {
    id: 18,
    ar: 'دعاء إبراهيم بالولد الصالح',
    en: 'Ibrahim\'s prayer for a righteous son',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ هَبْ لِي مِنَ الصَّالِحِينَ',
    desc_en: 'My Lord, grant me a child from among the righteous.',
    refs: ['37:100'],
    context_ar: 'دعاء إبراهيم أن يرزقه الله ولدًا صالحًا',
    context_en: 'Ibrahim\'s prayer asking God to grant him a righteous child'
  },

  // ── Lut (لوط) ──
  {
    id: 19,
    ar: 'دعاء لوط للنصر',
    en: 'Lut\'s prayer for help',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ انصُرْنِي عَلَى الْقَوْمِ الْمُفْسِدِينَ',
    desc_en: 'My Lord, support me against the corrupting people.',
    refs: ['29:30'],
    context_ar: 'دعاء لوط ربه أن ينصره على قومه المفسدين',
    context_en: 'Lut\'s prayer asking God for help against his corrupt people'
  },
  {
    id: 20,
    ar: 'دعاء لوط للنجاة',
    en: 'Lut\'s prayer for deliverance',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ نَجِّنِي وَأَهْلِي مِمَّا يَعْمَلُونَ',
    desc_en: 'My Lord, save me and my family from what they do.',
    refs: ['26:169'],
    context_ar: 'دعاء لوط ربه أن ينجيه وأهله من فعل قومه',
    context_en: 'Lut\'s prayer asking God to save him and his family from his people\'s actions'
  },

  // ── Yusuf (يوسف) ──
  {
    id: 21,
    ar: 'دعاء يوسف عند الفتنة',
    en: 'Yusuf\'s prayer when tempted',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ السِّجْنُ أَحَبُّ إِلَيَّ مِمَّا يَدْعُونَنِي إِلَيْهِ ۖ وَإِلَّا تَصْرِفْ عَنِّي كَيْدَهُنَّ أَصْبُ إِلَيْهِنَّ وَأَكُن مِّنَ الْجَاهِلِينَ',
    desc_en: 'My Lord, prison is more to my liking than that to which they invite me. And if You do not avert from me their plan, I might incline toward them and be of the ignorant.',
    refs: ['12:33'],
    context_ar: 'دعاء يوسف حين راودته امرأة العزيز والنسوة',
    context_en: 'Yusuf\'s prayer when the women tried to seduce him, preferring prison over sin'
  },
  {
    id: 22,
    ar: 'دعاء يوسف بالوفاة على الإسلام',
    en: 'Yusuf\'s prayer to die in submission',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ قَدْ آتَيْتَنِي مِنَ الْمُلْكِ وَعَلَّمْتَنِي مِن تَأْوِيلِ الْأَحَادِيثِ ۚ فَاطِرَ السَّمَاوَاتِ وَالْأَرْضِ أَنتَ وَلِيِّي فِي الدُّنْيَا وَالْآخِرَةِ ۖ تَوَفَّنِي مُسْلِمًا وَأَلْحِقْنِي بِالصَّالِحِينَ',
    desc_en: 'My Lord, You have given me something of sovereignty and taught me of the interpretation of dreams. Creator of the heavens and earth, You are my protector in this world and the Hereafter. Cause me to die a Muslim and join me with the righteous.',
    refs: ['12:101'],
    context_ar: 'دعاء يوسف بعد اجتماع شمله بأهله وتحقق الرؤيا',
    context_en: 'Yusuf\'s prayer after reuniting with his family and the fulfillment of his dream'
  },

  // ── Shu\'ayb (شعيب) ──
  {
    id: 23,
    ar: 'دعاء شعيب بالتوكل',
    en: 'Shu\'ayb\'s prayer of reliance on God',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'وَمَا تَوْفِيقِي إِلَّا بِاللَّهِ ۚ عَلَيْهِ تَوَكَّلْتُ وَإِلَيْهِ أُنِيبُ',
    desc_en: 'And my success is not but through Allah. Upon Him I have relied, and to Him I return.',
    refs: ['11:88'],
    context_ar: 'قول شعيب لقومه حين دعاهم إلى الإصلاح',
    context_en: 'Shu\'ayb\'s declaration to his people while calling them to righteousness'
  },
  {
    id: 24,
    ar: 'دعاء شعيب بالفتح',
    en: 'Shu\'ayb\'s prayer for God\'s judgment',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا افْتَحْ بَيْنَنَا وَبَيْنَ قَوْمِنَا بِالْحَقِّ وَأَنتَ خَيْرُ الْفَاتِحِينَ',
    desc_en: 'Our Lord, decide between us and our people in truth, and You are the best of those who give decision.',
    refs: ['7:89'],
    context_ar: 'دعاء شعيب ربه أن يحكم بينه وبين قومه بالحق',
    context_en: 'Shu\'ayb\'s prayer asking God to judge between him and his people'
  },

  // ── Musa (موسى) ──
  {
    id: 25,
    ar: 'دعاء موسى بشرح الصدر',
    en: 'Musa\'s prayer to open his heart',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اشْرَحْ لِي صَدْرِي ۝ وَيَسِّرْ لِي أَمْرِي ۝ وَاحْلُلْ عُقْدَةً مِّن لِّسَانِي ۝ يَفْقَهُوا قَوْلِي',
    desc_en: 'My Lord, expand for me my breast. And ease for me my task. And untie the knot from my tongue. That they may understand my speech.',
    refs: ['20:25-28'],
    context_ar: 'دعاء موسى عندما أمره الله بالذهاب إلى فرعون',
    context_en: 'Musa\'s prayer when God commanded him to go to Pharaoh'
  },
  {
    id: 26,
    ar: 'دعاء موسى بعد قتل الرجل',
    en: 'Musa\'s prayer after killing a man',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي ظَلَمْتُ نَفْسِي فَاغْفِرْ لِي',
    desc_en: 'My Lord, indeed I have wronged myself, so forgive me.',
    refs: ['28:16'],
    context_ar: 'دعاء موسى بعد أن قتل رجلاً من القبط خطأً',
    context_en: 'Musa\'s prayer after accidentally killing an Egyptian man'
  },
  {
    id: 27,
    ar: 'دعاء موسى للخير',
    en: 'Musa\'s prayer for goodness',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي لِمَا أَنزَلْتَ إِلَيَّ مِنْ خَيْرٍ فَقِيرٌ',
    desc_en: 'My Lord, indeed I am, for whatever good You would send down to me, in need.',
    refs: ['28:24'],
    context_ar: 'دعاء موسى بعد أن سقى للمرأتين وهو في حال فقر وغربة',
    context_en: 'Musa\'s prayer after helping two women water their flock, while he was poor and a stranger'
  },
  {
    id: 28,
    ar: 'دعاء موسى بالنجاة من الظالمين',
    en: 'Musa\'s prayer for deliverance from the oppressors',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ نَجِّنِي مِنَ الْقَوْمِ الظَّالِمِينَ',
    desc_en: 'My Lord, save me from the wrongdoing people.',
    refs: ['28:21'],
    context_ar: 'دعاء موسى حين فرّ من مصر خوفًا من فرعون',
    context_en: 'Musa\'s prayer when he fled Egypt fearing Pharaoh'
  },
  {
    id: 29,
    ar: 'دعاء موسى بالمغفرة لأخيه وله',
    en: 'Musa\'s prayer for forgiveness for himself and his brother',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اغْفِرْ لِي وَلِأَخِي وَأَدْخِلْنَا فِي رَحْمَتِكَ ۖ وَأَنتَ أَرْحَمُ الرَّاحِمِينَ',
    desc_en: 'My Lord, forgive me and my brother and admit us into Your mercy, for You are the most merciful of the merciful.',
    refs: ['7:151'],
    context_ar: 'دعاء موسى بعد عودته ووجد قومه يعبدون العجل',
    context_en: 'Musa\'s prayer after returning and finding his people worshipping the calf'
  },
  {
    id: 30,
    ar: 'دعاء موسى بأن يجعل هارون وزيرًا',
    en: 'Musa\'s prayer for Harun as his assistant',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'وَاجْعَل لِّي وَزِيرًا مِّنْ أَهْلِي ۝ هَارُونَ أَخِي ۝ اشْدُدْ بِهِ أَزْرِي ۝ وَأَشْرِكْهُ فِي أَمْرِي',
    desc_en: 'And appoint for me a minister from my family - Aaron, my brother. Increase through him my strength. And let him share my task.',
    refs: ['20:29-32'],
    context_ar: 'طلب موسى من ربه أن يجعل هارون أخاه وزيرًا يعينه',
    context_en: 'Musa\'s request for God to appoint his brother Harun as his assistant'
  },
  {
    id: 31,
    ar: 'دعاء موسى يوم الزينة',
    en: 'Musa\'s prayer on the day of the festival',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا اطْمِسْ عَلَىٰ أَمْوَالِهِمْ وَاشْدُدْ عَلَىٰ قُلُوبِهِمْ فَلَا يُؤْمِنُوا حَتَّىٰ يَرَوُا الْعَذَابَ الْأَلِيمَ',
    desc_en: 'Our Lord, obliterate their wealth and harden their hearts so they will not believe until they see the painful punishment.',
    refs: ['10:88'],
    context_ar: 'دعاء موسى على فرعون وملئه',
    context_en: 'Musa\'s prayer against Pharaoh and his establishment'
  },
  {
    id: 32,
    ar: 'دعاء موسى لطلب رؤية الله',
    en: 'Musa\'s request to see God',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ أَرِنِي أَنظُرْ إِلَيْكَ',
    desc_en: 'My Lord, show me Yourself that I may look at You.',
    refs: ['7:143'],
    context_ar: 'طلب موسى من ربه أن يراه عند جبل الطور',
    context_en: 'Musa\'s request to see God at Mount Tur'
  },
  {
    id: 33,
    ar: 'توبة موسى بعد طلب الرؤية',
    en: 'Musa\'s repentance after requesting to see God',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'سُبْحَانَكَ تُبْتُ إِلَيْكَ وَأَنَا أَوَّلُ الْمُؤْمِنِينَ',
    desc_en: 'Exalted are You! I have repented to You, and I am the first of the believers.',
    refs: ['7:143'],
    context_ar: 'قول موسى بعد أن تجلى الله للجبل فجعله دكًا وخرّ موسى صعقًا',
    context_en: 'Musa\'s words after God manifested to the mountain and Musa fell unconscious'
  },
  {
    id: 34,
    ar: 'دعاء موسى بالرحمة',
    en: 'Musa\'s prayer for mercy',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'أَنتَ وَلِيُّنَا فَاغْفِرْ لَنَا وَارْحَمْنَا ۖ وَأَنتَ خَيْرُ الْغَافِرِينَ ۝ وَاكْتُبْ لَنَا فِي هَٰذِهِ الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ إِنَّا هُدْنَا إِلَيْكَ',
    desc_en: 'You are our Protector, so forgive us and have mercy upon us, and You are the best of forgivers. And decree for us in this world that which is good and in the Hereafter; indeed, we have turned to You.',
    refs: ['7:155-156'],
    context_ar: 'دعاء موسى بعد أن أخذت قومه الرجفة',
    context_en: 'Musa\'s prayer after his people were seized by the earthquake'
  },

  // ── Sulaiman (سليمان) ──
  {
    id: 35,
    ar: 'دعاء سليمان بالشكر والعمل الصالح',
    en: 'Sulaiman\'s prayer of gratitude',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ أَوْزِعْنِي أَنْ أَشْكُرَ نِعْمَتَكَ الَّتِي أَنْعَمْتَ عَلَيَّ وَعَلَىٰ وَالِدَيَّ وَأَنْ أَعْمَلَ صَالِحًا تَرْضَاهُ وَأَدْخِلْنِي بِرَحْمَتِكَ فِي عِبَادِكَ الصَّالِحِينَ',
    desc_en: 'My Lord, enable me to be grateful for Your favor which You have bestowed upon me and upon my parents, and to do righteousness of which You approve. And admit me by Your mercy among Your righteous servants.',
    refs: ['27:19'],
    context_ar: 'دعاء سليمان حين سمع كلام النملة وتبسّم',
    context_en: 'Sulaiman\'s prayer when he heard the ant\'s words and smiled'
  },
  {
    id: 36,
    ar: 'دعاء سليمان بالملك',
    en: 'Sulaiman\'s prayer for a kingdom',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ اغْفِرْ لِي وَهَبْ لِي مُلْكًا لَّا يَنبَغِي لِأَحَدٍ مِّن بَعْدِي ۖ إِنَّكَ أَنتَ الْوَهَّابُ',
    desc_en: 'My Lord, forgive me and grant me a kingdom such as will not belong to anyone after me. Indeed, You are the Bestower.',
    refs: ['38:35'],
    context_ar: 'دعاء سليمان ربه بعد أن فُتن بالجسد على كرسيه ثم تاب',
    context_en: 'Sulaiman\'s prayer after being tested and then turning back to God'
  },

  // ── Ayyub (أيوب) ──
  {
    id: 37,
    ar: 'دعاء أيوب في البلاء',
    en: 'Ayyub\'s prayer during affliction',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'أَنِّي مَسَّنِيَ الضُّرُّ وَأَنتَ أَرْحَمُ الرَّاحِمِينَ',
    desc_en: 'Indeed, adversity has touched me, and You are the Most Merciful of the merciful.',
    refs: ['21:83'],
    context_ar: 'دعاء أيوب حين أصابه المرض والبلاء الشديد',
    context_en: 'Ayyub\'s prayer during his severe illness and trial'
  },
  {
    id: 38,
    ar: 'دعاء أيوب بالشيطان',
    en: 'Ayyub\'s prayer regarding Satan\'s affliction',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'أَنِّي مَسَّنِيَ الشَّيْطَانُ بِنُصْبٍ وَعَذَابٍ',
    desc_en: 'Indeed, Satan has touched me with hardship and torment.',
    refs: ['38:41'],
    context_ar: 'نداء أيوب ربه يشكو ما أصابه من الشيطان',
    context_en: 'Ayyub crying out to God about the hardship Satan inflicted upon him'
  },

  // ── Yunus (يونس) / Dhun-Nun ──
  {
    id: 39,
    ar: 'دعاء يونس في بطن الحوت',
    en: 'Yunus\'s prayer inside the whale',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'لَّا إِلَٰهَ إِلَّا أَنتَ سُبْحَانَكَ إِنِّي كُنتُ مِنَ الظَّالِمِينَ',
    desc_en: 'There is no deity except You; exalted are You. Indeed, I have been of the wrongdoers.',
    refs: ['21:87'],
    context_ar: 'دعاء يونس (ذي النون) وهو في بطن الحوت في ظلمات ثلاث',
    context_en: 'Yunus (Dhun-Nun)\'s prayer while inside the whale in layers of darkness'
  },

  // ── Zakariya (زكريا) ──
  {
    id: 40,
    ar: 'دعاء زكريا بالذرية',
    en: 'Zakariya\'s prayer for offspring',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ لَا تَذَرْنِي فَرْدًا وَأَنتَ خَيْرُ الْوَارِثِينَ',
    desc_en: 'My Lord, do not leave me alone with no heir, and You are the best of inheritors.',
    refs: ['21:89'],
    context_ar: 'دعاء زكريا وهو شيخ كبير يطلب الولد',
    context_en: 'Zakariya\'s prayer in his old age asking God for a child'
  },
  {
    id: 41,
    ar: 'دعاء زكريا بالولي',
    en: 'Zakariya\'s prayer for an heir',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ هَبْ لِي مِن لَّدُنكَ ذُرِّيَّةً طَيِّبَةً ۖ إِنَّكَ سَمِيعُ الدُّعَاءِ',
    desc_en: 'My Lord, grant me from Yourself a good offspring. Indeed, You are the Hearer of supplication.',
    refs: ['3:38'],
    context_ar: 'دعاء زكريا بعد أن رأى رزق مريم في المحراب',
    context_en: 'Zakariya\'s prayer after he saw Maryam\'s miraculous provision in the sanctuary'
  },
  {
    id: 42,
    ar: 'نداء زكريا الخفي',
    en: 'Zakariya\'s secret call',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي وَهَنَ الْعَظْمُ مِنِّي وَاشْتَعَلَ الرَّأْسُ شَيْبًا وَلَمْ أَكُن بِدُعَائِكَ رَبِّ شَقِيًّا',
    desc_en: 'My Lord, indeed my bones have weakened, and my head has filled with white, and never have I been in my supplication to You, my Lord, unhappy.',
    refs: ['19:4'],
    context_ar: 'نداء زكريا ربه نداءً خفيًا وهو يشكو ضعف جسده وشيبه',
    context_en: 'Zakariya\'s secret call to God, lamenting his physical weakness and grey hair'
  },

  // ── Isa (عيسى) ──
  {
    id: 43,
    ar: 'دعاء عيسى بالمائدة',
    en: 'Isa\'s prayer for the Table',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'اللَّهُمَّ رَبَّنَا أَنزِلْ عَلَيْنَا مَائِدَةً مِّنَ السَّمَاءِ تَكُونُ لَنَا عِيدًا لِّأَوَّلِنَا وَآخِرِنَا وَآيَةً مِّنكَ ۖ وَارْزُقْنَا وَأَنتَ خَيْرُ الرَّازِقِينَ',
    desc_en: 'O Allah, our Lord, send down to us a table from the heaven to be for us a festival for the first of us and the last of us and a sign from You. And provide for us, and You are the best of providers.',
    refs: ['5:114'],
    context_ar: 'دعاء عيسى حين طلب الحواريون مائدة من السماء',
    context_en: 'Isa\'s prayer when the disciples asked for a table spread from heaven'
  },

  // ── Muhammad (محمد ﷺ) and instructions to the Prophet ──
  {
    id: 44,
    ar: 'دعاء طلب العلم',
    en: 'Prayer for increased knowledge',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَّبِّ زِدْنِي عِلْمًا',
    desc_en: 'My Lord, increase me in knowledge.',
    refs: ['20:114'],
    context_ar: 'أمر الله لنبيه محمد ﷺ أن يدعو بطلب المزيد من العلم',
    context_en: 'God\'s instruction to Prophet Muhammad to pray for increased knowledge'
  },
  {
    id: 45,
    ar: 'دعاء مُدخل الصدق',
    en: 'Prayer for a truthful entrance and exit',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَّبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ وَاجْعَل لِّي مِن لَّدُنكَ سُلْطَانًا نَّصِيرًا',
    desc_en: 'My Lord, cause me to enter a sound entrance and to exit a sound exit and grant me from Yourself a supporting authority.',
    refs: ['17:80'],
    context_ar: 'دعاء أُمر به النبي محمد ﷺ بأن يدخل ويخرج بصدق',
    context_en: 'Prayer instructed to Prophet Muhammad for a truthful entrance and exit'
  },

  // ── Ya\'qub (يعقوب) ──
  {
    id: 46,
    ar: 'شكوى يعقوب لله',
    en: 'Ya\'qub\'s complaint to God',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'إِنَّمَا أَشْكُو بَثِّي وَحُزْنِي إِلَى اللَّهِ وَأَعْلَمُ مِنَ اللَّهِ مَا لَا تَعْلَمُونَ',
    desc_en: 'I only complain of my suffering and my grief to Allah, and I know from Allah that which you do not know.',
    refs: ['12:86'],
    context_ar: 'يعقوب يشكو حزنه على يوسف إلى الله وحده',
    context_en: 'Ya\'qub expressing his grief over Yusuf to God alone'
  },
  {
    id: 47,
    ar: 'صبر يعقوب',
    en: 'Ya\'qub\'s patience',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'فَصَبْرٌ جَمِيلٌ ۖ وَاللَّهُ الْمُسْتَعَانُ عَلَىٰ مَا تَصِفُونَ',
    desc_en: 'So patience is most fitting. And Allah is the one sought for help against that which you describe.',
    refs: ['12:18'],
    context_ar: 'قول يعقوب حين أخبره أبناؤه بخبر يوسف',
    context_en: 'Ya\'qub\'s words when his sons told him about Yusuf'
  },
  {
    id: 48,
    ar: 'دعاء يعقوب بالفرج',
    en: 'Ya\'qub\'s prayer for relief',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'عَسَى اللَّهُ أَن يَأْتِيَنِي بِهِمْ جَمِيعًا ۚ إِنَّهُ هُوَ الْعَلِيمُ الْحَكِيمُ',
    desc_en: 'Perhaps Allah will bring them to me all together. Indeed, it is He who is the Knowing, the Wise.',
    refs: ['12:83'],
    context_ar: 'رجاء يعقوب في أن يجمع الله شمله بأبنائه يوسف وأخيه',
    context_en: 'Ya\'qub\'s hopeful prayer that God would reunite him with Yusuf and his brother'
  },

  // ── Hud (هود) ──
  {
    id: 49,
    ar: 'توكل هود على الله',
    en: 'Hud\'s reliance on God',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'إِنِّي تَوَكَّلْتُ عَلَى اللَّهِ رَبِّي وَرَبِّكُم ۚ مَّا مِن دَابَّةٍ إِلَّا هُوَ آخِذٌ بِنَاصِيَتِهَا ۚ إِنَّ رَبِّي عَلَىٰ صِرَاطٍ مُّسْتَقِيمٍ',
    desc_en: 'Indeed, I have relied upon Allah, my Lord and your Lord. There is no creature but that He holds its forelock. Indeed, my Lord is on a path that is straight.',
    refs: ['11:56'],
    context_ar: 'إعلان هود توكله على الله أمام قوم عاد',
    context_en: 'Hud\'s declaration of trust in God before the people of \'Aad'
  },

  // ── Dawud & Sulaiman ──
  {
    id: 50,
    ar: 'شكر داود وسليمان',
    en: 'Dawud and Sulaiman\'s gratitude',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي فَضَّلَنَا عَلَىٰ كَثِيرٍ مِّنْ عِبَادِهِ الْمُؤْمِنِينَ',
    desc_en: 'Praise to Allah, who has favored us over many of His believing servants.',
    refs: ['27:15'],
    context_ar: 'قول داود وسليمان حمدًا لله على ما أنعم عليهما',
    context_en: 'Dawud and Sulaiman praising God for the favors bestowed upon them'
  },

  // ═══════════════════════════════════════════════════════════════
  // BELIEVER DUAS - أدعية المؤمنين (Supplications of the Believers)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 51,
    ar: 'ربنا آتنا في الدنيا حسنة',
    en: 'Our Lord, give us good in this world and the Hereafter',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ',
    desc_en: 'Our Lord, give us in this world that which is good and in the Hereafter that which is good, and protect us from the punishment of the Fire.',
    refs: ['2:201'],
    context_ar: 'دعاء المؤمنين الذين يسألون خير الدنيا والآخرة',
    context_en: 'The believers\' prayer asking for the good of this life and the Hereafter'
  },
  {
    id: 52,
    ar: 'ربنا لا تؤاخذنا',
    en: 'Our Lord, do not hold us accountable',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تُؤَاخِذْنَا إِن نَّسِينَا أَوْ أَخْطَأْنَا ۚ رَبَّنَا وَلَا تَحْمِلْ عَلَيْنَا إِصْرًا كَمَا حَمَلْتَهُ عَلَى الَّذِينَ مِن قَبْلِنَا ۚ رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا ۚ أَنتَ مَوْلَانَا فَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, do not impose blame upon us if we forget or make a mistake. Our Lord, and lay not upon us a burden like that which You laid upon those before us. Our Lord, and burden us not with that which we have no ability to bear. And pardon us; and forgive us; and have mercy upon us. You are our protector, so give us victory over the disbelieving people.',
    refs: ['2:286'],
    context_ar: 'دعاء المؤمنين في ختام سورة البقرة',
    context_en: 'The great du\'a at the end of Surah Al-Baqarah'
  },
  {
    id: 53,
    ar: 'ربنا لا تزغ قلوبنا',
    en: 'Our Lord, let not our hearts deviate',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً ۚ إِنَّكَ أَنتَ الْوَهَّابُ',
    desc_en: 'Our Lord, let not our hearts deviate after You have guided us and grant us from Yourself mercy. Indeed, You are the Bestower.',
    refs: ['3:8'],
    context_ar: 'دعاء الراسخين في العلم بالثبات على الهداية',
    context_en: 'Prayer of those firm in knowledge, asking for steadfastness upon guidance'
  },
  {
    id: 54,
    ar: 'ربنا إننا آمنا',
    en: 'Our Lord, indeed we have believed',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا إِنَّنَا آمَنَّا فَاغْفِرْ لَنَا ذُنُوبَنَا وَقِنَا عَذَابَ النَّارِ',
    desc_en: 'Our Lord, indeed we have believed, so forgive us our sins and protect us from the punishment of the Fire.',
    refs: ['3:16'],
    context_ar: 'دعاء المؤمنين الصابرين الصادقين القانتين',
    context_en: 'Prayer of the patient, truthful, and devoutly obedient believers'
  },
  {
    id: 55,
    ar: 'ربنا آمنا فاكتبنا مع الشاهدين',
    en: 'Our Lord, we have believed, so register us among the witnesses',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آمَنَّا بِمَا أَنزَلْتَ وَاتَّبَعْنَا الرَّسُولَ فَاكْتُبْنَا مَعَ الشَّاهِدِينَ',
    desc_en: 'Our Lord, we have believed in what You revealed and have followed the messenger, so register us among the witnesses to the truth.',
    refs: ['3:53'],
    context_ar: 'دعاء الحواريين أتباع عيسى عليه السلام',
    context_en: 'Prayer of the disciples, followers of Isa (Jesus)'
  },
  {
    id: 56,
    ar: 'ربنا اغفر لنا ذنوبنا وإسرافنا',
    en: 'Our Lord, forgive us our sins and excesses',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا اغْفِرْ لَنَا ذُنُوبَنَا وَإِسْرَافَنَا فِي أَمْرِنَا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, forgive us our sins and the excess committed in our affairs and plant firmly our feet and give us victory over the disbelieving people.',
    refs: ['3:147'],
    context_ar: 'دعاء المؤمنين المجاهدين مع الأنبياء',
    context_en: 'Prayer of the believers who fought alongside the prophets'
  },
  {
    id: 57,
    ar: 'حسبنا الله ونعم الوكيل',
    en: 'Sufficient for us is Allah, and He is the best Disposer of affairs',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ',
    desc_en: 'Sufficient for us is Allah, and He is the best Disposer of affairs.',
    refs: ['3:173'],
    context_ar: 'قول المؤمنين حين خوّفهم الناس من جمع الأعداء',
    context_en: 'The believers\' response when people warned them that their enemies had gathered against them'
  },
  {
    id: 58,
    ar: 'ربنا ما خلقت هذا باطلا',
    en: 'Our Lord, You did not create this in vain',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا مَا خَلَقْتَ هَٰذَا بَاطِلًا سُبْحَانَكَ فَقِنَا عَذَابَ النَّارِ ۝ رَبَّنَا إِنَّكَ مَن تُدْخِلِ النَّارَ فَقَدْ أَخْزَيْتَهُ ۖ وَمَا لِلظَّالِمِينَ مِنْ أَنصَارٍ ۝ رَّبَّنَا إِنَّنَا سَمِعْنَا مُنَادِيًا يُنَادِي لِلْإِيمَانِ أَنْ آمِنُوا بِرَبِّكُمْ فَآمَنَّا ۚ رَبَّنَا فَاغْفِرْ لَنَا ذُنُوبَنَا وَكَفِّرْ عَنَّا سَيِّئَاتِنَا وَتَوَفَّنَا مَعَ الْأَبْرَارِ ۝ رَبَّنَا وَآتِنَا مَا وَعَدتَّنَا عَلَىٰ رُسُلِكَ وَلَا تُخْزِنَا يَوْمَ الْقِيَامَةِ ۗ إِنَّكَ لَا تُخْلِفُ الْمِيعَادَ',
    desc_en: 'Our Lord, You did not create this aimlessly; exalted are You, so protect us from the punishment of the Fire. Our Lord, indeed whoever You admit to the Fire - You have disgraced him, and for the wrongdoers there are no helpers. Our Lord, indeed we have heard a caller calling to faith saying "Believe in your Lord," and we have believed. Our Lord, so forgive us our sins and remove from us our misdeeds and cause us to die with the righteous. Our Lord, and grant us what You promised us through Your messengers and do not disgrace us on the Day of Resurrection. Indeed, You do not fail in Your promise.',
    refs: ['3:191-194'],
    context_ar: 'دعاء أولي الألباب الذين يتفكرون في خلق السماوات والأرض',
    context_en: 'Prayer of the people of understanding who reflect upon the creation of the heavens and earth'
  },
  {
    id: 59,
    ar: 'ربنا أفرغ علينا صبرا',
    en: 'Our Lord, pour upon us patience',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, pour upon us patience and plant firmly our feet and give us victory over the disbelieving people.',
    refs: ['2:250'],
    context_ar: 'دعاء جنود طالوت حين لقوا جالوت وجنوده',
    context_en: 'Prayer of Talut\'s soldiers when they faced Jalut (Goliath) and his army'
  },
  {
    id: 60,
    ar: 'ربنا لا تجعلنا فتنة للقوم الظالمين',
    en: 'Our Lord, make us not a trial for the wrongdoing people',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تَجْعَلْنَا فِتْنَةً لِّلْقَوْمِ الظَّالِمِينَ ۝ وَنَجِّنَا بِرَحْمَتِكَ مِنَ الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, make us not objects of trial for the wrongdoing people. And save us by Your mercy from the disbelieving people.',
    refs: ['10:85-86'],
    context_ar: 'دعاء مؤمني قوم موسى حين خافوا من فرعون',
    context_en: 'Prayer of the believers among Musa\'s people when they feared Pharaoh'
  },
  {
    id: 61,
    ar: 'ربنا اصرف عنا عذاب جهنم',
    en: 'Our Lord, avert from us the punishment of Hell',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا اصْرِفْ عَنَّا عَذَابَ جَهَنَّمَ ۖ إِنَّ عَذَابَهَا كَانَ غَرَامًا ۝ إِنَّهَا سَاءَتْ مُسْتَقَرًّا وَمُقَامًا',
    desc_en: 'Our Lord, avert from us the punishment of Hell. Indeed, its punishment is ever adhering. Indeed, it is evil as a settlement and residence.',
    refs: ['25:65-66'],
    context_ar: 'دعاء عباد الرحمن الذين يمشون على الأرض هونًا',
    context_en: 'Prayer of the servants of the Most Merciful who walk upon the earth humbly'
  },
  {
    id: 62,
    ar: 'دعاء عباد الرحمن بالذرية',
    en: 'Servants of the Most Merciful - prayer for family',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا',
    desc_en: 'Our Lord, grant us from among our spouses and offspring comfort to our eyes, and make us an example for the righteous.',
    refs: ['25:74'],
    context_ar: 'دعاء عباد الرحمن بأن تكون أسرهم قرة عين لهم',
    context_en: 'Prayer of the servants of the Most Merciful for their families to be a source of joy'
  },
  {
    id: 63,
    ar: 'ربنا أتمم لنا نورنا',
    en: 'Our Lord, perfect for us our light',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَتْمِمْ لَنَا نُورَنَا وَاغْفِرْ لَنَا ۖ إِنَّكَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ',
    desc_en: 'Our Lord, perfect for us our light and forgive us. Indeed, You are over all things competent.',
    refs: ['66:8'],
    context_ar: 'دعاء المؤمنين يوم القيامة حين يسعى نورهم بين أيديهم',
    context_en: 'Prayer of the believers on the Day of Resurrection when their light will be proceeding before them'
  },
  {
    id: 64,
    ar: 'ربنا اغفر لنا ولإخواننا',
    en: 'Our Lord, forgive us and our brothers',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا اغْفِرْ لَنَا وَلِإِخْوَانِنَا الَّذِينَ سَبَقُونَا بِالْإِيمَانِ وَلَا تَجْعَلْ فِي قُلُوبِنَا غِلًّا لِّلَّذِينَ آمَنُوا رَبَّنَا إِنَّكَ رَءُوفٌ رَّحِيمٌ',
    desc_en: 'Our Lord, forgive us and our brothers who preceded us in faith and put not in our hearts any resentment toward those who have believed. Our Lord, indeed You are Kind and Merciful.',
    refs: ['59:10'],
    context_ar: 'دعاء المؤمنين الذين يأتون بعد المهاجرين والأنصار',
    context_en: 'Prayer of the believers who came after the Emigrants and Helpers'
  },
  {
    id: 65,
    ar: 'ربنا عليك توكلنا',
    en: 'Our Lord, upon You we have relied',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا عَلَيْكَ تَوَكَّلْنَا وَإِلَيْكَ أَنَبْنَا وَإِلَيْكَ الْمَصِيرُ ۝ رَبَّنَا لَا تَجْعَلْنَا فِتْنَةً لِّلَّذِينَ كَفَرُوا وَاغْفِرْ لَنَا رَبَّنَا ۖ إِنَّكَ أَنتَ الْعَزِيزُ الْحَكِيمُ',
    desc_en: 'Our Lord, upon You we have relied, and to You we have returned, and to You is the destination. Our Lord, make us not objects of trial for the disbelievers and forgive us, our Lord. Indeed, it is You who is the Exalted in Might, the Wise.',
    refs: ['60:4-5'],
    context_ar: 'دعاء إبراهيم والذين معه حين تبرأوا من المشركين',
    context_en: 'Prayer of Ibrahim and those with him when they disassociated from the polytheists'
  },
  {
    id: 66,
    ar: 'سمعنا وأطعنا',
    en: 'We hear and we obey',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'سَمِعْنَا وَأَطَعْنَا ۖ غُفْرَانَكَ رَبَّنَا وَإِلَيْكَ الْمَصِيرُ',
    desc_en: 'We hear and we obey. We seek Your forgiveness, our Lord, and to You is the final destination.',
    refs: ['2:285'],
    context_ar: 'قول المؤمنين حين آمنوا بالله ورسله وكتبه وملائكته',
    context_en: 'The believers\' declaration of faith in God, His messengers, books, and angels'
  },
  {
    id: 67,
    ar: 'ربنا لا تجعلنا مع القوم الظالمين',
    en: 'Our Lord, put us not with the wrongdoing people',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تَجْعَلْنَا مَعَ الْقَوْمِ الظَّالِمِينَ',
    desc_en: 'Our Lord, put us not with the wrongdoing people.',
    refs: ['7:47'],
    context_ar: 'دعاء أصحاب الأعراف حين يرون أهل النار',
    context_en: 'Prayer of the people of the heights (Al-A\'raf) when they see the people of the Fire'
  },
  {
    id: 68,
    ar: 'ربنا أفرغ علينا صبرا وتوفنا مسلمين',
    en: 'Our Lord, pour upon us patience and let us die as Muslims',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَتَوَفَّنَا مُسْلِمِينَ',
    desc_en: 'Our Lord, pour upon us patience and let us die as Muslims in submission to You.',
    refs: ['7:126'],
    context_ar: 'دعاء سحرة فرعون بعد أن آمنوا بموسى',
    context_en: 'Prayer of Pharaoh\'s magicians after they believed in Musa'
  },
  {
    id: 69,
    ar: 'ربنا آمنا فاغفر لنا',
    en: 'Our Lord, we have believed, so forgive us',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آمَنَّا فَاغْفِرْ لَنَا وَارْحَمْنَا وَأَنتَ خَيْرُ الرَّاحِمِينَ',
    desc_en: 'Our Lord, we have believed, so forgive us and have mercy upon us, and You are the best of the merciful.',
    refs: ['23:109'],
    context_ar: 'دعاء عباد الله المؤمنين الذين كان الكافرون يسخرون منهم',
    context_en: 'Prayer of God\'s believing servants whom the disbelievers used to ridicule'
  },
  {
    id: 70,
    ar: 'ربنا إننا سمعنا مناديا',
    en: 'Our Lord, indeed we have heard a caller',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَّبَّنَا إِنَّنَا سَمِعْنَا مُنَادِيًا يُنَادِي لِلْإِيمَانِ أَنْ آمِنُوا بِرَبِّكُمْ فَآمَنَّا',
    desc_en: 'Our Lord, indeed we have heard a caller calling to faith saying "Believe in your Lord," and we have believed.',
    refs: ['3:193'],
    context_ar: 'دعاء أولي الألباب استجابةً لنداء الإيمان',
    context_en: 'Prayer of the people of understanding in response to the call of faith'
  },
  {
    id: 71,
    ar: 'ربنا ظلمنا أنفسنا',
    en: 'Our Lord, we have wronged ourselves (general believers)',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ',
    desc_en: 'Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.',
    refs: ['7:23'],
    context_ar: 'الدعاء الذي علّمه الله آدم وأصبح دعاء كل مذنب تائب',
    context_en: 'The prayer God taught Adam, which became the supplication of every repentant sinner'
  },
  {
    id: 72,
    ar: 'ربنا آتنا من لدنك رحمة',
    en: 'Our Lord, grant us from Yourself mercy',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا',
    desc_en: 'Our Lord, grant us from Yourself mercy and prepare for us from our affair right guidance.',
    refs: ['18:10'],
    context_ar: 'دعاء أصحاب الكهف حين لجأوا إلى الكهف',
    context_en: 'Prayer of the People of the Cave when they took refuge in the cave'
  },
  {
    id: 73,
    ar: 'ربنا آمنا بما أنزلت',
    en: 'Our Lord, we have believed in what You revealed',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آمَنَّا فَاكْتُبْنَا مَعَ الشَّاهِدِينَ',
    desc_en: 'Our Lord, we have believed, so register us among the witnesses.',
    refs: ['5:83'],
    context_ar: 'قول النصارى الذين آمنوا حين سمعوا القرآن',
    context_en: 'Words of the Christians who believed when they heard the Quran'
  },
  {
    id: 74,
    ar: 'ربنا أخرجنا من هذه القرية',
    en: 'Our Lord, take us out of this city',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَخْرِجْنَا مِنْ هَٰذِهِ الْقَرْيَةِ الظَّالِمِ أَهْلُهَا وَاجْعَل لَّنَا مِن لَّدُنكَ وَلِيًّا وَاجْعَل لَّنَا مِن لَّدُنكَ نَصِيرًا',
    desc_en: 'Our Lord, take us out of this city of oppressive people and appoint for us from Yourself a protector and appoint for us from Yourself a helper.',
    refs: ['4:75'],
    context_ar: 'دعاء المستضعفين في مكة من الرجال والنساء والأطفال',
    context_en: 'Prayer of the oppressed men, women, and children in Makkah'
  },

  // ═══════════════════════════════════════════════════════════════
  // PROTECTION DUAS - أدعية الاستعاذة (Seeking Refuge)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 75,
    ar: 'الاستعاذة برب الفلق',
    en: 'Seeking refuge with the Lord of daybreak',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ ۝ مِن شَرِّ مَا خَلَقَ ۝ وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ ۝ وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ ۝ وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ',
    desc_en: 'Say, "I seek refuge in the Lord of daybreak, from the evil of that which He created, and from the evil of darkness when it settles, and from the evil of the blowers in knots, and from the evil of an envier when he envies."',
    refs: ['113:1-5'],
    context_ar: 'سورة الفلق كاملة - للاستعاذة من الشرور',
    context_en: 'The entire Surah Al-Falaq - seeking refuge from all forms of evil'
  },
  {
    id: 76,
    ar: 'الاستعاذة برب الناس',
    en: 'Seeking refuge with the Lord of mankind',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'قُلْ أَعُوذُ بِرَبِّ النَّاسِ ۝ مَلِكِ النَّاسِ ۝ إِلَٰهِ النَّاسِ ۝ مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ ۝ الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ ۝ مِنَ الْجِنَّةِ وَالنَّاسِ',
    desc_en: 'Say, "I seek refuge in the Lord of mankind, the Sovereign of mankind, the God of mankind, from the evil of the retreating whisperer - who whispers in the breasts of mankind - from among the jinn and mankind."',
    refs: ['114:1-6'],
    context_ar: 'سورة الناس كاملة - للاستعاذة من الوسوسة',
    context_en: 'The entire Surah An-Nas - seeking refuge from the evil whisperer'
  },
  {
    id: 77,
    ar: 'الاستعاذة من همزات الشياطين',
    en: 'Seeking refuge from the proddings of the devils',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'رَبِّ أَعُوذُ بِكَ مِنْ هَمَزَاتِ الشَّيَاطِينِ ۝ وَأَعُوذُ بِكَ رَبِّ أَن يَحْضُرُونِ',
    desc_en: 'My Lord, I seek refuge in You from the incitements of the devils. And I seek refuge in You, my Lord, lest they be present with me.',
    refs: ['23:97-98'],
    context_ar: 'أمر الله بالاستعاذة من وساوس الشياطين وحضورهم',
    context_en: 'God\'s command to seek refuge from the devils\' incitement and their presence'
  },
  {
    id: 78,
    ar: 'الاستعاذة من الشيطان الرجيم',
    en: 'Seeking refuge from Satan the accursed',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'أَعُوذُ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ',
    desc_en: 'I seek refuge in Allah from Satan the accursed.',
    refs: ['16:98'],
    context_ar: 'أمر الله بالاستعاذة من الشيطان عند قراءة القرآن',
    context_en: 'God\'s command to seek refuge from Satan when reciting the Quran'
  },
  {
    id: 79,
    ar: 'دعاء مريم عليها السلام',
    en: 'Maryam\'s seeking of refuge',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'إِنِّي أَعُوذُ بِالرَّحْمَٰنِ مِنكَ إِن كُنتَ تَقِيًّا',
    desc_en: 'Indeed, I seek refuge in the Most Merciful from you, if you should be fearing of God.',
    refs: ['19:18'],
    context_ar: 'استعاذة مريم بالرحمن حين ظهر لها جبريل في صورة بشر',
    context_en: 'Maryam seeking refuge in the Most Merciful when Jibril appeared to her in human form'
  },

  // ═══════════════════════════════════════════════════════════════
  // FORGIVENESS DUAS - أدعية المغفرة (Seeking Forgiveness)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 80,
    ar: 'ربنا اغفر لنا وارحمنا',
    en: 'Our Lord, forgive us and have mercy on us',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'رَبَّنَا اغْفِرْ لَنَا وَارْحَمْنَا وَأَنتَ خَيْرُ الرَّاحِمِينَ',
    desc_en: 'Our Lord, forgive us and have mercy upon us, and You are the best of the merciful.',
    refs: ['23:118'],
    context_ar: 'أمر الله بالدعاء بالمغفرة والرحمة',
    context_en: 'God\'s command to pray for forgiveness and mercy'
  },
  {
    id: 81,
    ar: 'رب اغفر وارحم وأنت خير الراحمين',
    en: 'My Lord, forgive and have mercy, and You are the best of the merciful',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'رَّبِّ اغْفِرْ وَارْحَمْ وَأَنتَ خَيْرُ الرَّاحِمِينَ',
    desc_en: 'My Lord, forgive and have mercy, and You are the best of the merciful.',
    refs: ['23:118'],
    context_ar: 'أمر من الله تعالى بهذا الدعاء في ختام سورة المؤمنون',
    context_en: 'A divine command to make this supplication at the end of Surah Al-Mu\'minun'
  },
  {
    id: 82,
    ar: 'دعاء الاستغفار العام',
    en: 'General prayer for forgiveness',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'وَاسْتَغْفِرِ اللَّهَ ۖ إِنَّ اللَّهَ كَانَ غَفُورًا رَّحِيمًا',
    desc_en: 'And seek forgiveness of Allah. Indeed, Allah is ever Forgiving and Merciful.',
    refs: ['4:106'],
    context_ar: 'أمر الله بالاستغفار في جميع الأحوال',
    context_en: 'God\'s command to seek forgiveness at all times'
  },
  {
    id: 83,
    ar: 'استغفار الأسحار',
    en: 'Seeking forgiveness at dawn',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'وَبِالْأَسْحَارِ هُمْ يَسْتَغْفِرُونَ',
    desc_en: 'And in the hours before dawn they would ask forgiveness.',
    refs: ['51:18'],
    context_ar: 'صفة المتقين الذين يستغفرون الله في وقت السحر',
    context_en: 'The quality of the God-conscious who seek forgiveness in the pre-dawn hours'
  },
  {
    id: 84,
    ar: 'دعاء استغفار الذنب',
    en: 'Prayer after committing a sin',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'رَبَّنَا ظَلَمْنَا أَنفُسَنَا وَإِن لَّمْ تَغْفِرْ لَنَا وَتَرْحَمْنَا لَنَكُونَنَّ مِنَ الْخَاسِرِينَ',
    desc_en: 'Our Lord, we have wronged ourselves, and if You do not forgive us and have mercy upon us, we will surely be among the losers.',
    refs: ['7:23'],
    context_ar: 'الدعاء الذي يُقال بعد ارتكاب ذنب، كما فعل آدم وحواء',
    context_en: 'The supplication to be said after committing a sin, as Adam and Eve did'
  },
  {
    id: 85,
    ar: 'ذكر الله واستغفار الذنوب',
    en: 'Remembering God and seeking forgiveness for sins',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'وَالَّذِينَ إِذَا فَعَلُوا فَاحِشَةً أَوْ ظَلَمُوا أَنفُسَهُمْ ذَكَرُوا اللَّهَ فَاسْتَغْفَرُوا لِذُنُوبِهِمْ وَمَن يَغْفِرُ الذُّنُوبَ إِلَّا اللَّهُ',
    desc_en: 'And those who, when they commit an immorality or wrong themselves, remember Allah and seek forgiveness for their sins - and who can forgive sins except Allah?',
    refs: ['3:135'],
    context_ar: 'صفة المؤمنين الذين يسارعون إلى الاستغفار بعد الذنب',
    context_en: 'Quality of the believers who hasten to seek forgiveness after sinning'
  },

  // ═══════════════════════════════════════════════════════════════
  // GUIDANCE DUAS - أدعية الهداية (Seeking Guidance)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 86,
    ar: 'اهدنا الصراط المستقيم',
    en: 'Guide us to the straight path',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ ۝ صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ',
    desc_en: 'Guide us to the straight path - the path of those upon whom You have bestowed favor, not of those who have earned Your anger or of those who are astray.',
    refs: ['1:6-7'],
    context_ar: 'الدعاء الأعظم في سورة الفاتحة الذي يُقرأ في كل صلاة',
    context_en: 'The greatest du\'a in Surah Al-Fatihah, recited in every prayer'
  },
  {
    id: 87,
    ar: 'ربنا لا تزغ قلوبنا',
    en: 'Our Lord, let not our hearts deviate',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً ۚ إِنَّكَ أَنتَ الْوَهَّابُ',
    desc_en: 'Our Lord, let not our hearts deviate after You have guided us and grant us from Yourself mercy. Indeed, You are the Bestower.',
    refs: ['3:8'],
    context_ar: 'دعاء الراسخين في العلم بأن يثبتهم الله على الهداية',
    context_en: 'Prayer of those firm in knowledge asking God for steadfastness'
  },
  {
    id: 88,
    ar: 'دعاء طلب الهداية والسداد',
    en: 'Prayer for guidance and righteousness',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا',
    desc_en: 'Our Lord, grant us from Yourself mercy and prepare for us from our affair right guidance.',
    refs: ['18:10'],
    context_ar: 'دعاء أصحاب الكهف حين أووا إلى الكهف فرارًا بدينهم',
    context_en: 'Prayer of the People of the Cave when they took refuge fleeing for their faith'
  },
  {
    id: 89,
    ar: 'رب أوزعني أن أشكر نعمتك',
    en: 'My Lord, enable me to be grateful',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبِّ أَوْزِعْنِي أَنْ أَشْكُرَ نِعْمَتَكَ الَّتِي أَنْعَمْتَ عَلَيَّ وَعَلَىٰ وَالِدَيَّ وَأَنْ أَعْمَلَ صَالِحًا تَرْضَاهُ وَأَصْلِحْ لِي فِي ذُرِّيَّتِي ۖ إِنِّي تُبْتُ إِلَيْكَ وَإِنِّي مِنَ الْمُسْلِمِينَ',
    desc_en: 'My Lord, enable me to be grateful for Your favor which You have bestowed upon me and upon my parents, and to work righteousness of which You approve. And make righteous for me my offspring. Indeed, I have repented to You, and indeed, I am of the Muslims.',
    refs: ['46:15'],
    context_ar: 'دعاء الإنسان حين يبلغ أربعين سنة ويشكر الله على نعمه',
    context_en: 'Prayer of a person upon reaching forty years of age, thanking God for His blessings'
  },

  // ═══════════════════════════════════════════════════════════════
  // PROVISION DUAS - أدعية الرزق والنعم (Provision and Blessings)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 90,
    ar: 'ربنا آتنا في الدنيا حسنة',
    en: 'Our Lord, give us good in this world',
    cat: 'provision',
    cat_ar: 'أَدْعِيَةُ الرِّزْقِ وَالنِّعَمِ',
    desc_ar: 'رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ',
    desc_en: 'Our Lord, give us in this world that which is good and in the Hereafter that which is good, and protect us from the punishment of the Fire.',
    refs: ['2:201'],
    context_ar: 'دعاء جامع يطلب خير الدنيا والآخرة معًا',
    context_en: 'A comprehensive du\'a asking for the good of both this life and the Hereafter'
  },
  {
    id: 91,
    ar: 'دعاء إبراهيم لأهل مكة بالرزق',
    en: 'Ibrahim\'s prayer for Makkah\'s provision',
    cat: 'provision',
    cat_ar: 'أَدْعِيَةُ الرِّزْقِ وَالنِّعَمِ',
    desc_ar: 'رَبِّ اجْعَلْ هَٰذَا بَلَدًا آمِنًا وَارْزُقْ أَهْلَهُ مِنَ الثَّمَرَاتِ مَنْ آمَنَ مِنْهُم بِاللَّهِ وَالْيَوْمِ الْآخِرِ',
    desc_en: 'My Lord, make this a secure city and provide its people with fruits - whoever of them believes in Allah and the Last Day.',
    refs: ['2:126'],
    context_ar: 'دعاء إبراهيم بالأمن والرزق لأهل مكة المؤمنين',
    context_en: 'Ibrahim\'s prayer for security and provision for the believing people of Makkah'
  },
  {
    id: 92,
    ar: 'دعاء طلب الذرية الطيبة',
    en: 'Prayer for righteous offspring',
    cat: 'provision',
    cat_ar: 'أَدْعِيَةُ الرِّزْقِ وَالنِّعَمِ',
    desc_ar: 'رَبِّ هَبْ لِي مِن لَّدُنكَ ذُرِّيَّةً طَيِّبَةً ۖ إِنَّكَ سَمِيعُ الدُّعَاءِ',
    desc_en: 'My Lord, grant me from Yourself a good offspring. Indeed, You are the Hearer of supplication.',
    refs: ['3:38'],
    context_ar: 'دعاء زكريا بعد رؤية كرامات مريم في المحراب',
    context_en: 'Zakariya\'s prayer after witnessing Maryam\'s miraculous provisions'
  },
  {
    id: 93,
    ar: 'دعاء طلب الأزواج والذرية',
    en: 'Prayer for spouses and children as a comfort',
    cat: 'provision',
    cat_ar: 'أَدْعِيَةُ الرِّزْقِ وَالنِّعَمِ',
    desc_ar: 'رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا',
    desc_en: 'Our Lord, grant us from among our spouses and offspring comfort to our eyes, and make us an example for the righteous.',
    refs: ['25:74'],
    context_ar: 'دعاء عباد الرحمن بأن تكون أسرهم قرة عين',
    context_en: 'Prayer of the servants of the Most Merciful for their families to bring them joy'
  },

  // ═══════════════════════════════════════════════════════════════
  // PRAISE DUAS - أدعية الحمد والثناء (Praise and Glorification)
  // ═══════════════════════════════════════════════════════════════
  {
    id: 94,
    ar: 'الحمد لله رب العالمين',
    en: 'All praise belongs to God, Lord of all worlds',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ۝ الرَّحْمَٰنِ الرَّحِيمِ ۝ مَالِكِ يَوْمِ الدِّينِ',
    desc_en: 'All praise is due to Allah, Lord of the worlds - the Entirely Merciful, the Especially Merciful - Sovereign of the Day of Recompense.',
    refs: ['1:2-4'],
    context_ar: 'افتتاحية القرآن الكريم بحمد الله وثنائه',
    context_en: 'The opening of the Noble Quran with praise and glorification of God'
  },
  {
    id: 95,
    ar: 'إياك نعبد وإياك نستعين',
    en: 'You alone we worship, You alone we ask for help',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ',
    desc_en: 'It is You we worship and You we ask for help.',
    refs: ['1:5'],
    context_ar: 'إعلان التوحيد والعبودية الخالصة لله في الفاتحة',
    context_en: 'Declaration of monotheism and exclusive worship of God in Al-Fatihah'
  },
  {
    id: 96,
    ar: 'سبحانك لا علم لنا',
    en: 'Exalted are You; we have no knowledge',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'سُبْحَانَكَ لَا عِلْمَ لَنَا إِلَّا مَا عَلَّمْتَنَا ۖ إِنَّكَ أَنتَ الْعَلِيمُ الْحَكِيمُ',
    desc_en: 'Exalted are You; we have no knowledge except what You have taught us. Indeed, it is You who is the Knowing, the Wise.',
    refs: ['2:32'],
    context_ar: 'قول الملائكة لله حين سألهم عن أسماء الأشياء',
    context_en: 'The angels\' response to God when He asked them about the names of things'
  },
  {
    id: 97,
    ar: 'لا إله إلا أنت سبحانك',
    en: 'There is no deity except You; exalted are You',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'لَّا إِلَٰهَ إِلَّا أَنتَ سُبْحَانَكَ إِنِّي كُنتُ مِنَ الظَّالِمِينَ',
    desc_en: 'There is no deity except You; exalted are You. Indeed, I have been of the wrongdoers.',
    refs: ['21:87'],
    context_ar: 'تسبيح يونس في بطن الحوت - أعظم أدعية الكرب',
    context_en: 'Yunus\'s glorification inside the whale - one of the greatest prayers in distress'
  },
  {
    id: 98,
    ar: 'آية الكرسي',
    en: 'The Verse of the Throne (Ayat Al-Kursi)',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ',
    desc_en: 'Allah - there is no deity except Him, the Ever-Living, the Sustainer of existence. Neither drowsiness overtakes Him nor sleep. To Him belongs whatever is in the heavens and whatever is on the earth. Who is it that can intercede with Him except by His permission? He knows what is before them and what will be after them, and they encompass not a thing of His knowledge except for what He wills. His Kursi extends over the heavens and the earth, and their preservation tires Him not. And He is the Most High, the Most Great.',
    refs: ['2:255'],
    context_ar: 'آية الكرسي - أعظم آية في القرآن للحفظ والثناء على الله',
    context_en: 'Ayat Al-Kursi - the greatest verse in the Quran, praising God\'s sovereignty'
  },
  {
    id: 99,
    ar: 'سورة الإخلاص',
    en: 'Surah Al-Ikhlas (Sincerity)',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'قُلْ هُوَ اللَّهُ أَحَدٌ ۝ اللَّهُ الصَّمَدُ ۝ لَمْ يَلِدْ وَلَمْ يُولَدْ ۝ وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ',
    desc_en: 'Say, "He is Allah, the One. Allah, the Eternal Refuge. He neither begets nor is born. Nor is there to Him any equivalent."',
    refs: ['112:1-4'],
    context_ar: 'سورة الإخلاص - تعدل ثلث القرآن في التوحيد وتمجيد الله',
    context_en: 'Surah Al-Ikhlas - equivalent to one-third of the Quran in declaring God\'s oneness'
  },
  {
    id: 100,
    ar: 'تسبيح الملائكة',
    en: 'Glorification of the angels',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'رَبَّنَا وَسِعْتَ كُلَّ شَيْءٍ رَّحْمَةً وَعِلْمًا فَاغْفِرْ لِلَّذِينَ تَابُوا وَاتَّبَعُوا سَبِيلَكَ وَقِهِمْ عَذَابَ الْجَحِيمِ',
    desc_en: 'Our Lord, You have encompassed all things in mercy and knowledge, so forgive those who have repented and followed Your way and protect them from the punishment of Hellfire.',
    refs: ['40:7'],
    context_ar: 'دعاء الملائكة حملة العرش للمؤمنين التائبين',
    context_en: 'Prayer of the angels who bear the Throne for the repentant believers'
  },
  {
    id: 101,
    ar: 'دعاء الملائكة بالجنة للمؤمنين',
    en: 'Angels\' prayer for believers to enter Paradise',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'رَبَّنَا وَأَدْخِلْهُمْ جَنَّاتِ عَدْنٍ الَّتِي وَعَدتَّهُمْ وَمَن صَلَحَ مِنْ آبَائِهِمْ وَأَزْوَاجِهِمْ وَذُرِّيَّاتِهِمْ ۚ إِنَّكَ أَنتَ الْعَزِيزُ الْحَكِيمُ ۝ وَقِهِمُ السَّيِّئَاتِ ۚ وَمَن تَقِ السَّيِّئَاتِ يَوْمَئِذٍ فَقَدْ رَحِمْتَهُ ۚ وَذَٰلِكَ هُوَ الْفَوْزُ الْعَظِيمُ',
    desc_en: 'Our Lord, and admit them to gardens of perpetual residence which You have promised them and whoever was righteous among their fathers, their spouses, and their offspring. Indeed, it is You who is the Exalted in Might, the Wise. And protect them from the evil consequences of their deeds. And he whom You protect from evil consequences that Day - You will have given him mercy. And that is the great attainment.',
    refs: ['40:8-9'],
    context_ar: 'تتمة دعاء الملائكة حملة العرش بإدخال المؤمنين وأهلهم الجنة',
    context_en: 'Continuation of the Throne-bearing angels\' prayer for believers and their families to enter Paradise'
  },
  {
    id: 102,
    ar: 'الحمد لله الذي هدانا',
    en: 'Praise to Allah who has guided us',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي هَدَانَا لِهَٰذَا وَمَا كُنَّا لِنَهْتَدِيَ لَوْلَا أَنْ هَدَانَا اللَّهُ',
    desc_en: 'Praise to Allah, who has guided us to this; and we would never have been guided if Allah had not guided us.',
    refs: ['7:43'],
    context_ar: 'قول أهل الجنة حمدًا لله على أن هداهم',
    context_en: 'Words of the people of Paradise praising God for guiding them'
  },
  {
    id: 103,
    ar: 'الحمد لله الذي صدقنا وعده',
    en: 'Praise to Allah who has fulfilled His promise',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي صَدَقَنَا وَعْدَهُ وَأَوْرَثَنَا الْأَرْضَ نَتَبَوَّأُ مِنَ الْجَنَّةِ حَيْثُ نَشَاءُ ۖ فَنِعْمَ أَجْرُ الْعَامِلِينَ',
    desc_en: 'Praise to Allah, who has fulfilled for us His promise and made us inherit the earth so we may settle in Paradise wherever we will. And excellent is the reward of those who work.',
    refs: ['39:74'],
    context_ar: 'قول المؤمنين حين يدخلون الجنة',
    context_en: 'Words of the believers when they enter Paradise'
  },
  {
    id: 104,
    ar: 'الحمد لله الذي أذهب عنا الحزن',
    en: 'Praise to Allah who has removed from us sorrow',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي أَذْهَبَ عَنَّا الْحَزَنَ ۖ إِنَّ رَبَّنَا لَغَفُورٌ شَكُورٌ',
    desc_en: 'Praise to Allah, who has removed from us all sorrow. Indeed, our Lord is Forgiving and Appreciative.',
    refs: ['35:34'],
    context_ar: 'قول أهل الجنة حين يدخلونها ويذهب عنهم كل حزن',
    context_en: 'Words of the people of Paradise when all sorrow is removed from them'
  },

  // ═══════════════════════════════════════════════════════════════
  // ADDITIONAL COMPREHENSIVE DUAS
  // ═══════════════════════════════════════════════════════════════

  // ── More Prophet Duas ──
  {
    id: 105,
    ar: 'دعاء إبراهيم بأن لا يخزيه يوم البعث',
    en: 'Ibrahim\'s prayer not to be disgraced on Resurrection Day',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'وَلَا تُخْزِنِي يَوْمَ يُبْعَثُونَ ۝ يَوْمَ لَا يَنفَعُ مَالٌ وَلَا بَنُونَ ۝ إِلَّا مَنْ أَتَى اللَّهَ بِقَلْبٍ سَلِيمٍ',
    desc_en: 'And do not disgrace me on the Day they are all resurrected - the Day when there will not benefit anyone wealth or children, but only one who comes to Allah with a sound heart.',
    refs: ['26:87-89'],
    context_ar: 'دعاء إبراهيم بأن لا يُخزى يوم القيامة',
    context_en: 'Ibrahim\'s prayer asking not to be humiliated on the Day of Resurrection'
  },
  {
    id: 106,
    ar: 'دعاء موسى بالتوبة',
    en: 'Musa\'s prayer of repentance',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبِّ إِنِّي ظَلَمْتُ نَفْسِي فَاغْفِرْ لِي فَغَفَرَ لَهُ ۚ إِنَّهُ هُوَ الْغَفُورُ الرَّحِيمُ',
    desc_en: 'My Lord, indeed I have wronged myself, so forgive me, and He forgave him. Indeed, He is the Forgiving, the Merciful.',
    refs: ['28:16'],
    context_ar: 'دعاء موسى بعد قتل القبطي وتوبته إلى الله',
    context_en: 'Musa\'s prayer and immediate repentance after killing the Egyptian'
  },
  {
    id: 107,
    ar: 'دعاء موسى بالمعية والتأييد',
    en: 'Musa\'s declaration of God\'s support',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'كَلَّا ۖ إِنَّ مَعِيَ رَبِّي سَيَهْدِينِ',
    desc_en: 'No! Indeed, with me is my Lord; He will guide me.',
    refs: ['26:62'],
    context_ar: 'قول موسى لأصحابه حين رأوا البحر أمامهم وفرعون خلفهم',
    context_en: 'Musa\'s words to his companions when they saw the sea before them and Pharaoh behind them'
  },

  // ── More Believer Duas ──
  {
    id: 108,
    ar: 'دعاء المؤمنين في البلاء',
    en: 'Believers\' prayer during calamity',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'إِنَّا لِلَّهِ وَإِنَّا إِلَيْهِ رَاجِعُونَ',
    desc_en: 'Indeed we belong to Allah, and indeed to Him we will return.',
    refs: ['2:156'],
    context_ar: 'قول الصابرين حين تصيبهم مصيبة',
    context_en: 'Words of the patient ones when affliction strikes them'
  },
  {
    id: 109,
    ar: 'ربنا لا تؤاخذنا إن نسينا',
    en: 'Our Lord, do not blame us if we forget',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تُؤَاخِذْنَا إِن نَّسِينَا أَوْ أَخْطَأْنَا',
    desc_en: 'Our Lord, do not impose blame upon us if we have forgotten or erred.',
    refs: ['2:286'],
    context_ar: 'بداية الدعاء العظيم في ختام سورة البقرة',
    context_en: 'The opening of the great supplication at the end of Surah Al-Baqarah'
  },
  {
    id: 110,
    ar: 'على الله توكلنا',
    en: 'Upon Allah we have relied',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا لَا تَجْعَلْنَا فِتْنَةً لِّلْقَوْمِ الظَّالِمِينَ',
    desc_en: 'Our Lord, make us not a trial for the wrongdoing people.',
    refs: ['10:85'],
    context_ar: 'قول قوم موسى المؤمنين حين توكلوا على الله ضد فرعون',
    context_en: 'Words of the believing followers of Musa when they relied on God against Pharaoh'
  },
  {
    id: 111,
    ar: 'ربنا لا تحملنا ما لا طاقة لنا به',
    en: 'Our Lord, burden us not with what we cannot bear',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا وَلَا تُحَمِّلْنَا مَا لَا طَاقَةَ لَنَا بِهِ ۖ وَاعْفُ عَنَّا وَاغْفِرْ لَنَا وَارْحَمْنَا ۚ أَنتَ مَوْلَانَا فَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, and burden us not with that which we have no ability to bear. And pardon us; and forgive us; and have mercy upon us. You are our protector, so give us victory over the disbelieving people.',
    refs: ['2:286'],
    context_ar: 'الجزء الأخير من الدعاء العظيم في ختام سورة البقرة',
    context_en: 'The final part of the great supplication at the end of Surah Al-Baqarah'
  },
  {
    id: 112,
    ar: 'دعاء ركوب الدابة',
    en: 'Prayer upon mounting a ride',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'سُبْحَانَ الَّذِي سَخَّرَ لَنَا هَٰذَا وَمَا كُنَّا لَهُ مُقْرِنِينَ ۝ وَإِنَّا إِلَىٰ رَبِّنَا لَمُنقَلِبُونَ',
    desc_en: 'Exalted is He who has subjected this to us, and we could not have otherwise subdued it. And indeed we, to our Lord, will surely return.',
    refs: ['43:13-14'],
    context_ar: 'ذكر الله عند ركوب وسائل النقل',
    context_en: 'Remembrance of God when riding means of transportation'
  },
  {
    id: 113,
    ar: 'دعاء مؤمن آل فرعون',
    en: 'Prayer of the believing man from Pharaoh\'s family',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'وَأُفَوِّضُ أَمْرِي إِلَى اللَّهِ ۚ إِنَّ اللَّهَ بَصِيرٌ بِالْعِبَادِ',
    desc_en: 'And I entrust my affair to Allah. Indeed, Allah is Seeing of His servants.',
    refs: ['40:44'],
    context_ar: 'قول المؤمن من آل فرعون حين فوّض أمره إلى الله',
    context_en: 'The believing man from Pharaoh\'s family entrusting his affair to God'
  },
  {
    id: 114,
    ar: 'دعاء أصحاب الكهف عند الاستيقاظ',
    en: 'People of the Cave - after waking up',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا آتِنَا مِن لَّدُنكَ رَحْمَةً وَهَيِّئْ لَنَا مِنْ أَمْرِنَا رَشَدًا',
    desc_en: 'Our Lord, grant us from Yourself mercy and prepare for us from our affair right guidance.',
    refs: ['18:10'],
    context_ar: 'دعاء الفتية المؤمنين حين آووا إلى الكهف هربًا بدينهم',
    context_en: 'Prayer of the believing youth when they sought refuge in the cave to preserve their faith'
  },

  // ── Additional Quranic Instructions to Pray ──
  {
    id: 115,
    ar: 'دعاء المظلوم',
    en: 'Prayer for relief from oppression',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَخْرِجْنَا مِنْ هَٰذِهِ الْقَرْيَةِ الظَّالِمِ أَهْلُهَا وَاجْعَل لَّنَا مِن لَّدُنكَ وَلِيًّا وَاجْعَل لَّنَا مِن لَّدُنكَ نَصِيرًا',
    desc_en: 'Our Lord, take us out of this city of oppressive people and appoint for us from Yourself a protector and appoint for us from Yourself a helper.',
    refs: ['4:75'],
    context_ar: 'صرخة المستضعفين من الرجال والنساء والولدان',
    context_en: 'The cry of the oppressed men, women, and children'
  },
  {
    id: 116,
    ar: 'دعاء دخول المدينة',
    en: 'Prayer when entering a place',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبِّ أَدْخِلْنِي مُدْخَلَ صِدْقٍ وَأَخْرِجْنِي مُخْرَجَ صِدْقٍ وَاجْعَل لِّي مِن لَّدُنكَ سُلْطَانًا نَّصِيرًا',
    desc_en: 'My Lord, cause me to enter a sound entrance and to exit a sound exit and grant me from Yourself a supporting authority.',
    refs: ['17:80'],
    context_ar: 'دعاء يقال عند الدخول والخروج من أي مكان',
    context_en: 'A prayer to be said when entering and exiting any place'
  },
  {
    id: 117,
    ar: 'دعاء الوالدين',
    en: 'Prayer for parents',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَّبِّ ارْحَمْهُمَا كَمَا رَبَّيَانِي صَغِيرًا',
    desc_en: 'My Lord, have mercy upon them as they brought me up when I was small.',
    refs: ['17:24'],
    context_ar: 'دعاء البر بالوالدين والرحمة لهما',
    context_en: 'Prayer of filial piety and mercy for one\'s parents'
  },
  {
    id: 118,
    ar: 'رب لا تذرني فردا',
    en: 'My Lord, do not leave me alone',
    cat: 'provision',
    cat_ar: 'أَدْعِيَةُ الرِّزْقِ وَالنِّعَمِ',
    desc_ar: 'رَبِّ لَا تَذَرْنِي فَرْدًا وَأَنتَ خَيْرُ الْوَارِثِينَ',
    desc_en: 'My Lord, do not leave me alone with no heir, and You are the best of inheritors.',
    refs: ['21:89'],
    context_ar: 'دعاء زكريا بأن يرزقه الله الذرية',
    context_en: 'Zakariya\'s prayer for God to grant him offspring'
  },
  {
    id: 119,
    ar: 'دعاء الاستفتاح بالحق',
    en: 'Prayer for judgment with truth',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبِّ احْكُم بِالْحَقِّ ۗ وَرَبُّنَا الرَّحْمَٰنُ الْمُسْتَعَانُ عَلَىٰ مَا تَصِفُونَ',
    desc_en: 'My Lord, judge in truth. And our Lord is the Most Merciful, the one whose help is sought against that which you describe.',
    refs: ['21:112'],
    context_ar: 'أمر النبي ﷺ بأن يطلب من الله الحكم بالحق',
    context_en: 'The Prophet instructed to ask God to judge in truth'
  },
  {
    id: 120,
    ar: 'دعاء البركة عند النزول',
    en: 'Prayer for a blessed landing',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبِّ أَنزِلْنِي مُنزَلًا مُّبَارَكًا وَأَنتَ خَيْرُ الْمُنزِلِينَ',
    desc_en: 'My Lord, let me land at a blessed landing place, and You are the best to accommodate us.',
    refs: ['23:29'],
    context_ar: 'دعاء يقال عند النزول في مكان جديد طلبًا للبركة',
    context_en: 'Prayer to be said when arriving at a new place, seeking blessings'
  },

  // ── Ibrahim\'s additional duas ──
  {
    id: 121,
    ar: 'شكر إبراهيم على الولد في الكبر',
    en: 'Ibrahim\'s gratitude for children in old age',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي وَهَبَ لِي عَلَى الْكِبَرِ إِسْمَاعِيلَ وَإِسْحَاقَ ۚ إِنَّ رَبِّي لَسَمِيعُ الدُّعَاءِ',
    desc_en: 'Praise to Allah, who has granted to me in old age Ismail and Ishaq. Indeed, my Lord is the Hearer of supplication.',
    refs: ['14:39'],
    context_ar: 'حمد إبراهيم لله أن رزقه إسماعيل وإسحاق في شيخوخته',
    context_en: 'Ibrahim praising God for granting him Ismail and Ishaq in his old age'
  },

  // ── Dawud (داود) ──
  {
    id: 122,
    ar: 'دعاء جنود طالوت',
    en: 'Prayer of Talut\'s soldiers',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, pour upon us patience and plant firmly our feet and give us victory over the disbelieving people.',
    refs: ['2:250'],
    context_ar: 'دعاء جنود طالوت وفيهم داود حين واجهوا جالوت',
    context_en: 'Prayer of Talut\'s army, including Dawud, when facing Jalut (Goliath)'
  },

  // ── Isma\'il and Ibrahim together ──
  {
    id: 123,
    ar: 'دعاء إبراهيم بصون ذريته عن الأصنام',
    en: 'Ibrahim\'s prayer to protect descendants from idols',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'وَاجْنُبْنِي وَبَنِيَّ أَن نَّعْبُدَ الْأَصْنَامَ',
    desc_en: 'And keep me and my sons away from worshipping idols.',
    refs: ['14:35'],
    context_ar: 'جزء من دعاء إبراهيم حين أسكن ذريته بوادٍ غير ذي زرع',
    context_en: 'Part of Ibrahim\'s prayer when he settled his family in an uncultivated valley'
  },

  // ── Salih ──
  {
    id: 124,
    ar: 'تحذير صالح لقومه',
    en: 'Salih\'s warning to his people',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'يَا قَوْمِ لَقَدْ أَبْلَغْتُكُمْ رِسَالَةَ رَبِّي وَنَصَحْتُ لَكُمْ وَلَٰكِن لَّا تُحِبُّونَ النَّاصِحِينَ',
    desc_en: 'O my people, I had certainly conveyed to you the message of my Lord and advised you, but you do not like advisors.',
    refs: ['7:79'],
    context_ar: 'قول صالح لقومه ثمود بعد هلاكهم',
    context_en: 'Salih\'s words to his people Thamud after their destruction'
  },

  // ── Additional Guidance/Forgiveness ──
  {
    id: 125,
    ar: 'دعاء طلب العفو',
    en: 'Prayer seeking pardon',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'رَبَّنَا فَاغْفِرْ لَنَا ذُنُوبَنَا وَكَفِّرْ عَنَّا سَيِّئَاتِنَا وَتَوَفَّنَا مَعَ الْأَبْرَارِ',
    desc_en: 'Our Lord, so forgive us our sins and remove from us our misdeeds and cause us to die with the righteous.',
    refs: ['3:193'],
    context_ar: 'دعاء أولي الألباب بالمغفرة والموت مع الأبرار',
    context_en: 'Prayer of the people of understanding for forgiveness and dying among the righteous'
  },
  {
    id: 126,
    ar: 'دعاء التوبة النصوح',
    en: 'Prayer of sincere repentance',
    cat: 'forgiveness',
    cat_ar: 'أَدْعِيَةُ المَغْفِرَةِ',
    desc_ar: 'رَبَّنَا أَتْمِمْ لَنَا نُورَنَا وَاغْفِرْ لَنَا ۖ إِنَّكَ عَلَىٰ كُلِّ شَيْءٍ قَدِيرٌ',
    desc_en: 'Our Lord, perfect for us our light and forgive us. Indeed, You are over all things competent.',
    refs: ['66:8'],
    context_ar: 'دعاء المؤمنين يوم القيامة بعد التوبة النصوح',
    context_en: 'Prayer of the believers on Judgment Day following sincere repentance'
  },

  // ── More Quranic duas from various surahs ──
  {
    id: 127,
    ar: 'دعاء المسافر والغريب',
    en: 'Prayer of the traveler and stranger',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبِّ إِنِّي لِمَا أَنزَلْتَ إِلَيَّ مِنْ خَيْرٍ فَقِيرٌ',
    desc_en: 'My Lord, indeed I am, for whatever good You would send down to me, in need.',
    refs: ['28:24'],
    context_ar: 'دعاء كل محتاج وغريب يطلب من الله الخير',
    context_en: 'Prayer of every person in need, asking God for any good He would bestow'
  },
  {
    id: 128,
    ar: 'دعاء امرأة فرعون',
    en: 'Prayer of Pharaoh\'s wife (Asiyah)',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبِّ ابْنِ لِي عِندَكَ بَيْتًا فِي الْجَنَّةِ وَنَجِّنِي مِن فِرْعَوْنَ وَعَمَلِهِ وَنَجِّنِي مِنَ الْقَوْمِ الظَّالِمِينَ',
    desc_en: 'My Lord, build for me near You a house in Paradise and save me from Pharaoh and his deeds and save me from the wrongdoing people.',
    refs: ['66:11'],
    context_ar: 'دعاء آسية امرأة فرعون - ضُرب بها مثل للمؤمنين',
    context_en: 'Prayer of Asiyah, Pharaoh\'s wife - set as an example for the believers'
  },
  {
    id: 129,
    ar: 'دعاء السحرة بعد الإيمان',
    en: 'Prayer of Pharaoh\'s magicians after believing',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا أَفْرِغْ عَلَيْنَا صَبْرًا وَتَوَفَّنَا مُسْلِمِينَ',
    desc_en: 'Our Lord, pour upon us patience and let us die as Muslims.',
    refs: ['7:126'],
    context_ar: 'دعاء سحرة فرعون بعد أن آمنوا برب موسى وهارون',
    context_en: 'Prayer of Pharaoh\'s magicians after believing in the Lord of Musa and Harun'
  },
  {
    id: 130,
    ar: 'دعاء السحرة بالمغفرة',
    en: 'Magicians\' prayer for forgiveness',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'إِنَّا نَطْمَعُ أَن يَغْفِرَ لَنَا رَبُّنَا خَطَايَانَا أَن كُنَّا أَوَّلَ الْمُؤْمِنِينَ',
    desc_en: 'Indeed, we aspire that our Lord will forgive us our sins because we were the first of the believers.',
    refs: ['26:51'],
    context_ar: 'طمع سحرة فرعون في مغفرة الله لأنهم أول من آمن',
    context_en: 'The magicians hoping for forgiveness as they were the first to believe'
  },
  {
    id: 131,
    ar: 'لا حول ولا قوة إلا بالله',
    en: 'There is no power except with God',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'مَا شَاءَ اللَّهُ لَا قُوَّةَ إِلَّا بِاللَّهِ',
    desc_en: 'What Allah willed has occurred; there is no power except in Allah.',
    refs: ['18:39'],
    context_ar: 'نصيحة المؤمن لصاحب الجنتين بأن يعترف بقدرة الله',
    context_en: 'The believer\'s advice to the owner of two gardens to acknowledge God\'s power'
  },
  {
    id: 132,
    ar: 'توكل النبي',
    en: 'The Prophet\'s reliance on God',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'حَسْبِيَ اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ ۖ عَلَيْهِ تَوَكَّلْتُ ۖ وَهُوَ رَبُّ الْعَرْشِ الْعَظِيمِ',
    desc_en: 'Sufficient for me is Allah; there is no deity except Him. On Him I have relied, and He is the Lord of the Great Throne.',
    refs: ['9:129'],
    context_ar: 'توجيه النبي ﷺ بالتوكل على الله وحده',
    context_en: 'The Prophet directed to rely solely on God'
  },
  {
    id: 133,
    ar: 'دعاء الخروج من القبر',
    en: 'Supplication upon awakening from death',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'يَا وَيْلَنَا مَن بَعَثَنَا مِن مَّرْقَدِنَا ۜ ۗ هَٰذَا مَا وَعَدَ الرَّحْمَٰنُ وَصَدَقَ الْمُرْسَلُونَ',
    desc_en: 'Oh, woe to us! Who has raised us up from our sleeping place? This is what the Most Merciful had promised, and the messengers told the truth.',
    refs: ['36:52'],
    context_ar: 'قول الناس عند البعث يوم القيامة',
    context_en: 'Words spoken upon resurrection on the Day of Judgment'
  },
  {
    id: 134,
    ar: 'دعاء الدخول في الإسلام',
    en: 'Prayer of entering Islam',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبَّنَا آمَنَّا فَاكْتُبْنَا مَعَ الشَّاهِدِينَ',
    desc_en: 'Our Lord, we have believed, so register us among the witnesses.',
    refs: ['5:83'],
    context_ar: 'دعاء من دخلوا الإسلام بعد سماع القرآن',
    context_en: 'Prayer of those who embraced Islam after hearing the Quran'
  },
  {
    id: 135,
    ar: 'دعاء ختام سورة آل عمران',
    en: 'Supplication at the end of Surah Aal-Imran',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا وَآتِنَا مَا وَعَدتَّنَا عَلَىٰ رُسُلِكَ وَلَا تُخْزِنَا يَوْمَ الْقِيَامَةِ ۗ إِنَّكَ لَا تُخْلِفُ الْمِيعَادَ',
    desc_en: 'Our Lord, and grant us what You promised us through Your messengers and do not disgrace us on the Day of Resurrection. Indeed, You do not fail in Your promise.',
    refs: ['3:194'],
    context_ar: 'ختام سلسلة أدعية أولي الألباب في سورة آل عمران',
    context_en: 'The concluding du\'a of the people of understanding in Surah Aal-Imran'
  },
  {
    id: 136,
    ar: 'تسبيح الرعد',
    en: 'Glorification of thunder',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'سُبْحَانَكَ اللَّهُمَّ وَبِحَمْدِكَ',
    desc_en: 'Exalted are You, O Allah, and praised.',
    refs: ['13:13'],
    context_ar: 'الرعد يسبح بحمد الله والملائكة من خيفته',
    context_en: 'The thunder glorifies God with His praise, and so do the angels from fear of Him'
  },

  // ── Additional famous Quranic supplications ──
  {
    id: 137,
    ar: 'دعاء طلب الثبات',
    en: 'Prayer for steadfastness',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبَّنَا اغْفِرْ لَنَا ذُنُوبَنَا وَإِسْرَافَنَا فِي أَمْرِنَا وَثَبِّتْ أَقْدَامَنَا وَانصُرْنَا عَلَى الْقَوْمِ الْكَافِرِينَ',
    desc_en: 'Our Lord, forgive us our sins and the excess committed in our affairs and plant firmly our feet and give us victory over the disbelieving people.',
    refs: ['3:147'],
    context_ar: 'دعاء المؤمنين المقاتلين طلبًا للثبات والنصر',
    context_en: 'Prayer of the fighting believers seeking steadfastness and victory'
  },
  {
    id: 138,
    ar: 'دعاء النبي ﷺ عند الشدائد',
    en: 'Prophet\'s prayer during hardship',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ',
    desc_en: 'Sufficient for us is Allah, and He is the best Disposer of affairs.',
    refs: ['3:173'],
    context_ar: 'قالها النبي ﷺ والمؤمنون حين قيل لهم إن الناس قد جمعوا لكم',
    context_en: 'Said by the Prophet and believers when told that people had gathered forces against them'
  },
  {
    id: 139,
    ar: 'دعاء الصبر على الموت',
    en: 'Prayer of patience in the face of death',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'إِنَّا لِلَّهِ وَإِنَّا إِلَيْهِ رَاجِعُونَ',
    desc_en: 'Indeed we belong to Allah, and indeed to Him we will return.',
    refs: ['2:156'],
    context_ar: 'ذكر الله عند المصيبة والموت - جزاؤهم صلوات من ربهم ورحمة',
    context_en: 'Remembrance of God upon calamity and death - rewarded with blessings and mercy from their Lord'
  },
  {
    id: 140,
    ar: 'لا إله إلا الله',
    en: 'There is no deity except Allah',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'لَا إِلَٰهَ إِلَّا اللَّهُ وَحْدَهُ',
    desc_en: 'There is no deity except Allah alone.',
    refs: ['37:35', '47:19'],
    context_ar: 'كلمة التوحيد - أساس الدين والدعاء',
    context_en: 'The declaration of monotheism - the foundation of faith and supplication'
  },
  {
    id: 141,
    ar: 'دعاء النبي بالنصر',
    en: 'The Prophet\'s prayer for victory',
    cat: 'prophet',
    cat_ar: 'أَدْعِيَةُ الأَنْبِيَاءِ',
    desc_ar: 'رَبَّنَا افْتَحْ بَيْنَنَا وَبَيْنَ قَوْمِنَا بِالْحَقِّ وَأَنتَ خَيْرُ الْفَاتِحِينَ',
    desc_en: 'Our Lord, decide between us and our people in truth, and You are the best of those who give decision.',
    refs: ['7:89'],
    context_ar: 'طلب الحكم بالحق بين المؤمنين والكافرين',
    context_en: 'Asking for God\'s true judgment between the believers and disbelievers'
  },
  {
    id: 142,
    ar: 'دعاء السلامة من النار',
    en: 'Prayer for safety from the Fire',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'رَبَّنَا اصْرِفْ عَنَّا عَذَابَ جَهَنَّمَ ۖ إِنَّ عَذَابَهَا كَانَ غَرَامًا',
    desc_en: 'Our Lord, avert from us the punishment of Hell. Indeed, its punishment is ever adhering.',
    refs: ['25:65'],
    context_ar: 'دعاء عباد الرحمن بالنجاة من عذاب جهنم',
    context_en: 'Prayer of the servants of the Most Merciful for salvation from Hellfire'
  },
  {
    id: 143,
    ar: 'دعاء حسن الخاتمة',
    en: 'Prayer for a good ending',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'تَوَفَّنِي مُسْلِمًا وَأَلْحِقْنِي بِالصَّالِحِينَ',
    desc_en: 'Cause me to die a Muslim and join me with the righteous.',
    refs: ['12:101'],
    context_ar: 'جزء من دعاء يوسف بحسن الخاتمة والموت على الإسلام',
    context_en: 'Part of Yusuf\'s prayer for a good ending and dying upon Islam'
  },
  {
    id: 144,
    ar: 'دعاء عدم التكليف فوق الوسع',
    en: 'God does not burden a soul beyond its capacity',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا',
    desc_en: 'Allah does not charge a soul except with that within its capacity.',
    refs: ['2:286'],
    context_ar: 'تمهيد الدعاء العظيم في آخر البقرة بأن الله لا يكلف نفسًا فوق طاقتها',
    context_en: 'Preamble to the great supplication at the end of Al-Baqarah: God does not overburden a soul'
  },
  {
    id: 145,
    ar: 'دعاء الاستعاذة من عذاب القبر',
    en: 'Seeking refuge from the punishment of the grave',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'رَبِّ أَعُوذُ بِكَ مِنْ هَمَزَاتِ الشَّيَاطِينِ',
    desc_en: 'My Lord, I seek refuge in You from the incitements of the devils.',
    refs: ['23:97'],
    context_ar: 'الاستعاذة بالله من كل شر في الحياة وبعد الممات',
    context_en: 'Seeking God\'s refuge from all evil in life and after death'
  },
  {
    id: 146,
    ar: 'دعاء شكر النعمة',
    en: 'Prayer of gratitude for blessings',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'الْحَمْدُ لِلَّهِ الَّذِي فَضَّلَنَا عَلَىٰ كَثِيرٍ مِّنْ عِبَادِهِ الْمُؤْمِنِينَ',
    desc_en: 'Praise to Allah, who has favored us over many of His believing servants.',
    refs: ['27:15'],
    context_ar: 'شكر داود وسليمان لله على ما منحهم من العلم والملك',
    context_en: 'Dawud and Sulaiman\'s gratitude for the knowledge and kingdom God granted them'
  },

  // ── Final comprehensive additions ──
  {
    id: 147,
    ar: 'دعاء الحاج والمعتمر',
    en: 'Pilgrim\'s prayer',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'رَبَّنَا تَقَبَّلْ مِنَّا ۖ إِنَّكَ أَنتَ السَّمِيعُ الْعَلِيمُ',
    desc_en: 'Our Lord, accept this from us. Indeed, You are the All-Hearing, the All-Knowing.',
    refs: ['2:127'],
    context_ar: 'يُقال أثناء أداء مناسك الحج والعمرة طلبًا للقبول',
    context_en: 'Recited during Hajj and Umrah rituals, asking for acceptance'
  },
  {
    id: 148,
    ar: 'دعاء عباد الرحمن بالصلاح',
    en: 'Servants of the Most Merciful - complete supplication',
    cat: 'believer',
    cat_ar: 'أَدْعِيَةُ المُؤْمِنِينَ',
    desc_ar: 'وَالَّذِينَ يَقُولُونَ رَبَّنَا هَبْ لَنَا مِنْ أَزْوَاجِنَا وَذُرِّيَّاتِنَا قُرَّةَ أَعْيُنٍ وَاجْعَلْنَا لِلْمُتَّقِينَ إِمَامًا',
    desc_en: 'And those who say, "Our Lord, grant us from among our spouses and offspring comfort to our eyes and make us an example for the righteous."',
    refs: ['25:74'],
    context_ar: 'الدعاء الأخير في صفات عباد الرحمن في سورة الفرقان',
    context_en: 'The closing supplication in the description of the servants of the Most Merciful in Surah Al-Furqan'
  },
  {
    id: 149,
    ar: 'رب أعوذ بك من الخبث',
    en: 'Seeking refuge from evil',
    cat: 'protection',
    cat_ar: 'أَدْعِيَةُ الاسْتِعَاذَةِ',
    desc_ar: 'فَإِذَا قَرَأْتَ الْقُرْآنَ فَاسْتَعِذْ بِاللَّهِ مِنَ الشَّيْطَانِ الرَّجِيمِ',
    desc_en: 'So when you recite the Quran, seek refuge in Allah from Satan, the expelled.',
    refs: ['16:98'],
    context_ar: 'أمر إلهي بالاستعاذة من الشيطان عند تلاوة القرآن',
    context_en: 'Divine command to seek refuge from Satan before reciting the Quran'
  },
  {
    id: 150,
    ar: 'دعاء أولي الألباب',
    en: 'Prayer of the people of deep understanding',
    cat: 'guidance',
    cat_ar: 'أَدْعِيَةُ الهِدَايَةِ',
    desc_ar: 'رَبَّنَا مَا خَلَقْتَ هَٰذَا بَاطِلًا سُبْحَانَكَ فَقِنَا عَذَابَ النَّارِ',
    desc_en: 'Our Lord, You did not create this aimlessly; exalted are You above such a thing, then protect us from the punishment of the Fire.',
    refs: ['3:191'],
    context_ar: 'تأمل أولي الألباب في خلق السماوات والأرض',
    context_en: 'The reflection of the people of understanding upon the creation of the heavens and the earth'
  },
  {
    id: 151,
    ar: 'تسبيح الله رب العزة',
    en: 'Glorification of God, Lord of Might',
    cat: 'praise',
    cat_ar: 'أَدْعِيَةُ الحَمْدِ وَالثَّنَاءِ',
    desc_ar: 'سُبْحَانَ رَبِّكَ رَبِّ الْعِزَّةِ عَمَّا يَصِفُونَ ۝ وَسَلَامٌ عَلَى الْمُرْسَلِينَ ۝ وَالْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ',
    desc_en: 'Exalted is your Lord, the Lord of Might, above what they describe. And peace upon the messengers. And praise to Allah, Lord of the worlds.',
    refs: ['37:180', '37:181', '37:182'],
    context_ar: 'خاتمة سورة الصافات - تنزيه الله عن كل نقص وسلام على الأنبياء وحمد لله رب العالمين',
    context_en: 'Closing verses of Surah As-Saffat - glorifying God above all imperfection, sending peace upon the messengers, and praising the Lord of all worlds'
  }
];
