// Tests for web/place.js, what the site keeps in the browser for a reader: node data-build/tests/test_place.js
// The latest place read in each surah, and the verses saved. Nothing here may throw, whatever the browser does.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'data.js'));
const P = require(path.join(WEB, 'place.js'));
const META = window.QURAN_DATA.datasets.surahMeta;
const L = P.lensOf(META);

// a stand-in for the browser's storage, counting its writes
class Store {
  constructor(init) { this.m = new Map(Object.entries(init || {})); this.writes = 0; }
  getItem(k) { return this.m.has(k) ? this.m.get(k) : null; }
  setItem(k, v) { this.writes++; this.m.set(k, String(v)); }
  removeItem(k) { this.m.delete(k); }
}
// a browser that refuses storage altogether (some private windows), and one that is full
const Refusing = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('denied'); }, removeItem() { throw new Error('denied'); } };
class Full extends Store { setItem() { throw new Error('QuotaExceededError'); } }

const DAY = 864e5, T = new Date(2026, 10, 19, 12, 0).getTime();
const places = st => P.recent(st, L).map(p => p.s + ':' + p.v);

const tests = {
  'the surah lengths come from the site data'() {
    assert.equal(L[1], 7); assert.equal(L[2], 286); assert.equal(L[114], 6);
    assert.equal(L.slice(1).reduce((a, b) => a + b, 0), 6236);
  },
  'one place for each surah, the latest first'() {
    const st = new Store();
    P.seen(st, 2, 10, T, L); P.seen(st, 18, 5, T + 1, L); P.seen(st, 2, 40, T + 2, L);
    assert.deepEqual(places(st), ['2:40', '18:5']);
  },
  'only the six latest surahs are kept'() {
    const st = new Store();
    [1, 2, 3, 4, 5, 6, 7, 8].forEach((s, i) => P.seen(st, s, 1, T + i, L));
    assert.deepEqual(places(st), ['8:1', '7:1', '6:1', '5:1', '4:1', '3:1']);
  },
  'staying on the same verse writes nothing'() {
    const st = new Store();
    P.seen(st, 36, 12, T, L); const w = st.writes;
    P.seen(st, 36, 12, T + 5000, L); P.seen(st, 36, 12, T + 9000, L);
    assert.equal(st.writes, w);
    P.seen(st, 36, 13, T + 9000, L); assert.equal(st.writes, w + 1);
  },
  'a verse that does not exist is refused'() {
    const st = new Store();
    for (const [s, v] of [[1, 8], [115, 1], [0, 1], [2, 0], [2, 287], [2.5, 3], [2, '3']]) assert.equal(P.seen(st, s, v, T, L), null, s + ':' + v);
    assert.equal(P.toggle(st, '1:8', T, L), null); assert.equal(P.toggle(st, '2:255 ', T, L), null); assert.equal(P.toggle(st, 'x', T, L), null);
    assert.equal(st.writes, 0);
  },
  'saving a verse twice takes it off again'() {
    const st = new Store();
    P.toggle(st, '2:255', T, L); P.toggle(st, '18:10', T + 1, L);
    assert.deepEqual(P.saved(st, L).map(b => b.k), ['18:10', '2:255']);
    assert.ok(P.isSaved(P.saved(st, L), '2:255'));
    P.toggle(st, '2:255', T + 2, L);
    assert.deepEqual(P.saved(st, L).map(b => b.k), ['18:10']);
    assert.ok(!P.isSaved(P.saved(st, L), '2:255'));
  },
  'saved verses step through in the order of the mushaf'() {
    const st = new Store();
    ['36:1', '2:255', '112:1', '2:3', '18:10'].forEach((k, i) => P.toggle(st, k, T + i, L));
    assert.deepEqual(P.inOrder(P.saved(st, L)), ['2:3', '2:255', '18:10', '36:1', '112:1']);
  },
  'saving more than the limit lets the oldest go'() {
    const st = new Store(), keys = [];
    for (let s = 1; s <= 114 && keys.length < P.MAX_SAVED + 1; s++) for (let v = 1; v <= L[s] && keys.length < P.MAX_SAVED + 1; v++) keys.push(s + ':' + v);
    keys.forEach((k, i) => P.toggle(st, k, T + i, L));
    const got = P.saved(st, L);
    assert.equal(got.length, P.MAX_SAVED);
    assert.equal(got[0].k, keys[keys.length - 1]);
    assert.ok(!P.isSaved(got, keys[0]));
  },
  'broken or edited data is dropped, never shown'() {
    const st = new Store({
      'qi.read': JSON.stringify([{ s: 2, v: 999, t: T }, { s: 'x', v: 1, t: T }, null, { s: 3, v: 4 }, { s: 18, v: 10, t: T }, { s: 18, v: 20, t: T - 1 }]),
      'qi.saved': JSON.stringify([{ k: '2:255', t: T }, { k: '2:255', t: T - 1 }, { k: '1:9' }, { k: '<b>' }, 7, { k: '36:1' }]),
    });
    assert.deepEqual(places(st), ['18:10']);
    assert.deepEqual(P.saved(st, L), [{ k: '2:255', t: T }, { k: '36:1', t: 0 }]);
    assert.deepEqual(P.recent(new Store({ 'qi.read': 'not json {' }), L), []);
    assert.deepEqual(P.saved(new Store({ 'qi.saved': '{"k":"2:255"}' }), L), []);
  },
  'a browser that keeps nothing: told apart, and nothing throws'() {
    assert.equal(P.canKeep(null), false);
    assert.equal(P.canKeep(Refusing), false);
    assert.equal(P.canKeep(new Full()), false);
    assert.equal(P.canKeep(new Store()), true);
    for (const st of [null, Refusing, new Full()]) {
      assert.deepEqual(P.recent(st, L), []); assert.deepEqual(P.saved(st, L), []);
      assert.doesNotThrow(() => { P.seen(st, 2, 1, T, L); P.toggle(st, '2:1', T, L); P.forget(st); });
    }
    const st = new Store(); P.canKeep(st); assert.equal(st.getItem('qi.test'), null);
  },
  'forgetting clears the places and the saved verses'() {
    const st = new Store();
    P.seen(st, 2, 10, T, L); P.toggle(st, '2:255', T, L);
    P.forget(st);
    assert.deepEqual(P.recent(st, L), []); assert.deepEqual(P.saved(st, L), []);
  },
  'days are counted by the calendar, not by 24 hours'() {
    const late = new Date(2026, 10, 18, 23, 59).getTime(), early = new Date(2026, 10, 19, 0, 1).getTime();
    assert.equal(P.daysAgo(late, early), 1);
    assert.equal(P.daysAgo(early, new Date(2026, 10, 19, 23, 59).getTime()), 0);
    assert.equal(P.daysAgo(T - 3 * DAY, T), 3);
    assert.equal(P.daysAgo(T + DAY, T), 0);   // a clock set back does not give a negative day
  },
  'the site uses this file, and keeps nothing behind its back'() {
    const app = fs.readFileSync(path.join(WEB, 'app.html'), 'utf8');
    assert.ok(app.includes('<script defer src="place.js"></script>'));
    assert.ok(app.includes('const PLACE = window.QI_PLACE || null;'));
    for (const own of ["'qi.read'", "'qi.saved'", 'localStorage.setItem(\'qi', 'sessionStorage', 'indexedDB'])
      assert.ok(!app.includes(own), 'app.html has ' + own);
    // the only other thing app.html keeps itself is the reader's choice of simple or detailed explanations; the
    // reciter picked is kept by recite.js, and test_recite.js holds it to that one key
    const sets = app.match(/localStorage\.setItem\([^)]*\)/g) || [];
    assert.deepEqual(sets, ['localStorage.setItem(DEPTH_KEY, d)']);
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
