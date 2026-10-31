// Kamera-Einstellungen pro Satz. t = Sekunden seit Beginn des Satzes, D = Satzlänge.
// Jede Einstellung bestimmt: Zugposition, Kamera, Signale, Nebel und Spezialeffekte.
export type V3 = [number, number, number];

export type ShotState = {
  trainZ: number; // Position der Zugspitze (Zug fährt Richtung -z)
  cam: V3;
  look: V3;
  fov?: number;
  signals: { z: number; color: string; glow: number }[];
  fogNear: number;
  fogFar: number;
  brakeBar?: number; // 0..1 Länge des roten Bremsweg-Balkens
  cable?: number; // Zeit für Kabel-Impulse
  blocks?: number; // wie viele Streckenabschnitte grün sind (0..13)
  emergency?: number; // 0..1 Intensität Notbremsung
};

const V = 83; // 300 km/h in m/s
const lerp = (a: number, b: number, p: number) => a + (b - a) * Math.min(1, Math.max(0, p));
const ease = (p: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, p)), 3);
const GREEN = "#22ff6a";
const RED = "#ff2626";

export const SHOTS: Record<string, (t: number, D: number) => ShotState> = {
  // Tiefe Kamera neben dem Gleis, Zug rast vorbei
  intro: (t, D) => {
    const trainZ = 170 - V * t;
    return {
      trainZ,
      cam: [7.5, 1.3, lerp(-62, -70, t / D)],
      look: [0, 2.4, lerp(110, -10, ease(t / D))],
      fov: 42,
      signals: [{ z: -22, color: GREEN, glow: 5 }],
      fogNear: 150,
      fogFar: 2600,
    };
  },
  // Über dem Zug, weit vorne leuchtet ein rotes Signal
  redAhead: (t, D) => {
    const trainZ = -V * t;
    return {
      trainZ,
      cam: [2.6, lerp(8, 6.4, t / D), trainZ + 34],
      look: [0.5, 3, trainZ - 500],
      fov: 38,
      signals: [{ z: -720, color: RED, glow: 40 + 10 * Math.sin(t * 9) }],
      fogNear: 400,
      fogFar: 3500,
    };
  },
  // Luftaufnahme: roter Balken = 3 km Bremsweg, Signal liegt weit davor
  brakeBar: (t, D) => {
    const trainZ = -V * t;
    return {
      trainZ,
      cam: [lerp(320, 240, t / D), lerp(560, 480, t / D), trainZ + 380],
      look: [0, 0, trainZ - 1500],
      fov: 45,
      signals: [{ z: -720, color: RED, glow: 140 }],
      fogNear: 2500,
      fogFar: 14000,
      brakeBar: ease((t - 0.3) / 1.6),
    };
  },
  // Zug rast am roten Signal vorbei
  passed: (t) => {
    const trainZ = 150 - V * t;
    return {
      trainZ,
      cam: [-3.2, 1.6, -34],
      look: [1.2, 3.3, 40],
      fov: 46,
      signals: [{ z: 0, color: RED, glow: 6 + 1.5 * Math.sin(t * 14) }],
      fogNear: 150,
      fogFar: 2600,
    };
  },
  // Kamera fährt vor dem Zug her, Kabel im Gleis leuchtet
  cable: (t, D) => {
    const trainZ = -V * t;
    return {
      trainZ,
      cam: [lerp(2.4, 1.5, t / D), lerp(1.4, 0.95, t / D), trainZ - lerp(42, 30, ease(t / D))],
      look: [0, 1.8, trainZ + 12],
      fov: 48,
      signals: [],
      fogNear: 120,
      fogFar: 2200,
      cable: t,
    };
  },
  // Luftaufnahme: 13 Streckenabschnitte werden nacheinander grün
  blocks: (t, D) => {
    const trainZ = -V * t;
    return {
      trainZ,
      cam: [lerp(130, 70, t / D), lerp(380, 300, t / D), trainZ + 420],
      look: [0, 0, trainZ - 4200],
      fov: 46,
      signals: [],
      fogNear: 6000,
      fogFar: 30000,
      blocks: Math.min(13, Math.max(0, (t - 0.2) / 0.19)),
    };
  },
  // Notbremsung: Zug wird rot markiert und kommt zum Stehen
  emergency: (t, D) => {
    const a = 30;
    const tStop = V / a;
    const tt = Math.min(t, tStop);
    const trainZ = 70 - (V * tt - 0.5 * a * tt * tt);
    return {
      trainZ,
      cam: [10, 2.4, -88],
      look: [0, 2.2, lerp(40, -30, ease(t / D))],
      fov: 44,
      signals: [{ z: -120, color: RED, glow: 7 }],
      fogNear: 150,
      fogFar: 2600,
      emergency: Math.min(1, t / 0.3) * (t < tStop ? 1 : Math.max(0.35, 1 - (t - tStop))),
    };
  },
};
