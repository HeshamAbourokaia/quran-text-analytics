// Tests for web/archaic.js, the old English of the translation made plain: node data-build/tests/test_archaic.js
// Every old verb form of the translation is covered, every glossed word is really in it, and the HTML is safe.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'translation_en.js'));
const A = require(path.join(WEB, 'archaic.js'));
const EN = window.QURAN_EN;

// the translation's words, and the words beside "thou"
const vocab = new Map(), nearThou = new Set();
for (const v of Object.values(EN)) {
  const t = v.match(/[A-Za-z]+/g) || [];
  t.forEach((w, i) => {
    const k = w.toLowerCase(); vocab.set(k, (vocab.get(k) || 0) + 1);
    if (k === 'thou') for (const j of [i - 1, i + 1, i + 2]) if (t[j]) nearThou.add(t[j].toLowerCase());
  });
}
const NOT_VERBS = new Set(['teeth', 'seth', 'beneath']);
const ORDINAL = /(twent|thirt|fort|fift|sixt|sevent|eight|ninet)ieth$/;
const MODERN_ST = new Set(['trust', 'most', 'best', 'fast', 'must', 'cast', 'lest', 'outcast', 'almost', 'steadfast', 'tryst',
  'hast', 'dost', 'wast', 'didst', 'canst', 'art', 'wilt', 'shalt', 'wert']);   // modern words, or old ones the glossary explains

const tests = {
  'every old -eth verb of the translation has its modern verb'() {
    const missing = [...vocab.keys()].filter(w => /eth$/.test(w) && w.length >= 5 && !NOT_VERBS.has(w) && !ORDINAL.test(w) && !A.ETH[w]);
    assert.deepEqual(missing, []);
    assert.ok(Object.keys(A.ETH).length > 350);
  },
  'every old -est verb used with thou has its modern verb'() {
    const missing = [...nearThou].filter(w => /e?st$/.test(w) && w.length > 3 && !MODERN_ST.has(w) && !A.EST[w]);
    assert.deepEqual(missing, []);
    for (const w of MODERN_ST) assert.ok(!A.EST[w], w + ' is a modern word, not an old verb form');
  },
  'the modern form reads as today\'s English'() {
    const want = { knoweth: 'knows', doeth: 'does', goeth: 'goes', seeth: 'sees', crieth: 'cries', passeth: 'passes', obeyeth: 'obeys',
      maketh: 'makes', befalleth: 'befalls', agreeth: 'agrees', aileth: 'ails', casteth: 'casts', seetheth: 'seethes', purifieth: 'purifies' };
    for (const [w, m] of Object.entries(want)) assert.equal(A.lookup(w).form.modern, m, w);
    const thou = { seest: 'you see', knowest: 'you know', broughtest: 'you brought', madest: 'you made', camest: 'you came', mayst: 'you may' };
    for (const [w, m] of Object.entries(thou)) assert.equal(A.lookup(w).form.modern, m, w);
  },
  'no number ending in -eth is taken for a verb'() {
    for (const w of ['twentieth', 'fortieth', 'teeth', 'beneath']) assert.equal(A.lookup(w), null, w);
  },
  'every glossed word is in the translation, with today\'s English and its Arabic'() {
    for (const [w, g] of Object.entries(A.GLOSS)) {
      assert.ok(vocab.has(w), w + ' is not in the translation');
      assert.ok(typeof g[0] === 'string' && g[0].length > 1 && !/[؀-ۿ]/.test(g[0]), w + ': English');
      assert.ok(/[؀-ۿ]/.test(g[1]), w + ': Arabic');
      if (g[2] || g[3]) assert.ok(g[2] && /[؀-ۿ]/.test(g[3]), w + ': a note in both languages');
    }
    assert.ok(Object.keys(A.GLOSS).length > 120);
  },
  'the words Pickthall uses most are covered'() {
    for (const w of ['lo', 'ye', 'unto', 'hath', 'thou', 'thee', 'thy', 'verily', 'doom', 'save', 'whoso', 'nay', 'naught', 'therein', 'bethink', 'thereto'])
      assert.ok(A.lookup(w) && A.lookup(w).gloss, w);
    // 11:28, the verse that showed the need
    const v = EN['11:28'];
    for (const w of ['Bethink', 'hath', 'averse', 'thereto']) { assert.ok(v.includes(w), w); assert.ok(A.lookup(w).gloss, w); }
  },
  'the quiet few are glossed, and nothing else is quiet'() {
    for (const w of A.QUIET) assert.ok(A.GLOSS[w], w);
    assert.equal(A.lookup('thou').quiet, true);
    assert.equal(A.lookup('bethink').quiet, false);
  },
  'any case and stray marks find the word'() {
    assert.equal(A.lookup('Lo!').word, 'lo');
    assert.equal(A.lookup('HATH').word, 'hath');
    assert.equal(A.lookup('Knoweth,').form.base, 'know');
    for (const w of ['', null, undefined, '123', 'compel', 'cloth']) assert.equal(A.lookup(w), null, String(w));
  },
  'the wrapped translation is the same text, safe, with the old words marked'() {
    const t = 'Lo! <script>x</script> & He hath made it plain unto ye "averse" thereto; cloth, sloth.';
    const h = A.wrap(t);
    assert.ok(!h.includes('<script'), 'markup in the text stays text');
    const back = h.replace(/<span class="eg( q)?" data-w="[a-z]+">/g, '').replace(/<\/span>/g, '')
      .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');
    assert.equal(back, t);
    assert.ok(h.includes('<span class="eg" data-w="lo">Lo</span>'));
    assert.ok(h.includes('<span class="eg q" data-w="hath">hath</span>'));
    assert.ok(h.includes('<span class="eg" data-w="thereto">thereto</span>'));
    assert.ok(!/data-w="(cloth|sloth|lo)">(cloth|sloth)/.test(h), 'a word inside another word is left alone');
    assert.equal(A.wrap(''), '');
    // the whole translation wraps back to itself
    for (const [k, v] of Object.entries(EN)) {
      const b = A.wrap(v).replace(/<span class="eg( q)?" data-w="[a-z]+">/g, '').replace(/<\/span>/g, '')
        .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&amp;/g, '&');
      if (b !== v) assert.fail(k + ' changed when wrapped');
    }
  },
  'the site loads this file with the translation'() {
    const app = fs.readFileSync(path.join(WEB, 'app.html'), 'utf8');
    assert.ok(/verses:\['corpus\.js','translation_en\.js','archaic\.js'\]/.test(app), 'archaic.js does not load with the translation');
    assert.ok(app.includes('window.QI_ARCHAIC'));
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
