// Batch jobs that ask Jev for a second opinion on labels the site already has.
//
//   surahs  For every surah, Jev reads the opening verses (Arabic and English, without the name) and
//           judges Meccan or Medinan, and the main tone (mercy, guidance, hope or warning). Written to
//           web/content/jev-data.js and shown in the Classifier and Emotion views.
//   tags    For every du'a and lesson, Jev picks the category that fits. Where it differs from the tag
//           in web/content, the item is listed in data-build/reports/jev-tag-review.md for a person to
//           check. Nothing on the site changes automatically.
//
//   TYPESAFE_API_KEY=... node data-build/jev/run-batch.js              (both jobs, real Jev)
//   AI_GATEWAY_API_KEY=... node data-build/jev/run-batch.js            (the same, through Vercel's AI Gateway)
//   node data-build/jev/run-batch.js --dry-run                         (how many calls a run would make)
//   node data-build/jev/run-batch.js --jobs tags --limit 5             (a sample; written under cache/sample/)
//   node data-build/jev/run-batch.js --mock                            (mock Jev; writes under cache/, never web/)
//
// Every answer is cached in data-build/jev/cache/ (gitignored), so a re-run only pays for questions
// it hasn't asked before. Keep the key in the environment; never commit it.
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const vm = require('vm');

const ROOT = path.join(__dirname, '..', '..');
const WEB = path.join(ROOT, 'web');
const CACHE = path.join(__dirname, 'cache');

function parseArgs(argv) {
  const a = { jobs: ['surahs', 'tags'], limit: Infinity, mock: false, dryRun: false, out: null, report: null, concurrency: 4 };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i], v = () => argv[++i];
    if (k === '--jobs') a.jobs = v().split(',').map(s => s.trim()).filter(Boolean);
    else if (k === '--limit') a.limit = Math.max(1, parseInt(v(), 10) || 1);
    else if (k === '--mock') a.mock = true;
    else if (k === '--dry-run') a.dryRun = true;
    else if (k === '--out') a.out = path.resolve(v());
    else if (k === '--report') a.report = path.resolve(v());
    else if (k === '--concurrency') a.concurrency = Math.max(1, parseInt(v(), 10) || 1);
    else throw new Error(`unknown option ${k}`);
  }
  for (const j of a.jobs) if (!['surahs', 'tags'].includes(j)) throw new Error(`unknown job ${j} (use surahs, tags)`);
  // A mock run or a --limit sample never lands on the site's data or the maintainer report unless you name
  // the output yourself: a sample would replace the full results with a few surahs.
  const scratch = a.mock ? path.join(CACHE, 'mock') : a.limit !== Infinity ? path.join(CACHE, 'sample') : null;
  a.out = a.out || (scratch ? path.join(scratch, 'jev-data.js') : path.join(WEB, 'content', 'jev-data.js'));
  a.report = a.report || (scratch ? path.join(scratch, 'jev-tag-review.md') : path.join(ROOT, 'data-build', 'reports', 'jev-tag-review.md'));
  if (a.mock && (a.out.startsWith(WEB + path.sep) || a.report.startsWith(path.join(ROOT, 'data-build', 'reports')))) {
    throw new Error('mock answers are not real results: write them outside web/ and data-build/reports/');
  }
  return a;
}

// ---- inputs ----

function loadScript(file, names) {
  const ctx = { window: {} };
  vm.createContext(ctx);
  const tail = names.map(n => `window.${n} = typeof ${n} !== 'undefined' ? ${n} : window.${n};`).join('');
  vm.runInContext(fs.readFileSync(file, 'utf8') + '\n;' + tail, ctx, { filename: file });
  return ctx.window;
}

// The opening verses of each surah, up to about `maxChars` of Arabic, with their English translation.
// The surah's name is left out, so Jev judges the passage rather than recalling the label.
function surahExcerpts(maxChars = 360) {
  const ar = loadScript(path.join(WEB, 'corpus.js'), ['QURAN_VERSES']).QURAN_VERSES;
  const enWin = loadScript(path.join(WEB, 'translation_en.js'), ['QURAN_EN']);
  const en = enWin.QURAN_EN || {};
  const meta = loadScript(path.join(WEB, 'data.js'), ['QURAN_DATA']).QURAN_DATA.datasets.surahMeta;
  return meta.map(m => {
    const a = [], e = [];
    for (let v = 1; ar[`${m.n}:${v}`]; v++) {
      if (a.length && a.join(' ').length + ar[`${m.n}:${v}`].length > maxChars) break;
      a.push(ar[`${m.n}:${v}`]);
      if (en[`${m.n}:${v}`]) e.push(en[`${m.n}:${v}`]);
    }
    return { n: m.n, place: m.place === 'Medina' ? 'medinan' : 'meccan',
      state: `Opening verses of a surah of the Quran.\nArabic: ${a.join(' ۝ ')}\nEnglish: ${e.join(' ')}` };
  });
}

