// „Was wäre, wenn …“ – Low-Poly-POV-Simulation (1080×1920). Szene = Satz, Herzfrequenz-Anzeige, Untertitel mit roten Schlüsselwörtern.
import React from "react";
import { AbsoluteFill, Audio, Sequence, getInputProps, interpolate, staticFile, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import "@fontsource/libre-baskerville/400.css";
import "@fontsource/libre-baskerville/700.css";
import { World } from "./World";
import { FPS, SHOTS, TOTAL, shotAt } from "./timeline";

export const whatifFrames = () => TOTAL;
const W = 1080, H = 1920;
const SERIF = "'Libre Baskerville', Georgia, serif";
const SANS = "Inter, 'DejaVu Sans', sans-serif";
const RED = "#ff3b30";
const DPR = Number((getInputProps() as any).dpr ?? 1);

const Words: React.FC<{ text: string; words: { word: string; start: number }[]; t: number; size: number }> = ({ text, words, t, size }) => {
  const parts = text.split(/\s+/);
  return (
    <div style={{ fontFamily: SERIF, fontSize: size, lineHeight: 1.32, color: "#fff", textAlign: "center", textShadow: "0 3px 18px rgba(0,0,0,0.75), 0 1px 3px rgba(0,0,0,0.9)" }}>
      {parts.map((w, i) => {
        const st = words[i]?.start ?? 0;
        const on = interpolate(t, [st - 0.05, st + 0.18], [0.45, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
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

const Hud: React.FC<{ f: number }> = ({ f }) => {
  const sh = shotAt(f);
  const t = (f - sh.start) / FPS;
  const prev = SHOTS[Math.max(0, sh.i - 1)].hud[0];
  const bpmF = interpolate(t, [0, 1.4], [sh.i ? prev : sh.hud[0], sh.hud[0]], { extrapolateRight: "clamp" });
  const bpm = Math.round(bpmF + Math.sin(Math.floor(f / 12) * 1.7) * 1.2);
  // EKG-Linie: Ausschläge im Takt der Herzfrequenz
  const T = f / FPS;
  const per = 60 / bpmF;
  const pts: string[] = [];
  for (let x = 0; x <= 180; x += 2) {
    const tt = T - (180 - x) / 180 * 2.2;
    const ph = ((tt % per) + per) % per / per;
    let y = 0;
    if (ph < 0.06) y = -Math.sin((ph / 0.06) * Math.PI) * 4;
    else if (ph < 0.1) y = 6 * ((ph - 0.06) / 0.04);
    else if (ph < 0.14) y = 6 - 40 * ((ph - 0.1) / 0.04);
    else if (ph < 0.19) y = -34 + 44 * ((ph - 0.14) / 0.05);
    else if (ph < 0.23) y = 10 - 10 * ((ph - 0.19) / 0.04);
    else if (ph > 0.35 && ph < 0.5) y = -Math.sin(((ph - 0.35) / 0.15) * Math.PI) * 7;
    pts.push(`${x},${40 + y}`);
  }
  const beat = (((T % per) + per) % per) / per;
  const fade = interpolate(f, [SHOTS[0].start + 50, SHOTS[0].start + 70], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) * interpolate(f, [SHOTS[7].start, SHOTS[7].start + 15], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 70, top: 640, opacity: fade, color: "#fff", textShadow: "0 2px 12px rgba(0,0,0,0.7)" }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 21, letterSpacing: 5, opacity: 0.85 }}>HERZFREQUENZ</div>
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ fontFamily: SERIF, fontSize: 74, lineHeight: 1.1 }}>
          {bpm} <span style={{ fontSize: 50 }}>BPM</span>
        </div>
        <svg width={180} height={80} style={{ overflow: "visible", filter: "drop-shadow(0 0 6px rgba(255,59,48,0.6))" }}>
          <polyline points={pts.join(" ")} fill="none" stroke={RED} strokeWidth={3} strokeLinejoin="round" />
          <circle cx={180} cy={pts[pts.length - 1].split(",")[1]} r={5} fill="#fff" />
        </svg>
        <div style={{ fontSize: 34, color: RED, transform: `scale(${1 + Math.max(0, 1 - beat * 6) * 0.25})` }}>♥</div>
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 21, letterSpacing: 4, opacity: 0.75, marginTop: 4 }}>{sh.hud[1]}</div>
    </div>
  );
};

export const WhatIfVideo: React.FC = () => {
  const f = useCurrentFrame();
  const sh = shotAt(f);
  const t = (f - sh.start) / FPS;
  const first = sh.i === 0;
  const end = sh.shot === "end";
  // Wasser-Eintritt: weißer Blitz, dann türkis
  const crack = SHOTS[1];
  const tc = (f - crack.start) / FPS;
  const flash = sh.shot === "crack" ? interpolate(tc, [3.12, 3.22, 3.6], [0, 0.9, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  const underTint = sh.shot === "under" ? interpolate(t, [0, 0.5], [0.5, 0], { extrapolateRight: "clamp" }) : 0;
  const card = end ? interpolate(t, [0.2, 0.9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) : 0;
  const fadeIn = interpolate(f, [0, 10], [1, 0], { extrapolateRight: "clamp" });
  const fadeOut = interpolate(f, [TOTAL - 12, TOTAL - 1], [0, 1], { extrapolateLeft: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#05080e" }}>
      <ThreeCanvas width={W} height={H} dpr={DPR} camera={{ fov: 62, near: 0.02, far: 900 }} gl={{ toneMapping: THREE.NoToneMapping, antialias: true }}>
        <World frame={f} />
      </ThreeCanvas>

      {/* Vignette */}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)" }} />
      <AbsoluteFill style={{ background: "#fff", opacity: flash }} />
      <AbsoluteFill style={{ background: "#0b3a40", opacity: underTint }} />

      <Hud f={f} />

      {/* Titel oben (1. Szene) bzw. Untertitel */}
      {first ? (
        <div style={{ position: "absolute", left: 90, right: 90, top: 300 }}>
          <Words text={sh.text} words={sh.words.map((w) => ({ ...w, start: w.start }))} t={t - sh.delay} size={66} />
        </div>
      ) : !end ? (
        <div style={{ position: "absolute", left: 100, right: 100, top: 1180, opacity: interpolate(t, [0, 0.2], [0, 1], { extrapolateRight: "clamp" }) }}>
          <Words text={sh.text} words={sh.words} t={t - sh.delay} size={50} />
        </div>
      ) : null}

      {/* Schluss-Karte */}
      {end ? (
        <AbsoluteFill style={{ opacity: card, background: "linear-gradient(rgba(4,8,14,0.35), rgba(4,8,14,0.82) 45%, rgba(4,8,14,0.9))", alignItems: "center", justifyContent: "center", padding: "0 110px", textAlign: "center", color: "#fff" }}>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 22, letterSpacing: 6, opacity: 0.75 }}>DRAMATISIERUNG</div>
          <div style={{ fontFamily: SERIF, fontSize: 70, lineHeight: 1.15, marginTop: 18 }}>EINBRUCH IM EIS</div>
          <div style={{ width: 120, height: 3, background: RED, margin: "34px 0" }} />
          <div style={{ fontFamily: SERIF, fontSize: 36, lineHeight: 1.45, opacity: 0.92 }}>
            1-10-1-Regel: rund <b>1 Minute</b> Kälteschock, etwa <b>10 Minuten</b> Kraft in den Armen, bis zu <b>1 Stunde</b> bis zur Bewusstlosigkeit.
          </div>
          <div style={{ marginTop: 50, maxWidth: 820 }}>
            <Words text={sh.text} words={sh.words} t={t - sh.delay} size={46} />
          </div>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 22, letterSpacing: 6, opacity: 0.7, marginTop: 60 }}>● WAS WÄRE WENN</div>
        </AbsoluteFill>
      ) : null}

      <AbsoluteFill style={{ background: "#000", opacity: Math.max(fadeIn, fadeOut) }} />

      {/* Ton */}
      <Audio src={staticFile("whatif/sfx.mp3")} volume={0.5} />
      {SHOTS.map((s) => (
        <Sequence key={s.i} from={s.start + Math.round(s.delay * FPS)}>
          <Audio src={staticFile(s.file)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
