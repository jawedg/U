// Prüfungsgestell als echtes 3D-Modell (Maße in Metern, Lage nach src/pruef/Gestell.tsx).
// Montageplatte (Lochblech), Hutschienen, Kabelkanäle mit Kammfingern, Geräte, Klemmen, Adern, Bedieneinheit, CEE-Stecker.
import React, { useMemo } from "react";
import * as THREE from "three";
import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { FONT, faceTex, labelTex, numberAtlas, once, pePattern, phys, plateTex, rr } from "./tex";

export const GW = 960;
export const K = 0.9 / GW;
export const CY = 1.25;
export const X = (px: number) => (px - 480) * K;
export const Y = (py: number) => CY - (py - 380) * K;
export const ZP = 0.002; // Vorderseite Montageplatte
export const ZR = 0.0095; // Oberkante Hutschiene

// ------------------------------------------------------------------ Geometrie-Helfer
type G = THREE.BufferGeometry;
const prep = (g: G) => {
  const n = g.index ? g.toNonIndexed() : g;
  Object.keys(n.attributes).forEach((k) => !["position", "normal", "uv"].includes(k) && n.deleteAttribute(k));
  if (!n.attributes.uv) n.setAttribute("uv", new THREE.Float32BufferAttribute(new Float32Array((n.attributes.position.count * 2)), 2));
  return n;
};
export const merge = (gs: G[]) => (gs.length ? mergeGeometries(gs.map(prep)) : new THREE.BufferGeometry());
export const bx = (w: number, h: number, d: number, x: number, y: number, z: number, r = 0) => {
  const g = r > 0 ? new RoundedBoxGeometry(w, h, d, 2, r) : new THREE.BoxGeometry(w, h, d);
  g.translate(x, y, z);
  return g;
};
// Zylinder entlang z
export const cz = (r: number, len: number, x: number, y: number, z: number, seg = 18, r2?: number) => {
  const g = new THREE.CylinderGeometry(r2 ?? r, r, len, seg);
  g.rotateX(Math.PI / 2);
  g.translate(x, y, z);
  return g;
};
const tube = (pts: THREE.Vector3[], r: number, seg = 24) => new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts, false, "catmullrom", 0.3), seg, r, 7, false);

// ------------------------------------------------------------------ Materialien
export const MAT = () =>
  once("mats", () => {
    const P = (color: string, roughness: number, extra: Partial<THREE.MeshPhysicalMaterialParameters> = {}) => phys({ color, roughness, ...extra });
    const S = (color: string, roughness: number, metalness = 0, extra: Partial<THREE.MeshStandardMaterialParameters> = {}) => new THREE.MeshStandardMaterial({ color, roughness, metalness, ...extra });
    return {
      white: P("#ecebe5", 0.42, { clearcoat: 0.25, clearcoatRoughness: 0.45 }),
      grey: P("#cdd0cb", 0.5, { clearcoat: 0.1 }),
      greyMid: P("#a9aeb0", 0.55),
      anth: P("#3a3f44", 0.45, { clearcoat: 0.2 }),
      black: P("#1c1f22", 0.5, { clearcoat: 0.15 }),
      rubber: S("#141618", 0.85),
      metal: S("#d3d7db", 0.28, 1),
      zinc: S("#b9bfc5", 0.38, 0.95),
      alu: S("#c9ced3", 0.36, 0.85),
      hole: S("#0c0d0e", 0.9),
      duct: P("#aeb3b5", 0.6),
      termGrey: P("#aeb2ae", 0.5),
      termBlue: P("#2f6fba", 0.45),
      termPE: phys({ map: pePattern(), roughness: 0.45 }),
      plate: S("#ffffff", 0.42, 0.65, { map: plateTex() }),
      red: P("#c3261f", 0.42, { clearcoat: 0.3 }),
      pcb: P("#1f5e36", 0.35, { clearcoat: 0.6 }),
      yellow: P("#f2c200", 0.5),
      copper: S("#c58b4f", 0.3, 1),
    };
  });
type MatKey = keyof ReturnType<typeof MAT>;

export const M: React.FC<{ g: G; m: MatKey | THREE.Material; shadow?: boolean }> = ({ g, m, shadow = true }) => (
  <mesh geometry={g} material={typeof m === "string" ? MAT()[m] : m} castShadow={shadow} receiveShadow />
);

const faceMat = (t: THREE.Texture, rough = 0.5) => new THREE.MeshStandardMaterial({ map: t, roughness: rough, polygonOffset: true, polygonOffsetFactor: -2 });
// Bild-Ebene (Beschriftung) – liegt minimal vor der Fläche
const Face: React.FC<{ t: THREE.Texture; w: number; h: number; x: number; y: number; z: number; rough?: number }> = ({ t, w, h, x, y, z, rough }) => {
  const m = useMemo(() => faceMat(t, rough), [t, rough]);
  return (
    <mesh position={[x, y, z + 0.0003]} material={m} receiveShadow>
      <planeGeometry args={[w, h]} />
    </mesh>
  );
};

// ------------------------------------------------------------------ Kabelkanäle
export const DUCTS: [number, number, number][] = [[14, 626, 14], [14, 626, 214], [14, 626, 414], [14, 590, 606]]; // x0, x1, y (px), Breite 26 px
const DW = 26 * K, DD = 0.04, PITCH = 0.012;
const ductEdge = (y: number, up: boolean) => (up ? Y(y + 26) : Y(y)); // untere Kante (Kanal oberhalb) bzw. obere Kante
export const gapX = (xm: number, x0px: number) => {
  const x0 = X(x0px);
  const n = Math.round((xm - x0 - 0.009) / PITCH);
  return x0 + n * PITCH + 0.009;
};

const ductGeo = () =>
  once("ductGeo", () => {
    const base: G[] = [], cover: G[] = [];
    DUCTS.forEach(([a, b, y]) => {
      const x0 = X(a), x1 = X(b), L = x1 - x0, cx = (x0 + x1) / 2, cy = Y(y + 13);
      base.push(bx(L, DW, 0.0015, cx, cy, ZP + 0.00075));
      [1, -1].forEach((s) => {
        const yy = cy + (s * (DW - 0.002)) / 2;
        base.push(bx(L, 0.002, 0.01, cx, yy, ZP + 0.005));
        for (let x = x0; x + 0.006 <= x1; x += PITCH) base.push(bx(0.006, 0.002, DD - 0.01, x + 0.003, yy, ZP + 0.01 + (DD - 0.01) / 2));
      });
      cover.push(bx(L + 0.002, DW + 0.004, 0.003, cx, cy, ZP + DD + 0.0015, 0.001));
      [1, -1].forEach((s) => cover.push(bx(L + 0.002, 0.0012, 0.006, cx, cy + (s * (DW + 0.003)) / 2, ZP + DD - 0.002)));
    });
    return { base: merge(base), cover: merge(cover) };
  });

