// Prozedurale Texturen (Canvas, synchron, deterministisch) für die 3D-Werkstatt.
import * as THREE from "three";

export const rng = (seed: number) => () => {
  seed |= 0;
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};

export const FONT = "Inter, 'DejaVu Sans', sans-serif";

export const canvasTex = (w: number, h: number, draw: (c: CanvasRenderingContext2D, w: number, h: number) => void, srgb = true) => {
  const cv = document.createElement("canvas");
  cv.width = w;
  cv.height = h;
  const c = cv.getContext("2d")!;
  draw(c, w, h);
  const t = new THREE.CanvasTexture(cv);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
};

const cache = new Map<string, any>();
export const once = <T,>(key: string, make: () => T): T => {
  if (!cache.has(key)) cache.set(key, make());
  return cache.get(key) as T;
};

const noise = (c: CanvasRenderingContext2D, w: number, h: number, n: number, alpha: number, seed: number, light = true) => {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const v = light ? (r() > 0.5 ? 255 : 0) : 0;
    c.fillStyle = `rgba(${v},${v},${v},${alpha * r()})`;
    c.fillRect(r() * w, r() * h, 1 + r() * 2, 1 + r() * 2);
  }
};

// Verzinktes Lochblech (Montageplatte 600 × 600 mm)
export const plateTex = () =>
  once("plate", () =>
    canvasTex(2048, 2048, (c, w, h) => {
      c.fillStyle = "#c4c9cd";
      c.fillRect(0, 0, w, h);
      const r = rng(7);
      // Zink-Blumen
      for (let i = 0; i < 900; i++) {
        const x = r() * w, y = r() * h, s = 30 + r() * 90;
        c.fillStyle = `rgba(${r() > 0.5 ? "255,255,255" : "70,80,90"},${0.05 + r() * 0.07})`;
        c.beginPath();
        for (let k = 0; k < 7; k++) {
          const a = (k / 7) * Math.PI * 2 + r() * 0.6, rr = s * (0.6 + r() * 0.5);
          k ? c.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr) : c.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr);
        }
        c.fill();
      }
      noise(c, w, h, 60000, 0.12, 3);
      // Löcher 14 mm Raster
      const p = (14 / 600) * w * (600 / 640);
      for (let y = p / 2; y < h; y += p)
        for (let x = p / 2; x < w; x += p) {
          c.fillStyle = "#3a3f44";
          c.beginPath();
          c.arc(x, y, p * 0.17, 0, Math.PI * 2);
          c.fill();
          c.strokeStyle = "rgba(255,255,255,0.35)";
          c.lineWidth = 1.5;
          c.beginPath();
          c.arc(x + 0.8, y + 0.8, p * 0.17, 0.2, 1.6);
          c.stroke();
        }
      // Kantenverschmutzung
      const g = c.createRadialGradient(w / 2, h / 2, w * 0.3, w / 2, h / 2, w * 0.75);
      g.addColorStop(0, "rgba(0,0,0,0)");
      g.addColorStop(1, "rgba(40,40,30,0.18)");
      c.fillStyle = g;
      c.fillRect(0, 0, w, h);
    }),
  );

export const woodTex = () =>
  once("wood", () =>
    canvasTex(2048, 1024, (c, w, h) => {
      c.fillStyle = "#d3ab7f";
      c.fillRect(0, 0, w, h);
      const r = rng(11);
      for (let i = 0; i < 260; i++) {
        const y0 = r() * h, a = 2 + r() * 8, f = 0.002 + r() * 0.004, ph = r() * 6;
        c.strokeStyle = `rgba(${120 + r() * 40},${80 + r() * 20},${45},${0.08 + r() * 0.15})`;
        c.lineWidth = 0.6 + r() * 2.2;
        c.beginPath();
        for (let x = 0; x <= w; x += 16) {
          const y = y0 + Math.sin(x * f + ph) * a + Math.sin(x * f * 3.1 + ph) * a * 0.3;
          x ? c.lineTo(x, y) : c.moveTo(x, y);
        }
        c.stroke();
      }
      noise(c, w, h, 40000, 0.08, 5);
      // Gebrauchsspuren
      for (let i = 0; i < 40; i++) {
        c.strokeStyle = `rgba(60,40,20,${0.05 + r() * 0.1})`;
        c.lineWidth = 0.6;
        c.beginPath();
        const x = r() * w, y = r() * h;
        c.moveTo(x, y);
        c.lineTo(x + (r() - 0.5) * 200, y + (r() - 0.5) * 40);
        c.stroke();
      }
    }),
  );

export const wallTex = () =>
  once("wall", () =>
    canvasTex(1024, 1024, (c, w, h) => {
      c.fillStyle = "#dedbd3";
      c.fillRect(0, 0, w, h);
      const r = rng(21);
      for (let i = 0; i < 400; i++) {
        const g = c.createRadialGradient(0, 0, 0, 0, 0, 60);
        const x = r() * w, y = r() * h;
        c.save();
        c.translate(x, y);
        g.addColorStop(0, `rgba(${r() > 0.5 ? "255,255,255" : "120,110,100"},0.06)`);
        g.addColorStop(1, "rgba(0,0,0,0)");
        c.fillStyle = g;
        c.fillRect(-60, -60, 120, 120);
        c.restore();
      }
      noise(c, w, h, 50000, 0.1, 9);
    }),
  );

export const floorTex = () =>
  once("floor", () =>
    canvasTex(1024, 1024, (c, w, h) => {
      c.fillStyle = "#8b938f";
      c.fillRect(0, 0, w, h);
      noise(c, w, h, 90000, 0.25, 13);
      const r = rng(17);
      for (let i = 0; i < 60; i++) {
        c.fillStyle = `rgba(30,30,30,${r() * 0.05})`;
        c.beginPath();
        c.ellipse(r() * w, r() * h, 20 + r() * 80, 10 + r() * 40, r() * 3, 0, Math.PI * 2);
        c.fill();
      }
    }),
  );

