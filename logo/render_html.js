// Rendert jede .logo-Fläche einer HTML-Datei als PNG (1080×1080): node logo/render_html.js <datei.html> <name>
// -> out/logo/<name>-<n>.png (n = Ziffern aus der id)
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const [html, name] = process.argv.slice(2);
  const out = path.resolve(__dirname, "..", "out", "logo");
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto("file://" + path.resolve(html));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(400);
  const ids = await p.$$eval(".logo", (e) => e.map((x) => x.id));
  for (const id of ids) await (await p.$("#" + id)).screenshot({ path: path.join(out, `${name}-${id.replace(/\D/g, "")}.png`) });
  await b.close();
  console.log("✓", ids.length, "Bilder ->", out);
})();
