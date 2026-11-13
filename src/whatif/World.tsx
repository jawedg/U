// Low-Poly-Welt „Einbruch im Eis“: zugefrorener See bei Nacht, Schnee, Ufer mit Hütte, Einbruchstelle.
import React, { useMemo } from "react";
import * as THREE from "three";
import { useThree } from "@react-three/fiber";
import { FPS, SHOTS, Shot } from "./timeline";

// ---------- Hilfen ----------
const rng = (seed: number) => () => {
  seed = (seed + 0x6d2b79f5) | 0;
  let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const cl = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const sm = (a: number, b: number, x: number) => {
  const t = cl((x - a) / (b - a));
  return t * t * (3 - 2 * t);
};
const eio = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const V = (x: number, y: number, z: number) => new THREE.Vector3(x, y, z);
const cache = new Map<string, any>();
const once = <T,>(k: string, f: () => T): T => {
  if (!cache.has(k)) cache.set(k, f());
  return cache.get(k);
};
const canvasTex = (w: number, h: number, draw: (c: CanvasRenderingContext2D) => void) => {
  const cv = document.createElement("canvas");
  cv.width = w;
  cv.height = h;
  draw(cv.getContext("2d")!);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
};

const ICE_TOP = 0;
const ICE_T = 0.15;
const WATER_Y = -0.045;
const NEAR = 4; // Nahbereich ±4 m als eigenes Stück mit Loch

// Loch-Umriss (gezackt). Richtung +z (Ufer/Hütte) und −z etwas enger, damit die Hände sicher auf dem Eis liegen.
const HOLE = once("hole", () => {
  const r = rng(42);
  const N = 15;
  const pts: THREE.Vector2[] = []; // (x, z)
  for (let k = 0; k < N; k++) {
    const a = (k / N) * Math.PI * 2 + (r() - 0.5) * 0.22;
    let rad = 1.0 + r() * 0.28;
    const toZ = Math.abs(Math.cos(a));
    if (toZ > 0.85) rad = 1.0 + r() * 0.06;
    pts.push(new THREE.Vector2(Math.sin(a) * rad, Math.cos(a) * rad));
  }
  return pts;
});

// Shape-Koordinaten: (x, -z) → nach rotateX(-π/2) liegt die Fläche in xz, Extrusion nach oben.
const toShape = (p: THREE.Vector2) => new THREE.Vector2(p.x, -p.y);
const layFlat = (g: THREE.BufferGeometry, depth: number) => {
  g.rotateX(-Math.PI / 2);
  g.translate(0, ICE_TOP - depth, 0);
  return g;
};

// ---------- Texturen ----------
const iceTex = () =>
  once("iceTex", () => {
    const t = canvasTex(1024, 1024, (c) => {
      const r = rng(5);
      c.fillStyle = "#8fa7b8";
      c.fillRect(0, 0, 1024, 1024);
      // dunkles Klareis
      for (let i = 0; i < 26; i++) {
        c.fillStyle = `rgba(40,70,92,${0.12 + r() * 0.18})`;
        c.beginPath();
        c.ellipse(r() * 1024, r() * 1024, 40 + r() * 140, 20 + r() * 80, r() * 3, 0, Math.PI * 2);
        c.fill();
      }
      // Schneeflecken
      for (let i = 0; i < 70; i++) {
        c.fillStyle = `rgba(232,240,246,${0.25 + r() * 0.45})`;
        c.beginPath();
        const x = r() * 1024, y = r() * 1024, s = 20 + r() * 110;
        for (let k = 0; k < 7; k++) {
          const a = (k / 7) * Math.PI * 2, rr = s * (0.6 + r() * 0.5);
          k ? c.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr * 0.6) : c.moveTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr * 0.6);
        }
        c.fill();
      }
      // feine Risse/Kratzer im Eis
      for (let i = 0; i < 60; i++) {
        c.strokeStyle = `rgba(230,245,255,${0.08 + r() * 0.18})`;
        c.lineWidth = 1 + r() * 1.5;
        c.beginPath();
        let x = r() * 1024, y = r() * 1024;
        c.moveTo(x, y);
        for (let k = 0; k < 4; k++) {
          x += (r() - 0.5) * 120;
          y += (r() - 0.5) * 120;
          c.lineTo(x, y);
        }
        c.stroke();
      }
    });
    t.repeat.set(1 / (2 * NEAR), 1 / (2 * NEAR));
    t.offset.set(0.5, 0.5);
    return t;
  });

const dotTex = () =>
  once("dot", () =>
    canvasTex(64, 64, (c) => {
      const g = c.createRadialGradient(32, 32, 0, 32, 32, 32);
      g.addColorStop(0, "rgba(255,255,255,1)");
      g.addColorStop(0.45, "rgba(255,255,255,0.8)");
      g.addColorStop(1, "rgba(255,255,255,0)");
      c.fillStyle = g;
      c.fillRect(0, 0, 64, 64);
    }),
  );
