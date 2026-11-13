// Anime-Folge (Motion Comic) aus dem Charakterblatt des Nutzers: dunkler Psycho-Thriller-Look,
// Kamerafahrten, Regen, Blitz, Glitch, Handy-Nachrichten, rote Augen, Erzähler Charon. 1080×1920.
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame } from "remotion";
import "@fontsource/libre-baskerville/400.css";
import "@fontsource/libre-baskerville/700.css";
import { FPS, SHOTS, Shot, TOTAL, shotAt } from "./timeline";

export const animeFrames = () => TOTAL;
const W = 1080, H = 1920;
const SERIF = "'Libre Baskerville', Georgia, serif";
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const MONO = "'DejaVu Sans Mono', monospace";
const RED = "#e5202e";
const cl = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const hash = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
const IMG: Record<string, { src: string; w: number; h: number }> = {
  body: { src: "anime/body.jpg", w: 468, h: 2027 },
  face: { src: "anime/face.jpg", w: 1092, h: 1365 },
  side: { src: "anime/side.jpg", w: 1120, h: 852 },
  sit: { src: "anime/sit.jpg", w: 1120, h: 740 },
};
// Wort-Zeitpunkt (Sekunden ab Szenenbeginn) eines markierten Worts
const wordAt = (sh: Shot, needle: string) => {
  const i = sh.text.split(/\s+/).findIndex((w) => w.includes(needle));
  return sh.delay + (sh.words[i]?.start ?? 0);
};

// ---------- Bausteine ----------
const Grade: React.CSSProperties = { filter: "contrast(1.14) saturate(0.8) brightness(0.97)" };

// Bild mit unscharfem Hintergrund (füllt das Hochformat), Vordergrund passend in der Breite, weiche Kanten
const Panel: React.FC<{ k: string; scale: number; x?: number; y?: number; origin?: string; blurBg?: boolean; dim?: number; split?: number; fit?: "w" | "h" }> = ({ k, scale, x = 0, y = 0, origin = "50% 50%", blurBg = true, dim = 0, split = 0, fit = "w" }) => {
  const im = IMG[k];
  const fw = fit === "w" ? W : (H * im.w) / im.h;
  const fh = fit === "w" ? (W * im.h) / im.w : H;
  const fg = (filter?: string, dx = 0, blend?: React.CSSProperties["mixBlendMode"]) => (
    <Img
      src={staticFile(im.src)}
      style={{
        position: "absolute",
        left: (W - fw) / 2 + dx,
        top: (H - fh) / 2,
        width: fw,
        height: fh,
        filter,
        mixBlendMode: blend,
        WebkitMaskImage: fit === "w" ? "linear-gradient(transparent, #000 9%, #000 91%, transparent)" : "linear-gradient(90deg, transparent, #000 14%, #000 86%, transparent)",
      }}
    />
  );
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#0b0b0d" }}>
      {blurBg ? (
        <Img src={staticFile(im.src)} style={{ position: "absolute", left: -120, top: -120, width: W + 240, height: H + 240, objectFit: "cover", filter: "blur(38px) brightness(0.42) saturate(0.7)" }} />
      ) : null}
      <AbsoluteFill style={{ transform: `translate(${x}px, ${y}px) scale(${scale})`, transformOrigin: origin, ...Grade }}>
        {split > 0.5 ? (
          <AbsoluteFill style={{ background: "#000" }}>
            {fg("url(#onlyR)", split, "screen")}
            {fg("url(#onlyG)", 0, "screen")}
            {fg("url(#onlyB)", -split, "screen")}
          </AbsoluteFill>
        ) : (
          fg()
        )}
      </AbsoluteFill>
      {dim > 0 ? <AbsoluteFill style={{ background: "#000", opacity: dim }} /> : null}
    </AbsoluteFill>
  );
};

const Rain: React.FC<{ f: number; n?: number; op?: number }> = ({ f, n = 140, op = 0.28 }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
    {Array.from({ length: n }, (_, i) => {
      const sp = 55 + hash(i) * 45;
      const len = 50 + hash(i + 7) * 90;
      const x0 = hash(i + 3) * (W + 300) - 150;
      const y = ((hash(i + 11) * (H + 400) + f * sp) % (H + 400)) - 200;
      const x = x0 - y * 0.12;
      return <line key={i} x1={x} y1={y} x2={x - len * 0.12} y2={y + len} stroke="#c9d3e6" strokeOpacity={op * (0.4 + hash(i + 5) * 0.6)} strokeWidth={1 + hash(i + 9) * 1.6} />;
    })}
  </svg>
);