// ------------------------------------------------------------------ Adern
type Wire = { pts: THREE.Vector3[]; col: string };
const WCOL: Record<string, string> = { L: "#25272a", BR: "#5c3b26", GR: "#80858a", N: "#3f86d4", DB: "#1f3d8a", RD: "#b4231c", WH: "#e8e8e2" };
// Ader von einem Anschluss (x, y, z) zum Kanal (oben/unten)
const toDuct = (x: number, y: number, z: number, ductY: number, ductX0: number, up: boolean, col: string, bend = 0): Wire => {
  const e = ductEdge(ductY, up);
  const s = up ? 1 : -1;
  const xs = gapX(x + bend, ductX0);
  return {
    col,
    pts: [
      new THREE.Vector3(x, y, z),
      new THREE.Vector3(x, y + s * 0.007, z + 0.001),
      new THREE.Vector3((x + xs) / 2, (y + e) / 2 + s * 0.004, (z + 0.022) / 2 + 0.004),
      new THREE.Vector3(xs, e - s * 0.006, 0.023),
      new THREE.Vector3(xs, e + s * 0.004, 0.022),
      new THREE.Vector3(xs, e + s * 0.012, 0.018),
    ],
  };
};

// ------------------------------------------------------------------ Hutschienen-Geräte
const ROWA = Y(126);
const screwPair = (g: { screw: G[]; hole: G[] }, x: number, y: number, z: number, w = 0.007) => {
  g.hole.push(bx(w, 0.0075, 0.002, x, y, z - 0.0005));
  g.screw.push(cz(0.0026, 0.003, x, y, z - 0.0025, 14));
  g.hole.push(bx(0.0042, 0.0007, 0.0006, x, y, z - 0.0007));
};

type Parts = Record<"white" | "grey" | "anth" | "black" | "screw" | "hole" | "metal" | "yellow" | "red" | "pcb" | "greyMid" | "rubber", G[]>;
const newParts = (): Parts => ({ white: [], grey: [], anth: [], black: [], screw: [], hole: [], metal: [], yellow: [], red: [], pcb: [], greyMid: [], rubber: [] });

const mcb = (P: Parts, x0: number, w: number, on: boolean, test: boolean) => {
  const W = w * K - 0.0006, cx = X(x0 + w / 2), cy = ROWA;
  P.white.push(bx(W, 0.09, 0.044, cx, cy, ZR + 0.022, 0.0015));
  P.white.push(bx(W, 0.046, 0.026, cx, cy, ZR + 0.056, 0.0015));
  // Schräge Schultern
  P.white.push(bx(W, 0.008, 0.012, cx, cy + 0.026, ZR + 0.047, 0.001));
  P.white.push(bx(W, 0.008, 0.012, cx, cy - 0.026, ZR + 0.047, 0.001));
  // Kippschalter
  const lev = bx(Math.min(W * 0.5, 0.009), 0.014, 0.014, 0, 0, 0, 0.0015);
  lev.rotateX(on ? -0.45 : 0.45);
  lev.translate(cx, cy + (on ? 0.008 : -0.008), ZR + 0.072);
  P.anth.push(lev);
  P.hole.push(bx(W * 0.62, 0.03, 0.001, cx, cy, ZR + 0.0693));
  if (test) P.yellow.push(bx(0.006, 0.006, 0.003, cx + W / 2 - 0.007, cy - 0.016, ZR + 0.0705, 0.0008));
  const nS = Math.max(1, Math.round(w / 24));
  for (let i = 0; i < nS; i++) {
    const sx = cx - W / 2 + (W / nS) * (i + 0.5);
    screwPair(P as any, sx, cy + 0.037, ZR + 0.0442);
    screwPair(P as any, sx, cy - 0.037, ZR + 0.0442);
  }
  return { cx, W, top: cy + 0.045, bot: cy - 0.045, n: nS };
};

const contactor = (P: Parts, x0: number) => {
  const W = 0.0425, cx = X(x0 + 23), cy = ROWA;
  P.grey.push(bx(W, 0.085, 0.05, cx, cy, ZR + 0.025, 0.002));
  P.grey.push(bx(W - 0.003, 0.052, 0.032, cx, cy, ZR + 0.064, 0.002));
  P.hole.push(bx(0.016, 0.01, 0.001, cx, cy + 0.01, ZR + 0.0802));
  P.greyMid.push(bx(0.012, 0.006, 0.002, cx, cy + 0.01, ZR + 0.0803));
  [-0.013, 0, 0.013].forEach((dx) => {
    screwPair(P as any, cx + dx, cy + 0.035, ZR + 0.0502);
    screwPair(P as any, cx + dx, cy - 0.035, ZR + 0.0502);
  });
  return { cx, top: cy + 0.0425, bot: cy - 0.0425 };
};

