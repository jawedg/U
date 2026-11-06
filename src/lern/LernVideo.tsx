import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import s1 from "../lern_kb1/script.json";
import s2 from "../lern_kb2/script.json";
import s3 from "../lern_kb3/script.json";
import s4 from "../lern_kb4/script.json";
import t1 from "../lern_kb1/timing.json";
import t2 from "../lern_kb2/timing.json";
import t3 from "../lern_kb3/timing.json";
import t4 from "../lern_kb4/timing.json";
import s5 from "../lern_gk/script.json";
import t5 from "../lern_gk/timing.json";
import { collectCues } from "../wiso/Visuals";
import { BG, INK, LINE, MUTED, MinVisual, SANS, accent, kbLabel } from "./Min";

type Word = { word: string; start: number };
type Line = { file: string; seconds: number; words: Word[] };
type Scene = { topic: number; tname: string; text: string; part: number; v: any };
type Script = { kb: number; title: string; topics: string[]; sentences: Scene[] };

export const LFPS = 25;
const DATA: Record<number, { s: Script; t: Line[] }> = {
  1: { s: s1 as Script, t: (t1 as { lines: Line[] }).lines },
  2: { s: s2 as Script, t: (t2 as { lines: Line[] }).lines },
  3: { s: s3 as Script, t: (t3 as { lines: Line[] }).lines },
  4: { s: s4 as Script, t: (t4 as { lines: Line[] }).lines },
  5: { s: s5 as Script, t: (t5 as { lines: Line[] }).lines },
};

const info = (kb: number, i: number): Line => {
  const { s, t } = DATA[kb];
  if (t.length === s.sentences.length) return t[i];
  const ws = s.sentences[i].text.split(/\s+/);
  return { file: "", seconds: ws.length * 0.38 + 0.6, words: ws.map((w, k) => ({ word: w, start: 0.2 + k * 0.38 })) };
};
const lead = (sc: Scene) => (sc.v.type === "topic" ? 10 : 0);
const durF = (kb: number, i: number) => Math.ceil(info(kb, i).seconds * LFPS) + lead(DATA[kb].s.sentences[i]);
export const lernFrames = (kb: number) => DATA[kb].s.sentences.reduce((a, _, i) => a + durF(kb, i), 0);

const cueFn = (words: Word[]) => (c?: string) => {
  if (!c) return 0;
  const n = c.toLowerCase();
  const f = words.find((w) => w.word.replace(/[*„“"(),.:!?]/g, "").toLowerCase().startsWith(n));
  return f ? Math.max(0.05, f.start - 0.15) : 0;
};

const Header: React.FC<{ kb: number; sc: Scene; topics: string[]; title: string; p: number }> = ({ kb, sc, topics, title, p }) => (
  <AbsoluteFill style={{ height: 110 }}>
    <div style={{ position: "absolute", top: 0, left: 0, height: 5, width: `${p * 100}%`, background: accent(kb) }} />
    <div style={{ position: "absolute", top: 40, left: 60, display: "flex", alignItems: "center", gap: 16, fontFamily: SANS }}>
      <div style={{ width: 14, height: 14, background: accent(kb) }} />
      <div style={{ fontWeight: 900, fontSize: 26, color: accent(kb), letterSpacing: 2 }}>{kbLabel(kb)}</div>
      <div style={{ fontWeight: 500, fontSize: 26, color: MUTED }}>{title}</div>
    </div>
    {sc.topic > 0 ? (
      <div style={{ position: "absolute", top: 40, right: 60, fontFamily: SANS, fontSize: 26, display: "flex", gap: 14 }}>
        <span style={{ color: MUTED, fontWeight: 600 }}>Thema {sc.topic}/{topics.length}</span>
        <span style={{ color: INK, fontWeight: 800 }}>{sc.tname}</span>
      </div>
    ) : null}
    <div style={{ position: "absolute", top: 100, left: 60, right: 60, height: 1, background: LINE }} />
  </AbsoluteFill>
);

const Subtitle: React.FC<{ words: Word[]; kb: number }> = ({ words, kb }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (!words.length || t < words[0].start - 0.1) return null;
  const sents: Word[][] = [[]];
  words.forEach((w) => {
    sents[sents.length - 1].push(w);
    if (/[.!?]$/.test(w.word.replace(/\*/g, "")) || (sents[sents.length - 1].length > 20 && /[,:]$/.test(w.word))) sents.push([]);
  });
  const cur = sents.filter((x) => x.length).reduce((acc, x) => (t >= x[0].start - 0.1 ? x : acc), sents[0]);
  return (
    <AbsoluteFill style={{ top: 920, height: 140, alignItems: "center", justifyContent: "center" }}>
      <div style={{ maxWidth: 1600, textAlign: "center", fontFamily: SANS, fontWeight: 550, fontSize: 36, lineHeight: 1.35 }}>
        {cur.map((w, i) => {
          const key = w.word.includes("*");
          return (
            <span key={i} style={{ color: key ? accent(kb) : INK, fontWeight: key ? 800 : 550, opacity: t >= w.start ? 1 : 0.3 }}>
              {w.word.replace(/\*/g, "")}{" "}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const SceneView: React.FC<{ kb: number; i: number; dur: number; start: number; total: number }> = ({ kb, i, dur, start, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { s } = DATA[kb];
  const sc = s.sentences[i];
  const ln = info(kb, i);
  const enter = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Header kb={kb} sc={sc} topics={s.topics} title={s.title} p={(start + frame) / total} />
      <AbsoluteFill style={{ top: 110, height: 800, opacity: enter }}>
        <MinVisual v={sc.v} t={frame / fps} D={dur / fps} cue={cueFn(ln.words)} kb={kb} topics={s.topics} topicNo={sc.topic} />
      </AbsoluteFill>
      <Subtitle words={ln.words} kb={kb} />
    </AbsoluteFill>
  );
};

export const LernVideo: React.FC<{ kb: number }> = ({ kb }) => {
  const { fps } = useVideoConfig();
  const total = lernFrames(kb);
  const { s } = DATA[kb];
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: BG }}>
      {s.sentences.map((sc, i) => {
        const ln = info(kb, i);
        const dur = durF(kb, i);
        const start = from;
        from += dur;
        const cue = cueFn(ln.words);
        const pops = Array.from(new Set(collectCues(sc.v).map((c) => cue(c)).filter((x) => x > 0.3)));
        const l = lead(sc);
        return (
          <Sequence key={i} from={start} durationInFrames={dur}>
            <SceneView kb={kb} i={i} dur={dur} start={start} total={total} />
            {ln.file ? (
              <Sequence from={l}>
                <Audio src={staticFile(ln.file)} />
              </Sequence>
            ) : null}
            {sc.v.type === "topic" ? <Audio src={staticFile("wiso/sfx/whoosh.mp3")} volume={0.35} /> : null}
            {sc.v.type === "merke" ? <Audio src={staticFile("wiso/sfx/ding.mp3")} volume={0.18} /> : null}
            {pops.map((p, k) => (
              <Sequence key={k} from={Math.round((p + l / fps) * fps)}>
                <Audio src={staticFile("wiso/sfx/pop.mp3")} volume={0.12} />
              </Sequence>
            ))}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
