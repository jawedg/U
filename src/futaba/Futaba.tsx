// „Futaba, 11. März 2011“ – Testclip: Blender-Comic-Rendering (blender/futaba/town.py, Fischauge per ffmpeg)
// + Uhrzeit/Ort oben links, Untertitel, Handy-Banner, Alarm-Blitz, Beben-Wackeln, Ton.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import script from "./script.json";
import timing from "./timing.json";
import lineAt from "./line_at.json";
import ev from "./events.json";

export const FUTABA_FPS = 24;
export const FUTABA_FRAMES = Math.round(ev.end * FUTABA_FPS);
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const AT = lineAt as Record<string, number>;
const HOT = /^(Meer|Curry|Runter|aufhört|hört)/;
const LINES = (script as any).sentences.map((s: any, i: number) => ({ ...s, at: AT[s.id], l: (timing as any).lines[i] }));

const Caption: React.FC<{ t: number }> = ({ t }) => {
  for (const ln of LINES) {
    const local = t - ln.at;
    if (local < -0.05 || local > ln.l.seconds + 0.15) continue;
    const words: { word: string; start: number }[] = ln.l.words;
    const chunks: { s: number; ws: string[] }[] = [];
    let cur: string[] = [];
    let s0 = 0;
    words.forEach((w, i) => {
      if (!cur.length) s0 = w.start;
      cur.push(w.word);
      if (cur.length >= 4 || /[.!?:,]$/.test(w.word) || i === words.length - 1) {
        chunks.push({ s: s0, ws: cur });
        cur = [];
      }
    });
    const c = [...chunks].reverse().find((k) => local >= k.s - 0.08);
    if (!c) return null;
    const me = ln.id.startsWith("m");
    const pop = spring({ frame: Math.round((local - c.s) * FUTABA_FPS), fps: FUTABA_FPS, config: { damping: 14, stiffness: 240 } });
    return (
      <div style={{ position: "absolute", left: 60, right: 60, top: 1180, textAlign: "center" }}>
        <div
          style={{
            transform: `scale(${0.88 + 0.12 * pop})`,
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: 58,
            lineHeight: 1.15,
            color: me ? "#9fe3ff" : "#ffffff",
            WebkitTextStroke: "9px #111",
            paintOrder: "stroke fill",
          }}
        >
          {c.ws.map((w, i) => (
            <span key={i} style={{ color: HOT.test(w) ? "#ffd23f" : undefined }}>
              {w}{" "}
            </span>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

// Handy-Banner oben (wie eine echte Benachrichtigung)
const Banner: React.FC<{ t: number; at: number; dur: number; who: string; text: string; time: string; red?: boolean }> = ({ t, at, dur, who, text, time, red }) => {
  const local = t - at;
  if (local < 0 || local > dur) return null;
  const inn = spring({ frame: Math.round(local * FUTABA_FPS), fps: FUTABA_FPS, config: { damping: 15, stiffness: 180 } });
  const out = interpolate(local, [dur - 0.3, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const y = -260 + 380 * inn - 380 * out;
  return (
    <div
      style={{
        position: "absolute",
        left: 50,
        right: 50,
        top: y,
        background: red ? "#d81e28" : "rgba(250,250,250,0.97)",
        borderRadius: 30,
        padding: "26px 32px",
        boxShadow: "0 12px 40px rgba(0,0,0,0.35)",
        fontFamily: SANS,
        color: red ? "#fff" : "#111",
        border: "4px solid #111",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 800 }}>
        <span>{who}</span>
        <span style={{ opacity: 0.6, fontWeight: 600 }}>{time}</span>
      </div>
      <div style={{ fontSize: 38, fontWeight: 600, marginTop: 10 }}>{text}</div>
    </div>
  );
};

export const FutabaVideo: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUTABA_FPS;
  const q = t > ev.quake ? Math.min(1, (t - ev.quake) / 0.8) : 0;
  const sx = q * 14 * Math.sin(t * 41) + q * 6 * Math.sin(t * 17);
  const sy = q * 12 * Math.sin(t * 37 + 1) + q * 5 * Math.sin(t * 13);
  const alarm = t > ev.alarm && t < ev.quake + 2 ? 0.35 + 0.35 * Math.sin((t - ev.alarm) * Math.PI * 4) : 0;
  const time = t < ev.alarm ? "14:45" : "14:46";
  const hit = t > ev.quake + 1.4 && t < ev.quake + 4.4;
  const hitIn = interpolate(t, [ev.quake + 1.4, ev.quake + 1.7, ev.quake + 4.0, ev.quake + 4.4], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px) scale(${1 + 0.04 * q})` }}>
        <OffthreadVideo src={staticFile("futaba/render.mp4")} muted />
      </AbsoluteFill>
      <AbsoluteFill style={{ boxShadow: `inset 0 0 200px 30px rgba(230,20,20,${alarm})` }} />
      <div style={{ position: "absolute", left: 48, top: 70, fontFamily: SANS, color: "#fff", textShadow: "0 0 6px #000, 0 0 2px #000" }}>
        <div style={{ fontWeight: 800, fontSize: 40, letterSpacing: 1 }}>
          FREITAG · <span style={{ color: t >= ev.alarm && t < ev.alarm + 0.6 ? "#ffd23f" : "#fff" }}>{time} UHR</span>
        </div>
        <div style={{ fontWeight: 600, fontSize: 28, marginTop: 6 }}>Futaba, Präfektur Fukushima</div>
        <div style={{ fontWeight: 600, fontSize: 24, marginTop: 4, opacity: 0.85 }}>ca. 4 km vom Atomkraftwerk</div>
      </div>
      <Banner t={t} at={ev.ping} dur={2.4} who="💬 Mama" text="Heute gibt's Curry! Komm pünktlich um 7 :)" time="14:44" />
      <Banner t={t} at={ev.alarm} dur={1.6} who="⚠️ 緊急地震速報" text="Erdbeben-Frühwarnung: Starkes Beben!" time="14:46" red />
      {hit ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 640, textAlign: "center", opacity: hitIn, fontFamily: SANS }}>
          <div style={{ display: "inline-block", background: "#111", color: "#ffd23f", fontWeight: 900, fontSize: 64, padding: "10px 26px", border: "4px solid #ffd23f" }}>
            STÄRKE 9,0
          </div>
          <div style={{ marginTop: 14, color: "#fff", fontWeight: 800, fontSize: 34, textShadow: "0 0 8px #000" }}>
            das stärkste Beben in Japans Geschichte
          </div>
        </div>
      ) : null}
      <Caption t={t} />
      <Audio src={staticFile("futaba/sfx.mp3")} volume={0.9} />
      {LINES.map((ln: any, i: number) => (
        <Sequence key={i} from={Math.round(ln.at * FUTABA_FPS)}>
          <Audio src={staticFile(ln.l.file)} volume={1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
