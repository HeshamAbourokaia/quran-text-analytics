// Run the site and the /api/decide function together on one local port, the way Vercel serves them.
//
//   TYPESAFE_API_KEY=... node data-build/jev/dev-server.js [port]            (real Jev)
//   JEV_URL=http://localhost:8788/v1/systemone TYPESAFE_API_KEY=test \
//     node data-build/jev/dev-server.js                                       (with mock-jev.js)
//
// config.js is served with jevEndpoint pointing at this server, so the Jev features switch on.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');

const WEB = path.join(__dirname, '..', '..', 'web');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json',
  '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.webp': 'image/webp' };

function start(port = 8000) {
  const handler = require('../../api/decide');
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host}`);
    if (url.pathname === '/api/decide') {
      let raw = '';
      req.on('data', c => { raw += c; if (raw.length > 20000) req.destroy(); });
      req.on('end', () => {
        try { req.body = raw ? JSON.parse(raw) : null; } catch (e) { req.body = null; }
        Promise.resolve(handler(req, res)).catch(e => { res.statusCode = 500; res.end(String(e)); });
      });
      return;
    }
    if (url.pathname === '/config.js') {
      res.writeHead(200, { 'Content-Type': TYPES['.js'] });
      return res.end("window.QTA_CONFIG = { jevEndpoint: '/api/decide' };\n");
    }
    const file = path.normalize(path.join(WEB, decodeURIComponent(url.pathname === '/' ? '/index.html' : url.pathname)));
    if (!file.startsWith(WEB) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.statusCode = 404; return res.end('not found'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  return new Promise(resolve => server.listen(port, () => resolve(server)));
}

if (require.main === module) {
  const port = Number(process.argv[2] || 8000);
  start(port).then(() => console.log(`site + /api/decide on http://localhost:${port}/app.html`));
}
module.exports = { start };
