// Prüfungssimulation AP T2 (Werkstatt-Look, volles Bild): Gestell, Dialog Prüfer ↔ Ich, Messgerät, Prüfprotokoll.
import "@fontsource/caveat/600.css";
import React from "react";
import { AbsoluteFill, Audio, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { DATA, Scene, Word, cueFn, durF, info, lead } from "../lern/LernVideo";
import { GH, GW, Gestell, GestellDefs, GState, PT } from "./Gestell";

const KB = 7;
const FPS = 25;
const INK = "#1f2933";
const MUTED = "#64748b";
const LINE = "#cbd5e1";
const ORANGE = "#f26b1d";
const GREEN = "#16a34a";
const BLUE = "#1d4ed8";
const SANS = "Inter, sans-serif";
const HAND = "Caveat, cursive";

const ramp = (t: number, a: number, b: number) => interpolate(t, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const sp = (t: number, at: number, d = 14, s = 150) => (at > 900 ? 0 : spring({ frame: Math.round((t - at) * FPS), fps: FPS, config: { damping: d, stiffness: s } }));
type Cue = (c?: string) => number;
const at0 = (cue: Cue, c: string | number) => (typeof c === "number" ? c : cue(c) || 999);
// letzter Eintrag, dessen Cue erreicht ist
const lastOf = <T,>(arr: [string | number, ...any[]][] | undefined, t: number, cue: Cue): { item: any[] | null; at: number; idx: number } => {
  let r: any[] | null = null, a = -1, idx = -1;
  (arr ?? []).forEach((x, i) => {
    const c = at0(cue, x[0]);
    if (t >= c) { r = x; a = c; idx = i; }
  });
  return { item: r, at: a, idx };
};

// ------------------------------------------------------------------ Gestell-Ansicht mit Kamera
const GestellView: React.FC<{ w: number; h: number; cam?: [number, number, number]; t: number; st?: GState; hl?: string[]; hlA?: number; children?: (tf: (p: [number, number]) => [number, number]) => React.ReactNode }> = ({
  w, h, cam, t, st, hl, hlA, children,
}) => {
  const base = Math.min((w - 40) / GW, (h - 20) / GH);
  const [cx, cy, s0] = cam ?? [GW / 2, GH / 2, 1];
  const zin = ramp(t, 0, 1.6);
  const ease = 1 - Math.pow(1 - zin, 3);
  const s = base * (s0 * (0.88 + 0.12 * ease) + 0.012 * t * 0.15);
  const ccx = GW / 2 + (cx - GW / 2) * ease, ccy = GH / 2 + (cy - GH / 2) * ease;
  const tx = w / 2 - ccx * s, ty = h / 2 - ccy * s;
  const tf = (p: [number, number]): [number, number] => [tx + p[0] * s, ty + p[1] * s];
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: "hidden", borderRadius: 18 }}>
      <GestellDefs />
      <g transform={`translate(${tx} ${ty}) scale(${s})`}>
        <Gestell st={st} t={t} hl={hl} hlA={hlA} />
      </g>
      {children ? children(tf) : null}
    </svg>
  );
};

// ------------------------------------------------------------------ Messgerät
const MODES = ["R LOW", "R ISO 500 V", "RCD 10 mA", "DREHFELD"];
const Tester: React.FC<{ mode: string; value: string; measuring: boolean; ok: number; limit?: string; t: number }> = ({ mode, value, measuring, ok, limit, t }) => {
  const mi = Math.max(0, MODES.findIndex((m) => mode.startsWith(m.split(" ")[0]) && (m === mode || mode.includes(m.split(" ")[1] ?? ""))));
  const ang = -60 + mi * 40;
  const flick = measuring ? ["8.88", "- - -", "88.8", "- -"][Math.floor(t * 12) % 4] : value;
  return (
    <div style={{ width: 520, position: "relative" }}>
      <div style={{ background: "linear-gradient(180deg,#334155,#1e293b)", borderRadius: 36, padding: 30, boxShadow: "0 30px 60px rgba(15,23,42,0.35)", border: "6px solid #f59e0b" }}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, color: "#fbbf24", letterSpacing: 3, marginBottom: 14 }}>INSTALLATIONSTESTER</div>
        <div style={{ background: "#c7dccb", borderRadius: 14, padding: "18px 24px", boxShadow: "inset 0 4px 10px rgba(0,0,0,0.25)" }}>
          <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 700, fontSize: 26, color: "#1f3a2a" }}>{mode}</div>
          <div style={{ fontFamily: "'JetBrains Mono', monospace", fontWeight: 800, fontSize: 64, color: "#0f2318", textAlign: "right", minHeight: 80 }}>{flick}</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 26, marginTop: 24 }}>
          <svg width={170} height={170} viewBox="0 0 170 170">
            <circle cx={85} cy={85} r={62} fill="#0f172a" stroke="#475569" strokeWidth={4} />
            <g transform={`rotate(${ang} 85 85)`}>
              <rect x={78} y={30} width={14} height={60} rx={6} fill="#f59e0b" />
            </g>
            <circle cx={85} cy={85} r={18} fill="#1e293b" />
          </svg>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {MODES.map((m, i) => (
              <div key={m} style={{ fontFamily: SANS, fontWeight: 700, fontSize: 22, color: i === mi ? "#fbbf24" : "#94a3b8" }}>{i === mi ? "▶ " : "   "}{m}</div>
            ))}
          </div>
        </div>
      </div>
      {limit ? (
        <div style={{ marginTop: 24, display: "flex", alignItems: "center", gap: 18, background: "#fff", borderRadius: 18, padding: "16px 24px", boxShadow: "0 10px 30px rgba(15,23,42,0.12)" }}>
          <div style={{ fontFamily: SANS, fontSize: 26, color: MUTED }}>Grenzwert:</div>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 28, color: INK, whiteSpace: "nowrap" }}>{limit}</div>
          <div style={{ marginLeft: "auto", opacity: ok, transform: `scale(${0.6 + 0.4 * ok})`, fontFamily: SANS, fontWeight: 900, fontSize: 30, color: "#fff", background: GREEN, borderRadius: 30, padding: "6px 22px" }}>OK ✓</div>
        </div>
      ) : null}
    </div>
  );
};

