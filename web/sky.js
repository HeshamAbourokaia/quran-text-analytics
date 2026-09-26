// The verse sky behind the app: the landing page's field of 6,236 points, one per verse (gold for
// Meccan surahs, green for Medinan), re-arranged for each part of the app. Home shows the galaxy of
// surahs, the counting pages stand the surahs up as columns, the Mecca/Medina and lab pages sort the
// verses by length, the claim pages scatter them. The reader lights up the surah you are reading and
// the word search lights up every verse that matches.
//
// Loaded after data.js; three.js is imported on demand (the landing page's copy is usually cached).
// window.QTA_SKY is the app's handle. Calls made before the scene is ready are remembered and applied.
(function () {
  'use strict';
  const THREE_URL = 'https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.min.js';
  const want = { view: 'home', lang: 'en', keys: null, surah: 0 };
  let scene = null;
  const push = () => { if (scene) scene.apply(want); };
  window.QTA_SKY = {
    setView(view) { want.view = view; push(); },
    setLang(lang) { want.lang = lang; push(); },
    highlightKeys(keys) { want.keys = keys && keys.length ? keys : null; want.surah = 0; push(); },
    highlightSurah(n) { want.surah = n || 0; want.keys = null; push(); },
    clearHighlight() { want.keys = null; want.surah = 0; push(); },
  };

  // Which arrangement each page uses.
  const FORM = {
    home: 'hero',
    overview: 'bars', word: 'bars', letters: 'bars', nlp: 'bars', advanced: 'bars', emotion: 'bars', pronouns: 'bars', dashboard: 'bars',
    mecca: 'split', classifier: 'split', stats: 'split', cluster: 'split', hifz: 'split',
    auditor: 'dust', symmetry: 'dust', n19: 'dust', abjad: 'dust', structural: 'dust', coincidence: 'dust', science: 'dust',
  };
  const formOf = v => FORM[v] || 'galaxy';

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = t => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

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
    const geo = new THREE.BufferGeometry();
    const posAttr = new THREE.BufferAttribute(pos, 3); posAttr.setUsage(THREE.DynamicDrawUsage);
    const hiAttr = new THREE.BufferAttribute(hi, 1); hiAttr.setUsage(THREE.DynamicDrawUsage);
    geo.setAttribute('position', posAttr);
    geo.setAttribute('aColor', new THREE.BufferAttribute(col, 3));
    geo.setAttribute('aSize', new THREE.BufferAttribute(size, 1));
    geo.setAttribute('aSurah', new THREE.BufferAttribute(surA, 1));
    geo.setAttribute('aPhase', new THREE.BufferAttribute(phase, 1));
    geo.setAttribute('aHi', hiAttr);
    const mat = new THREE.ShaderMaterial({
      uniforms: { uTime: { value: 0 }, uSize: { value: 2.3 }, uPR: { value: PR }, uAlpha: { value: 0 }, uHover: { value: -1 }, uHiOn: { value: 0 } },
      vertexShader: [
        'attribute vec3 aColor; attribute float aSize; attribute float aSurah; attribute float aPhase; attribute float aHi;',
        'uniform float uTime; uniform float uSize; uniform float uPR; uniform float uHover; uniform float uHiOn;',
        'varying vec3 vC; varying float vA;',
        'void main(){',
        '  vec4 mv = modelViewMatrix * vec4(position, 1.0);',
        '  float h = 1.0 - step(0.5, abs(aSurah - uHover));',
        '  float k = max(h, aHi * uHiOn);',
        '  gl_PointSize = uSize * aSize * uPR * (1.0 + 1.3 * k) * (60.0 / max(1.0, -mv.z));',
        '  gl_Position = projectionMatrix * mv;',
        '  vC = mix(aColor, vec3(1.0, 0.96, 0.84), 0.5 * k);',
        '  float tw = 0.78 + 0.22 * sin(uTime * 1.3 + aPhase * 6.2831);',
        '  vA = tw * mix(mix(1.0, 0.26, uHiOn), 1.9, k);',
        '}'].join('\n'),
      fragmentShader: [
        'uniform float uAlpha; varying vec3 vC; varying float vA;',
        'void main(){',
        '  float d = length(gl_PointCoord - 0.5);',
        '  if (d > 0.5) discard;',
        '  gl_FragColor = vec4(vC, pow(1.0 - d * 2.0, 1.5) * uAlpha * vA);',
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
    const out = [0, 0, 0];
    function targetInto(n, o) {
      if (form === 'hero' || form === 'galaxy') { galaxyInto(o, n); return; }
      const a = T[form]; o[0] = a[3 * n]; o[1] = a[3 * n + 1]; o[2] = a[3 * n + 2];
    }
    function goTo(f, instant, force) {
      if (f === form && !instant && !force) return;
      snap.set(pos);
      const prev = form;
      form = f;
      if (form === 'hero' || form === 'galaxy') setGalaxy(G[form]());
      // stagger: columns sweep in surah order, other arrangements settle in a random order
      for (let n = 0; n < N; n++) DL[n] = form === 'bars' ? sur[n] / 113 * .85 + jit[n] * .15 : form === 'split' ? jit2[n] : jit[n];
      morph = instant || reduced || prev === null ? 1 : 0;
      morphDur = prev === 'hero' && form === 'galaxy' || prev === 'galaxy' && form === 'hero' ? 1.5 : 1.8;
      if (morph === 1) for (let n = 0; n < N; n++) { targetInto(n, out); pos[3 * n] = out[0]; pos[3 * n + 1] = out[1]; pos[3 * n + 2] = out[2]; }
      posAttr.needsUpdate = true;
      kick();
    }

    // ---- highlights: the reader's surah, the search's verses ----
    let hiKeys = null, hiSurah = 0;
    function setHighlight(keys, surah) {
      if (keys === hiKeys && surah === hiSurah) return;
      hiKeys = keys; hiSurah = surah;
      hi.fill(0);
      if (surah >= 1 && surah <= VW.length) for (let n = start[surah - 1]; n < start[surah]; n++) hi[n] = 1;
      else if (keys) for (const k of keys) { const c = k.indexOf(':'), s = +k.slice(0, c), v = +k.slice(c + 1);
        if (s >= 1 && s <= VW.length && v >= 1 && v <= VW[s - 1].length) hi[start[s - 1] + v - 1] = 1; }
      hiAttr.needsUpdate = true;
      hiTarget = surah || keys ? 1 : 0;
      kick();
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
    }
    let rz = 0;
    window.addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(() => resize(false), 150); });

    // ---- pointer: parallax, and on the home page the verses answer to hover and tap ----
    const tip = document.getElementById('tip');
    let mouse = null, moved = false, hovered = -1, touchTip = 0, rotX = 0, rotY = 0;
    const PM = new THREE.Matrix4();
    function project(n) {
      group.updateMatrixWorld(); cam.updateMatrixWorld();
      PM.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse).multiply(pts.matrixWorld);
      const e = PM.elements, x = pos[3 * n], y = pos[3 * n + 1], z = pos[3 * n + 2], w = e[3] * x + e[7] * y + e[11] * z + e[15];
      return w <= 0 ? null : { x: ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * .5 + .5) * innerWidth, y: (.5 - (e[1] * x + e[5] * y + e[9] * z + e[13]) / w * .5) * innerHeight };
    }
    function pick(px, py, rad) {
      let best = -1, bd = rad * rad;
      group.updateMatrixWorld(); cam.updateMatrixWorld();
      PM.multiplyMatrices(cam.projectionMatrix, cam.matrixWorldInverse).multiply(pts.matrixWorld);
      const e = PM.elements, vw = innerWidth, vh = innerHeight;
      for (let n = 0; n < N; n++) {
        const x = pos[3 * n], y = pos[3 * n + 1], z = pos[3 * n + 2], w = e[3] * x + e[7] * y + e[11] * z + e[15];
        if (w <= 0) continue;
        const sx = ((e[0] * x + e[4] * y + e[8] * z + e[12]) / w * .5 + .5) * vw, sy = (.5 - (e[1] * x + e[5] * y + e[9] * z + e[13]) / w * .5) * vh;
        const d = (sx - px) * (sx - px) + (sy - py) * (sy - py); if (d < bd) { bd = d; best = n; }
      }
      return best;
    }
    const digits = s => (want.lang === 'ar' ? String(s).replace(/\d/g, c => '٠١٢٣٤٥٦٧٨٩'[c]) : String(s));
    function tipHTML(n, touch) {
      const m = META[sur[n]], ar = want.lang === 'ar', w = wc[n];
      const words = ar ? (w === 1 ? 'كلمة واحدة' : w === 2 ? 'كلمتان' : digits(w) + (w % 100 >= 3 && w % 100 <= 10 ? ' كلمات' : ' كلمة')) : w + (w === 1 ? ' word' : ' words');
      return '<b>' + (ar ? m.ar : m.en) + '</b> <span class="k">' + digits((sur[n] + 1) + ':' + (ver[n] + 1)) + '</span><br>' +
        (m.place === 'Medina' ? (ar ? 'مدنية' : 'Medinan') : (ar ? 'مكية' : 'Meccan')) + ' · ' + words +
        (touch ? '<br><a href="?view=reader&s=' + (sur[n] + 1) + '" data-s="' + (sur[n] + 1) + '">' + (ar ? 'اقرأ السورة ‹' : 'Read the surah ›') + '</a>' : '');
    }
    function setHover(n, touch) {
      if (!tip) return;
      hovered = n; mat.uniforms.uHover.value = n >= 0 ? sur[n] + 1 : -1;
      document.body.style.cursor = n >= 0 && !touch ? 'pointer' : '';
      if (n < 0) { tip.hidden = true; clearTimeout(touchTip); touchTip = 0; kick(); return; }
      tip.innerHTML = tipHTML(n, touch); tip.hidden = false; tip.classList.toggle('touch', !!touch);
      const tw = tip.offsetWidth, th = tip.offsetHeight;
      tip.style.transform = 'translate(' + clamp(mouse.x + 16, 8, innerWidth - tw - 8) + 'px,' + clamp(mouse.y + 16, 8, innerHeight - th - 8) + 'px)';
      kick();
    }
    const blocked = t => !t.closest || !!t.closest('a,button,input,select,textarea,label,form,.tile,.card,.side,.topbar,.kpis,.askres,.subtabs,.homet,.homesub,.eyebrow,.ctas,p,h1,h2,h3,#tip');
    const pickable = () => form === 'hero' && morph >= 1 && uAlpha > .5;
    const read = s => window.dispatchEvent(new CustomEvent('sky:read', { detail: { surah: s } }));
    window.addEventListener('pointermove', e => {
      if (e.pointerType !== 'mouse') return;
      mouse = { x: e.clientX, y: e.clientY }; kick();
      if (!pickable() || blocked(e.target)) { if (hovered >= 0 && !touchTip) setHover(-1); return; }
      moved = true;
    }, { passive: true });
    document.addEventListener('pointerleave', () => { mouse = null; if (hovered >= 0) setHover(-1); });
    window.addEventListener('click', e => {
      const a = e.target.closest && e.target.closest('#tip a[data-s]');
      if (a) { e.preventDefault(); setHover(-1); read(+a.dataset.s); return; }
      if (!pickable() || blocked(e.target)) return;
      if (e.pointerType === 'mouse' || (!e.pointerType && fine)) { if (hovered >= 0) { const s = sur[hovered] + 1; setHover(-1); read(s); } return; }
      mouse = { x: e.clientX, y: e.clientY };
      const n = pick(e.clientX, e.clientY, 22);
      if (n < 0) { setHover(-1); return; }
      setHover(n, true); touchTip = setTimeout(() => setHover(-1), 5000);
    });
    window.addEventListener('scroll', () => { if (touchTip) setHover(-1); }, { passive: true });

    // ---- the loop: full speed while something moves, about 30 fps otherwise, still when reduced ----
    // After a while with no touch, scroll or key the sky holds still (a long read shouldn't keep the GPU busy);
    // any interaction wakes it.
    let raf = 0, lastDraw = performance.now(), intro = reduced ? 1 : 0, active = performance.now();
    function kick() { active = performance.now(); if (!raf) raf = requestAnimationFrame(loop); }
    ['scroll', 'touchstart', 'keydown', 'wheel'].forEach(ev => window.addEventListener(ev, kick, { passive: true }));
    function loop(now) {
      raf = 0;
      const busy = morph < 1 || intro < 1 || Math.abs(hiOn - hiTarget) > .002 || Math.abs(uAlpha - ALPHA[form] * intro) > .003 || fadeIn < 1;
      if (busy || (!reduced && now - active < 25000)) raf = requestAnimationFrame(loop);
      if (!busy && !reduced && now - lastDraw < 32) return;   // idle: about 30 frames a second is plenty for a slow spin
      const dt = Math.min((now - lastDraw) / 1000, .05); lastDraw = now;

      if (intro < 1) intro = Math.min(1, intro + dt / 1.8);
      const ie = 1 - Math.pow(1 - intro, 4);
      cam.position.z = lerp(118, CAMZ, ie);
      if (!reduced) spin += dt * .03;
      if (form === 'hero' || form === 'galaxy') setGalaxy(G[form]());

      if (morph < 1) morph = Math.min(1, morph + dt / morphDur);
      const K = .55, dynamic = morph < 1 || ((form === 'hero' || form === 'galaxy') && !reduced);
      if (dynamic) {
        for (let n = 0; n < N; n++) {
          targetInto(n, out);
          if (morph < 1) {
            const tt = clamp((morph - K * DL[n]) / (1 - K), 0, 1), e = ease(tt);
            pos[3 * n] = snap[3 * n] + (out[0] - snap[3 * n]) * e;
            pos[3 * n + 1] = snap[3 * n + 1] + (out[1] - snap[3 * n + 1]) * e;
            pos[3 * n + 2] = snap[3 * n + 2] + (out[2] - snap[3 * n + 2]) * e + Math.sin(Math.PI * tt) * 7 * arc[n];
          } else { pos[3 * n] = out[0]; pos[3 * n + 1] = out[1]; pos[3 * n + 2] = out[2]; }
        }
        posAttr.needsUpdate = true;
      }
      const k = 1 - Math.exp(-dt * 4);
      uSize += ((SIZE[form] || 2) * clamp(innerWidth / 1440, .72, 1) - uSize) * k;
      uAlpha += (ALPHA[form] * ie - uAlpha) * k;
      hiOn += (hiTarget - hiOn) * (1 - Math.exp(-dt * 5));
      if (fadeIn < 1) fadeIn = Math.min(1, fadeIn + dt / .8);
      mat.uniforms.uSize.value = uSize;
      mat.uniforms.uAlpha.value = uAlpha * fadeIn;
      mat.uniforms.uHiOn.value = hiOn;
      mat.uniforms.uTime.value = reduced ? 0 : now / 1000;
      starMat.opacity = .5 * ie;

      const live = mouse && fine && !reduced;
      const tx = live ? ((mouse.y / innerHeight) - .5) * .06 : 0, ty = live ? ((mouse.x / innerWidth) - .5) * .1 : 0;
      rotX += (tx - rotX) * .05; rotY += (ty - rotY) * .05;
      group.rotation.set(rotX, rotY, 0); stars.rotation.set(rotX * .5, rotY * .5 + now / 1000 * .003, 0);

      if (mouse && fine && moved && pickable()) { moved = false; setHover(pick(mouse.x, mouse.y, 14)); }
      else if (hovered >= 0 && !pickable() && !touchTip) setHover(-1);
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
        setHighlight(s.keys, s.surah);
        if (hovered >= 0 && formOf(s.view) !== 'hero') setHover(-1);
      },
      relayout() { relayout(); if (form) goTo(form, true); },
    };
  }

  function boot() {
    init().then(api => {
      const root = document.documentElement;
      if (!api) { root.classList.add('no-gl'); return; }
      scene = api; root.classList.add('gl');
      const c = document.getElementById('gl'); if (c) c.classList.add('on');
      scene.apply(want);
      window.QTA_SKY.relayout = () => scene.relayout();
    }).catch(() => document.documentElement.classList.add('no-gl'));
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
