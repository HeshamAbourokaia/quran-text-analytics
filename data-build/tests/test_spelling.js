// Tests for web/spelling.js against the site's own word list: node data-build/tests/test_spelling.js
// A word or a phrase typed in today's spelling must find what the mushaf's own spelling finds.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'words.js'));
const S = require(path.join(WEB, 'spelling.js'));
const W = window.QURAN_WORDS;
const T0 = Date.now(), X = S.tables(W), BUILD_MS = Date.now() - T0;

// how many words of the text a typed word matches as written (the whole word, or inside longer words)
const count = (raw, whole = true) => { const t = S.asWritten(W, raw, whole); let n = 0; if (t) for (let i = 0; i < W.surface.length; i++) if (t(i)) n++; return n; };
// how many times a phrase comes (each word exactly, or with letters joined to its first and last word)
const times = (text, whole = true) => S.phrase(W, text, whole).starts.length;

const tests = {
  'a word is read the way the word list reads it'() {
    let same = 0;
    for (let i = 0; i < W.surface.length; i++) if (S.normalize(W.surface[i]) === W.norm[i]) same++;
    assert.equal(same, W.surface.length);
    assert.equal(S.normalize(String.fromCharCode(0xFDF2)), 'الله');   // the ready-made «Allah» some keyboards type
    assert.equal(S.normalize(''), '');
  },
  'a word typed in today\'s spelling counts what the mushaf\'s own spelling counts'() {
    const pairs = [['العالمين', 'العلمين', 61], ['الصالحات', 'الصلحت', 61], ['السماوات', 'السموت', 182], ['الملائكة', 'الملئكة', 38],
      ['آمنوا', 'ءامنوا', 263], ['الآخرة', 'الءاخرة', 71], ['القرآن', 'القرءان', 43], ['آيات', 'ءايت', 52], ['الصلاة', 'الصلوة', 58],
      ['الزكاة', 'الزكوة', 26], ['الكتاب', 'الكتب', 163], ['الظالمين', 'الظلمين', 64], ['الشيطان', 'الشيطن', 63], ['سليمان', 'سليمن', 10],
      ['إسرائيل', 'إسرءيل', 42]];
    for (const [today, mushaf, n] of pairs) {
      assert.equal(count(today), n, today);
      assert.equal(count(mushaf), n, mushaf);
    }
  },
  'a name the mushaf spells two ways is found under both'() {
    assert.equal(count('إبرهيم'), 43);   // most of the Quran
    assert.equal(count('إبرهم'), 15);    // the spelling of al-Baqarah
    assert.equal(count('إبراهيم'), 43 + 15);
  },
  'a phrase typed in today\'s spelling, and the same in the mushaf\'s'() {
    const P = { 'الذين آمنوا': 184, 'يا أيها الذين آمنوا': 89, 'الذين آمنوا وعملوا الصالحات': 36, 'رب العالمين': 34, 'يوم القيامة': 60,
      'السماوات والأرض': 133, 'أهل الكتاب': 19, 'الحياة الدنيا': 61, 'بسم الله الرحمن الرحيم': 2, 'الحمد لله رب العالمين': 4,
      'إن الله على كل شيء قدير': 8, 'لا إله إلا الله': 2, 'في الدنيا والآخرة': 13, 'جنات تجري من تحتها الأنهار': 26, 'إن الله غفور رحيم': 12 };
    for (const t in P) assert.equal(times(t), P[t], t);
    const same = [['الذين آمنوا', 'الذين ءامنوا'], ['يا أيها الذين آمنوا', 'يأيها الذين ءامنوا'], ['الذين آمنوا وعملوا الصالحات', 'الذين ءامنوا وعملوا الصلحت'],
      ['في الدنيا والآخرة', 'في الدنيا والءاخرة'], ['جنات تجري من تحتها الأنهار', 'جنت تجري من تحتها الأنهر']];
    for (const [today, mushaf] of same) assert.equal(times(mushaf), times(today), mushaf);
  },
  'the calling «يا» goes with the word it calls, as the mushaf writes them'() {
    const P = { 'يا أيها': 142, 'يا موسى': 24, 'يا آدم': 4, 'يا بني إسرائيل': 6, 'يا أيها الناس': 20 };
    for (const t in P) assert.equal(times(t), P[t], t);
    assert.equal(times('يأيها الناس'), times('يا أيها الناس'));
    assert.equal(S.phrase(W, 'يا موسى', true).n, 1);   // one word of the text
    assert.equal(S.phrase(W, 'يا أيها الذين آمنوا', true).n, 3);
  },
  'a typed hamza keeps its seat, and typed vowel marks mean exactly as written'() {
    assert.equal(times('إن الله'), 205);
    assert.equal(times('أن الله'), 52);
    assert.equal(times('ان الله'), 205 + 52);   // without a hamza, both
    assert.equal(count('إن'), 966);
    assert.equal(count('أن'), 638);
    assert.equal(count('ان'), 1605);
    assert.equal(count('مَلِك'), 4);    // king
    assert.equal(count('مَلَك'), 8);    // angel
    assert.equal(count('مُلْك'), 21);   // kingdom
  },
  'a hamza\'s seat tells faith from oaths, even where the mushaf writes the word otherwise'() {
    // the mushaf writes the long «a» of both as a small alif, so its own letters cannot decide: only the seat can
    assert.equal(count('الإيمان'), 7);    // faith
    assert.equal(count('الأيمان'), 2);    // oaths
    assert.equal(count('الايمان'), 7 + 2);   // without a hamza, both
    assert.equal(count('إيمانكم'), 6);
    assert.equal(count('أيمانكم'), 15);
  },
  'letters joined to the ends of a phrase are counted only when asked, and include the exact ones'() {
    const P = [['اليوم الآخر', 1, 26], ['أقيموا الصلاة', 1, 12], ['رب العالمين', 34, 42], ['الحمد لله', 21, 23], ['يوم الدين', 10, 13],
      ['عذاب أليم', 37, 46], ['الصلاة والزكاة', 0, 2], ['أقيموا الصلاة وآتوا الزكاة', 0, 8]];
    for (const [t, whole, joined] of P) {
      assert.equal(times(t), whole, t);
      assert.equal(times(t, false), joined, t + ', joined');
      const loose = new Set(S.phrase(W, t, false).starts);
      for (const i of S.phrase(W, t, true).starts) assert.ok(loose.has(i), t + ' at ' + i);
    }
  },
  'a word in today\'s spelling leads to its dictionary word'() {
    const D = { 'العالمين': ['العلمين', 'عالم'], 'آمنوا': ['ءامنوا', 'امن'], 'السماوات': ['السموت', 'سماء'], 'الملائكة': ['الملئكة', 'ملك'],
      'القرآن': ['القرءان', 'قرءان'], 'الصلاة': ['الصلوة', 'صلاة'], 'آيات': ['ءايت', 'اية'] };
    for (const t in D) {
      const r = S.today(W, t);
      assert.ok(r, t);
      assert.deepEqual([r.as, r.lemma], D[t], t);
      assert.equal(S.normalize(r.surf), r.as, t);           // the same spelling, with its marks to show
      assert.notEqual(r.surf, r.as, t);
    }
    assert.equal(S.today(W, 'ززززز'), null);
  },
  'every word of the text, typed in today\'s spelling, finds itself'() {
    let bad = 0;
    for (let i = 0; i < W.surface.length; i++) if (S.key(X.ham[i]) !== X.mod[i] || S.hamzaTyped(X.ham[i]) !== X.ham[i]) bad++;
    assert.equal(bad, 0, 'the tables disagree for ' + bad + ' words');
    // without hamzas: every word whose spelling today has none
    const HZ = /[أإآؤئء]/, made = new Map(), miss = [];
    let checked = 0;
    for (let i = 0; i < W.surface.length; i++) {
      const m = X.mod[i]; if (HZ.test(m)) continue;
      let t = made.get(m); if (!t) made.set(m, (t = S.asWritten(W, m, true)));
      checked++; if (!t(i) && miss.length < 5) miss.push(W.surface[i]);
    }
    assert.ok(checked > 70000, 'checked ' + checked);
    assert.deepEqual(miss, []);
    // with its hamzas on their seats: one in forty of the forms that have one
    const seen = new Set(), forms = [];
    for (let i = 0; i < W.surface.length; i++) { const h = X.ham[i]; if (HZ.test(h) && !seen.has(h)) { seen.add(h); forms.push(i); } }
    const miss2 = [];
    for (let k = 0; k < forms.length; k += 40) { const i = forms[k], t = S.asWritten(W, X.ham[i], true); if (!t || !t(i)) miss2.push(W.surface[i]); }
    assert.ok(forms.length > 3000, 'forms ' + forms.length);
    assert.deepEqual(miss2, []);
  },
  'everyday spellings people type all find something'() {
    const words = ['آمنوا', 'الآخرة', 'القرآن', 'الصلاة', 'الزكاة', 'الحياة', 'السماوات', 'الملائكة', 'إبراهيم', 'إسماعيل', 'الكتاب', 'الصالحات',
      'العالمين', 'آيات', 'الآيات', 'القيامة', 'جهنم', 'إسرائيل', 'الظالمين', 'الصابرين', 'سليمان', 'داود', 'هارون', 'إسحاق', 'الشيطان', 'الإنسان', 'أولئك', 'هؤلاء'];
    for (const w of words) assert.ok(count(w) > 0 || S.today(W, w), w);
    const phrases = ['يا أيها', 'يا موسى', 'يا آدم', 'يا بني إسرائيل', 'الذين آمنوا', 'يا أيها الذين آمنوا', 'الذين آمنوا وعملوا الصالحات',
      'بسم الله الرحمن الرحيم', 'الحمد لله رب العالمين', 'إن الله على كل شيء قدير', 'أقيموا الصلاة', 'السماوات والأرض', 'يوم القيامة',
      'الحياة الدنيا', 'لا إله إلا الله', 'اليوم الآخر', 'أهل الكتاب', 'رب العالمين', 'ذلك الكتاب'];
    for (const p of phrases) assert.ok(times(p) > 0, p);
  },
  'nothing is found for what is not there'() {
    assert.equal(count('ززززز'), 0);
    assert.equal(times('ككك ششش'), 0);
    assert.equal(times(''), 0);
    assert.equal(S.asWritten(W, '', true), null);
  },
  'the site uses this file, not a copy of its own'() {
    const app = fs.readFileSync(path.join(WEB, 'app.html'), 'utf8');
    assert.ok(app.includes('<script defer src="spelling.js"></script>'));
    assert.ok(app.includes('const SP = window.QI_SPELL;'));
    for (const own of ['function normalize(', 'function surfTest(', 'function spellTables(', 'function asWritten(', 'const hamzaTyped', 'const modernLetters'])
      assert.ok(!app.includes(own), 'app.html still defines ' + own);
  },
  'fast enough for a search as it is typed'() {
    assert.ok(BUILD_MS < 2000, 'tables took ' + BUILD_MS + ' ms');
    let t = Date.now(); for (let k = 0; k < 10; k++) times('يا أيها الذين آمنوا'); const ph = (Date.now() - t) / 10;
    t = Date.now(); for (let k = 0; k < 5; k++) count('الملائكة'); const wd = (Date.now() - t) / 5;
    assert.ok(ph < 100, 'a phrase took ' + ph.toFixed(1) + ' ms');
    assert.ok(wd < 300, 'a word took ' + wd.toFixed(1) + ' ms');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
