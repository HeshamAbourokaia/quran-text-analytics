// A stand-in for Jev's POST /v1/systemone, for testing the endpoint and the batch jobs without a key.
// It checks the request has the documented shape and answers with crude keyword overlap, marked as
// model "jev-mock". Never use its output as real results.
//
//   node data-build/jev/mock-jev.js [port]        (default 8788; MOCK_FAIL=1 makes every call fail)
'use strict';
const http = require('http');

const words = s => (String(s).toLowerCase().match(/[\p{L}\p{N}]+/gu) || []);

function answerChoice(state, criteria) {
  const have = new Set(words(state));
  const keys = Object.keys(criteria);
  const scores = keys.map(k => words(`${k.replace(/_/g, ' ')} ${criteria[k]}`).filter(w => w.length > 2 && have.has(w)).length);
  const exp = scores.map(s => Math.exp(2 * s));
  const total = exp.reduce((a, b) => a + b, 0);
  const probabilities = Object.fromEntries(keys.map((k, i) => [k, +(exp[i] / total).toFixed(4)]));
  const best = keys[scores.indexOf(Math.max(...scores))];
  const pmax = probabilities[best], n = keys.length;
  return { choice: best, probabilities, confidence: +Math.max(0, (pmax - 1 / n) / (1 - 1 / n)).toFixed(4) };
}

function answerYesNo(state) {
  const text = String(state).toLowerCase();
  const onTopic = /[؀-ۿ]|\d|quran|verse|surah|word|times|prayer|dua|allah|god|prophet|story|lesson|afraid|worried|sad|forgive|help|family|parents|job|money/.test(text);
  const p = onTopic ? 0.92 : 0.12;
  return { probability: p, confidence: +(Math.abs(p - 0.5) * 2).toFixed(4) };
}

function handle(body) {
  const answers = {};
  for (const [key, q] of Object.entries(body.questions)) {
    answers[key] = q.type === 'noul' ? answerYesNo(body.state) : answerChoice(body.state, q.criteria);
  }
  return { model: 'jev-mock', answers, usage: { input_tokens: words(body.state).length, output_tokens: 0 } };
}

function validate(req, body) {
  if (req.method !== 'POST' || req.url !== '/v1/systemone') return 'expected POST /v1/systemone';
  if (!/^Bearer \S+/.test(req.headers.authorization || '')) return 'missing bearer token';
  if (!body || typeof body.state !== 'string' || !body.state) return 'state is required';
  if (typeof body.model !== 'string') return 'model is required';
  if (!body.questions || typeof body.questions !== 'object') return 'questions is required';
  for (const [k, q] of Object.entries(body.questions)) {
    if (!['noul', 'choice', 'score'].includes(q.type)) return `question ${k}: bad type`;
    if (!q.criteria || typeof q.criteria !== 'object' || !Object.keys(q.criteria).length) return `question ${k}: criteria required`;
    if (q.type === 'noul' && !('true' in q.criteria && 'false' in q.criteria)) return `question ${k}: yes/no needs true and false`;
  }
  return null;
}

function start(port = 8788) {
  const server = http.createServer((req, res) => {
    let raw = '';
    req.on('data', c => { raw += c; });
    req.on('end', () => {
      let body = null;
      try { body = JSON.parse(raw); } catch (e) { /* reported below */ }
      const problem = validate(req, body);
      const reply = (status, obj) => { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); };
      if (process.env.MOCK_FAIL) return reply(500, { error: 'mock failure' });
      if (problem) return reply(400, { error: problem });
      reply(200, handle(body));
    });
  });
  return new Promise(resolve => server.listen(port, () => resolve(server)));
}

if (require.main === module) {
  const port = Number(process.argv[2] || 8788);
  start(port).then(() => console.log(`mock Jev listening on http://localhost:${port}/v1/systemone`));
}
module.exports = { start };
