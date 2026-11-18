// Tests for web/lookup.js against the site's own surah list: node data-build/tests/test_lookup.js
'use strict';
const assert = require('assert/strict');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'data.js'));
const L = require(path.join(WEB, 'lookup.js'));
const META = window.QURAN_DATA.datasets.surahMeta;

const P = (q, o) => L.parse(q, META, o);
const V = (q, o) => { const r = P(q, o); return r && r.kind === 'verse' ? r.s + ':' + r.a + (r.b !== r.a ? '-' + r.b : '') : r && r.kind; };
const S = (q, o) => { const r = P(q, o); return r && r.kind === 'surah' ? r.s : r && r.kind; };

const tests = {
  'every surah has an English meaning'() {
    assert.equal(L.NAMES.length, 115);
    for (const m of META) assert.ok(L.meaning(m.n), 'no meaning for ' + m.n);
  },
  'no spelling, sound or meaning belongs to two surahs'() {
    const spell = new Map(), sound = new Map(), mean = new Map(), ar = new Map();
    const put = (map, k, n, what) => { if (!k) return; if (map.has(k) && map.get(k) !== n) assert.fail(`${what} «${k}» is both surah ${map.get(k)} and ${n}`); map.set(k, n); };
    for (const m of META) {
      const X = L.NAMES[m.n];
      for (const t of [m.en].concat(X.en)) for (const f of L.nameForms(t)) { put(spell, f, m.n, 'spelling'); put(sound, L.enKey(f), m.n, 'sound'); }
      for (const t of [X.m].concat(X.means)) put(mean, L.meanKey(t), m.n, 'meaning');
      for (const t of [m.ar].concat(X.ar)) put(ar, L.arKey(t), m.n, 'Arabic name');
    }
  },
  'every surah is found by its own Arabic and English name, and by its number'() {
    for (const m of META) {
      if (m.ar.length > 1) assert.equal(S(m.ar), m.n, m.ar);   // ص and ق alone are letters, not names
      assert.equal(S('سورة ' + m.ar), m.n, 'سورة ' + m.ar);
      assert.equal(S(m.en), m.n, m.en);
      assert.equal(S('Surah ' + m.en), m.n, 'Surah ' + m.en);
      assert.equal(S(L.meaning(m.n)), m.n, L.meaning(m.n));
      assert.equal(S('surah ' + m.n), m.n);
      assert.equal(S(String(m.n)), m.n);
      assert.equal(V(m.n + ':' + m.verses), m.n + ':' + m.verses);
      assert.equal(P(m.n + ':' + (m.verses + 1)).kind, 'bad');
    }
  },
  'a reference in numbers, in either kind of digit'() {
    assert.equal(V('2:255'), '2:255');
    assert.equal(V('٢:٢٥٥'), '2:255');
    assert.equal(V('۲:۲۵۵'), '2:255');
    assert.equal(V(' 2 : 255 '), '2:255');
    assert.equal(V('2.255'), '2:255');
    assert.equal(V('2/255'), '2:255');
    assert.equal(V('2 255'), '2:255');
    assert.equal(V('Q 2:255'), '2:255');
    assert.equal(V('2:285-286'), '2:285-286');
    assert.equal(V('2:285 \u2013 286'), '2:285-286');
    assert.equal(V('2:285 to 286'), '2:285-286');
    assert.equal(V('2:280-300'), '2:280-286');
    assert.equal(V('surah 2 verse 255'), '2:255');
    assert.equal(V('Surah 2, Ayah 255'), '2:255');
    assert.equal(V('verse 255 of surah 2'), '2:255');
    assert.equal(V('سورة ٢ آية ٢٥٥'), '2:255');
    assert.equal(V('الآية 255 من سورة 2'), '2:255');
    assert.equal(V('chapter 18 verses 9-26'), '18:9-26');
  },
  'a reference outside the text says so'() {
    assert.deepEqual(P('2:300'), { kind: 'bad', why: 'verse', s: 2, max: 286 });
    assert.deepEqual(P('115:1'), { kind: 'bad', why: 'surah' });
    assert.deepEqual(P('surah 200'), { kind: 'bad', why: 'surah' });
    assert.equal(P('2:0').kind, 'bad');
    assert.equal(P('Yusuf 200').kind, 'bad');
  },
  'a surah name with a verse'() {
    assert.equal(V('Baqarah 255'), '2:255');
    assert.equal(V('Al-Baqarah 255'), '2:255');
    assert.equal(V('al baqara: 255'), '2:255');
    assert.equal(V('Surah Al-Baqarah, verse 255'), '2:255');
    assert.equal(V('Ayah 255 of Surah Al-Baqarah'), '2:255');
    assert.equal(V('Baqarah 285-286'), '2:285-286');
    assert.equal(V('Al-Baqarah 2:255'), '2:255');
    assert.equal(V('the cave 10'), '18:10');
    assert.equal(V('Yusuf 4'), '12:4');
    assert.equal(V('البقرة ٢٥٥'), '2:255');
    assert.equal(V('البقرة 255'), '2:255');
    assert.equal(V('سورة البقرة آية ٢٥٥'), '2:255');
    assert.equal(V('سورة البقرة الآية 255'), '2:255');
    assert.equal(V('آية 255 من سورة البقرة'), '2:255');
    assert.equal(V('الكهف ١٠'), '18:10');
    assert.equal(V('آل عمران 103'), '3:103');
    assert.equal(V('البقرة ٢٨٥-٢٨٦'), '2:285-286');
    assert.equal(V('البقرة من 285 إلى 286'), '2:285-286');
    assert.equal(P('Yusuf 2:255'), null);
  },
  'English spellings of surah names'() {
    const same = (n, list) => { for (const q of list) assert.equal(S(q), n, q); };
    same(1, ['Fatiha', 'al-fatihah', 'Al Fatiha', 'Fateha', 'alfatiha', 'el-fateha', 'SURAH FATIHA', 'sorah fatiha', 'Surat Al-Fatihah', 'suratul fatiha', 'the opening']);
    same(2, ['Baqarah', 'baqara', 'Bakara', 'bakarah', 'Al-Baqarah', 'albaqarah', 'el-baqara', 'The Cow', 'cow']);
    same(3, ['Aal-Imran', 'Ali Imran', 'Al Imran', 'Aali Imran', 'Ale Imran', 'Imran', 'The Family of Imran', 'family of imran']);
    same(4, ['Nisa', "An-Nisa'", 'an nisaa', 'annisa', 'El-Nesa', 'women', 'The Women']);
    same(9, ['Tawbah', 'At-Tawbah', 'Taubah', 'Al-Tawba', 'Baraah', 'repentance']);
    same(12, ['Yusuf', 'Yousuf', 'Yousef', 'yusef', 'Youssef', 'Joseph']);
    same(17, ['Al-Isra', 'Israa', 'Bani Israel', 'The Night Journey']);
    same(18, ['Kahf', 'Al-Kahf', 'alkahf', 'el-kahf', 'kahaf', 'the cave', 'Cave']);
    same(19, ['Maryam', 'Mariam', 'Mary']);
    same(20, ['Taha', 'Ta-Ha', 'Ta Ha']);
    same(22, ['Hajj', 'Al-Hajj', 'Haj', 'El-Hagg', 'the pilgrimage']);
    same(24, ['Nur', 'An-Nur', 'Noor', 'an-noor', 'annur', 'Light', 'the light']);
    same(36, ['Yasin', 'Ya-Sin', 'Ya Sin', 'Yaseen', 'Yaasin', 'Yassin']);
    same(40, ['Ghafir', 'Ghaafir', 'Mumin', 'The Forgiver']);
    same(55, ['Rahman', 'Ar-Rahman', 'arrahman', 'Ar Rahmaan', 'the most merciful', 'The Beneficent']);
    same(56, ['Waqiah', "Al-Waqi'ah", 'Waqia', 'the event']);
    same(62, ['Jumuah', "Al-Jumu'ah", 'Jumah', 'Juma', 'El-Gomaa', 'Friday']);
    same(67, ['Mulk', 'Al-Mulk', 'Tabarak', 'the sovereignty']);
    same(71, ['Nuh', 'Nooh', 'Noah']);
    same(73, ['Muzzammil', 'Muzammil', 'Al-Muzzammil']);
    same(74, ['Muddaththir', 'Muddathir', 'Mudassir', 'Al-Muddassir']);
    same(87, ['Ala', "Al-A'la", 'Al-Ala', 'alala', 'Aala', 'the most high']);
    same(89, ['Fajr', 'Al-Fajr', 'El-Fagr', 'the dawn']);
    same(93, ['Duha', 'Ad-Duha', 'Dhuha', 'Adh-Dhuha', 'adduha', 'the morning hours']);
    same(94, ['Sharh', 'Ash-Sharh', 'Inshirah', 'Al-Inshirah', 'ashsharh', 'the relief']);
    same(96, ['Alaq', 'Al-Alaq', 'Iqra', 'the clot']);
    same(103, ['Asr', 'Al-Asr', 'alasr', 'the declining day']);
    same(105, ['Fil', 'Al-Fil', 'Feel', 'the elephant']);
    same(108, ['Kauthar', 'Kawthar', 'Al-Kawthar', 'Kausar', 'Kowsar', 'abundance']);
    same(109, ['Kafirun', 'Kafiroon', 'Al-Kafirun', 'the disbelievers']);
    same(111, ['Masad', 'Al-Masad', 'Lahab', 'the palm fibre', 'the palm fiber']);
    same(112, ['Ikhlas', 'Al-Ikhlas', 'Ikhlaas', 'Tawhid', 'sincerity']);
    same(113, ['Falaq', 'Al-Falaq', 'the daybreak']);
    same(114, ['Nas', 'An-Nas', 'annas', 'Naas', 'An-Naas', 'mankind']);
  },
  'a spelling a letter away is offered as near, not as certain'() {
    for (const [q, n] of [['Baqarrah', 2], ['Bakkarah', 2], ['Yousif', 12], ['Ibrahem', 14], ['Mumenoon', 23], ['Ankabot', 29], ['Zukhrof', 43], ['Mujadela', 58], ['Munafiqon', 63], ['Mutaffifen', 83], ['Ghashiyeh', 88], ['Kafiroun', 109]]) {
      const r = P(q);
      assert.ok(r && r.kind === 'surah' && r.s === n, `${q} -> ${JSON.stringify(r)}`);
    }
    assert.equal(P('Baqaroh').how, 'near');
    assert.equal(P('Baqarah').how, 'en');
  },
  'Arabic spellings of surah names'() {
    const same = (n, list) => { for (const q of list) assert.equal(S(q), n, q); };
    same(1, ['الفاتحة', 'الفاتحه', 'فاتحة', 'سورة الفاتحة', 'سوره الفاتحه', 'الْفَاتِحَة', 'فاتحة الكتاب', 'أم القرآن', 'السبع المثاني']);
    same(2, ['البقرة', 'البقره', 'بقرة', 'سورة البقرة']);
    same(3, ['آل عمران', 'ال عمران', 'العمران', 'عمران', 'سورة آل عمران']);
    same(17, ['الإسراء', 'الاسراء', 'اسراء', 'سورة بني إسرائيل']);
    same(18, ['الكهف', 'كهف', 'سورة الكهف']);
    same(36, ['يس', 'ياسين', 'سورة يس']);
    same(38, ['سورة ص', 'صاد']);
    same(50, ['سورة ق', 'قاف']);
    same(67, ['الملك', 'سورة تبارك']);
    same(78, ['النبأ', 'النبا', 'سورة عم', 'عم يتساءلون']);
    same(87, ['الأعلى', 'الاعلى', 'الاعلي']);
    same(94, ['الشرح', 'الانشراح', 'ألم نشرح']);
    same(112, ['الإخلاص', 'الاخلاص', 'التوحيد', 'قل هو الله أحد', 'سورة الصمد']);
  },
  'an everyday word is a surah only after the word surah, and a lone letter is not one'() {
    for (const q of ['تبارك', 'عم', 'اقرأ', 'تبت', 'الصمد', 'الحمد', 'بني إسرائيل', 'المؤمن', 'ص', 'ق', 'ن']) assert.equal(P(q), null, q);
  },
  'verses known by a name'() {
    for (const q of ['Ayat al-Kursi', 'ayatul kursi', 'Ayat ul Kursi', 'ayat alkursi', 'Ayatul-Kursi', 'throne verse', 'The Verse of the Throne', 'آية الكرسي', 'اية الكرسي', 'ايه الكرسى', 'آيَةُ الْكُرْسِيّ']) assert.equal(V(q), '2:255', q);
    assert.equal(P('Ayat al-Kursi').name.ar, 'آية الكرسي');
    assert.equal(V('Amana ar-Rasul'), '2:285-286');
    assert.equal(V('آمن الرسول'), '2:285-286');
    assert.equal(V('خواتيم البقرة'), '2:285-286');
    assert.equal(V('آية النور'), '24:35');
    assert.equal(V('the light verse'), '24:35');
    assert.equal(V('verse of light'), '24:35');
    assert.equal(V('آية الدين'), '2:282');
    assert.equal(V('the longest verse'), '2:282');
    assert.equal(V('أطول آية'), '2:282');
    assert.equal(V('البسملة'), '1:1');
    assert.equal(V('bismillah'), '1:1');
    assert.equal(V('آية البر'), '2:177');
    assert.equal(V('آية الوضوء'), '5:6');
    assert.equal(V('ayat al-wudu'), '5:6');
  },
  'a number on its own'() {
    assert.equal(S('18'), 18);
    assert.equal(S('١٨'), 18);
    assert.equal(S('114'), 114);
    assert.equal(V('255'), '2:255');                 // only al-Baqarah has a verse 255
    assert.equal(V('285-286'), '2:285-286');
    assert.deepEqual(P('200'), { kind: 'verses', v: 200, list: [2, 3, 7, 26] });
    assert.deepEqual(P('verse 200'), { kind: 'verses', v: 200, list: [2, 3, 7, 26] });
    assert.equal(P('365'), null);                    // a number someone is counting, not a verse
    assert.equal(P('verse 365').kind, 'bad');
    assert.equal(P('آية 5').kind, 'verses');
    assert.equal(P('5-7'), null);
  },
  'in the reader a number on its own is a verse of the surah being read'() {
    const here = { bare: 'verse', surah: 18 };
    assert.equal(V('10', here), '18:10');
    assert.equal(V('١٠', here), '18:10');
    assert.equal(V('verse 10', here), '18:10');
    assert.equal(V('9-26', here), '18:9-26');
    assert.equal(S('surah 10', here), 10);
    assert.equal(S('112', { bare: 'verse', surah: 1 }), 112);      // al-Fatihah has no verse 112: the surah
    assert.equal(V('255', { bare: 'verse', surah: 1 }), '2:255');
    assert.equal(V('2:255', here), '2:255');
    assert.equal(S('تبارك', { loose: true }), 67);
    assert.deepEqual(P('300', here), { kind: 'bad', why: 'verse', s: 18, max: 110 });
    assert.deepEqual(P('200', here), { kind: 'verses', v: 200, list: [2, 3, 7, 26] });
  },
  'ordinary searches are not references'() {
    for (const q of ['', '   ', 'يوم', 'رحمة', 'الله', 'رب العالمين', 'mercy', 'paradise', 'angels', 'the story of Yusuf', 'day 365', 'يوم 365', 'kafir', 'fat', 'fill', 'nor', 'tour',
      'how many times is day mentioned', '1:1:1', ':', '-', 'surah', 'سورة', 'x'.repeat(90)]) assert.equal(P(q), null, JSON.stringify(q));
  },
  'suggestions as a name is typed'() {
    const sug = q => L.suggest(q, META, 8);
    assert.deepEqual(sug('ka'), [18, 28, 54, 68, 97, 101, 108, 109]);
    assert.ok(sug('baq').includes(2));
    assert.ok(sug('al-ba').includes(2) && sug('al-ba').includes(90));
    assert.ok(sug('الك').includes(18) && sug('الك').includes(108) && sug('الك').includes(109));
    assert.ok(sug('كه').includes(18));
    assert.ok(sug('سورة الب').includes(2));
    assert.ok(sug('the c').length === 0 && sug('the ca').includes(18));
    assert.deepEqual(sug('2:25'), []);
    assert.deepEqual(sug(''), []);
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
