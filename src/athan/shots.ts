// Kamera & Stimmung pro Szene. t = Sekunden seit Szenenbeginn, D = Szenenlänge.
import { ABDULLAH_HOUSE, TALL_HOUSE, TALL_ROOF_Y, UMAR_HOUSE } from "./world";

export type V3 = [number, number, number];
export type Place = "medina" | "dream" | "desert" | "space";

export type ShotState = {
  place: Place;
  cam: V3;
  look: V3;
  fov?: number;
  dawn: number; // 0 Nacht … 1 Morgendämmerung
  heat?: number; // Mittagshitze (Mekka)
  symbols?: [number, number, number]; // Glocke, Horn, Feuer: Sichtbarkeit 0..1
  dreamBell?: number; // 0..1 Glocke im Traum sichtbar
  goldLight?: number; // 0..1 goldenes Licht (Worte des Adhan)
  roofLight?: number; // Licht auf dem höchsten Dach
  waves?: number; // Zeit für Schallwellen
  door?: number; // Tür von Umar geht auf
  lanterns?: number;
};

const lerp = (a: number, b: number, p: number) => a + (b - a) * Math.min(1, Math.max(0, p));
const ease = (p: number) => {
  const x = Math.min(1, Math.max(0, p));
  return x * x * (3 - 2 * x);
};
const fadeIn = (t: number, at: number, len = 0.5) => ease((t - at) / len);

const T = TALL_HOUSE;
const RY = TALL_ROOF_Y;

