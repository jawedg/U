import React, { useMemo } from "react";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import {
  buildMedina,
  makeBell,
  makeFire,
  makeGlobe,
  makeGlow,
  makeHorn,
  makeMoon,
  makeSky,
  makeStars,
  rng,
  TALL_HOUSE,
  TALL_ROOF_Y,
} from "./world";
import { ShotState } from "./shots";

const c = (hex: string) => new THREE.Color(hex);
const mix = (a: THREE.Color, b: THREE.Color, t: number) => a.clone().lerp(b, Math.min(1, Math.max(0, t)));

export const AthanScene: React.FC<{ s: ShotState; time: number }> = ({ s, time }) => {
  const { camera, scene } = useThree();

  const w = useMemo(() => {
    const rand = rng(3);
    const { sky, uniforms } = makeSky();
    const stars = makeStars(rand);
    const moon = makeMoon();
    const medina = buildMedina();

    // Symbole über der Moschee
    const bell = makeBell();
    bell.position.set(-5.5, 13, 0);
    bell.scale.setScalar(2.2);
    const horn = makeHorn();
    horn.position.set(0, 13, 0);
    horn.scale.setScalar(2.2);
    const fire = makeFire();
    fire.position.set(5.5, 11.5, 0);
    fire.scale.setScalar(1.8);
    const symGlows = [-5.5, 0, 5.5].map((x) => {
      const g = makeGlow("#ffcf7a", 12, 0.5);
      g.position.set(x, 13.5, -0.5);
      return g;
    });
    const symbols = new THREE.Group();
    symbols.add(bell, horn, fire, ...symGlows);

    // Traum
    const dream = new THREE.Group();
    const dBell = makeBell("#f0d080");
    dBell.position.set(0, -0.3, 0);
    const green = makeGlow("#3dff9a", 16, 0.75);
    green.position.set(0, 0.8, -2.5);
    const gold = makeGlow("#ffd27a", 30, 1);
    gold.position.set(0, 0.8, -1);
    const motes = new THREE.Group();
    for (let i = 0; i < 60; i++) {
      const m = makeGlow(i % 3 ? "#9dffcf" : "#ffe6a0", 0.25 + rand() * 0.35, 0.9);
      m.userData = { x: (rand() - 0.5) * 14, y: (rand() - 0.5) * 8, z: -rand() * 8, sp: 0.2 + rand() * 0.5 };
      motes.add(m);
    }
    dream.add(dBell, green, gold, motes);

    // Wüste von Mekka
    const desert = new THREE.Group();
    const dGround = new THREE.Mesh(
      new THREE.PlaneGeometry(20000, 20000),
      new THREE.MeshStandardMaterial({ color: "#d69a5c", roughness: 1 }),
    );
    dGround.rotation.x = -Math.PI / 2;
    const rockMat = new THREE.MeshStandardMaterial({ color: "#7a5a44", roughness: 1, flatShading: true });
    const rock = new THREE.Mesh(new THREE.DodecahedronGeometry(1.6, 0), rockMat);
    rock.position.set(0, 0.9, 0);
    rock.scale.set(1.3, 0.75, 1);
    desert.add(dGround, rock);
    for (let i = 0; i < 40; i++) {
      const st = new THREE.Mesh(new THREE.DodecahedronGeometry(1, 0), rockMat);
      const a = rand() * Math.PI * 2;
      const d = 8 + rand() * 150;
      st.position.set(Math.cos(a) * d, 0, Math.sin(a) * d - 30);
      st.scale.setScalar(0.3 + rand() * 2.5);
      desert.add(st);
    }
    const hills = new THREE.MeshStandardMaterial({ color: "#8a5a3c", roughness: 1, flatShading: true });
    for (let i = 0; i < 10; i++) {
      const h = new THREE.Mesh(new THREE.ConeGeometry(1, 1, 6), hills);
      h.position.set(-1500 + i * 330, 0, -1400 - rand() * 400);
      h.scale.set(300 + rand() * 300, 120 + rand() * 200, 250);
      desert.add(h);
    }
    const sun = makeGlow("#fff4c8", 900, 1);
    sun.position.set(-260, 420, -1500);
    const sunCore = makeGlow("#ffffff", 260, 1);
    sunCore.position.copy(sun.position);
    desert.add(sun, sunCore);

    // Erde
    const globe = makeGlobe();

    // Licht auf dem Dach + Schallwellen
    const roofGlow = makeGlow("#ffd27a", 14, 1);
    roofGlow.position.set(TALL_HOUSE.x, TALL_ROOF_Y + 1.6, TALL_HOUSE.z);
    const waves = new THREE.Group();
    for (let i = 0; i < 6; i++) {
      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(1, 0.012, 6, 96),
        new THREE.MeshBasicMaterial({
          color: "#ffe2a0",
          transparent: true,
          blending: THREE.AdditiveBlending,
          depthWrite: false,
          fog: false,
        }),
      );
      ring.rotation.x = Math.PI / 2;
      waves.add(ring);
    }
    waves.position.set(TALL_HOUSE.x, TALL_ROOF_Y + 1.6, TALL_HOUSE.z);

    return {
      sky, uniforms, stars, moon, medina, symbols, bell, horn, fire, symGlows,
      dream, dBell, green, gold, motes, desert, globe, roofGlow, waves,
    };
  }, []);

  // ---------- pro Frame ----------
  const heat = s.heat ?? 0;
  const space = s.place === "space" ? 1 : 0;
  w.uniforms.uDawn.value = s.dawn;
  w.uniforms.uHeat.value = heat;
  w.uniforms.uSpace.value = space;
  (w.stars.material as THREE.PointsMaterial).opacity = Math.max(0, 1 - s.dawn * 1.3 - heat) + space;
  w.moon.visible = s.place === "medina" || s.place === "dream";
  w.moon.children.forEach((m) => ((m as THREE.Sprite).material.opacity = Math.max(0, 1 - s.dawn * 1.1)));

  w.medina.group.visible = s.place === "medina";
  w.dream.visible = s.place === "dream";
  w.desert.visible = s.place === "desert";
  w.globe.visible = s.place === "space";

  // Licht & Nebel je nach Stimmung
  const skyCol = mix(mix(c("#4c5a9a"), c("#f0b48a"), s.dawn), c("#fff0d0"), heat);
  const groundCol = mix(mix(c("#2a2030"), c("#6a4a3a"), s.dawn), c("#c08050"), heat);
  const sunCol = mix(mix(c("#9fb0ff"), c("#ffc89a"), s.dawn), c("#fff2d0"), heat);
  const fogCol = mix(mix(c("#1a2142"), c("#e6a483"), s.dawn), c("#f6dcae"), heat);
  scene.fog =
    s.place === "medina" || s.place === "desert"
      ? new THREE.Fog(fogCol, heat ? 60 : 250, heat ? 1600 : 2400)
      : null;
  const hemiI = s.place === "space" ? 0.3 : lerpN(1.15, 1.5, s.dawn) + heat * 0.8;
  const dirI = s.place === "space" ? 2.2 : lerpN(0.9, 1.6, s.dawn) + heat * 1.6;
  const sunPos: [number, number, number] =
    s.place === "space" ? [200, 80, 120] : heat ? [-260, 420, -1500] : s.dawn > 0.3 ? [600, 250, -300] : [-300, 500, -900];

  // Kamera
  const cam = camera as THREE.PerspectiveCamera;
  cam.position.set(...s.cam);
  cam.fov = s.fov ?? 50;
  cam.near = 0.1;
  cam.far = 60000;
  cam.updateProjectionMatrix();
  cam.lookAt(...s.look);
  w.sky.position.copy(cam.position);
  w.stars.position.copy(cam.position);

  // Laternen
  const lan = s.lanterns ?? 0;
  w.medina.lanterns.children.forEach((l, i) => {
    const sp = l as THREE.Sprite;
    sp.material.opacity = lan * (0.75 + 0.25 * Math.sin(time * 7 + i * 1.7));
  });

  // Symbole
  const sym = s.symbols ?? [0, 0, 0];
  w.symbols.visible = s.place === "medina" && sym.some((v) => v > 0);
  [w.bell, w.horn, w.fire].forEach((o, i) => {
    o.visible = sym[i] > 0.01;
    const base = i === 2 ? 1.8 : 2.2;
    o.scale.setScalar(base * (0.6 + 0.4 * sym[i]));
    o.rotation.y = time * 0.6 + i;
    o.position.y = (i === 2 ? 11.5 : 13) + Math.sin(time * 1.5 + i) * 0.3;
    (w.symGlows[i].material as THREE.SpriteMaterial).opacity = 0.5 * sym[i];
  });
  (w.fire.userData.flames as THREE.Mesh[]).forEach((f, i) => {
    f.scale.set(1, 0.85 + 0.25 * Math.sin(time * 13 + i * 2), 1);
  });

  // Traum
  const db = s.dreamBell ?? 0;
  w.dBell.visible = db > 0.01;
  w.dBell.scale.setScalar(0.8 + 0.2 * db);
  w.dBell.rotation.y = time * 0.5;
  w.dBell.rotation.z = Math.sin(time * 1.2) * 0.12;
  w.dBell.traverse((o) => {
    const m = (o as THREE.Mesh).material as THREE.MeshStandardMaterial | undefined;
    if (m) {
      m.transparent = true;
      m.opacity = db;
    }
  });
  const gl = s.goldLight ?? 0;
  (w.green.material as THREE.SpriteMaterial).opacity = 0.75 * (1 - gl * 0.7);
  w.green.scale.setScalar(14 + 2 * Math.sin(time * 1.3));
  (w.gold.material as THREE.SpriteMaterial).opacity = gl;
  w.gold.scale.setScalar(4 + 34 * gl);
  w.motes.children.forEach((m) => {
    const u = m.userData as { x: number; y: number; z: number; sp: number };
    m.position.set(u.x + Math.sin(time * 0.3 + u.y) * 0.4, ((u.y + time * u.sp + 4) % 8) - 4, u.z);
  });

  // Dach-Licht & Schallwellen
  const rl = s.roofLight ?? 0;
  w.roofGlow.visible = rl > 0.01 && s.place === "medina";
  (w.roofGlow.material as THREE.SpriteMaterial).opacity = rl * (0.85 + 0.15 * Math.sin(time * 5));
  w.roofGlow.scale.setScalar(10 + 6 * rl);
  const wv = s.waves;
  w.waves.visible = wv !== undefined && s.place === "medina";
  if (wv !== undefined) {
    w.waves.children.forEach((r, i) => {
      const age = (wv * 1.1 + i * 1.6) % 9.6; // Sekunden
      const radius = 2 + age * 22;
      r.scale.set(radius, radius, radius * 0.6);
      const startFade = Math.min(1, wv / 0.8);
      ((r as THREE.Mesh).material as THREE.MeshBasicMaterial).opacity = startFade * Math.max(0, 1 - age / 9.6) * 0.9;
    });
  }

  // Tür von Umar
  const door = s.door ?? 0;
  (w.medina.doorGlow.material as THREE.SpriteMaterial).opacity = door;
  w.medina.doorGlow.scale.setScalar(4 + 10 * door);

  // Erde dreht sich
  w.globe.rotation.y = time * 0.12;

  return (
    <>
      <hemisphereLight args={[skyCol, groundCol, hemiI]} />
      <directionalLight position={sunPos} intensity={dirI} color={sunCol} />
      <ambientLight intensity={0.15} />
      <primitive object={w.sky} />
      <primitive object={w.stars} />
      <primitive object={w.moon} />
      <primitive object={w.medina.group} />
      <primitive object={w.symbols} />
      <primitive object={w.dream} />
      <primitive object={w.desert} />
      <primitive object={w.globe} />
      <primitive object={w.roofGlow} />
      <primitive object={w.waves} />
    </>
  );
};

function lerpN(a: number, b: number, t: number) {
  return a + (b - a) * Math.min(1, Math.max(0, t));
}
