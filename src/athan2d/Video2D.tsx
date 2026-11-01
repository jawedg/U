import React from "react";
import "@fontsource/amiri/700.css";
import { AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import script from "./script.json";
import timing from "./timing.json";
import { Defs, GOLD } from "./art";
import { SCENES, SceneProps, WordFn } from "./scenes";

type Word = { word: string; start: number };
type Line = { file: string; seconds: number; words: Word[] };
type S = { shot: string; text: string; athan?: boolean };

const LIST = script.sentences as S[];
const LINES = (timing as { lines: Line[] }).lines;
const ATHAN_FILE = (script as { athanFile: string | null }).athanFile;
const ATHAN_SECONDS = (script as { athanSeconds: number }).athanSeconds;

const info = (i: number): Line => {
  if (LINES.length === LIST.length) return LINES[i];
  const s = LIST[i];
  if (!s.text) return { file: "", seconds: ATHAN_SECONDS, words: [] };
  const ws = s.text.split(/\s+/);
  return { file: "", seconds: ws.length * 0.36 + 0.5, words: ws.map((w, k) => ({ word: w, start: 0.15 + k * 0.36 })) };
};

export const video2dFrames = (fps: number) => LIST.reduce((a, _, i) => a + Math.ceil(info(i).seconds * fps), 0);

const wordFn = (words: Word[]): WordFn => (needle, fallback = 0) => {
  const f = words.find((w) => w.word.replace(/\*/g, "").toLowerCase().startsWith(needle.toLowerCase()));
  return f ? f.start : fallback;
};

// Untertitel: aktueller Satz, gesprochene Wörter hell, Schlüsselwörter gold
const Subtitle: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (!words.length || t < words[0].start - 0.1) return null;
  const sentences: Word[][] = [[]];
  words.forEach((w) => {
    sentences[sentences.length - 1].push(w);
    if (/[.!?]$/.test(w.word.replace(/\*/g, ""))) sentences.push([]);
  });
  const cur = sentences.filter((s) => s.length).reduce((acc, s) => (t >= s[0].start - 0.1 ? s : acc), sentences[0]);
  const appear = interpolate(t, [cur[0].start - 0.1, cur[0].start + 0.15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ top: 1420, height: 260, alignItems: "center", opacity: appear }}>
      <div style={{ width: 920, textAlign: "center", fontFamily: "Inter, sans-serif", fontWeight: 700, fontSize: 50, lineHeight: 1.3 }}>
        {cur.map((w, i) => {
          const key = w.word.includes("*");
          const spoken = t >= w.start;
          const clean = w.word.replace(/\*/g, "");
          return (
            <span
              key={i}
              style={{
                color: key && spoken ? GOLD : "#f3ecdc",
                opacity: spoken ? 1 : 0.32,
                textShadow: "0 2px 10px rgba(0,0,0,0.9)",
              }}
            >
              {clean}{" "}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ i: number; dur: number }> = ({ i, dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const D = dur / fps;
  const s = LIST[i];
  const def = SCENES[s.shot];
  const ln = info(i);
  const p: SceneProps = { t, D, w: wordFn(ln.words) };
  const fadeIn = interpolate(frame, [0, 9], [0, 1], { extrapolateRight: "clamp" });
  const fadeOut = i === LIST.length - 1 ? interpolate(frame, [dur - 20, dur], [1, 0], { extrapolateLeft: "clamp" }) : 1;
  const ar = def.arabic?.(p);
  const Draw = def.draw;
  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <Defs />
        {/* Bühne 30 % größer, Drehpunkt = Bodenlinie */}
        <g transform="translate(540,1310) scale(1.3) translate(-540,-1310)">
          <Draw {...p} />
        </g>
        {/* Papier-Körnung + Vignette */}
        <rect width="1080" height="1920" filter="url(#grain)" />
        <radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">
          <stop offset="0.6" stopColor="#000" stopOpacity="0" />
          <stop offset="1" stopColor="#000" stopOpacity="0.65" />
        </radialGradient>
        <rect width="1080" height="1920" fill="url(#vig)" />
        {/* dunkle Fläche hinter den Untertiteln */}
        <rect y="1390" width="1080" height="530" fill="#07080f" opacity={0.9} />
      </svg>
      {def.label ? (
        <AbsoluteFill style={{ top: 170, alignItems: "center" }}>
          <div style={{ fontFamily: "Inter, sans-serif", fontWeight: 700, fontSize: 30, letterSpacing: 7, color: "rgba(243,236,220,0.6)" }}>{def.label}</div>
        </AbsoluteFill>
      ) : null}
      {ar && ar.o > 0 ? (
        <AbsoluteFill style={{ top: 225, alignItems: "center", opacity: ar.o }}>
          <div style={{ fontFamily: "Amiri, serif", fontWeight: 700, fontSize: 84, color: "#f3ecdc", direction: "rtl", textShadow: "0 0 24px rgba(230,184,92,0.45)" }}>{ar.text}</div>
          {ar.sub ? <div style={{ fontFamily: "Inter, sans-serif", fontWeight: 500, fontSize: 32, color: GOLD, marginTop: 4 }}>{ar.sub}</div> : null}
        </AbsoluteFill>
      ) : null}
      <Subtitle words={ln.words} />
    </AbsoluteFill>
  );
};

export const Video2D: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();
  let from = 0;
  const starts = LIST.map((_, i) => {
    const st = from;
    from += Math.ceil(info(i).seconds * fps);
    return st;
  });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0d16" }}>
      {LIST.map((s, i) => {
        const ln = info(i);
        const dur = Math.ceil(ln.seconds * fps);
        const def = SCENES[s.shot];
        const p: SceneProps = { t: 0, D: dur / fps, w: wordFn(ln.words) };
        const fx = def.sfx?.(p) ?? [];
        const ambGain = (def.ambGain ?? 1) * 0.55;
        return (
          <Sequence key={i} from={starts[i]} durationInFrames={dur}>
            <Scene i={i} dur={dur} />
            {ln.file ? <Audio src={staticFile(ln.file)} /> : null}
            {/* Atmo dieser Szene (weich ein/aus) */}
            <Audio
              src={staticFile(`athan2d/sfx/${def.amb}.mp3`)}
              loop
              volume={(f) => ambGain * interpolate(f, [0, 10, dur - 10, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
            />
            {def.whoosh ? <Audio src={staticFile("athan2d/sfx/whoosh.mp3")} volume={0.35} /> : null}
            {fx.map((e, k) => (
              <Sequence key={k} from={Math.max(0, Math.round(e.at * fps))}>
                <Audio src={staticFile(`athan2d/sfx/${e.file}.mp3`)} volume={e.gain ?? 0.6} />
              </Sequence>
            ))}
            {s.athan && ATHAN_FILE ? (
              <Audio
                src={staticFile(ATHAN_FILE)}
                volume={(f) => interpolate(f, [0, 15, dur - 45, dur], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
              />
            ) : null}
          </Sequence>
        );
      })}
      {/* durchgehender, leiser Wind als Bett */}
      <Audio
        src={staticFile("athan/wind.mp3")}
        volume={(f) => 0.18 * interpolate(f, [0, 30, durationInFrames - 30, durationInFrames], [0, 1, 1, 0], { extrapolateRight: "clamp" })}
      />
    </AbsoluteFill>
  );
};