const Probe: React.FC<{ from: [number, number]; to: [number, number]; color: string }> = ({ from, to, color }) => (
  <g>
    <path d={`M${from[0]} ${from[1]} C${from[0] - 120} ${from[1] + 260} ${to[0] + 160} ${to[1] + 220} ${to[0] + 10} ${to[1] + 46}`} fill="none" stroke={color} strokeWidth={7} strokeLinecap="round" />
    <g transform={`translate(${to[0]} ${to[1]}) rotate(-20)`}>
      <rect x={-8} y={10} width={16} height={46} rx={6} fill={color} stroke="#0f172a" strokeWidth={2} />
      <path d="M-3 10 L0 -6 L3 10 Z" fill="#cbd5e1" stroke="#0f172a" strokeWidth={1.5} />
    </g>
    <circle cx={to[0]} cy={to[1]} r={9} fill="none" stroke={color} strokeWidth={3} opacity={0.8} />
  </g>
);

// ------------------------------------------------------------------ Protokoll
const BES = ["Schaltungsunterlagen komplett", "Betriebsmittel", "Leitungsanschlüsse", "Leitungswahl und Verlegung", "PE- und N-Leiter", "Schutz gegen direktes Berühren", "Überstromschutzeinrichtungen", "Keine erkennbaren Mängel"];
const ISO = [["X1:1", "X1:3"], ["X1:1", "X1:5"], ["X1:1", "X1:7"], ["X1:1", "X1:9"], ["X1:3", "X1:5"], ["X1:3", "X1:7"], ["X1:3", "X1:9"], ["X1:5", "X1:7"], ["X1:5", "X1:9"], ["X1:7", "X1:9"]];
export type Fill = { key: string; val: string; at: number };
const Box: React.FC<{ on: number }> = ({ on }) => (
  <span style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 26, height: 26, border: `2px solid ${INK}`, marginRight: 6, verticalAlign: "middle", background: "#fff" }}>
    <span style={{ fontFamily: HAND, fontWeight: 700, fontSize: 34, color: BLUE, opacity: on, transform: `scale(${0.4 + 0.6 * on}) translateY(-3px)` }}>✗</span>
  </span>
);
export const Protocol: React.FC<{ fills: Fill[]; t: number; isoVals?: string[] }> = ({ fills, t, isoVals }) => {
  const get = (k: string) => fills.find((f) => f.key === k);
  const prog = (k: string, delay = 0) => {
    const f = get(k);
    return f ? ramp(t, f.at + delay, f.at + delay + 0.35) : 0;
  };
  const active = (k: string) => {
    const f = get(k);
    return f && t >= f.at && t < f.at + 2.5 ? 1 : 0;
  };
  const Row: React.FC<{ label: string; k: string; delay?: number; val?: string }> = ({ label, k, delay = 0, val }) => (
    <div style={{ display: "flex", alignItems: "center", padding: "7px 10px", borderBottom: `1px solid ${LINE}`, background: active(k) ? "rgba(242,107,29,0.10)" : "transparent", borderRadius: 6 }}>
      <div style={{ flex: 1, fontFamily: SANS, fontSize: 21, color: INK }}>{label}</div>
      {val !== undefined ? <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 34, color: BLUE, width: 150, opacity: prog(k, delay) }}>{val}</div> : null}
      <Box on={prog(k, delay)} /><span style={{ fontFamily: SANS, fontSize: 19, marginRight: 14 }}>OK</span>
      <Box on={0} /><span style={{ fontFamily: SANS, fontSize: 19 }}>nicht OK</span>
    </div>
  );
  const pe = get("pe"), iso = get("iso"), ta = get("ta");
  return (
    <div style={{ display: "flex", gap: 30, padding: "0 70px", height: "100%", alignItems: "flex-start" }}>
      <div style={{ flex: 1, background: "#fff", borderRadius: 10, padding: "22px 26px", boxShadow: "0 20px 50px rgba(15,23,42,0.15)" }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 26, color: INK }}>Prüfprotokoll nach DIN VDE 0100-600</div>
        <div style={{ fontFamily: SANS, fontSize: 19, color: MUTED, marginBottom: 10 }}>Anlage: <span style={{ fontFamily: HAND, fontSize: 30, color: BLUE }}>Blechbearbeitungsmaschine</span></div>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, color: INK, margin: "6px 0" }}>Besichtigung</div>
        {BES.map((b, i) => <Row key={b} label={b} k="bes" delay={i * 0.25} />)}
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, color: INK, margin: "14px 0 6px" }}>Messen/Prüfen</div>
        <Row label="Durchgängigkeit des Schutzleiters" k="pe" val={pe?.val ?? ""} />
      </div>
      <div style={{ flex: 1, background: "#fff", borderRadius: 10, padding: "22px 26px", boxShadow: "0 20px 50px rgba(15,23,42,0.15)" }}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, color: INK, marginBottom: 8 }}>Isolationsmessung</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "4px 24px", background: active("iso") ? "rgba(242,107,29,0.10)" : "transparent", borderRadius: 6, padding: 4 }}>
          {ISO.map(([a, b], i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", borderBottom: `1px solid ${LINE}`, padding: "2px 0" }}>
              <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 18, width: 160, color: INK }}>-{a} / -{b}</div>
              <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 28, color: BLUE, opacity: iso ? ramp(t, iso.at + i * 0.18, iso.at + i * 0.18 + 0.3) : 0 }}>{isoVals?.[i] ?? iso?.val}</div>
            </div>
          ))}
        </div>
        <div style={{ marginTop: 8 }}>
          <Row label="RCD – Berührungsspannung" k="rcd" />
          <Row label="Auslösezeit (RCD)" k="ta" val={ta?.val ?? ""} />
          <Row label="Drehfeld (Rechtsdrehfeld)" k="dreh" />
        </div>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, color: INK, margin: "12px 0 6px" }}>Erprobung</div>
        <Row label="Funktion der Anlage" k="funk" />
        <Row label="Funktion RCD (Prüftaste)" k="rcdt" />
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 12, padding: "8px 10px", background: active("frei") ? "rgba(242,107,29,0.10)" : "transparent", borderRadius: 6 }}>
          <Box on={prog("frei")} />
          <span style={{ fontFamily: SANS, fontSize: 20, color: INK }}>Anlage entspricht den anerkannten Regeln der Elektrotechnik, mängelfrei</span>
        </div>
        <div style={{ fontFamily: HAND, fontSize: 40, color: BLUE, opacity: prog("frei", 1), marginTop: 4, marginLeft: 20 }}>Unterschrift Prüfling ✍</div>
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ Dialog-Bausteine
const Avatar: React.FC<{ who: string; size?: number }> = ({ who, size = 86 }) => (
  <div style={{ width: size, height: size, borderRadius: size, background: who === "pruefer" ? "#475569" : ORANGE, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, boxShadow: "0 8px 20px rgba(15,23,42,0.2)" }}>
    <svg width={size * 0.62} height={size * 0.62} viewBox="0 0 60 60">
      {who === "pruefer" ? (
        <g fill="none" stroke="#fff" strokeWidth={4} strokeLinejoin="round">
          <rect x={14} y={10} width={32} height={42} rx={4} />
          <rect x={22} y={6} width={16} height={9} rx={2} fill="#fff" />
          <path d="M20 26 h20 M20 34 h20 M20 42 h12" />
        </g>
      ) : (
        <g fill="#fff">
          <path d="M8 40 Q8 16 30 14 Q52 16 52 40 Z" />
          <rect x={4} y={40} width={52} height={7} rx={3} />
          <rect x={27} y={8} width={6} height={12} rx={2} />
        </g>
      )}
    </svg>
  </div>
);