// Grün-gelbe Streifen (PE-Klemmen, PE-Adern)
export const pePattern = (diag = true) =>
  once("pe" + diag, () =>
    canvasTex(128, 128, (c, w, h) => {
      c.fillStyle = "#2f9e44";
      c.fillRect(0, 0, w, h);
      c.fillStyle = "#f2c80f";
      if (diag) {
        for (let k = -2; k < 4; k++) {
          c.beginPath();
          c.moveTo(k * 64, 0);
          c.lineTo(k * 64 + 32, 0);
          c.lineTo(k * 64 + 32 + 128, h);
          c.lineTo(k * 64 + 128, h);
          c.fill();
        }
      } else c.fillRect(0, 0, w / 2, h);
    }),
  );

// Beschriftungsschild (weiß, schwarzer Text)
export const labelTex = (lines: { t: string; s: number; b?: number; c?: string; y?: number; a?: CanvasTextAlign; x?: number }[], w = 256, h = 128, bg = "#f4f4f0", key = "") =>
  once("lbl" + key + JSON.stringify(lines) + w + h + bg, () =>
    canvasTex(w, h, (c) => {
      c.fillStyle = bg;
      c.fillRect(0, 0, w, h);
      lines.forEach((l, i) => {
        c.fillStyle = l.c ?? "#16191c";
        c.font = `${l.b ?? 700} ${l.s}px ${FONT}`;
        c.textAlign = l.a ?? "center";
        c.textBaseline = "middle";
        c.fillText(l.t, l.x ?? w / 2, l.y ?? (h / (lines.length + 1)) * (i + 1));
      });
    }),
  );

// Drawing-Funktion für Front-Texturen beliebiger Geräte
export const faceTex = (key: string, w: number, h: number, draw: (c: CanvasRenderingContext2D, w: number, h: number) => void) => once("face" + key, () => canvasTex(w, h, draw));

export const rr = (c: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) => {
  c.beginPath();
  c.moveTo(x + r, y);
  c.arcTo(x + w, y, x + w, y + h, r);
  c.arcTo(x + w, y + h, x, y + h, r);
  c.arcTo(x, y + h, x, y, r);
  c.arcTo(x, y, x + w, y, r);
  c.closePath();
};

// Zahlen-Atlas für Klemmen-Markierer (1..32)
export const numberAtlas = () =>
  once("numatlas", () =>
    canvasTex(2048, 64, (c, w, h) => {
      c.fillStyle = "#f6f6f2";
      c.fillRect(0, 0, w, h);
      for (let i = 0; i < 32; i++) {
        c.strokeStyle = "#c9c9c2";
        c.strokeRect(i * 64 + 0.5, 0.5, 63, 63);
        c.fillStyle = "#111";
        c.font = `700 40px ${FONT}`;
        c.textAlign = "center";
        c.textBaseline = "middle";
        c.fillText(String(i + 1), i * 64 + 32, 34);
      }
    }),
  );

// Protokoll-Blatt (Aufsicht auf dem Klemmbrett)
export const paperTex = () =>
  once("paper", () =>
    canvasTex(420, 594, (c, w, h) => {
      c.fillStyle = "#f7f6f1";
      c.fillRect(0, 0, w, h);
      c.fillStyle = "#222";
      c.font = `800 18px ${FONT}`;
      c.fillText("Prüfprotokoll VDE 0100-600", 24, 40);
      c.strokeStyle = "#9aa1a8";
      c.lineWidth = 1;
      for (let y = 70; y < h - 30; y += 22) {
        c.beginPath();
        c.moveTo(24, y);
        c.lineTo(w - 24, y);
        c.stroke();
        c.strokeRect(w - 70, y - 16, 12, 12);
        c.strokeRect(w - 40, y - 16, 12, 12);
      }
    }),
  );

// Lochwand mit Werkzeugen (unscharf im Hintergrund)
export const pegTex = () =>
  once("peg", () =>
    canvasTex(900, 600, (c, w, h) => {
      c.fillStyle = "#cfc6b4";
      c.fillRect(0, 0, w, h);
      c.fillStyle = "#8e8574";
      for (let y = 15; y < h; y += 30) for (let x = 15; x < w; x += 30) c.fillRect(x - 3, y - 3, 6, 6);
      const tools = [["#c1272d", 80, 120, 30, 220], ["#1f2937", 180, 90, 18, 260], ["#f5c400", 260, 110, 26, 200], ["#c1272d", 360, 140, 60, 140], ["#1f5fc4", 480, 100, 22, 240], ["#4b5563", 600, 120, 120, 40], ["#c1272d", 760, 90, 34, 250]] as const;
      tools.forEach(([col, x, y, tw, th]) => {
        c.fillStyle = col;
        rr(c, x, y, tw, th, 8);
        c.fill();
      });
    }),
  );

// Physikalisches Material – für schnelles Rendern auf CPU als Standard-Material (Klarlack/Sheen weggelassen)
export const phys = (p: THREE.MeshPhysicalMaterialParameters = {}): THREE.MeshStandardMaterial => {
  const { clearcoat, clearcoatRoughness, sheen, sheenColor, sheenRoughness, transmission, thickness, ...rest } = p as any;
  void clearcoat; void clearcoatRoughness; void sheen; void sheenColor; void sheenRoughness; void transmission; void thickness;
  return new THREE.MeshStandardMaterial(rest);
};
