import React from "react";
import "@fontsource/amiri/700.css";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import script from "./script.json";
import timing from "./timing.json";
import { SHOTS } from "./shots";
import { AthanScene } from "./AthanScene";
import { Caption, Word } from "../common/Caption";

type Line = { file: string; seconds: number; words: Word[] };
type Scene = { shot: string; text: string; athan?: boolean };

const SCENES = script.sentences as Scene[];
const LINES = (timing as { lines: Line[] }).lines;
const ATHAN_FILE = (script as { athanFile: string | null }).athanFile;
const ATHAN_SECONDS = (script as { athanSeconds: number }).athanSeconds;

const lineInfo = (i: number): Line => {
  if (LINES.length === SCENES.length) return LINES[i];
  const s = SCENES[i];
  if (!s.text) return { file: "", seconds: ATHAN_SECONDS, words: [] };
  const words = s.text.split(/\s+/);
  return { file: "", seconds: words.length * 0.36 + 0.5, words: words.map((w, k) => ({ word: w, start: 0.15 + k * 0.36 })) };
};

export const athanDurationFrames = (fps: number) =>
  SCENES.reduce((sum, _, i) => sum + Math.ceil(lineInfo(i).seconds * fps), 0);

const ARABIC: React.CSSProperties = {
  fontFamily: "Amiri, 'DejaVu Sans', serif",
  fontWeight: 700,
  color: "#ffe2a0",
  textShadow: "0 0 30px rgba(255,190,90,0.8), 0 4px 18px rgba(0,0,0,0.7)",
  direction: "rtl",
};

const Overlay: React.FC<{ shot: string; info: Line; dur: number }> = ({ shot, info, dur }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const D = dur / fps;
  const fade = (a: number, b: number) =>
    interpolate(t, [a, a + 0.6, b - 0.5, b], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  if (shot === "hook") {
    const o = fade(0.2, D);
    return (
      <AbsoluteFill style={{ alignItems: "center", top: 250 }}>
        <div style={{ fontFamily: "Inter, sans-serif", fontWeight: 800, fontSize: 44, letterSpacing: 8, color: "rgba(255,230,180,0.9)", opacity: o }}>
          DER ERSTE ADHAN
        </div>
        <div style={{ ...ARABIC, fontSize: 80, marginTop: 10, opacity: o }}>الأَذَان</div>
      </AbsoluteFill>
    );
  }
  if (shot === "words") {
    const o = fade(D * 0.55, D);
    return (
      <AbsoluteFill style={{ alignItems: "center", top: 330, opacity: o }}>
        <div style={{ ...ARABIC, fontSize: 130 }}>اللّٰهُ أَكْبَرُ</div>
      </AbsoluteFill>
    );
  }
  if (shot === "desert") {
    const ahad = info.words.find((w) => w.word.includes("Ahad"));
    if (!ahad) return null;
    const o = fade(ahad.start, D);
    return (
      <AbsoluteFill style={{ alignItems: "center", top: 330, opacity: o }}>
        <div style={{ ...ARABIC, fontSize: 170 }}>أَحَد</div>
      </AbsoluteFill>
    );
  }
  if (shot === "athan") {
    const o = fade(0.8, D);
    return (
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", opacity: o }}>
        <div style={{ ...ARABIC, fontSize: 120 }}>اللّٰهُ أَكْبَرُ</div>
        <div style={{ ...ARABIC, fontSize: 120, marginTop: -10 }}>اللّٰهُ أَكْبَرُ</div>
        <div style={{ fontFamily: "Inter, sans-serif", fontWeight: 700, fontSize: 46, color: "white", marginTop: 30, textShadow: "0 3px 12px rgba(0,0,0,0.8)" }}>
          Allahu Akbar
        </div>
        <div style={{ fontFamily: "Inter, sans-serif", fontWeight: 500, fontSize: 38, color: "rgba(255,255,255,0.85)", marginTop: 6, textShadow: "0 3px 12px rgba(0,0,0,0.8)" }}>
          Allah ist der Größte
        </div>
      </AbsoluteFill>
    );
  }
  return null;
};

const Shot: React.FC<{ index: number; duration: number }> = ({ index, duration }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const state = SHOTS[SCENES[index].shot](t, duration / fps);
  const blur = index === 0 ? 0 : interpolate(frame, [0, 7], [10, 0], { extrapolateRight: "clamp" });
  const dark = index === 0 ? interpolate(frame, [0, 12], [1, 0], { extrapolateRight: "clamp" }) : interpolate(frame, [0, 6], [0.5, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ filter: blur > 0.1 ? `blur(${blur}px)` : undefined }}>
      <ThreeCanvas width={width} height={height} camera={{ fov: 50, near: 0.1, far: 60000 }}>
        <AthanScene s={state} time={t + index * 3.7} />
      </ThreeCanvas>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(5,5,15,0.6) 100%)" }} />
      {dark > 0 ? <AbsoluteFill style={{ backgroundColor: `rgba(0,0,0,${dark})` }} /> : null}
    </AbsoluteFill>
  );
};

export const AthanVideo: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();
  let from = 0;
  const starts = SCENES.map((_, i) => {
    const st = from;
    from += Math.ceil(lineInfo(i).seconds * fps);
    return st;
  });
  const athanIdx = SCENES.findIndex((s) => s.athan);
  const aStart = athanIdx >= 0 ? starts[athanIdx] : -1;
  const aLen = athanIdx >= 0 ? Math.ceil(lineInfo(athanIdx).seconds * fps) : 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#05060f" }}>
      {SCENES.map((s, i) => {
        const info = lineInfo(i);
        const dur = Math.ceil(info.seconds * fps);
        return (
          <Sequence key={i} from={starts[i]} durationInFrames={dur}>
            <Shot index={i} duration={dur} />
            <Overlay shot={s.shot} info={info} dur={dur} />
            <Caption words={info.words} top={s.shot === "words" || s.shot === "desert" ? 260 : 120} />
            {info.file ? <Audio src={staticFile(info.file)} /> : null}
          </Sequence>
        );
      })}
      {/* leiser Wind, beim Adhan noch leiser */}
      <Audio
        src={staticFile("athan/wind.mp3")}
        volume={(f) =>
          interpolate(f, [0, 30, durationInFrames - 45, durationInFrames], [0, 0.35, 0.35, 0], { extrapolateRight: "clamp" }) *
          (aStart >= 0 && f > aStart - 10 && f < aStart + aLen + 10 ? 0.4 : 1)
        }
      />
      {ATHAN_FILE && aStart >= 0 ? (
        <Sequence from={aStart} durationInFrames={aLen}>
          <Audio
            src={staticFile(ATHAN_FILE)}
            volume={(f) => interpolate(f, [0, 15, aLen - 45, aLen], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </Sequence>
      ) : null}
    </AbsoluteFill>
  );
};
