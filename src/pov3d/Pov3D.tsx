// 3D-POV-Probe „Plan Rot“: Blender-Rendering (blender/pov/classroom.py) + Uhrzeit, Untertitel, Schlussfrage, Ton.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import timing from "./timing.json";

export const POV_FPS = 24;
export const POV_FRAMES = Math.round(20.5 * POV_FPS);
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const LINES = [
  { who: "DURCHSAGE", at: 1.8, file: "pov3d/pa.wav", l: (timing as any).lines[0] },
  { who: "LEHRERIN", at: 9.5, file: "pov3d/line-1-0.wav", l: (timing as any).lines[1] },
];
const END = 17.5;

// Untertitel in kurzen Stücken (max. 4 Wörter), wie bei TikTok
const Caption: React.FC<{ t: number }> = ({ t }) => {
  for (const ln of LINES) {
    const words: { word: string; start: number }[] = ln.l.words;
    const local = t - ln.at;
    if (local < 0 || local > ln.l.seconds) continue;
    const chunks: { s: number; text: string }[] = [];
    let cur: string[] = [];
    let s0 = 0;
    words.forEach((w, i) => {
      if (!cur.length) s0 = w.start;
      cur.push(w.word);
      if (cur.length >= 4 || /[.!?:]$/.test(w.word) || i === words.length - 1) {
        chunks.push({ s: s0, text: cur.join(" ") });
        cur = [];
      }
    });
    const c = [...chunks].reverse().find((k) => local >= k.s - 0.05);
    if (!c) return null;
    return (
      <div style={{ position: "absolute", left: 60, right: 60, top: 1430, textAlign: "center" }}>
        <div style={{ display: "inline-block", fontFamily: SANS, fontWeight: 800, fontSize: 24, letterSpacing: 4, color: "#111", background: "#fff", borderRadius: 8, padding: "6px 14px", marginBottom: 14 }}>{ln.who}</div>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 64, lineHeight: 1.15, color: "#ffd84a", WebkitTextStroke: "3px #000", paintOrder: "stroke fill", textShadow: "0 4px 14px rgba(0,0,0,0.8)" }}>{c.text}</div>
      </div>
    );
  }
  return null;
};

export const Pov3DVideo: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / POV_FPS;
  const card = interpolate(t, [END, END + 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const s1 = spring({ frame: f - Math.round((END + 0.4) * POV_FPS), fps: POV_FPS, config: { damping: 13 } });
  const s2 = spring({ frame: f - Math.round((END + 0.7) * POV_FPS), fps: POV_FPS, config: { damping: 13 } });
  const time = t < 13.6 ? "10:41" : "10:43";
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <OffthreadVideo src={staticFile("pov3d/render.mp4")} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, transparent 55%, rgba(0,0,0,0.55) 100%)" }} />
      {/* Ort/Zeit oben links */}
      <div style={{ position: "absolute", left: 50, top: 110, fontFamily: SANS, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,0.9)", opacity: 1 - card }}>
        <div style={{ fontWeight: 800, fontSize: 34, letterSpacing: 3 }}>MITTWOCH · {time} UHR</div>
        <div style={{ fontWeight: 600, fontSize: 24, letterSpacing: 4, opacity: 0.8, marginTop: 6 }}>MATHE · RAUM 2.14</div>
      </div>
      {t < END ? <Caption t={t} /> : null}
      {/* Schlussfrage */}
      <AbsoluteFill style={{ opacity: card, background: "rgba(5,6,10,0.78)", alignItems: "center", justifyContent: "center", fontFamily: SANS, color: "#fff", textAlign: "center" }}>
        <div style={{ fontWeight: 900, fontSize: 84, lineHeight: 1.05, letterSpacing: 1 }}>
          WAS WÜRDEST
          <br />
          DU TUN?
        </div>
        <div style={{ marginTop: 70, width: 760, padding: "34px 0", borderRadius: 26, background: "#1f9d55", fontWeight: 900, fontSize: 52, transform: `scale(${s1})` }}>TÜR AUFMACHEN</div>
        <div style={{ margin: "26px 0", fontWeight: 800, fontSize: 34, opacity: 0.7 }}>ODER</div>
        <div style={{ width: 760, padding: "34px 0", borderRadius: 26, background: "#c62828", fontWeight: 900, fontSize: 52, transform: `scale(${s2})` }}>LEISE BLEIBEN</div>
        <div style={{ marginTop: 60, fontWeight: 600, fontSize: 30, opacity: 0.75 }}>Schreib es in die Kommentare</div>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "#000", opacity: interpolate(f, [0, 8], [1, 0], { extrapolateRight: "clamp" }) }} />
      <Audio src={staticFile("pov3d/sfx.mp3")} volume={0.9} />
      {LINES.map((ln, i) => (
        <Sequence key={i} from={Math.round(ln.at * POV_FPS)}>
          <Audio src={staticFile(ln.file)} volume={i === 0 ? 0.9 : 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
