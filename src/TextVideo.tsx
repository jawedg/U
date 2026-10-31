import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { SCENES, TITLE, Scene } from "./script";
import voice from "./voice.json";

type VoiceInfo = { file: string; seconds: number };
const VOICE = (voice as { scenes: VoiceInfo[] }).scenes;
const hasVoice = VOICE.length === SCENES.length;

const COLORS = ["#ff2d55", "#00e5ff", "#ffd60a", "#7cff6b", "#bf5af2", "#ff9f0a"];

// Ohne Stimme: Dauer nach Wortanzahl. Mit Stimme: Länge der Audiodatei + kurze Pause.
export const sceneDurations = (fps: number): number[] =>
  SCENES.map((s, i) => {
    if (hasVoice) return Math.ceil((VOICE[i].seconds + 0.35) * fps);
    const words = s.text.split(/\s+/).length;
    return Math.round((1.2 + words * 0.38) * fps);
  });

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const a = frame * 0.6;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${50 + 30 * Math.sin(a / 40)}% ${
          35 + 20 * Math.cos(a / 55)
        }%, #3a1c71 0%, #1b1035 45%, #07060f 100%)`,
      }}
    >
      {/* weiche, schwebende Lichtpunkte */}
      {new Array(14).fill(0).map((_, i) => {
        const x = (i * 137) % 100;
        const y = (((i * 61 + frame * (0.15 + (i % 4) * 0.08)) % 120) + 120) % 120 - 10;
        const size = 60 + (i % 5) * 50;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `${x}%`,
              top: `${100 - y}%`,
              width: size,
              height: size,
              borderRadius: "50%",
              background: COLORS[i % COLORS.length],
              opacity: 0.08,
              filter: "blur(30px)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

const Words: React.FC<{ scene: Scene; index: number; duration: number }> = ({
  scene,
  index,
  duration,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = scene.text.split(/\s+/);
  const accent = COLORS[index % COLORS.length];
  // Wörter erscheinen gleichmäßig verteilt über ~75 % der Szene (passt grob zur Stimme)
  const step = (duration * 0.75) / words.length;

  const exit = interpolate(frame, [duration - 6, duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const emojiPop = spring({ frame, fps, config: { damping: 9, stiffness: 120 } });

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 90px",
        opacity: exit,
        transform: `scale(${0.96 + 0.04 * exit})`,
      }}
    >
      {scene.emoji ? (
        <div
          style={{
            fontSize: 190,
            marginBottom: 50,
            transform: `scale(${emojiPop}) rotate(${(1 - emojiPop) * -25}deg)`,
          }}
        >
          {scene.emoji}
        </div>
      ) : null}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: "10px 26px",
          textAlign: "center",
        }}
      >
        {words.map((w, i) => {
          const highlighted = w.includes("*");
          const clean = w.replace(/\*/g, "");
          const start = i * step;
          const s = spring({ frame: frame - start, fps, config: { damping: 12, stiffness: 180 } });
          const active = frame >= start && frame < start + step + 2;
          return (
            <span
              key={i}
              style={{
                fontFamily: "Inter, 'DejaVu Sans', sans-serif",
                fontWeight: 900,
                fontSize: 104,
                lineHeight: 1.12,
                color: highlighted ? accent : "white",
                opacity: s,
                transform: `translateY(${(1 - s) * 50}px) scale(${active ? 1.08 : 1})`,
                textShadow: highlighted
                  ? `0 0 40px ${accent}aa, 0 6px 0 rgba(0,0,0,0.5)`
                  : "0 6px 0 rgba(0,0,0,0.5)",
                display: "inline-block",
              }}
            >
              {clean}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Header: React.FC<{ total: number }> = ({ total }) => {
  const frame = useCurrentFrame();
  const progress = Math.min(1, frame / total);
  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: 190,
          width: "100%",
          textAlign: "center",
          fontFamily: "Inter, sans-serif",
          fontWeight: 800,
          fontSize: 46,
          letterSpacing: 6,
          color: "rgba(255,255,255,0.75)",
          textTransform: "uppercase",
        }}
      >
        {TITLE}
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 300,
          left: 140,
          right: 140,
          height: 10,
          borderRadius: 10,
          background: "rgba(255,255,255,0.15)",
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: "100%",
            borderRadius: 10,
            background: "linear-gradient(90deg,#ff2d55,#00e5ff)",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const TextVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const durations = sceneDurations(fps);
  const total = durations.reduce((a, b) => a + b, 0);
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Background />
      {SCENES.map((scene, i) => {
        const start = from;
        from += durations[i];
        return (
          <Sequence key={i} from={start} durationInFrames={durations[i]}>
            <Words scene={scene} index={i} duration={durations[i]} />
            {hasVoice ? <Audio src={staticFile(VOICE[i].file)} /> : null}
          </Sequence>
        );
      })}
      <Header total={total} />
    </AbsoluteFill>
  );
};
