// Hearing a verse recited: the reciters the site offers, where each verse's recording is, and the reciter a reader
// picked. The recordings come from AlQuran Cloud's open audio library (Islamic Network, https://alquran.cloud/cdn):
// free, with no account or key, offered for personal and educational use. Each verse is a file of its own, numbered
// through the whole Quran from 1 (al-Fatiha 1:1) to 6236 (an-Nas 114:6). The reciter picked is remembered in the
// browser's own storage (localStorage) and nowhere else.
// Used by the Reader and the study panel in app.html. Also loaded by the Node tests in data-build/tests.
//
// Every function that counts verses takes the surahs' lengths (place.js lensOf), so a verse that does not exist gives
// no file rather than the wrong one.
(function (root) {
  'use strict';

  const BASE = 'https://cdn.islamic.network/quran/audio/';
  const KEY = 'qi.reciter';
  // five well-known reciters, each in the steady murattal style, at the lightest quality the library keeps for them
  // (64 kbps where there is one: Ayat al-Kursi is about 420 KB, half the 128 kbps file). The short name, the one
  // people know them by, is for the player bar on a phone.
  const RECITERS = [
    { id: 'ar.alafasy', kbps: 64, en: 'Mishary Rashid Alafasy', ar: 'مشاري راشد العفاسي', short: ['Alafasy', 'العفاسي'] },
    { id: 'ar.husary', kbps: 64, en: 'Mahmoud Khalil al-Husary', ar: 'محمود خليل الحصري', short: ['al-Husary', 'الحصري'] },
    { id: 'ar.minshawi', kbps: 128, en: 'Muhammad Siddiq al-Minshawi', ar: 'محمد صديق المنشاوي', short: ['al-Minshawi', 'المنشاوي'] },
    { id: 'ar.abdulbasitmurattal', kbps: 64, en: 'Abdul Basit Abdul Samad', ar: 'عبد الباسط عبد الصمد', short: ['Abdul Basit', 'عبد الباسط'] },
    { id: 'ar.mahermuaiqly', kbps: 64, en: 'Maher al-Muaiqly', ar: 'ماهر المعيقلي', short: ['al-Muaiqly', 'المعيقلي'] },
  ];
  const BY_ID = new Map(RECITERS.map(r => [r.id, r]));

  // the reciter of this id, or the first one for an id the site does not offer
  function reciter(id) { return BY_ID.get(id) || RECITERS[0]; }

  // the place of verse v of surah s in the whole Quran, counting from 1; 0 for a verse that does not exist
  function ayahNo(s, v, lens) {
    if (!Number.isInteger(s) || !Number.isInteger(v) || s < 1 || s > 114 || v < 1 || !lens || v > (lens[s] || 0)) return 0;
    let n = v;
    for (let i = 1; i < s; i++) n += lens[i] || 0;
    return n;
  }

  // the recording of verse v of surah s by this reciter; '' for a verse that does not exist
  function url(id, s, v, lens) {
    const n = ayahNo(s, v, lens);
    if (!n) return '';
    const r = reciter(id);
    return BASE + r.kbps + '/' + r.id + '/' + n + '.mp3';
  }

  // the verse after (d = 1) or before (d = -1) in the same surah, or null at either end
  function step(s, v, d, lens) { return ayahNo(s, v + d, lens) ? [s, v + d] : null; }

  // a surah recited from its first verse opens with the Basmala, except al-Fatiha, where the Basmala is the first
  // verse itself, and at-Tawbah, which has none. Its recording is al-Fatiha's first verse.
  function basmalaFirst(s, v) { return v === 1 && s !== 1 && s !== 9; }

  // the reciter this browser picked last, or the first one
  function chosen(store) {
    try { const id = store && store.getItem(KEY); return BY_ID.has(id) ? id : RECITERS[0].id; }
    catch (e) { return RECITERS[0].id; }
  }
  // remember the reciter picked; false where the browser keeps nothing, and the choice then lasts until the page closes
  function choose(store, id) {
    if (!BY_ID.has(id)) return false;
    try { if (!store) return false; store.setItem(KEY, id); return true; }
    catch (e) { return false; }
  }

  const api = { BASE, KEY, RECITERS, reciter, ayahNo, url, step, basmalaFirst, chosen, choose };
  root.QI_RECITE = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
