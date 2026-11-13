// „Blindflug im Reaktor“: Blender-Rendering (blender/fuku/fuku.py) + Zeitstempel, Untertitel, Schlusskarte, Ton.
import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import script from "./script.json";
import timing from "./timing.json";

export const FUKU_FPS = 24;
import extra from "../fuku_extra/timing.json";
const COLD_FROM = 41.6; // Ausschnitt aus dem Blackout für den Einstieg
const COLD = 6.6;
const CARD = 1.0;
const OFF = COLD + CARD;
const TAIL = 6.6 + 3.4;
export const FUKU_FRAMES = Math.round((OFF + 59.4 + TAIL) * FUKU_FPS);
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const END = 59.4;
const AT: Record<string, number> = { n1: 1.0, k1a: 10.8, n2: 15.6, k1b: 32.4, k2a: 35.8, n3: 41.2, k1c: 48.9, n4: 51.4 };
const WHO: Record<string, string> = { k1: "KOLLEGE", k2: "SCHICHTLEITER" };
const HOT = /^(9|Japan|Batterien|Autos|Alles|Steuerstäbe|Tsunami|6|doppelt|tot|Strom|Kühlpumpen|blind|Kernschmelze|Strahlung|Notstrom-Generatoren|überflutet|heiß)/;
const LINES = (script as any).sentences.map((s: any, i: number) => ({ ...s, at: AT[s.id], l: (timing as any).lines[i] }));

const Caption: React.FC<{ t: number; lines?: any[] }> = ({ t, lines = LINES }) => {
  for (const ln of lines) {
    const local = t - ln.at;
    if (local < -0.05 || local > ln.l.seconds - 0.1) continue;
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
    const who = WHO[ln.id.slice(0, 2)];
    const pop = spring({ frame: Math.round((local - c.s) * FUKU_FPS), fps: FUKU_FPS, config: { damping: 14, stiffness: 220 } });
    return (
      <div style={{ position: "absolute", left: 50, right: 50, top: 1330, textAlign: "center" }}>
        {who ? <div style={{ display: "inline-block", fontFamily: SANS, fontWeight: 800, fontSize: 24, letterSpacing: 4, color: "#000", background: "#ffd23f", borderRadius: 8, padding: "6px 14px", marginBottom: 14 }}>{who}</div> : null}
        <div style={{ transform: `scale(${0.9 + 0.1 * pop})`, fontFamily: SANS, fontWeight: 900, fontSize: 66, lineHeight: 1.12, color: "#fff", WebkitTextStroke: "10px #000", paintOrder: "stroke fill", textShadow: "0 6px 18px rgba(0,0,0,0.7)" }}>
          {c.ws.map((w, i) => (
            <span key={i} style={{ color: HOT.test(w) ? (who ? "#ff4b3e" : "#ffd23f") : "#fff" }}>
              {w}{" "}
            </span>
          ))}
        </div>
      </div>
    );
  }
  return null;
};

