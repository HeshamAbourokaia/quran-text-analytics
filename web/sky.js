// The verse sky behind the app: the landing page's field of 6,236 points, one per verse (gold for
// Meccan surahs, green for Medinan), re-arranged for each part of the app. Home shows the galaxy of
// surahs, the counting pages stand the surahs up as columns, the Mecca/Medina and lab pages sort the
// verses by length, the claim pages scatter them. The reader lights up the surah you are reading and
// the word search lights up every verse that matches.
//
// A page can also hold a stage: a transparent box in its flow (.stage) where the field draws that page's
// figure itself, as the landing's scenes do. See "stages" below.
//
// Loaded after data.js; three.js is imported on demand (the landing page's copy is usually cached).
// window.QTA_SKY is the app's handle. Calls made before the scene is ready are remembered and applied.
(function () {
  'use strict';
  const THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js';
  const want = { view: 'home', lang: 'en', keys: null, surah: 0, stage: null };
  let scene = null;
  const push = () => { if (scene) scene.apply(want); };
  window.QTA_SKY = {
    setView(view) { want.view = view; push(); },
    setLang(lang) { want.lang = lang; push(); },
    highlightKeys(keys) { want.keys = keys && keys.length ? keys : null; want.surah = 0; push(); },
    highlightSurah(n) { want.surah = n || 0; want.keys = null; push(); },
    clearHighlight() { want.keys = null; want.surah = 0; push(); },
    // el: the page's .stage box (or null); type: a scene below; data: what it draws
    setStage(el, type, data) { want.stage = el && type ? { el, type, data: data || {} } : null; push(); },
  };

  // Which arrangement each page uses. Pages with a stage keep the rest of the field as quiet dust.
  const FORM = {
    home: 'hero',
    overview: 'dust', word: 'dust', letters: 'dust', nlp: 'dust', advanced: 'dust', emotion: 'dust', pronouns: 'dust', dashboard: 'dust',
    mecca: 'dust', classifier: 'split', stats: 'dust', cluster: 'dust', hifz: 'split',
    auditor: 'dust', wordcount: 'dust', symmetry: 'dust', n19: 'dust', abjad: 'dust', structural: 'dust', coincidence: 'dust', science: 'dust',
    'd-endings': 'dust', 'd-rhyme': 'dust', 'd-themes': 'dust', 'd-repeats': 'dust', 'd-chrono': 'dust',
  };
  const formOf = v => FORM[v] || 'galaxy';

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);

  async function init() {
    const D = window.QURAN_DATA, VW = D && D.stats && D.stats.verseWords, META = D && D.datasets && D.datasets.surahMeta;
    const canvas = document.getElementById('gl');
    if (!VW || !META || !canvas) return null;
    let THREE, renderer;
    try { THREE = await import(THREE_URL); } catch (e) { return null; }
    try { renderer = new THREE.WebGLRenderer({ canvas, antialias: false, alpha: true, powerPreference: 'low-power' }); } catch (e) { return null; }

    const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
    const PR = Math.min(window.devicePixelRatio || 1, innerWidth < 760 ? 1.5 : 2);
    renderer.setPixelRatio(PR); renderer.setClearColor(0x000000, 0);
    const scene3 = new THREE.Scene();
    const cam = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, .1, 2000);
    const CAMZ = 60, HW = 2 * CAMZ * Math.tan(20 * Math.PI / 180);
    cam.position.z = reduced ? CAMZ : 118;

    // per-verse data, in mushaf order
    const N = VW.reduce((s, a) => s + a.length, 0);
    const sur = new Uint8Array(N), ver = new Uint16Array(N), wc = new Uint8Array(N), med = new Uint8Array(N), start = new Uint32Array(VW.length + 1);
    let maxV = 0, longW = 0, i = 0;
    VW.forEach((arr, k) => { start[k] = i; maxV = Math.max(maxV, arr.length);
      arr.forEach((w, j) => { sur[i] = k; ver[i] = j; wc[i] = w; med[i] = META[k].place === 'Medina' ? 1 : 0; if (w > longW) longW = w; i++; }); });
    start[VW.length] = N;
    const R = rng(20260925), jit = new Float32Array(N), jit2 = new Float32Array(N), jz = new Float32Array(N), arc = new Float32Array(N), dust = new Float32Array(N * 3);
    for (i = 0; i < N; i++) { jit[i] = R(); jit2[i] = R(); jz[i] = R(); arc[i] = R() * 2 - 1; dust[3 * i] = R() - .5; dust[3 * i + 1] = R() - .5; dust[3 * i + 2] = R(); }
    // a fixed shuffle of the points, for scenes whose points stand for something other than a verse
    const pool = new Uint16Array(N);
    for (i = 0; i < N; i++) pool[i] = i;
    for (i = N - 1; i > 0; i--) { const j = Math.floor(R() * (i + 1)), t = pool[i]; pool[i] = pool[j]; pool[j] = t; }

    // galaxy: the surahs on a golden-angle spiral in mushaf order, each surah a disc of its verses
    const gR = new Float32Array(N), gA = new Float32Array(N), gZ = new Float32Array(N), GA = Math.PI * (3 - Math.sqrt(5));
    i = 0;
    VW.forEach((arr, k) => {
      const n = arr.length, cr = .92 * Math.sqrt((k + .5) / VW.length), ca = k * GA, cl = .02 + .085 * Math.sqrt(n / maxV);
      for (let j = 0; j < n; j++, i++) {
        const rho = cl * Math.sqrt((j + .5) / n), ph = j * GA + k;
        const x = cr * Math.cos(ca) + rho * Math.cos(ph), y = cr * Math.sin(ca) + rho * Math.sin(ph);
        gR[i] = Math.hypot(x, y); gA[i] = Math.atan2(y, x); gZ[i] = (jz[i] - .5) * .07;
      }
    });
    const hist = [new Uint16Array(longW + 2), new Uint16Array(longW + 2)];
    for (i = 0; i < N; i++) hist[med[i]][wc[i]]++;
    const maxC = [Math.max(...hist[0]), Math.max(...hist[1])];

    const GOLD = [.914, .725, .373], GREEN = [.204, .827, .6];
    const pos = new Float32Array(N * 3), col = new Float32Array(N * 3), size = new Float32Array(N), surA = new Float32Array(N), phase = new Float32Array(N), hi = new Float32Array(N);
    for (i = 0; i < N; i++) {
      const c = med[i] ? GREEN : GOLD, b = .85 + jit2[i] * .3;
      col[3 * i] = c[0] * b; col[3 * i + 1] = c[1] * b; col[3 * i + 2] = c[2] * b;
      size[i] = .75 + jit[i] * .5 + Math.min(wc[i], 60) / 120; surA[i] = sur[i] + 1; phase[i] = jz[i];
    }
    // what the stage changes per point: colour, how much it belongs to the stage (front), glow, size
    const colBuf = col.slice(), frB = new Float32Array(N), emB = new Float32Array(N), bsB = new Float32Array(N).fill(1), idx = new Float32Array(N);
    for (i = 0; i < N; i++) idx[i] = i;
    const geo = new THREE.BufferGeometry();
    const dyn = a => { a.setUsage(THREE.DynamicDrawUsage); return a; };
    const posAttr = dyn(new THREE.BufferAttribute(pos, 3)), hiAttr = dyn(new THREE.BufferAttribute(hi, 1)), colAttr = dyn(new THREE.BufferAttribute(colBuf, 3)),
      frAttr = dyn(new THREE.BufferAttribute(frB, 1)), emAttr = dyn(new THREE.BufferAttribute(emB, 1)), bsAttr = dyn(new THREE.BufferAttribute(bsB, 1));
    geo.setAttribute('position', posAttr);
    geo.setAttribute('aColor', colAttr);
    geo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
    geo.setAttribute('aSurah', new THREE.BufferAttribute(surA, 1));
    geo.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
    geo.setAttribute('aHi', hiAttr);
    geo.setAttribute('aFront', frAttr); geo.setAttribute('aEm', emAttr); geo.setAttribute('aBoost', bsAttr);
    geo.setAttribute('aIdx', new THREE.BufferAttribute(idx, 1));
    const mat = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uSize: { value: 2.3 }, uPR: { value: PR }, uAlpha: { value: 0 }, uHover: { value: -1 }, uHp: { value: -1 }, uHiOn: { value: 0 },
        uBack: { value: 1 }, uStage: { value: 1 } },
      vertexShader: [
        'attribute vec3 aColor; attribute float aSize; attribute float aSurah; attribute float aPhase; attribute float aHi;',
        'attribute float aFront; attribute float aEm; attribute float aBoost; attribute float aIdx;',
        'uniform float uTime; uniform float uSize; uniform float uPR; uniform float uHover; uniform float uHp; uniform float uHiOn; uniform float uBack; uniform float uStage;',
        'varying vec3 vC; varying float vA; varying float vE;',
        'void main(){',
        '  vec4 mv = modelViewMatrix * vec4(position, 1.0);',
        '  float h = max(1.0 - step(0.5, abs(aSurah - uHover)), 1.0 - step(0.5, abs(aIdx - uHp)));',
        '  float k = max(h, aHi * uHiOn * (1.0 - aFront));',
        '  gl_PointSize = uSize * mix(aSize, 1.0, aFront) * aBoost * uPR * (1.0 + mix(1.3, 0.55, aFront) * k) * (60.0 / max(1.0, -mv.z));',
        '  gl_Position = projectionMatrix * mv;',
        '  vC = mix(aColor, vec3(1.0, 0.96, 0.84), mix(0.5, 0.35, aFront) * k);',
        '  float tw = 0.78 + 0.22 * sin(uTime * 1.3 + aPhase * 6.2831);',
        '  float back = tw * mix(mix(1.0, 0.26, uHiOn), 1.9, k) * uBack;',
        // a stage point keeps its full strength whatever the page does to the sky, and a glowing one burns a little brighter
        '  float front = (0.9 + 0.1 * tw) * uStage * (1.0 + 0.5 * aEm) * (1.0 + 0.7 * h);',
        '  vA = mix(back, front, aFront);',
        '  vE = aEm * aFront;',
        '}'].join('\n'),
      fragmentShader: [
        'uniform float uAlpha; varying vec3 vC; varying float vA; varying float vE;',
        'void main(){',
        '  float d = length(gl_PointCoord - 0.5);',
        '  if (d > 0.5) discard;',
        '  float soft = pow(1.0 - d * 2.0, 1.5);',
        '  float glow = (1.0 - smoothstep(0.14, 0.26, d)) * 0.95 + pow(1.0 - d * 2.0, 2.0) * 0.55;',   // a bright core in a soft halo
        '  gl_FragColor = vec4(vC, mix(soft, glow, vE) * uAlpha * vA);',
        '}'].join('\n'),
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    });
    const pts = new THREE.Points(geo, mat); pts.frustumCulled = false;
    const SN = 1400, sp = new Float32Array(SN * 3);
    for (i = 0; i < SN; i++) { const u = R() * 2 - 1, th = R() * Math.PI * 2, r = 150 + R() * 300, q = Math.sqrt(1 - u * u);
      sp[3 * i] = r * q * Math.cos(th); sp[3 * i + 1] = r * q * Math.sin(th); sp[3 * i + 2] = -Math.abs(r * u) - 40; }
    const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(sp, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xcfe7dc, size: 1.2, sizeAttenuation: false, transparent: true, opacity: 0, depthWrite: false });
    const stars = new THREE.Points(sg, starMat);
    const group = new THREE.Group(); group.add(pts);
    scene3.add(stars, group);

    // ---- arrangements, in fractions of the viewport (x from the reading-start side, y from the top) ----
    let W = HW, H = HW, mob = false, mirror = false, left = 0, lastW = 0, lastH = 0;
    const mx = fx => (mirror ? 1 - fx : fx), wx = fx => (fx - .5) * W, wy = fy => (.5 - fy) * H;
    const main = f => left + (1 - left) * f;            // a fraction of the content area beside the sidebar
    const G = {
      // r is a fraction of the viewport's height on desktop and of its width on phones
      hero: () => (mob ? { fx: .5, fy: .25, r: .52, tilt: 1.0, roll: -.3 } : { fx: main(.74), fy: .47, r: .56, tilt: 1.05, roll: -.36 }),
      galaxy: () => (mob ? { fx: .5, fy: .56, r: .95, tilt: 1.12, roll: -.42 } : { fx: main(.62), fy: .56, r: .78, tilt: 1.14, roll: -.44 }),
    };
    const BOX = () => (mob ? { x0: .05, x1: .95, y0: .22, y1: .9 } : { x0: main(.05), x1: main(.97), y0: .16, y1: .9 });
    const T = { bars: new Float32Array(N * 3), split: new Float32Array(N * 3), dust: new Float32Array(N * 3) };
    function layoutBars() {
      const f = BOX(), cw = (f.x1 - f.x0) / VW.length, a = T.bars;
      for (let n = 0; n < N; n++) {
        const fx = mx(f.x0 + cw * (sur[n] + .5) + (jit[n] - .5) * cw * .5), fy = f.y1 - (f.y1 - f.y0) * (ver[n] + .5) / maxV;
        a[3 * n] = wx(fx); a[3 * n + 1] = wy(fy); a[3 * n + 2] = (jz[n] - .5) * .4;
      }
    }
    const lnMax = Math.log(longW + 1);
    const xOfW = (f, w) => f.x0 + (f.x1 - f.x0) * ((Math.log(w) + Math.log(w + 1)) / 2) / lnMax;
    function layoutSplit() {
      const f = BOX(), h = f.y1 - f.y0, cen = [f.y0 + .27 * h, f.y0 + .73 * h], half = .2 * h, a = T.split;
      const run = [new Uint16Array(longW + 2), new Uint16Array(longW + 2)];
      for (let n = 0; n < N; n++) {
        const b = med[n], w = wc[n], c = run[b][w]++, dy = half / Math.max(1, maxC[b] / 2);
        const off = (c === 0 ? 0 : (c % 2 ? 1 : -1) * Math.ceil(c / 2)) * dy;
        const gap = (Math.log(w + 1) - Math.log(w)) / lnMax * (f.x1 - f.x0);
        a[3 * n] = wx(mx(xOfW(f, w) + (jit[n] - .5) * gap * .7)); a[3 * n + 1] = wy(cen[b] + off); a[3 * n + 2] = (jz[n] - .5) * .4;
      }
    }
    function layoutDust() {
      const a = T.dust;
      for (let n = 0; n < N; n++) { a[3 * n] = dust[3 * n] * W * 1.6; a[3 * n + 1] = dust[3 * n + 1] * H * 1.5; a[3 * n + 2] = 6 - dust[3 * n + 2] * 42; }
    }
    function measure() {
      const side = document.querySelector('.side');
      left = !side || innerWidth <= 920 ? 0 : clamp(side.getBoundingClientRect().width / innerWidth, 0, .4);
    }
    function relayout() { measure(); layoutBars(); layoutSplit(); layoutDust(); }

    // galaxy positions for a set of parameters (spin is shared, so the galaxy keeps turning)
    let spin = 0;
    const gp = { cx: 0, cy: 0, R: 1, ct: 1, st: 0, cr: 1, sr: 0 };
    function setGalaxy(p) {
      const roll = p.roll * (mirror ? -1 : 1);
      gp.cx = wx(mx(p.fx)); gp.cy = wy(p.fy); gp.R = p.r * (mob ? W : H);
      gp.ct = Math.cos(p.tilt); gp.st = Math.sin(p.tilt); gp.cr = Math.cos(roll); gp.sr = Math.sin(roll);
    }
    function galaxyInto(out, n) {
      const a = gA[n] + spin, r = gR[n] * gp.R, x = r * Math.cos(a), yd = r * Math.sin(a), zd = gZ[n] * gp.R;
      const y = yd * gp.ct - zd * gp.st, z = yd * gp.st + zd * gp.ct;
      out[0] = gp.cx + x * gp.cr - y * gp.sr; out[1] = gp.cy + x * gp.sr + y * gp.cr; out[2] = z;
    }

    // ---- state: the current arrangement, and a morph from a snapshot to it ----
    const SIZE = { hero: 2.5, galaxy: 2.15, bars: 1.9, split: 1.75, dust: 1.6 };
    const ALPHA = { hero: 1, galaxy: .62, bars: .5, split: .5, dust: .42 };
    let form = null, morph = 1, morphDur = 1.7, snap = new Float32Array(N * 3), fadeIn = reduced ? 1 : 0;
    const DL = new Float32Array(N);
    let uSize = 2.3, uAlpha = 0, hiOn = 0, hiTarget = 0;
    const out = [0, 0, 0], base = new Float32Array(N * 3);
    function targetInto(n, o) {
      if (form === 'hero' || form === 'galaxy') { galaxyInto(o, n); return; }
      const a = T[form]; o[0] = a[3 * n]; o[1] = a[3 * n + 1]; o[2] = a[3 * n + 2];
    }
    function goTo(f, instant, force) {
      if (f === form && !instant && !force) return;
      snap.set(base);
      const prev = form;
      form = f;
      if (form === 'hero' || form === 'galaxy') setGalaxy(G[form]());
      // stagger: columns sweep in surah order, other arrangements settle in a random order
      for (let n = 0; n < N; n++) DL[n] = form === 'bars' ? sur[n] / 113 * .85 + jit[n] * .15 : form === 'split' ? jit2[n] : jit[n];
      morph = instant || reduced || prev === null ? 1 : 0;
      morphDur = prev === 'hero' && form === 'galaxy' || prev === 'galaxy' && form === 'hero' ? 1.5 : 1.8;
      if (morph === 1) for (let n = 0; n < N; n++) { targetInto(n, out); base[3 * n] = out[0]; base[3 * n + 1] = out[1]; base[3 * n + 2] = out[2]; }
      kick();
    }

    // ---- highlights: the reader's surah, the search's verses ----
    let hiKeys = null, hiSurah = 0;
    function setHighlight(keys, surah) {
      if (keys === hiKeys && surah === hiSurah) return;
      hiKeys = keys; hiSurah = surah;
      hi.fill(0);
      if (surah >= 1 && surah <= VW.length) for (let n = start[surah - 1]; n < start[surah]; n++) hi[n] = 1;
      else if (keys) for (const k of keys) { const n = keyIdx(k); if (n >= 0) hi[n] = 1; }
      hiAttr.needsUpdate = true;
      hiTarget = surah || keys ? 1 : 0;
      kick();
    }
    function keyIdx(k) {   // "s:v" -> the verse's point, or -1
      const c = String(k).indexOf(':'), s = +String(k).slice(0, c), v = +String(k).slice(c + 1);
      return s >= 1 && s <= VW.length && v >= 1 && v <= VW[s - 1].length ? start[s - 1] + v - 1 : -1;
    }

    // ================================ stages ================================
    // A stage is a view's figure drawn by the field. The page holds a transparent box (.stage) in its
    // flow; a scene says where each point goes inside it, in fractions of the box (x from the reading-start
    // side, so Arabic mirrors), with its colour, glow and size in CSS pixels. The points gather while the
    // box rises into view and follow it as the page scrolls; points the scene doesn't use stay in the sky,
    // stepped back. Labels are HTML inside the box, so they scroll with it by themselves.
    //
    // Most scenes use one point per verse, or one per mention/occurrence of a word, so hovering a point can
    // name it. Scenes of counts too large for that (letters, lemmas) share the points out by count, and say so.
    const digits = s => (want.lang === 'ar' ? String(s).replace(/\d/g, c => '٠١٢٣٤٥٦٧٨٩'[c]) : String(s));
    const nf = v => digits(Math.round(v).toLocaleString('en-US')).replace(/,/g, want.lang === 'ar' ? '٬' : ',');
    const AR = () => want.lang === 'ar';
    const sname = s => (AR() ? META[s].ar : META[s].en);
    const PAL = { gold: GOLD, green: GREEN, teal: [.22, .78, .86], rose: [.96, .55, .55], violet: [.66, .56, .98], amber: [1, .78, .4],
      emerald: [.3, .86, .62], pale: [.78, .86, .82], white: [.95, .93, .86] };
    const mixc = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
    const colorOf = c => (Array.isArray(c) ? c : PAL[c] || PAL.pale);
    // share P points out over counts, largest remainders first
    function share(counts, P) {
      const tot = counts.reduce((a, b) => a + b, 0) || 1, raw = counts.map(c => c / tot * P), k = raw.map(Math.floor);
      let left = P - k.reduce((a, b) => a + b, 0);
      raw.map((r, i) => [r - k[i], i]).sort((a, b) => b[0] - a[0]).forEach(([, i]) => { if (left > 0) { k[i]++; left--; } });
      return k;
    }
    function blank() {
      return { on: new Uint8Array(N), fx: new Float32Array(N), fy: new Float32Array(N), col: new Float32Array(N * 3), em: new Float32Array(N),
        px: new Float32Array(N).fill(2.4), dl: new Float32Array(N), grp: new Int32Array(N).fill(-1), labels: [], shapes: [], kind: 'verse', hover: null, link: null };
    }
    function put(S, n, fx, fy, c, em, px, dl, g) {
      S.on[n] = 1; S.fx[n] = fx; S.fy[n] = fy; S.col[3 * n] = c[0]; S.col[3 * n + 1] = c[1]; S.col[3 * n + 2] = c[2];
      S.em[n] = em; S.px[n] = px; S.dl[n] = clamp(dl, 0, 1); if (g != null) S.grp[n] = g;
    }
    const placeCol = n => { const c = med[n] ? GREEN : GOLD, b = .88 + jit2[n] * .28; return [c[0] * b, c[1] * b, c[2] * b]; };
    function verseTip(n, extra) {
      const m = META[sur[n]], ar = AR(), w = wc[n];
      const words = ar ? (w === 1 ? 'كلمة واحدة' : w === 2 ? 'كلمتان' : digits(w) + (w % 100 >= 3 && w % 100 <= 10 ? ' كلمات' : ' كلمة')) : w + (w === 1 ? ' word' : ' words');
      return (extra ? extra + '<br>' : '') + '<b>' + esc(ar ? m.ar : m.en) + '</b> <span class="k">' + digits((sur[n] + 1) + ':' + (ver[n] + 1)) + '</span><br>' +
        (m.place === 'Medina' ? (ar ? 'مدنية' : 'Medinan') : (ar ? 'مكية' : 'Meccan')) + ' · ' + words;
    }
    const L = (x, y, html, cls, a) => ({ x, y, html, cls: cls || '', a: a || 'c' });

    const SCENES = {
      // every verse, standing in its surah's column (mushaf order, or the order the page gives)
      columns(d, bx) {
        const S = blank(), order = d.order || META.map((m, k) => k + 1), K = order.length, kOf = new Int16Array(VW.length + 1).fill(-1);
        order.forEach((s, k) => { kOf[s] = k; });
        let mv = 1; order.forEach(s => { mv = Math.max(mv, VW[s - 1].length); });
        const top = .1, bot = .9, cw = 1 / K, px = clamp(bx.w / K * 1.05, 2, 5.5);
        for (let n = 0; n < N; n++) {
          const k = kOf[sur[n] + 1]; if (k < 0) continue;
          put(S, n, (k + .5) * cw + (jit[n] - .5) * cw * .45, bot - (bot - top) * (ver[n] + .5) / mv, placeCol(n), .25, px, k / K * .8 + jit[n] * .2, sur[n]);
        }
        const yOf = v => bot - (bot - top) * v / mv;
        for (const v of [50, 100, 150, 200, 250]) if (v < mv * .96) S.labels.push(L(0, yOf(v), digits(v), 'hl', 's'));
        if (!d.order) for (const s of [1, 20, 40, 60, 80, 100, 114]) S.labels.push(L((kOf[s] + .5) * cw, .965, digits(s), 'tk'));
        order.slice().sort((a, b) => VW[b - 1].length - VW[a - 1].length).slice(0, d.peaks == null ? 3 : d.peaks).forEach(s => {
          S.labels.push(L((kOf[s] + .5) * cw, yOf(VW[s - 1].length) - .035, esc(sname(s - 1)) + ' <span class="k">' + digits(VW[s - 1].length) + '</span>', 'pk'));
        });
        S.hover = n => verseTip(n); S.link = n => sur[n] + 1;
        return S;
      },

      // every verse by its length in words (a log scale), Meccan above and Medinan below
      lengths(d, bx) {
        const S = blank(), f = { x0: .03, x1: .97 }, cen = [.31, .72], half = .15, run = [new Uint16Array(longW + 2), new Uint16Array(longW + 2)];
        const px = clamp(bx.w / 330, 1.8, 3.2);
        for (let n = 0; n < N; n++) {
          const b = med[n], w = wc[n], c = run[b][w]++, dy = half / Math.max(1, maxC[b] / 2);
          const off = (c === 0 ? 0 : (c % 2 ? 1 : -1) * Math.ceil(c / 2)) * dy, gap = (Math.log(w + 1) - Math.log(w)) / lnMax * (f.x1 - f.x0);
          put(S, n, xOfW(f, w) + (jit[n] - .5) * gap * .7, cen[b] + off, placeCol(n), .25, px, jit2[n], null);
        }
        const xOfMean = m => f.x0 + (f.x1 - f.x0) * Math.log(m + .5) / lnMax, ar = AR(), cnt = [0, 0];
        for (let n = 0; n < N; n++) cnt[med[n]]++;
        const means = d.means || {};
        [[0, ar ? 'مكية' : 'Meccan', means.mecca], [1, ar ? 'مدنية' : 'Medinan', means.medina]].forEach(([b, name, m]) => {
          S.labels.push(L(f.x0, cen[b] - half - .045, '<b>' + name + '</b> · ' + nf(cnt[b]) + (ar ? ' آية' : ' verses'), 'ttl', 's'));
          if (m) S.labels.push(L(xOfMean(m), cen[b], '<i></i><span>' + (ar ? 'المتوسط ' : 'mean ') + digits(m) + '</span>', 'mean' + (d.showMeans ? ' strong' : '')));
        });
        for (const w of [1, 2, 5, 10, 20, 50, 100]) if (w <= longW) S.labels.push(L(xOfW(f, w), .915, digits(w), 'tk'));
        S.labels.push(L(f.x1, .975, ar ? 'كلمة في الآية ›' : 'words per verse ›', 'tk axis', 'e'));
        S.hover = n => verseTip(n); S.link = n => sur[n] + 1;
        return S;
      },

      // ranked counts as bars of light (h) or columns (v); the points are shared out by count
      bars(d, bx) {
        const S = blank(), it = d.items || [], I = it.length; if (!I) return S;
        const k = share(it.map(x => x.c), N), k0 = Math.max(...k), ar = AR(), tot = it.reduce((a, x) => a + x.c, 0);
        const warm = colorOf(d.from || 'amber'), cool = colorOf(d.to || 'emerald');
        let p = 0;
        if (d.orient === 'v') {
          const mb = 38, mt = 24, colW = bx.w / I, barW = colW * .66, Hm = bx.h - mb - mt;
          const t = Math.max(1, Math.round(Math.sqrt(k0 * barW / Hm))), cx = barW / t, cy = Hm / Math.ceil(k0 / t), px = Math.max(cx, cy) * 1.2;
          it.forEach((x, i) => {
            const c = mixc(warm, cool, I > 1 ? i / (I - 1) : 0), x0 = i * colW + (colW - barW) / 2;
            for (let j = 0; j < k[i]; j++, p++) {
              const r = Math.floor(j / t), q = j % t;
              put(S, pool[p], (x0 + (q + .5) * cx) / bx.w, (bx.h - mb - (r + .5) * cy) / bx.h, c, .4, px, i / I * .6 + j / k[i] * .3 + jit[pool[p]] * .1, i);
            }
            const topY = (bx.h - mb - Math.ceil(k[i] / t) * cy) / bx.h;
            S.labels.push(L((i + .5) * colW / bx.w, 1 - mb / 2 / bx.h, '<b lang="ar">' + esc(x.label) + '</b>', 'vlab'));
            // on a narrow screen the columns are too close for every figure: every other one of the tallest
            if (x.short !== '' && (colW >= 22 || (i < 8 && i % 2 === 0))) S.labels.push(L((i + .5) * colW / bx.w, topY - 11 / bx.h, x.short != null ? esc(x.short) : nf(x.c), 'vnum'));
          });
        } else {
          const ls = bx.w * (d.labelW || .2), le = bx.w * .1, Lm = bx.w - ls - le, rh = bx.h / I, bh = rh * .56;
          const t = Math.max(2, Math.round(Math.sqrt(k0 * bh / Lm))), cx = Lm / Math.ceil(k0 / t), cy = bh / t, px = Math.max(cx, cy) * 1.25;
          it.forEach((x, i) => {
            const c = mixc(warm, cool, I > 1 ? i / (I - 1) : 0), y0 = i * rh + (rh - bh) / 2;
            for (let j = 0; j < k[i]; j++, p++) {
              const q = Math.floor(j / t), r = j % t;
              put(S, pool[p], (ls + (q + .5) * cx) / bx.w, (y0 + (r + .5) * cy) / bx.h, c, .4, px, i / I * .55 + j / k[i] * .35 + jit[pool[p]] * .1, i);
            }
            const yc = (i + .5) * rh / bx.h, len = Math.ceil(k[i] / t) * cx;
            S.labels.push(L((ls - 12) / bx.w, yc, '<b lang="ar">' + esc(x.label) + '</b>' + (x.sub && !ar ? '<i>' + esc(x.sub) + '</i>' : ''), 'hlab', 'e'));
            S.labels.push(L((ls + len + 10) / bx.w, yc, nf(x.c), 'hnum', 's'));
          });
        }
        S.kind = 'group';
        S.hover = n => { const i = S.grp[n]; if (i < 0) return null; const x = it[i];
          return '<b lang="ar">' + esc(x.label) + '</b>' + (x.sub && !ar ? ' <span class="k">' + esc(x.sub) + '</span>' : '') + '<br>' +
            nf(x.c) + (d.unit ? ' ' + (typeof d.unit === 'function' ? d.unit(x.c) : d.unit) : '') + ' · ' + (ar ? 'المرتبة ' + digits(i + 1) : '#' + (i + 1)) +
            (d.showShare ? ' · ' + digits((x.c / tot * 100).toFixed(1)) + '%' : ''); };
        if (d.search) S.link = n => ({ search: it[S.grp[n]].q || it[S.grp[n]].label, mode: d.search });
        return S;
      },

      // one point per occurrence, piled in a heap per group (a group's per-surah counts, when known, fill it in mushaf order)
      heaps(d, bx) {
        const S = blank(), gs = d.groups || [], G2 = gs.length; if (!G2) return S;
        const tot = gs.reduce((a, g) => a + g.c, 0), k = tot <= N ? gs.map(g => g.c) : share(gs.map(g => g.c), N);
        const b = k.map(v => Math.max(3, Math.sqrt(v / .43))), R2 = b.map(v => Math.max(2, Math.ceil(v * .55)));
        const caps = (bw, rows) => { let s = 0; for (let r = 0; r < rows; r++) s += Math.max(1, Math.floor(bw * Math.sqrt(1 - Math.pow((r + .5) / rows, 2)))); return s; };
        b.forEach((bw, i) => { while (caps(bw, R2[i]) < k[i]) R2[i]++; });
        const lab = 70, gapC = 6, totC = b.reduce((a, v) => a + v, 0) + gapC * (G2 + 1);
        const c = Math.min(bx.w * .94 / totC, (bx.h - lab - 14) / Math.max(...R2)), ar = AR();
        const x0 = (bx.w - (totC - gapC * 2) * c) / 2, base = bx.h - lab;
        let p = 0, cx = x0;
        gs.forEach((g, i) => {
          const center = cx + b[i] * c / 2, color = colorOf(g.color), src = [];
          if (g.per) g.per.forEach(e => { for (let q = 0; q < e.c; q++) src.push(e.s); });
          let j = 0;
          for (let r = 0; r < R2[i] && j < k[i]; r++) {
            const cap = Math.max(1, Math.floor(b[i] * Math.sqrt(1 - Math.pow((r + .5) / R2[i], 2)))), n0 = Math.min(cap, k[i] - j);
            for (let q = 0; q < n0; q++, j++, p++) {
              const n = pool[p], bright = .82 + jit2[n] * .36;
              put(S, n, (center + (q - (n0 - 1) / 2) * c + (jit[n] - .5) * c * .3) / bx.w, (base - (r + .5) * c) / bx.h,
                [color[0] * bright, color[1] * bright, color[2] * bright], .45, c * 1.2, i / G2 * .5 + r / R2[i] * .4 + jit[n] * .1, i * 1000 + (src.length ? src[j] : 0));
            }
          }
          S.labels.push(L(center / bx.w, (base + 10) / bx.h, (g.ar ? '<b lang="ar">' + esc(g.ar) + '</b>' : '') + (g.label && !ar ? '<span>' + esc(g.label) + '</span>' : '') +
            '<span class="k">' + nf(g.c) + '</span>', 'heaplab', 'ct'));
          cx += (b[i] + gapC) * c;
        });
        S.kind = 'group'; S.grpOf = n => Math.floor(S.grp[n] / 1000);
        S.hover = n => { const v = S.grp[n]; if (v < 0) return null; const g = gs[Math.floor(v / 1000)], s = v % 1000;
          let h = (g.ar ? '<b lang="ar">' + esc(g.ar) + '</b> ' : '') + (g.label && !ar ? '<b>' + esc(g.label) + '</b> ' : '') + '<span class="k">' + nf(g.c) + '</span>';
          if (s) { const e = g.per.find(x => x.s === s); h += '<br>' + (ar ? 'في سورة ' : 'in ') + esc(sname(s - 1)) + ': ' + nf(e ? e.c : 0); }
          if (g.note) h += '<br>' + esc(g.note);
          return h; };
        S.link = n => { const v = S.grp[n]; return v > 0 && v % 1000 ? v % 1000 : 0; };
        return S;
      },

      // the whole Quran as a carpet of its verses in reading order; the page's verses light up
      carpet(d, bx) {
        const S = blank(), C = Math.max(20, Math.round(Math.sqrt(N * bx.w / bx.h))), Rw = Math.ceil(N / C), c = Math.min(bx.w / C, bx.h / Rw);
        const ox = (bx.w - C * c) / 2, oy = (bx.h - Rw * c) / 2, lit = new Map();
        (d.lit || []).forEach(e => { const n = keyIdx(e.k); if (n >= 0) lit.set(n, e); });
        for (let n = 0; n < N; n++) {
          const r = Math.floor(n / C), q = n % C, e = lit.get(n), fx = (ox + (q + .5) * c) / bx.w, fy = (oy + (r + .5) * c) / bx.h;
          if (e) { put(S, n, fx, fy, colorOf(e.color || 'amber'), 1, c * 2.1, jit[n] * .4, null); (S.prefer || (S.prefer = new Uint8Array(N)))[n] = 1; }
          else { const pc = placeCol(n), dim = sur[n] % 2 ? .55 : .8; put(S, n, fx, fy, [pc[0] * dim, pc[1] * dim, pc[2] * dim], 0, c * .7, .3 + jit[n] * .7, null); }
        }
        S.hover = n => { const e = lit.get(n); return verseTip(n, e && e.label ? '<b>' + esc(e.label) + '</b>' : ''); };
        S.link = n => ({ verse: [sur[n] + 1, ver[n] + 1] });   // the verse itself, not the top of its surah
        return S;
      },

      // the whole Quran as a carpet in reading order, each verse coloured by its class (a rhyme, a theme, ...);
      // with focus set, that class glows and the rest dims
      mosaic(d, bx) {
        const S = blank(), cls = d.cls || [], names = d.names || [], cols = (d.colors || []).map(colorOf), f = d.focus == null ? -1 : d.focus;
        const C = Math.max(20, Math.round(Math.sqrt(N * bx.w / bx.h))), Rw = Math.ceil(N / C), c = Math.min(bx.w / C, bx.h / Rw);
        const ox = (bx.w - C * c) / 2, oy = (bx.h - Rw * c) / 2;
        for (let n = 0; n < N; n++) {
          const r = Math.floor(n / C), q = n % C, k = cls[n] == null ? -1 : cls[n], fx = (ox + (q + .5) * c) / bx.w, fy = (oy + (r + .5) * c) / bx.h;
          const on = k >= 0 && (f < 0 || f === k), b = .82 + jit2[n] * .3, cc = k >= 0 && cols[k] ? cols[k] : [.42, .48, .45];
          const dim = on ? (f >= 0 ? 1 : .82) : k >= 0 && f >= 0 ? .3 : .45;
          put(S, n, fx, fy, [cc[0] * b * dim, cc[1] * b * dim, cc[2] * b * dim], on ? (f >= 0 ? .9 : .32) : 0, c * (on ? (f >= 0 ? 1.7 : 1.15) : .75), (r / Rw) * .7 + jit[n] * .3, k);
        }
        S.hover = n => { const k = cls[n] == null ? -1 : cls[n]; return verseTip(n, k >= 0 && names[k] ? '<b>' + esc(names[k]) + '</b>' : ''); };
        S.link = n => ({ verse: [sur[n] + 1, ver[n] + 1] });
        return S;
      },

      // each surah a disc of its verses, placed by two numbers about it
      scatter(d, bx) {
        const S = blank(), P2 = d.pts || [], ml = .085, mr = .03, mt = .05, mbt = .13;
        const Tx = d.logx ? Math.log10 : v => v, Ty = d.logy ? Math.log10 : v => v;
        let [x0, x1] = d.xr, [y0, y1] = d.yr;
        // equal: a unit is as long across as up, so a direction drawn on it keeps its true angle (the axis with room to spare runs further)
        if (d.equal) { const pw = (1 - ml - mr) * bx.w, ph = (1 - mt - mbt) * bx.h, ux = (x1 - x0) / pw, uy = (y1 - y0) / ph; if (ux < uy) x1 = x0 + uy * pw; else y1 = y0 + ux * ph; }
        const fxOf = v => ml + (1 - ml - mr) * (Tx(v) - Tx(x0)) / (Tx(x1) - Tx(x0)), fyOf = v => 1 - mbt - (1 - mbt - mt) * (Ty(v) - Ty(y0)) / (Ty(y1) - Ty(y0));
        const every = (a, b, s) => { const o = []; for (let v = Math.ceil(a / s) * s; v <= b + 1e-9; v += s) o.push(Math.round(v * 1e6) / 1e6); return o; };
        const tkl = v => digits(v < 0 ? '−' + Math.abs(v) : v), px = (x, y) => [fxOf(x) * bx.w, fyOf(y) * bx.h];
        const info = {};
        P2.forEach(pt => {
          const k = pt.n - 1, nv = VW[k].length, cx = fxOf(pt.x) * bx.w, cy = fyOf(pt.y) * bx.h, rad = (d.r0 || 2) + (d.r1 || 10) * Math.sqrt(nv / maxV);
          const color = pt.color ? colorOf(pt.color) : null;
          info[pt.n] = pt.info;
          for (let j = 0; j < nv; j++) {
            const n = start[k] + j, rho = rad * Math.sqrt((j + .5) / nv), ph = j * GA + k, c = color ? mixc(color, [1, 1, 1], jit2[n] * .15) : placeCol(n);
            put(S, n, (cx + rho * Math.cos(ph)) / bx.w, (cy + rho * Math.sin(ph)) / bx.h, c, .35, 2.2, (fxOf(pt.x) * .6 + jit[n] * .4), null);
          }
        });
        // tick: a tick every so many units, over the range asked for (not over the room added to keep the units equal)
        (d.tick ? every(x0, Math.min(x1, d.xr[1]), d.tick) : d.xTicks || []).forEach(v => S.labels.push(L(fxOf(v), 1 - mbt + .045, tkl(v), 'tk')));
        (d.tick ? every(y0, Math.min(y1, d.yr[1]), d.tick) : d.yTicks || []).forEach(v => S.labels.push(L(ml - .012, fyOf(v), tkl(v), 'tk', 'e')));
        // zero: faint lines through the average (0 on a standardized axis)
        if (d.zero) {
          if (x0 < 0 && x1 > 0) S.shapes.push({ cls: 'pzero', pts: [px(0, y0), px(0, y1)] });
          if (y0 < 0 && y1 > 0) S.shapes.push({ cls: 'pzero', pts: [px(x0, 0), px(x1, 0)] });
        }
        // line: a direction through the origin, at an angle in the data's units, with an arrowhead; with shadows,
        // each point's projection on it is ticked and joined to the point by a faint drop. Its label shows while the
        // tip points right, away from the crowd of short surahs by the origin.
        if (d.line) {
          const c = Math.cos(d.line.angle), s = Math.sin(d.line.angle);
          let t0 = -Infinity, t1 = Infinity;
          if (Math.abs(c) > 1e-9) { const a = x0 / c, b = x1 / c; t0 = Math.max(t0, Math.min(a, b)); t1 = Math.min(t1, Math.max(a, b)); }
          if (Math.abs(s) > 1e-9) { const a = y0 / s, b = y1 / s; t0 = Math.max(t0, Math.min(a, b)); t1 = Math.min(t1, Math.max(a, b)); }
          if (t1 > t0) {
            const A = px(t0 * c, t0 * s), B = px(t1 * c, t1 * s), len = Math.hypot(B[0] - A[0], B[1] - A[1]) || 1, ux = (B[0] - A[0]) / len, uy = (B[1] - A[1]) / len;
            if (d.line.shadows) P2.forEach(pt => {
              const t = pt.x * c + pt.y * s, P = px(pt.x, pt.y), Q = px(t * c, t * s);
              S.shapes.push({ cls: 'pdrop', pts: [P, Q] });
              S.shapes.push({ cls: 'ptick', pts: [[Q[0] - uy * 5, Q[1] + ux * 5], [Q[0] + uy * 5, Q[1] - ux * 5]] });
            });
            S.shapes.push({ cls: 'pline', pts: [A, B] });
            S.shapes.push({ cls: 'phead', pts: [B, [B[0] - ux * 11 - uy * 5, B[1] - uy * 11 + ux * 5], [B[0] - ux * 11 + uy * 5, B[1] - uy * 11 - ux * 5]] });
            if (d.line.label && c > .2) S.labels.push(L(clamp(B[0] / bx.w, .14, .9), clamp(B[1] / bx.h + .075, .1, .84), esc(d.line.label), 'plbl'));
          }
        }
        // gauge: one big number where the plot has room (beside it in a wide box, in its top corner in a narrow one)
        if (d.gauge) { const wide = bx.w / bx.h > 1.35; S.labels.push(L(wide ? .8 : .3, wide ? .42 : .17, '<b>' + esc(d.gauge.value) + '</b><span>' + esc(d.gauge.label) + '</span>', 'gauge')); }
        if (d.xTitle) S.labels.push(L(1 - mr, 1 - .02, esc(d.xTitle), 'tk axis', 'e'));
        // in a narrow box the y title stands along the axis, where it has room; the legend keeps at least 78px an item
        if (d.yTitle) S.labels.push(bx.w < 560 ? L(.024, (mt + 1 - mbt) / 2, esc(d.yTitle), 'tk axis yv') : L(ml - .012, mt - .01, esc(d.yTitle), 'tk axis', 'e'));
        const lstep = Math.max(d.legendStep || .14, 78 / bx.w);
        (d.legend || []).forEach((g, q) => S.labels.push(L(ml + .01 + q * lstep, mt, '<i style="background:rgb(' + colorOf(g.color).map(v => Math.round(v * 255)).join(',') + ')"></i>' + esc(g.label), 'lg', 's')));
        S.hover = n => '<b>' + esc(sname(sur[n])) + '</b> <span class="k">' + digits(sur[n] + 1) + '</span>' + (info[sur[n] + 1] ? '<br>' + info[sur[n] + 1] : '');
        S.link = n => sur[n] + 1;
        return S;
      },

      // claims (or words) as blocks: a dashed outline holds the claimed number of cells; one point per counted mention
      // fills it in mushaf order, and any extra spills past it in gold
      blocks(d, bx) {
        const S = blank(), it = d.items || [], ar = AR(), labH = 46, gap = 22;
        const dims = it.map(x => { const m = Math.max(x.claimed || 0, x.counted, 1), cols = Math.max(4, Math.ceil(Math.sqrt(m * (d.wide || 1.4)))); return { cols, rows: Math.ceil(m / cols) }; });
        // perRow keeps pairs side by side: that many blocks to a row (two on a phone, so a pair shares a row)
        const per = d.perRow ? (bx.w < 560 ? 2 : d.perRow) : 0, minW = per ? (bx.w - (per - 1) * gap) / per - .5 : (d.minW || 150);
        const pack = c => { let x = 0, y = 0, rowH = 0; const at = [];
          dims.forEach(m => { const w = Math.max(m.cols * c, minW), h = labH + m.rows * c;
            if (x > 0 && x + w > bx.w) { x = 0; y += rowH + gap; rowH = 0; }
            at.push({ x, y, w, h }); x += w + gap; rowH = Math.max(rowH, h); });
          return { at, H: y + rowH }; };
        let c = d.cell ? d.cell * (bx.w < 560 ? .62 : 1) : (bx.w < 560 ? 3.6 : 6), pk = pack(c);
        while (pk.H > (d.maxH || 1.25) * bx.w && c > 2) { c -= .2; pk = pack(c); }
        S.height = Math.ceil(pk.H) + 6;
        const Ht = S.height;
        let p = 0;
        it.forEach((x, i) => {
          const a = pk.at[i], m = dims[i], match = x.claimed != null && x.counted === x.claimed;
          const inside = match ? PAL.emerald : PAL.pale, spill = PAL.amber, audit = x.audit || [], mk = x.marks;
          for (let j = 0; j < x.counted; j++, p++) {
            const q = j % m.cols, r = Math.floor(j / m.cols), n = audit[j] ? keyIdx(audit[j][0] + ':' + audit[j][1]) : -1;
            // a mention's own verse point stands for it when it is free, so hovering names the verse; otherwise a spare point
            const pt = n >= 0 && !S.on[n] ? n : nextFree();
            const over = x.claimed != null && j >= x.claimed, bright = .85 + jit2[pt] * .3, lit = mk ? !!mk[j] : true;
            const cc = mk ? (lit ? PAL.emerald : [.5, .56, .53]) : over ? spill : inside;
            put(S, pt, (a.x + (q + .5) * c) / bx.w, (a.y + labH + (r + .5) * c) / Ht, [cc[0] * bright, cc[1] * bright, cc[2] * bright], mk ? (lit ? .75 : .12) : over ? .8 : .45, c * (mk && !lit ? .95 : 1.15),
              i / it.length * .5 + j / Math.max(1, x.counted) * .4 + jit[pt] * .1, i * 100000 + j);
          }
          if (x.claimed) {   // the outline of the claimed number of cells; its last row stops where the count does
            const rows = Math.ceil(x.claimed / m.cols), lastW = x.claimed - (rows - 1) * m.cols, X0 = a.x - 1.5, Y0 = a.y + labH - 1.5, X1 = a.x + m.cols * c + 1.5, Y1 = a.y + labH + rows * c + 1.5, Xc = a.x + lastW * c + 1.5;
            S.shapes.push({ cls: 'claimbox ' + (match ? 'ok' : 'off'), pts: lastW < m.cols ? [[X0, Y0], [X1, Y0], [X1, Y1 - c], [Xc, Y1 - c], [Xc, Y1], [X0, Y1]] : [[X0, Y0], [X1, Y0], [X1, Y1], [X0, Y1]] });
          }
          const verdict = x.claimed == null ? '' : match ? 'ok' : 'off';
          S.labels.push(L(a.x / bx.w, a.y / Ht, '<b lang="ar">' + esc(x.ar || '') + '</b>' + (x.label && !ar ? ' <span>' + esc(x.label) + '</span>' : '') +
            '<em class="' + verdict + '">' + (x.note != null ? esc(x.note) : (x.claimed != null ? (ar ? 'المزعوم ' : 'claimed ') + nf(x.claimed) + ' · ' : '') + (ar ? 'المعدود ' : 'counted ') + nf(x.counted)) + '</em>', 'blab', 'st'));
        });
        function nextFree() { while (S.on[pool[freeP]]) freeP++; return pool[freeP++]; }
        S.kind = 'point';
        S.hover = n => { const v = S.grp[n]; if (v < 0) return null; const x = it[Math.floor(v / 100000)], j = v % 100000, a = (x.audit || [])[j];
          let h = '<b lang="ar">' + esc(x.ar || '') + '</b>' + (x.label && !ar ? ' ' + esc(x.label) : '') + '<br>' +
            (x.tips ? esc(x.tips[j] || '') : ar ? 'الموضع ' + nf(j + 1) + ' من ' + nf(x.counted) : 'mention ' + nf(j + 1) + ' of ' + nf(x.counted));
          if (x.claimed != null && j >= x.claimed) h += ar ? ' · بعد الرقم المزعوم' : ' · past the claimed number';
          if (a) { const k = keyIdx(a[0] + ':' + a[1]); if (k >= 0) h += '<br>' + esc(sname(sur[k])) + ' <span class="k">' + digits(a[0] + ':' + a[1]) + '</span>'; }
          return h; };
        S.link = n => { const v = S.grp[n]; if (v < 0) return 0; const x = it[Math.floor(v / 100000)], a = (x.audit || [])[v % 100000];
          return !a ? 0 : x.id ? { verse: [a[0], a[1]], claim: x.id } : d.verseLink ? { verse: [a[0], a[1]] } : a[0]; };
        return S;
      },

      // the lemmas as a grid of dots; the chosen number lights how many land on it exactly (gold) and within five (teal)
      grid(d, bx) {
        const S = blank(), M = Math.min(d.total || 0, N), C = Math.max(10, Math.round(Math.sqrt(M * bx.w / bx.h))), Rw = Math.ceil(M / C), c = Math.min(bx.w / C, bx.h / Rw);
        const ox = (bx.w - C * c) / 2, oy = (bx.h - Rw * c) / 2, pr = rng((d.n || 0) * 7919 + 1), perm = new Uint16Array(M);
        for (let j = 0; j < M; j++) perm[j] = j;
        for (let j = M - 1; j > 0; j--) { const q = Math.floor(pr() * (j + 1)), t = perm[j]; perm[j] = perm[q]; perm[q] = t; }
        const rank = new Uint16Array(M); for (let j = 0; j < M; j++) rank[perm[j]] = j;
        const small = bx.w < 560;
        for (let j = 0; j < M; j++) {
          const n = pool[N - 1 - j], r = Math.floor(j / C), q = j % C, rk = rank[j], ex = rk < (d.exact || 0), nr = !ex && rk < (d.near || 0);
          put(S, n, (ox + (q + .5) * c) / bx.w, (oy + (r + .5) * c) / bx.h, ex ? PAL.amber : nr ? PAL.teal : [.62, .8, .72], ex ? 1 : nr ? .8 : small ? .35 : .15,
            c * (ex ? 1.7 : nr ? 1.35 : small ? 1.05 : .85), jit[n], null);
        }
        S.hover = null;
        return S;
      },
    };

    // ---- the stage's state ----
    const st = { el: null, type: '', key: '', S: null, lab: null, w: 0, sp: 0, rect: null };
    // per point, eased toward the scene: where it sits in the box, how much it belongs to it, colour, glow, size
    const sx = new Float32Array(N), sy = new Float32Array(N), son = new Float32Array(N), scol = new Float32Array(N * 3), sem = new Float32Array(N), spx = new Float32Array(N).fill(2);
    let sInit = false, hot = -1, hotKind = '';
    function buildStage(force) {
      const w = want.stage, el = w && w.el && w.el.isConnected ? w.el : null;
      // no stage on this page: the labels go at once, and the points glide back to the sky from where they were
      if (!el) { if (st.lab) { st.lab.remove(); st.lab = null; } st.el = null; st.type = ''; st.key = ''; kick(); return; }
      const r = el.getBoundingClientRect(), key = w.type + '|' + want.lang + '|' + mirror + '|' + Math.round(r.width) + '|' + JSON.stringify(w.data);
      if (!force && el === st.el && key === st.key) return;
      if (el !== st.el) { if (st.lab) st.lab.remove(); st.lab = document.createElement('div'); st.lab.className = 'stlab'; st.lab.setAttribute('aria-hidden', 'true'); el.appendChild(st.lab); }
      st.el = el; st.type = w.type; st.key = key;
      const make = SCENES[w.type]; if (!make) { st.S = null; return; }
      freeP = 0;
      let bw = Math.max(1, r.width), bh = Math.max(1, r.height), S = make(w.data, { w: bw, h: bh });
      // a scene that sets its own height (blocks pack to their content) gets the box resized, then laid out again in it
      if (S.height && Math.abs(S.height - r.height) > 1) { el.style.height = S.height + 'px'; const r2 = el.getBoundingClientRect(); bw = r2.width; bh = r2.height; freeP = 0; S = make(w.data, { w: bw, h: bh }); }
      st.S = S; st.w = r.width;
      drawLabels(S, bw, bh);
      if (!sInit || reduced) { // first scene: start the eased state at the target, so nothing slides in from zero
        for (let n = 0; n < N; n++) { sx[n] = S.fx[n]; sy[n] = S.fy[n]; scol[3 * n] = S.col[3 * n]; scol[3 * n + 1] = S.col[3 * n + 1]; scol[3 * n + 2] = S.col[3 * n + 2]; sem[n] = S.em[n]; spx[n] = S.px[n]; son[n] = reduced ? S.on[n] : son[n]; }
        sInit = true;
      }
      hot = -1; kick();
    }
    let freeP = 0;
    function drawLabels(S, bw, bh) {
      const lab = st.lab; if (!lab) return;
      const pc = v => (v * 100).toFixed(3) + '%';
      // outlines are drawn in the box's pixels at the time of the build (a resize rebuilds), mirrored as a whole in Arabic
      const svg = S.shapes.length ? '<svg class="stsvg" viewBox="0 0 ' + bw.toFixed(1) + ' ' + bh.toFixed(1) + '" preserveAspectRatio="none">' +
        S.shapes.map(s => '<polygon class="' + s.cls + '" points="' + s.pts.map(([x, y]) => (mirror ? bw - x : x).toFixed(1) + ',' + y.toFixed(1)).join(' ') + '"/>').join('') + '</svg>' : '';
      lab.innerHTML = svg + S.labels.map(l => {
        // anchor: c/s/e = centred, or starting/ending at the point on the reading side; a trailing t hangs it from the point
        const x = mirror ? 1 - l.x : l.x, h = l.a[0], tx = h === 's' ? (mirror ? '-100%' : '0') : h === 'e' ? (mirror ? '0' : '-100%') : '-50%', ty = l.a[1] === 't' ? '0' : '-50%';
        return '<div class="' + l.cls + '" style="left:' + pc(x) + ';top:' + pc(l.y) + ';transform:translate(' + tx + ',' + ty + ')">' + l.html + '</div>';
      }).join('');
    }
    // how far the stage's points are gathered: they come in as the box rises into view and leave as it scrolls away
    function stageWant(r) {
      const vh = innerHeight;
      if (!r.width || !r.height) return 0;
      return clamp((vh * .97 - r.top) / (vh * .35), 0, 1) * (1 - clamp((Math.min(vh * .22, r.height * .5) - r.bottom) / Math.min(vh * .22, r.height * .5), 0, 1));
    }
    function stageFrame(dt, zs) {
      const S = st.S; if (!S) return false;
      if (st.el && !st.el.isConnected) st.el = null;
      const r = st.el ? (st.rect = st.el.getBoundingClientRect()) : st.rect;
      if (!r) return false;
      if (st.el && Math.abs(r.width - st.w) > 1) { buildStage(true); return true; }
      const w2 = st.el ? stageWant(r) : 0;
      st.sp = reduced ? w2 : st.sp + (w2 - st.sp) * (1 - Math.exp(-dt * 4.5));
      if (!st.el && st.sp < .004) {   // back in the sky: every point returns to plain
        st.S = null; st.sp = 0; son.fill(0); frB.fill(0); emB.fill(0); bsB.fill(1); colBuf.set(col);
        colAttr.needsUpdate = true; frAttr.needsUpdate = true; emAttr.needsUpdate = true; bsAttr.needsUpdate = true;
        return false;
      }
      const k = reduced ? 1 : 1 - Math.exp(-dt * 6), iw = innerWidth, ih = innerHeight, Wz = W * zs, Hz = H * zs, K = .5, moving = st.sp < .998 && st.sp > .002;
      const us = uSize, hk = hot;
      for (let n = 0; n < N; n++) {
        const on = S.on[n];
        son[n] += (on - son[n]) * k;
        if (son[n] < .002 && !on) { son[n] = 0; frB[n] = 0; emB[n] = 0; bsB[n] = 1; colBuf[3 * n] = col[3 * n]; colBuf[3 * n + 1] = col[3 * n + 1]; colBuf[3 * n + 2] = col[3 * n + 2]; continue; }
        if (on) {
          sx[n] += (S.fx[n] - sx[n]) * k; sy[n] += (S.fy[n] - sy[n]) * k; sem[n] += (S.em[n] - sem[n]) * k; spx[n] += (S.px[n] - spx[n]) * k;
          for (let c = 0; c < 3; c++) scol[3 * n + c] += (S.col[3 * n + c] - scol[3 * n + c]) * k;
        }
        const tt = clamp((st.sp - K * S.dl[n]) / (1 - K), 0, 1), e = ease(tt) * son[n];
        const X = ((r.left + (mirror ? 1 - sx[n] : sx[n]) * r.width) / iw - .5) * Wz, Y = (.5 - (r.top + sy[n] * r.height) / ih) * Hz;
        const n3 = 3 * n;
        pos[n3] = pos[n3] + (X - pos[n3]) * e; pos[n3 + 1] = pos[n3 + 1] + (Y - pos[n3 + 1]) * e;
        pos[n3 + 2] = pos[n3 + 2] * (1 - e) + (moving && !reduced ? Math.sin(Math.PI * tt) * 4 * arc[n] : 0);
        let cr = scol[n3], cg = scol[n3 + 1], cb = scol[n3 + 2], bs = spx[n] / (us * Math.max(.4, lerp(size[n], 1, e)));
        if (hk >= 0 && (hotKind === 'group' ? (S.grpOf ? S.grpOf(n) : S.grp[n]) === hk : false)) { bs *= 1.3; cr += (1 - cr) * .38; cg += (1 - cg) * .38; cb += (1 - cb) * .38; }
        colBuf[n3] = col[n3] + (cr - col[n3]) * e; colBuf[n3 + 1] = col[n3 + 1] + (cg - col[n3 + 1]) * e; colBuf[n3 + 2] = col[n3 + 2] + (cb - col[n3 + 2]) * e;
        frB[n] = e; emB[n] = sem[n]; bsB[n] = 1 + (bs - 1) * e;
      }
      if (st.lab) st.lab.style.opacity = clamp((st.sp - .35) / .5, 0, 1).toFixed(3);
      colAttr.needsUpdate = true; frAttr.needsUpdate = true; emAttr.needsUpdate = true; bsAttr.needsUpdate = true;
      return true;
    }

    // ---- sizing ----
    function resize(force) {
      const w = innerWidth, h = innerHeight;
      if (!force && w === lastW && Math.abs(h - lastH) < 120) return;
      lastW = w; lastH = h;
      renderer.setSize(w, h, false);
      cam.aspect = w / h; cam.updateProjectionMatrix();
      H = HW; W = HW * cam.aspect; mob = w < 760;
      relayout();
      if (form) goTo(form, true);
      if (st.el) buildStage(true);
    }
    let rz = 0;
    window.addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => resize(false), 150); });

    // ---- pointer: parallax, and on the home page and in a stage the verses answer to hover and tap ----
    const tip = document.getElementById('tip');
    let mouse = null, moved = false, hovered = -1, touchTip = 0, rotX = 0, rotY = 0;
    const PM = new THREE.Matrix4();
    function pick(px, py, rad, only) {
      let best = -1, bd = rad * rad;
      group.updateMatrixWorld(); cam.updateMatrixWorld();
      PM.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse).multiply(pts.matrixWorld);
      const e = PM.elements, vw = innerWidth, vh = innerHeight;
      for (let n = 0; n < N; n++) {
        if (only && !only[n]) continue;
        const x = pos[3 * n], y = pos[3 * n + 1], z = pos[3 * n + 2], w = e[3] * x + e[7] * y + e[11] * z + e[15];
        if (w <= 0) continue;
        const sx2 = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * .5 + .5) * vw, sy2 = (.5 - (e[1] * x + e[5] * y + e[9] * z + e[13]) / w * .5) * vh;
        const d = (sx2 - px) * (sx2 - px) + (sy2 - py) * (sy2 - py); if (d < bd) { bd = d; best = n; }
      }
      return best;
    }
    function tipHTML(n, touch) {
      const m = META[sur[n]], ar = want.lang === 'ar', w = wc[n];
      const words = ar ? (w === 1 ? 'كلمة واحدة' : w === 2 ? 'كلمتان' : digits(w) + (w % 100 >= 3 && w % 100 <= 10 ? ' كلمات' : ' كلمة')) : w + (w === 1 ? ' word' : ' words');
      return '<b>' + (ar ? m.ar : m.en) + '</b> <span class="k">' + digits((sur[n] + 1) + ':' + (ver[n] + 1)) + '</span><br>' +
        (m.place === 'Medina' ? (ar ? 'مدنية' : 'Medinan') : (ar ? 'مكية' : 'Meccan')) + ' · ' + words +
        (touch ? '<br><a href="?view=reader&s=' + (sur[n] + 1) + '" data-s="' + (sur[n] + 1) + '">' + (ar ? 'اقرأ السورة ‹' : 'Read the surah ›') + '</a>' : '');
    }
    // what a tap or click on a stage point opens: a surah in the reader, or a word in the search
    function linkHTML(L2) {
      const ar = want.lang === 'ar';
      if (!L2) return '';
      if (typeof L2 === 'number') return '<br><a href="?view=reader&s=' + L2 + '" data-s="' + L2 + '">' + (ar ? 'اقرأ السورة ‹' : 'Read the surah ›') + '</a>';
      if (L2.search) return '<br><a href="?view=search" data-q="' + esc(L2.search) + '" data-m="' + esc(L2.mode) + '">' + (ar ? 'ابحث عنها ‹' : 'Find it ›') + '</a>';
      if (L2.verse) return '<br><a href="?view=reader&s=' + L2.verse[0] + '&v=' + L2.verse[1] + '" data-vs="' + L2.verse.join(':') + '" data-c="' + esc(L2.claim || '') + '">' + (ar ? 'اقرأ الآية ‹' : 'Read the verse ›') + '</a>';
      return '';
    }
    function place(touch) {
      const tw = tip.offsetWidth, th = tip.offsetHeight;
      tip.style.transform = 'translate(' + clamp(mouse.x + 16, 8, innerWidth - tw - 8) + 'px,' + clamp(mouse.y + 16, 8, innerHeight - th - 8) + 'px)';
    }
    function setHover(n, touch) {
      if (!tip) return;
      hovered = n; mat.uniforms.uHover.value = n >= 0 ? sur[n] + 1 : -1; mat.uniforms.uHp.value = -1; hot = -1;
      document.body.style.cursor = n >= 0 && !touch ? 'pointer' : '';
      if (n < 0) { tip.hidden = true; clearTimeout(touchTip); touchTip = 0; kick(); return; }
      tip.innerHTML = tipHTML(n, touch); tip.hidden = false; tip.classList.toggle('touch', !!touch);
      place(touch); kick();
    }
    // a stage point: the scene says what it is; a verse lights its surah, a group lights itself, a mention lights alone
    function setStageHover(n, touch) {
      const S = st.S;
      if (!tip || !S) return;
      hovered = n; mat.uniforms.uHover.value = -1; mat.uniforms.uHp.value = -1; hot = -1; hotKind = '';
      const html = n >= 0 && S.hover ? S.hover(n) : null;
      if (n < 0 || !html) { hovered = -1; document.body.style.cursor = ''; tip.hidden = true; clearTimeout(touchTip); touchTip = 0; kick();
        window.dispatchEvent(new CustomEvent('sky:hover', { detail: null })); return; }
      if (S.kind === 'verse') { mat.uniforms.uHover.value = sur[n] + 1;   // the page can say in words what the tip says
        window.dispatchEvent(new CustomEvent('sky:hover', { detail: { s: sur[n] + 1, v: ver[n] + 1, place: META[sur[n]].place } })); }
      else if (S.kind === 'group') { hot = S.grpOf ? S.grpOf(n) : S.grp[n]; hotKind = 'group'; }
      else mat.uniforms.uHp.value = n;
      const link = S.link ? S.link(n) : null;
      document.body.style.cursor = !touch && link ? 'pointer' : '';
      tip.innerHTML = html + (touch ? linkHTML(link) : ''); tip.hidden = false; tip.classList.toggle('touch', !!touch);
      place(touch); kick();
    }
    const blocked = t => !t.closest || (!t.closest('.stage') && !!t.closest('a,button,input,select,textarea,label,form,.tile,.card,.side,.topbar,.kpis,.askres,.subtabs,.homet,.homesub,.eyebrow,.ctas,p,h1,h2,h3,#tip'));
    const pickable = () => form === 'hero' && morph >= 1 && uAlpha > .5 && st.sp < .05;
    const inStage = (x, y) => { if (!st.S || !st.el || !st.S.hover || st.sp < .9) return false; const r = st.el.getBoundingClientRect(); return x >= r.left - 8 && x <= r.right + 8 && y >= r.top - 8 && y <= r.bottom + 8; };
    const read = s => window.dispatchEvent(new CustomEvent('sky:read', { detail: { surah: s } }));
    const follow = L2 => { if (!L2) return; if (typeof L2 === 'number') read(L2);
      else if (L2.search) window.dispatchEvent(new CustomEvent('sky:search', { detail: { q: L2.search, mode: L2.mode } }));
      else if (L2.verse) window.dispatchEvent(new CustomEvent('sky:verse', { detail: { s: L2.verse[0], v: L2.verse[1], claim: L2.claim } })); };
    let stageHover = false;
    window.addEventListener('pointermove', e => {
      if (e.pointerType !== 'mouse') return;
      mouse = { x: e.clientX, y: e.clientY }; kick();
      if (inStage(e.clientX, e.clientY) && !blocked(e.target)) { stageHover = true; moved = true; return; }
      if (stageHover) { stageHover = false; if (!touchTip) setStageHover(-1); }
      if (!pickable() || blocked(e.target)) { if (hovered >= 0 && !touchTip) setHover(-1); return; }
      moved = true;
    }, { passive: true });
    document.addEventListener('pointerleave', () => { mouse = null; if (hovered >= 0) (stageHover ? setStageHover(-1) : setHover(-1)); stageHover = false; });
    window.addEventListener('click', e => {
      const a = e.target.closest && e.target.closest('#tip a[data-s], #tip a[data-q], #tip a[data-vs]');
      if (a) { e.preventDefault(); const wasStage = stageHover || (st.S && st.sp > .9); (wasStage ? setStageHover : setHover)(-1);
        if (a.dataset.s) read(+a.dataset.s); else if (a.dataset.vs) follow({ verse: a.dataset.vs.split(':').map(Number), claim: a.dataset.c });
        else follow({ search: a.dataset.q, mode: a.dataset.m }); return; }
      if (inStage(e.clientX, e.clientY) && !blocked(e.target)) {
        if (e.pointerType === 'mouse' || (!e.pointerType && fine)) { if (hovered >= 0 && stageHover) { const L2 = st.S.link ? st.S.link(hovered) : null; if (L2) { setStageHover(-1); follow(L2); } } return; }
        mouse = { x: e.clientX, y: e.clientY };
        const lit = st.S.prefer ? pick(e.clientX, e.clientY, 28, st.S.prefer) : -1, n = lit >= 0 ? lit : pick(e.clientX, e.clientY, 20, st.S.on);
        stageHover = true;
        if (n < 0) { setStageHover(-1); return; }
        setStageHover(n, true); clearTimeout(touchTip); touchTip = setTimeout(() => setStageHover(-1), 5000);
        return;
      }
      if (!pickable() || blocked(e.target)) return;
      if (e.pointerType === 'mouse' || (!e.pointerType && fine)) { if (hovered >= 0) { const s = sur[hovered] + 1; setHover(-1); read(s); } return; }
      mouse = { x: e.clientX, y: e.clientY };
      const n = pick(e.clientX, e.clientY, 22);
      if (n < 0) { setHover(-1); return; }
      setHover(n, true); touchTip = setTimeout(() => setHover(-1), 5000);
    });
    window.addEventListener('scroll', () => { if (touchTip) { (stageHover ? setStageHover : setHover)(-1); stageHover = false; } else if (stageHover && hovered >= 0) moved = true; }, { passive: true });

    // ---- the loop: full speed while something moves, about 30 fps otherwise, still when reduced ----
    // After a while with no touch, scroll or key the sky holds still (a long read shouldn't keep the GPU busy);
    // any interaction wakes it.
    let raf = 0, lastDraw = performance.now(), intro = reduced ? 1 : 0, active = performance.now(), lastScroll = 0;
    function kick() { active = performance.now(); if (!raf) raf = requestAnimationFrame(loop); }
    ['scroll', 'touchstart', 'keydown', 'wheel'].forEach(ev => window.addEventListener(ev, kick, { passive: true }));
    window.addEventListener('scroll', () => { lastScroll = performance.now(); }, { passive: true });
    function loop(now) {
      raf = 0;
      // a stage on screen follows every frame of a scroll, so its points never trail its labels
      const stBusy = !!st.S && ((st.sp > .001 && now - lastScroll < 250) || Math.abs(st.sp - (st.el ? stageWant(st.el.getBoundingClientRect()) : 0)) > .002);
      const busy = morph < 1 || intro < 1 || Math.abs(hiOn - hiTarget) > .002 || Math.abs(uAlpha - ALPHA[form] * intro) > .003 || fadeIn < 1 || stBusy;
      if (busy || (!reduced && now - active < 25000)) raf = requestAnimationFrame(loop);
      if (!busy && !reduced && now - lastDraw < 32) return;   // idle: about 30 frames a second is plenty for a slow spin
      const dt = Math.min((now - lastDraw) / 1000, .05); lastDraw = now;

      if (intro < 1) intro = Math.min(1, intro + dt / 1.8);
      const ie = 1 - Math.pow(1 - intro, 4);
      cam.position.z = lerp(118, CAMZ, ie);
      if (!reduced) spin += dt * .03;
      if (form === 'hero' || form === 'galaxy') setGalaxy(G[form]());

      if (morph < 1) morph = Math.min(1, morph + dt / morphDur);
      const Kc = .55, dynamic = morph < 1 || ((form === 'hero' || form === 'galaxy') && !reduced);
      if (dynamic) {
        for (let n = 0; n < N; n++) {
          targetInto(n, out);
          if (morph < 1) {
            const tt = clamp((morph - Kc * DL[n]) / (1 - Kc), 0, 1), e = ease(tt);
            base[3 * n] = snap[3 * n] + (out[0] - snap[3 * n]) * e;
            base[3 * n + 1] = snap[3 * n + 1] + (out[1] - snap[3 * n + 1]) * e;
            base[3 * n + 2] = snap[3 * n + 2] + (out[2] - snap[3 * n + 2]) * e + Math.sin(Math.PI * tt) * 7 * arc[n];
          } else { base[3 * n] = out[0]; base[3 * n + 1] = out[1]; base[3 * n + 2] = out[2]; }
        }
      }
      pos.set(base);
      const k = 1 - Math.exp(-dt * 4);
      uSize += ((SIZE[form] || 2) * clamp(innerWidth / 1440, .72, 1) - uSize) * k;
      // the stage is drawn over the sky: it follows its box, and the sky behind steps back
      const staged = stageFrame(dt, cam.position.z / CAMZ);
      posAttr.needsUpdate = true;
      uAlpha += (ALPHA[form] * ie - uAlpha) * k;
      hiOn += (hiTarget - hiOn) * (1 - Math.exp(-dt * 5));
      if (fadeIn < 1) fadeIn = Math.min(1, fadeIn + dt / .8);
      const g2 = staged ? st.sp : 0;
      mat.uniforms.uSize.value = uSize;
      mat.uniforms.uAlpha.value = uAlpha * fadeIn;
      mat.uniforms.uHiOn.value = hiOn;
      mat.uniforms.uBack.value = 1 - .55 * g2;
      mat.uniforms.uStage.value = Math.min(2.4, 1 / Math.max(.2, ALPHA[form] || .5)) * ie;
      mat.uniforms.uTime.value = reduced ? 0 : now / 1000;
      starMat.opacity = .5 * ie;

      // parallax toward the pointer, none while a stage is up so its points stay on their labels
      const live = mouse && fine && !reduced, flat = 1 - g2;
      const tx = live ? ((mouse.y / innerHeight) - .5) * .06 * flat : 0, ty = live ? ((mouse.x / innerWidth) - .5) * .1 * flat : 0;
      rotX += (tx - rotX) * .05; rotY += (ty - rotY) * .05;
      if (g2 > .5) { rotX *= .8; rotY *= .8; }
      group.rotation.set(rotX, rotY, 0); stars.rotation.set(rotX * .5, rotY * .5 + now / 1000 * .003, 0);

      if (mouse && fine && moved && stageHover && inStage(mouse.x, mouse.y)) { moved = false;   // a lit point within reach wins over the dim ones
        const lit = st.S.prefer ? pick(mouse.x, mouse.y, 24, st.S.prefer) : -1; setStageHover(lit >= 0 ? lit : pick(mouse.x, mouse.y, 12, st.S.on)); }
      else if (mouse && fine && moved && pickable()) { moved = false; setHover(pick(mouse.x, mouse.y, 14)); }
      else if (hovered >= 0 && !stageHover && !pickable() && !touchTip) setHover(-1);
      renderer.render(scene3, cam);
    }
    document.addEventListener('visibilitychange', () => { if (!document.hidden) kick(); });

    resize(true);
    return {
      apply(s) {
        const m = s.lang === 'ar', was = left;
        measure();
        if (m !== mirror || Math.abs(left - was) > .002) {   // language flipped the page, or the sidebar appeared: flow to the new places
          mirror = m; relayout(); if (form) goTo(form, false, true); if (hovered >= 0) setHover(-1);
        }
        goTo(formOf(s.view));
        setHighlight(s.stage ? null : s.keys, s.stage ? 0 : s.surah);
        if (hovered >= 0 && formOf(s.view) !== 'hero') { stageHover ? setStageHover(-1) : setHover(-1); stageHover = false; }
        buildStage(false);
      },
      relayout() { relayout(); if (form) goTo(form, true); if (st.el) buildStage(true); },
    };
  }

  function boot() {
    init().then(api => {
      const root = document.documentElement;
      if (!api) { root.classList.add('no-gl'); window.dispatchEvent(new Event('sky:nogl')); return; }
      scene = api; root.classList.add('gl'); root.classList.remove('no-gl');
      const c = document.getElementById('gl'); if (c) c.classList.add('on');
      scene.apply(want);
      window.QTA_SKY.relayout = () => scene.relayout();
      window.dispatchEvent(new Event('sky:ready'));
    }).catch(() => { document.documentElement.classList.add('no-gl'); window.dispatchEvent(new Event('sky:nogl')); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
