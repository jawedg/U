// „Futaba, 11. März 2011“ – Wohnzimmer (blender/inkpop/room_scene.py, Fischauge per ffmpeg).
// Oben links Wochentag · Uhrzeit, Ort; Untertitel mit Sprecher-Farben + 📺/📢; Warn-Banner; Schlusstafel mit Frage.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import script from "../futaba3/script.json";
import timing from "../futaba3/timing.json";
import TLj from "./timeline.json";

const TL = TLj as any;
export const FUTABA4_FPS = 24;
const CARDS = 9.0;
const VEND = TL.VEND;
export const FUTABA4_FRAMES = Math.round((VEND + CARDS) * FUTABA4_FPS);
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const AT = TL.AT as Record<string, number>;
const LINES = (script as any).sentences.map((s: any, i: number) => ({ ...s, at: AT[s.id], l: (timing as any).lines[i] })).filter((x: any) => x.at !== undefined);
const STYLE: Record<string, { c: string; icon?: string; it?: boolean }> = {
  m: { c: "#ffffff" },
  h: { c: "#ffb3d1" },
  ma: { c: "#ffd23f" },
  tv: { c: "#9fd8ff", icon: "📺 ", it: true },
  lsp: { c: "#ffb347", icon: "📢 ", it: true },
};
const who = (id: string) => (id.startsWith("ma") ? "ma" : id.startsWith("tv") ? "tv" : id.startsWith("lsp") ? "lsp" : id[0]);
const AUDIO: Record<string, string> = { tv1: "futaba4/tv1_tv.wav", tv2: "futaba4/tv2_tv.wav", tv3: "futaba4/tv3_tv.wav", lsp: "futaba4/lsp_far.wav" };

const Caption: React.FC<{ t: number }> = ({ t }) => {
  // neuere Zeile hat Vorrang (Überlappungen)
  for (const ln of [...LINES].sort((a: any, b: any) => b.at - a.at)) {
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
    const st = STYLE[who(ln.id)];
    const pop = spring({ frame: Math.round((local - c.s) * FUTABA4_FPS), fps: FUTABA4_FPS, config: { damping: 16, stiffness: 260 } });
    return (
      <div style={{ position: "absolute", left: 60, right: 60, top: 1250, textAlign: "center" }}>
        <span
          style={{
            display: "inline-block",
            transform: `scale(${0.92 + 0.08 * pop})`,
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: 50,
            lineHeight: 1.18,
            color: st.c,
            fontStyle: st.it ? "italic" : "normal",
            WebkitTextStroke: "8px #101018",
            paintOrder: "stroke fill",
          }}
        >
          {st.icon ?? ""}
          {c.ws.join(" ")}
        </span>
      </div>
    );
  }
  return null;
};

const Banner: React.FC<{ t: number; at: number; dur: number; who: string; text: string; sub: string; red?: boolean }> = ({ t, at, dur, who, text, sub, red }) => {
  const local = t - at;
  if (local < 0 || local > dur) return null;
  const inn = spring({ frame: Math.round(local * FUTABA4_FPS), fps: FUTABA4_FPS, config: { damping: 15, stiffness: 190 } });
  const out = interpolate(local, [dur - 0.3, dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: 56,
        right: 56,
        top: -260 + 560 * inn - 560 * out,
        background: red ? "#d81e28" : "#fbfbf8",
        borderRadius: 26,
        padding: "20px 28px",
        fontFamily: SANS,
        color: red ? "#fff" : "#111",
        border: "5px solid #111",
        boxShadow: "0 10px 0 rgba(0,0,0,0.25)",
      }}
    >
      <div style={{ fontSize: 26, fontWeight: 800, opacity: 0.9 }}>{who}</div>
      <div style={{ fontSize: 40, fontWeight: 900, marginTop: 6 }}>{text}</div>
      <div style={{ fontSize: 28, fontWeight: 650, marginTop: 4 }}>{sub}</div>
    </div>
  );
};