export const SpokenWords: React.FC<{ words: Word[]; t: number; size: number; color: string; key2: string }> = ({ words, t, size, color, key2 }) => (
  <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: size, lineHeight: 1.38 }}>
    {words.map((w, i) => {
      const k = w.word.includes("*");
      return (
        <span key={i} style={{ color: k ? key2 : color, fontWeight: k ? 800 : 600, opacity: t >= w.start - 0.05 ? 1 : 0.28 }}>{w.word.replace(/\*/g, "")} </span>
      );
    })}
  </div>
);

const Bubble: React.FC<{ who: string; words: Word[]; t: number }> = ({ who, words, t }) => {
  const p = sp(t, 0);
  const pr = who === "pruefer";
  return (
    <div style={{ display: "flex", gap: 24, alignItems: "flex-start", opacity: p, transform: `translateY(${(1 - p) * 40}px)` }}>
      <Avatar who={who} />
      <div style={{ flex: 1 }}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, color: pr ? "#475569" : ORANGE, marginBottom: 10 }}>{pr ? "Prüfer" : "Ich (Prüfling)"}</div>
        <div style={{ background: pr ? "#fff" : "#fff3eb", border: `3px solid ${pr ? "#cbd5e1" : "#fdba74"}`, borderRadius: "6px 28px 28px 28px", padding: "26px 32px", boxShadow: "0 16px 40px rgba(15,23,42,0.12)" }}>
          <SpokenWords words={words} t={t} size={36} color={INK} key2={pr ? "#334155" : ORANGE} />
        </div>
      </div>
    </div>
  );
};

