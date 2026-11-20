// Tests for web/recite.js, hearing a verse recited: node data-build/tests/test_recite.js
// Which recording plays for which verse, which reciters are offered, and the reciter remembered in the browser.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'data.js'));
const P = require(path.join(WEB, 'place.js'));
const R = require(path.join(WEB, 'recite.js'));
const META = window.QURAN_DATA.datasets.surahMeta;
const L = P.lensOf(META);

// a stand-in for the browser's storage, and one that refuses it altogether (some private windows)
class Store {
  constructor(init) { this.m = new Map(Object.entries(init || {})); }
  getItem(k) { return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { this.m.set(k, String(v)); }
}
const Refusing = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('denied'); } };

const tests = {
  'every verse of the Quran has its own recording, in reading order'() {
    let last = 0, count = 0;
    for (let s = 1; s <= 114; s++) for (let v = 1; v <= L[s]; v++) {
      const n = R.ayahNo(s, v, L);
      assert.equal(n, last + 1, s + ':' + v);
      last = n; count++;
    }
    assert.equal(count, 6236);
  },
  'the numbers agree with the library\'s own (its API, read on 20 Nov 2026)'() {
    const seen = { '1:1': 1, '2:1': 8, '2:255': 262, '18:9': 2149, '114:6': 6236 };
    for (const [k, n] of Object.entries(seen)) { const [s, v] = k.split(':').map(Number); assert.equal(R.ayahNo(s, v, L), n, k); }
  },
  'a verse that does not exist has no recording'() {
    for (const [s, v] of [[0, 1], [115, 1], [1, 8], [2, 0], [2, 287], [114, 7], ['2', 1], [2, '255'], [1.5, 1], [NaN, 1], [null, null]]) {
      assert.equal(R.ayahNo(s, v, L), 0, s + ':' + v);
      assert.equal(R.url('ar.alafasy', s, v, L), '', s + ':' + v);
    }
    assert.equal(R.ayahNo(2, 255, null), 0);
  },
  'each reciter\'s recording is at the quality the library keeps for them'() {
    assert.equal(R.url('ar.alafasy', 2, 255, L), 'https://cdn.islamic.network/quran/audio/64/ar.alafasy/262.mp3');
    assert.equal(R.url('ar.minshawi', 2, 255, L), 'https://cdn.islamic.network/quran/audio/128/ar.minshawi/262.mp3');
    assert.equal(R.url('ar.abdulbasitmurattal', 114, 6, L), 'https://cdn.islamic.network/quran/audio/64/ar.abdulbasitmurattal/6236.mp3');
    // a reciter the site does not offer (an edited setting) falls back to the first one
    assert.equal(R.url('ar.nobody', 1, 1, L), 'https://cdn.islamic.network/quran/audio/64/ar.alafasy/1.mp3');
  },
  'five reciters, each named in English and in Arabic'() {
    assert.equal(R.RECITERS.length, 5);
    assert.equal(new Set(R.RECITERS.map(r => r.id)).size, 5);
    for (const r of R.RECITERS) {
      assert.match(r.id, /^ar\.[a-z]+$/);
      assert.ok([64, 128].includes(r.kbps), r.id);
      assert.ok(r.en.length > 4 && !/[؀-ۿ]/.test(r.en), r.id);
      assert.ok(/^[؀-ۿ ]+$/.test(r.ar), r.id);
      // the short name is part of the full one, in both languages
      assert.ok(r.short.length === 2 && r.en.includes(r.short[0].replace(/^al-/, '')) && r.ar.includes(r.short[1]), r.id);
    }
  },
  'stepping stays inside the surah'() {
    assert.deepEqual(R.step(18, 10, 1, L), [18, 11]);
    assert.deepEqual(R.step(18, 10, -1, L), [18, 9]);
    assert.equal(R.step(18, 110, 1, L), null);
    assert.equal(R.step(18, 1, -1, L), null);
    assert.equal(R.step(1, 7, 1, L), null);
  },
  'a surah from its first verse opens with the Basmala, except al-Fatiha and at-Tawbah'() {
    assert.equal(R.basmalaFirst(2, 1), true);
    assert.equal(R.basmalaFirst(114, 1), true);
    assert.equal(R.basmalaFirst(1, 1), false);
    assert.equal(R.basmalaFirst(9, 1), false);
    assert.equal(R.basmalaFirst(2, 2), false);
  },
  'the reciter picked is remembered, and nothing else'() {
    const st = new Store();
    assert.equal(R.chosen(st), 'ar.alafasy');
    assert.equal(R.choose(st, 'ar.husary'), true);
    assert.equal(R.chosen(st), 'ar.husary');
    assert.deepEqual([...st.m.keys()], ['qi.reciter']);
    assert.equal(R.choose(st, 'ar.nobody'), false);
    assert.equal(R.chosen(st), 'ar.husary');
    assert.equal(R.chosen(new Store({ 'qi.reciter': '<b>edited</b>' })), 'ar.alafasy');
  },
  'a browser that keeps nothing still plays, with the first reciter'() {
    assert.equal(R.chosen(Refusing), 'ar.alafasy');
    assert.equal(R.choose(Refusing, 'ar.husary'), false);
    assert.equal(R.chosen(null), 'ar.alafasy');
    assert.equal(R.choose(null, 'ar.husary'), false);
  },
  'repeating a passage: each verse its times, then the next, then the passage again'() {
    const rep = { a: 1, b: 3, each: 2, all: 2 }, seen = [];
    for (let at = [1, 1, 1]; at; at = R.repeatNext(rep, ...at)) seen.push(at.join('.'));
    assert.deepEqual(seen, ['1.1.1', '1.2.1', '2.1.1', '2.2.1', '3.1.1', '3.2.1', '1.1.2', '1.2.2', '2.1.2', '2.2.2', '3.1.2', '3.2.2']);
    assert.equal(seen.length, R.repeatTotal(rep));
    // one verse, once: it plays and the passage is done
    assert.equal(R.repeatNext({ a: 5, b: 5, each: 1, all: 1 }, 5, 1, 1), null);
    assert.equal(R.repeatTotal({ a: 5, b: 5, each: 1, all: 1 }), 1);
  },
  'until the reader stops it, the passage starts over every time'() {
    const rep = { a: 4, b: 6, each: 3, all: 0 };
    assert.deepEqual(R.repeatNext(rep, 6, 3, 1), [4, 1, 2]);
    assert.deepEqual(R.repeatNext(rep, 6, 3, 99), [4, 1, 100]);
    assert.equal(R.repeatTotal(rep), Infinity);
  },
  'a passage is made safe before it plays'() {
    assert.deepEqual(R.repeatPlan({ s: 67, a: 1, b: 5, each: 3, all: 2, gap: 'len' }, L), { s: 67, a: 1, b: 5, each: 3, all: 2, gap: 'len' });
    assert.deepEqual(R.repeatPlan({ s: 67, a: 9, b: 2, each: 4, all: 7, gap: 9 }, L), { s: 67, a: 9, b: 9, each: 3, all: 1, gap: 0 });   // b before a, and choices the site does not offer
    assert.deepEqual(R.repeatPlan({ s: 1, a: 0, b: 99 }, L), { s: 1, a: 1, b: 7, each: 3, all: 1, gap: 0 });                          // past either end of al-Fatiha
    for (const bad of [null, {}, { s: 0, a: 1, b: 1 }, { s: 115, a: 1, b: 1 }, { s: '2', a: 1, b: 1 }]) assert.equal(R.repeatPlan(bad, L), null);
    assert.equal(R.repeatPlan({ s: 2, a: 1, b: 1 }, null), null);
  },
  'the repeat choices are remembered, under one key of their own'() {
    const st = new Store();
    assert.deepEqual(R.prefs(st), { each: 3, all: 1, gap: 0 });
    assert.equal(R.keepPrefs(st, { each: 5, all: 0, gap: 'len', s: 67, a: 1 }), true);
    assert.deepEqual(R.prefs(st), { each: 5, all: 0, gap: 'len' });
    assert.deepEqual(JSON.parse(st.getItem('qi.repeat')), { each: 5, all: 0, gap: 'len' });   // the choices only, not the passage
    assert.equal(R.keepPrefs(st, { each: 4, all: 1, gap: 0 }), false);
    assert.deepEqual(R.prefs(new Store({ 'qi.repeat': '{"each":7,"all":"x","gap":3}' })), { each: 3, all: 1, gap: 3 });   // an edited entry keeps what is valid
    assert.deepEqual(R.prefs(new Store({ 'qi.repeat': 'not json' })), { each: 3, all: 1, gap: 0 });
    assert.deepEqual(R.prefs(Refusing), { each: 3, all: 1, gap: 0 });
    assert.equal(R.keepPrefs(Refusing, { each: 3, all: 1, gap: 0 }), false);
    R.choose(st, 'ar.husary');
    assert.deepEqual([...st.m.keys()].sort(), ['qi.reciter', 'qi.repeat']);
  },
  'the site uses this file, and only this file knows where the recordings are'() {
    const app = fs.readFileSync(path.join(WEB, 'app.html'), 'utf8');
    assert.ok(app.includes('<script defer src="recite.js"></script>'));
    assert.ok(app.includes('const RECITE = window.QI_RECITE || null;'));
    assert.ok(!app.includes('cdn.islamic.network'), 'app.html builds a recording address itself');
    assert.ok(!app.includes("'qi.reciter'"), 'app.html writes the reciter itself');
    assert.ok(!app.includes("'qi.repeat'"), 'app.html writes the repeat choices itself');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