const EndCards: React.FC<{ t: number }> = ({ t }) => {
  const a = interpolate(t, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const b = interpolate(t, [2.6, 3.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const c = interpolate(t, [4.6, 5.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#16161c", alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: SANS, color: "#fff", padding: 70 }}>
      <div style={{ opacity: a, fontSize: 64, fontWeight: 900, lineHeight: 1.15 }}>ÜBERLEBEN SIE DIE NACHT?</div>
      <div style={{ opacity: b, fontSize: 34, fontWeight: 700, lineHeight: 1.35, marginTop: 34 }}>
        Am nächsten Morgen um 5:44 Uhr musste ganz Futaba evakuiert werden.
        <br />
        <span style={{ color: "#ffd23f", fontWeight: 900 }}>Die Menschen durften 11 Jahre nicht zurück.</span>
      </div>
      <div style={{ opacity: c, marginTop: 70, width: "100%" }}>
        <div style={{ fontSize: 50, fontWeight: 900 }}>WAS HÄTTEST DU GETAN?</div>
        <div style={{ margin: "30px auto 0", background: "#2f6fd6", border: "5px solid #111", borderRadius: 22, padding: "22px 20px", fontSize: 38, fontWeight: 900 }}>
          🏃 SOFORT ZUR SCHULE RENNEN
        </div>
        <div style={{ fontSize: 32, fontWeight: 900, color: "#ffd23f", margin: "16px 0" }}>ODER</div>
        <div style={{ background: "#d33a2f", border: "5px solid #111", borderRadius: 22, padding: "22px 20px", fontSize: 38, fontWeight: 900 }}>
          📞 ERST PAPA IM KRAFTWERK ANRUFEN
        </div>
        <div style={{ fontSize: 30, fontWeight: 700, marginTop: 30, opacity: 0.85 }}>Schreib es in die Kommentare 👇</div>
      </div>
    </AbsoluteFill>
  );
};

export const Futaba4Video: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUTABA4_FPS;
  const inVideo = t < VEND;
  const jumpCard = t >= TL.T2 && t < TL.T2 + 1.1;
  const q = t > TL.QUAKE && t < TL.QEND + 1.5 ? Math.min(1, (t - TL.QUAKE) / 1.2) * Math.min(1, Math.max(0, (TL.QEND + 1.5 - t) / 2.5)) : 0;
  const sx = q * 10 * Math.sin(t * 43) + q * 5 * Math.sin(t * 17);
  const sy = q * 9 * Math.sin(t * 37 + 1) + q * 4 * Math.sin(t * 13);
  const alarm = t > TL.EEW && t < TL.QUAKE + 1.5 ? 0.25 + 0.25 * Math.sin((t - TL.EEW) * Math.PI * 4) : 0;
  const hook = t < TL.HOOK;
  const time = hook ? "15:27" : t < TL.EEW ? "14:45" : t < TL.TVW ? "14:46" : t < TL.T2 ? "14:49" : "15:27";
  const flash = (t >= TL.EEW && t < TL.EEW + 0.8) || (t >= TL.TVW && t < TL.TVW + 0.8) || (t >= TL.T2 + 1.1 && t < TL.T2 + 2.2);
  const dark = t > TL.POWER ? 0.12 : 0;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {inVideo ? (
        <>
          <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px) scale(${1 + 0.03 * q})` }}>
            <OffthreadVideo src={staticFile("futaba4/render.mp4")} muted />
          </AbsoluteFill>
          <AbsoluteFill style={{ background: `rgba(10,15,40,${dark})` }} />
          <AbsoluteFill style={{ boxShadow: `inset 0 0 200px 30px rgba(230,20,20,${alarm})` }} />
          <div style={{ position: "absolute", left: 52, top: 92, fontFamily: SANS, color: "#fff", textShadow: "0 0 3px #000, 0 0 3px #000, 0 2px 6px #000" }}>
            <div style={{ fontWeight: 900, fontSize: 44, letterSpacing: 3 }}>
              FREITAG · <span style={{ color: flash ? "#ffd23f" : "#fff" }}>{time} UHR</span>
            </div>
            <div style={{ width: 120, height: 5, background: "#e2332b", margin: "8px 0 10px" }} />
            <div style={{ fontWeight: 700, fontSize: 30 }}>Futaba, Präfektur Fukushima</div>
            <div style={{ fontWeight: 600, fontSize: 26, opacity: 0.9 }}>11. März 2011 · 4 km vom Atomkraftwerk</div>
          </div>
          <Banner t={t} at={TL.PING + 0.15} dur={3.6} who="💬 Papa · 14:44" text="Muss heute länger im Kraftwerk bleiben." sub="Passt auf Hana auf! Bis heute Abend :)" />
          <Banner t={t} at={TL.EEW + 0.1} dur={2.2} who="⚠️ 緊急地震速報 · jetzt" text="Erdbeben-Frühwarnung" sub="Starke Erschütterungen erwartet" red />
          <Banner t={t} at={TL.CALL + 1.9} dur={1.2} who="📞 Papa" text="Anruf fehlgeschlagen" sub="Kein Netz" red />
          <Banner t={t} at={TL.TVW + 0.1} dur={3.0} who="⚠️ 大津波警報 · 14:49" text="Große Tsunami-Warnung" sub="Küste Fukushima – sofort in Sicherheit bringen" red />
          {t >= TL.BLACK ? <AbsoluteFill style={{ background: "#000" }} /> : null}
          {hook ? (
            <div style={{ position: "absolute", left: 0, right: 0, top: 700, textAlign: "center", fontFamily: SANS }}>
              <div style={{ display: "inline-block", background: "#111", color: "#fff", fontWeight: 900, fontSize: 52, padding: "12px 26px", border: "5px solid #fff", borderRadius: 12 }}>
                11. MÄRZ 2011
              </div>
              <div style={{ marginTop: 14, color: "#ffd23f", fontWeight: 900, fontSize: 40, WebkitTextStroke: "7px #111", paintOrder: "stroke fill" }}>
                Was wäre, wenn das dein Zuhause wäre?
              </div>
            </div>
          ) : null}
          {q > 0.3 && t > TL.QUAKE + 2.5 && t < TL.QUAKE + 6.5 ? (
            <div style={{ position: "absolute", left: 0, right: 0, top: 560, textAlign: "center", fontFamily: SANS }}>
              <div style={{ display: "inline-block", background: "#111", color: "#ffd23f", fontWeight: 900, fontSize: 54, padding: "10px 26px", border: "5px solid #ffd23f", borderRadius: 12 }}>
                STÄRKE 9,0
              </div>
            </div>
          ) : null}
          <Caption t={t} />
          {jumpCard ? (
            <AbsoluteFill style={{ background: "#0b0b10", alignItems: "center", justifyContent: "center", fontFamily: SANS, color: "#fff", textAlign: "center" }}>
              <div style={{ fontWeight: 900, fontSize: 64, letterSpacing: 4 }}>41 MINUTEN SPÄTER</div>
              <div style={{ fontWeight: 800, fontSize: 40, color: "#ffd23f", marginTop: 16 }}>15:27 UHR</div>
            </AbsoluteFill>
          ) : null}
        </>
      ) : (
        <EndCards t={t - VEND} />
      )}
      <Audio src={staticFile("futaba4/sfx.mp3")} volume={0.9} />
      {LINES.map((ln: any, i: number) => (
        <Sequence key={i} from={Math.round(ln.at * FUTABA4_FPS)}>
          <Audio src={staticFile(AUDIO[ln.id] ?? ln.l.file)} volume={ln.id.startsWith("tv") ? 0.75 : ln.id === "lsp" ? 0.8 : 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
