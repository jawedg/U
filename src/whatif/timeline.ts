// Zeitachse: Szene = Satz. Start/Länge in Bildern (gleiche Rechnung wie scripts/sfx_whatif.py).
import script from "./script.json";
import timing from "./timing.json";

export const FPS = 30;
export type Shot = {
  i: number;
  shot: string;
  text: string;
  hud: [number, string];
  start: number;
  dur: number;
  delay: number; // Sekunden bis die Stimme einsetzt
  file: string;
  words: { word: string; start: number }[];
  speech: number;
};

let acc = 0;
export const SHOTS: Shot[] = script.sentences.map((s: any, i: number) => {
  const l = (timing as any).lines[i];
  const dur = Math.round((s.delay + l.seconds + s.pad) * FPS);
  const sh: Shot = { i, shot: s.shot, text: s.text, hud: s.hud, start: acc, dur, delay: s.delay, file: l.file, words: l.words, speech: l.seconds };
  acc += dur;
  return sh;
});
export const TOTAL = acc;
export const shotAt = (f: number) => SHOTS.find((s) => f >= s.start && f < s.start + s.dur) ?? SHOTS[SHOTS.length - 1];
