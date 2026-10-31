// Low-Poly-3D-Welt: das alte Medina (Moschee aus Lehm & Palmstämmen, Häuser, Palmen, Wüste),
// dazu Traum-Raum, Wüste von Mekka und Erdkugel. Keine Menschen-Figuren (bewusst).
import * as THREE from "three";

export const rng = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const std = (color: string, extra: Partial<THREE.MeshStandardMaterialParameters> = {}) =>
  new THREE.MeshStandardMaterial({ color, roughness: 1, flatShading: true, ...extra });

const box = (w: number, h: number, d: number, mat: THREE.Material) => {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat);
  return m;
};

let glowTex: THREE.Texture | null = null;
const glowTexture = () => {
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

export const makeGlow = (color: string, size: number, opacity = 1) => {
  const s = new THREE.Sprite(
    new THREE.SpriteMaterial({
      map: glowTexture(),
      color,
      opacity,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      transparent: true,
      fog: false,
    }),
  );
  s.scale.set(size, size, 1);
  return s;
};

const crescentTexture = () => {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d")!;
  g.fillStyle = "#fff6dc";
  g.beginPath();
  g.arc(128, 128, 90, 0, Math.PI * 2);
  g.fill();
  g.globalCompositeOperation = "destination-out";
  g.beginPath();
  g.arc(168, 104, 84, 0, Math.PI * 2);
  g.fill();
  return new THREE.CanvasTexture(c);
};

// ---------- Himmel ----------
export const makeSky = () => {
  const uniforms = {
    uDawn: { value: 0 },
    uHeat: { value: 0 },
    uSpace: { value: 0 },
  };
  const mat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    depthWrite: false,
    fog: false,
    uniforms,
    vertexShader: `varying vec3 vPos; void main(){ vPos = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `varying vec3 vPos; uniform float uDawn; uniform float uHeat; uniform float uSpace;
      vec3 grad(vec3 hor, vec3 mid, vec3 top, float h){
        vec3 c = mix(hor, mid, smoothstep(0.0, 0.14, h));
        return mix(c, top, smoothstep(0.14, 0.65, h));
      }
      void main(){
        float h = clamp(vPos.y, -0.1, 1.0);
        vec3 night = grad(vec3(0.20,0.24,0.42), vec3(0.08,0.12,0.30), vec3(0.02,0.04,0.13), h);
        vec3 dawn  = grad(vec3(0.98,0.66,0.42), vec3(0.55,0.45,0.62), vec3(0.12,0.17,0.40), h);
        vec3 heat  = grad(vec3(1.00,0.93,0.74), vec3(0.98,0.72,0.42), vec3(0.80,0.46,0.25), h);
        vec3 col = mix(night, dawn, uDawn);
        col = mix(col, heat, uHeat);
        col = mix(col, vec3(0.005,0.008,0.03), uSpace);
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  const sky = new THREE.Mesh(new THREE.SphereGeometry(40000, 32, 16), mat);
  sky.renderOrder = -2;
  return { sky, uniforms };
};

export const makeStars = (rand: () => number) => {
  const n = 2600;
  const pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) {
    const th = rand() * Math.PI * 2;
    const y = Math.pow(rand(), 0.7) * 0.98 + 0.02;
    const r = Math.sqrt(1 - y * y);
    pos.set([Math.cos(th) * r * 30000, y * 30000, Math.sin(th) * r * 30000], i * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  return new THREE.Points(
    g,
    new THREE.PointsMaterial({
      color: "#fff8e8",
      size: 2.6,
      sizeAttenuation: false,
      transparent: true,
      fog: false,
      depthWrite: false,
    }),
  );
};

export const MOON_POS = new THREE.Vector3(-6000, 7000, -20000);
export const makeMoon = () => {
  const g = new THREE.Group();
  const moon = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: crescentTexture(), transparent: true, fog: false, depthWrite: false }),
  );
  moon.scale.set(2400, 2400, 1);
  g.add(moon, makeGlow("#ffe9b0", 6000, 0.35));
  g.position.copy(MOON_POS);
  return g;
};