const Devices: React.FC<{ st: Record<string, number> }> = ({ st }) => {
  const f3on = !st.F3trip;
  const built = useMemo(() => {
    const P = newParts();
    const wires: Wire[] = [];
    const D0 = DUCTS[0][0];
    // F3 FI/LS, F1, F2
    const f3 = mcb(P, 50, 52, f3on, true);
    const f1 = mcb(P, 104, 24, true, false);
    const f2 = mcb(P, 130, 24, true, false);
    [[f3, ["L", "N"]], [f1, ["L"]], [f2, ["L"]]].forEach(([d, cols]: any) => {
      cols.forEach((c: string, i: number) => {
        const sx = d.cx - d.W / 2 + (d.W / cols.length) * (i + 0.5);
        wires.push(toDuct(sx, d.top - 0.004, ZR + 0.02, 14, D0, true, WCOL[c]));
        wires.push(toDuct(sx, d.bot + 0.004, ZR + 0.02, 214, D0, false, WCOL[c], i ? 0.01 : -0.01));
      });
    });
    // T1 Netzteil
    const tx = X(206), ty = Y(126);
    P.grey.push(bx(0.084, 0.1, 0.058, tx, ty, ZR + 0.029, 0.003));
    [-0.03, -0.015, 0].forEach((dx) => screwPair(P as any, tx + dx, ty + 0.043, ZR + 0.0582));
    [-0.03, -0.015, 0, 0.015].forEach((dx) => screwPair(P as any, tx + dx, ty - 0.043, ZR + 0.0582));
    P.anth.push(cz(0.003, 0.004, tx + 0.03, ty - 0.03, ZR + 0.06, 12));
    ["DB", "DB", "WH", "WH"].forEach((c, i) => wires.push(toDuct(tx - 0.03 + i * 0.015, ty - 0.05, ZR + 0.03, 214, D0, false, WCOL[c === "WH" ? "DB" : "RD"])));
    // F4 Motorschutz
    const fx = X(293), fy = ROWA;
    P.anth.push(bx(0.045, 0.09, 0.06, fx, fy, ZR + 0.03, 0.002));
    P.anth.push(bx(0.042, 0.056, 0.026, fx, fy, ZR + 0.072, 0.003));
    P.black.push(cz(0.0145, 0.008, fx, fy + 0.008, ZR + 0.089, 28));
    const grip = bx(0.0065, 0.027, 0.009, 0, 0, 0, 0.002);
    grip.rotateZ(-0.0);
    grip.translate(fx, fy + 0.008, ZR + 0.096);
    P.black.push(grip);
    P.white.push(cz(0.0055, 0.003, fx, fy - 0.019, ZR + 0.0865, 16));
    [-0.013, 0, 0.013].forEach((dx) => {
      screwPair(P as any, fx + dx, fy + 0.038, ZR + 0.0602);
      screwPair(P as any, fx + dx, fy - 0.038, ZR + 0.0602);
      wires.push(toDuct(fx + dx, fy + 0.045, ZR + 0.03, 14, D0, true, WCOL[["BR", "L", "GR"][Math.round(dx / 0.013) + 1]]));
      wires.push(toDuct(fx + dx, fy - 0.045, ZR + 0.03, 214, D0, false, WCOL[["BR", "L", "GR"][Math.round(dx / 0.013) + 1]]));
    });
    // Wendeschütze Q1/Q2
    const q1 = contactor(P, 330), q2 = contactor(P, 380);
    [q1, q2].forEach((q, qi) => {
      [-0.013, 0, 0.013].forEach((dx, k) => {
        wires.push(toDuct(q.cx + dx, q.top, ZR + 0.035, 14, D0, true, WCOL[["BR", "L", "GR"][k]], qi ? 0.02 : -0.02));
        wires.push(toDuct(q.cx + dx, q.bot, ZR + 0.035, 214, D0, false, WCOL[["BR", "L", "GR"][qi ? 2 - k : k]], qi ? 0.02 : -0.02));
      });
      wires.push(toDuct(q.cx + 0.019, q.top - 0.006, ZR + 0.05, 14, D0, true, WCOL.DB));
      wires.push(toDuct(q.cx - 0.019, q.bot + 0.006, ZR + 0.05, 214, D0, false, WCOL.DB));
    });
    // Brücken Q1 → Q2 (oben)
    [-0.013, 0, 0.013].forEach((dx, k) => {
      const a = new THREE.Vector3(q1.cx + dx, q1.top, ZR + 0.035), b = new THREE.Vector3(q2.cx + dx, q2.top, ZR + 0.035);
      wires.push({ col: WCOL[["BR", "L", "GR"][k]], pts: [a, a.clone().add(new THREE.Vector3(0, 0.012 + k * 0.004, 0.004)), b.clone().add(new THREE.Vector3(0, 0.012 + k * 0.004, 0.004)), b] });
    });
    // Steckdose X5 – Gehäuse mit runder Vertiefung
    const sx = X(528), sy = Y(128);
    const shape = new THREE.Shape();
    const S = 0.084, R = 0.012;
    shape.moveTo(-S / 2 + R, -S / 2);
    shape.lineTo(S / 2 - R, -S / 2);
    shape.quadraticCurveTo(S / 2, -S / 2, S / 2, -S / 2 + R);
    shape.lineTo(S / 2, S / 2 - R);
    shape.quadraticCurveTo(S / 2, S / 2, S / 2 - R, S / 2);
    shape.lineTo(-S / 2 + R, S / 2);
    shape.quadraticCurveTo(-S / 2, S / 2, -S / 2, S / 2 - R);
    shape.lineTo(-S / 2, -S / 2 + R);
    shape.quadraticCurveTo(-S / 2, -S / 2, -S / 2 + R, -S / 2);
    const hole = new THREE.Path();
    hole.absarc(0, 0, 0.0205, 0, Math.PI * 2, true);
    shape.holes.push(hole);
    const house = new THREE.ExtrudeGeometry(shape, { depth: 0.042, bevelEnabled: true, bevelThickness: 0.002, bevelSize: 0.002, bevelSegments: 3, curveSegments: 40 });
    house.translate(sx, sy, ZP);
    P.white.push(house);
    const floor = new THREE.CircleGeometry(0.0206, 40);
    floor.translate(sx, sy, ZP + 0.027);
    P.white.push(floor);
    [-0.0095, 0.0095].forEach((dx) => P.hole.push(cz(0.0026, 0.002, sx + dx, sy, ZP + 0.0272, 16)));
    [1, -1].forEach((s) => P.metal.push(bx(0.008, 0.0025, 0.012, sx, sy + s * 0.019, ZP + 0.036, 0.0006)));
    return { geo: Object.fromEntries(Object.entries(P).map(([k, v]) => [k, merge(v)])) as Record<keyof Parts, G>, wires };
  }, [f3on]);

  const labels = useMemo(() => {
    const L: React.ReactNode[] = [];
    const lab = (k: string, lines: any[], w: number, h: number, x: number, y: number, z: number, pw = 256, ph = 128, bg?: string) =>
      L.push(<Face key={k} t={labelTex(lines, pw, ph, bg, k)} w={w} h={h} x={x} y={y} z={z} />);
    // Aufdrucke der LS / FI-LS
    lab("f3", [{ t: "B16", s: 54, b: 800 }, { t: "IΔn 10 mA  Typ A", s: 22 }], 0.044, 0.016, X(76), ROWA - 0.022, ZR + 0.069, 256, 96, "#ecebe5");
    lab("f1", [{ t: "B6", s: 54, b: 800 }], 0.019, 0.012, X(116), ROWA - 0.022, ZR + 0.069, 128, 80, "#ecebe5");
    lab("f2", [{ t: "B4", s: 54, b: 800 }], 0.019, 0.012, X(142), ROWA - 0.022, ZR + 0.069, 128, 80, "#ecebe5");
    // Betriebsmittelkennzeichen (weiße Schilder unter den Geräten)
    [["-F3", 76, 0.03], ["-F1", 116, 0.018], ["-F2", 142, 0.018], ["-T1", 206, 0.03], ["-F4", 293, 0.03], ["-Q1", 353, 0.03], ["-Q2", 403, 0.03]].forEach(([t, px, w]: any) =>
      lab("bmk" + t, [{ t, s: 64, b: 800 }], w, 0.009, X(px), Y(196), ZP + 0.0005, 256, 80, "#f7f7f2"));
    lab("x5", [{ t: "-X5", s: 64, b: 800 }], 0.03, 0.009, X(528), Y(206), ZP + 0.0005, 256, 80, "#f7f7f2");
    // T1 Front
    L.push(
      <Face key="t1f" t={faceTex("t1", 512, 600, (c, w, h) => {
        c.fillStyle = "#cfd2cd"; c.fillRect(0, 0, w, h);
        c.fillStyle = "#b7bbb6"; for (let i = 0; i < 9; i++) rr(c, 60 + i * 44, 120, 22, 120, 10), c.fill();
        c.fillStyle = "#1d2125"; c.font = `800 46px ${FONT}`; c.textAlign = "left"; c.fillText("POWER", 60, 320);
        c.font = `600 34px ${FONT}`; c.fillText("24 V DC  2,5 A", 60, 370); c.fillText("IN 100–240 V AC", 60, 415);
        c.font = `700 26px ${FONT}`; c.fillText("DC OK", 330, 498); c.fillText("ADJ", 330, 560);
        c.fillStyle = "#1d2125"; c.font = `700 24px ${FONT}`;
        ["L", "N", "⏚"].forEach((s, i) => c.fillText(s, 120 + i * 90, 40));
        ["+", "+", "−", "−"].forEach((s, i) => c.fillText(s, 120 + i * 90, 590));
      })} w={0.084} h={0.1} x={X(206)} y={Y(126)} z={ZR + 0.0582} />,
    );
    // F4 Front (Einstellskala)
    L.push(
      <Face key="f4f" t={faceTex("f4", 256, 512, (c, w, h) => {
        c.fillStyle = "#3a3f44"; c.fillRect(0, 0, w, h);
        c.fillStyle = "#e5e7eb"; c.font = `800 30px ${FONT}`; c.textAlign = "center";
        c.fillText("I", 128, 40); c.fillText("O", 40, 170);
        c.font = `600 22px ${FONT}`; c.fillText("2,5   3,25   4 A", 128, 420); c.fillText("ON", 200, 170);
        c.strokeStyle = "#e5e7eb"; c.lineWidth = 3; c.beginPath(); c.arc(128, 380, 50, Math.PI * 1.15, Math.PI * 1.85); c.stroke();
      })} w={0.042} h={0.056} x={X(293)} y={ROWA} z={ZR + 0.0851} />,
    );
    // Schütze Front
    ["Q1", "Q2"].forEach((q, i) =>
      L.push(<Face key={q} t={faceTex("q" + q, 256, 320, (c, w, h) => {
        c.fillStyle = "#c9ccc7"; c.fillRect(0, 0, w, h);
        c.fillStyle = "#23272b"; c.font = `800 40px ${FONT}`; c.textAlign = "center"; c.fillText("-" + q, 128, 230);
        c.font = `600 22px ${FONT}`; c.fillText("A1        A2", 128, 40); c.fillText("4 kW  AC-3  24 V DC", 128, 290);
      })} w={0.0395} h={0.052} x={X(353 + i * 50)} y={ROWA - 0.0} z={ZR + 0.0801} />),
    );
    return L;
  }, []);

  const T1on = !st.T1off;
  const wiresGeo = useMemo(() => {
    const by: Record<string, G[]> = {};
    built.wires.forEach((w) => (by[w.col] ??= []).push(tube(w.pts, 0.0015)));
    // Netzteil-Eingang (separat, wird bei der Isolationsmessung abgeklemmt)
    return Object.entries(by).map(([c, gs]) => [c, merge(gs)] as const);
  }, [built]);
  const t1in = useMemo(() => {
    const tx = X(206), ty = Y(126);
    return (["L", "N", "PE"] as const).map((c, i) => {
      const w = toDuct(tx - 0.03 + i * 0.015, ty + 0.05, ZR + 0.03, 14, DUCTS[0][0], true, c === "PE" ? "PE" : WCOL[c]);
      return { c, g: tube(w.pts, 0.0015) };
    });
  }, []);
  const t1loose = useMemo(() => {
    const tx = X(206), ty = Y(126);
    return [0, 1, 2].map((i) => {
      const x = tx - 0.03 + i * 0.015;
      const top = Y(40) - 0.004;
      return tube([new THREE.Vector3(gapX(x, 14), top, 0.022), new THREE.Vector3(gapX(x, 14), top - 0.01, 0.03), new THREE.Vector3(x + 0.004 * i, ty + 0.06, ZR + 0.07), new THREE.Vector3(x + 0.006 * i - 0.004, ty + 0.045, ZR + 0.085)], 0.0015);
    });
  }, []);

  return (
    <group>
      {Object.entries(built.geo).map(([k, g]) => (
        <M key={k} g={g} m={k === "screw" ? "metal" : (k as any)} />
      ))}
      {labels}
      {wiresGeo.map(([c, g]) => <M key={c} g={g} m={wireMat(c)} />)}
      {T1on
        ? t1in.map((w, i) => <M key={i} g={w.g} m={w.c === "PE" ? wirePE() : wireMat(WCOL[w.c])} />)
        : t1loose.map((g, i) => <M key={i} g={g} m={i === 2 ? wirePE() : wireMat(WCOL[["L", "N"][i]])} />)}
      {/* DC-OK-LED */}
      <mesh position={[X(206) + 0.024, Y(126) - 0.029, ZR + 0.0595]}>
        <sphereGeometry args={[0.0022, 12, 12]} />
        <meshStandardMaterial color={T1on ? "#3cff6a" : "#1d3524"} emissive={T1on ? "#2bff5a" : "#000"} emissiveIntensity={T1on ? 3 : 0} />
      </mesh>
    </group>
  );
};