export const SHOTS: Record<string, (t: number, D: number) => ShotState> = {
  // Luftaufnahme Medina bei Nacht, langsame Kreisfahrt
  hook: (t, D) => {
    const a = 0.9 + (t / D) * 0.35;
    return {
      place: "medina",
      cam: [Math.sin(a) * lerp(170, 130, t / D), lerp(90, 70, t / D), Math.cos(a) * lerp(170, 130, t / D)],
      look: [0, 0, 0],
      fov: 50,
      dawn: 0,
      lanterns: 1,
    };
  },
  // Auf die Moschee zu, durch den Eingang
  mosque: (t, D) => ({
    place: "medina",
    cam: [lerp(-6, 0, t / D), lerp(7, 3.5, ease(t / D)), lerp(75, 30, ease(t / D))],
    look: [0, 2.5, 0],
    fov: 48,
    dawn: 0,
    lanterns: 1,
  }),
  // Im leeren Innenhof, an den Palmsäulen entlang
  courtyard: (t, D) => ({
    place: "medina",
    cam: [lerp(-13, -2, t / D), 1.7, lerp(6, 2, t / D)],
    look: [lerp(4, 10, t / D), 2.4, -13],
    fov: 52,
    dawn: 0,
    lanterns: 0.6,
  }),
  // Von oben: Licht unter dem Dach, Beratung
  council: (t, D) => ({
    place: "medina",
    cam: [lerp(-14, -6, t / D), lerp(34, 26, t / D), lerp(30, 22, t / D)],
    look: [0, 1, -9],
    fov: 50,
    dawn: 0,
    lanterns: 1.4,
  }),
  // Glocke, Horn, Feuer erscheinen über der Moschee
  symbols: (t, D) => ({
    place: "medina",
    cam: [0, lerp(9, 11, t / D), lerp(52, 44, t / D)],
    look: [0, 13, 0],
    fov: 50,
    dawn: 0,
    lanterns: 0.8,
    symbols: [fadeIn(t, D * 0.04), fadeIn(t, D * 0.4), fadeIn(t, D * 0.72)],
  }),
  // Abdullahs Haus in der Nacht
  house: (t, D) => ({
    place: "medina",
    cam: [
      lerp(ABDULLAH_HOUSE.x + 22, ABDULLAH_HOUSE.x + 8, ease(t / D)),
      lerp(6, 3, t / D),
      lerp(ABDULLAH_HOUSE.z + 40, ABDULLAH_HOUSE.z + 20, ease(t / D)),
    ],
    look: [ABDULLAH_HOUSE.x + 1.5, 3, ABDULLAH_HOUSE.z + 4],
    fov: 48,
    dawn: 0,
  }),
  // Traum: grünes Licht, Glocke
  dream: (t, D) => ({
    place: "dream",
    cam: [Math.sin(t * 0.15) * 3, 0.5, lerp(13, 9, t / D)],
    look: [0, 0.6, 0],
    fov: 45,
    dawn: 0,
    dreamBell: fadeIn(t, 0.3, 1),
  }),
  // Die Glocke verschwindet, goldenes Licht – die Worte des Adhan
  words: (t, D) => ({
    place: "dream",
    cam: [0, 0.5, lerp(9, 7, t / D)],
    look: [0, 0.8, 0],
    fov: 45,
    dawn: 0,
    dreamBell: 1 - ease((t - D * 0.3) / (D * 0.25)),
    goldLight: ease((t - D * 0.4) / (D * 0.35)),
  }),
  // Morgengrauen über Medina, Gasse Richtung Moschee
  morning: (t, D) => ({
    place: "medina",
    cam: [lerp(-80, -45, t / D), lerp(3, 4, t / D), 0],
    look: [0, 6, -4],
    fov: 50,
    dawn: lerp(0.45, 0.7, t / D),
    lanterns: 0.5,
  }),
  // Mekka: glühende Wüste, Felsen
  desert: (t, D) => ({
    place: "desert",
    cam: [Math.sin(t * 0.06) * 2 + lerp(9, 6, t / D), lerp(1.2, 1.6, t / D), lerp(11, 8, t / D)],
    look: [-2, 2.4, -10],
    fov: 46,
    dawn: 0,
    heat: 1,
  }),
  // Das höchste Dach neben der Moschee, vor der Dämmerung
  rooftop: (t, D) => {
    const a = 0.4 + (t / D) * 0.6;
    return {
      place: "medina",
      cam: [T.x + Math.sin(a) * 32, lerp(22, 17, t / D), T.z + Math.cos(a) * 32],
      look: [T.x - 3, RY, T.z - 2],
      fov: 50,
      dawn: lerp(0.3, 0.45, t / D),
      roofLight: fadeIn(t, D * 0.35, 1.2),
      lanterns: 0.5,
    };
  },
  // Der erste Adhan: Schallwellen über der Stadt, es wird hell
  athan: (t, D) => ({
    place: "medina",
    cam: [lerp(55, 110, ease(t / D)), lerp(14, 60, ease(t / D)), lerp(55, 120, ease(t / D))],
    look: [T.x - 10, RY - 2, T.z - 8],
    fov: 50,
    dawn: lerp(0.45, 0.95, t / D),
    roofLight: 1,
    waves: t,
    lanterns: 0.4,
  }),
  // Umar eilt aus seinem Haus: Tür geht auf
  umar: (t, D) => ({
    place: "medina",
    cam: [
      lerp(UMAR_HOUSE.x + 5, UMAR_HOUSE.x + 1, ease(t / D)),
      lerp(3.2, 2, t / D),
      lerp(UMAR_HOUSE.z + 36, UMAR_HOUSE.z + 12, ease(t / D)),
    ],
    look: [UMAR_HOUSE.x, 1.8, UMAR_HOUSE.z + 4],
    fov: 50,
    dawn: 0.9,
    door: fadeIn(t, 0.2, 0.6),
    roofLight: 0.6,
  }),
  // Die Erde: überall Lichter
  globe: (t, D) => ({
    place: "space",
    cam: [Math.sin(t * 0.08) * 20, lerp(40, 25, t / D), lerp(190, 150, ease(t / D))],
    look: [0, 0, 0],
    fov: 45,
    dawn: 0,
  }),
  // Abschluss: Mondsichel über der Moschee
  outro: (t, D) => ({
    place: "medina",
    cam: [0, lerp(2, 3, t / D), lerp(62, 58, t / D)],
    look: [-55, 65, -200],
    fov: 50,
    dawn: 0,
    lanterns: 1,
  }),
};
