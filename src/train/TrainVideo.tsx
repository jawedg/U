import React from "react";
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
import { TrainScene } from "./TrainScene";
import { Caption, Word } from "../common/Caption";

type Line = { file: string; seconds: number; words: Word[] };

const SENTENCES = script.sentences as { shot: string; text: string }[];
const LINES = (timing as { lines: Line[] }).lines;

// Fallback ohne Stimme: Dauer nach Wortanzahl schätzen
const lineInfo = (i: number): Line => {
  if (LINES.length === SENTENCES.length) return LINES[i];
  const words = SENTENCES[i].text.split(/\s+/);
  const per = 0.36;
  return {
    file: "",
    seconds: words.length * per + 0.5,
    words: words.map((w, k) => ({ word: w, start: 0.15 + k * per })),
  };
};

export const trainDurationFrames = (fps: number) =>
  SENTENCES.reduce((sum, _, i) => sum + Math.ceil(lineInfo(i).seconds * fps), 0);

const Shot: React.FC<{ index: number; duration: number }> = ({ index, duration }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const D = duration / fps;
  const state = SHOTS[SENTENCES[index].shot](t, D);
  // kurzer "Whip"-Übergang am Anfang jeder Einstellung
  const blur = index === 0 ? 0 : interpolate(frame, [0, 6], [14, 0], { extrapolateRight: "clamp" });
  const flash = index === 0 ? 0 : interpolate(frame, [0, 5], [0.35, 0], { extrapolateRight: "clamp" });
  const red = state.emergency ? state.emergency * (0.35 + 0.25 * Math.sin(t * 16)) : 0;
  return (
    <AbsoluteFill style={{ filter: blur > 0.1 ? `blur(${blur}px)` : undefined }}>
      <ThreeCanvas width={width} height={height} camera={{ fov: 45, near: 0.3, far: 60000 }}>
        <TrainScene s={state} time={t} />
      </ThreeCanvas>
      {/* Vignette */}
      <AbsoluteFill
        style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(5,5,20,0.55) 100%)" }}
      />
      {red > 0 ? (
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse at center, rgba(255,0,40,0) 40%, rgba(255,0,40,${red}) 100%)`,
          }}
        />
      ) : null}
      {flash > 0 ? <AbsoluteFill style={{ backgroundColor: `rgba(255,255,255,${flash})` }} /> : null}
    </AbsoluteFill>
  );
};

export const TrainVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#0b0b16" }}>
      {SENTENCES.map((_, i) => {
        const info = lineInfo(i);
        const dur = Math.ceil(info.seconds * fps);
        const start = from;
        from += dur;
        return (
          <Sequence key={i} from={start} durationInFrames={dur}>
            <Shot index={i} duration={dur} />
            <Caption words={info.words} />
            {info.file ? <Audio src={staticFile(info.file)} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
