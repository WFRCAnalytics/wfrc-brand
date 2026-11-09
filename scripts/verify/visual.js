// node visual.js <oldDir> <newDir> <outDir> <page> [<page> ...]
// Loads each page from the OLD and NEW build in light and dark at 1300px and 390px and reports, per page:
// failed requests, console errors, horizontal overflow, navbar height, whether the logo/title overlap.
const { chromium } = require('playwright-core'); const fs = require('fs'), path = require('path'), http = require('http');
const [oldDir, newDir, outDir, ...pages] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.pdf': 'application/pdf' };
function serve(root) {
  return new Promise((resolve) => {
    const srv = http.createServer((q, r) => {
      let f = path.join(root, decodeURIComponent(q.url.split('?')[0])); if (!path.extname(f)) f = path.join(f, 'index.html');
      fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); } });
    }).listen(0, () => resolve(srv));
  });
}
(async () => {
  const so = await serve(oldDir), sn = await serve(newDir);
  const b = await chromium.launch({ executablePath: process.env.CHROME });
  const rows = [];
  for (const pg of pages) {
    for (const scheme of ['light', 'dark']) for (const w of [1300, 390]) {
      const res = {};
      for (const [label, srv] of [['old', so], ['new', sn]]) {
        const ctx = await b.newContext({ viewport: { width: w, height: 800 }, colorScheme: scheme, deviceScaleFactor: 1 });
        const p = await ctx.newPage(); const fails = [], errs = [];
        p.on('response', (r) => { if (r.status() >= 400 && r.url().includes('localhost')) fails.push(r.status() + ' ' + r.url().replace(/^http:\/\/localhost:\d+/, '')); });
        p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text().slice(0, 120)); });
        p.on('pageerror', (e) => errs.push('pageerror: ' + String(e).slice(0, 120)));
        await p.goto(`http://localhost:${srv.address().port}/${pg}`, { waitUntil: 'load' }).catch(() => {});
        await p.waitForTimeout(1300);
        const info = await p.evaluate(() => {
          const nb = document.querySelector('nav.navbar'); const logo = document.querySelector('.navbar-logo:not([style*="display: none"])'); const title = document.querySelector('.navbar-title');
          const lr = logo ? logo.getBoundingClientRect() : null, tr = title ? title.getBoundingClientRect() : null;
          const overlap = lr && tr && lr.width > 0 && tr.width > 0 && lr.right > tr.left + 1 && lr.left < tr.right && lr.top < tr.bottom && lr.bottom > tr.top;
          return { navH: nb ? Math.round(nb.getBoundingClientRect().height) : 0, overflowX: document.documentElement.scrollWidth - document.documentElement.clientWidth, overlap: !!overlap, title: document.title.slice(0, 40) };
        });
        const safe = pg.replace(/[^a-z0-9]+/gi, '_');
        await p.screenshot({ path: path.join(outDir, `${safe}-${scheme}-${w}-${label}.png`), clip: { x: 0, y: 0, width: w, height: 800 } });
        res[label] = { ...info, fails, errs }; await ctx.close();
      }
      rows.push({ pg, scheme, w, ...res });
    }
  }
  let bad = 0;
  for (const r of rows) {
    const flags = [];
    if (r.new.fails.length > r.old.fails.length) flags.push('NEW failed requests: ' + r.new.fails.filter((x) => !r.old.fails.includes(x)).slice(0, 3).join(', '));
    if (r.new.errs.length > r.old.errs.length) flags.push('NEW console errors: ' + r.new.errs.filter((x) => !r.old.errs.includes(x)).slice(0, 2).join(' | '));
    if (r.new.overflowX > 0 && r.new.overflowX > r.old.overflowX) flags.push(`NEW horizontal overflow ${r.new.overflowX}px (old ${r.old.overflowX}px)`);
    if (r.new.overlap) flags.push('logo overlaps title');
    if (flags.length) bad++;
    console.log(`${r.pg.padEnd(28)} ${r.scheme.padEnd(5)} ${String(r.w).padEnd(5)} navbar ${r.old.navH}->${r.new.navH}px  overflow ${r.old.overflowX}->${r.new.overflowX}  failed-req ${r.old.fails.length}->${r.new.fails.length}  console-err ${r.old.errs.length}->${r.new.errs.length}${flags.length ? '   <== ' + flags.join('; ') : ''}`);
  }
  console.log(`\n${rows.length} checks, ${bad} with a regression flag`);
  await b.close(); so.close(); sn.close();
})();
