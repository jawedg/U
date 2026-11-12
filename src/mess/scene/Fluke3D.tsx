// Fluke 1664 FC als 3D-Modell: gelbes Holster, Frontplatte mit Aufdruck, Segment-LCD (Canvas, jedes Bild neu),
// echter Drehschalter, F1–F4, TEST mit Touchpad, Buchsen L/PE/N mit gesteckten Messleitungen.
import React, { useMemo } from "react";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { FONT, canvasTex, once, phys, rr } from "./tex";
import { FlukeState } from "../Fluke";

// Layout in SVG-Einheiten (560 × 840) wie Fluke.tsx
export const FW = 0.112, FH = 0.168;
const U = FW / 560;
export const fx = (sx: number) => (sx - 280) * U;
export const fy = (sy: number) => -(sy - 420) * U;
const FACE_Z = 0.0035;

export const DIAL = [["V", "V"], ["RISO", "R ISO"], ["RLO", "R LO"], ["ZI", "Zi"], ["ZIHI", "Zi HI"], ["DT", "ΔT"], ["IDN", "IΔN"], ["PHASE", "⟳"], ["RE", "RE"], ["AUTO", "AUTO"]];
export const dialAng = (i: number) => 210 - (i * 240) / (DIAL.length - 1);
const DCX = 280, DCY = 640;

// Buchsen (lokal), für Messleitungen
export const JACKS: Record<string, THREE.Vector3> = {
  r: new THREE.Vector3(fx(200), FH / 2 + 0.024, -0.012),
  g: new THREE.Vector3(fx(280), FH / 2 + 0.024, -0.012),
  b: new THREE.Vector3(fx(360), FH / 2 + 0.024, -0.012),
};

// ------------------------------------------------------------------ Frontplatte (statisch)
const faceTexture = () =>
  once("flukeFace", () =>
    canvasTex(1120, 1680, (c) => {
      const S = 2;
      c.scale(S, S);
      const g = c.createLinearGradient(0, 0, 0, 840);
      g.addColorStop(0, "#353a3f");
      g.addColorStop(1, "#24282c");
      c.fillStyle = g;
      c.fillRect(0, 0, 560, 840);
      // feine Struktur
      for (let i = 0; i < 4000; i++) {
        c.fillStyle = `rgba(255,255,255,${Math.abs(Math.sin(i * 12.9898) * 0.03)})`;
        c.fillRect((i * 37.1) % 560, (i * 91.7) % 840, 1, 1);
      }
      c.fillStyle = "#f4c20d";
      c.font = `900 30px ${FONT}`;
      c.fillText("FLUKE", 34, 52);
      c.fillStyle = "#cbd5e1";
      c.font = `700 20px ${FONT}`;
      c.fillText("1664 FC  MULTIFUNCTION INSTALLATION TESTER", 136, 50);
      // Warndreieck
      c.strokeStyle = "#e2e8f0";
      c.lineWidth = 3;
      c.beginPath();
      c.moveTo(85, 86);
      c.lineTo(112, 134);
      c.lineTo(58, 134);
      c.closePath();
      c.stroke();
      c.fillStyle = "#e2e8f0";
      c.font = `900 26px ${FONT}`;
      c.textAlign = "center";
      c.fillText("!", 85, 128);
      // Touchpad (Metallfläche)
      const tp = c.createLinearGradient(25, 160, 145, 360);
      tp.addColorStop(0, "#c3c9cf");
      tp.addColorStop(0.5, "#8d959c");
      tp.addColorStop(1, "#b5bcc2");
      c.fillStyle = tp;
      c.beginPath();
      c.ellipse(85, 262, 60, 100, 0, 0, Math.PI * 2);
      c.fill();
      c.strokeStyle = "#1b1e21";
      c.lineWidth = 3;
      c.stroke();
      // LCD-Rahmen
      c.fillStyle = "#15181b";
      rr(c, 150, 76, 300, 320, 18);
      c.fill();
      // MEMORY / Pfeile
      c.fillStyle = "#cbd5e1";
      c.font = `700 15px ${FONT}`;
      c.fillText("MEMORY", 245, 462);
      c.fillText("▲  ▼", 345, 462);
      // Skala Drehschalter
      DIAL.forEach(([, label], i) => {
        const r = (dialAng(i) * Math.PI) / 180;
        c.strokeStyle = "#94a3b8";
        c.lineWidth = 4;
        c.beginPath();
        c.moveTo(DCX + Math.cos(r) * 128, DCY - Math.sin(r) * 128);
        c.lineTo(DCX + Math.cos(r) * 146, DCY - Math.sin(r) * 146);
        c.stroke();
        c.fillStyle = "#e5e7eb";
        c.font = `800 25px ${FONT}`;
        c.fillText(label, DCX + Math.cos(r) * 188, DCY - Math.sin(r) * 188 + 9);
      });
      c.strokeStyle = "#f4c20d";
      c.lineWidth = 5;
      c.beginPath();
      c.arc(DCX, DCY, 122, 0, Math.PI * 2);
      c.stroke();
      c.fillStyle = "#e5e7eb";
      c.font = `700 14px ${FONT}`;
      c.fillText("CAT III 600V  CAT IV 300V", 280, 826);
    }),
  );

