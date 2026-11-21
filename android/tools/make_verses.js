// The widget's verses (app/src/main/assets/verses.json): node android/tools/make_verses.js
// Every verse or short passage the site's Du'as and Lessons point to, short enough to read on a widget,
// with the mushaf's Arabic, Pickthall's English and the surah's names, in a fixed shuffled order.
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const WEB = path.join(__dirname, '..', '..', 'web');
const OUT = path.join(__dirname, '..', 'app', 'src', 'main', 'assets', 'verses.json');
const c = { }; c.window = c; vm.createContext(c);
const run = (f, tail = '') => vm.runInContext(fs.readFileSync(path.join(WEB, f), 'utf8') + tail, c);
run('corpus.js'); run('translation_en.js'); run('data.js');
run('content/quran_duas.js', ';this.DUAS=QURAN_DUAS;'); run('content/quran_lessons.js', ';this.LESSONS=QURAN_LESSONS;');
const AR = c.QURAN_VERSES, EN = c.QURAN_EN, META = c.QURAN_DATA.datasets.surahMeta;
const MAX_AR = 330, MAX_EN = 430, MAX_VERSES = 3;
const arDigits = n => String(n).replace(/\d/g, d => '٠١٢٣٤٥٦٧٨٩'[d]);

const seen = new Set(), out = [];
for (const item of [...c.DUAS, ...c.LESSONS]) for (const ref of item.refs || []) {
  const m = /^(\d+):(\d+)(?:-(\d+))?$/.exec(String(ref).trim()); if (!m) continue;
  const s = +m[1], a = +m[2], b = m[3] ? +m[3] : a;
  if (b < a || b - a + 1 > MAX_VERSES) continue;
  const key = s + ':' + a + (b > a ? '-' + b : ''); if (seen.has(key)) continue; seen.add(key);
  const vs = []; for (let v = a; v <= b; v++) vs.push(v);
  if (vs.some(v => !AR[s + ':' + v] || !EN[s + ':' + v])) continue;
  const ar = vs.map(v => AR[s + ':' + v] + (vs.length > 1 ? ' ﴿' + arDigits(v) + '﴾' : '')).join(' ');
  const en = vs.map(v => EN[s + ':' + v]).join(' ');
  if (ar.length > MAX_AR || en.length > MAX_EN) continue;
  const meta = META[s - 1];
  out.push({ s, a, b, ar, en, nameEn: meta.en, nameAr: meta.ar });
}
// a fixed shuffle, so the verse of a day is the same on every phone and every build
let seed = 786; const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
for (let i = out.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [out[i], out[j]] = [out[j], out[i]]; }
fs.writeFileSync(OUT, JSON.stringify(out));
console.log('verses', out.length, 'of', seen.size, 'references;', (fs.statSync(OUT).size / 1024).toFixed(0) + ' KB');
console.log(JSON.stringify(out[0]).slice(0, 300));