export const wireMat = (c: string) => once("wire" + c, () => phys({ color: c, roughness: 0.38, clearcoat: 0.4, clearcoatRoughness: 0.3 }));
export const wirePE = () => once("wirePE", () => {
  const t = pePattern(false).clone();
  t.needsUpdate = true;
  t.repeat.set(30, 1);
  return phys({ map: t, roughness: 0.38, clearcoat: 0.4 });
});

// ------------------------------------------------------------------ Reihenklemmen
const TERM_Y = Y(526), HT = 0.068;
const termShape = () =>
  once("termShape", () => {
    const s = new THREE.Shape();
    const P: [number, number][] = [[-HT / 2, 0], [HT / 2, 0], [HT / 2, 0.022], [0.028, 0.024], [0.028, 0.031], [0.012, 0.036], [0.009, 0.046], [-0.009, 0.046], [-0.012, 0.036], [-0.028, 0.031], [-0.028, 0.024], [-HT / 2, 0.022]];
    P.forEach(([u, v], i) => (i ? s.lineTo(u, v) : s.moveTo(u, v)));
    s.closePath();
    return s;
  });
const termGeo = (x: number, w: number) => {
  const g = new THREE.ExtrudeGeometry(termShape(), { depth: w, bevelEnabled: false });
  g.applyMatrix4(new THREE.Matrix4().set(0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1));
  g.translate(x - w / 2, TERM_Y, ZR);
  return g;
};
export const STRIPS: { id: string; x0: number; n: number; col: (k: number) => "termGrey" | "termBlue" | "termPE"; wires: (k: number) => string }[] = [
  { id: "X1", x0: 50, n: 22, col: (k) => ([9, 10, 16].includes(k) ? "termPE" : k === 7 ? "termBlue" : "termGrey"), wires: (k) => (k === 1 ? "L" : k === 3 ? "BR" : k === 5 ? "GR" : k === 7 ? "N" : [9, 10, 16].includes(k) ? "PE" : k < 7 ? "L" : "DB") },
  { id: "X2", x0: 304, n: 9, col: (k) => (k % 2 ? "termBlue" : "termGrey"), wires: (k) => (k % 2 ? "DB" : "DB") },
  { id: "X3", x0: 418, n: 7, col: () => "termGrey", wires: () => "DB" },
  { id: "X4", x0: 512, n: 8, col: () => "termGrey", wires: () => "DB" },
];
export const termX = (x0: number, k: number) => X(x0 + 5 + (k - 1) * 10.9);
export const TERM_SCREW_TOP = () => new THREE.Vector3(0, TERM_Y + 0.0195, ZR + 0.0348);