// ------------------------------------------------------------------ 7-Segment
const SEG: Record<string, string> = { "0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcfgd", "-": "g", " ": "", L: "fed", P: "abfge", E: "afged", O: "abcdef" };
const drawSeg = (c: CanvasRenderingContext2D, ch: string, x: number, y: number, h: number, on: boolean) => {
  const w = h * 0.52, t = h * 0.12, sk = h * 0.09;
  const segs = on ? SEG[ch] ?? "" : "abcdefg";
  const P = (px: number, py: number): [number, number] => [x + px + (1 - py / h) * sk, y - h + py];
  const hseg = (py: number) => [P(t * 0.6, py), P(t * 1.1, py - t / 2), P(w - t * 1.1, py - t / 2), P(w - t * 0.6, py), P(w - t * 1.1, py + t / 2), P(t * 1.1, py + t / 2)];
  const vseg = (px: number, y0: number, y1: number) => [P(px, y0 + t * 0.6), P(px + t / 2, y0 + t * 1.1), P(px + t / 2, y1 - t * 1.1), P(px, y1 - t * 0.6), P(px - t / 2, y1 - t * 1.1), P(px - t / 2, y0 + t * 1.1)];
  const shapes: Record<string, [number, number][]> = {
    a: hseg(t / 2), g: hseg(h / 2), d: hseg(h - t / 2),
    f: vseg(t / 2, 0, h / 2), b: vseg(w - t / 2, 0, h / 2), e: vseg(t / 2, h / 2, h), c: vseg(w - t / 2, h / 2, h),
  };
  for (const k of segs) {
    const pts = shapes[k];
    c.beginPath();
    pts.forEach(([px, py], i) => (i ? c.lineTo(px, py) : c.moveTo(px, py)));
    c.closePath();
    c.fill();
  }
  return w + h * 0.16;
};
// Zahlenstring rechtsbündig bei xr
const drawNum = (c: CanvasRenderingContext2D, s: string, xr: number, y: number, h: number, ghostN = 0) => {
  const chars: { ch: string; dp: boolean }[] = [];
  for (const ch of s) {
    if (ch === "." || ch === ",") {
      if (chars.length) chars[chars.length - 1].dp = true;
    } else chars.push({ ch, dp: false });
  }
  const adv = h * 0.52 + h * 0.16;
  const n = Math.max(ghostN, chars.length);
  // Geister-Segmente
  c.fillStyle = "rgba(20,30,20,0.055)";
  for (let i = 0; i < n; i++) drawSeg(c, "8", xr - (n - i) * adv, y, h, false);
  c.fillStyle = "#121a13";
  chars.forEach((d, i) => {
    const x = xr - (chars.length - i) * adv;
    drawSeg(c, d.ch, x, y, h, true);
    if (d.dp) {
      c.beginPath();
      c.arc(x + h * 0.6, y - h * 0.04, h * 0.065, 0, Math.PI * 2);
      c.fill();
    }
  });
  return xr - chars.length * adv;
};

