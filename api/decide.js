// POST /api/decide: the site's only door to Jev. It holds the TypeSafe key server-side and will only
// ask the fixed questions defined in _jev.js (claim, route, situation), so the key can't be used as a
// general-purpose classifier. Deploy on Vercel with TYPESAFE_API_KEY set; see "Jev features" in the README.
'use strict';

const { callJev, buildRequest } = require('./_jev');

const ALLOWED = (process.env.ALLOWED_ORIGINS || 'https://heshamabourokaia.github.io')
  .split(',').map(s => s.trim()).filter(Boolean);
const PER_MINUTE = Number(process.env.RATE_LIMIT_PER_MINUTE || 30);
const OFF_TOPIC_BELOW = 0.35;   // probability of "on topic" under which we answer nothing else

// Best-effort, per instance: serverless instances don't share memory, so treat this as a speed bump
// and set a spend limit on the TypeSafe account as the real cap.
const hits = new Map();
function limited(ip, now = Date.now()) {
  const h = hits.get(ip);
  if (!h || now > h.reset) { hits.set(ip, { n: 1, reset: now + 60000 }); return false; }
  h.n += 1;
  if (hits.size > 5000) for (const [k, v] of hits) if (now > v.reset) hits.delete(k);
  return h.n > PER_MINUTE;
}

function send(res, status, obj) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.setHeader('Cache-Control', 'no-store');
  res.end(JSON.stringify(obj));
}

function originAllowed(origin, host) {
  if (!origin) return true;                                   // same-origin or server-to-server
  if (ALLOWED.includes(origin)) return true;
  return !!host && (origin === `https://${host}` || origin === `http://${host}`);
}

module.exports = async function handler(req, res) {
  const origin = req.headers.origin || '';
  const allowed = originAllowed(origin, req.headers.host);
  if (origin && allowed) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Vary', 'Origin');
  }
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Access-Control-Max-Age', '86400');
    res.statusCode = allowed ? 204 : 403;
    return res.end();
  }
  if (req.method !== 'POST') return send(res, 405, { ok: false, error: 'use POST' });
  if (!allowed) return send(res, 403, { ok: false, error: 'origin not allowed' });

  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || (req.socket && req.socket.remoteAddress) || '?';
  if (limited(ip)) return send(res, 429, { ok: false, error: 'too many requests, try again in a minute' });

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
  const built = buildRequest(body);
  if (built.error) return send(res, 400, { ok: false, error: built.error });

  try {
    const { answers, model } = await callJev(built.state, built.questions);
    const topic = answers.on_topic;
    if (topic && topic.probability < OFF_TOPIC_BELOW) return send(res, 200, { ok: true, kind: built.kind, on_topic: false, model });
    delete answers.on_topic;
    return send(res, 200, { ok: true, kind: built.kind, on_topic: true, answers, model });
  } catch (e) {
    const status = e.status === 503 ? 503 : 502;
    console.error('jev error', e.status || '', e.message, e.detail || '');
    return send(res, status, { ok: false, error: status === 503 ? 'Jev is not configured' : 'Jev is unavailable right now' });
  }
};
