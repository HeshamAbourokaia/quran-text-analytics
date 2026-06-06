// Electron shell: serves the web/ build over a local http port and loads it.
// Same single source (web/app.html) runs as the website and as this desktop app.
const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { createStaticServer } = require('./server');

let win = null;
let server = null;

function webRoot() {
  // packaged: web/ is shipped as an extraResource; dev: sibling web/ dir
  return app.isPackaged
    ? path.join(process.resourcesPath, 'web')
    : path.join(__dirname, '..', 'web');
}

function createWindow(port) {
  win = new BrowserWindow({
    width: 1440, height: 920, minWidth: 1000, minHeight: 640,
    backgroundColor: '#0f3b2e',
    title: 'Quran Text Analytics',
    webPreferences: { contextIsolation: true, nodeIntegration: false },
  });
  win.loadURL(`http://127.0.0.1:${port}/app.html`);
  // open external links in the system browser, not inside the app
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://127.0.0.1')) return { action: 'allow' };
    shell.openExternal(url); return { action: 'deny' };
  });
  win.on('closed', () => { win = null; });
}

app.whenReady().then(() => {
  server = createStaticServer(webRoot());
  server.listen(0, '127.0.0.1', () => {
    createWindow(server.address().port);
  });
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0 && server) createWindow(server.address().port);
  });
});

app.on('window-all-closed', () => {
  if (server) server.close();
  if (process.platform !== 'darwin') app.quit();
});