const glowTex = () =>
  once("glow", () =>
    canvasTex(128, 128, (c) => {
      const g = c.createRadialGradient(64, 64, 0, 64, 64, 64);
      g.addColorStop(0, "rgba(255,255,255,0.9)");
      g.addColorStop(0.2, "rgba(255,255,255,0.35)");
      g.addColorStop(1, "rgba(255,255,255,0)");
      c.fillStyle = g;
      c.fillRect(0, 0, 128, 128);
    }),
  );

// ---------- Materialien ----------
const M = {
  ice: () => once("mIce", () => new THREE.MeshStandardMaterial({ map: iceTex(), roughness: 0.55, metalness: 0.05, flatShading: true })),
  iceSide: () => once("mIceSide", () => new THREE.MeshStandardMaterial({ color: "#4a7b8c", emissive: "#081d25", roughness: 0.35, flatShading: true })),
  far: () => once("mFar", () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.7, flatShading: true, side: THREE.DoubleSide })),
  water: () => once("mWater", () => new THREE.MeshStandardMaterial({ color: "#0e3a44", roughness: 0.18, metalness: 0.25, flatShading: true, side: THREE.DoubleSide })),
  crack: () => once("mCrack", () => new THREE.MeshBasicMaterial({ color: "#16242d", side: THREE.DoubleSide })),
  crackHi: () => once("mCrackHi", () => new THREE.MeshBasicMaterial({ color: "#d9f1ff", transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthWrite: false })),
  print: () => once("mPrint", () => new THREE.MeshStandardMaterial({ color: "#5e7487", roughness: 1 })),
  land: () => once("mLand", () => new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.9, flatShading: true })),
  tree: () => once("mTree", () => new THREE.MeshStandardMaterial({ color: "#132824", roughness: 1, flatShading: true })),
  skin: () => once("mSkin", () => new THREE.MeshStandardMaterial({ color: "#d9a07c", roughness: 0.75, flatShading: true })),
  jacket: () => once("mJacket", () => new THREE.MeshStandardMaterial({ color: "#e0a019", roughness: 0.7, flatShading: true })),
  cuff: () => once("mCuff", () => new THREE.MeshStandardMaterial({ color: "#2b3138", roughness: 0.9, flatShading: true })),
  pants: () => once("mPants", () => new THREE.MeshStandardMaterial({ color: "#26354a", roughness: 0.9, flatShading: true })),
  hut: () => once("mHut", () => new THREE.MeshStandardMaterial({ color: "#4a3426", roughness: 0.9, flatShading: true })),
  roof: () => once("mRoof", () => new THREE.MeshStandardMaterial({ color: "#d7e0e8", roughness: 0.9, flatShading: true })),
  window: () => once("mWin", () => new THREE.MeshBasicMaterial({ color: "#ffb257" })),
  bubble: () => once("mBub", () => new THREE.MeshBasicMaterial({ color: "#d8fbff", transparent: true, opacity: 0.55, depthWrite: false })),
  breath: () => once("mBreath", () => new THREE.MeshBasicMaterial({ color: "#e9f2f8", transparent: true, opacity: 0.1, depthWrite: false })),
  holeLight: () => once("mHoleL", () => new THREE.MeshBasicMaterial({ color: "#a9dfe6", side: THREE.DoubleSide, fog: false })),
  shaft: () => once("mShaft", () => new THREE.MeshBasicMaterial({ color: "#9fe3ec", transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false })),
};

// ---------- Geometrien ----------
const nearIceGeo = () =>
  once("nearIce", () => {
    const s = new THREE.Shape([V(-NEAR, -NEAR, 0), V(NEAR, -NEAR, 0), V(NEAR, NEAR, 0), V(-NEAR, NEAR, 0)].map((v) => new THREE.Vector2(v.x, v.y)));
    s.holes.push(new THREE.Path([...HOLE].reverse().map(toShape)));
    return layFlat(new THREE.ExtrudeGeometry(s, { depth: ICE_T, bevelEnabled: false, curveSegments: 1 }), ICE_T);
  });

// Schollen-Keile (füllen das Loch, bis es bricht)
const wedges = () =>
  once("wedges", () => {
    const N = HOLE.length;
    return HOLE.map((p, k) => {
      const q = HOLE[(k + 1) % N];
      const c = new THREE.Vector2(0, 0.0);
      const s = new THREE.Shape([toShape(c), toShape(p), toShape(q)]);
      const g = layFlat(new THREE.ExtrudeGeometry(s, { depth: ICE_T, bevelEnabled: false }), ICE_T);
      const mid = V((p.x + q.x) / 2, ICE_TOP - ICE_T / 2, (p.y + q.y) / 2);
      g.translate(-mid.x, -mid.y, -mid.z);
      const axis = V(q.x - p.x, 0, q.y - p.y).normalize();
      return { g, mid, axis, k };
    });
  });

