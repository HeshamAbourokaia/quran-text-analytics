// Minimal static file server for the offline Electron shell.
// Serving over http (rather than file://) lets the app's fetch() of data files
// (mushaf.json, alifi manifest) work without disabling web security.
const http = require('http');
const fs = require('fs');
const path = require('path');

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.gif': 'image/gif',
  '.woff': 'font/woff', '.woff2': 'font/woff2', '.ttf': 'font/ttf',
  '.icns': 'image/icns', '.ico': 'image/x-icon',
};

function createStaticServer(root) {
  root = path.resolve(root);
  return http.createServer((req, res) => {
    try {
      let urlPath = decodeURIComponent(req.url.split('?')[0]);
      if (urlPath === '/') urlPath = '/app.html';
      // prevent path traversal
      const safe = path.normalize(urlPath).replace(/^(\.\.[/\\])+/, '');
      const filePath = path.join(root, safe);
      if (filePath !== root && !filePath.startsWith(root + path.sep)) {
        res.writeHead(403); res.end('forbidden'); return;
      }
      fs.readFile(filePath, (err, data) => {
        if (err) { res.writeHead(404); res.end('not found'); return; }
        const ext = path.extname(filePath).toLowerCase();
        res.writeHead(200, { 'Content-Type': TYPES[ext] || 'application/octet-stream' });
        res.end(data);
      });
    } catch (e) {
      res.writeHead(500); res.end('error');
    }
  });
}

module.exports = { createStaticServer };
