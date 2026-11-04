import React from "react";
import "@fontsource/caveat/700.css";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import script from "./script.json";
import timing from "./timing.json";
import { AMBER, HAND, INK, PAPER, SANS, TOPIC, Visual, collectCues } from "../wiso/Visuals";

type Word = { word: string; start: number };
type Line = { file: string; seconds: number; words: Word[] };
type S = { part: number; topic: number; sub: string; text: string; v: any };

const LIST = script.sentences as S[];
const LINES = (timing as { lines: Line[] }).lines;
export const AFPS = 25;

const info = (i: number): Line => {
  if (LINES.length === LIST.length) return LINES[i];
  const ws = LIST[i].text.split(/\s+/);
  return { file: "", seconds: ws.length * 0.37 + 0.6, words: ws.map((w, k) => ({ word: w, start: 0.2 + k * 0.37 })) };
};
const durF = (i: number) => Math.ceil(info(i).seconds * AFPS) + (LIST[i].v.type === "topic" ? 12 : 0);
export const allFrames = () => LIST.reduce((a, _, i) => a + durF(i), 0);

const cueFn = (words: Word[]) => (c?: string) => {
  if (!c) return 0;
  const n = c.toLowerCase();
  const f = words.find((w) => w.word.replace(/[*„“"(),.:!?]/g, "").toLowerCase().startsWith(n));
  return f ? Math.max(0.05, f.start - 0.15) : 0;
};

const KB_NAME = ["Einstieg", "Mitarbeiter in der Arbeitswelt", "Konsument & Recht", "Markt & Wirtschaft", "Selbstständigkeit", "Abschluss"];
const KB_CHIP = ["WiSo", "KB I", "KB II", "KB III", "KB IV", "WiSo"];

const Header: React.FC<{ s: S; globalP: number }> = ({ s, globalP }) => (
  <AbsoluteFill style={{ height: 100 }}>
    <div style={{ position: "absolute", top: 0, left: 0, height: 8, width: `${globalP * 100}%`, background: TOPIC[s.topic] }} />
    <div style={{ position: "absolute", top: 22, left: 40, display: "flex", alignItems: "center", gap: 14 }}>
      <div style={{ background: TOPIC[s.topic], color: "#fff", fontFamily: SANS, fontWeight: 900, fontSize: 28, padding: "10px 22px", borderRadius: 30 }}>{KB_CHIP[s.topic]}</div>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: INK }}>{KB_NAME[s.topic]}</div>
    </div>
    <div style={{ position: "absolute", top: 22, right: 40, display: "flex", gap: 10, alignItems: "center" }}>
      {[1, 2, 3, 4].map((k) => (
        <div key={k} style={{ width: 16, height: 16, borderRadius: 8, background: k === s.topic ? TOPIC[k] : k < s.topic ? `${TOPIC[k]}88` : "#e2e8f0" }} />
      ))}
      <div style={{ marginLeft: 10, fontFamily: HAND, fontWeight: 700, fontSize: 40, color: s.sub.startsWith("Prüfungs") ? AMBER : TOPIC[s.topic] }}>{s.sub}</div>
    </div>
  </AbsoluteFill>
);

const Subtitle: React.FC<{ words: Word[]; color: string }> = ({ words, color }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (!words.length || t < words[0].start - 0.1) return null;
  const sents: Word[][] = [[]];
  words.forEach((w) => {
    sents[sents.length - 1].push(w);
    if (/[.!?]$/.test(w.word.replace(/\*/g, "")) || (sents[sents.length - 1].length > 22 && /[,:]$/.test(w.word))) sents.push([]);
  });
  const cur = sents.filter((x) => x.length).reduce((acc, x) => (t >= x[0].start - 0.1 ? x : acc), sents[0]);
  return (
    <AbsoluteFill style={{ top: 880, height: 190, alignItems: "center", justifyContent: "center" }}>
      <div style={{ maxWidth: 1700, textAlign: "center", fontFamily: SANS, fontWeight: 650, fontSize: 40, lineHeight: 1.35, background: "rgba(255,255,255,0.92)", borderRadius: 22, padding: "14px 30px", boxShadow: "0 6px 20px rgba(0,0,0,0.08)" }}>
        {cur.map((w, i) => {
          const key = w.word.includes("*");
          const spoken = t >= w.start;
          return (
            <span key={i} style={{ color: key ? color : INK, fontWeight: key ? 850 : 650, opacity: spoken ? 1 : 0.35 }}>
              {w.word.replace(/\*/g, "")}{" "}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ i: number; dur: number; start: number; total: number }> = ({ i, dur, start, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const s = LIST[i];
  const ln = info(i);
  const enter = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Header s={s} globalP={(start + frame) / total} />
      <AbsoluteFill style={{ top: 100, height: 770, opacity: enter, transform: `translateY(${(1 - enter) * 20}px)` }}>
        <Visual v={s.v} t={t} D={dur / fps} cue={cueFn(ln.words)} topic={s.topic} />
      </AbsoluteFill>
      <Subtitle words={ln.words} color={TOPIC[s.topic]} />
    </AbsoluteFill>
  );
};

export const AllVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const total = allFrames();
  let from = 0;
  return (
    <AbsoluteFill
      style={{
        backgroundColor: PAPER,
        backgroundImage: "linear-gradient(#e7eef7 2px, transparent 2px), linear-gradient(90deg, #e7eef7 2px, transparent 2px)",
        backgroundSize: "48px 48px",
      }}
    >
      {LIST.map((s, i) => {
        const ln = info(i);
        const dur = durF(i);
        const start = from;
        from += dur;
        const cue = cueFn(ln.words);
        const pops = Array.from(new Set(collectCues(s.v).map((c) => cue(c)).filter((x) => x > 0.3)));
        const lead = s.v.type === "topic" ? 12 : 0;
        return (
          <Sequence key={i} from={start} durationInFrames={dur}>
            <Scene i={i} dur={dur} start={start} total={total} />
            {ln.file ? (
              <Sequence from={lead}>
                <Audio src={staticFile(ln.file)} />
              </Sequence>
            ) : null}
            {s.v.type === "topic" ? <Audio src={staticFile("wiso/sfx/whoosh.mp3")} volume={0.5} /> : null}
            {s.v.type === "exam" ? <Audio src={staticFile("wiso/sfx/ding.mp3")} volume={0.25} /> : null}
            {pops.map((p, k) => (
              <Sequence key={k} from={Math.round((p + lead / fps) * fps)}>
                <Audio src={staticFile("wiso/sfx/pop.mp3")} volume={0.18} />
              </Sequence>
            ))}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