// Ferne Eisfläche: Raster mit Facetten-Farben, Nahbereich ausgespart
const farIceGeo = () =>
  once("farIce", () => {
    const S = 2.5, R = 150;
    const h = (i: number, j: number) => {
      const x = i * S, z = j * S;
      const d = Math.max(Math.abs(x), Math.abs(z));
      const r = rng((i * 7919) ^ (j * 104729));
      return d <= NEAR + 0.01 ? 0 : (r() - 0.3) * 0.12 * sm(NEAR, NEAR + 10, d);
    };
    const pos: number[] = [], col: number[] = [];
    const r = rng(9);
    const n = Math.round(R / S);
    for (let i = -n; i < n; i++)
      for (let j = -n; j < n; j++) {
        const x0 = i * S, z0 = j * S;
        if (x0 >= -NEAR && x0 + S <= NEAR && z0 >= -NEAR && z0 + S <= NEAR) continue;
        const a = [x0, h(i, j), z0], b = [x0 + S, h(i + 1, j), z0], c = [x0 + S, h(i + 1, j + 1), z0 + S], d = [x0, h(i, j + 1), z0 + S];
        for (const tri of [[a, d, c], [a, c, b]]) {
          const snow = r() < 0.55;
          const base = snow ? [0.78, 0.84, 0.9] : [0.5, 0.6, 0.68];
          const v = 0.9 + r() * 0.15;
          for (const p of tri) {
            pos.push(p[0], p[1], p[2]);
            col.push(base[0] * v, base[1] * v, base[2] * v);
          }
        }
      }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    g.computeVertexNormals();
    return g;
  });

// Ufer-Ring mit Hügeln
const landGeo = () =>
  once("land", () => {
    const A = 72, RS = [58, 66, 76, 92, 120, 170];
    const r = rng(77);
    const noise = Array.from({ length: A }, () => r());
    const hgt = (ri: number, ai: number) => {
      const n = noise[((ai % A) + A) % A];
      const base = [0, 1.2, 3.5, 7, 12, 18][ri];
      return ri === 0 ? -0.05 : base * (0.55 + n * 0.9);
    };
    const pt = (ri: number, ai: number) => {
      const a = (ai / A) * Math.PI * 2;
      return [Math.sin(a) * RS[ri], hgt(ri, ai), Math.cos(a) * RS[ri]];
    };
    const pos: number[] = [], col: number[] = [];
    for (let ri = 0; ri < RS.length - 1; ri++)
      for (let ai = 0; ai < A; ai++) {
        const a = pt(ri, ai), b = pt(ri, ai + 1), c = pt(ri + 1, ai + 1), d = pt(ri + 1, ai);
        for (const tri of [[a, b, c], [a, c, d]]) {
          const v = 0.72 + r() * 0.2;
          for (const p of tri) {
            pos.push(...p);
            col.push(v * 0.92, v * 0.96, v);
          }
        }
      }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    g.computeVertexNormals();
    return g;
  });

const skyGeo = () =>
  once("sky", () => {
    const g = new THREE.SphereGeometry(400, 32, 16);
    const top = new THREE.Color("#04070e"), hor = new THREE.Color("#2a3b52");
    const col: number[] = [];
    const p = g.attributes.position;
    for (let i = 0; i < p.count; i++) {
      const y = p.getY(i) / 400;
      const c = hor.clone().lerp(top, cl(Math.pow(Math.max(0, y), 0.55)));
      col.push(c.r, c.g, c.b);
    }
    g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    return g;
  });