const Terminals: React.FC = () => {
  const built = useMemo(() => {
    const body: Record<string, G[]> = { termGrey: [], termBlue: [], termPE: [] };
    const scr: G[] = [], hole: G[] = [], grey: G[] = [], marks: G[] = [];
    const wires: { col: string; g: G }[] = [];
    STRIPS.forEach((S) => {
      for (let k = 1; k <= S.n; k++) {
        const x = termX(S.x0, k);
        body[S.col(k)].push(termGeo(x, 0.0098));
        [1, -1].forEach((s) => {
          const y = TERM_Y + s * 0.0195, z = ZR + 0.0338;
          hole.push(bx(0.0066, 0.0066, 0.0012, x, y, z + 0.0002));
          scr.push(cz(0.0024, 0.0012, x, y, z + 0.0006, 16));
          hole.push(bx(0.0034, 0.0007, 0.0004, x, y, z + 0.0012));
          hole.push(bx(0.0055, 0.002, 0.004, x, TERM_Y + s * (HT / 2 + 0.0001), ZR + 0.012));
        });
        // Markierer
        const m = new THREE.PlaneGeometry(0.0085, 0.0075);
        const uv = m.attributes.uv as THREE.BufferAttribute;
        for (let i = 0; i < uv.count; i++) uv.setX(i, (k - 1 + uv.getX(i)) / 32);
        m.translate(x, TERM_Y, ZR + 0.0462);
        marks.push(m);
        // Adern oben (zum Kanal 414) und unten (Kanal 606)
        const c = S.wires(k);
        const top = toDuct(x, TERM_Y + HT / 2, ZR + 0.012, 414, 14, true, c, ((k % 3) - 1) * 0.004);
        wires.push({ col: c, g: tube(top.pts, 0.0015, 20) });
        if (S.id !== "X1" || k <= 9 || k === 16) {
          const bot = toDuct(x, TERM_Y - HT / 2, ZR + 0.012, 606, 14, false, c === "PE" ? "PE" : S.id === "X1" ? c : "DB", 0);
          wires.push({ col: c, g: tube(bot.pts, 0.0015, 20) });
        }
      }
      // Endhalter + Abschlussplatte
      const xa = termX(S.x0, 1) - 0.0105, xb = termX(S.x0, S.n) + 0.0062;
      grey.push(bx(0.009, 0.05, 0.036, xa, TERM_Y, ZR + 0.018, 0.0015));
      grey.push(bx(0.0018, HT, 0.044, xb, TERM_Y, ZR + 0.022));
      grey.push(bx(0.009, 0.05, 0.036, xb + 0.0062, TERM_Y, ZR + 0.018, 0.0015));
      scr.push(cz(0.002, 0.002, xa, TERM_Y + 0.015, ZR + 0.037, 12));
      scr.push(cz(0.002, 0.002, xb + 0.0062, TERM_Y + 0.015, ZR + 0.037, 12));
    });
    const byCol: Record<string, G[]> = {};
    wires.forEach((w) => (byCol[w.col] ??= []).push(w.g));
    return {
      body: Object.entries(body).map(([k, v]) => [k, merge(v)] as const),
      scr: merge(scr), hole: merge(hole), grey: merge(grey), marks: merge(marks),
      wires: Object.entries(byCol).map(([k, v]) => [k, merge(v)] as const),
    };
  }, []);
  const markMat = useMemo(() => new THREE.MeshStandardMaterial({ map: numberAtlas(), roughness: 0.6, polygonOffset: true, polygonOffsetFactor: -2 }), []);
  return (
    <group>
      {built.body.map(([k, g]) => <M key={k} g={g} m={k as MatKey} />)}
      <M g={built.scr} m="metal" />
      <M g={built.hole} m="hole" shadow={false} />
      <M g={built.grey} m="termGrey" />
      <mesh geometry={built.marks} material={markMat} receiveShadow />
      {built.wires.map(([c, g]) => <M key={c} g={g} m={c === "PE" ? wirePE() : wireMat(WCOL[c] ?? WCOL.DB)} />)}
      {STRIPS.map((S) => (
        <Face key={S.id} t={labelTex([{ t: "-" + S.id, s: 60, b: 800 }], 192, 80, "#f7f7f2", S.id)} w={0.016} h={0.0068} x={termX(S.x0, 1) - 0.0105} y={TERM_Y + 0.012} z={ZR + 0.0362} />
      ))}
    </group>
  );
};

