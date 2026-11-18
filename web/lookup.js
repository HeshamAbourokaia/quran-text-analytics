// Finding a verse or a surah from what a reader types (also loaded by the Node tests in data-build/tests).
//
// A reference in numbers (2:255, ٢:٢٥٥, 2 255, 2:285-286, surah 2 verse 255), a surah's name in Arabic or
// English (الكهف, Al-Kahf, Kahf, The Cave), a name with a verse (البقرة ٢٥٥, Baqarah 255), or a verse known by a
// name (آية الكرسي, Ayat al-Kursi). Plain matching against the names below; nothing is sent anywhere.
(function (root) {
  'use strict';

  const TASHKEEL = /[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]/g;
  const DASH = '\\-\u2013\u2014';   // a hyphen, and the two longer dashes a keyboard may put in a range
  const arPlain = s => String(s).replace(/[\uFB50-\uFDFF\uFE70-\uFEFC]/g, c => c.normalize('NFKC'));
  const latinDigits = s => String(s).replace(/[٠-٩]/g, c => c.charCodeAt(0) - 0x660).replace(/[۰-۹]/g, c => c.charCodeAt(0) - 0x6F0);
  const lettersOf = s => String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z]/g, '');

  // Each surah's English meaning (m, shown beside the name) and the other names and spellings people type.
  // en: spellings in Latin letters; means: English meanings; ar: other Arabic names. An Arabic name that starts
  // with ~ is also an everyday word of the text (تبارك, عم), so it counts only after the word «سورة».
  const N = (m, en, means, ar) => ({ m, en: en || [], means: means || [], ar: ar || [] });
  const NAMES = [null,
    N('The Opening', ['fatihah', 'fateha', 'al-hamd'], ['the opener', 'the opening chapter'], ['فاتحة الكتاب', 'أم القرآن', 'السبع المثاني', '~أم الكتاب', '~الحمد']),
    N('The Cow', ['baqarah', 'bakara', 'bakarah', 'baqra'], ['the heifer']),
    N('The Family of Imran', ['ali imran', 'al imran', 'ale imran', 'aali imran', 'imran'], ['the house of imran']),
    N('The Women', ['nisa', 'nesa'], []),
    N('The Table Spread', ['maidah', 'maeda', 'maedah'], ['the table', 'the feast']),
    N('The Cattle', ['anam', 'anaam'], ['livestock']),
    N('The Heights', ['araf', 'aaraf'], ['the elevated places']),
    N('The Spoils of War', [], ['the spoils']),
    N('The Repentance', ['tawbah', 'taubah', 'tauba', 'tawba', 'baraah', 'baraat'], [], ['~براءة']),
    N('Jonah', ['younus', 'younis', 'yunis', 'yonus'], []),
    N('Hud', ['hood'], []),
    N('Joseph', ['yousuf', 'yousef', 'yusef', 'youssef', 'yosef'], []),
    N('The Thunder', ['rad', 'raad'], []),
    N('Abraham', ['ibraheem', 'ebrahim'], []),
    N('The Rocky Tract', ['higr', 'hegr'], ['the stoneland', 'the rock']),
    N('The Bee', [], ['the bees']),
    N('The Night Journey', ['isra', 'israa', 'bani israel', 'bani israil'], ['the children of israel'], ['~بني إسرائيل']),
    N('The Cave', ['kahaf', 'kehf'], []),
    N('Mary', ['mariam', 'maryum', 'meryem'], []),
    N('Ta-Ha', ['taha', 'taaha'], []),
    N('The Prophets', ['anbiyaa', 'ambiya', 'anbiyah'], []),
    N('The Pilgrimage', ['haj', 'hagg', 'hag'], []),
    N('The Believers', ['muminoon', 'mominoon', 'mumineen'], []),
    N('The Light', ['noor', 'nour'], []),
    N('The Criterion', ['furqaan', 'forqan'], ['the standard']),
    N('The Poets', ['shuaraa', 'shoara', 'shuara'], []),
    N('The Ant', [], ['the ants']),
    N('The Stories', ['kasas'], ['the story', 'the narration', 'the narrations']),
    N('The Spider', ['ankaboot', 'ankabout'], []),
    N('The Romans', ['room', 'roum'], ['the byzantines', 'rome']),
    N('Luqman', ['lukman', 'lokman', 'luqmaan'], []),
    N('The Prostration', ['sajda', 'sagda', 'alif lam mim sajdah'], [], ['الم السجدة']),
    N('The Combined Forces', ['ahzaab'], ['the confederates', 'the clans', 'the allies', 'the parties']),
    N('Sheba', ['sabaa'], []),
    N('The Originator', ['faatir', 'fater'], ['the creator'], ['~الملائكة']),
    N('Ya-Sin', ['yaseen', 'ya sin', 'yaasin', 'yasen', 'yassin'], [], ['ياسين']),
    N('Those Who Set the Ranks', ['saffat', 'saaffat', 'safat'], ['those ranged in ranks', 'the rangers']),
    N('Sad', ['saad', 'suad'], [], ['صاد']),
    N('The Troops', [], ['the groups', 'the crowds', 'the throngs']),
    N('The Forgiver', ['ghaafir', 'ghafer', 'mumin', 'momin'], ['the believer'], ['~المؤمن']),
    N('Explained in Detail', ['fusilat', 'ha mim sajdah', 'hameem sajda'], ['detailed', 'the detailed'], ['حم السجدة']),
    N('The Consultation', ['shoora', 'shura'], ['counsel']),
    N('The Ornaments of Gold', ['zukhruf', 'zukruf'], ['the gold adornments', 'gold adornments']),
    N('The Smoke', ['dukhaan', 'dukhan'], []),
    N('The Crouching', ['jathiyah', 'jasiya', 'gathia'], ['the kneeling']),
    N('The Wind-Curved Sandhills', ['ahqaaf', 'ahkaf'], ['the sand dunes', 'the dunes', 'the sandhills']),
    N('Muhammad', ['mohammad', 'mohammed', 'muhammed', 'mohamed'], [], ['~القتال']),
    N('The Victory', ['fatah', 'fateh', 'fath'], ['the conquest']),
    N('The Rooms', ['hujuraat', 'hujraat', 'hugurat'], ['the chambers', 'the private apartments', 'the dwellings']),
    N('Qaf', ['qaaf'], [], ['قاف']),
    N('The Winnowing Winds', ['dhariyat', 'thariyat', 'zariyaat', 'dhariyaat'], ['the scatterers', 'the scattering winds']),
    N('The Mount', ['toor'], ['the mountain']),
    N('The Star', ['nagm', 'negm'], []),
    N('The Moon', ['kamar'], []),
    N('The Beneficent', ['rahmaan'], ['the most merciful', 'the most gracious', 'the merciful', 'the all merciful', 'the compassionate']),
    N('The Inevitable', ['waqiah', 'waqiaa', 'waqiyah', 'waqea'], ['the event', 'the inevitable event', 'the occurrence']),
    N('The Iron', ['hadeed'], []),
    N('The Pleading Woman', ['mujadila', 'mujadalah', 'mujadala'], ['she that disputes', 'the dispute', 'the pleading']),
    N('The Exile', ['hashr'], ['the gathering', 'the banishment', 'the mustering']),
    N('She That Is to Be Examined', ['mumtahina', 'mumtahana', 'mumtahanah'], ['the woman to be examined', 'the examined one']),
    N('The Ranks', ['saf'], ['the row', 'battle array']),
    N('Friday', ['jumuah', 'jumah', 'juma', 'jumua', 'jummah', 'jumaa', 'gomaa', 'gumaa'], ['the congregation', 'the day of congregation']),
    N('The Hypocrites', ['munafiqoon', 'munafiqeen'], []),
    N('The Mutual Disillusion', ['taghaabun'], ['the mutual loss and gain', 'loss and gain', 'mutual loss']),
    N('The Divorce', ['talaaq', 'talak'], []),
    N('The Prohibition', ['tahreem'], ['the banning']),
    N('The Sovereignty', ['tabarak', 'molk'], ['the dominion', 'the kingdom'], ['~تبارك']),
    N('The Pen', ['kalam'], []),
    N('The Reality', ['haaqqa', 'haqqa', 'haqah', 'haaqa'], ['the inevitable reality', 'the sure reality', 'the indubitable']),
    N('The Ascending Stairways', ['maarij'], ['the ways of ascent', 'the ascending steps'], ['سأل سائل']),
    N('Noah', ['nooh', 'nouh'], []),
    N('The Jinn', ['jin', 'djinn', 'ginn'], ['the jinns']),
    N('The Enshrouded One', ['muzammil', 'muzzamil'], ['the wrapped one', 'the enwrapped']),
    N('The Cloaked One', ['muddathir', 'mudathir', 'muddassir', 'mudassir', 'mudatsir'], ['the covered one']),
    N('The Resurrection', ['qiyama', 'qiyaamah', 'kiyamah', 'qiyamat'], ['the rising of the dead']),
    N('Man', ['insaan', 'dahr'], ['the human', 'the human being'], ['هل أتى', '~الدهر']),
    N('The Emissaries', ['mursalaat'], ['those sent forth', 'the sent ones']),
    N('The Tidings', ['nabaa', 'naba', 'amma'], ['the announcement', 'the great news', 'the news'], ['عم يتساءلون', '~عم']),
    N('Those Who Drag Forth', ['naziaat', 'nazeat'], ['those who pull out', 'the extractors', 'the snatchers']),
    N('He Frowned', ['abas'], ['the frowning']),
    N('The Overthrowing', ['takweer'], ['the folding up', 'the wrapping', 'the rolling']),
    N('The Cleaving', ['infitaar'], ['the splitting', 'the bursting apart']),
    N('The Defrauding', ['mutaffifeen', 'mutafifin', 'tatfif'], ['the defrauders', 'those who give less', 'the cheats']),
    N('The Sundering', ['inshiqaaq', 'inshikak'], ['the splitting open', 'the splitting asunder']),
    N('The Mansions of the Stars', ['burooj', 'burug'], ['the constellations', 'the great stars', 'the towers']),
    N('The Nightcomer', ['taariq', 'tarik'], ['the morning star', 'the night visitor', 'the piercing star']),
    N('The Most High', ['aala', 'alaa', 'ala'], ['the highest']),
    N('The Overwhelming', ['ghashiya', 'ghaashiyah'], ['the overwhelming event', 'the pall']),
    N('The Dawn', ['fajar', 'fagr'], ['the break of day']),
    N('The City', [], ['the land']),
    N('The Sun', ['shams'], []),
    N('The Night', ['layl', 'leyl', 'lail', 'leil'], []),
    N('The Morning Hours', ['dhuha', 'duhaa', 'zuha', 'doha', 'duha'], ['the morning light', 'the forenoon', 'the bright morning']),
    N('The Relief', ['inshirah', 'sharh', 'alam nashrah', 'nashrah'], ['the opening up', 'the expansion', 'the consolation', 'solace'], ['الانشراح', 'ألم نشرح']),
    N('The Fig', ['teen'], ['the figtree']),
    N('The Clot', ['alak', 'alaq', 'iqra', 'iqraa'], ['the clinging clot', 'the clinging substance', 'the blood clot'], ['~اقرأ']),
    N('The Power', ['qadar', 'kadr', 'qadr'], ['the night of decree', 'the decree', 'the night of power', 'destiny']),
    N('The Clear Proof', ['bayyinah', 'bayyina', 'bayina'], ['the clear evidence', 'the evidence', 'the proof']),
    N('The Earthquake', ['zalzala', 'zilzal', 'zilzaal'], ['the quake'], ['الزلزال']),
    N('The Courser', ['adiyaat', 'aadiyat'], ['the chargers', 'the coursers', 'the racers', 'those that run']),
    N('The Calamity', ['qaria', 'qaariah', 'karia'], ['the striking hour', 'the great calamity', 'the striking calamity']),
    N('The Rivalry in World Increase', ['takaathur', 'takasur'], ['the piling up', 'competition', 'the competition in increase', 'vying for increase']),
    N('The Declining Day', ['asr'], ['the epoch', 'the afternoon', 'the flight of time', 'time through the ages']),
    N('The Traducer', ['humaza'], ['the slanderer', 'the gossipmonger', 'the scandalmonger', 'the backbiter']),
    N('The Elephant', ['feel'], []),
    N('Quraysh', ['quraysh', 'qureysh', 'koraish', 'quresh'], []),
    N('The Small Kindnesses', ['maun', 'maoon', 'maoun'], ['the small kindness', 'the neighbourly assistance', 'almsgiving', 'the common kindnesses']),
    N('The Abundance', ['kawthar', 'kausar', 'kawsar', 'kowsar', 'kevser'], ['plenty', 'the abundant good']),
    N('The Disbelievers', ['kafiroon', 'kaafiroon', 'kafiron'], ['the unbelievers', 'the deniers']),
    N('The Divine Support', ['nasr'], ['the help', 'succour', 'the triumph']),
    N('The Palm Fibre', ['lahab', 'tabbat'], ['the palm fiber', 'the flame', 'the plaited rope'], ['اللهب', '~تبت']),
    N('The Sincerity', ['ikhlaas', 'iklas', 'tawhid', 'tawheed'], ['the purity', 'purity of faith', 'the unity', 'the oneness', 'monotheism'], ['التوحيد', 'قل هو الله أحد', '~الصمد']),
    N('The Daybreak', ['falak'], ['the rising dawn']),
    N('Mankind', ['naas', 'nas'], ['the people', 'men']),
  ];

  // Verses known by a name of their own. keys: other ways the name is typed.
  const NAMED = [
    { s: 2, a: 255, b: 255, en: 'Ayat al-Kursi', ar: 'آية الكرسي', keys: ['ayatul kursi', 'ayat kursi', 'ayat al kursiy', 'ayetel kursi', 'kursi verse', 'throne verse', 'verse of the throne', 'the throne verse'] },
    { s: 2, a: 285, b: 286, en: 'Amana ar-Rasul', ar: 'آمن الرسول', keys: ['amanar rasul', 'amana rasul', 'aamanar rasul', 'last two verses of al baqarah', 'last two verses of baqarah', 'خواتيم البقرة', 'خواتيم سورة البقرة', 'أواخر البقرة'] },
    { s: 24, a: 35, b: 35, en: 'The Light Verse', ar: 'آية النور', keys: ['ayat an nur', 'ayat al nur', 'ayatun nur', 'ayat an noor', 'light verse', 'verse of light', 'the verse of light'] },
    { s: 2, a: 282, b: 282, en: 'The Debt Verse', ar: 'آية الدَّين', keys: ['ayat ad dayn', 'ayat al dayn', 'ayat ad dain', 'debt verse', 'verse of debt', 'the verse of debt', 'the longest verse', 'longest verse', 'آية المداينة', 'أطول آية'] },
    { s: 1, a: 1, b: 1, en: 'The Basmala', ar: 'البسملة', keys: ['basmala', 'basmalah', 'bismillah', 'bismillah ar rahman ar rahim', 'بسملة'] },
    { s: 2, a: 177, b: 177, en: 'The Righteousness Verse', ar: 'آية البِرّ', keys: ['ayat al birr', 'ayat al bir', 'righteousness verse', 'verse of righteousness'] },
    { s: 5, a: 6, b: 6, en: 'The Ablution Verse', ar: 'آية الوضوء', keys: ['ayat al wudu', 'ayat al wudhu', 'ayat al wuzu', 'ablution verse', 'verse of ablution', 'wudu verse'] },
  ];

  // ---- keys: the form in which names are compared ----

  // an Arabic name without marks, hamza seats, the ة / ه and ى / ي differences, or spaces
  function arKey(s) {
    return arPlain(s).replace(TASHKEEL, '').replace(/[ٱآأإ]/g, 'ا').replace(/ى/g, 'ي').replace(/ة/g, 'ه')
      .replace(/ؤ/g, 'و').replace(/ئ/g, 'ي').replace(/[^\u0622-\u064A]/g, '');
  }
  const arBare = k => (k.startsWith('ال') && k.length > 3 ? k.slice(2) : k);

  // a Latin name by its sound: one letter for each of sh th dh kh gh, q as k, a lone g as j (the Egyptian ج),
  // o as u and e as i, doubled letters once, and no final h after a vowel (Baqarah, Baqara)
  function enKey(s) {
    let x = lettersOf(s);
    x = x.replace(/ph/g, 'f').replace(/c/g, 'k').replace(/sh/g, 'x').replace(/gh/g, 'G').replace(/g/g, 'j').replace(/G/g, 'g')
      .replace(/[tdk]h/g, m => m[0]).replace(/q/g, 'k').replace(/w/g, 'u').replace(/y/g, 'i').replace(/o/g, 'u').replace(/e/g, 'i')
      .replace(/(.)\1+/g, '$1');
    return x.length > 3 ? x.replace(/([aiu])h$/, '$1') : x;
  }
  // a typed Latin name as it stands, and without the Arabic article in front (al-, el-, and before a sun
  // letter: an-Nas, as-Saff, ash-Shams)
  function enForms(letters) {
    const out = [letters];
    for (const re of [/^[ae](?:sh|th|dh)(?=[a-z]{2})/, /^[ae][lnrstdz](?=[a-z]{2})/]) { const m = letters.match(re); if (m) out.push(letters.slice(m[0].length)); }
    return [...new Set(out)];
  }
  // a name from the list above, with and without an article that is written apart from it (Al-Kahf, kahf)
  const nameForms = t => [...new Set([lettersOf(t), lettersOf(String(t).replace(/^[ae](?:sh|th|dh|[lnrstdz])[-\s]+/i, ''))])];
  // an English meaning as written, without «the» and the small words around it
  const meanKey = s => String(s).toLowerCase().replace(/[^a-z ]+/g, ' ').replace(/\b(?:the|of|a|an|to|is|in)\b/g, ' ').replace(/\s+/g, '');

  const verseKey = t => enKey(String(t).toLowerCase().replace(/^the\s+/, ''));   // a verse's English name, without a leading «the»

  function lev(a, b) {
    let p = [...Array(b.length + 1).keys()];
    for (let i = 1; i <= a.length; i++) {
      const c = [i];
      for (let j = 1; j <= b.length; j++) c[j] = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      p = c;
    }
    return p[b.length];
  }

  // ---- the index of names, built once for a list of surahs ----

  let IX = null;
  function index(meta) {
    if (IX && IX.meta === meta) return IX;
    const spell = new Map(), sound = new Map(), mean = new Map(), ar = new Map(), weak = new Map(), verses = [];
    const put = (m, k, n) => { if (k && !m.has(k)) m.set(k, n); };
    for (const s of meta) {
      const X = NAMES[s.n] || N('');
      verses[s.n] = s.verses;
      for (const t of [s.en].concat(X.en)) for (const f of nameForms(t)) { put(spell, f, s.n); put(sound, enKey(f), s.n); }
      for (const t of [X.m].concat(X.means)) { const k = meanKey(t); if (k.length >= 3) put(mean, k, s.n); }
      for (const t of [s.ar].concat(X.ar)) { const m = t[0] === '~' ? weak : ar, k = arKey(t); put(m, k, s.n); put(m, arBare(k), s.n); }
    }
    const named = [];
    for (const v of NAMED) for (const t of [v.en, v.ar].concat(v.keys)) named.push([/[\u0600-\u06FF]/.test(t) ? arKey(t) : verseKey(t), v]);
    return (IX = { meta, spell, sound, mean, ar, weak, verses, named });
  }

  // which surah a typed name means: {s, how}; how = 'ar' | 'en' | 'meaning', or 'near' for a spelling a letter
  // or two away from one name only. said: the reader wrote «surah» / «سورة» before it.
  function surahByName(text, X, said) {
    const a = arKey(text);
    if (a) {
      if (a.length < 2 && !said) return null;                              // ص or ق alone is a letter being typed
      const b = arBare(a), s = X.ar.get(a) || X.ar.get(b) || (said && (X.weak.get(a) || X.weak.get(b)));
      return s ? { s, how: 'ar' } : null;
    }
    const letters = lettersOf(text);
    if (letters.length < 2) return null;
    const forms = enForms(letters);
    for (const f of forms) if (X.spell.has(f)) return { s: X.spell.get(f), how: 'en' };
    const mk = meanKey(text);
    if (X.mean.has(mk)) return { s: X.mean.get(mk), how: 'meaning' };
    // by sound, for a name of five letters or more: Baqarah, Bakara and Baqara are one name. Short English
    // words would otherwise turn into surahs (fat is not al-Fath)
    const keys = forms.filter(f => f.length >= 5).map(enKey);
    for (const k of keys) if (X.sound.has(k)) return { s: X.sound.get(k), how: 'en' };
    let best = null, tie = false;
    for (const k of keys) {
      const allow = k.length >= 8 ? 2 : 1;
      for (const [t, s] of X.sound) {
        if (t[0] !== k[0] || Math.abs(t.length - k.length) > allow) continue;
        const d = lev(k, t);
        if (d > allow) continue;
        if (!best || d < best.d) { best = { s, d }; tie = false; } else if (d === best.d && s !== best.s) tie = true;
      }
    }
    return best && !tie ? { s: best.s, how: 'near' } : null;
  }

  // ---- reading what was typed ----

  const EN_SURAH = /\b(?:surah?|soorah?|sorah?|surat(?:u|ul|al)?|sourate|chapter|ch)\b\.?/g;
  const EN_VERSE = /\b(?:verses?|ayah?s?|ayat|ayaat|aayah?)\b\.?/g;
  const AR_SURAH = /(?:^|\s)(?:ال)?سور[ةه](?=\s|\d|$)/g;
  const AR_VERSE = /(?:^|\s)(?:ال)?(?:[آا]ي[ةه]|[آا]يات)(?=\s|\d|$)/g;
  const has = (re, t) => { re.lastIndex = 0; const r = re.test(t); re.lastIndex = 0; return r; };
  const RANGE = '(?:\\s*[' + DASH + ']\\s*(\\d{1,3}))?';
  const RE_SV = new RegExp('^(\\d{1,3})\\s*[:.\\/]\\s*(\\d{1,3})' + RANGE + '$');   // 2:255, 2.255, 2/255-257
  const RE_S_V = new RegExp('^(\\d{1,3})\\s+(\\d{1,3})' + RANGE + '$');              // 2 255
  const RE_V = new RegExp('^(\\d{1,3})' + RANGE + '$');                              // 255, 285-286
  const RE_SAID_V = new RegExp('(?:verses?|ayah?s?|ayat|[آا]ي[ةه]|[آا]يات)\\s*(?:رقم|no\\.?|number)?\\s*(\\d{1,3})' + RANGE);
  const RE_SAID_S = /(?:surah?|soorah?|sorah?|surat|chapter|سور[ةه])\s*(?:رقم|no\.?|number)?\s*(\d{1,3})/;

  // What the text points at, or null when it is not a reference:
  //   {kind:'verse', s, a, b, how, name?, near?}   one verse or a run of verses
  //   {kind:'surah', s, how}                       a whole surah
  //   {kind:'verses', v, list}                     a verse number with no surah: the surahs that have such a verse
  //   {kind:'bad', why, s?, max?}                  a reference outside the text (2:300)
  // opts.surah with opts.bare === 'verse': a number on its own is a verse of that surah (the reader's own box).
  function parse(raw, meta, opts) {
    opts = opts || {};
    if (!meta || !meta.length) return null;
    const X = index(meta);
    let t = latinDigits(arPlain(raw || '')).replace(TASHKEEL, '').toLowerCase().replace(/[\u200e\u200f]/g, '').trim();
    if (!t || t.length > 80) return null;

    // a verse known by its own name
    const isAr = /[\u0600-\u06FF]/.test(t), nk = isAr ? arKey(t) : verseKey(t);
    if (nk.length >= 5 && !/\d/.test(t)) {
      for (const [k, v] of X.named) if (k === nk || (!isAr && nk.length >= 9 && k[0] === nk[0] && lev(k, nk) <= 1)) return verse(X, v.s, v.a, v.b, 'named', v);
    }

    const saidSurah = has(EN_SURAH, t) || has(AR_SURAH, t), saidVerse = has(EN_VERSE, t) || has(AR_VERSE, t);
    // «verse 255 of surah 2», in either order
    const vs = t.match(RE_SAID_V), ss = t.match(RE_SAID_S);
    if (vs && ss) return verse(X, +ss[1], +vs[1], vs[2] ? +vs[2] : +vs[1], 'ref');

    t = t.replace(/^q\.?\s*(?=\d)/, '').replace(EN_SURAH, ' ').replace(EN_VERSE, ' ').replace(AR_SURAH, ' ').replace(AR_VERSE, ' ')
      .replace(/\b(?:no|number|num|of|from)\b\.?/g, ' ').replace(/(?:^|\s)(?:رقم|من|في)(?=\s|\d|$)/g, ' ')
      .replace(/(\d)\s*(?:to|until|الي|إلى|الى|حتي|حتى)\s*(?=\d)/g, '$1-').replace(/[،,;؛()«»"“”]/g, ' ');
    const sep = '[\\s:.\\/' + DASH + ']+';
    const nums = t.replace(new RegExp('[^\\d:.\\/\\s' + DASH + ']', 'g'), ' ').replace(/\s+/g, ' ').replace(new RegExp('^' + sep + '|' + sep + '$', 'g'), '');
    const words = t.replace(/[\d:.\/\u2013\u2014]/g, ' ').replace(/(?:^|\s)-+|-+(?=\s|$)/g, ' ').replace(/\s+/g, ' ').trim();

    let s = 0, a = 0, b = 0, m;
    if ((m = nums.match(RE_SV)) || (m = nums.match(RE_S_V))) { s = +m[1]; a = +m[2]; b = m[3] ? +m[3] : a; }
    else if ((m = nums.match(RE_V))) { a = +m[1]; b = m[2] ? +m[2] : a; }
    else if (nums) return null;

    const named = words ? surahByName(words, X, saidSurah || !!opts.loose) : null;
    if (words && !named) return null;                                    // other words: not a reference
    if (named) {
      if (s && s !== named.s) return null;                               // «Yusuf 2:255» says two things
      if (!a) return { kind: 'surah', s: named.s, how: named.how };
      return verse(X, named.s, a, b, 'name', null, named.how);
    }
    if (s) return verse(X, s, a, b, 'ref');
    if (!a) return null;
    // a number on its own
    const here = opts.bare === 'verse' && opts.surah >= 1 && opts.surah <= 114 ? opts.surah : 0;
    if (saidSurah && !saidVerse) return b === a && a >= 1 && a <= 114 ? { kind: 'surah', s: a, how: 'num' } : { kind: 'bad', why: 'surah' };
    if (here && b <= X.verses[here]) return verse(X, here, a, b, 'here');
    if (b === a && !saidVerse && a >= 1 && a <= 114) return { kind: 'surah', s: a, how: 'num' };
    // in the reader, a number no surah reaches is past the end of the one being read
    return holders(X, a, b, saidVerse) || (here ? { kind: 'bad', why: 'verse', s: here, max: X.verses[here] } : null);
  }

  function verse(X, s, a, b, how, name, nameHow) {
    if (!(s >= 1 && s <= 114)) return { kind: 'bad', why: 'surah' };
    const max = X.verses[s];
    if (!(a >= 1) || a > max || b < a) return { kind: 'bad', why: 'verse', s, max };
    const r = { kind: 'verse', s, a, b: Math.min(b, max), how };
    if (name) r.name = { en: name.en, ar: name.ar };
    if (nameHow === 'near') r.near = true;
    return r;
  }
  // the surahs long enough to hold this verse number: 255 is in al-Baqarah alone, 200 in four surahs
  function holders(X, a, b, said) {
    const list = [];
    for (let s = 1; s <= 114; s++) if (a >= 1 && b <= X.verses[s]) list.push(s);
    if (list.length === 1) return verse(X, list[0], a, b, 'only');
    if (!list.length) return said ? { kind: 'bad', why: 'verse', max: Math.max(...X.verses.filter(Boolean)) } : null;
    return a === b ? { kind: 'verses', v: a, list } : null;
  }

  // surahs whose name begins with what has been typed so far, for a box that suggests as you type
  function suggest(raw, meta, limit) {
    const out = [], t = arPlain(raw || '').replace(TASHKEEL, '').toLowerCase().trim();
    if (!meta || !meta.length || !t || /[\d٠-٩۰-۹]/.test(t)) return out;
    const X = index(meta), seen = new Set(), add = s => { if (!seen.has(s)) { seen.add(s); out.push(s); } };
    const a = arKey(t.replace(AR_SURAH, ' ')), letters = lettersOf(t.replace(EN_SURAH, ' '));
    if (a.length >= 2) {
      for (const m of [X.ar, X.weak]) for (const [k, s] of m) if (k.startsWith(a) || k.startsWith(arBare(a))) add(s);
    } else if (!a && letters.length >= 2) {
      const forms = enForms(letters), keys = forms.map(enKey), mk = meanKey(t);
      for (const [k, s] of X.spell) if (forms.some(f => k.startsWith(f))) add(s);
      for (const [k, s] of X.sound) if (keys.some(q => q.length >= 3 && k.startsWith(q))) add(s);
      if (mk.length >= 2) for (const [k, s] of X.mean) if (k.startsWith(mk)) add(s);
    }
    return out.sort((p, q) => p - q).slice(0, limit || 6);
  }

  const meaning = n => (NAMES[n] ? NAMES[n].m : '');

  const api = { parse, suggest, meaning, NAMES, NAMED, arKey, enKey, nameForms, meanKey };
  root.QI_LOOKUP = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
