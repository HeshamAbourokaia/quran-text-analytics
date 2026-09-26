// End-to-end test of /api/decide against mock-jev.js: node data-build/jev/test-endpoint.js
'use strict';
const assert = require('assert/strict');

const MOCK_PORT = 18788, SITE_PORT = 18000;
process.env.JEV_URL = `http://localhost:${MOCK_PORT}/v1/systemone`;
process.env.TYPESAFE_API_KEY = 'test-key';
delete process.env.AI_GATEWAY_API_KEY;
delete process.env.VERCEL_OIDC_TOKEN;
process.env.RATE_LIMIT_PER_MINUTE = '12';
process.env.ALLOWED_ORIGINS = 'https://heshamabourokaia.github.io';

const mock = require('./mock-jev');
const dev = require('./dev-server');
const URL_ = `http://localhost:${SITE_PORT}/api/decide`;
const ORIGIN = 'https://heshamabourokaia.github.io';
let ipCounter = 0;

async function post(body, { origin = ORIGIN, ip, headers: extra = {} } = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-Forwarded-For': ip || `10.0.0.${++ipCounter}`, ...extra };
  if (origin) headers.Origin = origin;
  const r = await fetch(URL_, { method: 'POST', headers, body: typeof body === 'string' ? body : JSON.stringify(body) });
  return { status: r.status, cors: r.headers.get('access-control-allow-origin'), json: await r.json().catch(() => null) };
}