// Diagramme für das Fachgespräch
const Diagram: React.FC<{ kind: string; t: number }> = ({ kind, t }) => {
  const d = ramp(t, 0.3, 3.5);
  if (kind === "flanke") {
    const edges = [0.18, 0.5, 0.82];
    return (
      <svg width={820} height={560} viewBox="0 0 820 560">
        <text x={20} y={40} fontFamily={SANS} fontWeight={800} fontSize={28} fill={INK}>Signal B10 (Klappe zu)</text>
        <path d={`M40 180 ${edges.map((e) => `H${40 + e * 740} V90 H${40 + (e + 0.2) * 740} V180`).join(" ")} H780`} fill="none" stroke={BLUE} strokeWidth={6} strokeDasharray={3000} strokeDashoffset={3000 * (1 - d)} />
        <text x={20} y={260} fontFamily={SANS} fontWeight={800} fontSize={28} fill={INK}>Positive Flanke (0 → 1)</text>
        {edges.map((e, i) => (
          <g key={i} opacity={ramp(t, 0.6 + i * 0.9, 0.9 + i * 0.9)}>
            <line x1={40 + e * 740} x2={40 + e * 740} y1={360} y2={290} stroke={ORANGE} strokeWidth={6} />
            <path d={`M${30 + e * 740} 302 L${40 + e * 740} 286 L${50 + e * 740} 302`} fill={ORANGE} />
          </g>
        ))}
        <text x={20} y={430} fontFamily={SANS} fontWeight={800} fontSize={28} fill={INK}>Zählerstand CV</text>
        {[0, 1, 2, 3].map((n, i) => (
          <g key={n} opacity={i === 0 ? 1 : ramp(t, 0.6 + (i - 1) * 0.9, 0.9 + (i - 1) * 0.9)}>
            <text x={(i === 0 ? 0.05 : edges[i - 1] + 0.05) * 740 + 40} y={500} fontFamily="'JetBrains Mono', monospace" fontWeight={800} fontSize={44} fill={i === 3 ? ORANGE : INK}>{n}</text>
          </g>
        ))}
        <text x={40 + edges[2] * 740 + 70} y={500} fontFamily={SANS} fontWeight={800} fontSize={30} fill={ORANGE} opacity={ramp(t, 2.6, 3)}>= PV → voll!</text>
      </svg>
    );
  }
  if (kind === "verriegelung") {
    const branch = (x: number, coil: string, nc: string, hlS: number) => (
      <g>
        <line x1={x} x2={x} y1={60} y2={140} stroke={INK} strokeWidth={4} />
        <text x={x + 26} y={110} fontFamily={SANS} fontSize={26} fill={INK}>SPS-Ausgang</text>
        <line x1={x} x2={x} y1={140} y2={220} stroke={INK} strokeWidth={4} />
        <g opacity={0.4 + 0.6 * hlS}>
          <line x1={x} x2={x} y1={220} y2={246} stroke={ORANGE} strokeWidth={5} />
          <line x1={x - 22} x2={x + 6} y1={252} y2={290} stroke={ORANGE} strokeWidth={5} />
          <line x1={x - 22} x2={x + 8} y1={262} y2={262} stroke={ORANGE} strokeWidth={4} />
          <line x1={x} x2={x} y1={290} y2={316} stroke={ORANGE} strokeWidth={5} />
          <text x={x + 30} y={276} fontFamily={SANS} fontWeight={800} fontSize={28} fill={ORANGE}>{nc} (Öffner)</text>
        </g>
        <line x1={x} x2={x} y1={316} y2={380} stroke={INK} strokeWidth={4} />
        <rect x={x - 36} y={380} width={72} height={52} fill="#fff" stroke={INK} strokeWidth={4} />
        <text x={x} y={416} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={26} fill={INK}>{coil}</text>
        <line x1={x} x2={x} y1={432} y2={500} stroke={INK} strokeWidth={4} />
      </g>
    );
    return (
      <svg width={820} height={560} viewBox="0 0 820 560">
        <line x1={60} x2={760} y1={60} y2={60} stroke={INK} strokeWidth={4} />
        <line x1={60} x2={760} y1={500} y2={500} stroke={INK} strokeWidth={4} />
        <text x={20} y={46} fontFamily={SANS} fontSize={24} fill={MUTED}>24 V</text>
        <text x={20} y={540} fontFamily={SANS} fontSize={24} fill={MUTED}>0 V</text>
        {branch(220, "Q1", "Q2", ramp(t, 1.5, 2.2))}
        {branch(580, "Q2", "Q1", ramp(t, 2.5, 3.2))}
      </svg>
    );
  }
  // Typenschild
  const rows: [string, string, boolean][] = [["3 ~ Mot", "M1 Haspel", false], ["400 V Δ", "50 Hz", false], ["3,25 A", "", true], ["1,5 kW", "", false]];
  return (
    <div style={{ width: 640, background: "#e5e7eb", border: `5px solid ${INK}`, borderRadius: 16, padding: 30, boxShadow: "0 20px 40px rgba(15,23,42,0.2)" }}>
      <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 30, color: INK, marginBottom: 16 }}>Leistungsschild -M1</div>
      {rows.map(([a, b, hl], i) => (
        <div key={i} style={{ display: "flex", justifyContent: "space-between", fontFamily: "'JetBrains Mono', monospace", fontWeight: 800, fontSize: 40, padding: "10px 16px", margin: "6px 0", borderRadius: 10,
          color: hl ? "#fff" : INK, background: hl ? `rgba(242,107,29,${ramp(t, 0.8, 1.4)})` : "transparent", opacity: ramp(t, 0.1 + i * 0.2, 0.4 + i * 0.2) }}>
          <span>{a}</span><span>{b}</span>
        </div>
      ))}
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 28, color: ORANGE, marginTop: 14, opacity: ramp(t, 1.4, 2) }}>→ F4 auf 3,25 A einstellen</div>
    </div>
  );
};

