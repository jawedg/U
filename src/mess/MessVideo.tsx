// POV-Video (3D): VDE-Messungen am Prüfungsgestell mit dem Fluke 1664 FC.
// Eine einzige 3D-Szene für das ganze Video (Kamera = deine Augen), Overlays: Fluke in der Hand, Hinweise, Protokoll, Untertitel.
import React, { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, Audio, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { DATA, cueFn, durF, info, lead } from "../lern/LernVideo";
import { BOX, GH, GW, PT } from "../pruef/Gestell";
import { Fill, Protocol, Sub } from "../pruef/PruefVideo";
import { Fluke, FlukeState } from "./Fluke";

const KB = 8;
const FPS = 25;
const W = 1920, H = 1080;
const ORANGE = "#f26b1d";
const K = 0.9 / GW; // Meter pro Zeichnungs-Pixel
const CY = 1.25; // Höhe der Gestell-Mitte (m)
const ISO_VALS = ["620 MΩ", "710 MΩ", "655 MΩ", "580 MΩ", "690 MΩ", "742 MΩ", "605 MΩ", "630 MΩ", "668 MΩ", "590 MΩ"];

// Tiefe der Bauteile vor der Montageplatte (m)
const DEPTH: Record<string, number> = { F3: 0.075, F1: 0.075, F2: 0.075, T1: 0.06, F4: 0.085, Q1: 0.08, Q2: 0.08, X5: 0.05, SPS: 0.075, X10: 0.03, X1: 0.05, X2: 0.05, X3: 0.05, X4: 0.05, BED: 0.09, CEE: 0.035, PLATTE: 0.012 };
const DUCTS: [number, number, number, number][] = [14, 214, 414, 606].map((y) => [14, y, 612, 26]);
const w3 = (px: number, py: number, z = 0): THREE.Vector3 => new THREE.Vector3((px - GW / 2) * K, CY - (py - GH / 2) * K, z);
const depthAt = (px: number, py: number) => {
  let d = 0.004;
  for (const [id, b] of Object.entries(BOX)) if (px >= b[0] && px <= b[0] + b[2] && py >= b[1] && py <= b[1] + b[3]) d = Math.max(d, DEPTH[id] ?? 0);
  return d;
};
const P3 = (name: string): THREE.Vector3 => {
  if (name === "ALL") return new THREE.Vector3(-0.02, CY - 0.02, 0.04);
  if (name === "LOW") return w3(380, 640, 0.04);
  const b = BOX[name];
  if (!PT[name] && b) return w3(b[0] + b[2] / 2, b[1] + b[3] / 2, DEPTH[name] ?? 0.05);
  const p = PT[name] ?? [480, 380];
  return w3(p[0], p[1], depthAt(p[0], p[1]) + 0.003);
};

// ------------------------------------------------------------------ Zeitachse aus dem Skript
type Sc = { i: number; start: number; dur: number; v: any; cue: (c?: string) => number };
const useTimeline = () =>
  useMemo(() => {
    const { s } = DATA[KB];
    const scenes: Sc[] = [];
    let f = 0;
    s.sentences.forEach((sc, i) => {
      const d = durF(KB, i);
      scenes.push({ i, start: f, dur: d, v: sc.v, cue: cueFn(info(KB, i).words) });
      f += d;
    });
    const at = (S: Sc, c: string | number) =>
      typeof c === "number" ? S.start + c * FPS : c.startsWith("@") ? S.start + parseFloat(c.slice(1)) * S.dur : S.start + Math.max(0, S.cue(c)) * FPS;
    const cam: { f: number; tgt: string; d: number; yaw: number; pit: number }[] = [];
    const probes: Record<string, { f: number; pt: string }[]> = { r: [], g: [], b: [] };
    const fl: { f: number; p: FlukeState & { press?: string } }[] = [];
    const st: { f: number; p: Record<string, number> }[] = [];
    scenes.forEach((S) => {
      (S.v.cam ?? []).forEach((c: any) => cam.push({ f: at(S, c[0]), tgt: c[1], d: c[2], yaw: c[3], pit: c[4] }));
      (S.v.pr ?? []).forEach((c: any) => ["r", "g", "b"].forEach((k, j) => c[j + 1] !== null && c[j + 1] !== undefined && probes[k].push({ f: at(S, c[0]), pt: c[j + 1] })));
      (S.v.fl ?? []).forEach((c: any) => fl.push({ f: at(S, c[0]), p: c[1] }));
      (S.v.st ?? []).forEach((c: any) => st.push({ f: at(S, c[0]), p: c[1] }));
    });
    const sort = <T extends { f: number }>(a: T[]) => a.sort((x, y) => x.f - y.f);
    sort(cam); sort(fl); sort(st); Object.values(probes).forEach(sort);
    return { scenes, total: f, cam, probes, fl, st, at };
  }, []);

const ease = (x: number) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const camPose = (k: { tgt: string; d: number; yaw: number; pit: number }) => {
  const T = P3(k.tgt);
  const y = (k.yaw * Math.PI) / 180, p = (k.pit * Math.PI) / 180;
  return { pos: T.clone().add(new THREE.Vector3(Math.sin(y) * Math.cos(p) * k.d, Math.sin(p) * k.d, Math.cos(y) * Math.cos(p) * k.d)), tgt: T };
};

// ------------------------------------------------------------------ 3D-Welt
const Probe: React.FC<{ tip: THREE.Vector3; hand: THREE.Vector3; anchor: THREE.Vector3; color: string }> = ({ tip, hand, anchor, color }) => {
  const dir = hand.clone().sub(tip).normalize();
  const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir);
  const end = tip.clone().add(dir.clone().multiplyScalar(0.15));
  const mid = end.clone().lerp(anchor, 0.5).add(new THREE.Vector3(0, -0.12, 0));
  const curve = new THREE.CatmullRomCurve3([end, mid, anchor]);
  return (
    <group>
      <group position={tip} quaternion={q}>
        <mesh position={[0, 0.007, 0]}><cylinderGeometry args={[0.0012, 0.0006, 0.014, 8]} /><meshStandardMaterial color="#d1d5db" metalness={0.9} roughness={0.25} /></mesh>
        <mesh position={[0, 0.024, 0]}><cylinderGeometry args={[0.004, 0.0035, 0.022, 14]} /><meshStandardMaterial color={color} roughness={0.5} /></mesh>
        <mesh position={[0, 0.08, 0]}><cylinderGeometry args={[0.0065, 0.0058, 0.095, 16]} /><meshStandardMaterial color={color} roughness={0.45} /></mesh>
        <mesh position={[0, 0.05, 0]}><torusGeometry args={[0.0085, 0.0018, 8, 20]} /><meshStandardMaterial color={color} roughness={0.5} /></mesh>
      </group>
      <mesh><tubeGeometry args={[curve, 32, 0.0028, 8, false]} /><meshStandardMaterial color={color} roughness={0.55} /></mesh>
    </group>
  );
};