function libraryItems() {
  const d = loadScript(path.join(WEB, 'content', 'quran_duas.js'), ['QURAN_DUAS']).QURAN_DUAS || [];
  const l = loadScript(path.join(WEB, 'content', 'quran_lessons.js'), ['QURAN_LESSONS']).QURAN_LESSONS || [];
  const item = (lib, x) => ({ lib, id: x.id, title: x.en, cat: x.cat,
    state: [`${lib === 'duas' ? 'A prayer (du\'a) from the Quran' : 'A lesson from the Quran'}: ${x.en}`, x.desc_en, x.context_en || x.story || '']
      .filter(Boolean).join('\n').slice(0, 900) });
  return d.map(x => item('duas', x)).concat(l.map(x => item('lessons', x)));
}

// ---- asking Jev, with a cache and retries ----

// The model name answers are cached under. The gateway's typesafe-ai/jev is TypeSafe's jev-latest, so
// both routes share one entry, and a --dry-run without a key counts against the same entries.
function cacheModel(access, env = process.env) {
  const m = (access && access.model) || env.JEV_MODEL || 'jev-latest';
  return m === 'typesafe-ai/jev' ? 'jev-latest' : m;
}

function makeAsker({ mock, concurrency }) {
  const { callJev, jevAccess } = require('../../api/_jev');
  const model = cacheModel(jevAccess());
  const dir = path.join(CACHE, mock ? 'mock' : 'real');
  fs.mkdirSync(dir, { recursive: true });
  const stats = { asked: 0, cached: 0, failed: 0, tokens: 0 };
  const keyOf = (state, questions) => crypto.createHash('sha256').update(JSON.stringify({ model, state, questions })).digest('hex');
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  async function ask(state, questions, { dryRun } = {}) {
    const file = path.join(dir, keyOf(state, questions) + '.json');
    if (fs.existsSync(file)) { stats.cached++; return JSON.parse(fs.readFileSync(file, 'utf8')); }
    if (dryRun) { stats.asked++; return null; }
    for (let attempt = 0; ; attempt++) {
      try {
        const r = await callJev(state, questions, { timeoutMs: 30000 });
        stats.asked++;
        stats.tokens += (r.usage && (r.usage.input_tokens || 0) + (r.usage.output_tokens || 0)) || 0;
        fs.writeFileSync(file, JSON.stringify({ model: r.model, answers: r.answers }));
        return r;
      } catch (e) {
        const retry = !e.status || e.status === 429 || e.status >= 500;
        if (!retry || attempt >= 3) { stats.failed++; console.error(`  Jev failed (${e.status || e.name}): ${e.message}${e.detail ? ' ' + e.detail : ''}`); return null; }
        await sleep(1500 * 2 ** attempt);
      }
    }
  }
  async function each(items, fn) {
    let i = 0;
    const out = new Array(items.length);
    await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, async () => {
      while (i < items.length) { const k = i++; out[k] = await fn(items[k], k); }
    }));
    return out;
  }
  return { ask, each, stats };
}

// ---- the jobs ----

const choice = (instructions, criteria) => ({ type: 'choice', instructions, criteria });
const SURAH_QUESTIONS = {
  place: choice('Judging by its style and content, was this passage revealed in Mecca (before the migration) or in Medina (after it)?', {
    meccan: 'Meccan: revealed in Mecca, before the migration to Medina',
    medinan: 'Medinan: revealed in Medina, after the migration',
  }),
  tone: choice('Which best describes the main tone of this passage?', {
    mercy: 'mercy: God\'s compassion, forgiveness and care',
    guidance: 'guidance: instruction, law, or how to live',
    hope: 'hope: good news, reward and paradise',
    warning: 'warning: punishment, judgement and the fate of those who reject',
  }),
};

async function runSurahs(asker, args) {
  const items = surahExcerpts().slice(0, args.limit);
  const res = await asker.each(items, it => asker.ask(it.state, SURAH_QUESTIONS, { dryRun: args.dryRun }));
  if (args.dryRun) return null;
  const date = new Date().toISOString().slice(0, 10);
  let model = '';
  const revelation = [], tone = [];
  res.forEach((r, i) => {
    if (!r) return;
    model = model || r.model || '';
    const a = r.answers || {};
    if (a.place && SURAH_QUESTIONS.place.criteria[a.place.value]) revelation.push({ n: items[i].n, pred: a.place.value, confidence: round(a.place.confidence) });
    if (a.tone && SURAH_QUESTIONS.tone.criteria[a.tone.value]) tone.push({ n: items[i].n, tone: a.tone.value, confidence: round(a.tone.confidence) });
  });
  const agree = revelation.filter(x => x.pred === items.find(it => it.n === x.n).place).length;
  console.log(`surahs: ${revelation.length}/${items.length} answered; Jev agrees with the standard Meccan/Medinan label on ${agree}`);
  return { revelation: { model, date, items: revelation }, tone: { model, date, items: tone } };
}

