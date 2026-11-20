// Quran Insights as an app: the service worker that lets the installed site open and read without internet.
// Every page and file still comes from the network whenever there is one, so a new version is never hidden
// behind an old copy; the copies kept here answer only when the network does not.
'use strict';
const CACHE = 'qi-1';   // change only when what is kept, or how, changes; a deploy alone needs nothing here

// What the app needs to start: its two pages, the scripts app.html loads before it shows anything, and the icons.
const SHELL = ['/app.html', '/', '/manifest.webmanifest', '/manifest-ar.webmanifest', '/favicon.svg',
  '/icons/icon-192.png', '/icons/maskable-192.png',
  '/vendor/vue.global.prod.js', '/data.js', '/sky.js', '/config.js', '/jev-client.js', '/lookup.js', '/translit.js',
  '/study.js', '/spelling.js', '/place.js', '/card.js', '/recite.js', '/content/jev-data.js', '/content/quran_stories_data.js',
  '/content/quran_lessons.js', '/content/quran_duas.js', '/content/quran_tafsir_insights.js', '/content/quran_untranslatable.js',
  '/content/quran_history.js', '/content/v1_data.js', '/explain.js'];
// The text, translation and word index the pages load once they are on screen (LAZY in app.html). An installed
// app keeps them all, so the whole mushaf, its translation and the word counts read offline.
const READING = ['/corpus.js', '/translation_en.js', '/archaic.js', '/words.js', '/lemma-variants.js', '/roman.js',
  '/discover.js', '/discoveries.js', '/content/quran_history_viz.js', '/phrases.js'];
// Other sites whose files never change at the same address (the fonts, GSAP, the chart library): kept as they are used.
const HOSTS = ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net', 'cdn.plot.ly'];
const WAIT = 4000;   // how long a page waits for the network before the kept copy opens instead

// Every short link (/reader, /19 ...) is app.html, so one kept copy serves them all; the home page is its own.
function pageKey(path) {
  if (path === '/' || path === '/index.html') return '/';
  if (path === '/app.html' || /^\/[a-z0-9-]+$/.test(path)) return '/app.html';   // one word, no file ending: a short link
  return null;
}

const keep = (c, url) => fetch(url).then(r => { if (r.ok) return c.put(url, r); }).catch(() => {});

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => keep(c, u)))).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('qi-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// The installed app asks for the reading files once it is open, so the next time it can open offline.
self.addEventListener('message', e => {
  if (e.data !== 'qi-offline') return;
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(READING.map(u => c.match(u).then(k => k || keep(c, u))))));
});

// Fetch from the network and keep a copy under key; the copy is written before the worker may stop.
function fromNet(e, key, ok) {
  let put = Promise.resolve();
  const net = fetch(e.request).then(r => {
    if (ok(r)) { const copy = r.clone(); put = caches.open(CACHE).then(c => c.put(key, copy)).catch(() => {}); }
    return r;
  });
  e.waitUntil(net.then(() => put, () => null));
  return net;
}

// A page: the network first; the kept copy when there is no network, or after WAIT without an answer.
function page(e, key) {
  const net = fromNet(e, key, r => r.ok && r.type === 'basic');
  const kept = () => caches.match(key).then(k => k || (key === '/' ? caches.match('/app.html') : undefined));
  return new Promise(done => {
    let over = false;
    const end = r => { if (!over && r) { over = true; clearTimeout(t); done(r); } };
    const t = setTimeout(() => kept().then(end), WAIT);
    net.then(end, () => kept().then(k => end(k || Response.error())));
  });
}

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || r.headers.has('range')) return;   // audio asks in ranges; it streams as before
  const u = new URL(r.url);
  if (u.origin === self.location.origin) {
    if (u.pathname.startsWith('/api/') || u.pathname.startsWith('/_vercel/')) return;   // answers and page counts are never kept
    const key = r.mode === 'navigate' && r.destination === 'document' ? pageKey(u.pathname) : null;
    if (key) { e.respondWith(page(e, key)); return; }
    // any other file of the site: the network first, the kept copy offline
    e.respondWith(fromNet(e, r, x => x.ok && x.type === 'basic')
      .catch(() => caches.match(r).then(k => k || Response.error())));
    return;
  }
  if (HOSTS.includes(u.hostname)) {
    // fonts and libraries: the kept copy at once when there is one, refreshed behind it
    const net = fromNet(e, r, x => x.ok || x.type === 'opaque');
    e.respondWith(caches.match(r).then(k => k || net));
  }
});

if (typeof module === 'object' && module.exports) module.exports = { SHELL, READING, HOSTS, pageKey, CACHE };
