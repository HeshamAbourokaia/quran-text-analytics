// Tests for web/card.js, the layout of a verse's image card: node data-build/tests/test_card.js
// Text is measured with a stand-in for the canvas (a width per letter), which is enough to check that every verse
// fits the card, no word is lost, lines are balanced, and a long verse grows the card rather than the text shrinking.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'corpus.js'));
require(path.join(WEB, 'translation_en.js'));
const C = require(path.join(WEB, 'card.js'));
const V = window.QURAN_VERSES, E = window.QURAN_EN;

// about the widths of Amiri and Instrument Serif: marks above and below a letter take no width
const measure = (t, kind, size) => [...t].filter(ch => !/\p{M}/u.test(ch)).length * size * (kind === 'ar' ? 0.42 : 0.44);
const card = (k, en) => C.layout({ ar: V[k], en: en ? E[k] : '', measure });
const widest = (lines, kind, size) => Math.max(...lines.map(l => measure(l, kind, size)));

const tests = {
  'a short verse: a square card, in the largest size'() {
    const L = card('112:1', false);
    assert.equal(L.w, 1080); assert.equal(L.h, 1080);
    assert.equal(L.ar.size, C.AR_MAX);
  },
  'the longest verse grows the card, and the text stays readable'() {
    const L = card('2:282', true);
    assert.equal(L.ar.size, C.AR_MIN);
    assert.equal(L.en.size, C.EN_MIN);
    assert.ok(L.h > 1080, 'height ' + L.h);
  },
  'every verse fits: no line too wide, no word lost, with and without the translation'() {
    const t0 = Date.now(); let tall = 0;
    for (const k of Object.keys(V)) for (const en of [false, true]) {
      const L = card(k, en);
      assert.equal(L.ar.lines.join(' '), C.tokens(V[k]).join(' '), k + ' words lost');
      assert.ok(widest(L.ar.lines, 'ar', L.ar.size) <= L.width + 0.01, k + ' Arabic too wide');
      if (en) {
        assert.equal(L.en.lines.join(' '), C.tokens(E[k]).join(' '), k + ' English words lost');
        assert.ok(widest(L.en.lines, 'en', L.en.size) <= L.width + 0.01, k + ' English too wide');
        assert.ok(L.en.top >= L.ar.top + L.ar.lines.length * L.ar.lh, k + ' the English runs into the Arabic');
        assert.ok(L.en.credit + 26 <= L.foot, k + ' the credit runs into the footer');
      } else assert.ok(L.ar.top + L.ar.lines.length * L.ar.lh <= L.foot, k + ' the verse runs into the footer');
      assert.ok(L.h >= 1080 && Number.isFinite(L.h));
      if (L.h > 1080) tall++;
    }
    const ms = Date.now() - t0;
    assert.ok(ms < 20000, 'took ' + ms + ' ms');
    assert.ok(tall < 1500, tall + ' of 12,472 cards are taller than square');   // most verses make a square card
  },
  'lines are balanced: as many as a plain fill, none wider, and no lonely last word'() {
    const w = [50, 50, 50, 50, 50, 50, 50], words = w.map((_, i) => 'w' + i), m = t => t === ' ' ? 10 : 50;
    const plain = C.greedy(w, 10, 290).map(([a, b]) => b - a);
    assert.deepEqual(plain, [5, 2]);
    assert.deepEqual(C.balanced(words, m, 290).map(l => l.split(' ').length), [4, 3]);
    for (const k of ['2:255', '18:10', '24:35', '36:82', '55:13']) {
      const size = 60, mm = t => measure(t, 'ar', size), toks = C.tokens(V[k]);
      const g = C.greedy(toks.map(mm), mm(' '), C.CW).map(([a, b]) => toks.slice(a, b).join(' '));
      const b = C.balanced(toks, mm, C.CW);
      assert.equal(b.length, g.length, k);
      assert.ok(widest(b, 'ar', size) <= widest(g, 'ar', size) + 0.01, k);
      if (b.length > 1) assert.ok(mm(b[b.length - 1]) >= 0.45 * widest(b, 'ar', size), k + ' last line too short');
    }
  },
  'a small sign standing alone goes with the word before it'() {
    const mark = String.fromCharCode(0x06DA);
    assert.deepEqual(C.tokens('a ' + mark + ' b'), ['a ' + mark, 'b']);
    assert.deepEqual(C.tokens('  a   b '), ['a', 'b']);
    assert.deepEqual(C.tokens(''), []);
  },
  'the translation makes the card taller or the text smaller, never both untouched'() {
    for (const k of ['2:255', '18:10', '1:1']) {
      const a = card(k, false), b = card(k, true);
      assert.ok(b.h > a.h || b.ar.size < a.ar.size || (b.h === a.h && b.ar.size === a.ar.size && b.en), k);
      assert.ok(b.en && b.en.lines.length > 0, k);
    }
  },
  'the site uses this file'() {
    const app = fs.readFileSync(path.join(WEB, 'app.html'), 'utf8');
    assert.ok(app.includes('<script defer src="card.js"></script>'));
    assert.ok(app.includes('window.QI_CARD'));
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