async function runTags(asker, args) {
  const { CATEGORIES } = require('../../api/_jev');
  const all = libraryItems();
  const items = ['duas', 'lessons'].flatMap(lib => all.filter(x => x.lib === lib).slice(0, args.limit));
  const question = lib => ({ category: choice(lib === 'duas' ? 'Which kind of prayer is this?' : 'Which kind of lesson is this?', CATEGORIES[lib]) });
  const res = await asker.each(items, it => asker.ask(it.state, question(it.lib), { dryRun: args.dryRun }));
  if (args.dryRun) return null;
  let model = '';
  const rows = [];
  res.forEach((r, i) => {
    const a = r && r.answers && r.answers.category;
    if (!a || !CATEGORIES[items[i].lib][a.value]) return;
    model = model || r.model || '';
    rows.push({ ...items[i], jev: a.value, confidence: round(a.confidence) });
  });
  return { model, rows, asked: items.length };
}

function tagReport({ model, rows, asked }) {
  const date = new Date().toISOString().slice(0, 10);
  const esc = s => String(s).replace(/\|/g, '\\|').replace(/\s+/g, ' ');
  const pct = x => (x == null ? '' : Math.round(x * 100) + '%');
  const out = [
    '# Jev review of the library tags',
    '',
    `Generated by \`data-build/jev/run-batch.js --jobs tags\` on ${date} with ${model || 'Jev'}. For each du'a and lesson, Jev was asked which category fits, from the same list the site uses. This lists where its pick differs from the tag in \`web/content\`, most confident first. It is a prompt for a person to check, not a fix: nothing on the site changes from this report.`,
    '',
  ];
  for (const lib of ['duas', 'lessons']) {
    const mine = rows.filter(r => r.lib === lib);
    const differ = mine.filter(r => r.jev !== r.cat).sort((a, b) => (b.confidence || 0) - (a.confidence || 0));
    const name = lib === 'duas' ? "Du'as" : 'Lessons';
    out.push(`## ${name}: Jev agrees on ${mine.length - differ.length} of ${mine.length}`, '');
    if (!differ.length) { out.push('No disagreements.', ''); continue; }
    out.push('| id | title | tagged | Jev suggests | confidence |', '|---:|---|---|---|---:|');
    for (const r of differ) out.push(`| ${r.id} | ${esc(r.title)} | ${r.cat} | ${r.jev} | ${pct(r.confidence)} |`);
    out.push('');
  }
  if (rows.length < asked) out.push(`${asked - rows.length} items got no answer from Jev and are left out.`, '');
  return out.join('\n');
}

const round = x => (typeof x === 'number' && isFinite(x) ? Math.round(x * 1000) / 1000 : null);

function readJevData(file) {
  if (!fs.existsSync(file)) return {};
  const m = fs.readFileSync(file, 'utf8').match(/window\.QTA_JEV_DATA\s*=\s*(\{[\s\S]*\})\s*;?\s*$/);
  try { return m ? JSON.parse(m[1]) : {}; } catch (e) { return {}; }
}

function writeJevData(file, data) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, '// Written by data-build/jev/run-batch.js: Jev\'s second opinions, shown in the Classifier and Emotion views.\n'
    + 'window.QTA_JEV_DATA = ' + JSON.stringify(data) + ';\n');
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  let mockServer = null;
  if (args.mock) {
    mockServer = await require('./mock-jev').start(0);
    process.env.JEV_URL = `http://127.0.0.1:${mockServer.address().port}/v1/systemone`;
    process.env.TYPESAFE_API_KEY = process.env.TYPESAFE_API_KEY || 'mock';
  } else if (!args.dryRun && !require('../../api/_jev').jevAccess()) {
    console.error('Set TYPESAFE_API_KEY or AI_GATEWAY_API_KEY in the environment first (or use --mock / --dry-run). Never commit the key.');
    process.exit(2);
  }
  const asker = makeAsker(args);
  try {
    const data = readJevData(args.out);
    if (args.jobs.includes('surahs')) {
      const r = await runSurahs(asker, args);
      if (r) Object.assign(data, r);
    }
    if (args.jobs.includes('tags')) {
      const r = await runTags(asker, args);
      if (r) {
        fs.mkdirSync(path.dirname(args.report), { recursive: true });
        fs.writeFileSync(args.report, tagReport(r));
        console.log(`tags: ${r.rows.length}/${r.asked} answered; report in ${path.relative(ROOT, args.report)}`);
      }
    }
    const s = asker.stats;
    if (args.dryRun) {
      console.log(`dry run: ${s.asked} new Jev calls needed, ${s.cached} already cached`);
    } else {
      if (args.jobs.includes('surahs')) writeJevData(args.out, data);
      console.log(`Jev calls: ${s.asked} new, ${s.cached} from cache, ${s.failed} failed${s.tokens ? `, ${s.tokens} tokens` : ''}`);
      if (args.jobs.includes('surahs')) console.log(`wrote ${path.relative(ROOT, args.out)}`);
      if (args.limit !== Infinity && !args.mock) console.log('note: --limit was used, so these results cover only part of the Quran and library');
    }
  } finally {
    if (mockServer) mockServer.close();
  }
}

if (require.main === module) main().catch(e => { console.error(e.message || e); process.exit(1); });
module.exports = { parseArgs, surahExcerpts, libraryItems, tagReport, readJevData, SURAH_QUESTIONS, cacheModel };
