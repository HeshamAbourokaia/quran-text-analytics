// A verse as an image card, to share or keep: the Arabic, the English translation if wanted, where the verse is,
// and the site's name. Laid out and drawn here on a canvas the size of the image (1080 pixels wide), all in the
// browser: nothing is sent anywhere. Used by the share sheet of the verse study panel in app.html. Also loaded by
// the Node tests in data-build/tests, which check the layout with a stand-in for the canvas's text measuring.
//
// The card is square when the verse fits, and grows taller for a long verse rather than shrinking the text past
// what can be read on a phone. Lines are balanced: a verse that needs three lines gets three lines of about equal
// length, not two full lines and one word.
(function (root) {
  'use strict';

  const W = 1080, SIDE = 96, CW = W - 2 * SIDE;
  const AR_MAX = 84, AR_MIN = 38, AR_LH = 1.95;          // the Arabic: largest and smallest size, line height
  const EN_MAX = 36, EN_MIN = 25, EN_LH = 1.42;          // the English follows the Arabic's size, within these
  const TOP = 96, EYE = 36, RULE_GAP = 26, RULE = 10, AFTER_RULE = 50, AR_EN = 44, EN_CREDIT = 20, CREDIT = 26;
  const BEFORE_FOOT = 64, FOOT = 40, BOTTOM = 84;

  const enSize = ar => Math.max(EN_MIN, Math.min(EN_MAX, Math.round(ar * 0.46)));

  // the words of a text; a small sign standing alone (a pause mark) goes with the word before it, so no line starts with one
  function tokens(text) {
    const out = [];
    for (const t of String(text || '').split(/\s+/).filter(Boolean)) {
      if (out.length && !/\p{L}|\p{N}/u.test(t)) out[out.length - 1] += ' ' + t; else out.push(t);
    }
    return out;
  }

  // greedy lines no wider than width. w[i] = the width of word i, sp = the width of a space. A word wider than the
  // line on its own still gets a line of its own
  function greedy(w, sp, width) {
    const lines = []; let start = 0, cur = 0;
    for (let i = 0; i < w.length; i++) {
      const add = i === start ? w[i] : cur + sp + w[i];
      if (i > start && add > width) { lines.push([start, i]); start = i; cur = w[i]; } else cur = add;
    }
    if (w.length) lines.push([start, w.length]);
    return lines;
  }

  // the same number of lines as the greedy fill, but as even as they can be: the narrowest width that still needs
  // no more lines (found by halving), so the last line is not left with one word
  function balanced(words, measure, width) {
    if (!words.length) return [];
    const w = words.map(t => measure(t)), sp = measure(' ');
    const n = greedy(w, sp, width).length;
    let lo = Math.max(...w), hi = width;
    if (lo >= hi) return greedy(w, sp, width).map(([a, b]) => words.slice(a, b).join(' '));
    for (let k = 0; k < 24 && hi - lo > 0.5; k++) { const mid = (lo + hi) / 2; if (greedy(w, sp, mid).length <= n) hi = mid; else lo = mid; }
    return greedy(w, sp, hi).map(([a, b]) => words.slice(a, b).join(' '));
  }

  // where everything goes. measure(text, kind, size) gives a text's width in pixels, kind 'ar' for the verse and
  // 'en' for the translation. Returns the card's size, the sizes and lines of the two texts, and each block's top
  function layout(o) {
    const arWords = tokens(o.ar), enWords = o.en ? tokens(o.en) : [];
    const build = size => {
      const es = enSize(size);
      const ar = balanced(arWords, t => o.measure(t, 'ar', size), CW);
      const en = enWords.length ? balanced(enWords, t => o.measure(t, 'en', es), CW) : [];
      const arH = ar.length * size * AR_LH, enH = en.length ? AR_EN + en.length * es * EN_LH + EN_CREDIT + CREDIT : 0;
      const body = arH + enH, chrome = TOP + EYE + RULE_GAP + RULE + AFTER_RULE + BEFORE_FOOT + FOOT + BOTTOM;
      return { size, es, ar, en, arH, enH, body, need: chrome + body };
    };
    let pick = null;
    for (let s = AR_MAX; s >= AR_MIN; s -= 2) { const b = build(s); if (b.need <= W) { pick = b; break; } }
    if (!pick) pick = build(AR_MIN);
    const h = Math.max(W, Math.ceil(pick.need));
    // spare height (a short verse on a square card) goes above and below the texts, so they sit in the middle
    const spare = h - pick.need, top = TOP + EYE + RULE_GAP + RULE + AFTER_RULE + spare / 2;
    return {
      w: W, h, side: SIDE, width: CW,
      ar: { size: pick.size, lh: pick.size * AR_LH, lines: pick.ar, top },
      en: pick.en.length ? { size: pick.es, lh: pick.es * EN_LH, lines: pick.en, top: top + pick.arH + AR_EN, credit: top + pick.arH + AR_EN + pick.en.length * pick.es * EN_LH + EN_CREDIT } : null,
      eye: TOP, rule: TOP + EYE + RULE_GAP, foot: h - BOTTOM - FOOT,
    };
  }

  const THEMES = {
    night: { bg: '#040a07', glowA: 'rgba(15,181,109,.17)', glowB: 'rgba(233,185,95,.13)', dotA: '233,185,95', dotB: '52,211,153', dotAlpha: .5,
      ar: '#f5efe0', en: '#c3d3cb', gold: '#e9b95f', muted: '#7f978b', hair: 'rgba(255,255,255,.13)', brand: '#eef6f1' },
    paper: { bg: '#f6f0e1', glowA: 'rgba(15,140,90,.07)', glowB: 'rgba(185,138,36,.12)', dotA: '150,110,30', dotB: '20,120,80', dotAlpha: .32,
      ar: '#14211a', en: '#3f4f46', gold: '#8a6114', muted: '#6c7a72', hair: 'rgba(20,33,26,.16)', brand: '#14211a' },
  };

  // the same stars for the same verse every time: a small seeded random number generator (mulberry32)
  function rng(seed) {
    let a = 0; for (const ch of String(seed)) a = (Math.imul(a, 31) + ch.charCodeAt(0)) | 0;
    return () => { a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  // draw the card. L = layout(); t = the words to draw: {eye, ar, arDir, en, credit, brand, site, rtl, seed};
  // fonts = {ar(size), en(size), eye, credit, brand, site}: canvas font strings
  function draw(ctx, L, t, fonts, themeName) {
    const th = THEMES[themeName] || THEMES.night, W2 = L.w, H = L.h, cx = W2 / 2;
    ctx.save();
    ctx.fillStyle = th.bg; ctx.fillRect(0, 0, W2, H);
    const glow = (x, y, r, c) => { const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, c); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W2, H); };
    glow(W2 * 0.12, H * 0.06, W2 * 0.85, th.glowA); glow(W2 * 0.92, H * 0.96, W2 * 0.8, th.glowB);
    // a scatter of faint stars, thinner in the middle where the text sits
    const r = rng(t.seed || 'card');
    for (let i = 0; i < 170; i++) {
      const x = r() * W2, y = r() * H, dx = Math.abs(x - cx) / cx, mid = y > L.ar.top - 40 && y < (L.en ? L.en.credit : L.ar.top + L.ar.lines.length * L.ar.lh) + 20;
      if (mid && dx < 0.86 && r() < 0.85) continue;
      ctx.fillStyle = 'rgba(' + (r() < 0.6 ? th.dotA : th.dotB) + ',' + (th.dotAlpha * (0.25 + r() * 0.75)).toFixed(3) + ')';
      ctx.beginPath(); ctx.arc(x, y, 0.7 + r() * 1.5, 0, Math.PI * 2); ctx.fill();
    }
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const spaced = (px) => { if ('letterSpacing' in ctx) ctx.letterSpacing = px; };
    // where the verse is, and a gold rule
    ctx.fillStyle = th.gold; ctx.font = fonts.eye; ctx.direction = t.rtl ? 'rtl' : 'ltr'; spaced(t.rtl ? '0px' : '4px');
    ctx.fillText(t.eye, cx, L.eye + EYE / 2); spaced('0px');
    ctx.strokeStyle = th.gold; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(cx - 70, L.rule + RULE / 2); ctx.lineTo(cx - 12, L.rule + RULE / 2); ctx.moveTo(cx + 12, L.rule + RULE / 2); ctx.lineTo(cx + 70, L.rule + RULE / 2); ctx.stroke();
    ctx.save(); ctx.translate(cx, L.rule + RULE / 2); ctx.rotate(Math.PI / 4); ctx.fillRect(-4.5, -4.5, 9, 9); ctx.restore();
    // the verse
    ctx.fillStyle = th.ar; ctx.font = fonts.ar(L.ar.size); ctx.direction = 'rtl';
    L.ar.lines.forEach((line, i) => ctx.fillText(line, cx, L.ar.top + i * L.ar.lh + L.ar.lh / 2));
    // the translation, and whose it is
    if (L.en) {
      ctx.fillStyle = th.en; ctx.font = fonts.en(L.en.size); ctx.direction = 'ltr';
      L.en.lines.forEach((line, i) => ctx.fillText(line, cx, L.en.top + i * L.en.lh + L.en.lh / 2));
      ctx.fillStyle = th.muted; ctx.font = fonts.credit; ctx.direction = t.rtl ? 'rtl' : 'ltr';
      ctx.fillText(t.credit, cx, L.en.credit + CREDIT / 2);
    }
    // the site: a hairline, its name on the reading side and its address on the other
    const fy = L.foot + FOOT / 2;
    ctx.strokeStyle = th.hair; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(L.side, L.foot - 22); ctx.lineTo(W2 - L.side, L.foot - 22); ctx.stroke();
    const put = (text, font, color, x, align, dir) => { ctx.font = font; ctx.fillStyle = color; ctx.textAlign = align; ctx.direction = dir; ctx.fillText(text, x, fy); };
    put(t.brand, fonts.brand, th.brand, t.rtl ? W2 - L.side : L.side, t.rtl ? 'right' : 'left', t.rtl ? 'rtl' : 'ltr');
    put(t.site, fonts.site, th.muted, t.rtl ? L.side : W2 - L.side, t.rtl ? 'left' : 'right', 'ltr');
    ctx.restore();
  }

  const api = { W, SIDE, CW, AR_MAX, AR_MIN, EN_MIN, THEMES, tokens, greedy, balanced, layout, draw, enSize };
  root.QI_CARD = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
