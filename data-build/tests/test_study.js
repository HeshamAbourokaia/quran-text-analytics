// Tests for web/study.js against the site's own word index: node data-build/tests/test_study.js
'use strict';
const assert = require('assert/strict');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'words.js'));
require(path.join(WEB, 'lemma-variants.js'));
const S = require(path.join(WEB, 'study.js'));
const W = window.QURAN_WORDS, VAR = window.QURAN_LEMMA_VARIANTS, SENSE = window.QURAN_WORD_SENSE;
const T0 = Date.now(), IX = S.index(W, VAR, SENSE), BUILD_MS = Date.now() - T0;
const PLAIN = S.index(W);   // without the tables that tell same-spelling words apart

const like = (k, n) => S.like(IX, k, n);
const keysOf = (k, n) => like(k, n).map(r => r.k);

const tests = {
  'the index holds every verse and every word'() {
    assert.equal(IX.N, 6236);
    assert.equal(IX.keys[0], '1:1');
    assert.equal(IX.keys[6235], '114:6');
    assert.equal(IX.keys.reduce((s, k) => s + S.count(IX, k), 0), 77429);
    assert.equal(S.count(IX, '1:1'), 4);
    assert.equal(S.count(IX, '2:255'), 50);
    assert.equal(S.count(IX, '9:999'), 0);
  },
  'a verse said again word for word finds every repeat, and only those'() {
    const r = S.same(IX, '55:13');
    assert.equal(r.length, 30);                                   // «Which of your Lord's favours...» comes 31 times
    assert.ok(r.every(k => k.startsWith('55:')));
    assert.ok(!r.includes('55:13'));
    assert.deepEqual(S.same(IX, '2:1'), ['3:1', '29:1', '30:1', '31:1', '32:1']);   // الم opens six surahs
    assert.deepEqual(S.same(IX, '94:5'), []);                     // 94:6 lacks the opening «so»: near, not the same
    assert.deepEqual(S.same(IX, '1:1'), []);
    assert.deepEqual(S.same(IX, '9:999'), []);
  },
  'repeats are mutual: every verse of a group lists all the others'() {
    for (const k of ['55:13', '2:1', '26:8', '77:15', '54:17']) {
      const g = S.same(IX, k);
      assert.ok(g.length > 0, k);
      for (const o of g) assert.deepEqual([...S.same(IX, o), o].sort(), [...g, k].sort(), k + ' and ' + o);
    }
  },
  'the nearest verses are the ones a reader would expect'() {
    // «Allah, no god but He, the Living, the Sustaining», and «He knows what is before them and behind them»
    assert.deepEqual(keysOf('2:255', 2).sort(), ['20:110', '3:2']);
    assert.ok(keysOf('114:6').includes('11:119'));                 // «jinn and mankind together»
    assert.equal(keysOf('1:1')[0], '27:30');                       // the Basmala inside Solomon's letter
    assert.equal(keysOf('94:5')[0], '94:6');
    assert.ok(like('94:5')[0].score > 0.99);
    assert.equal(keysOf('20:25')[0], '94:1');                      // «expand my breast» and «did We not expand your breast»
    assert.ok(keysOf('7:54').includes('10:3'));                    // six days, then the Throne
    assert.equal(keysOf('97:1')[0], '97:2');
    assert.equal(keysOf('2:152')[0], '14:7');                      // thanks and ingratitude
  },
  'a verse with only common words, or no dictionary words, offers nothing rather than noise'() {
    assert.deepEqual(like('112:1'), []);                           // «one» alone comes in too many verses to be a link
    assert.deepEqual(like('2:1'), []);                             // opening letters have no dictionary word
    assert.deepEqual(like('108:1'), []);                           // «abundance» comes nowhere else
    assert.deepEqual(like('9:999'), []);
  },
  'a verse that repeats is offered once, with how many more say the same'() {
    assert.ok(!keysOf('55:13', 50).some(k => S.same(IX, '55:13').includes(k)));
    const r = like('53:55').find(x => x.k === '55:13');
    assert.ok(r, '53:55 should point at the refrain of surah 55');
    assert.equal(r.twins, 30);
    assert.equal(like('53:55').filter(x => x.k.startsWith('55:')).length, 1);
  },
  'every result, for every verse, keeps the rules'() {
    let withMatch = 0;
    for (const k of IX.keys) {
      const r = like(k);
      if (r.length) withMatch++;
      assert.ok(r.length <= 5, k);
      let prev = Infinity;
      for (const x of r) {
        assert.notEqual(x.k, k);
        assert.ok(x.score >= S.FLOOR && x.score <= 1.0000001 && x.score <= prev, k + ' ' + x.k + ' ' + x.score);
        prev = x.score;
        assert.ok(x.shared.length >= 1 && x.shared.every(l => l && !l.includes('|') && IX.tot.has(l)), k);
        assert.equal(new Set(x.shared).size, x.shared.length, k + ' ' + x.k + ' lists a shared word twice');
      }
    }
    assert.ok(withMatch > 5500 && withMatch < 6236, 'verses with a match: ' + withMatch);
    assert.equal(like('2:255', 3).length, 3);
    assert.ok(like('2:255', 12).length > 5);
  },
  'a single shared word links two verses only when it is rare'() {
    for (const k of ['53:55', '19:4', '33:56', '38:34', '2:286', '12:4', '21:87']) {
      for (const x of like(k, 20)) if (x.shared.length === 1) assert.ok(IX.inV.get(x.shared[0]) <= S.RARE, k + ' ' + x.k + ' ' + x.shared[0]);
    }
  },
  'words that share a spelling are told apart'() {
    assert.equal(SENSE.length, W.key.length);
    assert.ok(IX.exact && !PLAIN.exact);
    // every dictionary word behind a shared spelling is counted as the table of variants counts it
    for (const l in VAR) VAR[l].forEach((v, i) => assert.equal(IX.tot.get(l + '#' + i), v[1], l + ' ' + v[0]));
    // the last verse of the Quran speaks of the jinn (jinna), not the garden (janna), though both are written «جنة»
    const jinn = S.words(IX, '114:6').find(w => w.l === 'جنة'), garden = S.words(IX, '2:35').find(w => w.l === 'جنة');
    assert.ok(jinn.amb && garden.amb && jinn.id !== garden.id);
    assert.equal(jinn.n + garden.n, VAR['جنة'].slice(0, 2).reduce((s, v) => s + v[1], 0));
    assert.ok(jinn.n < 20 && garden.n > 100, jinn.n + ' ' + garden.n);
    assert.equal(jinn.dict, VAR['جنة'][jinn.sense][0]);
    // slumber in Ayat al-Kursi comes once, though «سنة» is also the year and the way
    assert.equal(S.words(IX, '2:255').find(w => w.l === 'سنة').n, 1);
    // so the garden does not make 114:6 look like a verse about Paradise
    assert.ok(!like('114:6', 20).some(x => x.shared.length === 1 && x.shared[0] === garden.id));
    // without the tables the counts fall back to the spelling, and the engine still answers
    assert.equal(S.words(PLAIN, '114:6').find(w => w.l === 'جنة').n, VAR['جنة'].reduce((s, v) => s + v[1], 0));
    assert.equal(S.like(PLAIN, '2:255')[0].k, '3:2');
    assert.ok(S.like(PLAIN, '2:255').every(x => x.shared.every(l => !l.includes('|'))));
  },
  'a verse lists its dictionary words from the rarest, each counted in all its forms'() {
    const total = new Map();
    W.lemma.forEach((l, i) => { if (l) total.set(IX.ids[i], (total.get(IX.ids[i]) || 0) + 1); });
    const ws = S.words(IX, '2:255');
    assert.equal(ws[0].n, 1);                                      // a word that comes only here
    assert.equal(ws.find(w => w.l === 'كرسي').n, 2);
    assert.equal(ws.find(w => w.l === 'كرسي').surf, W.surface[ws.find(w => w.l === 'كرسي').i]);
    for (const k of ['2:255', '1:1', '24:35', '36:82', '112:1']) {
      const list = S.words(IX, k);
      let prev = 0, here = 0;
      for (const w of list) {
        assert.ok(w.l.length > 1, k + ' lists a joined letter');
        assert.equal(w.n, total.get(w.id), k + ' ' + w.id);
        assert.equal(w.amb, !!VAR[w.l], k + ' ' + w.l);
        if (!w.amb) assert.equal(w.id, w.l);
        assert.ok(w.n >= prev && w.here >= 1 && w.verses >= 1 && w.verses <= w.n, k + ' ' + w.l);
        prev = w.n; here += w.here;
      }
      assert.ok(here <= S.count(IX, k), k);
      assert.equal(new Set(list.map(w => w.id)).size, list.length, k);
    }
    assert.deepEqual(S.words(IX, '1:1').map(w => w.l), ['اسم', 'رحمن', 'رحيم', 'الله']);
    assert.deepEqual(S.words(IX, '2:1'), []);
    assert.deepEqual(S.words(IX, '9:999'), []);
    assert.equal(S.words(IX, '36:82').find(w => w.l === 'كان').here, 2);   // «Be», and it is
  },
  'fast enough to run when a panel opens'() {
    assert.ok(BUILD_MS < 1500, 'index took ' + BUILD_MS + ' ms');
    const t = Date.now(), ks = ['2:255', '2:282', '24:35', '4:12', '5:3', '2:102'];
    for (let i = 0; i < 20; i++) for (const k of ks) { like(k); S.words(IX, k); S.same(IX, k); }
    assert.ok((Date.now() - t) / (20 * ks.length) < 10, 'slow: ' + ((Date.now() - t) / (20 * ks.length)).toFixed(1) + ' ms');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