const Grain: React.FC<{ f: number }> = ({ f }) => (
  <AbsoluteFill style={{ backgroundImage: `url(${staticFile("anime/grain.png")})`, backgroundPosition: `${Math.floor(hash(f) * 512)}px ${Math.floor(hash(f + 99) * 512)}px`, mixBlendMode: "overlay", opacity: 0.22 }} />
);

// Glitch-Streifen: Bildteile verrutschen kurz
const Slices: React.FC<{ f: number; amt: number; k: string; scale: number; origin?: string }> = ({ f, amt, k, scale, origin }) => {
  if (amt <= 0.05) return null;
  return (
    <>
      {[0, 1, 2, 3, 4].map((i) => {
        const y0 = hash(f * 3 + i) * H;
        const hgt = 30 + hash(f * 5 + i) * 140;
        const dx = (hash(f * 7 + i) - 0.5) * 160 * amt;
        return (
          <AbsoluteFill key={i} style={{ clipPath: `inset(${y0}px 0 ${Math.max(0, H - y0 - hgt)}px 0)`, transform: `translateX(${dx}px)` }}>
            <Panel k={k} scale={scale} origin={origin} />
          </AbsoluteFill>
        );
      })}
    </>
  );
};

const Words: React.FC<{ sh: Shot; t: number; size?: number }> = ({ sh, t, size = 50 }) => {
  const parts = sh.text.split(/\s+/);
  return (
    <div style={{ fontFamily: SERIF, fontSize: size, lineHeight: 1.35, color: "#fff", textAlign: "center", textShadow: "0 3px 16px rgba(0,0,0,0.9), 0 1px 3px #000" }}>
      {parts.map((w, i) => {
        const st = sh.delay + (sh.words[i]?.start ?? 0);
        const on = interpolate(t, [st - 0.05, st + 0.15], [0.4, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const kw = w.includes("*");
        return (
          <span key={i} style={{ opacity: on, color: kw ? RED : "#fff" }}>
            {w.replace(/\*/g, "")}{" "}
          </span>
        );
      })}
    </div>
  );
};

const Notif: React.FC<{ f: number; at: number; title: string; body: React.ReactNode; top: number; thumb?: boolean }> = ({ f, at, title, body, top, thumb }) => {
  const s = spring({ frame: f - at, fps: FPS, config: { damping: 14, stiffness: 140 } });
  if (f < at) return null;
  const buzz = f - at < 10 ? Math.sin((f - at) * 2.6) * 7 * (1 - (f - at) / 10) : 0;
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top: top - 60 * (1 - s), opacity: s, transform: `translateX(${buzz}px)`, background: "rgba(22,22,26,0.86)", borderRadius: 38, padding: "28px 32px", boxShadow: "0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.08)", color: "#fff", fontFamily: SANS, display: "flex", gap: 24, alignItems: "center" }}>
      <div style={{ width: 84, height: 84, borderRadius: 20, background: "#2a2a30", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 44, color: RED, flexShrink: 0 }}>✉</div>
      <div style={{ flex: 1 }}>
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 30, fontWeight: 700 }}>
          <span>{title}</span>
          <span style={{ fontWeight: 500, opacity: 0.55 }}>03:17</span>
        </div>
        <div style={{ fontSize: 38, marginTop: 8, opacity: 0.95 }}>{body}</div>
      </div>
      {thumb ? <Img src={staticFile("anime/side.jpg")} style={{ width: 190, height: 145, objectFit: "cover", borderRadius: 16, filter: "brightness(0.8) saturate(0.6)" }} /> : null}
    </div>
  );
};

