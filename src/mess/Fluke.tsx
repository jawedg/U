// Fluke 1664 FC als Overlay (gehalten in der Hand, POV). Aufbau nach Users Manual: Drehschalter, LCD mit
// F1–F4 rechts daneben, TEST-Taste mit Touchpad links, Warndreieck darüber, Messbuchsen L (rot) / PE (grün) / N (blau).
import React from "react";

export type FlukeState = {
  dial?: string; fn?: string; prim?: string; unit?: string; sec?: string; F1?: string; F2?: string; F3?: string; F4?: string;
  zero?: number; rcdok?: number; hl?: string; hold?: number; note?: string; pose?: string;
};

const DIAL = [
  ["V", "V"], ["RISO", "R ISO"], ["RLO", "R LO"], ["ZI", "Zi"], ["ZIHI", "Zi HI"], ["DT", "ΔT"], ["IDN", "IΔN"], ["PHASE", "⟳"], ["RE", "RE"], ["AUTO", "AUTO"],
];
const ang = (i: number) => 210 - (i * 240) / (DIAL.length - 1); // Grad, 210° … −30°

export const Fluke: React.FC<{ st: FlukeState; press?: string; pressA: number; dialA: number; prevDial?: string; t: number }> = ({ st, press, pressA, dialA, prevDial, t }) => {
  const di = Math.max(0, DIAL.findIndex((d) => d[0] === (st.dial ?? "V")));
  const pi = Math.max(0, DIAL.findIndex((d) => d[0] === (prevDial ?? st.dial ?? "V")));
  const a = ang(pi) + (ang(di) - ang(pi)) * dialA;
  const cx = 280, cy = 640;
  const glow = (k: string) => (press === k ? pressA : 0) + (k === "F2" && st.hold ? 0.6 + 0.4 * Math.sin(t * 8) : 0);
  const hl = st.hl ?? "";
  const ring = (x: number, y: number, w: number, h: number, on: boolean) =>
    on ? <rect x={x} y={y} width={w} height={h} rx={18} fill="none" stroke="#ff7a1a" strokeWidth={7} opacity={0.6 + 0.4 * Math.sin(t * 6)} /> : null;
  const fkeys = ["F1", "F2", "F3", "F4"];
  return (
    <svg width={560} height={840} viewBox="0 0 560 840" style={{ overflow: "visible", filter: "drop-shadow(0 30px 40px rgba(0,0,0,0.45))" }}>
      {/* Messbuchsen oben */}
      {[["#dc2626", "L", 200], ["#16a34a", "PE", 280], ["#2563eb", "N", 360]].map(([c, l, x]) => (
        <g key={l as string}>
          <rect x={(x as number) - 20} y={-30} width={40} height={50} rx={8} fill={c as string} />
          <text x={x as number} y={-40} textAnchor="middle" fontFamily="Inter" fontWeight={800} fontSize={20} fill="#fff" stroke="#000" strokeWidth={0.6}>{l}</text>
        </g>
      ))}
      {/* Gehäuse */}
      <rect x={0} y={0} width={560} height={840} rx={64} fill="#f4c20d" stroke="#a37e00" strokeWidth={4} />
      <rect x={22} y={22} width={516} height={796} rx={46} fill="#2b2f33" />
      <text x={40} y={60} fontFamily="Inter" fontWeight={900} fontSize={26} fill="#f4c20d">FLUKE</text>
      <text x={140} y={60} fontFamily="Inter" fontWeight={700} fontSize={20} fill="#cbd5e1">1664 FC</text>
      {/* Warndreieck + Touchpad + TEST */}
      <path d="M85 92 L110 136 L60 136 Z" fill={hl === "warn" ? "#ef4444" : "#3f454b"} stroke="#e2e8f0" strokeWidth={3} />
      <text x={85} y={130} textAnchor="middle" fontFamily="Inter" fontWeight={900} fontSize={26} fill="#fff">!</text>
      <ellipse cx={85} cy={262} rx={60} ry={100} fill="#9aa3ab" stroke="#5b636b" strokeWidth={3} />
      <circle cx={85} cy={262} r={44} fill={glow("TEST") > 0 ? "#ffd166" : "#e5e7eb"} stroke="#111" strokeWidth={4} transform={`translate(${85 * glow("TEST") * 0.06} ${262 * glow("TEST") * 0.06}) scale(${1 - glow("TEST") * 0.06})`} />
      <text x={85} y={271} textAnchor="middle" fontFamily="Inter" fontWeight={900} fontSize={26} fill="#111">TEST</text>
      {ring(15, 150, 140, 230, hl === "test")}
      {ring(48, 82, 74, 64, hl === "warn")}
      {/* LCD */}
      <rect x={160} y={86} width={280} height={300} rx={14} fill="#aebba5" stroke="#1f2937" strokeWidth={4} />
      <text x={174} y={118} fontFamily="Inter" fontWeight={800} fontSize={22} fill="#1d2b1f">{st.F1 && /L-PE|L-N|N-PE/.test(st.F1) ? st.F1 : st.fn === "PHASE" ? "L1 L2 L3" : ""}</text>
      <text x={330} y={118} textAnchor="end" fontFamily="Inter" fontWeight={800} fontSize={22} fill="#1d2b1f">{st.fn === "DT" ? "ΔT" : st.fn === "PHASE" ? "⟳" : st.fn === "RISO" ? "R ISO" : st.fn === "RLO" ? "R LO" : ""}</text>
      {st.zero ? <text x={174} y={150} fontFamily="Inter" fontWeight={900} fontSize={22} fill="#1d2b1f">ZERO ✓</text> : null}
      {st.rcdok ? <text x={174} y={150} fontFamily="Inter" fontWeight={900} fontSize={22} fill="#1d2b1f">RCD ✓</text> : null}
      <text x={335} y={250} textAnchor="end" fontFamily="'JetBrains Mono', monospace" fontWeight={800} fontSize={82} fill="#0f1a11">{st.prim ?? ""}</text>
      <text x={340} y={250} fontFamily="Inter" fontWeight={800} fontSize={30} fill="#0f1a11">{st.unit ?? ""}</text>
      <text x={335} y={340} textAnchor="end" fontFamily="'JetBrains Mono', monospace" fontWeight={700} fontSize={34} fill="#1d2b1f">{st.sec ?? ""}</text>
      {fkeys.map((k, i) => (
        <text key={k} x={432} y={130 + i * 70} textAnchor="end" fontFamily="Inter" fontWeight={800} fontSize={19} fill="#1d2b1f">{(st as any)[k] ?? ""}</text>
      ))}
      {/* F1–F4 rechts neben dem Display */}
      {fkeys.map((k, i) => {
        const g = glow(k);
        return (
          <g key={k}>
            <rect x={458} y={100 + i * 70} width={64} height={50} rx={14} fill={g > 0 ? "#ffd166" : "#7dd3fc"} stroke="#0f172a" strokeWidth={3} />
            <text x={490} y={133 + i * 70} textAnchor="middle" fontFamily="Inter" fontWeight={900} fontSize={22} fill="#0f172a">{k}</text>
          </g>
        );
      })}
      {ring(448, 90, 84, 290, hl === "fkeys")}
      {/* MEMORY / Pfeile */}
      <rect x={190} y={404} width={110} height={36} rx={10} fill="#4b5563" />
      <text x={245} y={428} textAnchor="middle" fontFamily="Inter" fontWeight={800} fontSize={15} fill="#e5e7eb">MEMORY</text>
      <rect x={320} y={404} width={50} height={36} rx={10} fill="#4b5563" />
      <text x={345} y={429} textAnchor="middle" fontFamily="Inter" fontSize={18} fill="#e5e7eb">▲▼</text>
      {/* Drehschalter */}
      {DIAL.map(([id, label], i) => {
        const r = ((ang(i) * Math.PI) / 180);
        const on = id === st.dial;
        return (
          <g key={id}>
            <line x1={cx + Math.cos(r) * 128} y1={cy - Math.sin(r) * 128} x2={cx + Math.cos(r) * 146} y2={cy - Math.sin(r) * 146} stroke={on ? "#ffd166" : "#94a3b8"} strokeWidth={on ? 7 : 4} />
            <text x={cx + Math.cos(r) * 190} y={cy - Math.sin(r) * 190 + 9} textAnchor="middle" fontFamily="Inter" fontWeight={on ? 900 : 700} fontSize={on ? 30 : 24} fill={on ? "#ffd166" : "#e5e7eb"}>{label}</text>
          </g>
        );
      })}
      <circle cx={cx} cy={cy} r={120} fill="#1f2328" stroke="#f4c20d" strokeWidth={6} />
      <g transform={`rotate(${-a + 90} ${cx} ${cy})`}>
        <rect x={cx - 26} y={cy - 116} width={52} height={232} rx={22} fill="#3b4148" stroke="#0b0d0f" strokeWidth={3} />
        <path d={`M${cx} ${cy - 112} L${cx - 14} ${cy - 84} L${cx + 14} ${cy - 84} Z`} fill="#ffd166" />
      </g>
      {ring(cx - 230, cy - 230, 460, 400, hl === "dial")}
      {hl === "leads" ? <rect x={170} y={-50} width={220} height={80} rx={14} fill="none" stroke="#ff7a1a" strokeWidth={7} opacity={0.6 + 0.4 * Math.sin(t * 6)} /> : null}
    </svg>
  );
};
