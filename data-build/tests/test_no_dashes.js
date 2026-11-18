// The site's text carries no em dash, en dash or minus sign: node data-build/tests/test_no_dashes.js
// Ranges and negative numbers are written with a plain hyphen. Where the code must recognise a dash that a
// visitor types (2:255, then a long dash, then 257), the character is written as an escape, which this allows.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
const SIGNS = { [String.fromCharCode(0x2014)]: 'em dash', [String.fromCharCode(0x2013)]: 'en dash', [String.fromCharCode(0x2212)]: 'minus sign' };   // built from their numbers, so this file holds none either
const TEXT = /\.(?:js|html|json|css|svg|txt|webmanifest)$/i;

function files(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === 'vendor' || e.name.startsWith('.')) continue;   // other people's code is not our text
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...files(p));
    else if (TEXT.test(e.name)) out.push(p);
  }
  return out;
}

const tests = {
  'the scan sees the site'() {
    const list = files(WEB).map(p => path.relative(WEB, p));
    for (const f of ['app.html', 'index.html', 'explain.js', 'discover.js', 'sky.js', path.join('content', 'quran_stories_data.js')]) assert.ok(list.includes(f), f);
    assert.ok(list.length > 20, 'only ' + list.length + ' files');
  },
  'no file of the site holds an em dash, an en dash or a minus sign'() {
    const found = [];
    for (const p of files(WEB)) {
      const t = fs.readFileSync(p, 'utf8');
      for (const ch in SIGNS) {
        let i = t.indexOf(ch), n = 0, first = i;
        while (i >= 0) { n++; i = t.indexOf(ch, i + 1); }
        if (n) found.push(path.relative(WEB, p) + ': ' + n + ' ' + SIGNS[ch] + (n > 1 ? 's' : '') + ', the first near «' + t.slice(Math.max(0, first - 30), first + 12).replace(/\s+/g, ' ') + '»');
      }
    }
    assert.deepEqual(found, []);
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