const ItemList: React.FC<{ items: { text: string; cue: string }[]; t: number; cue: Cue; check?: boolean; size?: number; num?: boolean }> = ({ items, t, cue, check, size = 36, num }) => {
  const cs = items.map((it) => at0(cue, it.cue));
  return (
    <div>
      {items.map((it, i) => {
        const p = sp(t, cs[i]);
        const cur = t >= cs[i] && (i === items.length - 1 || t < cs[i + 1]);
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 20, margin: "12px 0", padding: "12px 20px", borderRadius: 14, opacity: Math.min(1, p * 1.4), transform: `translateX(${(1 - p) * -60}px)`,
            background: cur ? "#fff" : "rgba(255,255,255,0.55)", boxShadow: cur ? "0 10px 26px rgba(15,23,42,0.12)" : "none", borderLeft: `6px solid ${cur ? ORANGE : "transparent"}` }}>
            <div style={{ width: 44, height: 44, borderRadius: 10, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 900, fontSize: 26,
              background: check ? (p > 0.5 ? GREEN : LINE) : ORANGE, color: "#fff" }}>{check ? "✓" : num ? i + 1 : "•"}</div>
            <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: size, color: INK }}>{it.text}</div>
          </div>
        );
      })}
    </div>
  );
};

// ------------------------------------------------------------------ Szene
const Phases: React.FC<{ cur: number; topics: string[] }> = ({ cur, topics }) => (
  <div style={{ position: "absolute", top: 26, right: 50, display: "flex", gap: 10 }}>
    {topics.map((x, i) => {
      const n = i + 1, on = n === cur, done = n < cur;
      return (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 14px", borderRadius: 30, fontFamily: SANS, fontSize: 18, fontWeight: on ? 800 : 600,
          background: on ? ORANGE : done ? "#dcfce7" : "rgba(255,255,255,0.7)", color: on ? "#fff" : done ? GREEN : MUTED }}>
          {done ? "✓" : n} {on ? x : ""}
        </div>
      );
    })}
  </div>
);