const MainPart: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUKU_FPS;
  const time = t < 22.0 ? "14:46" : t < 28.4 ? "14:49" : t < 31.0 ? "15:35" : "15:37";
  const jump = [22.0, 28.4, 31.0].some((x) => t >= x && t < x + 0.5);
  const red = t > 51 && t < END ? (0.5 + 0.5 * Math.sin((t - 51.2) * Math.PI / 0.6)) * 0.45 : 0;
  const black = t >= END;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {!black ? <OffthreadVideo src={staticFile("fuku/render.mp4")} /> : null}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, transparent 50%, rgba(0,0,0,0.6) 100%)" }} />
      <AbsoluteFill style={{ boxShadow: `inset 0 0 220px 40px rgba(255,20,10,${red})` }} />
      {!black ? (
        <div style={{ position: "absolute", right: 46, top: 110, textAlign: "right", fontFamily: SANS, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>
          <div style={{ fontWeight: 800, fontSize: 30, letterSpacing: 2 }}>
            11. MÄRZ 2011 • <span style={{ color: jump ? "#ffd23f" : "#fff" }}>{time} UHR</span>
          </div>
          <div style={{ fontWeight: 600, fontSize: 22, letterSpacing: 4, opacity: 0.8, marginTop: 6 }}>FUKUSHIMA DAIICHI, JAPAN</div>
        </div>
      ) : null}
      {!black ? <Caption t={t} /> : null}
      <Audio src={staticFile("fuku/sfx.mp3")} volume={0.85} />
      {LINES.map((ln: any, i: number) => (
        <Sequence key={i} from={Math.round(ln.at * FUKU_FPS)}>
          <Audio src={staticFile(ln.l.file)} volume={ln.id.startsWith("k1c") ? 0.8 : 1} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

const EX = (extra as any).lines;
const COLD_LINE = [{ id: "cold", at: 0.3, l: EX[0] }];
const BAT_LINE = [{ id: "bat", at: 0.5, l: EX[1] }];

const ColdOpen: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUKU_FPS;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <OffthreadVideo src={staticFile("fuku/render.mp4")} startFrom={Math.round(COLD_FROM * FUKU_FPS)} muted />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 50%, transparent 45%, rgba(0,0,0,0.65) 100%)" }} />
      <div style={{ position: "absolute", right: 46, top: 110, textAlign: "right", fontFamily: SANS, color: "#fff", textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>
        <div style={{ fontWeight: 800, fontSize: 30, letterSpacing: 2 }}>11. MÄRZ 2011 • <span style={{ color: "#ff4b3e" }}>15:37 UHR</span></div>
        <div style={{ fontWeight: 600, fontSize: 22, letterSpacing: 4, opacity: 0.8, marginTop: 6 }}>FUKUSHIMA DAIICHI, JAPAN</div>
      </div>
      <Caption t={t} lines={COLD_LINE} />
      <Audio src={staticFile("fuku/sfx.mp3")} startFrom={Math.round(COLD_FROM * FUKU_FPS)} volume={0.85} />
      <Audio src={staticFile(EX[0].file)} startFrom={0} />
    </AbsoluteFill>
  );
};

const TimeCard: React.FC = () => {
  const f = useCurrentFrame();
  const txt = "50 MINUTEN VORHER";
  return (
    <AbsoluteFill style={{ background: "#000", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 64, letterSpacing: 6, color: "#fff" }}>{txt.slice(0, Math.min(txt.length, Math.floor(f * 1.4) + 1))}</div>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: 4, color: "#ffd23f", marginTop: 20, opacity: f > 8 ? 1 : 0 }}>14:46 UHR</div>
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / FUKU_FPS;
  const card = interpolate(t, [6.6, 7.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {t < 6.5 ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 8, color: "#ffd23f", opacity: 0.9, marginBottom: 600 }}>WAHRE BEGEBENHEIT</div>
        </AbsoluteFill>
      ) : null}
      {t < 6.5 ? <Caption t={t} lines={BAT_LINE} /> : null}
      <AbsoluteFill style={{ opacity: card, alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: SANS, color: "#fff" }}>
        <div style={{ fontWeight: 700, fontSize: 28, letterSpacing: 8, opacity: 0.7 }}>WAHRE BEGEBENHEIT</div>
        <div style={{ fontWeight: 900, fontSize: 72, lineHeight: 1.1, marginTop: 24 }}>
          WÄRST DU
          <br />
          REINGEGANGEN?
        </div>
        <div style={{ fontWeight: 600, fontSize: 30, opacity: 0.75, marginTop: 40 }}>Teil 2: Die Explosionen</div>
      </AbsoluteFill>
      <Audio src={staticFile(EX[1].file)} startFrom={0} volume={1} />
      <Audio src={staticFile("fuku/sfx.mp3")} startFrom={Math.round(59.4 * FUKU_FPS)} volume={0.85} />
    </AbsoluteFill>
  );
};

export const FukuVideo: React.FC = () => (
  <AbsoluteFill style={{ background: "#000" }}>
    <Sequence durationInFrames={Math.round(COLD * FUKU_FPS)}>
      <ColdOpen />
    </Sequence>
    <Sequence from={Math.round(COLD * FUKU_FPS)} durationInFrames={Math.round(CARD * FUKU_FPS)}>
      <TimeCard />
    </Sequence>
    <Sequence from={Math.round(OFF * FUKU_FPS)} durationInFrames={Math.round(59.4 * FUKU_FPS)}>
      <MainPart />
    </Sequence>
    <Sequence from={Math.round((OFF + 59.4) * FUKU_FPS)}>
      <Outro />
    </Sequence>
  </AbsoluteFill>
);
