// Low-Poly-3D-Welt: Gleise, Masten, Felder, Büsche, Hügel, Himmel, Zug, Signale.
// Alles deterministisch (fester Zufalls-Seed), damit jedes Frame gleich aussieht.
import * as THREE from "three";

export const TRACK_X = 0; // unser Gleis
export const TRACK2_X = -4.6; // Nachbargleis
const Z_FRONT = 2500;
const Z_END = -17000;

const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const box = (w: number, h: number, d: number, mat: THREE.Material) =>
  new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);

let glowTex: THREE.Texture | null = null;
export const glowTexture = () => {
  if (glowTex) return glowTex;
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grd = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grd.addColorStop(0, "rgba(255,255,255,1)");
  grd.addColorStop(0.2, "rgba(255,255,255,0.55)");
  grd.addColorStop(0.5, "rgba(255,255,255,0.12)");
  grd.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grd;
  g.fillRect(0, 0, 128, 128);
  glowTex = new THREE.CanvasTexture(c);
  return glowTex;
};

export const makeGlow = (color: string, size: number) => {
  const s = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture(),
      color,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      fog: false,
    }),
  );
  s.scale.set(size, size, 1);
  return s;
};

const makeSky = () => {
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms: {},
    vertexShader: `varying vec3 vPos; void main(){ vPos = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vPos;
      void main(){
        float h = clamp(vPos.y, -0.1, 1.0);
        vec3 horizon = vec3(0.86,0.66,0.76);
        vec3 mid = vec3(0.42,0.43,0.68);
        vec3 top = vec3(0.13,0.18,0.42);
        vec3 col = mix(horizon, mid, smoothstep(0.0, 0.12, h));
        col = mix(col, top, smoothstep(0.12, 0.6, h));
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(40000, 32, 16), mat);
  sky.renderOrder = -1;
  return sky;
};

const makeTrack = (x: number, rand: () => number) => {
  const g = new THREE.Group();
  const len = Z_FRONT - Z_END;
  const mid = (Z_FRONT + Z_END) / 2;
  const ballast = box(4.2, 0.45, len, new THREE.MeshStandardMaterial({ color: "#55546a", roughness: 1 }));
  ballast.position.set(x, 0.2, mid);
  g.add(ballast);
  const railMat = new THREE.MeshStandardMaterial({ color: "#d8dcef", metalness: 0.8, roughness: 0.25, emissive: "#3b3f5a" });
  for (const side of [-0.72, 0.72]) {
    const r = box(0.09, 0.16, len, railMat);
    r.position.set(x + side, 0.55, mid);
    g.add(r);
  }
  // Schwellen (nur im Nahbereich)
  const n = 3200;
  const sleeper = new THREE.InstancedMesh(
    new THREE.BoxGeometry(2.6, 0.12, 0.25),
    new THREE.MeshStandardMaterial({ color: "#3c3a44", roughness: 1 }),
    n,
  );
  const m = new THREE.Matrix4();
  for (let i = 0; i < n; i++) {
    m.makeTranslation(x, 0.45, 600 - i * 1.4 + rand() * 0.02);
    sleeper.setMatrixAt(i, m);
  }
  g.add(sleeper);
  return g;
};

const makeMasts = () => {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: "#1d1d26", roughness: 0.8 });
  const step = 65;
  const count = Math.floor((Z_FRONT - Z_END) / step);
  const pole = new THREE.InstancedMesh(new THREE.BoxGeometry(0.35, 7.5, 0.35), mat, count * 2);
  const arm = new THREE.InstancedMesh(new THREE.BoxGeometry(5.2, 0.12, 0.12), mat, count * 2);
  const m = new THREE.Matrix4();
  for (let i = 0; i < count; i++) {
    const z = Z_FRONT - i * step;
    m.makeTranslation(3.3, 3.75, z);
    pole.setMatrixAt(i * 2, m);
    m.makeTranslation(-7.9, 3.75, z);
    pole.setMatrixAt(i * 2 + 1, m);
    m.makeTranslation(1.0, 6.9, z);
    arm.setMatrixAt(i * 2, m);
    m.makeTranslation(-5.6, 6.9, z);
    arm.setMatrixAt(i * 2 + 1, m);
  }
  g.add(pole, arm);
  const wireMat = new THREE.MeshBasicMaterial({ color: "#11121a" });
  for (const x of [TRACK_X, TRACK2_X]) {
    for (const y of [6.3, 6.85]) {
      const w = box(0.04, 0.04, Z_FRONT - Z_END, wireMat);
      w.position.set(x, y, (Z_FRONT + Z_END) / 2);
      g.add(w);
    }
  }
  return g;
};

const makeLandscape = (rand: () => number) => {
  const g = new THREE.Group();
  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(80000, 80000),
    new THREE.MeshStandardMaterial({ color: "#5e535a", roughness: 1 }),
  );
  ground.rotation.x = -Math.PI / 2;
  g.add(ground);

  // Felder (leicht unterschiedliche Brauntöne)
  const fieldColors = ["#5a4a40", "#4d4448", "#62523f", "#453f47"];
  for (let i = 0; i < 260; i++) {
    const w = 60 + rand() * 220;
    const d = 80 + rand() * 400;
    const side = rand() < 0.5 ? -1 : 1;
    const f = new THREE.Mesh(
      new THREE.PlaneGeometry(w, d),
      new THREE.MeshStandardMaterial({ color: fieldColors[i % 4], roughness: 1 }),
    );
    f.rotation.x = -Math.PI / 2;
    f.position.set(side * (14 + w / 2 + rand() * 500), 0.02 + i * 0.0005, Z_FRONT - rand() * (Z_FRONT - Z_END));
    g.add(f);
  }

  // Büsche/Bäume in Reihen (wie Plantagen) + verstreut
  const N = 9000;
  const bush = new THREE.InstancedMesh(
    new THREE.IcosahedronGeometry(1, 0),
    new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 1, flatShading: true }),
    N,
  );
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const col = new THREE.Color();
  let i = 0;
  while (i < N) {
    // Plantage: Raster-Block
    const side = rand() < 0.5 ? -1 : 1;
    const near = rand() < 0.8;
    const cz = near ? 500 - rand() * 1500 : Z_FRONT - rand() * (Z_FRONT - Z_END);
    const cx = side * (11 + rand() * (near ? 160 : 600));
    const rows = 4 + Math.floor(rand() * 6);
    const cols = 6 + Math.floor(rand() * 14);
    const gap = 5 + rand() * 3;
    for (let r = 0; r < rows && i < N; r++) {
      for (let c = 0; c < cols && i < N; c++) {
        const s = 1.3 + rand() * 1.2;
        m.compose(
          new THREE.Vector3(cx + side * r * gap, s * 0.8, cz - c * gap),
          q,
          new THREE.Vector3(s, s * 0.9, s),
        );
        bush.setMatrixAt(i, m);
        col.setHSL(0.3 + rand() * 0.12, 0.18 + rand() * 0.12, 0.17 + rand() * 0.07);
        bush.setColorAt(i, col);
        i++;
      }
    }
  }
  g.add(bush);

  // dichte Buschreihen direkt am Gleis (für die tiefen Kamerafahrten)
  const N2 = 5000;
  const near = new THREE.InstancedMesh(
    new THREE.IcosahedronGeometry(1, 0),
    new THREE.MeshStandardMaterial({ color: "#ffffff", roughness: 1, flatShading: true }),
    N2,
  );
  for (let k = 0; k < N2; k++) {
    const side = rand() < 0.5 ? -1 : 1;
    const x = side > 0 ? 6 + Math.pow(rand(), 1.6) * 70 : -10.5 - Math.pow(rand(), 1.6) * 70;
    const z = 700 - rand() * 2600;
    // Lichtung für die Kameras neben dem Gleis
    if (x > 0 && x < 30 && z > -150 && z < 10) {
      k--;
      continue;
    }
    const sc = 0.5 + rand() * 1.4;
    m.compose(new THREE.Vector3(x, sc * 0.6, z), q, new THREE.Vector3(sc * 1.3, sc, sc * 1.3));
    near.setMatrixAt(k, m);
    col.setHSL(0.28 + rand() * 0.14, 0.2 + rand() * 0.12, 0.16 + rand() * 0.08);
    near.setColorAt(k, col);
  }
  g.add(near);

  // Hügel am Horizont
  const hillMat = new THREE.MeshStandardMaterial({ color: "#1f2030", roughness: 1, flatShading: true });
  for (let h = 0; h < 46; h++) {
    const hill = new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8), hillMat);
    const ang = rand() * Math.PI * 2;
    const dist = 9000 + rand() * 9000;
    hill.position.set(Math.cos(ang) * dist, -60, Math.sin(ang) * dist - 3000);
    hill.scale.set(2000 + rand() * 3000, 200 + rand() * 350, 2000 + rand() * 3000);
    g.add(hill);
  }
  return g;
};

export const buildWorld = () => {
  const rand = rng(42);
  const g = new THREE.Group();
  g.add(makeSky(), makeLandscape(rand), makeTrack(TRACK_X, rand), makeTrack(TRACK2_X, rand), makeMasts());
  return g;
};

// ---------- Zug ----------
export const CAR_LEN = 25;
export const CARS = 8;

export const buildTrain = () => {
  const train = new THREE.Group();
  const white = new THREE.MeshStandardMaterial({ color: "#e4e7f2", roughness: 0.35, metalness: 0.25 });
  const dark = new THREE.MeshStandardMaterial({ color: "#14161f", roughness: 0.3 });
  const red = new THREE.MeshStandardMaterial({ color: "#d1203a", emissive: "#5a0612", roughness: 0.5 });
  const windowLit = new THREE.MeshStandardMaterial({ color: "#ffd27a", emissive: "#ffb54a", emissiveIntensity: 0.9 });
  const under = new THREE.MeshStandardMaterial({ color: "#2a2c36", roughness: 0.9 });

  for (let c = 0; c < CARS; c++) {
    const car = new THREE.Group();
    const lead = c === 0;
    const bodyLen = lead ? CAR_LEN - 7 : CAR_LEN - 0.6;
    const offset = lead ? 7 + bodyLen / 2 : bodyLen / 2;
    const body = box(3.0, 3.1, bodyLen, white);
    body.position.set(0, 2.45, offset);
    const band = box(3.04, 0.75, bodyLen - 0.4, lead ? dark : windowLit);
    band.position.set(0, 2.85, offset);
    const stripe = box(3.04, 0.22, bodyLen - 0.2, red);
    stripe.position.set(0, 1.6, offset);
    const skirt = box(2.8, 0.7, bodyLen, under);
    skirt.position.set(0, 0.95, offset);
    car.add(body, band, stripe, skirt);
    if (lead) {
      // Lok-Fenster beleuchtet nur hinten
      const lit = box(3.05, 0.75, 8, windowLit);
      lit.position.set(0, 2.85, offset + bodyLen / 2 - 5);
      car.add(lit);
      // Nase
      const nose = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2), white);
      nose.rotation.x = -Math.PI / 2;
      nose.scale.set(1.5, 7.2, 1.55);
      nose.position.set(0, 2.45, 7.05);
      const windshield = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 12, 0, Math.PI * 2, 0, Math.PI / 2), dark);
      windshield.rotation.x = -Math.PI / 2;
      windshield.scale.set(1.25, 4.2, 0.95);
      windshield.position.set(0, 3.0, 7.0);
      car.add(nose, windshield);
      // Scheinwerfer + Lichtkegel
      for (const sx of [-0.8, 0.8]) {
        const lamp = new THREE.Mesh(
          new THREE.SphereGeometry(0.16, 10, 8),
          new THREE.MeshBasicMaterial({ color: "#ffffff" }),
        );
        lamp.position.set(sx, 1.55, 1.6);
        const glow = makeGlow("#cfe8ff", 3);
        glow.position.copy(lamp.position).add(new THREE.Vector3(0, 0, -0.3));
        car.add(lamp, glow);
      }
      // Lichtschein auf dem Gleis
      const pool = new THREE.Mesh(
        new THREE.PlaneGeometry(5, 70),
        new THREE.MeshBasicMaterial({
          color: "#7fc8ff",
          transparent: true,
          opacity: 0.22,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
        }),
      );
      pool.rotation.x = -Math.PI / 2;
      pool.position.set(0, 0.62, -35);
      car.add(pool);
    }
    car.position.z = c * CAR_LEN;
    train.add(car);
  }
  return train;
};

// ---------- Signal ----------
export const buildSignal = () => {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: "#16171f", roughness: 0.7 });
  const mast = box(0.22, 5.2, 0.22, mat);
  mast.position.y = 2.6;
  const head = box(0.7, 1.6, 0.4, mat);
  head.position.y = 5.6;
  const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.2, 12, 8), new THREE.MeshBasicMaterial({ color: "#ff2020" }));
  lamp.position.set(0, 5.9, -0.22);
  const glow = makeGlow("#ff2020", 4);
  glow.position.set(0, 5.9, -0.5);
  g.add(mast, head, lamp, glow);
  g.userData = { lamp, glow };
  return g;
};
