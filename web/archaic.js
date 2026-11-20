// The old English of the site's translation, made plain. Pickthall's English (1930) is the English of the King James
// Bible: thou and ye, hath and doth, lo and verily, knoweth and seest. A reader who taps such a word sees what it
// means today and its Arabic, which is often the very word in the verse (Lo = إنّ, Bethink you = أرأيتم).
// Pickthall also gives a few modern words a sense of his own: doom for عذاب, those who ward off (evil) for المتّقون,
// save for إلّا. Those are here too.
// Used by the Reader, the study panel and Search in app.html, loaded with the translation. Also loaded by the Node
// tests in data-build/tests.
//
// GLOSS: an old word, or a word in Pickthall's own sense: [today's English, Arabic, a note in English, a note in Arabic].
// ETH and EST: the old verb forms of the translation and the verb each comes from, found in the translation itself
// and checked by hand: knoweth is knows, and thou seest is you see.
(function (root) {
  'use strict';

  const GLOSS = {
    // talking to one person (thou) and to many (ye)
    thou: ['you (to one person)', 'أنتَ'],
    thee: ['you (to one person, as in "to thee")', 'ـكَ، إيّاكَ'],
    thy: ['your (one person\'s)', 'ـكَ (ربُّكَ، كتابُكَ)'],
    thine: ['yours; your', 'لكَ، ـكَ'],
    ye: ['you (more than one person)', 'أنتم'],
    // old forms of be, have, do and the rest
    art: ['are, with thou ("thou art" = you are)', 'تكون؛ «Thou art» = أنتَ', 'Once, in 21:80, it is today\'s "art", a skill.', 'ومرةً واحدة، في ٢١:٨٠، هي بمعناها اليوم: الصنعة.'],
    wast: ['were, with thou ("thou wast" = you were)', 'كنتَ'],
    wert: ['were, with thou', 'كنتَ'],
    hath: ['has ("He hath made" = He has made)', 'قد (hath sent = قد أرسل)، له'],
    hast: ['have, with thou ("thou hast" = you have)', 'قد، لكَ'],
    doth: ['does', 'يفعل'],
    dost: ['do, with thou ("dost thou" = do you)', 'تفعل؛ وفي السؤال: هل'],
    didst: ['did, with thou', 'فعلتَ'],
    wilt: ['will, with thou', 'سـ، سوف؛ أو تريد'],
    shalt: ['shall, will, with thou', 'سوف'],
    canst: ['can, with thou', 'تستطيع'],
    saith: ['says', 'يقول'],
    spake: ['spoke', 'تكلّم، قال'],
    smite: ['strike', 'اضرب، يضرب'],
    smote: ['struck', 'ضرب'],
    slay: ['kill', 'اقتل، يقتل'],
    slew: ['killed', 'قتل'],
    begotten: ['fathered', 'وَلَد'],
    hearken: ['listen', 'استمع، أنصت'],
    beseech: ['beg, ask earnestly', 'أرجو، أتوسّل'],
    behold: ['look, see; also a call to notice what follows', 'انظر؛ وإذ'],
    bethink: ['think, consider ("Bethink you" = think about it, tell me)', 'تأمّلوا؛ «Bethink you» = أرأيتم'],
    // little words of stress, place and time
    lo: ['Look! Mark this! Pickthall\'s usual word for the Arabic inna, which stresses what follows', 'إنّ (للتوكيد)'],
    verily: ['truly, surely', 'إنّ، لقد'],
    nay: ['no; rather', 'كلّا، بل'],
    yea: ['yes; indeed', 'نعم، بلى'],
    aught: ['anything', 'شيء، أيّ شيء'],
    naught: ['nothing', 'لا شيء'],
    nought: ['nothing', 'لا شيء'],
    ere: ['before', 'قبل أن'],
    lest: ['so that not; for fear that', 'لئلّا، خشيةَ أن'],
    unto: ['to', 'إلى، لـ'],
    betwixt: ['between', 'بين'],
    twain: ['two', 'اثنان'],
    haply: ['perhaps ("that haply ye may" = so that you may)', 'لعلّ'],
    peradventure: ['perhaps', 'لعلّ، ربّما'],
    perchance: ['perhaps', 'لعلّ'],
    whence: ['from where', 'من أين'],
    whither: ['to where', 'إلى أين'],
    hither: ['here, to this place', 'إلى هنا'],
    thither: ['there, to that place', 'إلى هناك'],
    hence: ['from here; from now', 'من هنا'],
    thence: ['from there', 'من هناك، منها'],
    yonder: ['over there; that', 'هناك، ذلك'],
    hitherto: ['until now', 'حتى الآن'],
    heretofore: ['before now', 'من قبل'],
    aforetime: ['before, in earlier times', 'من قبل'],
    henceforth: ['from now on', 'من الآن'],
    wherein: ['in which', 'فيه، التي فيها'],
    whereof: ['of which, about which', 'منه، الذي عنه'],
    whereby: ['by which', 'به، الذي به'],
    wherewith: ['with which', 'به، الذي به'],
    wherewithal: ['the means, what is needed (often money)', 'ما يُنفَق، القدرة'],
    whereupon: ['and then, upon that', 'فعندئذٍ'],
    thereof: ['of it', 'منه'],
    therein: ['in it', 'فيه، فيها'],
    thereto: ['to it ("averse thereto" = against it)', 'له، إليه'],
    thereby: ['by that, through it', 'به، بذلك'],
    therefrom: ['from it', 'منه'],
    therewith: ['with it', 'به، معه'],
    thereupon: ['then, at that', 'عندئذٍ'],
    thereat: ['at that', 'عند ذلك'],
    whoso: ['whoever', 'مَن'],
    whosoever: ['whoever', 'مَن'],
    whatsoever: ['whatever', 'ما، أيّ شيء'],
    // words in Pickthall's own sense
    doom: ['punishment, torment (Pickthall\'s usual word for the Arabic adhab)', 'عذاب'],
    ward: ['keep off; "those who ward off (evil)" are the God-fearing, al-muttaqun', 'اتّقى؛ المتّقون'],
    save: ['except (as in "all save Iblis")', 'إلّا، سوى'],
    portent: ['a sign, a wonder (often for the Arabic aya)', 'آية'],
    beneficent: ['the most gracious, ar-Rahman', 'الرحمن'],
    bounty: ['grace, generosity (for the Arabic fadl)', 'فضل'],
    hereafter: ['the life after death', 'الآخرة'],
    bondmen: ['servants, slaves (for the Arabic ibad)', 'عباد'],
    bondman: ['servant, slave', 'عبد'],
    bondwoman: ['slave woman', 'أَمَة'],
    tidings: ['news ("glad tidings" = good news)', 'بُشرى، نبأ'],
    // old words for everyday things
    abide: ['stay, live; "abiding therein" = staying there forever', 'خالدين، مقيمين'],
    abiding: ['staying (forever)', 'خالدين، مقيمين'],
    abode: ['home, dwelling', 'دار، مأوى'],
    nigh: ['near', 'قريب، دنا'],
    kinsfolk: ['relatives', 'الأقارب'],
    kinsman: ['relative', 'قريب، ذو قربى'],
    kinsmen: ['relatives', 'الأقارب'],
    brethren: ['brothers', 'إخوة، إخوان'],
    countenance: ['face', 'وجه'],
    raiment: ['clothing', 'لباس، ثياب'],
    kine: ['cows, cattle', 'بقرات'],
    suckle: ['breastfeed', 'أرضع'],
    suckling: ['a nursing baby', 'رضيع'],
    sojourn: ['stay for a while', 'لبث، أقام'],
    tarry: ['stay, wait', 'لبث، مكث'],
    tarried: ['stayed', 'لبث، مكث'],
    surety: ['guarantee, guarantor', 'كفيل، ضمان'],
    asunder: ['apart, into pieces', 'منفصلين، متفرّقين'],
    manifold: ['many times over', 'أضعافًا'],
    // doing good and doing wrong, reward and punishment
    averse: ['unwilling, against it', 'كارهون، كاره'],
    wont: ['used to ("were wont to" = used to)', 'اعتاد؛ كانوا يفعلون'],
    fain: ['gladly; would like to', 'يودّ'],
    wroth: ['very angry', 'غاضب'],
    fie: ['shame! (an old cry of disgust)', 'أفّ'],
    woe: ['great sorrow ("woe unto" = ruin to)', 'ويل'],
    woeful: ['terrible, sad', 'سيّئ، بئيس'],
    abase: ['humble, bring low', 'أذلّ، خفض'],
    abased: ['brought low, humbled', 'ذليل'],
    abasement: ['humiliation', 'ذلّة'],
    ignominy: ['public shame, disgrace', 'خزي'],
    guile: ['deceit, cunning', 'مكر، كيد'],
    beguile: ['deceive, mislead', 'غرّ، خدع'],
    beguiled: ['deceived, misled', 'غرّه، خدعه'],
    froward: ['stubbornly disobedient', 'عاتٍ، معاند'],
    wanton: ['reckless, unrestrained', 'مسرف، طاغٍ'],
    iniquity: ['great wrong, sin', 'إثم، ظلم'],
    forsake: ['leave, abandon', 'ترك، هجر'],
    forsaken: ['abandoned', 'متروك'],
    bewitched: ['under a spell', 'مسحور'],
    vex: ['annoy, trouble', 'أزعج، آذى'],
    heed: ['attention ("take heed" = be careful)', 'انتباه، حذر'],
    heedless: ['not paying attention', 'غافل'],
    chastise: ['punish', 'عذّب، عاقب'],
    chastisement: ['punishment', 'عذاب'],
    requite: ['repay, reward or punish in return', 'جازى، يجزي'],
    requital: ['repayment, reward or punishment', 'جزاء'],
    recompense: ['reward, repayment', 'جزاء'],
    guerdon: ['reward', 'أجر'],
    mete: ['give out (a punishment)', 'أوقع'],
    meted: ['given out', 'أُوقع'],
    bestow: ['give', 'منح، أعطى'],
    bestowed: ['given', 'أعطى، آتى'],
    vouchsafe: ['grant, as a favour', 'تفضّل بـ، منح'],
    succour: ['help, rescue', 'نصر، عون'],
    bounteous: ['generous', 'كريم'],
    ordain: ['decree, prescribe', 'كتب، شرع'],
    ordained: ['decreed, prescribed', 'كُتب، شُرع'],
    behest: ['command', 'أمر'],
    gainsay: ['deny, contradict', 'أنكر، ردّ'],
    forbear: ['hold back', 'كفّ، أمسك'],
    amiss: ['wrong', 'خطأ'],
    sorely: ['badly, greatly', 'شديدًا'],
    wax: ['grow, become', 'ازداد'],
    wrought: ['made, did', 'صنع، عمل'],
    // old verb forms that also need their meaning
    quicken: ['give life to', 'أحيا'],
    quickeneth: ['gives life to', 'يحيي'],
    straiteneth: ['restricts, gives sparingly', 'يقدِر، يضيّق'],
    sufficeth: ['is enough', 'يكفي'],
    availeth: ['is of use, helps', 'يُغني، ينفع'],
    befalleth: ['happens to', 'يصيب'],
    aileth: ['troubles ("what aileth thee" = what is the matter with you)', 'ما لكَ؟'],
  };
  // so common that underlining them would mark every line: they open their card all the same
  const QUIET = new Set(['thou', 'thee', 'thy', 'ye', 'unto', 'hath', 'verily', 'art', 'hast', 'doth']);

  // the old verb forms of the translation: -eth (knoweth, goeth) and, with thou, -est (seest, broughtest)
  const ETH = {
    abateth:'abate', abolisheth:'abolish', aboundeth:'abound', accepteth:'accept', accounteth:'account', addeth:'add',
    admonisheth:'admonish', afflicteth:'afflict', agreeth:'agree', aileth:'ail', alloweth:'allow', altereth:'alter',
    amendeth:'amend', angereth:'anger', announceth:'announce', answereth:'answer', appertaineth:'appertain',
    appointeth:'appoint', approacheth:'approach', ariseth:'arise', ascendeth:'ascend', ascribeth:'ascribe',
    asketh:'ask', attacketh:'attack', attaineth:'attain', attendeth:'attend', availeth:'avail', averteth:'avert',
    awaiteth:'await', beareth:'bear', becometh:'become', befalleth:'befall', befitteth:'befit', befooleth:'befool',
    befriendeth:'befriend', begetteth:'beget', beguileth:'beguile', beholdeth:'behold', belieth:'belie',
    believeth:'believe', belongeth:'belong', benefiteth:'benefit', bestoweth:'bestow', biddeth:'bid', bindeth:'bind',
    blesseth:'bless', bloweth:'blow', bodeth:'bode', boileth:'boil', breaketh:'break', bringeth:'bring',
    burieth:'bury', burneth:'burn', calleth:'call', calmeth:'calm', carrieth:'carry', casteth:'cast', causeth:'cause',
    ceaseth:'cease', changeth:'change', chargeth:'charge', chastiseth:'chastise', choketh:'choke', chooseth:'choose',
    citeth:'cite', coineth:'coin', cometh:'come', commandeth:'command', committeth:'commit', complaineth:'complain',
    comprehendeth:'comprehend', confirmeth:'confirm', constraineth:'constrain', containeth:'contain',
    contenteth:'content', continueth:'continue', covereth:'cover', coveteth:'covet', craveth:'crave',
    createth:'create', crieth:'cry', curseth:'curse', darkeneth:'darken', deafeneth:'deafen', debarreth:'debar',
    deceiveth:'deceive', decreeth:'decree', deemeth:'deem', defameth:'defame', defendeth:'defend', delayeth:'delay',
    delivereth:'deliver', denieth:'deny', departeth:'depart', dependeth:'depend', derideth:'deride',
    descendeth:'descend', desireth:'desire', despaireth:'despair', despiseth:'despise', destroyeth:'destroy',
    detaileth:'detail', devastateth:'devastate', deviseth:'devise', dieth:'die', directeth:'direct',
    disbelieveth:'disbelieve', disdaineth:'disdain', dismisseth:'dismiss', disobeyeth:'disobey', dispelleth:'dispel',
    disposeth:'dispose', disputeth:'dispute', dissuadeth:'dissuade', distracteth:'distract', doeth:'do',
    doometh:'doom', draweth:'draw', dreadeth:'dread', drieth:'dry', drinketh:'drink', driveth:'drive',
    dwelleth:'dwell', earneth:'earn', eateth:'eat', effaceth:'efface', embezzleth:'embezzle', embraceth:'embrace',
    emergeth:'emerge', encloseth:'enclose', encompasseth:'encompass', endureth:'endure', enjoineth:'enjoin',
    enlargeth:'enlarge', enricheth:'enrich', enshroudeth:'enshroud', entereth:'enter', entrusteth:'entrust',
    envieth:'envy', erreth:'err', escapeth:'escape', establisheth:'establish', exerciseth:'exercise',
    exhorteth:'exhort', expandeth:'expand', expendeth:'expend', expoundeth:'expound', extinguisheth:'extinguish',
    exulteth:'exult', faileth:'fail', fainteth:'faint', falleth:'fall', fashioneth:'fashion', favoureth:'favour',
    feareth:'fear', feedeth:'feed', fighteth:'fight', findeth:'find', flasheth:'flash', fleeth:'flee', floweth:'flow',
    followeth:'follow', forbiddeth:'forbid', forgeth:'forge', forgetteth:'forget', forgiveth:'forgive',
    forgoeth:'forgo', forsaketh:'forsake', fruiteth:'fruit', fulfilleth:'fulfil', gathereth:'gather', giveth:'give',
    glorifieth:'glorify', gnaweth:'gnaw', goeth:'go', granteth:'grant', graspeth:'grasp', greeteth:'greet',
    grieveth:'grieve', groweth:'grow', guardeth:'guard', guideth:'guide', gusheth:'gush', harmeth:'harm',
    hasteneth:'hasten', healeth:'heal', heareth:'hear', helpeth:'help', hideth:'hide', hindereth:'hinder',
    hoardeth:'hoard', holdeth:'hold', honoureth:'honour', hopeth:'hope', hurleth:'hurl', hurteth:'hurt',
    hymneth:'hymn', impedeth:'impede', improveth:'improve', includeth:'include', increaseth:'increase',
    incurreth:'incur', inspireth:'inspire', intendeth:'intend', intercedeth:'intercede', interveneth:'intervene',
    inventeth:'invent', inviteth:'invite', judgeth:'judge', keepeth:'keep', killeth:'kill', kindleth:'kindle',
    knoweth:'know', launcheth:'launch', layeth:'lay', leadeth:'lead', leapeth:'leap', leaveth:'leave', lieth:'lie',
    likeneth:'liken', listeneth:'listen', liveth:'live', loitereth:'loiter', looketh:'look', loseth:'lose',
    loveth:'love', lurketh:'lurk', magnifieth:'magnify', maketh:'make', manifesteth:'manifest', meaneth:'mean',
    measureth:'measure', migrateth:'migrate', mingleth:'mingle', misleadeth:'mislead', mistaketh:'mistake',
    multiplieth:'multiply', narrateth:'narrate', narroweth:'narrow', noiseth:'noise', numbereth:'number',
    obeyeth:'obey', observeth:'observe', offereth:'offer', openeth:'open', opposeth:'oppose', ordaineth:'ordain',
    ordereth:'order', overseeth:'oversee', overtaketh:'overtake', oweth:'owe', owneth:'own', panteth:'pant',
    pardoneth:'pardon', passeth:'pass', payeth:'pay', perfecteth:'perfect', perisheth:'perish', permitteth:'permit',
    placeth:'place', pleaseth:'please', plotteth:'plot', plougheth:'plough', possesseth:'possess', prayeth:'pray',
    prepareth:'prepare', preserveth:'preserve', preventeth:'prevent', produceth:'produce', profiteth:'profit',
    promiseth:'promise', pronounceth:'pronounce', proportioneth:'proportion', proposeth:'propose',
    protecteth:'protect', provideth:'provide', punisheth:'punish', purifieth:'purify', purposeth:'purpose',
    pursueth:'pursue', putteth:'put', quickeneth:'quicken', rageth:'rage', raiseth:'raise', reacheth:'reach',
    receiveth:'receive', reciteth:'recite', recordeth:'record', refraineth:'refrain', refuseth:'refuse',
    rejecteth:'reject', relapseth:'relapse', relenteth:'relent', relieth:'rely', remaineth:'remain',
    remembereth:'remember', removeth:'remove', rendereth:'render', repayeth:'repay', repelleth:'repel',
    repenteth:'repent', replaceth:'replace', reprieveth:'reprieve', reproduceth:'reproduce', resoundeth:'resound',
    respondeth:'respond', resteth:'rest', returneth:'return', revealeth:'reveal', reviveth:'revive', riddeth:'rid',
    riseth:'rise', rolleth:'roll', runneth:'run', saveth:'save', scattereth:'scatter', scoreth:'score',
    scorneth:'scorn', sealeth:'seal', seeketh:'seek', seeth:'see', seetheth:'seethe', selecteth:'select',
    sendeth:'send', serveth:'serve', setteth:'set', sheddeth:'shed', shineth:'shine', showeth:'show',
    shrivelleth:'shrivel', shroudeth:'shroud', sippeth:'sip', slayeth:'slay', smiteth:'smite', snatcheth:'snatch',
    soweth:'sow', spareth:'spare', speaketh:'speak', spendeth:'spend', splitteth:'split', spoileth:'spoil',
    spreadeth:'spread', springeth:'spring', stealeth:'steal', stirreth:'stir', straiteneth:'straiten',
    strayeth:'stray', strengtheneth:'strengthen', stretcheth:'stretch', striketh:'strike', striveth:'strive',
    stunteth:'stunt', submitteth:'submit', sufficeth:'suffice', summoneth:'summon', supporteth:'support',
    supposeth:'suppose', surrendereth:'surrender', surroundeth:'surround', sustaineth:'sustain', taketh:'take',
    tasketh:'task', tasteth:'taste', teacheth:'teach', teareth:'tear', telleth:'tell', testifieth:'testify',
    thinketh:'think', threateneth:'threaten', thrilleth:'thrill', throweth:'throw', tireth:'tire', toucheth:'touch',
    trafficketh:'traffick', transgresseth:'transgress', trieth:'try', troubleth:'trouble', turneth:'turn',
    unravelleth:'unravel', upholdeth:'uphold', upriseth:'uprise', urgeth:'urge', uttereth:'utter', vanisheth:'vanish',
    visiteth:'visit', wafteth:'waft', walketh:'walk', wardeth:'ward', wasteth:'waste', watereth:'water',
    whispereth:'whisper', willeth:'will', wisheth:'wish', withdraweth:'withdraw', withholdeth:'withhold',
    worshippeth:'worship', wrongeth:'wrong', yieldeth:'yield'
  };
  const EST = {
    abasest:'abase', appointedst:'appointed', apprehendest:'apprehend', askest:'ask', attackest:'attack',
    bannest:'ban', believest:'believe', biddest:'bid', breakest:'break', bringest:'bring', broughtest:'brought',
    callest:'call', camest:'came', causest:'cause', choosest:'choose', comest:'come', commandedst:'commanded',
    completest:'complete', comprehendest:'comprehend', couldst:'could', createdst:'created', decidest:'decide',
    deemest:'deem', desirest:'desire', diest:'die', disbelievest:'disbelieve', disclaimest:'disclaim',
    enteredst:'entered', exaltest:'exalt', fearest:'fear', followedst:'followed', followest:'follow',
    forgettest:'forget', gatherest:'gather', givest:'give', hadst:'had', hearest:'hear', hirest:'hire', hopest:'hope',
    hungerest:'hunger', increasest:'increase', judgest:'judge', keepest:'keep', knewest:'knew', knowest:'know',
    leavest:'leave', lovest:'love', madest:'made', makest:'make', mayst:'may', meetest:'meet', mightest:'might',
    obeyedst:'obeyed', payest:'pay', preachest:'preach', readest:'read', receivest:'receive', recitest:'recite',
    rejectest:'reject', removest:'remove', reproachest:'reproach', saidst:'said', sayest:'say', seest:'see',
    sendest:'send', sentest:'sent', settedst:'set', shouldst:'should', spakest:'spoke', speakest:'speak',
    standest:'stand', summonest:'summon', takest:'take', tellest:'tell', thinkest:'think', thirstest:'thirst',
    threatenest:'threaten', threwest:'threw', tookest:'took', tormentest:'torment', uprisest:'uprise', wardest:'ward',
    warnest:'warn', withdrawest:'withdraw', wonderest:'wonder', worshippest:'worship', wouldst:'would'
  };

  // knows, does, goes, cries, passes
  function third(b) { return /(s|x|z|ch|sh|o)$/.test(b) ? b + 'es' : /[^aeiou]y$/.test(b) ? b.slice(0, -1) + 'ies' : b + 's'; }

  // what this word is: an old word (gloss), an old verb form (form), both, or neither (null)
  function lookup(word) {
    const w = String(word || '').toLowerCase().replace(/[^a-z]/g, '');
    if (!w) return null;
    const g = GLOSS[w], eb = ETH[w], sb = EST[w];
    if (!g && !eb && !sb) return null;
    return {
      word: w, quiet: QUIET.has(w),
      gloss: g ? { en: g[0], ar: g[1], noteEn: g[2] || '', noteAr: g[3] || '' } : null,
      form: eb ? { base: eb, modern: third(eb), thou: false } : sb ? { base: sb, modern: 'you ' + sb, thou: true } : null,
    };
  }

  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  // the translation as HTML, each old word in a span the reader can tap: underlined unless it is one of the common few
  function wrap(text) {
    return String(text || '').replace(/[A-Za-z]+|[^A-Za-z]+/g, t => {
      const w = t.toLowerCase();
      if (!/^[a-z]/.test(w) || !GLOSS[w]) return esc(t);
      return '<span class="eg' + (QUIET.has(w) ? ' q' : '') + '" data-w="' + w + '">' + t + '</span>';
    });
  }

  const api = { GLOSS, QUIET, ETH, EST, third, lookup, wrap };
  root.QI_ARCHAIC = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
