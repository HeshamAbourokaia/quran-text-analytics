// Tests for the site as an installable app (web/manifest*.webmanifest, web/sw.js, web/icons): node data-build/tests/test_pwa.js
// The two manifests describe one app in two languages, their links and icons are real, and the service worker keeps
// every file the app needs to start and to read, so a new page or script cannot be added and quietly left out.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..', '..');
const WEB = path.join(ROOT, 'web');
global.self = { addEventListener() {}, location: { origin: 'https://quraninsights.vercel.app' } };   // the worker's own world, enough to read it
const SW = require(path.join(WEB, 'sw.js'));
const read = f => fs.readFileSync(path.join(WEB, f), 'utf8');
const EN = JSON.parse(read('manifest.webmanifest')), AR = JSON.parse(read('manifest-ar.webmanifest'));
const APP = read('app.html'), INDEX = read('index.html');
const SLUGS = (() => {   // the short links vercel.json sends to app.html
  const v = JSON.parse(fs.readFileSync(path.join(ROOT, 'vercel.json'), 'utf8'));
  const src = v.rewrites.find(r => r.destination === '/app.html').source;
  return new Set(src.match(/\(([^)]*)\)/)[1].split('|'));
})();
const exists = u => fs.existsSync(path.join(WEB, u.replace(/^\//, '').split('?')[0] || 'index.html'));
const pngSize = f => { const b = fs.readFileSync(path.join(WEB, f.replace(/^\//, ''))); assert.equal(b.toString('ascii', 1, 4), 'PNG', f + ' is not a PNG'); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };
// a page address the app answers: a short link, or app.html itself
const opens = u => { const p = u.split('?')[0]; return p === '/app.html' || SLUGS.has(p.replace(/^\//, '')); };

const tests = {
  'each manifest has what a phone needs to install it'() {
    for (const m of [EN, AR]) {
      for (const k of ['id', 'name', 'short_name', 'start_url', 'scope', 'display', 'background_color', 'theme_color', 'icons', 'lang', 'dir'])
        assert.ok(m[k], m.lang + ': ' + k);
      assert.equal(m.display, 'standalone');
      assert.ok(m.short_name.length <= 15, m.lang + ': the short name fits under an icon');
      const kinds = new Set(m.icons.map(i => i.sizes + ' ' + i.purpose));
      for (const k of ['192x192 any', '512x512 any', '192x192 maskable', '512x512 maskable']) assert.ok(kinds.has(k), m.lang + ': ' + k);
    }
  },
  'English and Arabic are one app, and each opens in its own language'() {
    assert.equal(EN.id, AR.id, 'two ids would install two apps');
    assert.equal(EN.lang, 'en'); assert.equal(EN.dir, 'ltr'); assert.ok(!/lang=ar/.test(EN.start_url));
    assert.equal(AR.lang, 'ar'); assert.equal(AR.dir, 'rtl'); assert.ok(/[?&]lang=ar\b/.test(AR.start_url));
    assert.ok(/[؀-ۿ]/.test(AR.name) && /[؀-ۿ]/.test(AR.description), 'the Arabic manifest speaks Arabic');
    assert.equal(EN.name, 'Quran Insights'); assert.equal(AR.name, 'بصائر قرآنية');
    assert.ok(APP.includes("lang==='ar' ? 'بصائر قرآنية' : 'Quran Insights'"), 'the app names itself as the manifests do');
    assert.deepEqual(EN.icons, AR.icons);
    assert.equal(EN.theme_color, AR.theme_color);
    assert.ok(APP.includes('<meta name="theme-color" content="' + EN.theme_color + '" />'), 'the bar colour is the page\'s own');
  },
  'every address a manifest opens is a page of the app, in the right language'() {
    for (const m of [EN, AR]) {
      assert.ok(opens(m.start_url), m.lang + ' start ' + m.start_url);
      assert.equal(m.shortcuts.length, 4);
      for (const s of m.shortcuts) {
        assert.ok(opens(s.url), m.lang + ' shortcut ' + s.url);
        assert.equal(/[?&]lang=ar\b/.test(s.url), m.lang === 'ar', m.lang + ' shortcut language ' + s.url);
        for (const i of s.icons || []) assert.ok(exists(i.src), i.src);
      }
    }
    // the shortcuts are named as the menu names their pages (a page's menu name equals its h1)
    for (const [a, b] of EN.shortcuts.map((s, i) => [s, AR.shortcuts[i]])) {
      const id = Object.entries({ reader: '/reader', search: '/search', hifz: '/hifz', duas: '/duas' }).find(([, u]) => a.url === u)[0];
      const item = APP.match(new RegExp("\\{id:'" + id + "',en:(\"[^\"]*\"|'[^']*'),ar:'([^']*)'\\}"));
      assert.ok(item, id + ' is not in the menu');
      assert.equal(a.name, item[1].slice(1, -1)); assert.equal(b.name, item[2]);
    }
  },
  'the icons are real PNGs of the sizes they claim'() {
    for (const i of EN.icons) { const [w, h] = pngSize(i.src); assert.equal(w + 'x' + h, i.sizes, i.src); }
    assert.deepEqual(pngSize('icons/apple-touch-icon.png'), [180, 180]);
  },
  'both pages link the manifest and the iPhone icon; the app starts the service worker'() {
    for (const [name, page] of [['app.html', APP], ['index.html', INDEX]]) {
      assert.ok(page.includes('<link rel="manifest" id="qimf" href="/manifest.webmanifest" />'), name + ': manifest');
      assert.ok(page.includes('<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />'), name + ': iPhone icon');
      assert.ok(page.includes("'/manifest-ar.webmanifest'"), name + ': the Arabic page offers the Arabic app');
    }
    assert.ok(APP.includes("navigator.serviceWorker.register('/sw.js')"), 'app.html starts the service worker');
    assert.ok(!INDEX.includes('serviceWorker'), 'a visit to the tour alone downloads nothing more');
  },
  'the service worker keeps every script the app starts with'() {
    const local = [...APP.matchAll(/<script defer src="([^"]+)"><\/script>/g)].map(m => m[1]).filter(s => !/^https?:/.test(s));
    assert.ok(local.length > 15, 'only ' + local.length + ' scripts found');
    const missing = local.filter(s => !SW.SHELL.includes('/' + s));
    assert.deepEqual(missing, [], 'a script app.html starts with is not kept for offline');
    for (const u of SW.SHELL) assert.ok(exists(u), u + ' does not exist');
    assert.ok(SW.SHELL.includes('/app.html') && SW.SHELL.includes('/'));
  },
  'the service worker keeps every file the pages load later (LAZY)'() {
    const lazy = APP.match(/const LAZY = \{([\s\S]*?)\};/)[1];
    const files = [...lazy.matchAll(/'([^']+\.js)'/g)].map(m => m[1]);
    const local = files.filter(s => !/^https?:/.test(s)), far = files.filter(s => /^https?:/.test(s));
    assert.ok(local.includes('corpus.js') && local.includes('translation_en.js'));
    assert.deepEqual(local.filter(s => !SW.READING.includes('/' + s)), [], 'a LAZY file is not kept for offline');
    for (const u of SW.READING) assert.ok(exists(u), u + ' does not exist');
    for (const u of far) assert.ok(SW.HOSTS.includes(new URL(u).hostname), u + ' is not kept when used');
  },
  'every short link is kept as the one app page, and nothing else is'() {
    for (const s of SLUGS) assert.equal(SW.pageKey('/' + s), '/app.html', s);
    assert.equal(SW.pageKey('/app.html'), '/app.html');
    assert.equal(SW.pageKey('/'), '/'); assert.equal(SW.pageKey('/index.html'), '/');
    for (const p of ['/content/quran_graph.html', '/data.js', '/icons/icon-192.png', '/api/decide', '/a/b']) assert.equal(SW.pageKey(p), null, p);
  },
  'the service worker leaves audio, answers and page counts to the network'() {
    const sw = read('sw.js');
    assert.ok(/r\.headers\.has\('range'\)/.test(sw), 'audio asks in ranges and must stream');
    assert.ok(sw.includes("startsWith('/api/')") && sw.includes("startsWith('/_vercel/')"));
    assert.ok(!SW.HOSTS.some(h => /islamic|wiktionary|mymemory|everyayah/.test(h)), 'recordings and dictionaries are not kept');
    assert.ok(/^qi-\d+$/.test(SW.CACHE));
  },
  'the install buttons, the iPhone steps and the offline request are in the app'() {
    for (const s of ['instInit()', 'instGo()', 'instLater()', "postMessage('qi-offline')", 'class="sinst"', 'class="hinst"', 'class="insheet"',
      "addEventListener('beforeinstallprompt'", 'e.preventDefault(); window.__qiPrompt = e;'])
      assert.ok(APP.includes(s), s);
    assert.ok(read('sw.js').includes("e.data !== 'qi-offline'"), 'the worker answers the app\'s request');
    assert.ok(/try\{ this\.instInit\(\); \}catch\(e\)\{\}/.test(APP), 'the install checks can never stop the app from starting');
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