// ---------- Szenen ----------
const ShotView: React.FC<{ sh: Shot; f: number }> = ({ sh, f }) => {
  const t = (f - sh.start) / FPS;
  const p = (f - sh.start) / sh.dur;
  const glitchIn = (dur = 0.35) => cl(1 - t / dur);
  switch (sh.shot) {
    case "body": {
      const flick = t < 1.2 ? (hash(Math.floor(f / 2)) > 0.55 ? 0.55 : 0) : t < 1.4 ? 0.25 : 0;
      const light = interpolate(t, [0.25, 0.32, 0.6, 0.66, 0.8], [0, 0.85, 0.1, 0.5, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      return (
        <>
          <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 18%, #2a2c33 0%, #101115 45%, #060607 100%)" }} />
          <Panel k="body" fit="h" blurBg={false} scale={1.0 + p * 0.1} origin="50% 12%" y={-p * 40} dim={flick} />
          <AbsoluteFill style={{ background: "linear-gradient(transparent 60%, rgba(6,6,8,0.9))" }} />
          <Rain f={f} n={170} op={0.32} />
          <AbsoluteFill style={{ background: "#dfe6ff", opacity: light, mixBlendMode: "screen" }} />
          {/* Kapitel-Karte */}
          <div style={{ position: "absolute", top: 1120, left: 0, right: 0, textAlign: "center", color: "#fff", opacity: interpolate(t, [0.6, 1.1, sh.dur / FPS - 0.5, sh.dur / FPS - 0.1], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 14, opacity: 0.8 }}>KAPITEL 1</div>
            <div style={{ fontFamily: SERIF, fontSize: 86, marginTop: 14, textShadow: "0 4px 30px #000" }}>
              {"DIE NACHRICHT".slice(0, Math.max(0, Math.floor((t - 0.9) * 18)))}
            </div>
            <div style={{ width: interpolate(t, [1.2, 2], [0, 260], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }), height: 3, background: RED, margin: "26px auto 0" }} />
          </div>
        </>
      );
    }
    case "face":
      return <Panel k="face" scale={1.02 + p * 0.12} origin="57% 43%" />;
    case "sit":
      return <Panel k="sit" scale={1.08 + p * 0.14} x={interpolate(p, [0, 1], [30, -30])} origin="45% 35%" />;
    case "phone1":
    case "phone2": {
      const s1 = SHOTS.find((s) => s.shot === "phone1")!;
      const s2 = SHOTS.find((s) => s.shot === "phone2")!;
      const at1 = s1.start + Math.round(wordAt(s1, "Nachricht") * FPS) - 4;
      const at2 = s2.start + Math.round(wordAt(s2, "Foto") * FPS) - 4;
      const P = (f - s1.start) / (s1.dur + s2.dur);
      const glow = f >= at1 ? 0.55 + 0.1 * Math.sin(f * 0.3) : 0;
      return (
        <>
          <Panel k="sit" scale={1.25 + P * 0.15} origin="45% 32%" dim={0.35} />
          <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 30%, rgba(170,200,255,0.35), transparent 60%)", opacity: glow, mixBlendMode: "screen" }} />
          <Notif f={f} at={at1} title="Unbekannt" body="Du bist der Nächste." top={300} />
          <Notif f={f} at={at2} title="Unbekannt" body="📷 Foto" top={520} thumb />
        </>
      );
    }
    case "side": {
      const g = glitchIn(0.4);
      return (
        <>
          <Panel k="side" scale={1.05 + p * 0.08} x={interpolate(p, [0, 1], [-150, -110])} origin="70% 40%" split={g * 22} />
          <Slices f={f} amt={g} k="side" scale={1.05} origin="70% 40%" />
          <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(229,32,46,0.0) 40%, rgba(229,32,46,0.35))", mixBlendMode: "overlay" }} />
          {/* Sucher: Das Foto */}
          <div style={{ position: "absolute", left: 70, right: 70, top: 470, bottom: 470 }}>
            {[[0, 0], [1, 0], [0, 1], [1, 1]].map(([a, b], i) => (
              <div key={i} style={{ position: "absolute", [a ? "right" : "left"]: 0, [b ? "bottom" : "top"]: 0, width: 70, height: 70, borderLeft: a ? "none" : "4px solid #fff", borderRight: a ? "4px solid #fff" : "none", borderTop: b ? "none" : "4px solid #fff", borderBottom: b ? "4px solid #fff" : "none", opacity: 0.85 }} />
            ))}
            <div style={{ position: "absolute", left: 24, top: 18, fontFamily: MONO, fontSize: 30, color: "#fff", opacity: 0.9 }}>
              <span style={{ color: RED, opacity: Math.floor(f / 15) % 2 ? 1 : 0.2 }}>●</span> IMG_0315
            </div>
            <div style={{ position: "absolute", right: 24, bottom: 18, fontFamily: MONO, fontSize: 32, color: "#fff" }}>03:15:42</div>
          </div>
        </>
      );
    }
    case "face2": {
      const g = glitchIn(0.3);
      const eye = interpolate(t, [1.4, 2.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      const sc = 1.05 + Math.pow(p, 1.6) * 0.55;
      // Augen im Bild (Anteile der Gesichtsgrafik), umgerechnet auf den Bildschirm
      const fh = (W * 1365) / 1092;
      const o = { x: 0.57 * W, y: (H - fh) / 2 + 0.43 * fh };
      const eyes = [
        { x: 0.41 * W, y: (H - fh) / 2 + 0.43 * fh },
        { x: 0.727 * W, y: (H - fh) / 2 + 0.445 * fh },
      ].map((e) => ({ x: o.x + (e.x - o.x) * sc, y: o.y + (e.y - o.y) * sc }));
      return (
        <>
          <Panel k="face" scale={sc} origin="57% 43%" split={g * 18} />
          <AbsoluteFill style={{ background: "linear-gradient(100deg, rgba(229,32,46,0.55), rgba(0,0,0,0) 45%, rgba(0,0,0,0.5))", mixBlendMode: "multiply" }} />
          <AbsoluteFill style={{ background: "linear-gradient(100deg, rgba(229,32,46,0.4), transparent 50%)", mixBlendMode: "overlay" }} />
          {eyes.map((e, i) => (
            <React.Fragment key={i}>
              <div style={{ position: "absolute", left: e.x - 60 * sc, top: e.y - 30 * sc, width: 120 * sc, height: 60 * sc, borderRadius: "50%", background: `radial-gradient(ellipse, rgba(255,40,50,${0.85 * eye}) 0%, rgba(255,20,30,${0.35 * eye}) 35%, transparent 70%)`, mixBlendMode: "screen" }} />
              <div style={{ position: "absolute", left: e.x - 260 * eye, top: e.y - 2, width: 520 * eye, height: 4, background: `linear-gradient(90deg, transparent, rgba(255,80,80,${0.9 * eye}), transparent)`, mixBlendMode: "screen" }} />
            </React.Fragment>
          ))}
          <Slices f={f} amt={g} k="face" scale={sc} origin="57% 43%" />
        </>
      );
    }
    default: {
      const g = glitchIn(0.3);
      const a = interpolate(t, [0.2, 0.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      const b = interpolate(t, [sh.speech + sh.delay - 0.2, sh.speech + sh.delay + 0.5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      return (
        <AbsoluteFill style={{ background: "#050506", alignItems: "center", justifyContent: "center", color: "#fff", textAlign: "center" }}>
          <Panel k="face" scale={1.6} origin="57% 43%" dim={0.86} blurBg={false} />
          <div style={{ position: "absolute", top: 760, left: 0, right: 0, transform: `translateX(${(hash(f) - 0.5) * 40 * g}px)` }}>
            <div style={{ fontFamily: SERIF, fontSize: 64, letterSpacing: 4, opacity: a, textShadow: `${6 * g}px 0 ${RED}, ${-6 * g}px 0 #39f` }}>FORTSETZUNG FOLGT</div>
            <div style={{ width: 200 * a, height: 3, background: RED, margin: "28px auto" }} />
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: 8, opacity: b * 0.85 }}>FOLGE 2 → FOLGEN</div>
          </div>
        </AbsoluteFill>
      );
    }
  }
};

export const AnimeVideo: React.FC = () => {
  const f = useCurrentFrame();
  const sh = shotAt(f);
  const t = (f - sh.start) / FPS;
  // kurzer Blitz bei harten Schnitten
  const flash = ["face", "sit", "side", "face2"].includes(sh.shot) ? interpolate(t, [0, 0.03, 0.22], [0.0, sh.shot === "side" || sh.shot === "face2" ? 0.55 : 0.3, 0], { extrapolateRight: "clamp" }) : 0;
  const shake = sh.shot === "face2" && t > 1.4 ? (hash(f) - 0.5) * 6 : 0;
  const fade = Math.max(interpolate(f, [0, 12], [1, 0], { extrapolateRight: "clamp" }), interpolate(f, [TOTAL - 15, TOTAL - 1], [0, 1], { extrapolateLeft: "clamp" }));
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <svg width={0} height={0} style={{ position: "absolute" }}>
        <filter id="onlyR"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
        <filter id="onlyG"><feColorMatrix type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter>
        <filter id="onlyB"><feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" /></filter>
      </svg>
      <AbsoluteFill style={{ transform: `translate(${shake}px, ${shake * 0.6}px)` }}>
        <ShotView sh={sh} f={f} />
      </AbsoluteFill>
      {/* Vignette + Korn */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 50%, rgba(0,0,0,0.7) 100%)" }} />
      <Grain f={f} />
      <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
      {/* kleines Kapitel-Label */}
      {sh.i > 0 && sh.shot !== "end" ? (
        <div style={{ position: "absolute", top: 150, left: 70, fontFamily: SANS, fontWeight: 700, fontSize: 22, letterSpacing: 6, color: "#fff", opacity: 0.6 }}>
          KAPITEL 1 <span style={{ color: RED }}>/</span> DIE NACHRICHT
        </div>
      ) : null}
      {/* Untertitel */}
      <div style={{ position: "absolute", left: 90, right: 90, top: sh.shot === "end" ? 1080 : 1560 }}>
        <Words sh={sh} t={t} size={sh.shot === "end" ? 44 : 50} />
      </div>
      <AbsoluteFill style={{ background: "#000", opacity: fade }} />
      <Audio src={staticFile("anime/sfx.mp3")} volume={0.55} />
      {SHOTS.map((s) => (
        <Sequence key={s.i} from={s.start + Math.round(s.delay * FPS)}>
          <Audio src={staticFile(s.file)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
