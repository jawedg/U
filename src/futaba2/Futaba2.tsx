// „Futaba, 11. März 2011“ – Teil 1 im Ink-Pop-Stil (blender/inkpop/scene1.py, Fischauge per ffmpeg)
// Oben links: Wochentag · Uhrzeit, Ort, Datum (wie im Vorbild). Untertitel mittig-unten, Handy-Banner oben, Beben-Wackeln.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import script from "./script.json";
import timing from "./timing.json";
import TLj from "./timeline.json";

const TL = TLj as any;
export const FUTABA2_FPS = 30;
export const FUTABA2_FRAMES = Math.round((TL.END + 1.2) * FUTABA2_FPS);
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const AT = TL.AT as Record<string, number>;
const LINES = (script as any).sentences.map((s: any, i: number) => ({ ...s, at: AT[s.id], l: (timing as any).lines[i] }));
const COLOR: Record<string, string> = { m: "#ffffff", s: "#ffd23f", o: "#ffd23f", l: "#ff9a3c" };

const Caption: React.FC<{ t: number }> = ({ t }) => {
  for (const ln of LINES) {
    const local = t - ln.at;
    if (local < -0.05 || local > ln.l.seconds + 0.1) continue;
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
    const c = [...chunks].reverse().find((k) => local >= k.s - 0.06);
    if (!c) return null;
    const col = COLOR[ln.id[0]] ?? "#fff";
    const pop = spring({ frame: Math.round((local - c.s) * FUTABA2_FPS), fps: FUTABA2_FPS, config: { damping: 16, stiffness: 260 } });
    const quote = ln.id.startsWith("lsp");
    return (
      <div style={{ position: "absolute", left: 70, right: 70, top: 1240, textAlign: "center" }}>
        <span
          style={{
            display: "inline-block",
            transform: `scale(${0.92 + 0.08 * pop})`,
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: 50,
            lineHeight: 1.18,
            color: col,
            fontStyle: quote ? "italic" : "normal",
            WebkitTextStroke: "8px #0d0d12",
            paintOrder: "stroke fill",
          }}
        >
          {quote ? "„" : ""}
          {c.ws.join(" ")}
          {quote ? "“" : ""}
        </span>
      </div>
    );
  }
  return null;
};

const Banner: React.FC<{ t: number; at: number; dur: number; who: string; text: string; time: string; red?: boolean }> = ({ t, at, dur, who, text, time, red }) => {
  const local = t - at;
  if (local < 0 || local > dur) return null;
  const inn = spring({ frame: Math.round(local * FUTABA2_FPS), fps: FUTABA2_FPS, config: { damping: 15, stiffness: 190 } });
  const out = interpolate(local, [dur - 0.3, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: 60,
        right: 60,
        top: -240 + 540 * inn - 540 * out,
        background: red ? "#d81e28" : "#fbfbf8",
        borderRadius: 28,
        padding: "22px 30px",
        fontFamily: SANS,
        color: red ? "#fff" : "#111",
        border: "5px solid #111",
        boxShadow: "0 10px 0 rgba(0,0,0,0.25)",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 800 }}>
        <span>{who}</span>
        <span style={{ fontWeight: 700, opacity: 0.75 }}>{time}</span>
      </div>
      <div style={{ fontSize: 38, fontWeight: 650, marginTop: 8 }}>{text}</div>
    </div>
  );
};

const Stamp: React.FC<{ day: string; time: string; place: string; date: string; flash: boolean }> = ({ day, time, place, date, flash }) => (
  <div style={{ position: "absolute", left: 52, top: 92, fontFamily: SANS, color: "#fff", textShadow: "0 0 3px #000, 0 0 3px #000, 0 2px 6px #000" }}>
    <div style={{ fontWeight: 900, fontSize: 44, letterSpacing: 3 }}>
      {day} · <span style={{ color: flash ? "#ffd23f" : "#fff" }}>{time} UHR</span>
    </div>
    <div style={{ width: 120, height: 5, background: "#e2332b", margin: "8px 0 10px" }} />
    <div style={{ fontWeight: 700, fontSize: 30 }}>{place}</div>
    <div style={{ fontWeight: 600, fontSize: 26, opacity: 0.9 }}>{date}</div>
  </div>
);

