// Prüfspitzen (mit Fingerschutz), Krokodilklemme, Handschuh-Hand mit Unterarm, Messleitungen.
import React, { useMemo } from "react";
import * as THREE from "three";
import { once, phys } from "./tex";

const V = (x: number, y: number) => new THREE.Vector2(x, y);
const probeGeo = () =>
  once("probeGeo", () => {
    const tip = new THREE.LatheGeometry([V(0, 0), V(0.0004, 0.0006), V(0.001, 0.0028), V(0.001, 0.012), V(0, 0.0121)], 20);
    const P: THREE.Vector2[] = [V(0, 0.0115), V(0.0026, 0.0116), V(0.0029, 0.026), V(0.0046, 0.04), V(0.0053, 0.052), V(0.0094, 0.0545), V(0.0099, 0.058), V(0.0094, 0.0605), V(0.0063, 0.0625)];
    for (let y = 0.066; y < 0.136; y += 0.0045) P.push(V(0.0064, y), V(0.00675, y + 0.00225));
    P.push(V(0.0062, 0.14), V(0.0047, 0.149), V(0.0034, 0.165), V(0.0026, 0.172), V(0, 0.1725));
    const body = new THREE.LatheGeometry(P, 28);
    return { tip, body };
  });
const clipGeo = () =>
  once("clipGeo", () => {
    const boot = new THREE.LatheGeometry([V(0, 0.013), V(0.006, 0.0135), V(0.0092, 0.028), V(0.0095, 0.05), V(0.0088, 0.064), V(0.005, 0.072), V(0.003, 0.08), V(0, 0.0805)], 26);
    boot.scale(1, 1, 0.75);
    const jawA = new THREE.BoxGeometry(0.0065, 0.03, 0.0018);
    jawA.translate(0, 0.012, 0.0028);
    const jawB = jawA.clone();
    jawB.translate(0, 0, -0.0056);
    return { boot, jawA, jawB };
  });

export const probeMat = (c: string) => once("pm" + c, () => phys({ color: c, roughness: 0.38, clearcoat: 0.35, clearcoatRoughness: 0.35 }));
const metal = () => once("pmetal", () => new THREE.MeshStandardMaterial({ color: "#d9dde1", metalness: 1, roughness: 0.22 }));
const glove = () => once("glove", () => phys({ color: "#545a63", roughness: 0.78, sheen: 0.7, sheenColor: new THREE.Color("#9aa1aa"), sheenRoughness: 0.55 }));
const gloveCoat = () => once("gloveC", () => phys({ color: "#2b2f34", roughness: 0.5, clearcoat: 0.25 }));
const sleeve = () => once("sleeve", () => phys({ color: "#26334d", roughness: 0.9, sheen: 0.5, sheenColor: new THREE.Color("#4b5d80") }));
const cuffM = () => once("cuff", () => phys({ color: "#1d2433", roughness: 0.95 }));

// Basis: y = Achse (Spitze → hinten), z = möglichst zur Kamera
export const basis = (axis: THREE.Vector3, toCam: THREE.Vector3) => {
  const y = axis.clone().normalize();
  const z = toCam.clone().sub(y.clone().multiplyScalar(toCam.dot(y))).normalize();
  const x = new THREE.Vector3().crossVectors(y, z).normalize();
  return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
};

export const Probe: React.FC<{ tip: THREE.Vector3; q: THREE.Quaternion; color: string }> = ({ tip, q, color }) => {
  const g = probeGeo();
  return (
    <group position={tip} quaternion={q}>
      <mesh geometry={g.tip} material={metal()} castShadow />
      <mesh geometry={g.body} material={probeMat(color)} castShadow receiveShadow />
    </group>
  );
};

export const Clip: React.FC<{ tip: THREE.Vector3; q: THREE.Quaternion; color: string }> = ({ tip, q, color }) => {
  const g = clipGeo();
  return (
    <group position={tip} quaternion={q}>
      <mesh geometry={g.jawA} material={metal()} castShadow />
      <mesh geometry={g.jawB} material={metal()} castShadow />
      <mesh geometry={g.boot} material={probeMat(color)} castShadow receiveShadow />
    </group>
  );
};

