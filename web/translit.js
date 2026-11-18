// Arabic words typed in English letters (rahma, sabr, jannah, ra7ma): which word of the Quran is meant.
// Also loaded by the Node tests in data-build/tests.
//
// roman.js gives the sound of every dictionary word (built by data-build/pipeline/roman.py, which lists the
// signs). Here a sound becomes the spelling shown to a reader (raHmap is «rahma») and the spellings a reader
// might type (rahma, rahmat), and a typed word is compared with them by sound: sh, kh, gh, th and dh are one
// letter each, q is k, o is u, e is i, a doubled letter counts once, and vowels may differ a little.
// Plain matching in the browser; nothing is sent anywhere.
(function (root) {
  'use strict';

  const APOS = '\u2019';
  const SHOW = { v: 'th', H: 'h', x: 'kh', '*': 'dh', $: 'sh', S: 's', D: 'd', T: 't', Z: 'z', g: 'gh', A: 'a', I: 'i', U: 'u' };
  const isV = c => c === 'a' || c === 'i' || c === 'u';

  // the spelling shown to a reader: rahma, salah, qur’an, isma’il
  function spell(s) {
    let out = '';
    for (let i = 0; i < s.length; i++) {
      const c = s[i], end = i === s.length - 1;
      if (c === "'" || c === 'E') { if (out && !end && !out.endsWith(APOS)) out += APOS; }
      else if (c === 'p') out += end && s[i - 1] === 'A' ? 'h' : end ? '' : 't';
      else out += SHOW[c] || c;
    }
    return out.replace(new RegExp(APOS + '$'), '');
  }

  // the ways a reader may write one sound, in Latin letters: a ث as th or s, a ذ as dh, z or th, a ظ as z, dh
  // or th, a ض as d or z, the ة silent, as h or as t, and aw / ay also as the o / e they are often said as
  const ALT = { v: ['th', 's'], '*': ['dh', 'z', 'th'], Z: ['z', 'dh', 'th'], D: ['d', 'z'] };
  const PLAIN = { H: 'h', x: 'kh', $: 'sh', S: 's', T: 't', g: 'gh', A: 'a', I: 'i', U: 'u', "'": '', E: '' };
  function spellings(s) {
    let outs = [''];
    const add = alts => { const next = []; for (const o of outs) for (const a of alts) if (next.length < 36) next.push(o + a); outs = next; };
    for (let i = 0; i < s.length; i++) {
      const c = s[i], n = s[i + 1], end = i === s.length - 1;
      if (ALT[c]) add(ALT[c]);
      else if (c === 'p') add(end ? ['', 'h', 't'] : ['t']);
      else if (c === 'a' && (n === 'w' || n === 'y') && !/[aiuAIU]/.test(s[i + 2] || '') && s[i + 2] !== n) { add(['a' + n, n === 'w' ? 'u' : 'i']); i++; }
      else add([c in PLAIN ? PLAIN[c] : c]);
    }
    return [...new Set(outs)];
  }

  // a typed word, or one of the spellings above, by its sound. The digits of the chat alphabet count as
  // letters when they sit among letters: 7 is ح, 3 is ع, 2 is ء, 5 is خ, 6 is ط, 9 is ص
  const chat = t => String(t).toLowerCase().replace(/[a-z2356789']*[a-z][a-z2356789']*/g, w => w.replace(/7/g, 'h').replace(/5/g, 'kh').replace(/6/g, 't').replace(/9/g, 's').replace(/[23]/g, ''));
  function key(t) {
    let x = chat(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z]/g, '');
    x = x.replace(/ph/g, 'f').replace(/sh/g, 'C').replace(/kh/g, 'X').replace(/gh/g, 'G').replace(/[td]h/g, m => m[0])
      .replace(/[cq]/g, 'k').replace(/g/g, 'j').replace(/p/g, 'b').replace(/v/g, 'f').replace(/o/g, 'u').replace(/e/g, 'i')
      .replace(/C/g, 'c').replace(/X/g, 'x').replace(/G/g, 'g');
    x = x.replace(/(.)\1+/g, '$1').replace(/au/g, 'aw').replace(/ai/g, 'ay').replace(/uw(?![aiu])/g, 'u').replace(/iy(?![aiu])/g, 'i')
      .replace(/(.)\1+/g, '$1');
    return x.length > 3 ? x.replace(/([aiu])h$/, '$1') : x;
  }

  // how far apart two keys sound: a different vowel is a small step, a vowel or a w / y more or less is half
  // a step, letters often swapped (d and z, k and kh, h and kh, j and gh) half a step, another consonant a full one
  const SOFT = { dz: 1, zd: 1, kx: 1, xk: 1, hx: 1, xh: 1, jg: 1, gj: 1, wu: 1, uw: 1, yi: 1, iy: 1 };
  const light = c => isV(c) || c === 'w' || c === 'y';
  function dist(a, b, cap) {
    let p = [0];
    for (let j = 1; j <= b.length; j++) p[j] = p[j - 1] + (light(b[j - 1]) ? 0.5 : 1);
    for (let i = 1; i <= a.length; i++) {
      const ca = a[i - 1], c = [p[0] + (light(ca) ? 0.5 : 1)];
      let low = c[0];
      for (let j = 1; j <= b.length; j++) {
        const cb = b[j - 1];
        const sub = ca === cb ? 0 : isV(ca) && isV(cb) ? 0.25 : SOFT[ca + cb] ? 0.5 : 1;
        c[j] = Math.min(p[j] + (light(ca) ? 0.5 : 1), c[j - 1] + (light(cb) ? 0.5 : 1), p[j - 1] + sub);
        if (c[j] < low) low = c[j];
      }
      if (low > cap) return cap + 1;
      p = c;
    }
    return p[b.length];
  }
  // plain letter distance, to put the spelling nearest to what was typed first
  function lev(a, b) {
    let p = [...Array(b.length + 1).keys()];
    for (let i = 1; i <= a.length; i++) {
      const c = [i];
      for (let j = 1; j <= b.length; j++) c[j] = Math.min(p[j] + 1, c[j - 1] + 1, p[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      p = c;
    }
    return p[b.length];
  }
  const letters = s => chat(s).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z]/g, '');
  const soft = s => letters(s).replace(/o/g, 'u').replace(/e/g, 'i');   // as typed, but for o / u and e / i

  // ---- the index: every sound of every word, with its keys ----
  // roman: {word without marks: "sound sound"}; count: how often each word comes (a Map or an object)
  function index(roman, count) {
    const n = l => (count ? (count.get ? count.get(l) : count[l]) : 0) || 0;
    const rows = [];
    for (const l in roman) {
      const c = n(l);
      if (count && !c) continue;
      for (const s of roman[l].split(' ')) {
        const lat = spell(s);
        const sp = spellings(s);
        rows.push({ l, s, lat, n: c, soft: [...new Set(sp.map(soft))], keys: [...new Set(sp.map(key))].filter(Boolean) });
      }
    }
    return { rows, first: new Map(Object.keys(roman).map(l => [l, spell(roman[l].split(' ')[0])])), one: l => roman[l] && roman[l].indexOf(' ') < 0 };
  }

  // a typed word as it stands, and without the Arabic article in front (al-, el-, and before a sun letter:
  // ar-rahman, as-salat)
  function forms(text) {
    const t = chat(String(text).trim()), all = letters(t), out = [all];
    const apart = t.match(/^(?:[ae]l|[ae](sh|th|dh|[lnrstdz]))[-\s]+(.+)$/);
    if (apart) out.unshift(letters(apart[2]));
    else { const m = all.match(/^[ae]l(?=[a-z]{3})/) || all.match(/^[ae]([nrstdz])(?=\1[a-z]{2})/); if (m) out.push(all.slice(m[0].length)); }
    return [...new Set(out)].filter(f => f.length >= 2);
  }

  // the words a typed text sounds like, best first: [{l, lat, n, how}]. how = 'exact' (the same sound), 'sound'
  // (a vowel differs), 'form' (a regular plural of it: muslimin, salihat), 'near' (a letter away). The same
  // sound comes first; among words that fit equally, the common one, unless a rarer one is spelled more like
  // what was typed.
  function match(text, IX, max) {
    if (!IX || /[\u0600-\u06FF]/.test(text) || /^[\s\d:.,-]*$/.test(String(text))) return [];
    const best = new Map();
    const take = (r, how, d, f) => {
      const sf = soft(f), far = Math.min(...r.soft.map(x => lev(sf, x)));
      const score = Math.log2(r.n + 1) - 3 * far - 6 * d - (how === 'form' ? 2 : 0), cur = best.get(r.l);
      if (!cur || score > cur.score) best.set(r.l, { l: r.l, lat: r.lat, n: r.n, how, d, score });
    };
    const scan = (f, how) => {
      const k = key(f), L = k.length;
      if (L < 2) return;
      const cap = how ? 0 : L >= 7 ? 1.5 : L >= 5 ? 1 : L >= 3 ? 0.5 : 0;
      for (const r of IX.rows) for (const t of r.keys) {
        if (Math.abs(t.length - L) > 3) continue;
        if (t === k) { take(r, how || 'exact', 0, f); continue; }
        if (!cap || (t[0] !== k[0] && !(light(t[0]) && light(k[0])))) continue;
        const d = dist(k, t, cap);
        if (d <= cap) take(r, d <= 0.5 ? 'sound' : 'near', d, f);
      }
    };
    const fs = forms(text);
    for (const f of fs) scan(f);
    // nothing sounds the same: a regular plural of a word that does (muslimin, kafirun, salihat)
    if (![...best.values()].some(b => b.how !== 'near')) for (const f of fs) { const m = f.match(/^(.{3,})(?:een|iin|in|oon|uun|un|aat|at)$/); if (m) scan(m[1], 'form'); }
    const tier = b => (b.how === 'exact' ? 0 : b.how === 'near' ? 2 : 1);
    return [...best.values()].sort((a, b) => tier(a) - tier(b) || b.score - a.score).slice(0, max || 5).map(b => ({ l: b.l, lat: b.lat, n: b.n, how: b.how }));
  }

  // ---- phrases known by their sound ----
  const PHRASES = [
    ['بسم الله', 'bismillah', 'bismi allah', 'bismillahi', 'besmellah'],
    ['الحمد لله', 'alhamdulillah', 'alhamdu lillah', 'al hamdu lillah', 'hamdulillah', 'elhamdulillah', 'alhamdolillah'],
    ['سبحان الله', 'subhanallah', 'subhan allah', 'sobhan allah', 'subhana allah'],
    ['إن شاء الله', 'inshallah', 'insha allah', 'in sha allah', 'inshaallah', 'in shaa allah'],
    ['ما شاء الله', 'mashallah', 'masha allah', 'ma sha allah', 'mashaallah'],
    ['لا إله إلا الله', 'la ilaha illa allah', 'la ilaha illallah', 'la ilaha ill allah', 'la ilah illa allah'],
    ['رب العالمين', 'rabbil alamin', 'rabb al alamin', 'rabbul alamin', 'rabbi al alamin', 'rabb il alamin'],
    ['الرحمن الرحيم', 'ar rahman ar rahim', 'al rahman al rahim', 'rahman rahim', 'ar rahmani ar rahim'],
    ['الصراط المستقيم', 'sirat al mustaqim', 'siratal mustaqim', 'as sirat al mustaqim', 'sirat mustaqim'],
    ['يوم القيامة', 'yawm al qiyama', 'yawmul qiyama', 'yawm il qiyama', 'yom el qiyama', 'yawmal qiyama'],
    ['يوم الدين', 'yawm al din', 'yawmid din', 'yawm ad din', 'yawmi din', 'yom el din'],
    ['أهل الكتاب', 'ahl al kitab', 'ahlul kitab', 'ahlal kitab', 'ahlil kitab', 'ahl kitab'],
    ['سلام عليكم', 'salam alaykum', 'salamun alaykum', 'assalamu alaykum', 'as salamu alaykum', 'salamu alaykum'],
    ['إنا لله', 'inna lillah', 'inna lillahi', 'innalillahi', 'inna li allah'],
    ['قل هو الله أحد', 'qul huwa allahu ahad', 'qul hu allahu ahad', 'qul huwa allah ahad'],
  ];
  let PX = null;
  // the Arabic phrase a typed one stands for (alhamdulillah, in sha allah), or ''
  function phrase(text) {
    if (!PX) { PX = new Map(); for (const [ar, ...en] of PHRASES) for (const e of en) PX.set(key(e), ar); }
    const k = key(text);
    return (k.length >= 6 && PX.get(k)) || '';
  }

  const api = { spell, spellings, key, dist, index, forms, match, phrase, chat, PHRASES };
  root.QI_ROMAN = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