const starsGeo = () =>
  once("stars", () => {
    const r = rng(3);
    const pos: number[] = [];
    for (let i = 0; i < 500; i++) {
      const a = r() * Math.PI * 2, y = 0.12 + r() * 0.88;
      const s = Math.sqrt(1 - y * y);
      pos.push(Math.cos(a) * s * 380, y * 380, Math.sin(a) * s * 380);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    return g;
  });

// Risse: Strahlen entlang der Keil-Kanten + Ring + Ausläufer
const CRACKS = once("cracks", () => {
  const r = rng(11);
  const segs: { a: THREE.Vector2; b: THREE.Vector2; t0: number; w: number }[] = [];
  HOLE.forEach((p, k) => {
    const d = p.clone().normalize();
    const t0 = 0.1 + r() * 0.35;
    // Strahl von der Mitte nach außen, leicht geknickt
    let a = new THREE.Vector2(0, 0);
    const steps = 3;
    for (let s = 1; s <= steps; s++) {
      const b = p.clone().multiplyScalar(s / steps).add(new THREE.Vector2((r() - 0.5) * 0.06, (r() - 0.5) * 0.06));
      segs.push({ a, b, t0: t0 + (s - 1) * 0.08, w: 0.008 });
      a = b;
    }
    // Ausläufer über den Rand hinaus
    let e = p.clone();
    for (let s = 0; s < 2 + Math.floor(r() * 3); s++) {
      const n = e.clone().add(d.clone().rotateAround(new THREE.Vector2(), (r() - 0.5) * 0.9).multiplyScalar(0.25 + r() * 0.35));
      segs.push({ a: e, b: n, t0: t0 + 0.3 + s * 0.1, w: 0.006 });
      e = n;
    }
    // Ring-Stück
    segs.push({ a: p, b: HOLE[(k + 1) % HOLE.length], t0: 0.45 + r() * 0.3, w: 0.007 });
  });
  return segs;
});

const FOOT = once("foot", () => {
  const r = rng(21);
  const out: { x: number; z: number; rot: number }[] = [];
  let x = 0.05;
  for (let i = 0; i < 90; i++) {
    const z = 1.25 + i * 0.68;
    x += (r() - 0.5) * 0.05;
    out.push({ x: x + (i % 2 ? 0.14 : -0.14), z, rot: (r() - 0.5) * 0.15 });
  }
  return out;
});

const TREES = once("trees", () => {
  const r = rng(31);
  const out: { p: THREE.Vector3; s: number }[] = [];
  for (let i = 0; i < 520; i++) {
    const a = r() * Math.PI * 2;
    const rad = 70 + r() * 45;
    // Lücke für die Hütte (Richtung +z)
    if (Math.abs(Math.atan2(Math.sin(a), Math.cos(a))) < 0.07 && rad < 80) continue;
    const ring = rad < 76 ? 2 + ((rad - 66) / 10) * 1.5 : rad < 92 ? 3.5 + ((rad - 76) / 16) * 3.5 : 7 + ((rad - 92) / 28) * 5;
    out.push({ p: V(Math.sin(a) * rad, ring * 0.75, Math.cos(a) * rad), s: 0.8 + r() * 0.9 });
  }
  return out;
});

// ---------- Bausteine ----------
const Trees: React.FC = () => {
  const mesh = useMemo(() => {
    const g = new THREE.ConeGeometry(1.6, 7, 6);
    g.translate(0, 3.5, 0);
    const m = new THREE.InstancedMesh(g, M.tree(), TREES.length);
    const o = new THREE.Object3D();
    TREES.forEach((t, i) => {
      o.position.copy(t.p);
      o.scale.set(t.s, t.s * (0.9 + (i % 5) * 0.08), t.s);
      o.rotation.y = i;
      o.updateMatrix();
      m.setMatrixAt(i, o.matrix);
    });
    return m;
  }, []);
  return <primitive object={mesh} />;
};

const Prints: React.FC = () => {
  const mesh = useMemo(() => {
    const g = new THREE.CircleGeometry(1, 8);
    g.rotateX(-Math.PI / 2);
    const m = new THREE.InstancedMesh(g, M.print(), FOOT.length);
    const o = new THREE.Object3D();
    FOOT.forEach((f, i) => {
      o.position.set(f.x, ICE_TOP + 0.004, f.z);
      o.rotation.set(0, f.rot, 0);
      o.scale.set(0.055, 1, 0.12);
      o.updateMatrix();
      m.setMatrixAt(i, o.matrix);
    });
    return m;
  }, []);
  return <primitive object={mesh} />;
};

const Hut: React.FC = () => (
  <group position={[1.5, 1.2, 64]} rotation={[0, Math.PI + 0.2, 0]}>
    <mesh material={M.hut()} position={[0, 1.4, 0]}>
      <boxGeometry args={[5, 2.8, 4]} />
    </mesh>
    <mesh material={M.roof()} position={[0, 3.6, 0]} rotation={[0, Math.PI / 4, 0]} scale={[1.25, 1, 1]}>
      <coneGeometry args={[3.9, 1.8, 4]} />
    </mesh>
    {[-1.2, 1.1].map((x) => (
      <mesh key={x} material={M.window()} position={[x, 1.5, 2.01]}>
        <planeGeometry args={[0.9, 0.8]} />
      </mesh>
    ))}
    <sprite position={[0, 1.6, 2.6]} scale={[9, 7, 1]}>
      <spriteMaterial map={glowTex()} color="#ff9a3c" transparent opacity={0.55} depthWrite={false} blending={THREE.AdditiveBlending} />
    </sprite>
  </group>
);

// Wasser im Loch: animierte Low-Poly-Wellen
const Waves: React.FC<{ t: number; amp: number }> = ({ t, amp }) => {
  const g = useMemo(() => {
    const geo = new THREE.PlaneGeometry(3.2, 3.2, 26, 26).toNonIndexed();
    geo.rotateX(-Math.PI / 2);
    (geo as any).base = Float32Array.from(geo.attributes.position.array as Float32Array);
    return geo;
  }, []);
  const base = (g as any).base as Float32Array;
  const p = g.attributes.position as THREE.BufferAttribute;
  for (let i = 0; i < p.count; i++) {
    const x = base[i * 3], z = base[i * 3 + 2];
    const y = Math.sin(x * 3.1 + t * 2.3) * 0.5 + Math.sin(z * 2.7 - t * 1.9 + 1) * 0.5 + Math.sin((x + z) * 5.3 + t * 3.4) * 0.25;
    p.setY(i, WATER_Y + y * amp);
  }
  p.needsUpdate = true;
  g.computeVertexNormals();
  return <mesh geometry={g} material={M.water()} />;
};

// Hand (Low-Poly). Handgelenk-Position, Finger-Richtung, Handrücken-Normale (Weltkoordinaten), Schulter für den Ärmel.
export const Hand: React.FC<{ wrist: THREE.Vector3; dir: THREE.Vector3; back: THREE.Vector3; shoulder: THREE.Vector3; side: number; curl?: number }> = ({ wrist, dir, back, shoulder, side, curl = 0 }) => {
  const y = dir.clone().normalize();
  const z = back.clone().sub(y.clone().multiplyScalar(back.dot(y))).normalize();
  const x = new THREE.Vector3().crossVectors(y, z);
  const q = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
  const s = side;
  const arm = shoulder.clone().sub(wrist);
  const armQ = new THREE.Quaternion().setFromUnitVectors(V(0, 1, 0), arm.clone().normalize());
  const fingers = [
    { x: -0.027, l1: 0.044, l2: 0.034, a: -0.08 },
    { x: -0.009, l1: 0.049, l2: 0.038, a: -0.02 },
    { x: 0.009, l1: 0.046, l2: 0.035, a: 0.04 },
    { x: 0.026, l1: 0.038, l2: 0.028, a: 0.11 },
  ];
  return (
    <group>
      <group position={wrist} quaternion={q}>
        {/* Handfläche */}
        <mesh material={M.skin()} position={[0, 0.048, 0]}>
          <boxGeometry args={[0.078, 0.092, 0.022]} />
        </mesh>
        {fingers.map((f, i) => (
          <group key={i} position={[f.x * s, 0.094, 0.002]} rotation={[-curl * 0.6, 0, -f.a * s]}>
            <mesh material={M.skin()} position={[0, f.l1 / 2, 0]}>
              <boxGeometry args={[0.017, f.l1, 0.017]} />
            </mesh>
            <group position={[0, f.l1, 0]} rotation={[-curl * 0.9, 0, 0]}>
              <mesh material={M.skin()} position={[0, f.l2 / 2, -0.0005]}>
                <boxGeometry args={[0.015, f.l2, 0.015]} />
              </mesh>
            </group>
          </group>
        ))}
        {/* Daumen */}
        <group position={[-0.04 * s, 0.03, -0.004]} rotation={[-0.25, 0, 0.42 * s]}>
          <mesh material={M.skin()} position={[0, 0.022, 0]}>
            <boxGeometry args={[0.022, 0.046, 0.02]} />
          </mesh>
          <mesh material={M.skin()} position={[0, 0.058, 0]} rotation={[-curl * 0.5, 0, 0]}>
            <boxGeometry args={[0.018, 0.034, 0.018]} />
          </mesh>
        </group>
        {/* Handgelenk */}
        <mesh material={M.skin()} position={[0, -0.01, 0]}>
          <boxGeometry args={[0.062, 0.03, 0.04]} />
        </mesh>
      </group>
      {/* Ärmel (Jacke) */}
      <mesh material={M.cuff()} position={wrist.clone().add(arm.clone().normalize().multiplyScalar(0.03))} quaternion={armQ}>
        <cylinderGeometry args={[0.042, 0.04, 0.04, 7]} />
      </mesh>
      <mesh material={M.jacket()} position={wrist.clone().add(arm.clone().multiplyScalar(0.5)).add(arm.clone().normalize().multiplyScalar(0.025))} quaternion={armQ}>
        <cylinderGeometry args={[0.05, 0.04, arm.length() - 0.05, 7]} />
      </mesh>
    </group>
  );
};

// Liegende Figur (Schluss-Einstellung), ohne Gesicht – nur Mütze/Hinterkopf
const Person: React.FC = () => (
  <group position={[1.15, 0, 2.3]} rotation={[0, 0.5, 0]}>
    <mesh material={M.jacket()} position={[0, 0.13, 0]}>
      <boxGeometry args={[0.46, 0.24, 0.66]} />
    </mesh>
    <mesh material={M.pants()} position={[-0.11, 0.09, -0.62]}>
      <boxGeometry args={[0.17, 0.16, 0.62]} />
    </mesh>
    <mesh material={M.pants()} position={[0.12, 0.09, -0.6]} rotation={[0, -0.12, 0]}>
      <boxGeometry args={[0.17, 0.16, 0.62]} />
    </mesh>
    <mesh material={M.jacket()} position={[-0.34, 0.1, 0.36]} rotation={[0, 0.5, 0]}>
      <boxGeometry args={[0.13, 0.13, 0.52]} />
    </mesh>
    <mesh material={M.jacket()} position={[0.34, 0.1, 0.38]} rotation={[0, -0.45, 0]}>
      <boxGeometry args={[0.13, 0.13, 0.52]} />
    </mesh>
    <mesh material={M.cuff()} position={[0, 0.15, 0.48]}>
      <icosahedronGeometry args={[0.13, 0]} />
    </mesh>
  </group>
);

// ---------- Kamera je Szene ----------
type Cam = { pos: THREE.Vector3; yaw: number; pitch: number; roll: number };
const camFor = (sh: Shot, t: number): Cam => {
  const d = sh.dur / FPS;
  switch (sh.shot) {
    case "walk": {
      const p = t / d;
      const z = 6.2 - 5.9 * (1 - Math.pow(1 - p, 1.6));
      const step = Math.abs(Math.sin(Math.PI * 1.8 * t));
      const slow = 1 - sm(0.82, 1, p);
      return { pos: V(Math.sin(t * 0.9) * 0.03, 1.62 + step * 0.035 * slow, z), yaw: Math.sin(t * 0.6) * 0.03, pitch: -0.1 - sm(0.75, 1, p) * 0.25, roll: Math.sin(Math.PI * 1.8 * t) * 0.012 * slow };
    }
    case "crack": {
      const tb = 2.75; // Bruch
      const look = sm(0, 0.8, t);
      const fall = cl((t - tb) / 0.62);
      const y = 1.62 - (1.62 + 1.5) * fall * fall;
      const shake = t > 1.2 && t < tb ? Math.sin(t * 61) * 0.004 * sm(1.2, 2.2, t) : 0;
      return { pos: V(shake, y + shake, 0.3 - fall * 0.25), yaw: 0, pitch: -0.35 - look * 0.95 - fall * 0.2, roll: fall * 0.35 + shake * 4 };
    }
    case "under": {
      const up = sm(0.1, 1.5, t);
      return { pos: V(Math.sin(t * 0.8) * 0.06, -1.5 + sm(0.3, d, t) * 0.7, 0.05 + up * 0.85), yaw: Math.sin(t * 0.5) * 0.08, pitch: -1.3 + up * 2.15, roll: 0.35 * (1 - up) + Math.sin(t * 0.9) * 0.05 };
    }
    case "surface": {
      return { pos: V(0, 0.13 + Math.sin(t * 2.1) * 0.025, 0.25), yaw: Math.sin(t * 0.7) * 0.12, pitch: -0.05 + Math.sin(t * 1.6) * 0.03, roll: Math.sin(t * 1.3) * 0.05 };
    }
    case "turn": {
      const k = eio(cl(t / 1.7));
      return { pos: V(0, 0.13 + Math.sin(t * 2.1) * 0.025, 0.25 + k * 0.25), yaw: k * Math.PI, pitch: -0.06 + Math.sin(t * 1.6) * 0.03, roll: Math.sin(t * 1.3) * 0.04 };
    }
    case "arms": {
      const kick = sm(1.3, d, t);
      const bob = Math.sin(t * 9) * 0.012 * (t > 1.3 ? 1 : 0);
      return { pos: V(0, 0.2 + kick * 0.25 + bob, 0.45 + kick * 0.45), yaw: Math.PI, pitch: -0.5 - kick * 0.25, roll: Math.sin(t * 4.5) * 0.03 * (t > 1.3 ? 1 : 0) };
    }
    case "roll": {
      const k = eio(cl(t / (d - 0.3)));
      return { pos: V(-k * 0.95, 0.24 + Math.abs(Math.sin(k * Math.PI)) * 0.06, 1.45 + k * 0.35), yaw: Math.PI, pitch: -0.12, roll: -k * Math.PI * 2 };
    }
    default: {
      const k = t / d;
      return { pos: V(3.4 - k * 0.6, 4.6 + k * 0.4, 5.8 + k * 0.4), yaw: 0, pitch: 0, roll: 0 };
    }
  }
};
const camQuat = (c: Cam) => new THREE.Quaternion().setFromEuler(new THREE.Euler(c.pitch, c.yaw, c.roll, "YXZ"));

// ---------- Welt ----------
export const World: React.FC<{ frame: number }> = ({ frame }) => {
  const sh = SHOTS.find((s) => frame >= s.start && frame < s.start + s.dur) ?? SHOTS[SHOTS.length - 1];
  const t = (frame - sh.start) / FPS;
  const T = frame / FPS;
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const scene = useThree((s) => s.scene);
  const c = camFor(sh, t);
  const q = camQuat(c);
  camera.position.copy(c.pos);
  camera.quaternion.copy(q);
  if (sh.shot === "end") camera.lookAt(0.6, 0, 1.4);
  camera.updateMatrixWorld();
  const under = sh.shot === "under" || (sh.shot === "crack" && c.pos.y < WATER_Y);

  // Nebel/Hintergrund
  const fogAbove = once("fogA", () => new THREE.Fog("#1d2b3c", 18, 175));
  const fogUnder = once("fogU", () => new THREE.FogExp2("#0c3d44", 0.6));
  scene.fog = under ? fogUnder : fogAbove;
  scene.background = under ? once("bgU", () => new THREE.Color("#0b363d")) : null;

  const fwd = V(0, 0, -1).applyQuaternion(q);
  const upv = V(0, 1, 0).applyQuaternion(q);
  const rightv = V(1, 0, 0).applyQuaternion(q);
  const local = (x: number, y: number, z: number) => c.pos.clone().add(rightv.clone().multiplyScalar(x)).add(upv.clone().multiplyScalar(y)).add(fwd.clone().multiplyScalar(z));

  // Schnee (relativ zur Kamera, deterministisch)
  const snow = useMemo(() => {
    const r = rng(99);
    const n = 2600;
    const base = new Float32Array(n * 4);
    for (let i = 0; i < n; i++) {
      base[i * 4] = (r() - 0.5) * 16;
      base[i * 4 + 1] = r() * 9;
      base[i * 4 + 2] = (r() - 0.5) * 16;
      base[i * 4 + 3] = 0.5 + r() * 0.6;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(n * 3), 3));
    return { g, base, n };
  }, []);
  {
    const p = snow.g.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < snow.n; i++) {
      const b = snow.base;
      const sp = b[i * 4 + 3];
      const y = (((b[i * 4 + 1] - T * sp) % 9) + 9) % 9;
      const x = b[i * 4] + Math.sin(T * 0.7 + i) * 0.25 + T * 0.35;
      const wrap = (v: number, cc: number) => ((((v - cc + 8) % 16) + 16) % 16) - 8 + cc;
      let px = wrap(x, c.pos.x), pz = wrap(b[i * 4 + 2], c.pos.z);
      const py = y - 0.5 + Math.max(0, c.pos.y - 1.6);
      const dx = px - c.pos.x, dy = py - c.pos.y, dz = pz - c.pos.z;
      const dd = Math.sqrt(dx * dx + dy * dy + dz * dz);
      if (dd < 0.9) {
        const k = 0.9 / Math.max(dd, 0.05);
        px = c.pos.x + dx * k;
        pz = c.pos.z + dz * k;
      }
      p.setXYZ(i, px, py, pz);
    }
    p.needsUpdate = true;
  }

  // Risse wachsen
  const crackT = sh.shot === "crack" ? (t - 0.35) / 2.2 : sh.i > 1 ? 9 : -1;
  const breakP = sh.shot === "crack" ? cl((t - 2.75) / 0.9) : sh.i > 1 ? 1 : 0;

  // Atem
  const breaths: React.ReactNode[] = [];
  if (["surface", "turn"].includes(sh.shot)) {
    const per = sh.shot === "arms" ? 1.3 : 2.1;
    for (let k = 0; k < 2; k++) {
      const age = ((t + k * per) % (per * 2)) / 1.6;
      if (age > 1) continue;
      for (let j = 0; j < 5; j++) {
        const o = local((j - 2) * 0.012 * (1 + age * 2), -0.1 + Math.sin(j * 2.3) * 0.01 + age * 0.06, 0.32 + age * 0.4 + j * 0.015);
        breaths.push(
          <mesh key={`b${k}${j}`} position={o} scale={0.008 + age * 0.04} material={M.breath()} renderOrder={5}>
            <icosahedronGeometry args={[1, 0]} />
          </mesh>,
        );
      }
    }
  }

  // Blasen unter Wasser
  const bubbles: React.ReactNode[] = [];
  if (under) {
    const r = rng(55);
    for (let i = 0; i < 70; i++) {
      const ph = r(), sp = 0.35 + r() * 0.5, size = 0.006 + r() * 0.02;
      const burst = sh.shot === "under" && t < 1.4 && i < 40;
      const lx = (r() - 0.5) * (burst ? 0.9 : 2.4), lz = burst ? 0.4 + r() * 0.8 : (r() - 0.5) * 2.4;
      const y = burst ? -1.6 + t * (1.2 + r()) + r() * 0.6 : -2.4 + (((T * sp + ph * 3) % 2.6) + 2.6) % 2.6;
      if (y > WATER_Y - 0.02) continue;
      const wob = Math.sin(T * 5 + i) * 0.02;
      bubbles.push(
        <mesh key={`u${i}`} position={[c.pos.x + lx + wob, y, c.pos.z - lz * (burst ? Math.cos(c.yaw) : 1)]} scale={size * (burst ? 1.6 : 1)} material={M.bubble()}>
          <icosahedronGeometry args={[1, 1]} />
        </mesh>,
      );
    }
  }

  // Hände
  let hands: React.ReactNode = null;
  if (sh.shot === "under") {
    const sw = Math.sin(t * 3.2);
    hands = [-1, 1].map((s) => {
      const w = local(s * (0.095 + sw * 0.03), -0.22 + sw * 0.05, 0.48);
      const dir = fwd.clone().multiplyScalar(0.35).add(upv.clone().multiplyScalar(1)).add(rightv.clone().multiplyScalar(s * (0.25 + sw * 0.15)));
      return <Hand key={s} wrist={w} dir={dir} back={fwd.clone().negate().add(rightv.clone().multiplyScalar(-s * 0.2))} shoulder={local(s * 0.22, -0.4, -0.05)} side={s} curl={0.15 + sw * 0.1} />;
    });
  } else if (sh.shot === "arms") {
    hands = [-1, 1].map((s) => {
      const k = eio(cl((t - 0.15 - (s > 0 ? 0.18 : 0)) / 0.9));
      const start = V(-s * 0.15, -0.3, 0.7);
      const end = V(-s * 0.15, ICE_TOP + 0.024, 1.17);
      const w = start.clone().lerp(end, k);
      w.y += Math.sin(k * Math.PI) * 0.18;
      const dir = V(-s * 0.12, 0.9 - k * 0.9, 0.4 + k * 0.6);
      const back = V(0, 1, -0.2 * (1 - k)).add(V(0, 0, -1).multiplyScalar(1 - k));
      return <Hand key={s} wrist={w} dir={dir} back={back} shoulder={local(s * 0.2, -0.5, 0.0)} side={s} curl={0.08} />;
    });
  }

  return (
    <>
      <hemisphereLight args={["#5d7898", "#0b1622", under ? 1.6 : 1.15]} />
      <directionalLight position={[55, 75, -220]} intensity={under ? 0.9 : 1.9} color="#a9c2ff" />
      <directionalLight position={[30, 20, 80]} intensity={0.35} color="#ffb070" />
      <ambientLight intensity={0.12} />
      {under ? <pointLight position={c.pos} intensity={2.2} distance={3} decay={1} color="#bff4ff" /> : null}

      {/* Himmel */}
      <mesh geometry={skyGeo()} position={c.pos}>
        <meshBasicMaterial vertexColors side={THREE.BackSide} fog={false} />
      </mesh>
      <points geometry={starsGeo()} position={c.pos}>
        <pointsMaterial size={1.6} color="#cfd8ff" fog={false} sizeAttenuation={false} transparent opacity={0.8} />
      </points>
      <mesh position={c.pos.clone().add(V(55, 75, -220).normalize().multiplyScalar(300))}>
        <icosahedronGeometry args={[7, 2]} />
        <meshBasicMaterial color="#eef3ff" fog={false} />
      </mesh>
      <sprite position={c.pos.clone().add(V(55, 75, -220).normalize().multiplyScalar(298))} scale={[90, 90, 1]}>
        <spriteMaterial map={glowTex()} color="#9fb6ff" transparent opacity={0.5} depthWrite={false} fog={false} />
      </sprite>

      {/* Ufer, Bäume, Hütte */}
      <mesh geometry={landGeo()} material={M.land()} />
      <Trees />
      <Hut />

      {/* Eis */}
      <mesh geometry={farIceGeo()} material={M.far()} />
      <mesh geometry={nearIceGeo()} material={[M.ice(), M.iceSide()]} />
      {wedges().map((w) => {
        const delay = ((w.k * 7) % 5) * 0.06;
        const b = cl((breakP - delay) / (1 - delay));
        if (b >= 1 && sh.i > 1) return null;
        const ang = b * (1.1 + (w.k % 3) * 0.25);
        const rot = new THREE.Quaternion().setFromAxisAngle(w.axis, ang);
        return (
          <mesh key={w.k} geometry={w.g} material={[M.ice(), M.iceSide()]} position={[w.mid.x, w.mid.y - b * b * 0.6, w.mid.z]} quaternion={rot} />
        );
      })}
      {CRACKS.map((s, i) => {
        const g = cl((crackT - s.t0) / 0.25);
        if (g <= 0 || breakP > 0.15) return null;
        const d = s.b.clone().sub(s.a);
        const len = d.length() * g;
        const ang = Math.atan2(d.y, d.x);
        return (
          <group key={i} position={[s.a.x, ICE_TOP + 0.003, s.a.y]} rotation={[0, -ang, 0]}>
            <mesh material={M.crack()} position={[len / 2, 0, 0]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[len, s.w]} />
            </mesh>
            <mesh material={M.crackHi()} position={[len / 2, 0.001, s.w * 0.9]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[len, s.w * 0.5]} />
            </mesh>
          </group>
        );
      })}
      <Prints />

      {/* Wasser */}
      <mesh position={[0, WATER_Y - 0.05, 0]} rotation={[-Math.PI / 2, 0, 0]} material={M.water()}>
        <planeGeometry args={[300, 300]} />
      </mesh>
      <Waves t={T} amp={sh.i <= 1 ? 0.004 : sh.shot === "arms" ? 0.03 : 0.02} />

      {/* Unter Wasser: helles Loch + Lichtstrahlen */}
      {under ? (
        <>
          <mesh position={[0, WATER_Y - 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]} material={M.holeLight()}>
            <shapeGeometry args={[new THREE.Shape(HOLE.map((p) => new THREE.Vector2(p.x, -p.y)))]} />
          </mesh>
          {[0, 1, 2].map((k) => (
            <mesh key={k} position={[Math.sin(k * 2.1) * 0.6, -1.7, Math.cos(k * 1.7) * 0.55 - 0.5]} rotation={[0.18 + Math.sin(k) * 0.1, 0, Math.cos(k * 1.3) * 0.15]} material={M.shaft()}>
              <cylinderGeometry args={[0.03 + (k % 3) * 0.02, 0.1 + (k % 2) * 0.08, 3.4, 6, 1, true]} />
            </mesh>
          ))}
        </>
      ) : null}

      {sh.shot === "end" ? <Person /> : null}
      {hands}
      {breaths}
      {bubbles}
      {!under ? (
        <points geometry={snow.g}>
          <pointsMaterial map={dotTex()} size={0.045} color="#f4f8ff" transparent opacity={0.9} depthWrite={false} />
        </points>
      ) : null}
    </>
  );
};
