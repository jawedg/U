import React from "react";
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from "remotion";

export type Word = { word: string; start: number };

// Ein großes Wort pro Moment (TikTok-Stil). *Wort* im Skript = Schlüsselwort (farbig).
export const Caption: React.FC<{ words: Word[]; accent?: string; top?: number }> = ({
  words,
  accent = "#ffc531",
  top = 120,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  let idx = -1;
  words.forEach((w, i) => {
    if (t >= w.start) idx = i;
  });
  if (idx < 0) return null;
  const w = words[idx];
  const key = w.word.includes("*");
  const clean = w.word.replace(/\*/g, "").replace(/[.,:!?]+$/, "");
  const label = clean.charAt(0).toUpperCase() + clean.slice(1);
  const pop = spring({ frame: frame - Math.round(w.start * fps), fps, config: { damping: 11, stiffness: 260 } });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top }}>
      <div
        style={{
          fontFamily: "Inter, 'DejaVu Sans', sans-serif",
          fontWeight: 800,
          fontSize: label.length > 14 ? 74 : 92,
          color: key ? accent : "white",
          transform: `scale(${0.75 + 0.25 * pop})`,
          textShadow: "0 0 6px rgba(0,0,0,0.9), 0 4px 14px rgba(0,0,0,0.75)",
          WebkitTextStroke: "2px rgba(0,0,0,0.35)",
          letterSpacing: 0.5,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