// ------------------------------------------------------------------ SPS + Erweiterung + Prozess-Simulation
const Plc: React.FC = () => {
  const cy = Y(326);
  const parts = useMemo(() => {
    const P = newParts();
    const mods: [number, number][] = [[X(50) + 0.056, 0.11], [X(50) + 0.137, 0.045], [X(50) + 0.185, 0.045]];
    const wires: G[] = [], wiresR: G[] = [];
    mods.forEach(([x, w], mi) => {
      P.anth.push(bx(w - 0.001, 0.1, 0.072, x, cy, ZR + 0.036, 0.002));
      [1, -1].forEach((s) => P.grey.push(bx(w - 0.004, 0.024, 0.008, x, cy + s * 0.034, ZR + 0.074, 0.0015)));
      const n = mi ? 4 : 8;
      for (let i = 0; i < n; i++) {
        const wx = x - w / 2 + 0.006 + (i * (w - 0.012)) / (n - 1);
        if (i % 2 === 0 || mi) wires.push(tube(toDuct(wx, cy + 0.05, ZR + 0.06, 214, 14, true, "DB").pts, 0.0013, 20));
        if (i % 3 !== 1) (i === 0 ? wiresR : wires).push(tube(toDuct(wx, cy - 0.05, ZR + 0.06, 414, 14, false, "DB").pts, 0.0013, 20));
      }
    });
    P.black.push(bx(0.014, 0.011, 0.004, X(50) + 0.03, cy - 0.046, ZR + 0.073, 0.001));
    // Prozess-Simulationsplatine X10
    const px = X(511), py = Y(327);
    P.pcb.push(bx(0.168, 0.138, 0.0016, px, py, ZP + 0.026));
    [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([a, b]) => P.metal.push(cz(0.003, 0.024, px + a * 0.078, py + b * 0.063, ZP + 0.013, 10)));
    [0, 1, 2, 3].forEach((i) => {
      const sx = X(443 + i * 36), sy = Y(352);
      P.black.push(bx(0.012, 0.008, 0.007, sx, sy, ZP + 0.0305, 0.001));
      const lev = cz(0.0011, 0.009, 0, 0, 0, 8);
      lev.rotateY(i === 1 ? 0.5 : -0.5);
      lev.translate(sx, sy, ZP + 0.037);
      P.metal.push(lev);
    });
    P.black.push(bx(0.05, 0.008, 0.009, px, py + 0.058, ZP + 0.031, 0.001));
    // Flachbandkabel X10 → Kanal
    const rib = tube([new THREE.Vector3(px, py + 0.062, ZP + 0.034), new THREE.Vector3(px, py + 0.075, ZP + 0.03), new THREE.Vector3(px + 0.01, Y(240) - 0.004, 0.024), new THREE.Vector3(px + 0.01, Y(240) + 0.01, 0.018)], 0.0018);
    rib.scale(1, 1, 1);
    P.greyMid.push(rib);
    return { geo: Object.fromEntries(Object.entries(P).map(([k, v]) => [k, merge(v)])) as Record<keyof Parts, G>, wires: merge(wires), wiresR: merge(wiresR) };
  }, []);
  const cpuFace = faceTex("cpu", 600, 540, (c, w, h) => {
    c.fillStyle = "#3a3f44"; c.fillRect(0, 0, w, h);
    c.fillStyle = "#cfd2cd"; c.fillRect(0, 0, w, 140); c.fillRect(0, 400, w, 140);
    c.fillStyle = "#2a2e32"; c.font = `600 22px ${FONT}`; c.textAlign = "center";
    for (let i = 0; i < 14; i++) c.fillText(`.${i % 8}`, 30 + i * 40, 30);
    for (let i = 0; i < 12; i++) c.fillText(i < 2 ? ["L+", "M"][i] : `.${(i - 2) % 8}`, 30 + i * 46, 520);
    c.fillStyle = "#4fb3a9"; c.font = `800 44px ${FONT}`; c.textAlign = "left"; c.fillText("SIMATIC", 30, 210);
    c.fillStyle = "#e5e7eb"; c.font = `700 30px ${FONT}`; c.fillText("S7-1200", 30, 252);
    c.font = `500 22px ${FONT}`; c.fillText("CPU 1214C DC/DC/DC", 30, 290);
    ["RUN/STOP", "ERROR", "MAINT"].forEach((l, i) => c.fillText(l, 70, 330 + i * 26));
    c.fillText("DI a", 380, 210); c.fillText("DQ a", 380, 300);
    for (let i = 0; i < 8; i++) { c.fillStyle = "#2a3a2c"; c.fillRect(380 + (i % 8) * 24, 222, 16, 10); c.fillRect(380 + (i % 8) * 24, 312, 16, 10); }
  });
  const smFace = faceTex("sm", 240, 540, (c, w, h) => {
    c.fillStyle = "#3a3f44"; c.fillRect(0, 0, w, h);
    c.fillStyle = "#cfd2cd"; c.fillRect(0, 0, w, 140); c.fillRect(0, 400, w, 140);
    c.fillStyle = "#e5e7eb"; c.font = `700 26px ${FONT}`; c.textAlign = "center"; c.fillText("SM 1223", 120, 210);
    c.font = `500 20px ${FONT}`; c.fillText("DI8 / DQ8", 120, 244);
    for (let i = 0; i < 8; i++) { c.fillStyle = "#2a3a2c"; c.fillRect(40 + (i % 4) * 44, 280 + Math.floor(i / 4) * 24, 22, 10); }
  });
  const pcbFace = faceTex("pcb", 720, 560, (c, w, h) => {
    c.fillStyle = "#1f6138"; c.fillRect(0, 0, w, h);
    c.strokeStyle = "rgba(160,220,150,0.35)"; c.lineWidth = 5;
    const r = Math.random; void r;
    for (let i = 0; i < 18; i++) { c.beginPath(); c.moveTo(40 + i * 36, 60); c.lineTo(40 + i * 36, 160 + (i % 4) * 30); c.lineTo(100 + i * 30, 240 + (i % 3) * 20); c.stroke(); }
    c.fillStyle = "#e8f5e9"; c.font = `700 26px ${FONT}`; c.textAlign = "left"; c.fillText("-X10  PROZESS-SIMULATION", 30, 40);
    c.font = `600 20px ${FONT}`; c.textAlign = "center";
    [["P10", "M1 links"], ["P11", "M1 rechts"], ["P12", "M2"], ["P13", ""], ["P14", ""]].forEach(([a, b], i) => { c.fillText(a, 80 + i * 135, 230); c.fillText(b, 80 + i * 135, 256); });
    [["B10", "zu"], ["B11", "auf"], ["B12", ""], ["B13", "Band"]].forEach(([a, b], i) => { c.fillText(a, 92 + i * 142, 470); c.fillText(b, 92 + i * 142, 496); });
  });
  return (
    <group>
      {Object.entries(parts.geo).map(([k, g]) => <M key={k} g={g} m={k as any} />)}
      <M g={parts.wires} m={wireMat(WCOL.DB)} />
      <M g={parts.wiresR} m={wireMat(WCOL.RD)} />
      <Face t={cpuFace} w={0.109} h={0.1} x={X(50) + 0.056} y={cy} z={ZR + 0.0722} rough={0.45} />
      <Face t={smFace} w={0.044} h={0.1} x={X(50) + 0.137} y={cy} z={ZR + 0.0722} rough={0.45} />
      <Face t={smFace} w={0.044} h={0.1} x={X(50) + 0.185} y={cy} z={ZR + 0.0722} rough={0.45} />
      <Face t={pcbFace} w={0.168} h={0.138} x={X(511)} y={Y(327)} z={ZP + 0.0269} rough={0.3} />
      {/* RUN-LED */}
      <mesh position={[X(50) + 0.056 - 0.047, cy - 0.003, ZR + 0.0728]}>
        <boxGeometry args={[0.004, 0.0025, 0.001]} />
        <meshStandardMaterial color="#5dff7a" emissive="#3dff60" emissiveIntensity={2.5} />
      </mesh>
      {[0, 1, 2, 3, 4].map((i) => (
        <mesh key={i} position={[X(440 + i * 34), Y(298), ZP + 0.0285]}>
          <sphereGeometry args={[0.0028, 14, 10, 0, Math.PI * 2, 0, Math.PI / 2]} />
          <meshPhysicalMaterial color="#14532d" roughness={0.15} transmission={0} clearcoat={1} />
        </mesh>
      ))}
    </group>
  );
};