// ---------- Palme ----------
const addPalm = (
  trunks: THREE.InstancedMesh,
  fronds: THREE.InstancedMesh,
  ti: number,
  fi: number,
  x: number,
  z: number,
  h: number,
  rand: () => number,
) => {
  const m = new THREE.Matrix4();
  const lean = (rand() - 0.5) * 0.2;
  m.compose(
    new THREE.Vector3(x, h / 2, z),
    new THREE.Quaternion().setFromEuler(new THREE.Euler(lean, 0, lean * 0.7)),
    new THREE.Vector3(1, h, 1),
  );
  trunks.setMatrixAt(ti, m);
  const top = new THREE.Vector3(x + Math.sin(lean * 0.7) * -h * 0.5, h, z + Math.sin(lean) * h * 0.5);
  for (let k = 0; k < 8; k++) {
    const yaw = (k / 8) * Math.PI * 2 + rand() * 0.4;
    const pitch = 0.35 + rand() * 0.55;
    const len = 0.8 + rand() * 0.35;
    m.compose(
      top,
      new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch, yaw, 0, "YXZ")),
      new THREE.Vector3(len, 1, len),
    );
    fronds.setMatrixAt(fi + k, m);
  }
};

// ---------- Medina ----------
export const TALL_HOUSE = new THREE.Vector3(25, 0, 6); // Haus der Frau aus Banu Najjar (höchstes Haus)
export const TALL_ROOF_Y = 9;
export const ABDULLAH_HOUSE = new THREE.Vector3(-46, 0, 34);
export const UMAR_HOUSE = new THREE.Vector3(-30, 0, -46);

// Bereiche, durch die Kameras fliegen -> keine Häuser/Palmen
const CORRIDORS: [number, number, number, number][] = [
  [-12, 12, 17, 95], // Anflug auf die Moschee (x1, x2, z1, z2)
  [-85, -22, -6, 6], // Gasse am Morgen
  [-40, -20, -43, -6], // Weg zu Umars Haus
  [-30, 0, 30, 80], // Blick auf Abdullahs Haus
];
const inCorridor = (x: number, z: number, pad = 0) =>
  CORRIDORS.some(([x1, x2, z1, z2]) => x > x1 - pad && x < x2 + pad && z > z1 - pad && z < z2 + pad);

