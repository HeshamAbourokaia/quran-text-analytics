// What a reader keeps on this device: the place they last read in each surah, and the verses they saved.
// It lives in the browser's own storage (localStorage) and nowhere else: nothing is sent anywhere and there is
// no account, so clearing the browser's data for the site forgets it all. Where the browser keeps nothing
// (some private windows), canKeep() says so and the site does not offer these at all.
// Used by the Reader, the study panel and Home in app.html. Also loaded by the Node tests in data-build/tests.
//
// Every function takes the storage as its first argument, so the tests can pass a stand-in. Everything read back
// is checked against the surahs' lengths: a broken or edited entry is dropped, never shown.
(function (root) {
  'use strict';

  const READ = 'qi.read', SAVED = 'qi.saved';
  const RECENT = 6;        // places kept, one for each surah, the latest first
  const MAX_SAVED = 500;   // saved verses kept; saving one more lets the oldest go

  function get(store, key) {
    try { const t = store && store.getItem(key); const v = t ? JSON.parse(t) : []; return Array.isArray(v) ? v : []; }
    catch (e) { return []; }
  }
  function put(store, key, list) {
    try { if (!store) return false; store.setItem(key, JSON.stringify(list)); return true; }
    catch (e) { return false; }
  }

  // whether this browser keeps anything for the site: a test write, taken back at once
  function canKeep(store) {
    try { if (!store) return false; store.setItem('qi.test', '1'); const ok = store.getItem('qi.test') === '1'; store.removeItem('qi.test'); return ok; }
    catch (e) { return false; }
  }

  // lens[s] = the number of verses in surah s (1 to 114). Without it only the shape of a place is checked.
  function lensOf(surahMeta) { const L = new Array(115).fill(0); for (const m of surahMeta || []) if (m && m.n >= 1 && m.n <= 114) L[m.n] = m.verses; return L; }
  function okVerse(s, v, lens) {
    return Number.isInteger(s) && Number.isInteger(v) && s >= 1 && s <= 114 && v >= 1 && (!lens || v <= (lens[s] || 0));
  }
  function parseKey(k) { const m = /^(\d{1,3}):(\d{1,3})$/.exec(String(k)); return m ? [+m[1], +m[2]] : null; }
  const keyOk = (k, lens) => { const p = parseKey(k); return !!p && okVerse(p[0], p[1], lens); };

  // the places read lately, the latest first, one for each surah
  function recent(store, lens) {
    const seen = new Set(), out = [];
    for (const p of get(store, READ)) {
      if (!p || !okVerse(p.s, p.v, lens) || !(p.t > 0) || seen.has(p.s)) continue;
      seen.add(p.s); out.push({ s: p.s, v: p.v, t: p.t });
      if (out.length >= RECENT) break;
    }
    return out;
  }

  // the reader is at verse v of surah s: that becomes the latest place, in place of the one kept for that surah.
  // Returns the new list, or null when the verse does not exist. Staying on the same verse writes nothing.
  function seen(store, s, v, now, lens) {
    if (!okVerse(s, v, lens)) return null;
    const old = recent(store, lens);
    if (old.length && old[0].s === s && old[0].v === v) return old;
    const list = [{ s, v, t: now }].concat(old.filter(p => p.s !== s)).slice(0, RECENT);
    put(store, READ, list);
    return list;
  }

  // the saved verses, the latest saved first
  function saved(store, lens) {
    const seen = new Set(), out = [];
    for (const b of get(store, SAVED)) {
      if (!b || !keyOk(b.k, lens) || seen.has(b.k)) continue;
      seen.add(b.k); out.push({ k: b.k, t: b.t > 0 ? b.t : 0 });
      if (out.length >= MAX_SAVED) break;
    }
    return out;
  }
  const isSaved = (list, k) => (list || []).some(b => b.k === k);

  // save the verse, or let it go if it was saved. Returns the new list, or null when the verse does not exist.
  function toggle(store, k, now, lens) {
    if (!keyOk(k, lens)) return null;
    const old = saved(store, lens);
    const list = isSaved(old, k) ? old.filter(b => b.k !== k) : [{ k, t: now }].concat(old).slice(0, MAX_SAVED);
    put(store, SAVED, list);
    return list;
  }

  // the saved verses in the order of the mushaf, for stepping through them in the Reader
  function inOrder(list) {
    return (list || []).map(b => b.k).sort((a, b) => { const x = parseKey(a), y = parseKey(b); return x[0] - y[0] || x[1] - y[1]; });
  }

  // forget everything kept here
  function forget(store) {
    try { if (store) { store.removeItem(READ); store.removeItem(SAVED); } return true; }
    catch (e) { return false; }
  }

  // whole days between then and now by this device's calendar: 0 is today, 1 is yesterday
  function daysAgo(t, now) {
    const a = new Date(t), b = new Date(now); a.setHours(0, 0, 0, 0); b.setHours(0, 0, 0, 0);
    return Math.max(0, Math.round((b - a) / 864e5));
  }

  const api = { READ, SAVED, RECENT, MAX_SAVED, canKeep, lensOf, okVerse, parseKey, recent, seen, saved, isSaved, toggle, inOrder, forget, daysAgo };
  root.QI_PLACE = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
