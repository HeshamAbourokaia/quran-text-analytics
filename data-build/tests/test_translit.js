// Tests for web/translit.js against the site's own word index: node data-build/tests/test_translit.js
'use strict';
const assert = require('assert/strict');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'words.js'));
require(path.join(WEB, 'roman.js'));
const R = require(path.join(WEB, 'translit.js'));
const W = window.QURAN_WORDS, ROMAN = window.QURAN_ROMAN, COUNT = new Map();
for (const l of W.lemma) if (l) COUNT.set(l, (COUNT.get(l) || 0) + 1);
const IX = R.index(ROMAN, COUNT);

const M = (q, n) => R.match(q, IX, n || 5);
const top = q => { const m = M(q, 1)[0]; return m ? m.l : null; };
const how = q => { const m = M(q, 1)[0]; return m ? m.how : null; };
const all = q => M(q, 6).map(m => m.l);

const tests = {
  'every word of the index has a sound, written in the signs the table uses'() {
    const missing = [...COUNT.keys()].filter(l => l.length > 1 && !ROMAN[l]);
    assert.deepEqual(missing, []);
    for (const l in ROMAN) assert.match(ROMAN[l], /^[abdfghijklmnqrstuwxyzAIUEHSDTZvp*$' ]+$/, l);
  },
  'a sound is shown in plain letters'() {
    const S = { raHmap: 'rahma', SalAp: 'salah', "qur'An": 'qur’an', "'ismAEIl": 'isma’il', Eilm: 'ilm', "samA'": 'sama', $ayTAn: 'shaytan',
      '*ikr': 'dhikr', vawAb: 'thawab', xayr: 'khayr', magfirap: 'maghfira', "'Amana": 'amana', nabI: 'nabi', allAh: 'allah', "duEA'": 'du’a' };
    for (const s in S) assert.equal(R.spell(s), S[s], s);
    assert.equal(R.spell(ROMAN['رحمة']), 'rahma');
    assert.equal(R.spell(ROMAN['يوم']), 'yawm');
    assert.equal(R.spell(ROMAN['موسي']), 'musa');
    assert.equal(R.spell(ROMAN['ابراهيم']), 'ibrahim');
    assert.equal(R.spell(ROMAN['قيامة']), 'qiyama');
    assert.equal(ROMAN['ملك'], 'malak mulk malik malk');
  },
  'spellings of one word share a key'() {
    const same = [['rahma', 'rahmah', 'Rahma', 'ra7ma', 'rahmaa'], ['deen', 'din', 'dîn'], ['noor', 'nur', 'nour'], ['quran', "qur'an", 'koran', 'Qur’an'],
      ['iman', 'eman', 'imaan', 'eeman'], ['yom', 'youm'], ['yawm', 'yaum'], ['shaytan', 'shaitan'], ['3ilm', 'ilm', 'elm', "'ilm"], ['khayr', 'khair']];
    for (const g of same) for (const x of g) assert.equal(R.key(x), R.key(g[0]), x + ' / ' + g[0]);
    assert.notEqual(R.key('nur'), R.key('nar'));
    assert.notEqual(R.key('sabr'), R.key('shabr'));
  },
  'a word typed in English letters finds the Arabic word'() {
    const T = { rahma: 'رحمة', rahmah: 'رحمة', rahmat: 'رحمة', sabr: 'صبر', jannah: 'جنة', jannat: 'جنة', salat: 'صلاة', salah: 'صلاة', zakat: 'زكاة', zakah: 'زكاة',
      iman: 'ايمان', taqwa: 'تقوي', quran: 'قرءان', koran: 'قرءان', musa: 'موسي', isa: 'عيسي', ibrahim: 'ابراهيم', ibraheem: 'ابراهيم', nuh: 'نوح', yusuf: 'يوسف',
      maryam: 'مريم', muhammad: 'محمد', allah: 'الله', rabb: 'رب', yawm: 'يوم', nur: 'نور', noor: 'نور', deen: 'دين', dunya: 'دنيا', jahannam: 'جهنم',
      shaytan: 'شيطان', rasul: 'رسول', rasool: 'رسول', nabi: 'نبي', kitab: 'كتاب', qalb: 'قلب', nafs: 'نفس', ruh: 'روح', ilm: 'علم', abd: 'عبد', haqq: 'حق',
      tawba: 'توبة', maghfira: 'مغفرة', shukr: 'شكر', hamd: 'حمد', kufr: 'كفر', kafir: 'كافر', muslim: 'مسلم', mumin: 'مؤمن', zalim: 'ظالم', zulm: 'ظلم',
      firawn: 'فرعون', sulayman: 'سليمان', dawud: 'داود', harun: 'هارون', adam: 'ادم', ard: 'ارض', sama: 'سماء', shams: 'شمس', qamar: 'قمر', layl: 'ليل',
      bahr: 'بحر', nar: 'نار', hayat: 'حياة', mawt: 'موت', khayr: 'خير', salam: 'سلام', sirat: 'صراط', mustaqim: 'مستقيم', huda: 'هدي', fitna: 'فتنة',
      ajr: 'اجر', thawab: 'ثواب', hisab: 'حساب', mizan: 'ميزان', qiyama: 'قيامة', rizq: 'رزق', nisa: 'نساء', masjid: 'مسجد', qibla: 'قبلة', jihad: 'جهاد',
      shahid: 'شهيد', ramadan: 'رمضان', firdaws: 'فردوس', barzakh: 'برزخ', kawthar: 'كوثر' };
    for (const q in T) { assert.equal(top(q), T[q], q); assert.equal(how(q), 'exact', q); }
  },
  'however the sounds English lacks are written'() {
    const T = { zikr: 'ذكر', dhikr: 'ذكر', thikr: 'ذكر', dhulm: 'ظلم', thulm: 'ظلم', sawab: 'ثواب', ramadhan: 'رمضان', yom: 'يوم', youm: 'يوم', yaum: 'يوم',
      mot: 'موت', maut: 'موت', kheir: 'خير', khair: 'خير', sheitan: 'شيطان', shaitan: 'شيطان', tauba: 'توبة', toba: 'توبة', suleiman: 'سليمان', soliman: 'سليمان',
      dawood: 'داود', haroun: 'هارون', gannah: 'جنة', koran: 'قرءان', takwa: 'تقوي', rizk: 'رزق', eman: 'ايمان', ketab: 'كتاب', moslem: 'مسلم', momin: 'مؤمن',
      saleh: 'صالح', shokr: 'شكر', donya: 'دنيا', hoda: 'هدي', kaaba: 'كعبة', firdous: 'فردوس', "mu'min": 'مؤمن', "qur'an": 'قرءان', 'dîn': 'دين' };
    for (const q in T) { assert.equal(top(q), T[q], q); assert.equal(how(q), 'exact', q); }
  },
  'the chat alphabet: 7 is ح, 3 is ع, 5 is خ'() {
    assert.equal(top('ra7ma'), 'رحمة');
    assert.equal(top('7amd'), 'حمد');
    assert.equal(top('3ilm'), 'علم');
    assert.equal(top('5ayr'), 'خير');
    assert.equal(top('sa7ab'), 'سحاب');
    assert.equal(R.chat('juz 30'), 'juz 30');                     // a number on its own stays a number
    assert.equal(R.chat('2:255'), '2:255');
  },
  'with the Arabic article in front'() {
    for (const q of ['al-rahman', 'ar-rahman', 'alrahman', 'Ar-Rahman', 'el rahman', 'arrahman']) assert.equal(top(q), 'رحمن', q);
    for (const q of ['al-kitab', 'alkitab', 'el-kitab', 'al kitab']) assert.equal(top(q), 'كتاب', q);
    for (const q of ['as-salam', 'assalam', 'al-salam']) assert.equal(top(q), 'سلام', q);
    assert.equal(top('allah'), 'الله');                           // not «lah» with an article
    assert.equal(top('alladhi'), 'الذي');
  },
  'a rarer word spelled the same way is offered too'() {
    assert.deepEqual(all('qalb').slice(0, 2), ['قلب', 'كلب']);
    assert.deepEqual(all('kalb').slice(0, 2), ['قلب', 'كلب']);
    assert.ok(all('nur').includes('نار') && all('nar').includes('نور'));
    assert.equal(top('ilah'), 'اله');
    assert.equal(top('malik'), 'ملك');
    assert.ok(all('salat').includes('ثلاث'));
  },
  'a regular plural finds its word'() {
    for (const [q, l] of [['muslimin', 'مسلم'], ['muslimeen', 'مسلم'], ['kafirun', 'كافر'], ['kafireen', 'كافر'], ['zalimin', 'ظالم'], ['sabirin', 'صابر'], ['mumineen', 'مؤمن']]) {
      assert.equal(top(q), l, q); assert.equal(how(q), 'form', q);
    }
    assert.equal(top('salihat'), 'صالحة');
  },
  'a vowel or a letter out still finds it, and says it is less sure'() {
    assert.equal(top('yousef'), 'يوسف'); assert.equal(how('yousef'), 'sound');
    assert.equal(top('mohamed'), 'محمد'); assert.equal(how('mohamed'), 'sound');
    assert.equal(top('mariam'), 'مريم');
    assert.equal(top('ramzan'), 'رمضان');
    assert.equal(top('magfira'), 'مغفرة');
    assert.equal(top('tawakkul'), 'توكل');
    assert.equal(top('muttaqin'), 'متقي'); assert.equal(how('muttaqin'), 'near');
  },
  'English words and numbers are left alone'() {
    for (const q of ['mercy', 'light', 'the', 'pharaoh', 'forgiveness', 'heaven', 'water', '2:255', '36', 'x', '']) assert.deepEqual(M(q).filter(m => m.how === 'exact'), [], q);
    assert.deepEqual(M('رحمة'), []);                              // Arabic letters are not this module's business
    assert.deepEqual(M('2:255'), []);
  },
  'phrases known by their sound'() {
    const T = { bismillah: 'بسم الله', 'Bismi Allah': 'بسم الله', alhamdulillah: 'الحمد لله', 'al-hamdu lillah': 'الحمد لله', 'elhamdulillah': 'الحمد لله',
      subhanallah: 'سبحان الله', 'subhan Allah': 'سبحان الله', inshallah: 'إن شاء الله', 'in sha Allah': 'إن شاء الله', "insha'Allah": 'إن شاء الله',
      mashallah: 'ما شاء الله', 'la ilaha illa Allah': 'لا إله إلا الله', 'la ilaha illallah': 'لا إله إلا الله', 'rabbil alamin': 'رب العالمين', 'rabb al-alameen': 'رب العالمين',
      'sirat al-mustaqim': 'الصراط المستقيم', 'yawm al-qiyamah': 'يوم القيامة', 'yawm al-din': 'يوم الدين', 'yawm ad-deen': 'يوم الدين', 'ahl al-kitab': 'أهل الكتاب',
      'salam alaykum': 'سلام عليكم', 'assalamu alaikum': 'سلام عليكم', 'inna lillahi': 'إنا لله', 'qul huwa Allahu ahad': 'قل هو الله أحد' };
    for (const q in T) assert.equal(R.phrase(q), T[q], q);
    for (const q of ['rahma', 'mercy', 'allah', 'alham', 'the day of judgment', '']) assert.equal(R.phrase(q), '', q);
    const seen = new Map();
    for (const [ar, ...en] of R.PHRASES) for (const e of en) { const k = R.key(e); assert.ok(!seen.has(k) || seen.get(k) === ar, e); seen.set(k, ar); }
  },
  'it is quick enough to run on every keystroke'() {
    const t = Date.now(), qs = ['rahma', 'mustaqim', 'alhamdulillah', 'sulaymaan', 'qiyamah', 'the day of judgment'];
    for (let i = 0; i < 20; i++) for (const q of qs) M(q);
    assert.ok((Date.now() - t) / (20 * qs.length) < 12, 'slow: ' + ((Date.now() - t) / (20 * qs.length)).toFixed(1) + ' ms');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