const drawLcd = (c: CanvasRenderingContext2D, st: FlukeState, t: number) => {
  const W = 560, H = 600;
  const g = c.createLinearGradient(0, 0, W, H);
  g.addColorStop(0, "#c3cfb7");
  g.addColorStop(1, "#aebca5");
  c.fillStyle = g;
  c.fillRect(0, 0, W, H);
  const sh = c.createLinearGradient(0, 0, 0, 40);
  sh.addColorStop(0, "rgba(0,0,0,0.22)");
  sh.addColorStop(1, "rgba(0,0,0,0)");
  c.fillStyle = sh;
  c.fillRect(0, 0, W, 40);
  const ink = "#121a13";
  c.fillStyle = ink;
  c.textBaseline = "alphabetic";
  c.font = `800 40px ${FONT}`;
  c.textAlign = "left";
  const pair = st.F1 && /L-PE|L-N|N-PE/.test(st.F1) ? st.F1 : st.fn === "PHASE" ? "L1 L2 L3" : "";
  c.fillText(pair, 24, 62);
  c.textAlign = "right";
  c.fillText(st.fn === "DT" ? "ΔT" : st.fn === "PHASE" ? "⟳" : st.fn === "RISO" ? "R ISO" : st.fn === "RLO" ? "R LO" : "V", 400, 62);
  c.textAlign = "left";
  if (st.zero) c.fillText("ZERO", 24, 122);
  if (st.rcdok) {
    c.fillText("RCD", 24, 122);
    c.lineWidth = 7;
    c.strokeStyle = ink;
    c.beginPath();
    c.moveTo(118, 104);
    c.lineTo(132, 120);
    c.lineTo(160, 86);
    c.stroke();
  }
  // Hauptanzeige
  let prim = st.prim ?? "";
  if (prim === "…") prim = Math.floor(t * 4) % 2 ? "- - -" : "";
  prim = prim.replace(/ /g, "");
  const xEnd = 372;
  drawNum(c, prim, xEnd, 340, 150, 4);
  c.font = `800 52px ${FONT}`;
  c.textAlign = "left";
  c.fillText(st.unit ?? "", xEnd + 8, 340);
  // Nebenanzeige
  const sec = st.sec ?? "";
  const m = sec.match(/^(\D*?)\s*([-\d.,]+)\s*(.*)$/);
  if (m) {
    const x0 = drawNum(c, m[2], 372, 520, 64, 4);
    c.font = `800 34px ${FONT}`;
    c.textAlign = "left";
    c.fillText(m[3], 382, 520);
    c.textAlign = "right";
    c.fillText(m[1].replace("_", ""), x0 - 10, 520);
  } else {
    c.fillStyle = "rgba(20,30,20,0.055)";
    drawNum(c, "", 372, 520, 64, 4);
  }
  // Belegung F1–F4 am rechten Rand
  c.fillStyle = ink;
  c.textAlign = "right";
  c.font = `800 34px ${FONT}`;
  (["F1", "F2", "F3", "F4"] as const).forEach((k, i) => {
    const v = (st as any)[k] ?? "";
    c.fillText(v, 548, (130 + i * 70 - 86) * 2 + 26);
  });
  // Batterie-Symbol
  c.strokeStyle = ink;
  c.lineWidth = 4;
  c.strokeRect(470, 30, 52, 26);
  c.fillRect(522, 37, 6, 12);
  c.fillRect(476, 36, 36, 14);
};

// Hervorhebungen (orange Rahmen)
const drawHl = (c: CanvasRenderingContext2D, hl: string) => {
  c.clearRect(0, 0, 1120, 1840);
  c.save();
  c.scale(2, 2);
  c.translate(0, 80);
  c.strokeStyle = "#ff7a1a";
  c.lineWidth = 9;
  const R = (x: number, y: number, w: number, h: number) => (rr(c, x, y, w, h, 18), c.stroke());
  if (hl === "dial") R(DCX - 232, DCY - 232, 464, 410);
  if (hl === "fkeys") R(446, 88, 88, 294);
  if (hl === "test") R(15, 150, 140, 230);
  if (hl === "warn") R(46, 78, 78, 68);
  if (hl === "leads") R(170, -72, 220, 86);
  c.restore();
};

