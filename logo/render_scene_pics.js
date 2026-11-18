// Rendert logo/scene_pics.html (Profilbilder aus der Video-Welt) nach out/logo/qissah-szene-N.png: node logo/render_scene_pics.js
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const out = path.resolve(__dirname, "..", "out", "logo");
  const b = await chromium.launch({ args: ["--allow-file-access-from-files"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
  await p.goto("file://" + path.join(__dirname, "scene_pics.html"));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(500);
  for (const id of await p.$$eval(".logo", (e) => e.map((x) => x.id)))
    await (await p.$("#" + id)).screenshot({ path: path.join(out, `qissah-szene-${id.slice(1)}.png`) });
  await b.close();
  console.log("✓ Szenen-Profilbilder in", out);
})();
