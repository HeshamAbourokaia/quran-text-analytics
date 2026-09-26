// Site configuration.
// jevEndpoint: URL of the /api/decide function (see "Jev features" in the README). Pages served by the
// Vercel project (its domains and previews) call their own function; the GitHub Pages copy calls the
// production one. Anywhere else (a local static server, the desktop app) it stays empty, and every
// feature falls back to plain matching in the browser; nothing is sent anywhere.
(function () {
  const host = location.hostname;
  window.QTA_CONFIG = {
    jevEndpoint: host.endsWith('.vercel.app') ? '/api/decide'
      : host.endsWith('.github.io') ? 'https://quran-text-analytics.vercel.app/api/decide'
      : '',
  };
})();
