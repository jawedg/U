// Hochformat-Clip im Stil der großen Streamer-Clip-Kanäle:
// Facecam oben, Gameplay unten, harte Schnitte, Untertitel Wort für Wort (Anton, weiß/gelb, dicker schwarzer Rand).
import React from "react";
import { AbsoluteFill, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";
import "@fontsource/anton/400.css";

type Rect = { x: number; y: number; w: number; h: number };
export type ClipProps = {
  src: string;
  srcW: number;
  srcH: number;
  duration: number;
  segments: { from: number; to: number }[]; // Sekunden in der Quelldatei (Jump-Cuts)
  layout: { mode: "split" | "full" | "game"; cam?: Rect; focusX?: number };
  reactions: { from: number; to: number }[]; // Sekunden im fertigen Clip: Facecam groß
  captions: { from: number; to: number; text: string; yellow: boolean }[];
  tags: { from: number; to: number; text: string }[];
};

export const defaultClipProps: ClipProps = {
  src: "",
  srcW: 1920,
  srcH: 1080,
  duration: 10,
  segments: [{ from: 0, to: 10 }],
  layout: { mode: "game" },
  reactions: [],
  captions: [{ from: 0, to: 2, text: "VIRAL", yellow: true }],
  tags: [],
};

const W = 1080;
const H = 1920;
const SPLIT_CAM = 760; // Höhe Facecam-Feld im Normalfall
const REACT_CAM = 1180; // Höhe Facecam-Feld bei Reaktionen

// Ausschnitt `rect` (normiert) der Quelle so skalieren, dass er das Feld (fw×fh) füllt.
const Crop: React.FC<{
  src: string; srcW: number; srcH: number; rect: Rect; top: number; fh: number; trim: number; muted: boolean;
}> = ({ src, srcW, srcH, rect, top, fh, trim, muted }) => {
  const fw = W;
  const rw = rect.w * srcW;
  const rh = rect.h * srcH;
  const s = Math.max(fw / rw, fh / rh);
  const vw = srcW * s;
  const vh = srcH * s;
  let left = fw / 2 - (rect.x + rect.w / 2) * srcW * s;
  let tp = fh / 2 - (rect.y + rect.h / 2) * srcH * s;
  left = Math.min(0, Math.max(fw - vw, left));
  tp = Math.min(0, Math.max(fh - vh, tp));
  return (
    <div style={{ position: "absolute", left: 0, top, width: fw, height: fh, overflow: "hidden", background: "#000" }}>
      <OffthreadVideo
        src={src}
        trimBefore={trim}
        muted={muted}
        style={{ position: "absolute", left, top: tp, width: vw, height: vh, maxWidth: "none" }}
      />
    </div>
  );
};

const gameRect = (srcW: number, srcH: number, aspect: number): Rect => {
  // mittiger Ausschnitt in gewünschtem Seitenverhältnis (volle Höhe)
  const w = Math.min(1, (srcH * aspect) / srcW);
  return { x: 0.5 - w / 2, y: 0, w, h: 1 };
};

const Segment: React.FC<{ p: ClipProps; trim: number; offset: number }> = ({ p, trim, offset }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame + offset) / fps;
  const src = staticFile(p.src);
  const common = { src, srcW: p.srcW, srcH: p.srcH, trim };
  const { mode, cam, focusX = 0.5 } = p.layout;

  if (mode === "split" && cam) {
    const react = p.reactions.some((r) => t >= r.from && t < r.to);
    const ch = react ? REACT_CAM : SPLIT_CAM;
    const gh = H - ch;
    return (
      <AbsoluteFill style={{ background: "#000" }}>
        <Crop {...common} rect={cam} top={0} fh={ch} muted={false} />
        <Crop {...common} rect={gameRect(p.srcW, p.srcH, W / gh)} top={ch} fh={gh} muted />
      </AbsoluteFill>
    );
  }
  if (mode === "full") {
    const w = Math.min(1, (p.srcH * (W / H)) / p.srcW);
    const x = Math.min(1 - w, Math.max(0, focusX - w / 2));
    return (
      <AbsoluteFill style={{ background: "#000" }}>
        <Crop {...common} rect={{ x, y: 0, w, h: 1 }} top={0} fh={H} muted={false} />
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Crop {...common} rect={gameRect(p.srcW, p.srcH, W / H)} top={0} fh={H} muted={false} />
    </AbsoluteFill>
  );
};

const Caption: React.FC<{ text: string; yellow: boolean; y: number; local: number }> = ({ text, yellow, y, local }) => {
  const len = text.length;
  const size = Math.min(124, 1000 / Math.max(1, len * 0.5));
  const pop = interpolate(local, [0, 3], [0.82, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        width: W,
        top: y,
        transform: `translateY(-50%) scale(${pop})`,
        textAlign: "center",
        fontFamily: "Anton",
        fontSize: size,
        lineHeight: 1.05,
        letterSpacing: 1,
        color: yellow ? "#FFEE00" : "#FFFFFF",
        WebkitTextStroke: `${Math.round(size * 0.15)}px #000`,
        paintOrder: "stroke fill",
        textShadow: "0 5px 10px rgba(0,0,0,0.55)",
        padding: "0 40px",
      }}
    >
      {text}
    </div>
  );
};

export const ViralClip: React.FC<ClipProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  // Segmente hintereinander (harte Schnitte), Bildgrenzen kumuliert runden -> kein Versatz
  let acc = 0;
  const seqs = p.segments.map((s, i) => {
    const from = Math.round(acc * fps);
    acc += s.to - s.from;
    const to = Math.round(acc * fps);
    return { key: i, from, dur: Math.max(1, to - from), trim: Math.round(s.from * fps) };
  });

  const react = p.layout.mode === "split" && p.reactions.some((r) => t >= r.from && t < r.to);
  const capY = p.layout.mode === "split" ? (react ? 0.8 : 0.72) * H : 0.78 * H;
  const cap = p.captions.find((c) => t >= c.from && t < c.to);
  const tag = !cap ? p.tags.find((c) => t >= c.from && t < c.to) : undefined;
  const shown = cap ?? (tag ? { ...tag, yellow: false } : undefined);

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {seqs.map((s) => (
        <Sequence key={s.key} from={s.from} durationInFrames={s.dur} premountFor={15}>
          <Segment p={p} trim={s.trim} offset={s.from} />
        </Sequence>
      ))}
      {shown && <Caption text={shown.text} yellow={shown.yellow} y={capY} local={frame - Math.round(shown.from * fps)} />}
    </AbsoluteFill>
  );
};