const Device: React.FC<{ id: string; tex: THREE.Texture }> = ({ id, tex }) => {
  const b = BOX[id];
  const d = DEPTH[id] ?? 0.04;
  const mats = useMemo(() => {
    const t = tex.clone();
    t.needsUpdate = true;
    t.repeat.set(b[2] / GW, b[3] / GH);
    t.offset.set(b[0] / GW, 1 - (b[1] + b[3]) / GH);
    const side = new THREE.MeshStandardMaterial({ color: id === "BED" ? "#2f3b4a" : id === "CEE" ? "#b91c1c" : "#cfd5db", roughness: 0.7 });
    const front = new THREE.MeshStandardMaterial({ map: t, roughness: 0.55, transparent: true, alphaTest: 0.3 });
    return [side, side, side, side, front, side];
  }, [tex, id]);
  const c = w3(b[0] + b[2] / 2, b[1] + b[3] / 2, d / 2);
  return (
    <mesh position={c} material={mats}>
      <boxGeometry args={[b[2] * K, b[3] * K, d]} />
    </mesh>
  );
};

// Textur außerhalb des 3D-Canvas laden; erst weiterrendern, wenn sie im Zustand angekommen ist
const useGestellTex = () => {
  const [tex, setTex] = useState<THREE.Texture | null>(null);
  const [handle] = useState(() => delayRender("Gestell-Textur"));
  useEffect(() => {
    new THREE.TextureLoader().load(
      staticFile("mess/gestell.png"),
      (t) => {
        t.colorSpace = THREE.SRGBColorSpace;
        t.anisotropy = 8;
        setTex(t);
      },
      undefined,
      () => continueRender(handle),
    );
  }, [handle]);
  useEffect(() => {
    if (tex) requestAnimationFrame(() => requestAnimationFrame(() => continueRender(handle)));
  }, [tex, handle]);
  return tex;
};

