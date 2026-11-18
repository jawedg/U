// Vorschau wie bei TikTok (rund, groß + klein): node logo/preview.js <ausgabe.png> <bild1.png> <bild2.png> …
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");
(async () => {
  const [outFile, ...imgs] = process.argv.slice(2);
  const src = imgs.map((f) => "file://" + path.resolve(f));
  const cell = (s, i) => `<div style="text-align:center">
      <img src="${s}" style="width:330px;height:330px;border-radius:50%;display:block">
      <div style="display:flex;gap:14px;align-items:center;justify-content:center;margin-top:18px">
        <img src="${s}" style="width:96px;height:96px;border-radius:50%"><img src="${s}" style="width:48px;height:48px;border-radius:50%">
        <img src="${s}" style="width:32px;height:32px;border-radius:50%"></div>
      <div style="font:700 32px sans-serif;margin-top:12px">${String.fromCharCode(65 + i)}</div></div>`;
  const html = `<html><body style="margin:0;background:#fff"><div style="display:flex;gap:34px;padding:36px">${src.map(cell).join("")}</div></body></html>`;
  const tmp = path.resolve(path.dirname(outFile), "_preview.html");
  fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 36 + imgs.length * 364, height: 560 } });
  await p.goto("file://" + tmp);
  await p.waitForTimeout(400);
  await p.screenshot({ path: outFile, fullPage: true });
  await b.close();
  fs.unlinkSync(tmp);
  console.log("✓", outFile);
})();