const rbox = (w: number, h: number, d: number, r: number) => new RoundedBoxGeometry(w, h, d, 3, r);

export const Fluke3D: React.FC<{ st: FlukeState; press?: string; pressA: number; dialA: number; prevDial?: string; t: number; leads: string[] }> = ({ st, press, pressA, dialA, prevDial, t, leads }) => {
  const res = useMemo(() => {
    const lcdCanvas = document.createElement("canvas");
    lcdCanvas.width = 560;
    lcdCanvas.height = 600;
    const lcd = new THREE.CanvasTexture(lcdCanvas);
    lcd.colorSpace = THREE.SRGBColorSpace;
    lcd.anisotropy = 8;
    const hlCanvas = document.createElement("canvas");
    hlCanvas.width = 1120;
    hlCanvas.height = 1840;
    const hl = new THREE.CanvasTexture(hlCanvas);
    hl.colorSpace = THREE.SRGBColorSpace;
    // Holster-Rahmen mit Ausschnitt
    const sh = new THREE.Shape();
    const W = FW + 0.02, H = FH + 0.022, R = 0.016;
    sh.moveTo(-W / 2 + R, -H / 2);
    sh.lineTo(W / 2 - R, -H / 2);
    sh.quadraticCurveTo(W / 2, -H / 2, W / 2, -H / 2 + R);
    sh.lineTo(W / 2, H / 2 - R);
    sh.quadraticCurveTo(W / 2, H / 2, W / 2 - R, H / 2);
    sh.lineTo(-W / 2 + R, H / 2);
    sh.quadraticCurveTo(-W / 2, H / 2, -W / 2, H / 2 - R);
    sh.lineTo(-W / 2, -H / 2 + R);
    sh.quadraticCurveTo(-W / 2, -H / 2, -W / 2 + R, -H / 2);
    const hole = new THREE.Path();
    const w = FW - 0.002, h = FH - 0.002, r = 0.009;
    hole.moveTo(-w / 2 + r, -h / 2);
    hole.quadraticCurveTo(-w / 2, -h / 2, -w / 2, -h / 2 + r);
    hole.lineTo(-w / 2, h / 2 - r);
    hole.quadraticCurveTo(-w / 2, h / 2, -w / 2 + r, h / 2);
    hole.lineTo(w / 2 - r, h / 2);
    hole.quadraticCurveTo(w / 2, h / 2, w / 2, h / 2 - r);
    hole.lineTo(w / 2, -h / 2 + r);
    hole.quadraticCurveTo(w / 2, -h / 2, w / 2 - r, -h / 2);
    hole.closePath();
    sh.holes.push(hole);
    const rim = new THREE.ExtrudeGeometry(sh, { depth: 0.008, bevelEnabled: true, bevelThickness: 0.003, bevelSize: 0.003, bevelSegments: 4, curveSegments: 10 });
    rim.translate(0, 0, 0.0005);
    const mats = {
      holster: phys({ color: "#f1c100", roughness: 0.72, sheen: 0.4, sheenColor: new THREE.Color("#fff3b0") }),
      body: phys({ color: "#2b2f33", roughness: 0.5 }),
      face: new THREE.MeshStandardMaterial({ map: faceTexture(), roughness: 0.55 }),
      lcd: new THREE.MeshStandardMaterial({ map: lcd, roughness: 0.6, emissive: new THREE.Color("#ffffff"), emissiveMap: lcd, emissiveIntensity: 0.22 }),
      glass: phys({ color: "#ffffff", roughness: 0.04, metalness: 0, transparent: true, opacity: 0.12, clearcoat: 1, envMapIntensity: 1.4 }),
      knob: phys({ color: "#3b4148", roughness: 0.45, clearcoat: 0.3 }),
      knobBase: phys({ color: "#1c1f23", roughness: 0.6 }),
      key: phys({ color: "#8fb7cf", roughness: 0.45, clearcoat: 0.2 }),
      test: phys({ color: "#e3e5e8", roughness: 0.45, clearcoat: 0.3 }),
      yel: new THREE.MeshStandardMaterial({ color: "#ffd166", roughness: 0.4 }),
      hl: new THREE.MeshBasicMaterial({ map: hl, transparent: true, toneMapped: false, depthWrite: false }),
      jackR: phys({ color: "#c62828", roughness: 0.4 }),
      jackG: phys({ color: "#1f8f3a", roughness: 0.4 }),
      jackB: phys({ color: "#1f5fbf", roughness: 0.4 }),
      dark: new THREE.MeshStandardMaterial({ color: "#0b0c0d", roughness: 0.8 }),
      gray: phys({ color: "#59616a", roughness: 0.5 }),
    };
    const lbl = (txt: string, w: number, h: number, fs: number) => {
      const tt = canvasTex(256, 200, (c) => {
        c.fillStyle = "#0f172a";
        c.font = `900 ${fs}px ${FONT}`;
        c.textAlign = "center";
        c.textBaseline = "middle";
        c.fillText(txt, 128, 104);
      });
      return new THREE.MeshBasicMaterial({ map: tt, transparent: true, depthWrite: false });
    };
    return {
      lcdCanvas, lcd, hlCanvas, hl, mats, rim,
      body: rbox(FW + 0.016, FH + 0.018, 0.05, 0.013),
      key: rbox(64 * U, 50 * U, 0.005, 0.0018),
      knobBar: rbox(54 * U, 236 * U, 0.013, 0.0045),
      keyLbl: ["F1", "F2", "F3", "F4"].map((k) => lbl(k, 64 * U, 50 * U, 110)),
      testLbl: lbl("TEST", 0, 0, 62),
    };
  }, []);

  // LCD und Hervorhebung jedes Bild neu zeichnen
  // nur neu zeichnen, wenn sich der Inhalt ändert
  const lcdKey = JSON.stringify([st.F1, st.F2, st.F3, st.F4, st.fn, st.zero, st.rcdok, st.prim === "…" ? "…" + (Math.floor(t * 4) % 2) : st.prim, st.unit, st.sec]);
  const R = res as any;
  if (R.lcdKey !== lcdKey) {
    drawLcd(res.lcdCanvas.getContext("2d")!, st, t);
    res.lcd.needsUpdate = true;
    R.lcdKey = lcdKey;
  }
  if (R.hlKey !== (st.hl ?? "")) {
    drawHl(res.hlCanvas.getContext("2d")!, st.hl ?? "");
    res.hl.needsUpdate = true;
    R.hlKey = st.hl ?? "";
  }
  res.mats.hl.opacity = st.hl ? 0.65 + 0.35 * Math.sin(t * 6) : 0;

  const di = Math.max(0, DIAL.findIndex((d) => d[0] === (st.dial ?? "V")));
  const pi = Math.max(0, DIAL.findIndex((d) => d[0] === (prevDial ?? st.dial ?? "V")));
  const ang = dialAng(pi) + (dialAng(di) - dialAng(pi)) * dialA;
  const glow = (k: string) => (press === k ? pressA : 0) + (k === "F2" && st.hold ? 0.6 + 0.4 * Math.sin(t * 8) : 0);
  const keyMat = (k: string) => {
    const g = glow(k);
    if (g <= 0.01) return res.mats.key;
    const m = res.mats.key.clone();
    m.emissive = new THREE.Color("#ff8a1a");
    m.emissiveIntensity = 1.6 * Math.min(1, g);
    return m;
  };
  const tg = glow("TEST");
  const testMat = tg > 0.01 ? (() => { const m = res.mats.test.clone(); m.emissive = new THREE.Color("#ffb347"); m.emissiveIntensity = 1.2 * Math.min(1, tg); return m; })() : res.mats.test;

  return (
    <group>
      <mesh geometry={res.body} material={res.mats.holster} position={[0, 0, -0.022]} castShadow receiveShadow />
      <mesh geometry={res.rim} material={res.mats.holster} castShadow receiveShadow />
      <mesh material={res.mats.face} position={[0, 0, FACE_Z]} receiveShadow>
        <planeGeometry args={[FW, FH]} />
      </mesh>
      {/* LCD + Glas */}
      <mesh material={res.mats.lcd} position={[fx(300), fy(236), FACE_Z + 0.0002]}>
        <planeGeometry args={[280 * U, 300 * U]} />
      </mesh>
      <mesh material={res.mats.glass} position={[fx(300), fy(236), FACE_Z + 0.0012]}>
        <planeGeometry args={[296 * U, 316 * U]} />
      </mesh>
      {/* F1–F4 */}
      {["F1", "F2", "F3", "F4"].map((k, i) => {
        const dz = glow(k) > 0.2 ? -0.0013 : 0;
        return (
          <group key={k} position={[fx(490), fy(125 + i * 70), FACE_Z + 0.0025 + dz]}>
            <mesh geometry={res.key} material={keyMat(k)} castShadow />
            <mesh material={res.keyLbl[i]} position={[0, 0, 0.00255]}>
              <planeGeometry args={[64 * U, 50 * U]} />
            </mesh>
          </group>
        );
      })}
      {/* TEST */}
      <group position={[fx(85), fy(262), FACE_Z + 0.003 - (tg > 0.2 ? 0.0016 : 0)]}>
        <mesh rotation={[Math.PI / 2, 0, 0]} material={testMat} castShadow>
          <cylinderGeometry args={[44 * U, 46 * U, 0.006, 40]} />
        </mesh>
        <mesh material={res.testLbl} position={[0, 0, 0.0031]}>
          <planeGeometry args={[88 * U, 70 * U]} />
        </mesh>
      </group>
      {/* MEMORY-Tasten */}
      <mesh position={[fx(245), fy(422), FACE_Z + 0.0015]} material={res.mats.gray}>
        <boxGeometry args={[106 * U, 30 * U, 0.003]} />
      </mesh>
      <mesh position={[fx(345), fy(422), FACE_Z + 0.0015]} material={res.mats.gray}>
        <boxGeometry args={[50 * U, 30 * U, 0.003]} />
      </mesh>
      {/* Drehschalter */}
      <mesh position={[fx(DCX), fy(DCY), FACE_Z + 0.002]} rotation={[Math.PI / 2, 0, 0]} material={res.mats.knobBase}>
        <cylinderGeometry args={[118 * U, 120 * U, 0.004, 64]} />
      </mesh>
      <group position={[fx(DCX), fy(DCY), FACE_Z + 0.009]} rotation={[0, 0, ((ang - 90) * Math.PI) / 180]}>
        <mesh geometry={res.knobBar} material={res.mats.knob} castShadow />
        <mesh position={[0, 0, -0.002]} rotation={[Math.PI / 2, 0, 0]} material={res.mats.knob}>
          <cylinderGeometry args={[60 * U, 70 * U, 0.008, 40]} />
        </mesh>
        <mesh position={[0, 92 * U, 0.0066]} material={res.mats.yel}>
          <boxGeometry args={[14 * U, 34 * U, 0.0006]} />
        </mesh>
      </group>
      {/* Buchsen oben + gesteckte Leitungen */}
      {(["r", "g", "b"] as const).map((k) => {
        const p = JACKS[k];
        const m = k === "r" ? res.mats.jackR : k === "g" ? res.mats.jackG : res.mats.jackB;
        return (
          <group key={k} position={[p.x, FH / 2 + 0.011, p.z]}>
            <mesh material={res.mats.dark}>
              <cylinderGeometry args={[0.0058, 0.0058, 0.002, 24]} />
            </mesh>
            {leads.includes(k) ? (
              <mesh position={[0, 0.007, 0]} material={m} castShadow>
                <cylinderGeometry args={[0.0042, 0.0052, 0.016, 20]} />
              </mesh>
            ) : null}
          </group>
        );
      })}
      {/* Hervorhebung */}
      <mesh material={res.mats.hl} position={[0, 40 * U, FACE_Z + 0.014]} renderOrder={10}>
        <planeGeometry args={[FW, 920 * U]} />
      </mesh>
    </group>
  );
};