// Hand (Handschuh) hält die Spitze wie einen Stift; Unterarm läuft zur Kamera nach unten raus.
export const Hand: React.FC<{ tip: THREE.Vector3; q: THREE.Quaternion; elbow: THREE.Vector3; side: number }> = ({ tip, q, elbow, side }) => {
  const geo = useMemo(() => {
    return { back: new THREE.SphereGeometry(1, 28, 20) };
  }, []);
  const s = side >= 0 ? 1 : -1;
  // Weltpunkt des Handgelenks
  const wrist = new THREE.Vector3(0.008 * s, 0.182, 0.01).applyQuaternion(q).add(tip);
  const fa = elbow.clone().sub(wrist);
  const len = fa.length();
  const faQ = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), fa.clone().normalize());
  const mid = wrist.clone().add(fa.clone().multiplyScalar(0.5));
  const seg = (k: string, from: [number, number, number], to: [number, number, number], r: number, mat: THREE.Material) => {
    const A = new THREE.Vector3(from[0] * s, from[1], from[2]), B = new THREE.Vector3(to[0] * s, to[1], to[2]);
    const d = B.clone().sub(A);
    const qq = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().normalize());
    return (
      <mesh key={k} position={A.clone().add(B).multiplyScalar(0.5)} quaternion={qq} material={mat} castShadow receiveShadow>
        <capsuleGeometry args={[r, Math.max(0.001, d.length()), 6, 14]} />
      </mesh>
    );
  };
  return (
    <group>
      <group position={tip} quaternion={q}>
        {/* Handrücken */}
        <mesh geometry={geo.back} material={glove()} position={[0.007 * s, 0.142, 0.012]} scale={[0.03, 0.047, 0.0125]} rotation={[0.3, 0, 0.1 * s]} castShadow receiveShadow />
        {/* Zeigefinger lang auf der Spitze (2 Glieder) */}
        {seg("i1", [0.006, 0.122, 0.017], [0.003, 0.094, 0.0125], 0.0074, glove())}
        {seg("i2", [0.003, 0.094, 0.0125], [0.0012, 0.071, 0.0095], 0.0068, glove())}
        {/* Mittelfinger seitlich am Griff */}
        {seg("m1", [0.016, 0.125, 0.012], [0.0125, 0.1, 0.0005], 0.0074, glove())}
        {seg("m2", [0.0125, 0.1, 0.0005], [0.004, 0.092, -0.008], 0.0068, gloveCoat())}
        {/* Ring- und kleiner Finger eingerollt */}
        {seg("r1", [0.022, 0.133, 0.006], [0.018, 0.116, -0.007], 0.0072, glove())}
        {seg("p1", [0.024, 0.146, 0.0], [0.019, 0.132, -0.011], 0.0064, glove())}
        {/* Daumen */}
        {seg("t1", [-0.012, 0.15, 0.006], [-0.0105, 0.118, 0.006], 0.0088, glove())}
        {seg("t2", [-0.0105, 0.118, 0.006], [-0.0068, 0.097, 0.004], 0.0078, glove())}
      </group>
      {/* Unterarm mit Ärmel */}
      <mesh position={mid} quaternion={faQ} material={sleeve()} castShadow receiveShadow>
        <cylinderGeometry args={[0.04, 0.029, len, 28, 1, true]} />
      </mesh>
      <mesh position={wrist.clone().add(fa.clone().normalize().multiplyScalar(0.012))} quaternion={faQ} material={glove()} castShadow>
        <cylinderGeometry args={[0.028, 0.024, 0.034, 22]} />
      </mesh>
      <mesh position={wrist.clone().add(fa.clone().normalize().multiplyScalar(0.055))} quaternion={faQ} material={cuffM()}>
        <cylinderGeometry args={[0.0305, 0.0298, 0.01, 24, 1, true]} />
      </mesh>
    </group>
  );
};

// Messleitung (hängt durch)
export const Lead: React.FC<{ a: THREE.Vector3; aDir: THREE.Vector3; b: THREE.Vector3; color: string; r?: number }> = ({ a, aDir, b, color, r = 0.0021 }) => {
  const g = useMemo(() => {
    const d = a.distanceTo(b);
    const p1 = a.clone().add(aDir.clone().multiplyScalar(0.025));
    const p2 = a.clone().add(aDir.clone().multiplyScalar(0.05)).add(new THREE.Vector3(0, -0.05, 0));
    const mid = a.clone().lerp(b, 0.55).add(new THREE.Vector3(0, -0.12 - d * 0.25, 0.02));
    const p4 = b.clone().add(new THREE.Vector3(0, 0.035, 0));
    return new THREE.TubeGeometry(new THREE.CatmullRomCurve3([a, p1, p2, mid, p4, b], false, "centripetal"), 64, r, 8, false);
  }, [a.x, a.y, a.z, b.x, b.y, b.z, aDir.x, aDir.y, aDir.z]);
  return <mesh geometry={g} material={probeMat(color)} castShadow receiveShadow />;
};