export const Sub: React.FC<{ words: Word[]; t: number }> = ({ words, t }) => {
  if (!words.length || t < words[0].start - 0.1) return null;
  const sents: Word[][] = [[]];
  words.forEach((w) => {
    sents[sents.length - 1].push(w);
    if (/[.!?]$/.test(w.word.replace(/\*/g, "")) || (sents[sents.length - 1].length > 20 && /[,:]$/.test(w.word))) sents.push([]);
  });
  const cur = sents.filter((x) => x.length).reduce((acc, x) => (t >= x[0].start - 0.1 ? x : acc), sents[0]);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 26, display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth: 1600, background: "rgba(15,23,42,0.86)", borderRadius: 18, padding: "14px 30px", textAlign: "center" }}>
        <SpokenWords words={cur} t={t} size={34} color="#f8fafc" key2="#fdba74" />
      </div>
    </div>
  );
};

const PruefScene: React.FC<{ i: number; dur: number; fills: Fill[] }> = ({ i, dur, fills }) => {
  const frame = useCurrentFrame();
  const { s } = DATA[KB];
  const sc = s.sentences[i] as Scene & { who: string };
  const v = sc.v;
  const ln = info(KB, i);
  const t = frame / FPS;
  const cue = cueFn(ln.words);
  const enter = ramp(t, 0, 0.4);
  const hlFrom = (arr?: [string, ...string[]][]) => {
    const r = lastOf(arr as any, t, cue);
    return { ids: r.item ? (r.item.slice(1) as string[]) : [], a: r.item ? ramp(t, r.at, r.at + 0.3) : 0 };
  };
  const states = lastOf(v.states, t, cue).item?.[1] ?? (v.states ? {} : { P1: 0 });
  let body: React.ReactNode = null;
  let sub = true;

  if (v.type === "title") {
    body = (
      <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 80px", gap: 40 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 28, color: ORANGE, letterSpacing: 4, opacity: sp(t, 0) }}>ABSCHLUSSPRÜFUNG TEIL 2</div>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 104, color: INK, lineHeight: 1, letterSpacing: -3, margin: "16px 0", opacity: sp(t, 0.2) }}>Prüfungs­simulation</div>
          <div style={{ fontFamily: SANS, fontSize: 34, color: MUTED, opacity: sp(t, 0.5) }}>Elektroniker/-in für Betriebstechnik · Winter 2026/27</div>
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, color: INK, marginTop: 10, opacity: sp(t, 0.7) }}>Blechbearbeitungsmaschine · S7 · VDE 0100-600</div>
          <div style={{ display: "flex", gap: 16, marginTop: 40, opacity: sp(t, 1) }}>
            {[["pruefer", "Prüfer"], ["ich", "Ich (Prüfling)"]].map(([w, l]) => (
              <div key={w} style={{ display: "flex", alignItems: "center", gap: 14, background: "#fff", borderRadius: 60, padding: "10px 26px 10px 10px", boxShadow: "0 8px 20px rgba(15,23,42,0.1)" }}>
                <Avatar who={w} size={60} /><span style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, color: INK }}>{l}</span>
              </div>
            ))}
          </div>
        </div>
        <div style={{ opacity: sp(t, 0.3), transform: `translateX(${(1 - sp(t, 0.3)) * 120}px)` }}>
          <GestellView w={860} h={760} t={t} cam={[GW / 2, GH / 2, 1]} st={{ P1: 1 }} />
        </div>
      </div>
    );
  } else if (v.type === "phase") {
    body = (
      <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 120px" }}>
        <div>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 220, color: ORANGE, lineHeight: 0.9, opacity: sp(t, 0), transform: `translateY(${(1 - sp(t, 0)) * 60}px)` }}>{String(sc.topic).padStart(2, "0")}</div>
          <div style={{ width: 600 * ramp(t, 0.2, 0.8), height: 8, background: ORANGE, borderRadius: 4, margin: "24px 0" }} />
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 100, color: INK, letterSpacing: -2, opacity: sp(t, 0.25) }}>{sc.tname}</div>
        </div>
      </div>
    );
  } else if (v.type === "board") {
    const h = hlFrom(v.hl);
    body = (
      <div style={{ display: "flex", justifyContent: "center" }}>
        <GestellView w={1760} h={800} t={t} cam={v.cam} st={states} hl={h.ids} hlA={h.a} />
      </div>
    );
  } else if (v.type === "talk") {
    sub = false;
    const h = hlFrom(v.focus);
    const left = v.diagram ? <Diagram kind={v.diagram} t={t} /> : v.steps ? <div style={{ width: 760 }}><ItemList items={v.steps} t={t} cue={cue} num size={40} /></div>
      : <GestellView w={820} h={760} t={t} cam={h.ids.length ? undefined : undefined} st={{ P1: 1 }} hl={h.ids} hlA={h.a} />;
    body = (
      <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 60px", gap: 50 }}>
        <div style={{ width: 840, display: "flex", justifyContent: "center", opacity: 0.4 + 0.6 * enter }}>{left}</div>
        <div style={{ flex: 1 }}><Bubble who={sc.who} words={ln.words} t={t} /></div>
      </div>
    );
  } else if (v.type === "measure") {
    const pr = lastOf(v.probes, t, cue);
    const prevPr = pr.idx > 0 ? (v.probes[pr.idx - 1] as any[]) : pr.item;
    const mv = pr.item ? ramp(t, pr.at, pr.at + 0.5) : 0;
    const val = lastOf(v.vals, t, cue);
    const measuring = val.item ? t < val.at + 0.7 : false;
    const okA = v.ok ? ramp(t, at0(cue, v.ok), at0(cue, v.ok) + 0.3) : 0;
    const trip = v.trip ? t >= at0(cue, v.trip) + 0.7 : false;
    body = (
      <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 40px 0 30px", gap: 40 }}>
        <GestellView w={1180} h={800} t={t} cam={v.cam} st={{ ...(trip ? { F3trip: 1 } : {}), ...(v.mode.startsWith("R ") ? { T1off: v.mode.includes("ISO") ? 1 : 0 } : {}) }}>
          {(tf) => {
            if (!pr.item) return null;
            const lerp = (a: string, b: string): [number, number] => {
              const A = tf(PT[a] ?? PT.NULL), B = tf(PT[b] ?? PT.NULL);
              return [A[0] + (B[0] - A[0]) * mv, A[1] + (B[1] - A[1]) * mv];
            };
            const red = lerp(prevPr?.[1] ?? pr.item[1], pr.item[1]);
            const blk = lerp(prevPr?.[2] ?? pr.item[2], pr.item[2]);
            const same = pr.item[1] === pr.item[2];
            return (
              <g>
                {same ? <Probe from={[1180, 300]} to={red} color="#111827" /> : (
                  <>
                    <Probe from={[1180, 260]} to={blk} color="#111827" />
                    <Probe from={[1180, 340]} to={red} color="#dc2626" />
                  </>
                )}
              </g>
            );
          }}
        </GestellView>
        <div style={{ opacity: enter, transform: `translateX(${(1 - enter) * 80}px)` }}>
          <Tester mode={v.mode} value={val.item ? val.item[1] : "– – –"} measuring={measuring} ok={okA} limit={v.limit} t={t} />
        </div>
      </div>
    );
  } else if (v.type === "protocol") {
    body = <Protocol fills={fills} t={t} />;
  } else if (v.type === "change" || v.type === "docs" || v.type === "tip" || v.type === "check") {
    const titles: Record<string, string> = { change: "Mein Änderungsauftrag (Beispiel)", docs: "Der Prüfer schaut auf …", tip: v.title ?? "Tipp", check: v.title ?? "Besichtigung" };
    const right =
      v.type === "change" ? (
        <svg width={720} height={520} viewBox="0 0 720 520">
          <text x={10} y={40} fontFamily={SANS} fontWeight={800} fontSize={28} fill={MUTED}>Netzwerk: Container zählen</text>
          <rect x={260} y={90} width={200} height={230} rx={10} fill="#fff" stroke={INK} strokeWidth={4} />
          <text x={360} y={130} textAnchor="middle" fontFamily={SANS} fontWeight={900} fontSize={34} fill={INK}>CTU</text>
          {[["CU", "B10 (Klappe zu)", 180], ["R", "S2 (Quittieren)", 240], ["PV", "3", 300]].map(([p, l, y]) => (
            <g key={p as string} opacity={ramp(t, 1, 1.6)}>
              <line x1={60} x2={260} y1={y as number} y2={y as number} stroke={INK} strokeWidth={4} />
              <text x={272} y={(y as number) + 9} fontFamily={SANS} fontWeight={800} fontSize={24} fill={INK}>{p}</text>
              <text x={60} y={(y as number) - 12} fontFamily={SANS} fontSize={22} fill={BLUE}>{l}</text>
            </g>
          ))}
          <g opacity={ramp(t, 2, 2.6)}>
            <line x1={460} x2={640} y1={180} y2={180} stroke={INK} strokeWidth={4} />
            <text x={472} y={168} fontFamily={SANS} fontWeight={800} fontSize={24} fill={INK}>Q</text>
            <text x={520} y={168} fontFamily={SANS} fontSize={22} fill={ORANGE}>„voll“</text>
          </g>
          <g opacity={ramp(t, 3, 3.6)}>
            <text x={10} y={400} fontFamily={SANS} fontWeight={800} fontSize={26} fill={INK}>P2 = „voll“ UND Taktmerker 1 Hz</text>
            <text x={10} y={444} fontFamily={SANS} fontWeight={800} fontSize={26} fill={INK}>S4 Start nur wenn NICHT „voll“</text>
            <circle cx={660} cy={420} r={22} fill={Math.floor(t * 2) % 2 ? "#ef4444" : "#7f1d1d"} />
          </g>
        </svg>
      ) : v.type === "docs" ? (
        <div style={{ position: "relative", width: 640, height: 560 }}>
          {["Stromlaufplan (geändert)", "Zuordnungsliste", "Programmausdruck", "Prüfprotokoll"].map((d2, k) => (
            <div key={d2} style={{ position: "absolute", left: 40 + k * 26, top: 20 + k * 44, width: 470, height: 340, background: "#fff", borderRadius: 8, boxShadow: "0 12px 30px rgba(15,23,42,0.18)",
              transform: `rotate(${(k - 1.5) * 2.5}deg)`, padding: 24, opacity: ramp(t, k * 0.3, k * 0.3 + 0.4) }}>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, color: INK }}>{d2}</div>
              {Array.from({ length: 7 }, (_, r) => <div key={r} style={{ height: 8, background: "#e2e8f0", borderRadius: 4, margin: "18px 0", width: `${90 - r * 7}%` }} />)}
            </div>
          ))}
          <svg width={160} height={160} viewBox="0 0 160 160" style={{ position: "absolute", left: 300 + Math.sin(t * 1.2) * 120, top: 200 + Math.cos(t * 0.9) * 90 }}>
            <circle cx={64} cy={64} r={44} fill="rgba(255,255,255,0.35)" stroke={INK} strokeWidth={8} />
            <line x1={96} y1={96} x2={145} y2={145} stroke={INK} strokeWidth={14} strokeLinecap="round" />
          </svg>
        </div>
      ) : v.type === "tip" ? (
        <svg width={360} height={360} viewBox="0 0 120 120">
          <path d="M60 10 Q92 12 92 44 Q92 60 76 72 L76 86 L44 86 L44 72 Q28 60 28 44 Q28 12 60 10 Z" fill="#fde68a" stroke={INK} strokeWidth={4} />
          <path d="M46 96 h28 M50 106 h20" stroke={INK} strokeWidth={4} strokeLinecap="round" />
        </svg>
      ) : (
        <GestellView w={760} h={700} t={t} st={{}} />
      );
    body = (
      <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 90px", gap: 60 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 54, color: INK, marginBottom: 18, opacity: sp(t, 0) }}>{titles[v.type]}</div>
          <ItemList items={v.items} t={t} cue={cue} check={v.type === "check" || v.type === "docs"} size={v.items.length > 6 ? 30 : 34} />
        </div>
        <div style={{ opacity: enter }}>{right}</div>
      </div>
    );
  }

  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 50, top: 30, display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 24, color: "#fff", background: INK, borderRadius: 10, padding: "6px 12px" }}>AP T2</div>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 24, color: MUTED }}>Prüfungssimulation · Blechbearbeitungsmaschine</div>
      </div>
      {sc.topic > 0 ? <Phases cur={sc.topic} topics={s.topics} /> : null}
      <AbsoluteFill style={{ top: 100, height: 830, opacity: enter }}>{body}</AbsoluteFill>
      {sub ? <Sub words={ln.words} t={t} /> : null}
    </AbsoluteFill>
  );
};

