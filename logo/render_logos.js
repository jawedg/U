// Rendert die Logo-Entwürfe aus logo/qissah_logos.html als PNG (1080×1080) nach out/logo/
// + Vorschau, wie TikTok sie zeigt (rund, groß und klein): node logo/render_logos.js
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

(async () => {
  const root = path.resolve(__dirname, "..");
  const out = path.join(root, "out", "logo");
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.join(__dirname, "qissah_logos.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const ids = await page.$$eval(".logo", (els) => els.map((e) => e.id));
  for (const id of ids) {
    await (await page.$("#" + id)).screenshot({ path: path.join(out, `qissah-logo-${id.slice(1)}.png`) });
  }
  // Vorschau: jede Variante rund (wie im Profil) und klein (wie neben Kommentaren)
  const imgs = ids.map((id) => "file://" + path.join(out, `qissah-logo-${id.slice(1)}.png`));
  const html = `<html><body style="margin:0;background:#fff;font-family:sans-serif">
    <div style="display:flex;gap:40px;padding:40px;background:#fff">
    ${imgs.map((src, i) => `<div style="text-align:center">
        <img src="${src}" style="width:380px;height:380px;border-radius:50%;display:block">
        <div style="display:flex;gap:16px;align-items:center;justify-content:center;margin-top:20px">
          <img src="${src}" style="width:96px;height:96px;border-radius:50%">
          <img src="${src}" style="width:48px;height:48px;border-radius:50%">
          <img src="${src}" style="width:32px;height:32px;border-radius:50%">
        </div>
        <div style="font-size:34px;font-weight:700;margin-top:14px">${i + 1}</div></div>`).join("")}
    </div>
    <div style="display:flex;gap:40px;padding:40px;background:#121212">
    ${imgs.map((src) => `<div style="width:380px;display:flex;gap:16px;align-items:center;justify-content:center">
          <img src="${src}" style="width:96px;height:96px;border-radius:50%">
          <img src="${src}" style="width:48px;height:48px;border-radius:50%">
          <img src="${src}" style="width:32px;height:32px;border-radius:50%"></div>`).join("")}
    </div></body></html>`;
  const prev = path.join(out, "_vorschau.html");
  fs.writeFileSync(prev, html);
  const p2 = await browser.newPage({ viewport: { width: 1740, height: 760 }, deviceScaleFactor: 1 });
  await p2.goto("file://" + prev);
  await p2.waitForTimeout(300);
  await p2.screenshot({ path: path.join(out, "qissah-logos-vorschau.png"), fullPage: true });
  fs.unlinkSync(prev);
  await browser.close();
  console.log("✓", ids.length, "Logos + Vorschau in", out);
})();