export const buildMedina = () => {
  const rand = rng(7);
  const g = new THREE.Group();

  const sand = std("#b48b5f");
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(80000, 80000), sand);
  ground.rotation.x = -Math.PI / 2;
  g.add(ground);

  // Dünen & Berge (Uhud im Norden)
  const dune = std("#a27a52");
  for (let i = 0; i < 40; i++) {
    const d = new THREE.Mesh(new THREE.SphereGeometry(1, 10, 6), dune);
    const ang = rand() * Math.PI * 2;
    const dist = 500 + rand() * 1500;
    d.position.set(Math.cos(ang) * dist, -8, Math.sin(ang) * dist);
    d.scale.set(80 + rand() * 160, 18 + rand() * 30, 60 + rand() * 120);
    g.add(d);
  }
  const rock = std("#4a3a33");
  for (let i = 0; i < 9; i++) {
    const mtn = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 7), rock);
    mtn.position.set(-3000 + i * 750 + rand() * 300, 0, -5000 - rand() * 1500);
    const s = 900 + rand() * 900;
    mtn.scale.set(s, 400 + rand() * 500, s * 0.7);
    mtn.rotation.y = rand() * 3;
    g.add(mtn);
  }

  // --- Moschee: Lehmmauern, Säulen aus Palmstämmen, Dach aus Palmwedeln ---
  const mud = std("#c49a6c");
  const mudDark = std("#9c7650");
  const W = 34;
  const wallH = 3.4;
  const wall = (w: number, d: number, x: number, z: number) => {
    const b = box(w, wallH, d, mud);
    b.position.set(x, wallH / 2, z);
    g.add(b);
  };
  wall(W, 0.8, 0, -W / 2); // Nord
  wall(13, 0.8, -10.5, W / 2); // Süd links (Eingang in der Mitte)
  wall(13, 0.8, 10.5, W / 2); // Süd rechts
  wall(0.8, 14, -W / 2, -10); // West
  wall(0.8, 14, -W / 2, 10);
  wall(0.8, 14, W / 2, -10); // Ost
  wall(0.8, 14, W / 2, 10);
  const palmWood = std("#6b4a2e");
  for (let r = 0; r < 3; r++) {
    for (let c = 0; c < 9; c++) {
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, wallH, 7), palmWood);
      col.position.set(-14 + c * 3.5, wallH / 2, -14.2 + r * 2.6);
      g.add(col);
    }
  }
  const roof = box(W - 1, 0.25, 8.5, std("#5b4a2c"));
  roof.position.set(0, wallH, -12.6);
  g.add(roof);
  // Wedel-Struktur auf dem Dach
  for (let i = 0; i < 24; i++) {
    const f = box(1.2, 0.12, 8.6, std(i % 2 ? "#4c5a2c" : "#5d5530"));
    f.position.set(-15.5 + i * 1.35, wallH + 0.15, -12.6);
    f.rotation.z = (rand() - 0.5) * 0.2;
    g.add(f);
  }

  // --- Häuser ---
  const houseColors = ["#c9a274", "#b8906a", "#d2ae80", "#a98260", "#bf9a70"];
  const houses = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), std("#ffffff"), 420);
  const windows = new THREE.InstancedMesh(
    new THREE.BoxGeometry(0.9, 0.9, 0.12),
    new THREE.MeshBasicMaterial({ color: "#ffbf60" }),
    300,
  );
  const darkWin = new THREE.InstancedMesh(new THREE.BoxGeometry(0.9, 1.6, 0.12), std("#2a1c14"), 400);
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const col = new THREE.Color();
  let hi = 0;
  let wi = 0;
  let di = 0;
  const windowGlows = new THREE.Group();
  const reserved = [TALL_HOUSE, ABDULLAH_HOUSE, UMAR_HOUSE];
  for (let gx = -12; gx <= 12; gx++) {
    for (let gz = -12; gz <= 12; gz++) {
      const x = gx * 10 + (rand() - 0.5) * 3;
      const z = gz * 10 + (rand() - 0.5) * 3;
      const r = Math.hypot(x, z);
      if (Math.abs(x) < 24 && Math.abs(z) < 24) continue; // Moschee frei
      if (gx % 4 === 0 || gz % 5 === 0) continue; // Gassen
      if (r > 125 || rand() < 0.15 + r / 400) continue;
      if (reserved.some((p) => Math.hypot(p.x - x, p.z - z) < 9)) continue;
      if (inCorridor(x, z, 5)) continue;
      if (hi >= 420) break;
      const w = 5 + rand() * 3.5;
      const d = 5 + rand() * 3.5;
      const h = 3 + rand() * 3;
      m.compose(new THREE.Vector3(x, h / 2, z), q, new THREE.Vector3(w, h, d));
      houses.setMatrixAt(hi, m);
      col.set(houseColors[Math.floor(rand() * houseColors.length)]);
      houses.setColorAt(hi++, col);
      // Fenster/Tür zur Straße
      const lit = rand() < 0.3 && wi < 300;
      const wz = z + d / 2 + 0.03;
      if (lit) {
        m.makeTranslation(x + (rand() - 0.5) * (w - 2), h * 0.6, wz);
        windows.setMatrixAt(wi++, m);
        if (windowGlows.children.length < 80) {
          const gl = makeGlow("#ffad4a", 4, 0.6);
          gl.position.set(x, h * 0.6, wz + 0.4);
          windowGlows.add(gl);
        }
      } else if (di < 400) {
        m.makeTranslation(x + (rand() - 0.5) * (w - 2), 0.8, wz);
        darkWin.setMatrixAt(di++, m);
      }
    }
  }
  houses.count = hi;
  windows.count = wi;
  darkWin.count = di;
  g.add(houses, windows, darkWin, windowGlows);

  // Höchstes Haus neben der Moschee (Bilals Ort für den Adhan)
  const tall = box(8, TALL_ROOF_Y, 8, std("#d0a878"));
  tall.position.set(TALL_HOUSE.x, TALL_ROOF_Y / 2, TALL_HOUSE.z);
  const parapet = box(8.4, 0.6, 8.4, mudDark);
  parapet.position.set(TALL_HOUSE.x, TALL_ROOF_Y + 0.3, TALL_HOUSE.z);
  const inner = box(7.4, 0.7, 7.4, std("#b88f62"));
  inner.position.set(TALL_HOUSE.x, TALL_ROOF_Y + 0.36, TALL_HOUSE.z);
  g.add(tall, parapet, inner);

  // Haus von Abdullah ibn Zaid (Fenster leuchtet)
  const ah = box(9, 4.5, 8, std("#c39b6e"));
  ah.position.set(ABDULLAH_HOUSE.x, 2.25, ABDULLAH_HOUSE.z);
  const aw = box(1.4, 1.2, 0.15, new THREE.MeshBasicMaterial({ color: "#ffc070" }));
  aw.position.set(ABDULLAH_HOUSE.x + 1.5, 2.8, ABDULLAH_HOUSE.z + 4.05);
  const awg = makeGlow("#ffb050", 7, 0.8);
  awg.position.set(ABDULLAH_HOUSE.x + 1.5, 2.8, ABDULLAH_HOUSE.z + 4.6);
  g.add(ah, aw, awg);

  // Haus von Umar (Tür öffnet sich -> Licht)
  const uh = box(10, 4.8, 8, std("#bd956a"));
  uh.position.set(UMAR_HOUSE.x, 2.4, UMAR_HOUSE.z);
  const door = box(1.6, 2.6, 0.15, new THREE.MeshBasicMaterial({ color: "#ffd08a" }));
  door.position.set(UMAR_HOUSE.x, 1.3, UMAR_HOUSE.z + 4.05);
  const doorGlow = makeGlow("#ffc070", 10, 1);
  doorGlow.position.set(UMAR_HOUSE.x, 1.5, UMAR_HOUSE.z + 4.8);
  g.add(uh, door, doorGlow);

  // --- Palmen ---
  const PALMS = 260;
  const trunkGeo = new THREE.CylinderGeometry(0.18, 0.3, 1, 6);
  trunkGeo.translate(0, 0, 0);
  const trunks = new THREE.InstancedMesh(trunkGeo, std("#6a4b30"), PALMS);
  const frondGeo = new THREE.BoxGeometry(0.9, 0.06, 4.2);
  frondGeo.translate(0, 0, 2.1);
  const fronds = new THREE.InstancedMesh(frondGeo, std("#4f6b2c"), PALMS * 8);
  let p = 0;
  while (p < PALMS) {
    // Palmenhaine am Stadtrand + einzelne in der Stadt
    const grove = rand() < 0.8;
    const ang = rand() * Math.PI * 2;
    const dist = grove ? 120 + rand() * 260 : 30 + rand() * 90;
    const x = Math.cos(ang) * dist;
    const z = Math.sin(ang) * dist;
    if (Math.abs(x) < 22 && Math.abs(z) < 22) continue;
    if (inCorridor(x, z, 6)) continue;
    addPalm(trunks, fronds, p, p * 8, x, z, 7 + rand() * 6, rand);
    p++;
  }
  g.add(trunks, fronds);

  // Laternen unter dem Moscheedach
  const lanterns = new THREE.Group();
  for (let i = 0; i < 6; i++) {
    const l = makeGlow("#ffb45a", 6, 0.9);
    l.position.set(-12.5 + i * 5, 2.6, -11.5);
    lanterns.add(l);
  }
  g.add(lanterns);

  return { group: g, lanterns, doorGlow };
};