export const PruefVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const { s } = DATA[KB];
  let from = 0;
  const allFills: Fill[][] = [];
  const acc: Fill[] = [];
  s.sentences.forEach((sc, i) => {
    const ln = info(KB, i);
    const cue = cueFn(ln.words);
    const mine: Fill[] = ((sc.v as any).fill ?? []).map((f: [string, string, string]) => ({ key: f[1], val: f[2], at: cue(f[0]) || 0.5 }));
    allFills.push([...acc.map((f) => ({ ...f, at: -10 })), ...mine]);
    acc.push(...mine);
  });
  return (
    <AbsoluteFill style={{ background: "radial-gradient(1400px 900px at 30% 20%, #f4f6f8, #dde3e8)" }}>
      {s.sentences.map((sc, i) => {
        const ln = info(KB, i);
        const dur = durF(KB, i);
        const start = from;
        from += dur;
        return (
          <Sequence key={i} from={start} durationInFrames={dur}>
            <PruefScene i={i} dur={dur} fills={allFills[i]} />
            {ln.file ? (
              <Sequence from={lead(sc)}>
                <Audio src={staticFile(ln.file)} />
              </Sequence>
            ) : null}
            {sc.v.type === "phase" ? <Audio src={staticFile("wiso/sfx/whoosh.mp3")} volume={0.3} /> : null}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