const World: React.FC<{ tl: ReturnType<typeof useTimeline>; tex: THREE.Texture | null }> = ({ tl, tex }) => {
  const frame = useCurrentFrame();
  const camera = useThree((s) => s.camera);

  // Kamera (deine Augen)
  const ks = tl.cam;
  let ki = 0;
  for (let i = 0; i < ks.length; i++) if (ks[i].f <= frame) ki = i;
  const cur = camPose(ks[ki]);
  const prev = camPose(ks[Math.max(0, ki - 1)]);
  const e = ease(Math.min(1, Math.max(0, (frame - ks[ki].f) / (1.4 * FPS))));
  const pos = prev.pos.clone().lerp(cur.pos, e);
  const tgt = prev.tgt.clone().lerp(cur.tgt, e);
  const tt = frame / FPS;
  pos.add(new THREE.Vector3(Math.sin(tt * 0.7) * 0.006, Math.sin(tt * 1.3) * 0.004, 0));
  tgt.add(new THREE.Vector3(Math.sin(tt * 0.5 + 1) * 0.004, Math.cos(tt * 0.9) * 0.003, 0));
  camera.position.copy(pos);
  camera.lookAt(tgt);
  camera.updateMatrixWorld();
  const fwd = tgt.clone().sub(pos).normalize();
  const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
  const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
  const rel = (f: number, r: number, u: number) => pos.clone().add(fwd.clone().multiplyScalar(f)).add(right.clone().multiplyScalar(r)).add(up.clone().multiplyScalar(u));
  const anchor = rel(0.3, -0.2, -0.32);

  // Zustände
  const stNow: Record<string, number> = {};
  tl.st.forEach((x) => x.f <= frame && Object.assign(stNow, x.p));

  // Messspitzen
  const probe = (key: string, color: string, side: number) => {
    const L = tl.probes[key];
    let i = -1;
    for (let j = 0; j < L.length; j++) if (L[j].f <= frame) i = j;
    const rest = rel(0.25, side * 0.08 - 0.05, -0.4);
    const ptPos = (n?: string) => (!n || n === "-" ? rest : P3(n));
    if (i < 0) return null;
    const to = ptPos(L[i].pt), from = i > 0 ? ptPos(L[i - 1].pt) : rest;
    const m = ease(Math.min(1, (frame - L[i].f) / (0.7 * FPS)));
    const tip = from.clone().lerp(to, m).add(new THREE.Vector3(0, 0, Math.sin(Math.PI * m) * 0.06));
    if (L[i].pt === "-" && m >= 1) return null;
    const hand = rel(0.15, side * 0.12, -0.18);
    return <Probe key={key} tip={tip} hand={hand} anchor={anchor} color={color} />;
  };

  const plateW = GW * K, plateH = GH * K;
  const plugPos = P3("X5");
  return (
    <>
      <color attach="background" args={["#d9dee3"]} />
      <ambientLight intensity={0.85} />
      <hemisphereLight args={["#ffffff", "#8a8f96", 0.6]} />
      <directionalLight position={[1.2, 3, 2.5]} intensity={1.9} />
      <pointLight position={[pos.x, pos.y + 0.2, pos.z]} intensity={0.8} distance={3} />
      {/* Raum */}
      <mesh position={[0, 1.4, -0.08]}><planeGeometry args={[8, 4]} /><meshStandardMaterial color="#e7eaee" roughness={0.95} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 1]}><planeGeometry args={[10, 10]} /><meshStandardMaterial color="#9ca3af" roughness={1} /></mesh>
      {/* Werkbank */}
      <mesh position={[0, 0.83, 0.35]}><boxGeometry args={[2.2, 0.04, 0.8]} /><meshStandardMaterial color="#b7895a" roughness={0.8} /></mesh>
      <mesh position={[0, 0.42, 0.35]}><boxGeometry args={[2.1, 0.8, 0.7]} /><meshStandardMaterial color="#64748b" roughness={0.8} /></mesh>
      {/* Prüfgestell: Alu-Profile */}
      {[-0.475, 0.175, 0.44].map((x) => (
        <mesh key={x} position={[x, 1.28, -0.02]}><boxGeometry args={[0.04, 0.9, 0.04]} /><meshStandardMaterial color="#cbd5e1" metalness={0.6} roughness={0.35} /></mesh>
      ))}
      <mesh position={[-0.02, 0.87, -0.02]}><boxGeometry args={[1.0, 0.04, 0.3]} /><meshStandardMaterial color="#cbd5e1" metalness={0.6} roughness={0.35} /></mesh>
      {tex ? (
        <>
          <mesh position={[0, CY, 0.001]}>
            <planeGeometry args={[plateW, plateH]} />
            <meshStandardMaterial map={tex} transparent alphaTest={0.3} roughness={0.6} />
          </mesh>
          {/* Kabelkanäle */}
          {DUCTS.map(([x, y, w, h], i) => {
            const t = tex.clone();
            t.needsUpdate = true;
            t.repeat.set(w / GW, h / GH);
            t.offset.set(x / GW, 1 - (y + h) / GH);
            return (
              <mesh key={i} position={w3(x + w / 2, y + h / 2, 0.03)}>
                <boxGeometry args={[w * K, h * K, 0.06]} />
                <meshStandardMaterial attach="material" map={t} roughness={0.7} />
              </mesh>
            );
          })}
          {Object.keys(DEPTH).filter((id) => id !== "PLATTE").map((id) => <Device key={id} id={id} tex={tex} />)}
        </>
      ) : null}
      {/* FI/LS-Hebel ausgelöst */}
      {stNow.F3trip ? (
        <>
          <mesh position={w3(76, 105, 0.077)}><boxGeometry args={[18 * K, 30 * K, 0.004]} /><meshStandardMaterial color="#f8fafc" /></mesh>
          <mesh position={w3(76, 131, 0.08)}><boxGeometry args={[14 * K, 26 * K, 0.01]} /><meshStandardMaterial color="#ef4444" /></mesh>
        </>
      ) : null}
      {stNow.T1off ? <mesh position={w3(240, 76, 0.062)}><sphereGeometry args={[5 * K, 12, 12]} /><meshStandardMaterial color="#334155" /></mesh> : null}
      {/* Netzkabel des Fluke in der Steckdose */}
      {stNow.plug ? (
        <group>
          <mesh position={[plugPos.x, plugPos.y, plugPos.z + 0.02]}><boxGeometry args={[0.042, 0.05, 0.04]} /><meshStandardMaterial color="#111827" roughness={0.6} /></mesh>
          <mesh><tubeGeometry args={[new THREE.CatmullRomCurve3([new THREE.Vector3(plugPos.x, plugPos.y - 0.02, plugPos.z + 0.04), new THREE.Vector3(plugPos.x - 0.1, plugPos.y - 0.25, plugPos.z + 0.2), anchor]), 32, 0.004, 8, false]} /><meshStandardMaterial color="#111827" /></mesh>
        </group>
      ) : null}
      {probe("r", "#dc2626", 1)}
      {probe("g", "#16a34a", 0)}
      {probe("b", "#2563eb", -1)}
    </>
  );
};

