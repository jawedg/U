// POV-Video (3D): VDE-Messungen am Prüfungsgestell mit dem Fluke 1664 FC.
// Eine einzige 3D-Szene für das ganze Video (Kamera = deine Augen), Overlays: Fluke in der Hand, Hinweise, Protokoll, Untertitel.
import React, { useMemo } from "react";
import { AbsoluteFill, Audio, Sequence, getInputProps, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { DATA, cueFn, durF, info, lead } from "../lern/LernVideo";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import { EffectComposer, N8AO, DepthOfField, SMAA, Vignette, ToneMapping } from "@react-three/postprocessing";
import { ToneMappingMode } from "postprocessing";
import { BOX } from "../pruef/Gestell";
import { Fill, Protocol, Sub } from "../pruef/PruefVideo";
import { FlukeState } from "./Fluke";
import { BEDPE, CEE_PE, CY, Gestell3D, PLATE_PE, PLUG_CABLE_START, TERM_SCREW_TOP, X as GX, X5_PE, Y as GY, termX } from "./scene/Gestell3D";
import { Clip, Hand, Lead, Probe, basis } from "./scene/Probe3D";
import { Fluke3D, JACKS } from "./scene/Fluke3D";
import { floorTex, pegTex, paperTex, phys, wallTex, woodTex } from "./scene/tex";

const KB = 8;
const DPR: number = (getInputProps() as any).dpr ?? 1;
const FX: string = (getInputProps() as any).fx ?? "ao,dof";
const FPS = 25;
const W = 1920, H = 1080;
const ORANGE = "#f26b1d";
const ISO_VALS = ["620 MΩ", "710 MΩ", "655 MΩ", "580 MΩ", "690 MΩ", "742 MΩ", "605 MΩ", "630 MΩ", "668 MΩ", "590 MΩ"];

// Ziel- und Kontaktpunkte (Weltkoordinaten)
const DEPTH: Record<string, number> = { F3: 0.075, F1: 0.075, F2: 0.075, T1: 0.065, F4: 0.09, Q1: 0.085, Q2: 0.085, X5: 0.045, SPS: 0.08, X10: 0.03, X1: 0.05, X2: 0.05, X3: 0.05, X4: 0.05, BED: 0.09, CEE: 0.1, PLATTE: 0.012 };
const w3 = (px: number, py: number, z = 0): THREE.Vector3 => new THREE.Vector3(GX(px), GY(py), z);
const P3 = (name: string): THREE.Vector3 => {
  if (name === "ALL") return new THREE.Vector3(-0.02, CY - 0.02, 0.04);
  if (name === "LOW") return w3(380, 640, 0.04);
  if (name.startsWith("X1:")) return TERM_SCREW_TOP().setX(termX(50, parseInt(name.slice(3), 10)));
  if (name === "M1PE") return P3("X1:16");
  if (name === "CEEPE") return CEE_PE();
  if (name === "PLATTE") return PLATE_PE();
  if (name === "X5PE") return X5_PE();
  if (name === "BEDPE") return BEDPE();
  const b = BOX[name];
  if (b) return w3(b[0] + b[2] / 2, b[1] + b[3] / 2, DEPTH[name] ?? 0.05);
  return w3(480, 380, 0.05);
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
const useEnv = () => {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  useMemo(() => {
    const pm = new THREE.PMREMGenerator(gl);
    scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environmentIntensity = 0.42;
    pm.dispose();
  }, [gl, scene]);
};

type ProbeView = { key: "r" | "g" | "b"; tip: THREE.Vector3; q: THREE.Quaternion; axis: THREE.Vector3; clip: boolean; side: number; hand: boolean };
const COL: Record<string, string> = { r: "#c81f1f", g: "#1e8f3c", b: "#1f5fc4" };

export type FlukeView = { st: FlukeState; press: string; pressA: number; dialA: number; prevDial?: string; pose: number };

const World: React.FC<{ tl: ReturnType<typeof useTimeline>; fl: FlukeView }> = ({ tl, fl }) => {
  const frame = useCurrentFrame();
  const camera = useThree((s) => s.camera);
  useEnv();

  // Kamera (deine Augen)
  const ks = tl.cam;
  let ki = 0;
  for (let i = 0; i < ks.length; i++) if (ks[i].f <= frame) ki = i;
  const cur = camPose(ks[ki]);
  const prev = camPose(ks[Math.max(0, ki - 1)]);
  const e = ease(Math.min(1, Math.max(0, (frame - ks[ki].f) / (1.5 * FPS))));
  const pos = prev.pos.clone().lerp(cur.pos, e);
  const tgt = prev.tgt.clone().lerp(cur.tgt, e);
  const tt = frame / FPS;
  pos.add(new THREE.Vector3(Math.sin(tt * 0.61) * 0.004 + Math.sin(tt * 1.7) * 0.0012, Math.sin(tt * 1.13) * 0.003, Math.sin(tt * 0.37) * 0.003));
  tgt.add(new THREE.Vector3(Math.sin(tt * 0.43 + 1) * 0.003, Math.cos(tt * 0.77) * 0.0025, 0));
  camera.position.copy(pos);
  camera.lookAt(tgt);
  camera.updateMatrixWorld();
  const fwd = tgt.clone().sub(pos).normalize();
  const right = new THREE.Vector3().crossVectors(fwd, new THREE.Vector3(0, 1, 0)).normalize();
  const up = new THREE.Vector3().crossVectors(right, fwd).normalize();
  const rel = (f: number, r: number, u: number) => pos.clone().add(fwd.clone().multiplyScalar(f)).add(right.clone().multiplyScalar(r)).add(up.clone().multiplyScalar(u));

  // Zustände
  const stNow: Record<string, number> = {};
  tl.st.forEach((x) => x.f <= frame && Object.assign(stNow, x.p));

  // ---------------- Fluke vor der Brust / vor den Augen
  const poseHold = { p: rel(0.43, -0.265, -0.16), rx: -0.42, ry: 0.32, rz: 0.1 };
  const poseLook = { p: rel(0.3, -0.098, -0.008), rx: -0.06, ry: 0.14, rz: 0.03 };
  const pz = fl.pose;
  const fPos = poseHold.p.clone().lerp(poseLook.p, pz);
  fPos.add(up.clone().multiplyScalar(Math.sin(tt * 1.3) * 0.002));
  const fQ = camera.quaternion.clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(
    poseHold.rx + (poseLook.rx - poseHold.rx) * pz, poseHold.ry + (poseLook.ry - poseHold.ry) * pz, poseHold.rz + (poseLook.rz - poseHold.rz) * pz)));
  const jackW = (k: string) => JACKS[k].clone().applyQuaternion(fQ).add(fPos);

  // ---------------- Messspitzen
  const target = (key: string) => {
    const L = tl.probes[key];
    let i = -1;
    for (let j = 0; j < L.length; j++) if (L[j].f <= frame) i = j;
    return { L, i };
  };
  const activeTargets = (["r", "g", "b"] as const)
    .map((k) => ({ k, ...target(k) }))
    .filter((x) => x.i >= 0 && x.L[x.i].pt !== "-" && x.L[x.i].pt !== "CEEPE")
    .map((x) => ({ k: x.k, x: P3(x.L[x.i].pt).clone().project(camera).x }))
    .sort((a, b) => a.x - b.x);
  const sideOf: Record<string, number> = {};
  const handOf: Record<string, boolean> = {};
  const n = activeTargets.length;
  activeTargets.forEach((a, i) => {
    sideOf[a.k] = n === 1 ? 1 : n === 2 ? (i ? 1 : -1) : i - 1;
    handOf[a.k] = n < 3 || i !== 1;
  });
  const toCam = (p: THREE.Vector3) => pos.clone().sub(p).normalize();
  const dirFor = (pt: string, side: number, p: THREE.Vector3) => {
    if (pt === "CEEPE") return new THREE.Vector3(0.25, 1, 0.75).normalize();
    const nrm = new THREE.Vector3(0, 0, 1);
    const fan = pt === "X5PE" ? 0.18 : 0.5;
    const down = pt === "X5PE" ? 0.3 : 0.78;
    return nrm.multiplyScalar(0.5).add(toCam(p).multiplyScalar(0.3)).add(right.clone().multiplyScalar(side * fan)).add(up.clone().multiplyScalar(-down)).normalize();
  };
  const views: ProbeView[] = [];
  (["r", "g", "b"] as const).forEach((k) => {
    const { L, i } = target(k);
    if (i < 0) return;
    const side = sideOf[k] ?? (k === "r" ? 1 : k === "g" ? -1 : 0);
    const rest = rel(0.32, side * 0.16, -0.36);
    const restDir = toCam(rest).add(up.clone().multiplyScalar(-0.5)).normalize();
    const at = (pt?: string) => (!pt || pt === "-" ? { p: rest, d: restDir } : (() => { const p = P3(pt); return { p, d: dirFor(pt, side, p) }; })());
    const to = at(L[i].pt);
    const from = i > 0 ? at(L[i - 1].pt) : { p: rest, d: restDir };
    const m = ease(Math.min(1, (frame - L[i].f) / (0.85 * FPS)));
    if (L[i].pt === "-" && m >= 1) return;
    const d = from.d.clone().lerp(to.d, m).normalize();
    const lift = Math.sin(Math.PI * m) * (from.p.distanceTo(to.p) > 0.02 ? 0.07 : 0.03);
    const tip = from.p.clone().lerp(to.p, m).add(d.clone().multiplyScalar(lift));
    const clip = (L[i].pt === "CEEPE" || (L[i].pt === "-" && L[Math.max(0, i - 1)].pt === "CEEPE"));
    const q = basis(d, toCam(tip));
    views.push({ key: k, tip, q, axis: d, clip, side, hand: !clip && (handOf[k] ?? true) });
  });

  // Mittel-Abstand für Schärfe
  const focus = fl.pose > 0.5 ? 0.3 : pos.distanceTo(tgt);

  const plugStart = PLUG_CABLE_START();
  const leadsIn = views.map((v) => v.key);
  return (
    <>
      <color attach="background" args={["#cfd3d6"]} />
      <hemisphereLight args={["#f4f6ff", "#6b6157", 0.22]} />
      <directionalLight
        position={[-0.9, 3.2, 2.4]}
        intensity={2.9}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-bias={-0.0002}
        shadow-normalBias={0.002}
        shadow-camera-left={-1.1}
        shadow-camera-right={1.1}
        shadow-camera-top={1.1}
        shadow-camera-bottom={-1.1}
        shadow-camera-near={1}
        shadow-camera-far={6}
      >
        <object3D attach="target" position={[0, 1.2, 0]} />
      </directionalLight>
      <directionalLight position={[2.5, 1.8, 1.5]} intensity={0.45} color="#fff1e0" />
      <Room />
      <Gestell3D st={stNow} />
      {views.map((v) => (v.clip ? <Clip key={v.key} tip={v.tip} q={v.q} color={COL[v.key]} /> : <Probe key={v.key} tip={v.tip} q={v.q} color={COL[v.key]} />))}
      {views.filter((v) => v.hand).map((v) => (
        <Hand key={"h" + v.key} tip={v.tip} q={v.q} side={v.side} elbow={rel(0.0, v.side * 0.17, -0.6)} />
      ))}
      {views.map((v) => (
        <Lead key={"l" + v.key} a={v.tip.clone().add(v.axis.clone().multiplyScalar(v.clip ? 0.08 : 0.172))} aDir={v.axis} b={jackW(v.key).add(up.clone().multiplyScalar(0.004))} color={COL[v.key]} />
      ))}
      {stNow.plug ? <Lead a={plugStart} aDir={new THREE.Vector3(0, -1, 0.2).normalize()} b={rel(0.3, -0.28, -0.45)} color="#16181a" r={0.003} /> : null}
      <group position={fPos} quaternion={fQ}>
        <Fluke3D st={fl.st} press={fl.press} pressA={fl.pressA} dialA={fl.dialA} prevDial={fl.prevDial} t={tt} leads={leadsIn} />
      </group>
      {FX === "none" || FX === "noshadow" ? null : (
        <EffectComposer multisampling={0} enableNormalPass={false}>
          {FX.includes("ao") ? <N8AO aoRadius={0.04} distanceFalloff={0.6} intensity={2.2} quality="medium" halfRes /> : <></>}
          {FX.includes("dof") ? <DepthOfField worldFocusDistance={focus} worldFocusRange={fl.pose > 0.5 ? 0.12 : 0.35} bokehScale={2.2} /> : <></>}
          <SMAA />
          <Vignette offset={0.32} darkness={0.42} />
          {FX.includes("aces") ? <ToneMapping mode={ToneMappingMode.ACES_FILMIC} /> : FX.includes("agx") ? <ToneMapping mode={ToneMappingMode.AGX} /> : <></>}
        </EffectComposer>
      )}
    </>
  );
};