// ------------------------------------------------------------------ Bedieneinheit
const BED_C = new THREE.Vector3(X(800), Y(370), 0);
export const BEDPE = () => new THREE.Vector3(X(894), Y(552), 0.09 + 0.016);
const Panel: React.FC = () => {
  const geo = useMemo(() => {
    const P = newParts();
    P.grey.push(bx(0.206, 0.375, 0.09, BED_C.x, BED_C.y, 0.045, 0.008));
    [[-1, -1], [1, -1], [1, 1], [-1, 1]].forEach(([a, b]) => P.greyMid.push(cz(0.004, 0.002, BED_C.x + a * 0.09, BED_C.y + b * 0.172, 0.0905, 14)));
    const btn = (px: number, py: number, kind: "push" | "lamp" | "sel", col?: keyof Parts) => {
      const x = X(px), y = Y(py);
      P.metal.push(cz(0.0148, 0.005, x, y, 0.0925, 32));
      if (kind === "push") P[col!].push(cz(0.0118, 0.006, x, y, 0.097, 32));
      if (kind === "sel") {
        P.black.push(cz(0.0125, 0.008, x, y, 0.098, 32));
        const g = bx(0.006, 0.024, 0.008, 0, 0, 0, 0.002);
        g.rotateZ(-0.6);
        g.translate(x, y, 0.104);
        P.black.push(g);
      }
    };
    btn(748, 250, "sel");
    btn(852, 250, "lamp");
    btn(748, 350, "push", "anth");
    btn(852, 350, "lamp");
    btn(748, 450, "push", "black");
    btn(852, 450, "push", "anth");
    // PE-Bolzen
    const pe = BEDPE();
    P.metal.push(cz(0.0032, 0.016, pe.x, pe.y, 0.098, 14));
    P.metal.push(cz(0.0058, 0.004, pe.x, pe.y, 0.099, 6));
    P.metal.push(cz(0.0062, 0.0008, pe.x, pe.y, 0.0965, 20));
    return Object.fromEntries(Object.entries(P).map(([k, v]) => [k, merge(v)])) as Record<keyof Parts, G>;
  }, []);
  const coloured = useMemo(() => {
    const m = (c: string) => phys({ color: c, roughness: 0.25, clearcoat: 0.8 });
    return { blue: m("#1d5fd1"), green: m("#16a34a") };
  }, []);
  const lamps = useMemo(() => [["#f3f1e8", 250], ["#c81e1e", 350]].map(([c, py]) => [phys({ color: c as string, roughness: 0.12, clearcoat: 1, sheen: 0.3 }), py] as const), []);
  const lab = (t: string, px: number, py: number) => (
    <Face key={t} t={labelTex([{ t, s: 46, b: 800 }], 256, 72, "#f7f7f2", "bed" + t)} w={0.04} h={0.0112} x={X(px)} y={Y(py)} z={0.0905} />
  );
  const pe = BEDPE();
  const peWire = useMemo(() => tube([new THREE.Vector3(pe.x, pe.y, 0.096), new THREE.Vector3(pe.x - 0.01, pe.y - 0.004, 0.098), new THREE.Vector3(pe.x - 0.03, pe.y - 0.02, 0.092), new THREE.Vector3(pe.x - 0.04, Y(570), 0.07)], 0.0016), []);
  const cable = useMemo(() => tube([new THREE.Vector3(X(600), Y(606) + 0.0, 0.022), new THREE.Vector3(X(640), Y(600), 0.03), new THREE.Vector3(X(668), Y(560), 0.05), new THREE.Vector3(X(690), Y(530), 0.045), new THREE.Vector3(X(700), Y(525), 0.03)], 0.0042, 40), []);
  return (
    <group>
      {Object.entries(geo).map(([k, g]) => <M key={k} g={g} m={k as any} />)}
      <mesh position={[X(748), Y(350), 0.097]} rotation={[Math.PI / 2, 0, 0]} material={coloured.blue} castShadow><cylinderGeometry args={[0.0118, 0.0118, 0.006, 32]} /></mesh>
      <mesh position={[X(852), Y(450), 0.097]} rotation={[Math.PI / 2, 0, 0]} material={coloured.green} castShadow><cylinderGeometry args={[0.0118, 0.0118, 0.006, 32]} /></mesh>
      {lamps.map(([m, py], i) => (
        <mesh key={i} position={[X(852), Y(py as number), 0.094]} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.75, 1]} material={m as THREE.Material}>
          <sphereGeometry args={[0.0115, 28, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        </mesh>
      ))}
      {lab("S1 EIN/AUS", 748, 292)}
      {lab("P1 EIN", 852, 292)}
      {lab("S2 Quitt.", 748, 392)}
      {lab("P2 Störung", 852, 392)}
      {lab("S3 Rechts", 748, 492)}
      {lab("S4 Start", 852, 492)}
      <Face t={labelTex([{ t: "Bedieneinheit  -S", s: 40, b: 800 }], 512, 72, "#f7f7f2")} w={0.11} h={0.0155} x={X(800)} y={Y(196)} z={0.0905} />
      <M g={peWire} m={wirePE()} />
      <M g={cable} m="black" />
    </group>
  );
};

// ------------------------------------------------------------------ PE-Bolzen der Montageplatte
export const PLATE_PE = () => new THREE.Vector3(X(616), Y(616), ZP + 0.019);
const PlatePE: React.FC = () => {
  const g = useMemo(() => {
    const p = PLATE_PE();
    return {
      m: merge([cz(0.0032, 0.019, p.x, p.y, ZP + 0.0095, 14), cz(0.0062, 0.0045, p.x, p.y, ZP + 0.0085, 6), cz(0.0075, 0.001, p.x, p.y, ZP + 0.0055, 24), cz(0.0062, 0.0045, p.x, p.y, ZP + 0.0024, 6)]),
      lug: merge([cz(0.0068, 0.0012, p.x, p.y, ZP + 0.0066, 24)]),
      w: tube([new THREE.Vector3(p.x - 0.006, p.y, ZP + 0.0067), new THREE.Vector3(p.x - 0.02, p.y + 0.002, ZP + 0.008), new THREE.Vector3(p.x - 0.04, Y(606) - 0.01, 0.015), new THREE.Vector3(p.x - 0.045, Y(606) + 0.006, 0.02)], 0.0018),
    };
  }, []);
  const p = PLATE_PE();
  return (
    <group>
      <M g={g.m} m="zinc" />
      <M g={g.lug} m="copper" />
      <M g={g.w} m={wirePE()} />
      <Face t={faceTex("pesym", 128, 128, (c) => {
        c.fillStyle = "#f2c200"; c.beginPath(); c.arc(64, 64, 62, 0, Math.PI * 2); c.fill();
        c.strokeStyle = "#111"; c.lineWidth = 8; c.beginPath(); c.arc(64, 64, 50, 0, Math.PI * 2); c.stroke();
        c.beginPath(); c.moveTo(64, 26); c.lineTo(64, 62); c.moveTo(36, 62); c.lineTo(92, 62); c.moveTo(46, 76); c.lineTo(82, 76); c.moveTo(56, 90); c.lineTo(72, 90); c.stroke();
      })} w={0.014} h={0.014} x={p.x + 0.0} y={p.y + 0.017} z={ZP} />
    </group>
  );
};