// ---------- Symbole: Glocke, Horn, Feuer ----------
export const makeBell = (color = "#e8c26a") => {
  const pts = [
    [0, 1.4],
    [0.25, 1.38],
    [0.45, 1.2],
    [0.55, 0.8],
    [0.65, 0.3],
    [0.9, 0.0],
    [0.95, -0.12],
  ].map(([x, y]) => new THREE.Vector2(x, y));
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({
    color,
    metalness: 0.8,
    roughness: 0.3,
    emissive: color,
    emissiveIntensity: 0.25,
    side: THREE.DoubleSide,
  });
  g.add(new THREE.Mesh(new THREE.LatheGeometry(pts, 24), mat));
  const clapper = new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 8), mat);
  clapper.position.y = 0.05;
  const handle = new THREE.Mesh(new THREE.TorusGeometry(0.18, 0.06, 8, 16), mat);
  handle.position.y = 1.55;
  g.add(clapper, handle);
  return g;
};

export const makeHorn = () => {
  const g = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: "#f0dcb4", roughness: 0.5, emissive: "#a07a4a", emissiveIntensity: 0.5, flatShading: true });
  const segs = 22;
  for (let i = 0; i < segs; i++) {
    const t = i / segs;
    const r = 0.08 + t * t * 0.5;
    const seg = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.08, r, 0.2, 14), mat);
    const a = -0.3 + t * Math.PI * 0.85;
    seg.position.set(Math.sin(a) * 1.3 - 0.4, Math.cos(a) * 1.3 - 0.3, 0);
    seg.rotation.z = -a;
    g.add(seg);
  }
  return g;
};

