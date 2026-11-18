// What one verse shares with the rest of the Quran, read from the word index (words.js): the verses that say it
// again word for word, the verses nearest to it by the dictionary words they share, and its own words from the
// rarest. Used by the verse study panel in app.html. Also loaded by the Node tests in data-build/tests.
//
// Two verses are compared by their dictionary words (lemmas), not by their spelling in the text, so «رحمته» and
// «الرحمة» count as the same word. A word that comes in few verses says more than a common one, so each shared
// word is weighted by how few verses hold it (inverse document frequency), and the score is the cosine between
// the two verses: a long verse does not win just by being long. Plain counting in the browser; nothing is sent
// anywhere.
(function (root) {
  'use strict';

  const COMMON = 0.05;   // a word found in more than one verse in twenty links too many verses to mean anything
  const RARE = 6;        // one shared word alone is a link only when it comes in this many verses at most
  const FLOOR = 0.18;    // below this score two verses are not offered as alike
  const SIGNS = '0123456789abcdefghijklmnopqrstuvwxyz';

  // Every verse in order: where its words sit in the index, the dictionary words in it, and the weight of each.
  //
  // The word index writes lemmas without vowel marks, so one spelling can cover several dictionary words: «جنة» is
  // the garden (janna) and the jinn (jinna). VAR (lemma-variants.js) lists the words behind each such spelling and
  // SENSE gives, for every word of the text, which of them it is. A word's id is its lemma, with «#» and that
  // number where the spelling is shared. Without the two tables the root tells some of these words apart.
  function index(W, VAR, SENSE) {
    VAR = VAR || {};
    const exact = typeof SENSE === 'string' && SENSE.length === W.key.length;
    const n = W.key.length, ids = new Array(n);
    for (let i = 0; i < n; i++) { const l = W.lemma[i]; ids[i] = !l ? '' : exact && VAR[l] ? l + '#' + SIGNS.indexOf(SENSE[i]) : l; }
    const tok = i => (exact || !ids[i] ? ids[i] : ids[i] + '|' + (W.root[i] || ''));
    const keys = [], at = new Map(), span = [], toks = [];
    for (let i = 0; i < n; i++) {
      let j = at.get(W.key[i]);
      if (j === undefined) { j = keys.length; at.set(W.key[i], j); keys.push(W.key[i]); span.push([i, i + 1]); toks.push(new Set()); }
      else span[j][1] = i + 1;
      const t = tok(i);
      if (t) toks[j].add(t);
    }
    const N = keys.length, df = new Map(), tot = new Map(), inV = new Map();
    for (const id of ids) if (id) tot.set(id, (tot.get(id) || 0) + 1);
    for (const s of toks) for (const t of s) df.set(t, (df.get(t) || 0) + 1);
    for (let j = 0; j < N; j++) {
      const seen = new Set();
      for (let i = span[j][0]; i < span[j][1]; i++) { const id = ids[i]; if (id && !seen.has(id)) { seen.add(id); inV.set(id, (inV.get(id) || 0) + 1); } }
    }
    const cap = Math.round(N * COMMON), w = new Map(), post = new Map(), len = new Float64Array(N);
    for (const [t, c] of df) if (c <= cap) w.set(t, Math.log(N / c));
    toks.forEach((s, j) => {
      let q = 0;
      for (const t of s) { const x = w.get(t); if (x === undefined) continue; q += x * x; let p = post.get(t); if (!p) post.set(t, (p = [])); p.push(j); }
      len[j] = Math.sqrt(q);
    });
    // verses made of the same words in the same order, whatever their vowel marks
    const twin = new Map(), same = new Array(N);
    for (let j = 0; j < N; j++) {
      let t = '';
      for (let i = span[j][0]; i < span[j][1]; i++) t += W.norm[i] + ' ';
      let a = twin.get(t);
      if (!a) twin.set(t, (a = []));
      a.push(j);
    }
    for (const a of twin.values()) for (const j of a) same[j] = a;
    return { W, VAR, exact, N, ids, keys, at, span, toks, df, tot, inV, w, post, len, same };
  }

  // how many words the verse has
  function count(IX, k) { const j = IX.at.get(k); return j === undefined ? 0 : IX.span[j][1] - IX.span[j][0]; }

  // the other verses that say this one again, word for word, in the order of the mushaf
  function same(IX, k) {
    const j = IX.at.get(k);
    return j === undefined ? [] : IX.same[j].filter(u => u !== j).map(u => IX.keys[u]);
  }

  // The verses nearest to this one by the dictionary words they share. A verse that repeats it word for word is
  // left to same(); verses that repeat each other are offered once, with how many more say the same (twins).
  // Each result lists the ids of the shared words, the rarest first (compare them with IX.ids to mark the words).
  function like(IX, k, max) {
    const j = IX.at.get(k);
    if (j === undefined || !IX.len[j]) return [];
    const mine = new Set(IX.same[j]), score = new Map(), shared = new Map();
    for (const t of IX.toks[j]) {
      const x = IX.w.get(t);
      if (x === undefined) continue;
      for (const u of IX.post.get(t)) {
        if (mine.has(u)) continue;
        score.set(u, (score.get(u) || 0) + x * x);
        let a = shared.get(u);
        if (!a) shared.set(u, (a = []));
        a.push(t);
      }
    }
    const out = [];
    for (const [u, s] of score) {
      const a = shared.get(u), c = s / (IX.len[j] * IX.len[u]);
      if (c < FLOOR || (a.length < 2 && IX.df.get(a[0]) > RARE)) continue;
      out.push({ u, score: c, a });
    }
    out.sort((p, q) => q.score - p.score || p.u - q.u);
    const seen = new Set(), list = [];
    for (const r of out) {
      const set = IX.same[r.u];
      if (seen.has(set)) continue;
      seen.add(set);
      list.push({ k: IX.keys[r.u], score: r.score, twins: set.length - 1,
        shared: r.a.sort((p, q) => IX.df.get(p) - IX.df.get(q)).map(t => (IX.exact ? t : t.slice(0, t.indexOf('|')))) });
      if (list.length >= (max || 5)) break;
    }
    return list;
  }

  // The verse's own dictionary words, the rarest first. id: the word; l: its spelling in the index, to search
  // for; dict: the dictionary word with its vowel marks, where the spelling covers several (amb); surf: how it
  // is written here, the first time; sense: which of the words behind the spelling it is; n: how many times it
  // comes in the Quran in all its forms; verses: in how many verses; here: how many times in this verse.
  function words(IX, k) {
    const j = IX.at.get(k);
    if (j === undefined) return [];
    const W = IX.W, m = new Map();
    for (let i = IX.span[j][0]; i < IX.span[j][1]; i++) {
      const id = IX.ids[i], l = W.lemma[i];
      if (!id || l.length < 2) continue;   // a joined letter (و ف ب ل ك) is not a word to count
      const e = m.get(id);
      if (e) { e.here++; continue; }
      const cut = id.indexOf('#'), sense = cut < 0 ? 0 : +id.slice(cut + 1), v = IX.VAR[l];
      m.set(id, { id, l, amb: cut >= 0, sense, dict: cut >= 0 && v && v[sense] ? v[sense][0] : '', surf: W.surface[i], i,
        n: IX.tot.get(id), verses: IX.inV.get(id), here: 1 });
    }
    return [...m.values()].sort((a, b) => a.n - b.n || a.i - b.i);
  }

  const api = { index, count, same, like, words, COMMON, RARE, FLOOR };
  root.QI_STUDY = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