// ------------------------------------------------------------------ CEE-Stecker 16 A 5-polig
const CEE_C = new THREE.Vector3(X(151), Y(716), 0.0);
const CEE_FACE = 0.105;
export const CEE_PE = () => new THREE.Vector3(CEE_C.x, CEE_C.y + 0.0165, CEE_FACE + 0.017);
const Cee: React.FC<{ plugged: boolean }> = ({ plugged }) => {
  const g = useMemo(() => {
    const body: G[] = [], pins: G[] = [], dark: G[] = [];
    const c = CEE_C;
    body.push(cz(0.031, 0.06, c.x, c.y, 0.06, 40, 0.028));
    for (let i = 0; i < 10; i++) body.push(cz(0.0315, 0.002, c.x, c.y, 0.034 + i * 0.005, 40));
    body.push(cz(0.033, 0.018, c.x, c.y, 0.096, 44));
    body.push(cz(0.02, 0.025, c.x, c.y, 0.02, 24, 0.024));
    dark.push(cz(0.0285, 0.002, c.x, c.y, CEE_FACE - 0.012, 40));
    const ring = new THREE.TorusGeometry(0.0305, 0.002, 10, 48);
    ring.translate(c.x, c.y, CEE_FACE);
    body.push(ring);
    // Stifte: PE oben (größer), L1 L2 L3 N im Kreis
    pins.push(cz(0.0032, 0.03, c.x, c.y + 0.0165, CEE_FACE + 0.0, 18));
    [210, 270, 330, 30, 150].slice(0, 4).forEach((a, i) => {
      const r = (a * Math.PI) / 180;
      pins.push(cz(0.0025, 0.026, c.x + Math.cos(r - Math.PI / 2 + 0.3) * 0.0165, c.y + Math.sin(r - Math.PI / 2 + 0.3) * 0.0165, CEE_FACE - 0.002, 16));
      void i;
    });
    const cable = tube([new THREE.Vector3(c.x, c.y, 0.01), new THREE.Vector3(c.x - 0.01, c.y + 0.015, -0.004), new THREE.Vector3(X(100), Y(650), 0.004), new THREE.Vector3(X(100), Y(632) + 0.002, 0.018), new THREE.Vector3(X(100), Y(625), 0.02)], 0.0055, 40);
    return { body: merge(body), pins: merge(pins), dark: merge(dark), cable };
  }, []);
  const cpl = useMemo(() => {
    const c = CEE_C;
    return {
      b: merge([cz(0.0345, 0.07, c.x, c.y, CEE_FACE + 0.03, 44), cz(0.025, 0.04, c.x, c.y, CEE_FACE + 0.08, 24, 0.018)]),
      cable: tube([new THREE.Vector3(c.x, c.y, CEE_FACE + 0.09), new THREE.Vector3(c.x + 0.01, c.y - 0.01, CEE_FACE + 0.16), new THREE.Vector3(c.x + 0.05, 0.86, 0.32), new THREE.Vector3(c.x + 0.2, 0.86, 0.6)], 0.0055, 40),
    };
  }, []);
  return (
    <group>
      <M g={g.body} m="red" />
      <M g={g.pins} m="metal" />
      <M g={g.dark} m="anth" />
      <M g={g.cable} m="black" />
      {plugged ? (
        <>
          <M g={cpl.b} m="red" />
          <M g={cpl.cable} m="black" />
        </>
      ) : null}
      <Face t={labelTex([{ t: "16 A  6h  400 V", s: 30, b: 700, c: "#fff" }], 256, 48, "#c3261f", "cee")} w={0.04} h={0.0075} x={CEE_C.x} y={CEE_C.y - 0.022} z={0.088} />
    </group>
  );
};

// ------------------------------------------------------------------ Hutschienen, Platte, Rahmen
const Frame: React.FC = () => {
  const g = useMemo(() => {
    // 40er Aluprofil mit Nuten
    const s = new THREE.Shape();
    const a = 0.02, n = 0.004, d = 0.006;
    const pts: [number, number][] = [];
    const side = (rot: number) => {
      const P: [number, number][] = [[a, -a], [a, -n], [a - d, -n], [a - d, n], [a, n], [a, a]];
      P.forEach(([x, y]) => {
        const c = Math.cos(rot), si = Math.sin(rot);
        pts.push([x * c - y * si, x * si + y * c]);
      });
    };
    [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2].forEach(side);
    pts.forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
    s.closePath();
    const h = new THREE.Path();
    h.absarc(0, 0, 0.0035, 0, Math.PI * 2, true);
    s.holes.push(h);
    const prof = (len: number) => new THREE.ExtrudeGeometry(s, { depth: len, bevelEnabled: false, curveSegments: 12 });
    const out: G[] = [];
    [X(-27), X(666), X(949)].forEach((x) => {
      const p = prof(0.8);
      p.rotateX(-Math.PI / 2);
      p.translate(x, 0.87, -0.022);
      out.push(p);
    });
    [0.87 + 0.02, 1.67 - 0.02].forEach((y) => {
      const p = prof(X(949) - X(-27) + 0.04);
      p.rotateY(Math.PI / 2);
      p.translate(X(-27) - 0.02, y, -0.022);
      out.push(p);
    });
    // Füße
    out.push(bx(0.06, 0.02, 0.32, X(-27), 0.86, 0.06), bx(0.06, 0.02, 0.32, X(949), 0.86, 0.06));
    // Hutschienen 35 mm
    const rails: G[] = [];
    [126, 326, 526].forEach((py) => {
      const x0 = X(46), x1 = X(606), cx = (x0 + x1) / 2, L = x1 - x0, cy = Y(py);
      rails.push(bx(L, 0.025, 0.001, cx, cy, ZP + 0.0005));
      [1, -1].forEach((sg) => {
        rails.push(bx(L, 0.001, 0.0075, cx, cy + sg * 0.0125, ZP + 0.00375));
        rails.push(bx(L, 0.005, 0.001, cx, cy + sg * 0.015, ZP + 0.0075));
      });
    });
    return { alu: merge(out), rails: merge(rails) };
  }, []);
  return (
    <group>
      <M g={g.alu} m="alu" />
      <M g={g.rails} m="zinc" />
      <mesh position={[X(320), Y(320), ZP / 2]} castShadow receiveShadow material={MAT().plate}>
        <boxGeometry args={[0.6, 0.6, ZP]} />
      </mesh>
    </group>
  );
};

export const Gestell3D: React.FC<{ st: Record<string, number> }> = ({ st }) => {
  const d = ductGeo();
  return (
    <group>
      <Frame />
      <M g={d.base} m="duct" />
      <M g={d.cover} m="duct" />
      <Devices st={st} />
      <Terminals />
      <Plc />
      <Panel />
      <PlatePE />
      <Cee plugged={!!st.cee} />
      <Plug on={!!st.plug} />
    </group>
  );
};

// Schukostecker vom Netzkabel des Fluke in X5
export const X5_C = () => new THREE.Vector3(X(528), Y(128), ZP);
export const X5_PE = () => new THREE.Vector3(X(528), Y(128) + 0.0165, ZP + 0.036);
const Plug: React.FC<{ on: boolean }> = ({ on }) => {
  const g = useMemo(() => {
    const c = X5_C();
    return merge([cz(0.0195, 0.018, c.x, c.y, ZP + 0.036, 36), bx(0.034, 0.05, 0.032, c.x, c.y - 0.004, ZP + 0.06, 0.008), cz(0.006, 0.02, c.x, c.y - 0.03, ZP + 0.06, 16)]);
  }, []);
  return on ? <M g={g} m="black" /> : null;
};
export const PLUG_CABLE_START = () => new THREE.Vector3(X(528), Y(128) - 0.035, ZP + 0.062);
