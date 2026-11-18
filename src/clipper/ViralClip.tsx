// Hochformat-Clip im Stil der großen Streamer-Clip-Kanäle (Vorbild: streamer.clipss / kaicenatclips):
// - Facecam oben, Gameplay unten; bei Reaktionen Facecam groß (Punch-in), bei Action Gameplay voll
// - alle 1–3 s neue Einstellung (Zoomstufe wechselt, leichter Drift) -> nie statisch
// - Ansichtswechsel mit kurzer Zoom-Unschärfe
// - Untertitel Wort für Wort (Anton, dicker schwarzer Rand): Streamer weiß, andere Stimmen gelb
import React from "react";
import { AbsoluteFill, Easing, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import "@fontsource/anton/400.css";

type Rect = { x: number; y: number; w: number; h: number };
type View = "split" | "cam" | "game" | "full";
type Shot = { from: number; to: number; view: View; zoom: number; drift: number; punch?: boolean; whip?: boolean };
export type ClipProps = {
  src: string;
  srcW: number;
  srcH: number;
  cam?: { src: string; w: number; h: number; srcPx: number }; // separat hochskalierte Facecam
  duration: number;
  segments: { from: number; to: number }[]; // Sekunden in der Quelldatei (Jump-Cuts)
  layout: { mode: "split" | "full" | "game"; cam?: Rect; focusX?: number };
  shots: Shot[];
  captions: { from: number; to: number; text: string; who: "s" | "o"; big?: boolean }[];
  tags: { from: number; to: number; text: string; who?: "s" | "o" }[];
};

export const defaultClipProps: ClipProps = {
  src: "",
  srcW: 1920,
  srcH: 1080,
  duration: 10,
  segments: [{ from: 0, to: 10 }],
  layout: { mode: "game" },
  shots: [{ from: 0, to: 10, view: "game", zoom: 1, drift: 0.03 }],
  captions: [{ from: 0, to: 2, text: "VIRAL", who: "s" }],
  tags: [],
};

const W = 1080;
const H = 1920;
const CAM_H = 790; // Facecam-Feld im geteilten Bild
const BIG_CAM_H = 1260; // Facecam-Feld bei Reaktionen (wenn die Cam für Vollbild zu klein ist)
const YELLOW = "#FFE81A";

type Src = { src: string; w: number; h: number; trim: number };

// Ausschnitt `rect` (normiert) der Quelle mit Zusatz-Zoom so skalieren, dass er das Feld füllt.
const Crop: React.FC<{ s: Src; rect: Rect; top: number; fh: number; zoom: number; muted: boolean; fy?: number }> = ({
  s, rect, top, fh, zoom, muted, fy = 0.5,
}) => {
  const fw = W;
  const cx = rect.x + rect.w / 2;
  const cy = rect.y + rect.h * fy;
  const rw = (rect.w * s.w) / zoom;
  const rh = (rect.h * s.h) / zoom;
  const k = Math.max(fw / rw, fh / rh);
  const vw = s.w * k;
  const vh = s.h * k;
  let left = fw / 2 - cx * vw;
  let tp = fh / 2 - cy * vh;
  // nicht über den Rand des Ausschnitts hinaus (sonst sieht man Spiel neben der Cam)
  const minL = fw - (rect.x + rect.w) * vw;
  const maxL = -rect.x * vw;
  const minT = fh - (rect.y + rect.h) * vh;
  const maxT = -rect.y * vh;
  left = minL <= maxL ? Math.min(maxL, Math.max(minL, left)) : left;
  tp = minT <= maxT ? Math.min(maxT, Math.max(minT, tp)) : tp;
  return (
    <div style={{ position: "absolute", left: 0, top, width: fw, height: fh, overflow: "hidden", background: "#000" }}>
      <OffthreadVideo
        src={staticFile(s.src)}
        trimBefore={s.trim}
        muted={muted}
        style={{ position: "absolute", left, top: tp, width: vw, height: vh, maxWidth: "none" }}
      />
    </div>
  );
};

const centerRect = (s: Src, aspect: number): Rect => {
  const w = Math.min(1, (s.h * aspect) / s.w);
  return { x: 0.5 - w / 2, y: 0, w, h: 1 };
};

const shotAt = (shots: Shot[], t: number) => shots.find((s) => t >= s.from && t < s.to) ?? shots[shots.length - 1];

// Ansicht + Feldgrenzen (für Untertitel-Position)
const camFull = (p: ClipProps) => (p.cam?.srcPx ?? 0) >= 420;

const Frame: React.FC<{ p: ClipProps; trim: number; offset: number }> = ({ p, trim, offset }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = (frame + offset) / fps;
  const sh = shotAt(p.shots, t);
  const prog = Math.min(1, Math.max(0, (t - sh.from) / Math.max(0.1, sh.to - sh.from)));
  const local = (t - sh.from) * fps;
  // Punch-in: schneller Zoom rein bei Reaktionen
  const punch = sh.punch ? interpolate(local, [0, 7], [0.86, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }) : 1;
  const z = sh.zoom * punch * (1 + sh.drift * prog);
  const main: Src = { src: p.src, w: p.srcW, h: p.srcH, trim };
  const camSrc: Src | null = p.cam ? { src: p.cam.src, w: p.cam.w, h: p.cam.h, trim } : null;
  const camRect: Rect = camSrc ? { x: 0, y: 0, w: 1, h: 1 } : p.layout.cam ?? { x: 0, y: 0, w: 1, h: 1 };
  const cs = camSrc ?? main;
  const gz = 1 + (z - 1) * 0.45; // Gameplay zoomt etwas weniger mit

  let body: React.ReactNode;
  if (sh.view === "split" && p.layout.cam) {
    const gh = H - CAM_H;
    body = (
      <>
        <Crop s={cs} rect={camRect} top={0} fh={CAM_H} zoom={z} fy={0.45} muted={false} />
        <Crop s={main} rect={centerRect(main, W / gh)} top={CAM_H} fh={gh} zoom={gz} muted />
      </>
    );
  } else if (sh.view === "cam" && p.layout.cam) {
    if (camFull(p)) {
      body = <Crop s={cs} rect={camRect} top={0} fh={H} zoom={z} fy={0.42} muted={false} />;
    } else {
      body = (
        <>
          <Crop s={cs} rect={camRect} top={0} fh={BIG_CAM_H} zoom={z} fy={0.42} muted={false} />
          <Crop s={main} rect={centerRect(main, W / (H - BIG_CAM_H))} top={BIG_CAM_H} fh={H - BIG_CAM_H} zoom={1.05} muted />
        </>
      );
    }
  } else if (sh.view === "full") {
    const fx = p.layout.focusX ?? 0.5;
    const w = Math.min(1, (p.srcH * (W / H)) / p.srcW);
    const x = Math.min(1 - w, Math.max(0, fx - w / 2));
    body = <Crop s={main} rect={{ x, y: 0, w, h: 1 }} top={0} fh={H} zoom={z} fy={0.4} muted={false} />;
  } else {
    body = <Crop s={main} rect={centerRect(main, W / H)} top={0} fh={H} zoom={gz} muted={false} />;
  }

  // Zoom-Unschärfe beim Ansichtswechsel
  const wp = sh.whip ? interpolate(local, [0, 6], [1, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }) : 0;
  return (
    <AbsoluteFill style={{ background: "#000", transform: `scale(${1 + 0.22 * wp})`, filter: wp > 0.01 ? `blur(${14 * wp}px)` : undefined }}>
      {body}
    </AbsoluteFill>
  );
};

const Caption: React.FC<{ text: string; color: string; big?: boolean; y: number; local: number }> = ({ text, color, big, y, local }) => {
  const size = Math.min(big ? 138 : 120, 1000 / Math.max(1, text.length * 0.5));
  const pop = interpolate(local, [0, 3], [0.8, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.back(2)) });
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
        color,
        WebkitTextStroke: `${Math.round(size * 0.16)}px #000`,
        paintOrder: "stroke fill",
        textShadow: "0 6px 12px rgba(0,0,0,0.55)",
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

  // Jump-Cut-Segmente hintereinander, Bildgrenzen kumuliert runden -> kein Versatz
  let acc = 0;
  const seqs = p.segments.map((s, i) => {
    const from = Math.round(acc * fps);
    acc += s.to - s.from;
    const to = Math.round(acc * fps);
    return { key: i, from, dur: Math.max(1, to - from), trim: Math.round(s.from * fps) };
  });

  const cap = p.captions.find((c) => t >= c.from && t < c.to);
  const tag = !cap ? p.tags.find((c) => t >= c.from && t < c.to) : undefined;
  const shown = cap ?? (tag ? { ...tag, who: tag.who ?? "s", big: false } : undefined);

  let y = 0.76 * H;
  if (shown) {
    const sh = shotAt(p.shots, t);
    const other = shown.who === "o";
    if (sh.view === "split" && p.layout.cam) y = other ? 0.71 * H : CAM_H - 20;
    else if (sh.view === "cam" && p.layout.cam && !camFull(p)) y = other ? BIG_CAM_H + 120 : BIG_CAM_H - 120;
    else y = 0.78 * H;
  }

  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {seqs.map((s) => (
        <Sequence key={s.key} from={s.from} durationInFrames={s.dur} premountFor={15}>
          <Frame p={p} trim={s.trim} offset={s.from} />
        </Sequence>
      ))}
      {shown && (
        <Caption
          text={shown.text}
          color={shown.who === "o" ? YELLOW : "#FFFFFF"}
          big={shown.big}
          y={y}
          local={frame - Math.round(shown.from * fps)}
        />
      )}
    </AbsoluteFill>
  );
};