// ------------------------------------------------------------------ Overlays
const PHASES = DATA[KB].s.topics;
const Header: React.FC<{ topic: number }> = ({ topic }) => (
  <>
    <div style={{ position: "absolute", left: 40, top: 28, display: "flex", gap: 12, alignItems: "center" }}>
      <div style={{ fontFamily: "Inter", fontWeight: 900, fontSize: 24, color: "#fff", background: "#111827", borderRadius: 10, padding: "6px 12px" }}>POV</div>
      <div style={{ fontFamily: "Inter", fontWeight: 800, fontSize: 24, color: "#111827", background: "rgba(255,255,255,0.8)", borderRadius: 10, padding: "6px 12px" }}>Messen mit dem Fluke 1664 FC · VDE 0100-600</div>
    </div>
    {topic > 0 ? (
      <div style={{ position: "absolute", right: 40, top: 28, display: "flex", gap: 8 }}>
        {PHASES.map((p, i) => (
          <div key={p} style={{ fontFamily: "Inter", fontSize: 18, fontWeight: i + 1 === topic ? 800 : 600, padding: "7px 12px", borderRadius: 24,
            background: i + 1 === topic ? ORANGE : i + 1 < topic ? "#dcfce7" : "rgba(255,255,255,0.75)", color: i + 1 === topic ? "#fff" : i + 1 < topic ? "#15803d" : "#64748b" }}>
            {i + 1 < topic ? "✓" : i + 1} {i + 1 === topic ? p : ""}
          </div>
        ))}
      </div>
    ) : null}
  </>
);