// ------------------------------------------------------------------ Werkstatt
const Room: React.FC = () => {
  const m = useMemo(() => {
    const wood = woodTex().clone();
    wood.needsUpdate = true;
    wood.repeat.set(1.2, 0.6);
    const wall = wallTex().clone();
    wall.needsUpdate = true;
    wall.repeat.set(3, 1.5);
    const floor = floorTex().clone();
    floor.needsUpdate = true;
    floor.repeat.set(4, 4);
    return {
      wood: phys({ map: wood, roughness: 0.55, clearcoat: 0.25, clearcoatRoughness: 0.5 }),
      wall: new THREE.MeshStandardMaterial({ map: wall, roughness: 0.95 }),
      floor: new THREE.MeshStandardMaterial({ map: floor, roughness: 0.7 }),
      steel: phys({ color: "#56626e", roughness: 0.5, clearcoat: 0.3 }),
      paper: new THREE.MeshStandardMaterial({ map: paperTex(), roughness: 0.9 }),
      board: phys({ color: "#7a5a3a", roughness: 0.6 }),
      clipM: new THREE.MeshStandardMaterial({ color: "#c8ccd0", metalness: 1, roughness: 0.3 }),
      red: phys({ color: "#c1272d", roughness: 0.35, clearcoat: 0.6 }),
      yel: phys({ color: "#f5c400", roughness: 0.35, clearcoat: 0.6 }),
      black: phys({ color: "#1b1d20", roughness: 0.5 }),
      peg: new THREE.MeshStandardMaterial({ map: pegTex(), roughness: 0.8 }),
    };
  }, []);
  return (
    <group>
      <mesh position={[0, 1.6, -0.3]} material={m.wall} receiveShadow><planeGeometry args={[8, 3.2]} /></mesh>
      <mesh position={[1.25, 1.45, -0.29]} material={m.peg} receiveShadow><planeGeometry args={[0.9, 0.6]} /></mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 1]} material={m.floor} receiveShadow><planeGeometry args={[10, 10]} /></mesh>
      {/* Werkbank */}
      <mesh position={[0, 0.83, 0.2]} material={m.wood} castShadow receiveShadow><boxGeometry args={[2.6, 0.04, 0.95]} /></mesh>
      {[[-1.2, -0.2], [1.2, -0.2], [-1.2, 0.6], [1.2, 0.6]].map(([x, z], i) => (
        <mesh key={i} position={[x, 0.405, z]} material={m.steel} castShadow><boxGeometry args={[0.05, 0.81, 0.05]} /></mesh>
      ))}
      <mesh position={[0, 0.3, 0.2]} material={m.steel} receiveShadow><boxGeometry args={[2.4, 0.03, 0.85]} /></mesh>
      {/* Protokoll auf Klemmbrett */}
      <group position={[0.62, 0.852, 0.3]} rotation={[-Math.PI / 2, 0, 0.35]}>
        <mesh material={m.board} castShadow receiveShadow><boxGeometry args={[0.235, 0.33, 0.004]} /></mesh>
        <mesh material={m.paper} position={[0, -0.01, 0.0025]} receiveShadow><planeGeometry args={[0.21, 0.297]} /></mesh>
        <mesh material={m.clipM} position={[0, 0.15, 0.006]} castShadow><boxGeometry args={[0.09, 0.03, 0.008]} /></mesh>
      </group>
      {/* Schraubendreher */}
      <group position={[0.32, 0.862, 0.36]} rotation={[0, 0.6, Math.PI / 2]}>
        <mesh material={m.red} castShadow><cylinderGeometry args={[0.012, 0.014, 0.1, 20]} /></mesh>
        <mesh material={m.yel} position={[0, 0.03, 0]} castShadow><cylinderGeometry args={[0.0125, 0.0125, 0.02, 20]} /></mesh>
        <mesh material={m.clipM} position={[0, -0.1, 0]} castShadow><cylinderGeometry args={[0.0025, 0.0025, 0.1, 10]} /></mesh>
      </group>
      {/* Abisolierzange */}
      <group position={[-0.62, 0.857, 0.34]} rotation={[-Math.PI / 2, 0, -0.5]}>
        <mesh material={m.red} position={[-0.012, -0.05, 0]} rotation={[0, 0, 0.12]} castShadow><boxGeometry args={[0.016, 0.11, 0.012]} /></mesh>
        <mesh material={m.red} position={[0.012, -0.05, 0]} rotation={[0, 0, -0.12]} castShadow><boxGeometry args={[0.016, 0.11, 0.012]} /></mesh>
        <mesh material={m.black} position={[0, 0.03, 0]} castShadow><boxGeometry args={[0.03, 0.06, 0.012]} /></mesh>
      </group>
    </group>
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
  const poseVal = (p?: string) => (p === "look" ? 1 : 0);
  const pose = poseVal(prevPose) + (poseVal(flSt.pose) - poseVal(prevPose)) * pz;
  const look = flSt.pose === "look";

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
      <ThreeCanvas width={W} height={H} camera={{ fov: 50, near: 0.01, far: 30 }} shadows={!FX.includes("noshadow")} dpr={DPR} gl={{ toneMapping: THREE.NoToneMapping, antialias: false, powerPreference: "high-performance" }}>
        <World tl={tl} fl={{ st: flSt, press, pressA, dialA, prevDial, pose }} />
      </ThreeCanvas>
      <Header topic={sc.topic} />
      {/* Hinweis (was gerade eingestellt / gemessen wird) */}
      {note && !isProto ? (
        <div style={{ position: "absolute", left: look ? 900 : 560, right: look ? 70 : 60, top: look ? 360 : 120, display: "flex", justifyContent: look ? "flex-start" : "center" }}>
          <div style={{ fontFamily: "Inter", fontWeight: 800, fontSize: look ? 60 : 44, color: "#fff", background: "linear-gradient(135deg, rgba(17,24,39,0.82), rgba(30,41,59,0.72))",
            border: "1px solid rgba(255,255,255,0.18)", borderLeft: `8px solid ${ORANGE}`, borderRadius: 18, padding: look ? "20px 34px" : "14px 28px",
            boxShadow: "0 18px 50px rgba(0,0,0,0.35)", backdropFilter: "blur(6px)" }}>{note}</div>
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
      <div style={{ position: "absolute", left: isProto || sc.v.type === "card" || sc.v.type === "title" ? 0 : 520, right: 30, top: 0, bottom: 0 }}>
        <Sub words={ln.words} t={t} />
      </div>
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