export const makeFire = () => {
  const g = new THREE.Group();
  const flames: THREE.Mesh[] = [];
  const colors = ["#ff5a1f", "#ff9a2e", "#ffd25a"];
  for (let i = 0; i < 3; i++) {
    const f = new THREE.Mesh(
      new THREE.ConeGeometry(0.7 - i * 0.18, 2 - i * 0.4, 8),
      new THREE.MeshBasicMaterial({ color: colors[i], transparent: true, opacity: 0.9 - i * 0.1 }),
    );
    f.position.y = 1 - i * 0.15;
    flames.push(f);
    g.add(f);
  }
  const wood = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 1.6, 6), std("#4a2e1a"));
  wood.rotation.z = Math.PI / 2;
  const wood2 = wood.clone();
  wood2.rotation.y = Math.PI / 2;
  g.add(wood, wood2, makeGlow("#ff7a2a", 6, 0.9));
  g.userData.flames = flames;
  return g;
};

// ---------- Erdkugel ----------
export const makeGlobe = () => {
  const rand = rng(99);
  const g = new THREE.Group();
  const earth = new THREE.Mesh(
    new THREE.IcosahedronGeometry(50, 4),
    new THREE.MeshStandardMaterial({ color: "#1b3a6b", roughness: 0.9, flatShading: true, emissive: "#06122a" }),
  );
  g.add(earth);
  // Kontinente grob als Flecken
  const land = new THREE.InstancedMesh(
    new THREE.IcosahedronGeometry(1, 0),
    new THREE.MeshStandardMaterial({ color: "#3d6b3a", flatShading: true, emissive: "#0c1a0c" }),
    1000,
  );
  const lights = new THREE.Group();
  const m = new THREE.Matrix4();
  const blobs = [
    [20, 15], [30, 40], [25, 75], [0, 20], [-20, 25], [50, 100], [35, -100], [-15, -60], [40, -5], [55, 60], [-25, 135],
  ];
  let n = 0;
  for (const [lat, lon] of blobs) {
    for (let k = 0; k < 90 && n < 1000; k++) {
      const la = ((lat + (rand() - 0.5) * 30) * Math.PI) / 180;
      const lo = ((lon + (rand() - 0.5) * 40) * Math.PI) / 180;
      const v = new THREE.Vector3(Math.cos(la) * Math.cos(lo), Math.sin(la), Math.cos(la) * Math.sin(lo)).multiplyScalar(49.5);
      const s = 1.6 + rand() * 2.2;
      m.compose(v, new THREE.Quaternion(), new THREE.Vector3(s, s, s));
      land.setMatrixAt(n++, m);
      if (rand() < 0.35) {
        const l = makeGlow("#ffd27a", 2.5 + rand() * 2, 0.9);
        l.position.copy(v.clone().multiplyScalar(1.05));
        lights.add(l);
      }
    }
  }
  land.count = n;
  g.add(land, lights);
  g.add(makeGlow("#5aa0ff", 150, 0.35));
  return g;
};
