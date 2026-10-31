import React, { useMemo } from "react";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { buildSignal, buildTrain, buildWorld, makeGlow, CAR_LEN, TRACK_X } from "./world";
import { ShotState } from "./shots";

const SIGNAL_X = 2.4;

export const TrainScene: React.FC<{ s: ShotState; time: number }> = ({ s, time }) => {
  const { camera, scene } = useThree();

  const world = useMemo(() => buildWorld(), []);
  const train = useMemo(() => buildTrain(), []);
  const signals = useMemo(() => [buildSignal(), buildSignal()], []);

  // Effekte
  const fx = useMemo(() => {
    const additive = (color: string, opacity: number) =>
      new THREE.MeshBasicMaterial({
        color,
        transparent: true,
        opacity,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        fog: false,
      });
    const brakeBar = new THREE.Mesh(new THREE.BoxGeometry(12, 0.3, 1), additive("#ff2a3d", 0.9));
    const brakeEnd = new THREE.Mesh(new THREE.BoxGeometry(14, 120, 14), additive("#ff2a3d", 0.35));
    const brakeEndGlow = makeGlow("#ff3048", 160);

    const cable = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.06, 4000), additive("#29e6ff", 0.9));
    const pulses = new THREE.Group();
    for (let i = 0; i < 26; i++) {
      const p = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.12, 3), additive("#c8fbff", 1));
      const g = makeGlow("#29e6ff", 2.4);
      p.add(g);
      pulses.add(p);
    }
    const blocks = new THREE.Group();
    for (let k = 0; k < 13; k++) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(9, 0.4, 980), additive("#2bff7a", 0.9));
      b.position.set(TRACK_X, 0.8, -k * 1000 - 500);
      const edge = makeGlow("#2bff7a", 90);
      edge.position.set(0, 4, -490);
      b.add(edge);
      blocks.add(b);
    }
    const alarmBox = new THREE.Mesh(new THREE.BoxGeometry(4.6, 5.2, CAR_LEN + 2), additive("#ff1f3a", 0.2));
    const alarmEdges = new THREE.LineSegments(
      new THREE.EdgesGeometry(alarmBox.geometry),
      new THREE.LineBasicMaterial({ color: "#ff5a6e", transparent: true, fog: false }),
    );
    alarmBox.add(alarmEdges);
    const sparks = new THREE.Group();
    for (let i = 0; i < 16; i++) sparks.add(makeGlow("#ffb347", 1.6));
    return { brakeBar, brakeEnd, brakeEndGlow, cable, pulses, blocks, alarmBox, alarmEdges, sparks };
  }, []);

  // --- Szene für dieses Frame einstellen ---
  scene.fog = new THREE.Fog("#57557c", s.fogNear, s.fogFar);
  const cam = camera as THREE.PerspectiveCamera;
  cam.position.set(...s.cam);
  cam.fov = s.fov ?? 45;
  cam.near = 0.3;
  cam.far = 60000;
  cam.updateProjectionMatrix();
  cam.lookAt(...s.look);

  train.position.set(TRACK_X, 0, s.trainZ);

  signals.forEach((sig, i) => {
    const def = s.signals[i];
    sig.visible = Boolean(def);
    if (!def) return;
    sig.position.set(SIGNAL_X, 0, def.z);
    const { lamp, glow } = sig.userData as { lamp: THREE.Mesh; glow: THREE.Sprite };
    (lamp.material as THREE.MeshBasicMaterial).color.set(def.color);
    (glow.material as THREE.SpriteMaterial).color.set(def.color);
    glow.scale.set(def.glow, def.glow, 1);
  });

  // Bremsweg-Balken
  const bb = s.brakeBar ?? 0;
  fx.brakeBar.visible = fx.brakeEnd.visible = fx.brakeEndGlow.visible = bb > 0.001;
  const len = 3000 * bb;
  fx.brakeBar.scale.z = Math.max(0.001, len);
  fx.brakeBar.position.set(TRACK_X, 0.9, s.trainZ - len / 2);
  fx.brakeEnd.position.set(TRACK_X, 60, s.trainZ - len);
  fx.brakeEndGlow.position.set(TRACK_X, 20, s.trainZ - len);

  // Kabel im Gleis
  const c = s.cable;
  fx.cable.visible = fx.pulses.visible = c !== undefined;
  if (c !== undefined) {
    fx.cable.position.set(TRACK_X, 0.6, s.trainZ - 1500);
    fx.pulses.children.forEach((p, i) => {
      const travel = ((c * 140 + i * 24) % 620) - 600; // von vorne zum Zug
      p.position.set(TRACK_X, 0.66, s.trainZ + travel);
    });
  }

  // Streckenabschnitte
  const bl = s.blocks;
  fx.blocks.visible = bl !== undefined;
  if (bl !== undefined) {
    fx.blocks.children.forEach((b, k) => {
      const on = Math.min(1, Math.max(0, bl - k));
      b.visible = on > 0;
      ((b as THREE.Mesh).material as THREE.MeshBasicMaterial).opacity = 0.85 * on;
      b.scale.y = 1 + 2 * on;
    });
  }

  // Notbremsung
  const e = s.emergency ?? 0;
  fx.alarmBox.visible = fx.sparks.visible = e > 0;
  if (e > 0) {
    const pulse = 0.55 + 0.45 * Math.sin(time * 16);
    fx.alarmBox.position.set(TRACK_X, 2.6, s.trainZ + CAR_LEN / 2);
    (fx.alarmBox.material as THREE.MeshBasicMaterial).opacity = 0.22 * e * pulse;
    (fx.alarmEdges.material as THREE.LineBasicMaterial).opacity = e;
    fx.sparks.children.forEach((sp, i) => {
      const side = i % 2 ? 0.75 : -0.75;
      const z = s.trainZ + 3 + (i >> 1) * 7 + ((i * 13 + Math.floor(time * 30)) % 3);
      sp.position.set(TRACK_X + side, 0.7, z);
      sp.scale.setScalar((1 + ((i * 7 + Math.floor(time * 30)) % 5) * 0.5) * e);
    });
  }

  return (
    <>
      <hemisphereLight args={["#8f9ad8", "#4a3c48", 1.15]} />
      <directionalLight position={[-300, 500, 200]} intensity={1.7} color="#c3c9ff" />
      <ambientLight intensity={0.35} />
      <primitive object={world} />
      <primitive object={train} />
      {signals.map((sig, i) => (
        <primitive key={i} object={sig} />
      ))}
      <primitive object={fx.brakeBar} />
      <primitive object={fx.brakeEnd} />
      <primitive object={fx.brakeEndGlow} />
      <primitive object={fx.cable} />
      <primitive object={fx.pulses} />
      <primitive object={fx.blocks} />
      <primitive object={fx.alarmBox} />
      <primitive object={fx.sparks} />
    </>
  );
};