export const MessVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const tl = useTimeline();
  const tex = useGestellTex();
  const { s } = DATA[KB];
  let si = 0;
  tl.scenes.forEach((S, i) => S.start <= frame && (si = i));
  const S = tl.scenes[si];
  const sc = s.sentences[si] as any;
  const ln = info(KB, si);
  const t = (frame - S.start) / FPS;

  // Fluke-Zustand
  const flSt: FlukeState = {};
  let press = "", pressF = -999, dialF = -999, prevDial: string | undefined, poseF = 0, prevPose = "hold";
  tl.fl.forEach((x) => {
    if (x.f > frame) return;
    if (x.p.dial && x.p.dial !== flSt.dial) { prevDial = flSt.dial; dialF = x.f; }
    if (x.p.pose && x.p.pose !== flSt.pose) { prevPose = flSt.pose ?? "hold"; poseF = x.f; }
    if (x.p.press !== undefined) { press = x.p.press ?? ""; pressF = x.f; }
    Object.assign(flSt, x.p);
  });
  const pressA = Math.max(0, 1 - (frame - pressF) / (0.6 * FPS));
  const dialA = Math.min(1, (frame - dialF) / (0.5 * FPS));
  const pz = spring({ frame: frame - poseF, fps: FPS, config: { damping: 16, stiffness: 110 } });
  const P = { hold: { x: 30, y: 640, s: 0.5, r: -10 }, look: { x: 150, y: 140, s: 0.95, r: -3 } } as const;
  const A = P[(prevPose as "hold" | "look") ?? "hold"] ?? P.hold, B = P[(flSt.pose as "hold" | "look") ?? "hold"] ?? P.hold;
  const fx = A.x + (B.x - A.x) * pz, fy = A.y + (B.y - A.y) * pz, fs = A.s + (B.s - A.s) * pz, fr = A.r + (B.r - A.r) * pz;
  const sway = Math.sin(frame / 22) * 4;

  // Protokoll-Einträge
  const fills: Fill[] = [];
  tl.scenes.forEach((X, i) => {
    const sv: any = s.sentences[i].v;
    (sv.fill ?? []).forEach((f: [string, string, string]) =>
      fills.push({ key: f[1], val: f[2], at: i < si ? -10 : i === si ? Math.max(0, X.cue(f[0])) : 999 }));
  });
  const isProto = sc.v.type === "protocol";
  const protoA = isProto ? interpolate(t, [0, 0.4], [0, 1], { extrapolateRight: "clamp" }) : 0;
  const note = flSt.note ?? "";
  const cards = (sc.v.cards ?? []).filter((c: any) => t >= Math.max(0, S.cue(c[0])) - 0.05);

  return (
    <AbsoluteFill style={{ background: "#d9dee3" }}>
      <ThreeCanvas width={W} height={H} camera={{ fov: 52, near: 0.01, far: 50 }}>
        <World tl={tl} tex={tex} />
      </ThreeCanvas>
      <Header topic={sc.topic} />
      {/* Hinweis (was gerade eingestellt / gemessen wird) */}
      {note && !isProto ? (
        <div style={{ position: "absolute", left: flSt.pose === "look" ? 760 : 0, right: flSt.pose === "look" ? 80 : 0, top: flSt.pose === "look" ? 380 : 110,
          display: "flex", justifyContent: flSt.pose === "look" ? "flex-start" : "center" }}>
          <div style={{ fontFamily: "Inter", fontWeight: 900, fontSize: flSt.pose === "look" ? 64 : 46, color: "#fff", background: "rgba(17,24,39,0.88)", borderLeft: `10px solid ${ORANGE}`, borderRadius: 16, padding: "18px 30px" }}>{note}</div>
        </div>
      ) : null}
      {cards.length ? (
        <div style={{ position: "absolute", right: 80, top: 200, display: "flex", flexDirection: "column", gap: 14 }}>
          {cards.map((c: any) => (
            <div key={c[1]} style={{ fontFamily: "Inter", fontWeight: 800, fontSize: 40, color: "#111827", background: "#fff", borderRadius: 14, padding: "12px 24px", boxShadow: "0 10px 30px rgba(0,0,0,0.2)",
              borderLeft: `10px solid ${c[1].startsWith("rot") ? "#dc2626" : c[1].startsWith("grün") ? "#16a34a" : c[1].startsWith("blau") ? "#2563eb" : ORANGE}` }}>{c[1]}</div>
          ))}
        </div>
      ) : null}
      {/* Fluke in der Hand */}
      {!isProto && sc.v.type !== "card" ? (
        <div style={{ position: "absolute", left: fx, top: fy + sway, transform: `scale(${fs}) rotate(${fr}deg)`, transformOrigin: "top left" }}>
          <Fluke st={flSt} press={press} pressA={pressA} dialA={dialA} prevDial={prevDial} t={frame / FPS} />
        </div>
      ) : null}
      {/* Protokoll auf dem Klemmbrett */}
      {isProto ? (
        <AbsoluteFill style={{ background: `rgba(15,23,42,${0.45 * protoA})` }}>
          <div style={{ position: "absolute", left: 0, right: 0, top: 110, transform: `translateY(${(1 - protoA) * 700}px) scale(0.92)`, transformOrigin: "top center" }}>
            <Protocol fills={fills} t={t} isoVals={ISO_VALS} />
          </div>
        </AbsoluteFill>
      ) : null}
      {sc.v.type === "title" ? (
        <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(15,23,42,0.85), rgba(15,23,42,0.1))", justifyContent: "center", paddingLeft: 110 }}>
          <div style={{ fontFamily: "Inter", fontWeight: 800, fontSize: 30, letterSpacing: 4, color: "#fdba74" }}>PRAKTISCHE PRÜFUNG · POV</div>
          <div style={{ fontFamily: "Inter", fontWeight: 900, fontSize: 108, color: "#fff", lineHeight: 1.0, margin: "16px 0" }}>Messen nach<br />VDE 0100-600</div>
          <div style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 40, color: "#e2e8f0" }}>mit dem Fluke 1664 FC – jede Einstellung</div>
        </AbsoluteFill>
      ) : null}
      {sc.v.type === "card" ? (
        <AbsoluteFill style={{ background: "rgba(15,23,42,0.82)", padding: "120px 70px 160px", display: "flex", flexDirection: "row", gap: 26 }}>
          {sc.v.rows.map((r: any, i: number) => {
            const p = spring({ frame: frame - S.start - Math.round(Math.max(0, S.cue(r[0])) * FPS), fps: FPS, config: { damping: 14 } });
            return (
              <div key={i} style={{ flex: 1, background: "#fff", borderRadius: 22, padding: 28, opacity: p, transform: `translateY(${(1 - p) * 60}px)` }}>
                <div style={{ fontFamily: "Inter", fontWeight: 900, fontSize: 46, color: ORANGE, marginBottom: 14 }}>{r[1]}</div>
                {r[2].map((x: string) => <div key={x} style={{ fontFamily: "Inter", fontWeight: 700, fontSize: 30, color: "#111827", padding: "10px 0", borderBottom: "1px solid #e2e8f0" }}>{x}</div>)}
              </div>
            );
          })}
        </AbsoluteFill>
      ) : null}
      <Sub words={ln.words} t={t} />
      {tl.scenes.map((X, i) => {
        const l = info(KB, i);
        return l.file ? (
          <Sequence key={i} from={X.start + lead(s.sentences[i])} durationInFrames={X.dur}>
            <Audio src={staticFile(l.file)} />
          </Sequence>
        ) : null;
      })}
    </AbsoluteFill>
  );
};

export const messFrames = () => DATA[KB].s.sentences.reduce((a, _, i) => a + durF(KB, i), 0);
