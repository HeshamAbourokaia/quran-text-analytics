// Tests for the Android app (android/) against the site: node data-build/tests/test_android.js
// The site vouches for the app it names, the app opens the site's own start page, and the widget's verses are the
// mushaf's text and Pickthall's English exactly as the site has them.
'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..', '..');
const AND = path.join(ROOT, 'android'), WEB = path.join(ROOT, 'web');
const read = (...p) => fs.readFileSync(path.join(...p), 'utf8');
const LINKS = JSON.parse(read(WEB, '.well-known', 'assetlinks.json'));
const GRADLE = read(AND, 'app', 'build.gradle.kts');
const MANIFEST = read(AND, 'app', 'src', 'main', 'AndroidManifest.xml');
const STRINGS = read(AND, 'app', 'src', 'main', 'res', 'values', 'strings.xml');
const VERSES = JSON.parse(read(AND, 'app', 'src', 'main', 'assets', 'verses.json'));
const SITE = JSON.parse(read(WEB, 'manifest.webmanifest'));
const appId = GRADLE.match(/applicationId = "([^"]+)"/)[1];

const tests = {
  'the site vouches for the app it ships, by its package and key'() {
    assert.equal(LINKS.length, 1);
    const t = LINKS[0].target;
    assert.deepEqual(LINKS[0].relation, ['delegate_permission/common.handle_all_urls']);
    assert.equal(t.namespace, 'android_app');
    assert.equal(t.package_name, appId);
    assert.equal(t.sha256_cert_fingerprints.length, 1);
    assert.match(t.sha256_cert_fingerprints[0], /^([0-9A-F]{2}:){31}[0-9A-F]{2}$/, 'a SHA-256 fingerprint in capitals');
  },
  'the app opens the site\'s own start page and claims only the site'() {
    const url = MANIFEST.match(/trusted\.DEFAULT_URL" android:value="([^"]+)"/)[1];
    assert.equal(url, 'https://quraninsights.vercel.app' + SITE.start_url);
    assert.ok(STRINGS.includes('\\"site\\": \\"https://quraninsights.vercel.app\\"'), 'the app names the site back');
    assert.ok(MANIFEST.includes('android:host="quraninsights.vercel.app"'));
    const perms = [...MANIFEST.matchAll(/uses-permission android:name="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(perms, ['android.permission.INTERNET'], 'the app asks for nothing but the internet');
  },
  'the app is named as the site names itself'() {
    assert.ok(STRINGS.includes('<string name="app_name">' + SITE.name + '</string>'));
    const ar = read(AND, 'app', 'src', 'main', 'res', 'values-ar', 'strings.xml');
    assert.ok(ar.includes('<string name="app_name">' + JSON.parse(read(WEB, 'manifest-ar.webmanifest')).name + '</string>'));
  },
  'the widget\'s verses are the site\'s text, and the list is up to date'() {
    const c = {}; c.window = c; vm.createContext(c);
    vm.runInContext(read(WEB, 'corpus.js'), c); vm.runInContext(read(WEB, 'translation_en.js'), c);
    assert.ok(VERSES.length > 300, 'only ' + VERSES.length + ' verses');
    for (const v of VERSES) {
      assert.equal(v.en, Array.from({ length: v.b - v.a + 1 }, (_, i) => c.QURAN_EN[v.s + ':' + (v.a + i)]).join(' '), v.s + ':' + v.a);
      assert.ok(v.ar.startsWith(c.QURAN_VERSES[v.s + ':' + v.a]), v.s + ':' + v.a + ' Arabic');
      assert.ok(v.ar.length <= 330 && v.en.length <= 430, v.s + ':' + v.a + ' fits a widget');
    }
    const keys = VERSES.map(v => v.s + ':' + v.a + '-' + v.b);
    assert.equal(new Set(keys).size, keys.length, 'no verse twice');
    // the generator writes the same list again (run it after the site's text or library changes)
    const before = read(AND, 'app', 'src', 'main', 'assets', 'verses.json');
    require('child_process').execFileSync(process.execPath, [path.join(AND, 'tools', 'make_verses.js')], { stdio: 'ignore' });
    assert.equal(read(AND, 'app', 'src', 'main', 'assets', 'verses.json'), before, 'verses.json is out of date: run node android/tools/make_verses.js');
  },
  'the signing key never enters the repository'() {
    const ignore = read(AND, '.gitignore');
    for (const p of ['keystore.properties', '*.jks', 'local.properties']) assert.ok(ignore.includes(p), p);
  },
};

let failed = 0;
for (const [name, fn] of Object.entries(tests)) {
  try { fn(); console.log('ok   ' + name); } catch (e) { failed++; console.log('FAIL ' + name + '\n     ' + String(e.message).split('\n').join('\n     ')); }
}
console.log(failed ? `\n${failed} of ${Object.keys(tests).length} failed` : `\nall ${Object.keys(tests).length} passed`);
process.exit(failed ? 1 : 0);