export const Futaba2Video: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUTABA2_FPS;
  const inA = t < TL.A_END;
  const card = t >= TL.A_END && t < TL.B0;
  const q = t > TL.QUAKE ? Math.min(1, (t - TL.QUAKE) / 0.7) : 0;
  const sx = q * 12 * Math.sin(t * 43) + q * 6 * Math.sin(t * 17);
  const sy = q * 10 * Math.sin(t * 37 + 1) + q * 5 * Math.sin(t * 13);
  const alarm = t > TL.EEW && t < TL.QUAKE + 2 ? 0.3 + 0.3 * Math.sin((t - TL.EEW) * Math.PI * 4) : 0;
  const time = t < TL.EEW ? "14:45" : "14:46";
  const factIn = interpolate(t, [TL.QUAKE + 2.6, TL.QUAKE + 2.9, TL.QUAKE + 6.0, TL.QUAKE + 6.4], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const end = t >= TL.END;
  const cardTxt = "EINEN TAG VORHER";
  const cf = Math.max(0, t - TL.A_END) * 30;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {!card && !end ? (
        <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px) scale(${1 + 0.035 * q})` }}>
          <OffthreadVideo src={staticFile("futaba2/render.mp4")} muted />
        </AbsoluteFill>
      ) : null}
      {!card && !end ? <AbsoluteFill style={{ boxShadow: `inset 0 0 200px 30px rgba(230,20,20,${alarm})` }} /> : null}
      {inA ? <Stamp day="SAMSTAG" time="05:44" place="Futaba, Präfektur Fukushima" date="12. März 2011" flash={false} /> : null}
      {!inA && !card && !end ? <Stamp day="FREITAG" time={time} place="Futaba, Präfektur Fukushima" date="11. März 2011 · 4 km vom Atomkraftwerk" flash={t >= TL.EEW && t < TL.EEW + 0.8} /> : null}
      {card ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 66, letterSpacing: 6, color: "#fff" }}>{cardTxt.slice(0, Math.min(cardTxt.length, Math.floor(cf * 1.2) + 1))}</div>
        </AbsoluteFill>
      ) : null}
      <Banner t={t} at={TL.PING + 0.1} dur={2.6} who="💬 Mama" text="Heute gibt's Curry! Um 7 zuhause :)" time="14:44" />
      <Banner t={t} at={TL.EEW + 0.05} dur={1.9} who="⚠️ 緊急地震速報 · Erdbeben-Frühwarnung" text="Starkes Beben! Sofort Schutz suchen!" time="14:46" red />
      {factIn > 0 ? (
        <div style={{ position: "absolute", left: 0, right: 0, top: 560, textAlign: "center", opacity: factIn, fontFamily: SANS }}>
          <div style={{ display: "inline-block", background: "#111", color: "#ffd23f", fontWeight: 900, fontSize: 56, padding: "10px 26px", border: "5px solid #ffd23f", borderRadius: 12 }}>
            STÄRKE 9,0
          </div>
          <div style={{ marginTop: 14, color: "#fff", fontWeight: 800, fontSize: 32, WebkitTextStroke: "6px #111", paintOrder: "stroke fill" }}>
            das stärkste Beben, das Japan je gemessen hat
          </div>
        </div>
      ) : null}
      {!card && !end ? <Caption t={t} /> : null}
      {end ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", fontFamily: SANS, color: "#fff", textAlign: "center" }}>
          <div style={{ fontWeight: 900, fontSize: 60 }}>Und dann heulen die Sirenen…</div>
          <div style={{ fontWeight: 700, fontSize: 34, marginTop: 20, opacity: 0.8 }}>Teil 2 folgt</div>
        </AbsoluteFill>
      ) : null}
      <Audio src={staticFile("futaba2/sfx.mp3")} volume={0.9} />
      {LINES.map((ln: any, i: number) => (
        <Sequence key={i} from={Math.round(ln.at * FUTABA2_FPS)}>
          <Audio src={staticFile(ln.id === "lsp1" ? "futaba2/lsp_radio.wav" : ln.l.file)} volume={ln.id === "lsp1" ? 0.9 : 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