const tests = {
  async 'preflight from the site is allowed'() {
    const r = await fetch(URL_, { method: 'OPTIONS', headers: { Origin: ORIGIN, 'Access-Control-Request-Method': 'POST' } });
    assert.equal(r.status, 204);
    assert.equal(r.headers.get('access-control-allow-origin'), ORIGIN);
  },
  async 'other origins are refused'() {
    const r = await post({ kind: 'route', text: 'read surah yusuf' }, { origin: 'https://evil.example' });
    assert.equal(r.status, 403);
    assert.equal(r.cors, null);
  },
  async 'claim: picks a candidate word and a counting method'() {
    const r = await post({ kind: 'claim', text: 'The word angel appears 88 times in the Quran',
      candidates: [{ id: 'c0', label: 'مَلَك (angel)' }, { id: 'c1', label: 'مُلْك (dominion)' }, { id: 'c2', label: 'مَلِك (king)' }] });
    assert.equal(r.status, 200);
    assert.equal(r.json.ok, true);
    assert.equal(r.json.on_topic, true);
    assert.equal(r.json.answers.word.value, 'c0');
    assert.ok(['exact_form', 'all_forms', 'whole_root', 'unspecified'].includes(r.json.answers.method.value));
    assert.ok(typeof r.json.answers.word.confidence === 'number');
    assert.equal(r.cors, ORIGIN);
  },
  async 'claim with one candidate skips the word question'() {
    const r = await post({ kind: 'claim', text: 'day appears 365 times', candidates: [{ id: 'c0', label: 'يَوْم (day)' }] });
    assert.equal(r.status, 200);
    assert.equal(r.json.answers.word, undefined);
  },
  async 'route: maps a question to a page'() {
    const r = await post({ kind: 'route', text: 'I want to read a surah verse by verse' });
    assert.equal(r.status, 200);
    assert.equal(r.json.answers.page.value, 'reader');
  },
  async 'situation: maps a feeling to a du\'a category'() {
    const r = await post({ kind: 'situation', lib: 'duas', text: 'I am afraid and I want protection from harm' });
    assert.equal(r.status, 200);
    assert.equal(r.json.answers.category.value, 'protection');
  },
  async 'off-topic text gets no answers'() {
    const r = await post({ kind: 'route', text: 'cheap sneakers best deals' });
    assert.equal(r.status, 200);
    assert.equal(r.json.on_topic, false);
    assert.equal(r.json.answers, undefined);
  },
  async 'bad input is rejected'() {
    assert.equal((await post({ kind: 'anything', text: 'x' })).status, 400);
    assert.equal((await post({ kind: 'route', text: '' })).status, 400);
    assert.equal((await post({ kind: 'route', text: 'x'.repeat(201) })).status, 400);
    assert.equal((await post({ kind: 'situation', lib: 'stories', text: 'hi' })).status, 400);
    assert.equal((await post({ kind: 'claim', text: 'x', candidates: [{ id: 'bad id!', label: 'x' }] })).status, 400);
    assert.equal((await post('not json')).status, 400);
  },
  async 'missing key is a 503'() {
    const key = process.env.TYPESAFE_API_KEY;
    delete process.env.TYPESAFE_API_KEY;
    try { assert.equal((await post({ kind: 'route', text: 'read surah yusuf' })).status, 503); }
    finally { process.env.TYPESAFE_API_KEY = key; }
  },
  'a TypeSafe key goes to TypeSafe; otherwise AI Gateway, by key or by OIDC token'() {
    const { jevAccess, TYPESAFE_URL, GATEWAY_URL } = require('../../api/_jev');
    assert.deepEqual(jevAccess({}, { TYPESAFE_API_KEY: 't', AI_GATEWAY_API_KEY: 'g' }), { url: TYPESAFE_URL, model: 'jev-latest', key: 't' });
    assert.deepEqual(jevAccess({ oidcToken: 'o' }, { AI_GATEWAY_API_KEY: 'g' }), { url: GATEWAY_URL, model: 'typesafe-ai/jev', key: 'g' });
    assert.deepEqual(jevAccess({ oidcToken: 'o' }, {}), { url: GATEWAY_URL, model: 'typesafe-ai/jev', key: 'o' });
    assert.deepEqual(jevAccess({}, { VERCEL_OIDC_TOKEN: 'o' }), { url: GATEWAY_URL, model: 'typesafe-ai/jev', key: 'o' });
    assert.equal(jevAccess({}, {}), null);
  },
  'the OIDC token only ever goes to the gateway'() {
    const { jevAccess, GATEWAY_URL } = require('../../api/_jev');
    assert.equal(jevAccess({ oidcToken: 'o' }, { JEV_URL: 'https://elsewhere.example/v1/systemone' }).url, GATEWAY_URL);
  },
  'batch answers are cached under one name whichever route asks'() {
    const { jevAccess } = require('../../api/_jev');
    const { cacheModel } = require('./run-batch');
    const keyless = cacheModel(jevAccess({}, {}), {});
    assert.equal(cacheModel(jevAccess({}, { AI_GATEWAY_API_KEY: 'g' }), {}), keyless);
    assert.equal(cacheModel(jevAccess({}, { TYPESAFE_API_KEY: 't' }), {}), keyless);
    assert.equal(cacheModel(null, { JEV_MODEL: 'jev-2026-09' }), 'jev-2026-09');
  },
  async 'without a key the endpoint asks AI Gateway with the OIDC token Vercel sends it'() {
    const saved = process.env.TYPESAFE_API_KEY, realFetch = globalThis.fetch;
    let seen = null;
    delete process.env.TYPESAFE_API_KEY;
    globalThis.fetch = (url, init) => {
      if (!String(url).startsWith('https://ai-gateway.vercel.sh/')) return realFetch(url, init);
      seen = { url: String(url), auth: init.headers.Authorization, model: JSON.parse(init.body).model };
      return realFetch(process.env.JEV_URL, init);   // the mock answers in the gateway's place
    };
    try {
      const r = await post({ kind: 'route', text: 'read surah yusuf' }, { headers: { 'x-vercel-oidc-token': 'oidc-test' } });
      assert.equal(r.status, 200);
      assert.deepEqual(seen, { url: 'https://ai-gateway.vercel.sh/typesafe/v1/systemone', auth: 'Bearer oidc-test', model: 'typesafe-ai/jev' });
    } finally { globalThis.fetch = realFetch; process.env.TYPESAFE_API_KEY = saved; }
  },
  async 'Jev failing is a 502'() {
    process.env.MOCK_FAIL = '1';
    try { assert.equal((await post({ kind: 'route', text: 'read surah yusuf' })).status, 502); }
    finally { delete process.env.MOCK_FAIL; }
  },
  async 'one visitor is rate limited'() {
    const codes = [];
    for (let i = 0; i < 14; i++) codes.push((await post({ kind: 'route', text: 'read surah yusuf' }, { ip: '10.9.9.9' })).status);
    assert.deepEqual(codes.slice(0, 12), Array(12).fill(200));
    assert.equal(codes[12], 429);
  },
};

(async () => {
  const m = await mock.start(MOCK_PORT), d = await dev.start(SITE_PORT);
  let failed = 0;
  for (const [name, fn] of Object.entries(tests)) {
    try { await fn(); console.log('PASS', name); } catch (e) { failed++; console.log('FAIL', name, '\n   ', e.message); }
  }
  m.close(); d.close();
  console.log(`\n${Object.keys(tests).length - failed}/${Object.keys(tests).length} passed`);
  process.exit(failed ? 1 : 0);
})();
