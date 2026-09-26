// Tests for web/jev-client.js against the real corpus files: node data-build/jev/test-client.js
'use strict';
const assert = require('assert/strict');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
global.window = globalThis;
require(path.join(WEB, 'words.js'));
require(path.join(WEB, 'lemma-variants.js'));
require(path.join(WEB, 'data.js'));
const J = require(path.join(WEB, 'jev-client.js'));

const ix = J.makeIndex(window.QURAN_WORDS, window.QURAN_LEMMA_VARIANTS, window.QURAN_FORM_SENSES);
const D = window.QURAN_DATA, META = D.datasets.surahMeta;
const first = (text) => { const p = J.parseClaim(ix, text); return { p, w: p.words[0], c: p.words[0] && J.countOption(ix, p.words[0].options[p.words[0].pick], p.words[0].form) }; };

const tests = {
  'every English word points at a lemma that exists, and at a real sense of it'() {
    for (const [en, opts] of Object.entries(J.GLOSS)) for (const o of opts) {
      assert.ok(ix.lemmaCount.get(o.norm) > 0, `${en}: no lemma ${o.norm}`);
      if (o.sense) assert.ok((ix.VAR[o.norm] || []).some(v => J.canon(v[0]) === J.canon(o.sense)), `${en}: ${o.norm} has no sense ${o.sense}`);
    }
    for (const [pl, sg] of Object.entries(J.PLURAL)) assert.ok(J.GLOSS[sg], `plural ${pl} -> missing ${sg}`);
  },
  'every labelled sense exists in the homograph table'() {
    const all = new Set(Object.values(ix.VAR).flat().map(v => J.canon(v[0])));
    for (const s of Object.keys(J.SENSES)) assert.ok(all.has(J.canon(s)), `unknown sense ${s}`);
  },
  'the twelve audited claims reproduce their verified counts'() {
    for (const c of D.claims) {
      const { p, c: counts } = first(`The word ${c.en.replace(/\(.*\)/, '')} appears ${c.claimed} times`);
      assert.deepEqual(p.numbers, [c.claimed], c.id);
      assert.equal(counts.lemma, c.verifiedLemma, `${c.id}: ${counts.lemma} vs ${c.verifiedLemma}`);
    }
  },
  'an English claim picks the right sense of a shared spelling'() {
    const { w, c } = first('The word angel appears 88 times in the Quran');
    assert.equal(w.options.length, 1);
    assert.equal(J.canon(w.options[0].sense), J.canon('مَلَك'));
    assert.equal(c.lemma, 88);
    assert.equal(c.formText, 'ملك');
    assert.equal(c.form, 65);
    assert.equal(c.formOthers, 55, 'only 10 of the 65 words written ملك are angel (checked against the corpus)');
    assert.deepEqual(J.judge(c, 88).exact.includes('lemma'), true);
  },
  'English words are counted as the mushaf writes them'() {
    const devil = first('devils appear 88 times').c;
    assert.deepEqual([devil.formText, devil.form, devil.formOthers], ['شيطن', 68, 0]);
    const life = first('life appears 145 times').c;
    assert.equal(life.formText, 'حيوة');
    // The famous 115 for the hereafter holds only for the written form الآخرة, not for the lemma.
    const p = J.parseClaim(ix, 'The world and the hereafter both appear 115 times');
    const [dunya, akhira] = p.words.map(w => J.countOption(ix, w.options[w.pick], w.form));
    assert.deepEqual([dunya.form, dunya.lemma], [115, 115]);
    assert.deepEqual([akhira.formText, akhira.form, akhira.formOthers, akhira.lemma], ['ءاخرة', 115, 0, 155]);
    assert.equal(J.citationForm(ix, 'عقل'), null, 'the noun never occurs, only the verb');
  },
  'an Arabic claim finds the lemma from the written form, and only the senses that form has'() {
    const { p, w, c } = first('كلمة الملائكة وردت ٨٨ مرة');
    assert.deepEqual(p.numbers, [88]);
    assert.equal(w.options.length, 1, 'الملائكة is only ever angels');
    assert.equal(J.canon(w.options[0].sense), J.canon('مَلَك'));
    assert.equal(c.lemma, 88);
    assert.equal(w.form, 'ملئكة', 'the mushaf spelling of the form');
    assert.equal(w.respelled, true);
    const k = first('الملك ٤٨').w;
    assert.deepEqual(k.options.map(o => J.canon(o.sense)), [J.canon('مُلْك'), J.canon('مَلِك')], 'الملك is dominion or king, never angel');
    const life = first('الحياة ١٤٥').w;
    assert.deepEqual([life.form, life.respelled], ['حيوة', true], 'a dictionary spelling is counted as the mushaf writes it');
    const death = first('والموت ١٤٥').w;
    assert.equal(death.respelled, false, 'dropping a clitic is not a spelling difference');
  },
  'word pairs give two words and one number'() {
    const p = J.parseClaim(ix, 'Life and death are each mentioned 145 times');
    assert.deepEqual(p.words.map(w => w.options[0].norm), ['حياة', 'موت']);
    assert.deepEqual(p.numbers, [145]);
    const q = J.parseClaim(ix, 'الدنيا والآخرة ذكرتا ١١٥ مرة');
    assert.deepEqual(q.words.map(w => w.options[0].norm), ['دنيا', 'اخر']);
    assert.deepEqual(q.numbers, [115]);
  },
  'plurals and possessives are understood'() {
    assert.equal(first("The angels' count is 88").w.options[0].norm, 'ملك');
    assert.equal(first('devils appear 88 times').w.options[0].norm, 'شيطان');
  },
  'modern spellings find the mushaf spelling'() {
    assert.equal(first('الحياة ١٤٥ مرة').w.options[0].norm, 'حياة');
    assert.equal(first('الصلاة 99').w.options[0].norm, 'صلاة');
    assert.equal(first('الشيطان ٨٨').w.options[0].norm, 'شيطان');
    assert.deepEqual(J.mushafSpelling(ix, 'الملائكة'), ['الملئكة']);
    assert.equal(J.mushafSpelling(ix, 'الملئكة'), null);
  },
  'text with no known word finds nothing'() {
    const p = J.parseClaim(ix, 'hello there 12');
    assert.equal(p.words.length, 0);
    assert.deepEqual(p.numbers, [12]);
  },
  'judge names the methods that match and the nearest miss'() {
    const j = J.judge({ form: 70, lemma: 475, rootCount: 480 }, 365);
    assert.deepEqual(j.exact, []);
    assert.equal(j.nearest.method, 'lemma');
    assert.equal(j.nearest.diff, 110);
  },
  'search mode counts match the search box'() {
    const m = J.modeCounts(ix, 'ملك');
    assert.equal(m.lemma, 152);
    assert.equal(m.root, 206);
    assert.equal(m.surface, window.QURAN_WORDS.norm.filter(x => x.includes('ملك')).length);
  },
  'routing: surahs, claims and single words go straight to the right page'() {
    assert.deepEqual(J.routeLocal('surah yusuf', ix, META).shortcut, { view: 'reader', s: 12 });
    assert.deepEqual(J.routeLocal('read al-baqarah', ix, META).shortcut, { view: 'reader', s: 2 });
    assert.deepEqual(J.routeLocal('سورة الكهف', ix, META).shortcut, { view: 'reader', s: 18 });
    assert.deepEqual(J.routeLocal('surah 36', ix, META).shortcut, { view: 'reader', s: 36 });
    assert.equal(J.routeLocal('The word day appears 365 times', ix, META).shortcut.view, 'auditor');
    assert.deepEqual(J.routeLocal('رحمة', ix, META).shortcut, { view: 'search', q: 'رحمة' });
    assert.equal(J.routeLocal('the story of yusuf and his brothers', ix, META).shortcut, null);
  },
  'routing: keywords rank the pages'() {
    const top = t => (J.routeLocal(t, ix, META).ranked[0] || {}).view;
    assert.equal(top("a du'a for anxiety"), 'duas');
    assert.equal(top('how many verses are in the quran'), 'overview');
    assert.equal(top('the story of moses and pharaoh'), 'stories');
    assert.equal(top('help me plan to memorize the quran'), 'hifz');
    assert.equal(top('is it just chance that the numbers match'), 'coincidence');
    assert.equal(top('which surahs are meccan'), 'mecca');
    assert.equal(top('أريد قصة نوح'), 'stories');
    assert.equal(top('what did the scholars say, tafsir'), 'tafsir');
    assert.equal(J.routeLocal('said again and again', ix, META).ranked.some(r => r.view === 'classifier'), false);
    assert.equal(top('what do we know about moses'), 'stories', 'an ordinary "we" is not a question about pronouns');
    assert.equal(top('why does god say we in the quran'), 'pronouns');
  },
  'situations map to du\'a and lesson categories'() {
    const top = (t, lib) => (J.situationLocal(t, lib)[0] || {}).cat;
    assert.equal(top("I'm so anxious about tomorrow", 'duas'), 'protection');
    assert.equal(top('I made a big mistake and feel guilty', 'duas'), 'forgiveness');
    assert.equal(top('I lost my job and I have debts', 'duas'), 'provision');
    assert.equal(top('أشعر بالخوف والقلق', 'duas'), 'protection');
    assert.equal(top('I feel so sad and alone', 'duas'), 'prophet');
    assert.equal(top('My parents and I keep arguing', 'lessons'), 'family');
    assert.equal(top('I get angry very fast', 'lessons'), 'character');
    assert.equal(top('I have exams next week', 'lessons'), 'knowledge');
    assert.equal(J.situationLocal('the weather is nice', 'duas').length, 0);
    assert.deepEqual(J.situationLocal('المدرسة', 'duas'), [], 'short Arabic keys must not match inside longer words');
    assert.equal(top('امي مريضة', 'lessons'), 'family');
    assert.equal(J.situationLocal('هل اسافر ام ابقى', 'lessons').some(r => r.cat === 'family'), false, 'أم (or) is not a mother');
  },
  'crisis wording is recognised in both languages, everyday wording is not'() {
    for (const t of ['I want to kill myself', 'thinking about suicide', "I don't want to live anymore", 'I keep hurting myself', 'أريد أن أموت', 'افكر في الانتحار'])
      assert.equal(J.crisis(t), true, t);
    assert.equal(J.crisis('I want to end my life'), true);
    for (const t of ['this exam is killing me', 'the story of the death of Musa', 'I want to die my hair', 'أخاف من الموت', 'I want to end my contract'])
      assert.equal(J.crisis(t), false, t);
  },
  'Jev overrides plain matching only when it agrees, is sure, or plain matching found nothing'() {
    assert.equal(J.trust({ value: 'duas', confidence: 0.1 }, 'duas'), true);
    assert.equal(J.trust({ value: 'auditor', confidence: 0.1 }, 'duas'), false);
    assert.equal(J.trust({ value: 'auditor', confidence: 0.8 }, 'duas'), true);
    assert.equal(J.trust({ value: 'auditor', confidence: 0.1 }, null), true);
    assert.equal(J.trust(null, 'duas'), false);
  },
  async 'decide() stays silent until an endpoint is configured, then posts to it'() {
    window.QTA_CONFIG = { jevEndpoint: '' };
    assert.equal(await J.decide({ kind: 'route', text: 'x' }), null);
    window.QTA_CONFIG = { jevEndpoint: 'https://example.test/api/decide' };
    let seen = null;
    const fake = async (url, init) => { seen = { url, body: JSON.parse(init.body) }; return { ok: true, status: 200, json: async () => ({ ok: true, kind: 'route', on_topic: true, answers: { page: { value: 'reader', confidence: 0.9 } } }) }; };
    const r = await J.decide({ kind: 'route', text: 'read surah yusuf' }, { fetchImpl: fake });
    assert.equal(seen.url, 'https://example.test/api/decide');
    assert.equal(seen.body.kind, 'route');
    assert.equal(r.answers.page.value, 'reader');
    const down = async () => ({ ok: false, status: 502, json: async () => ({ ok: false, error: 'Jev is unavailable right now' }) });
    assert.deepEqual(await J.decide({ kind: 'route', text: 'x' }, { fetchImpl: down }), { ok: false, status: 502, error: 'Jev is unavailable right now' });
    const offline = async () => { throw new TypeError('Failed to fetch'); };
    assert.deepEqual(await J.decide({ kind: 'route', text: 'x' }, { fetchImpl: offline }), { ok: false, error: 'network' });
    window.QTA_CONFIG = { jevEndpoint: '' };
  },
};

(async () => {
  let failed = 0;
  for (const [name, fn] of Object.entries(tests)) {
    try { await fn(); console.log('PASS', name); } catch (e) { failed++; console.log('FAIL', name, '\n   ', e.message); }
  }
  console.log(`\n${Object.keys(tests).length - failed}/${Object.keys(tests).length} passed`);
  process.exit(failed ? 1 : 0);
})();
