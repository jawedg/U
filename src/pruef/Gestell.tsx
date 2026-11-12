// Prüfungsgestell (Montageplatte 600 × 600 mm) – Blechbearbeitungsmaschine, AP T2 Winter 2026/27.
// Koordinaten: viewBox 0 0 960 760. Montageplatte 0..640, Bedieneinheit rechts, CEE-Stecker unten.
import React from "react";

export const GW = 960, GH = 760;
const INK = "#1f2933";
const ORANGE = "#f26b1d";

// Bauteile: Rahmen für Hervorhebung
export const BOX: Record<string, [number, number, number, number]> = {
  F3: [50, 60, 52, 132], F1: [104, 60, 24, 132], F2: [130, 60, 24, 132], T1: [160, 64, 92, 124], F4: [266, 60, 54, 132], Q1: [330, 64, 46, 124], Q2: [380, 64, 46, 124],
  X5: [462, 62, 132, 132], SPS: [50, 262, 254, 128], X10: [420, 252, 182, 150], X1: [50, 470, 242, 112], X2: [304, 470, 104, 112], X3: [418, 470, 84, 112],
  X4: [512, 470, 90, 112], BED: [690, 170, 220, 400], CEE: [86, 680, 130, 72], PLATTE: [596, 596, 40, 40],
};

const x1 = (k: number): [number, number] => [52 + (k - 0.5) * 10.9, 482];
// Messpunkte
export const PT: Record<string, [number, number]> = {
  CEEPE: [151, 700], PLATTE: [616, 616], X5PE: [528, 92], X5: [528, 128], M1PE: x1(16), BEDPE: [900, 552], NULL: [760, 700],
  ...Object.fromEntries(Array.from({ length: 22 }, (_, i) => [`X1:${i + 1}`, x1(i + 1)])),
};

export type GState = Record<string, number | string>;

const Breaker: React.FC<{ x: number; w: number; label: string; sub: string; on: boolean; test?: boolean }> = ({ x, w, label, sub, on, test }) => (
  <g>
    <rect x={x} y={64} width={w} height={124} rx={4} fill="#f8fafc" stroke={INK} strokeWidth={2} />
    <rect x={x + w / 2 - 7} y={on ? 92 : 118} width={14} height={26} rx={3} fill={on ? "#475569" : "#ef4444"} />
    {test ? <rect x={x + 6} y={150} width={12} height={10} rx={2} fill="#facc15" stroke={INK} strokeWidth={1} /> : null}
    <text x={x + w / 2} y={86} textAnchor="middle" fontFamily="Inter" fontSize={11} fontWeight={700} fill={INK}>{sub}</text>
    <text x={x + w / 2} y={182} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill={INK}>{label}</text>
  </g>
);

const Contactor: React.FC<{ x: number; label: string; on: boolean }> = ({ x, label, on }) => (
  <g>
    <rect x={x} y={64} width={46} height={124} rx={5} fill="#e2e8f0" stroke={INK} strokeWidth={2} />
    <rect x={x + 6} y={74} width={34} height={20} rx={2} fill="#cbd5e1" />
    <rect x={x + 13} y={on ? 112 : 104} width={20} height={18} rx={3} fill={on ? ORANGE : "#94a3b8"} />
    {[0, 1, 2].map((i) => <circle key={i} cx={x + 10 + i * 13} cy={170} r={4} fill="#64748b" />)}
    <text x={x + 23} y={150} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill={INK}>{label}</text>
  </g>
);

const Terminals: React.FC<{ x: number; n: number; label: string; color: (k: number) => string }> = ({ x, n, label, color }) => (
  <g>
    <text x={x} y={466} fontFamily="Inter" fontSize={13} fontWeight={800} fill={INK}>{label}</text>
    {Array.from({ length: n }, (_, i) => (
      <g key={i}>
        <rect x={x + i * 10.9} y={474} width={10} height={104} rx={1.5} fill={color(i + 1)} stroke="#475569" strokeWidth={1} />
        <circle cx={x + i * 10.9 + 5} cy={482} r={3} fill="#334155" />
        <circle cx={x + i * 10.9 + 5} cy={570} r={3} fill="#334155" />
        <text x={x + i * 10.9 + 5} y={528} textAnchor="middle" fontFamily="Inter" fontSize={7} fill="#334155">{i + 1}</text>
      </g>
    ))}
  </g>
);

const Lamp: React.FC<{ cx: number; cy: number; color: string; on: number; label: string }> = ({ cx, cy, color, on, label }) => (
  <g>
    <circle cx={cx} cy={cy} r={22} fill="#1e293b" />
    <circle cx={cx} cy={cy} r={16} fill={on ? color : "#475569"} style={{ filter: on ? `drop-shadow(0 0 ${10 * on}px ${color})` : undefined }} />
    <text x={cx} y={cy + 42} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={700} fill="#e2e8f0">{label}</text>
  </g>
);
const Button: React.FC<{ cx: number; cy: number; color: string; label: string; rotary?: boolean }> = ({ cx, cy, color, label, rotary }) => (
  <g>
    <circle cx={cx} cy={cy} r={22} fill="#0f172a" />
    {rotary ? <rect x={cx - 5} y={cy - 18} width={10} height={36} rx={4} fill="#e2e8f0" transform={`rotate(35 ${cx} ${cy})`} /> : <circle cx={cx} cy={cy} r={15} fill={color} />}
    <text x={cx} y={cy + 42} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={700} fill="#e2e8f0">{label}</text>
  </g>
);

export const Gestell: React.FC<{ st?: GState; t?: number; hl?: string[]; hlA?: number }> = ({ st = {}, t = 0, hl = [], hlA = 1 }) => {
  const on = (k: string) => (st[k] === "blink" ? (Math.floor(t * 2) % 2 === 0 ? 1 : 0) : st[k] ? 1 : 0);
  return (
    <g>
      {/* Montageplatte */}
      <rect x={0} y={0} width={640} height={640} rx={8} fill="#cfd6dd" stroke="#64748b" strokeWidth={3} />
      <rect x={0} y={0} width={640} height={640} rx={8} fill="url(#lochblech)" opacity={0.5} />
      {/* Kabelkanäle */}
      {[14, 214, 414, 606].map((y) => (
        <g key={y}>
          <rect x={14} y={y} width={612} height={26} fill="#94a3b8" stroke="#64748b" />
          {Array.from({ length: 30 }, (_, i) => <rect key={i} x={20 + i * 20.4} y={y + 3} width={10} height={20} fill="#a8b4c2" />)}
        </g>
      ))}
      {/* Hutschienen */}
      {[126, 326, 526].map((y) => <rect key={y} x={46} y={y - 5} width={560} height={10} fill="#e5e7eb" stroke="#9ca3af" />)}
      {/* Reihe A */}
      <Breaker x={50} w={52} label="-F3" sub="B16 10mA" on={!st.F3trip} test />
      <Breaker x={104} w={24} label="-F1" sub="6A" on />
      <Breaker x={130} w={24} label="-F2" sub="4A" on />
      <g>
        <rect x={160} y={64} width={92} height={124} rx={6} fill="#dbe4ee" stroke={INK} strokeWidth={2} />
        <text x={206} y={112} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill={INK}>-T1</text>
        <text x={206} y={132} textAnchor="middle" fontFamily="Inter" fontSize={12} fill={INK}>230 V ~</text>
        <text x={206} y={150} textAnchor="middle" fontFamily="Inter" fontSize={12} fill={INK}>24 V =</text>
        <circle cx={240} cy={76} r={4} fill={st.T1off ? "#475569" : "#22c55e"} />
      </g>
      <g>
        <rect x={266} y={64} width={54} height={124} rx={5} fill="#334155" stroke={INK} strokeWidth={2} />
        <circle cx={293} cy={98} r={14} fill="#cbd5e1" stroke="#0f172a" />
        <line x1={293} y1={98} x2={302} y2={89} stroke="#0f172a" strokeWidth={3} />
        <rect x={281} y={st.F4trip ? 130 : 120} width={24} height={20} rx={3} fill={st.F4trip ? "#ef4444" : "#22c55e"} />
        <text x={293} y={176} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill="#f8fafc">-F4</text>
      </g>
      <Contactor x={330} label="-Q1" on={!!on("Q1")} />
      <Contactor x={380} label="-Q2" on={!!on("Q2")} />
      {/* Steckdose */}
      <g>
        <rect x={462} y={62} width={132} height={132} rx={14} fill="#f1f5f9" stroke={INK} strokeWidth={2} />
        <circle cx={528} cy={128} r={46} fill="#e2e8f0" stroke="#94a3b8" strokeWidth={2} />
        <circle cx={510} cy={128} r={6} fill="#334155" />
        <circle cx={546} cy={128} r={6} fill="#334155" />
        <rect x={522} y={84} width={12} height={10} fill="#94a3b8" />
        <rect x={522} y={162} width={12} height={10} fill="#94a3b8" />
        <text x={528} y={212} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill={INK}>-X5</text>
      </g>
      {/* SPS */}
      <g>
        <rect x={50} y={262} width={254} height={128} rx={6} fill="#e5e7eb" stroke={INK} strokeWidth={2} />
        <rect x={50} y={262} width={254} height={24} fill="#cbd5e1" />
        <rect x={50} y={366} width={254} height={24} fill="#cbd5e1" />
        {Array.from({ length: 22 }, (_, i) => <circle key={i} cx={60 + i * 11} cy={274} r={3} fill="#475569" />)}
        {Array.from({ length: 22 }, (_, i) => <circle key={`b${i}`} cx={60 + i * 11} cy={378} r={3} fill="#475569" />)}
        <text x={66} y={312} fontFamily="Inter" fontSize={15} fontWeight={900} fill="#0f766e">S7-1200</text>
        <text x={66} y={330} fontFamily="Inter" fontSize={11} fill={INK}>CPU · DI 14 / DQ 10 / AI 2</text>
        {["RUN", "ERR", "MAINT"].map((l, i) => (
          <g key={l}>
            <circle cx={70 + i * 46} cy={350} r={5} fill={i === 0 ? "#22c55e" : "#475569"} />
            <text x={78 + i * 46} y={354} fontFamily="Inter" fontSize={9} fill={INK}>{l}</text>
          </g>
        ))}
        {Array.from({ length: 10 }, (_, i) => <rect key={`io${i}`} x={210 + (i % 5) * 16} y={300 + Math.floor(i / 5) * 18} width={10} height={8} rx={2}
          fill={(i === 0 && on("P1")) || (i === 1 && on("P2")) || (i === 4 && on("Q1")) || (i === 5 && on("Q2")) ? "#22c55e" : "#94a3b8"} />)}
      </g>
      {/* Prozess-Simulationsplatine */}
      <g>
        <rect x={420} y={252} width={182} height={150} rx={6} fill="#14532d" stroke="#052e16" strokeWidth={2} />
        <text x={430} y={270} fontFamily="Inter" fontSize={11} fontWeight={800} fill="#bbf7d0">-X10 Prozess-Simulation</text>
        {[["P10", "M1 links"], ["P11", "M1 rechts"], ["P12", "M2"], ["P13", ""], ["P14", ""]].map(([id, l], i) => (
          <g key={id}>
            <circle cx={440 + i * 34} cy={298} r={8} fill={on(id) ? "#4ade80" : "#166534"} style={{ filter: on(id) ? "drop-shadow(0 0 8px #4ade80)" : undefined }} />
            <text x={440 + i * 34} y={320} textAnchor="middle" fontFamily="Inter" fontSize={9} fontWeight={700} fill="#dcfce7">{id}</text>
            <text x={440 + i * 34} y={331} textAnchor="middle" fontFamily="Inter" fontSize={7} fill="#bbf7d0">{l}</text>
          </g>
        ))}
        {[["B10", "zu"], ["B11", "auf"], ["B12", ""], ["B13", "Band"]].map(([id, l], i) => (
          <g key={id}>
            <rect x={432 + i * 36} y={346} width={22} height={12} rx={3} fill="#e5e7eb" />
            <rect x={(on(id) ? 444 : 434) + i * 36} y={348} width={8} height={8} rx={2} fill={on(id) ? "#f59e0b" : "#334155"} />
            <text x={443 + i * 36} y={372} textAnchor="middle" fontFamily="Inter" fontSize={9} fontWeight={700} fill="#dcfce7">{id}</text>
            <text x={443 + i * 36} y={383} textAnchor="middle" fontFamily="Inter" fontSize={7} fill="#bbf7d0">{l}</text>
          </g>
        ))}
        <circle cx={588} cy={360} r={9} fill="#cbd5e1" stroke="#0f172a" />
      </g>
      {/* Klemmleisten */}
      <Terminals x={50} n={22} label="-X1" color={(k) => ([9, 10, 16].includes(k) ? "url(#gnge)" : k === 7 ? "#7dd3fc" : "#9ca3af")} />
      <Terminals x={304} n={9} label="-X2" color={(k) => (k % 2 ? "#3b82f6" : "#9ca3af")} />
      <Terminals x={418} n={7} label="-X3" color={() => "#9ca3af"} />
      <Terminals x={512} n={8} label="-X4" color={() => "#9ca3af"} />
      {/* PE-Anschluss Montageplatte */}
      <g>
        <circle cx={616} cy={616} r={12} fill="#e5e7eb" stroke={INK} strokeWidth={2} />
        <path d="M608 616 h16 M611 621 h10 M614 626 h4 M616 604 v12" stroke={INK} strokeWidth={2} />
      </g>
      {/* CEE-Stecker mit Leitung */}
      <path d="M100 606 C100 650 120 660 150 680" fill="none" stroke="#111827" strokeWidth={9} />
      <g>
        <rect x={100} y={680} width={102} height={66} rx={14} fill="#dc2626" stroke="#7f1d1d" strokeWidth={2} />
        <text x={151} y={724} textAnchor="middle" fontFamily="Inter" fontSize={13} fontWeight={800} fill="#fff">CEE 16 A</text>
        <circle cx={151} cy={700} r={5} fill="#facc15" />
      </g>
      {/* Bedieneinheit */}
      <path d="M640 520 C665 520 670 520 690 520" fill="none" stroke="#111827" strokeWidth={8} />
      <g>
        <rect x={690} y={170} width={220} height={400} rx={16} fill="#334155" stroke="#0f172a" strokeWidth={3} />
        <text x={800} y={198} textAnchor="middle" fontFamily="Inter" fontSize={14} fontWeight={800} fill="#e2e8f0">Bedieneinheit</text>
        <Button cx={748} cy={250} color="#e2e8f0" label="S1 EIN/AUS" rotary />
        <Lamp cx={852} cy={250} color="#f8fafc" on={on("P1")} label="P1 EIN" />
        <Button cx={748} cy={350} color="#3b82f6" label="S2 Quitt." />
        <Lamp cx={852} cy={350} color="#ef4444" on={on("P2")} label="P2 Störung" />
        <Button cx={748} cy={450} color="#1f2937" label="S3 Rechts" />
        <Button cx={852} cy={450} color="#22c55e" label="S4 Start" />
        <circle cx={900} cy={552} r={7} fill="url(#gnge)" stroke={INK} />
      </g>
      {/* Hervorhebungen */}
      {hl.map((id) => {
        const b = BOX[id];
        if (!b) return null;
        return <rect key={id} x={b[0] - 8} y={b[1] - 8} width={b[2] + 16} height={b[3] + 16} rx={12} fill="rgba(242,107,29,0.08)" stroke={ORANGE} strokeWidth={5} opacity={hlA} style={{ filter: "drop-shadow(0 0 10px rgba(242,107,29,0.6))" }} />;
      })}
    </g>
  );
};

export const GestellDefs: React.FC = () => (
  <defs>
    <pattern id="lochblech" width="14" height="14" patternUnits="userSpaceOnUse">
      <circle cx="7" cy="7" r="2.2" fill="#94a3b8" />
    </pattern>
    <pattern id="gnge" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="8" height="8" fill="#22c55e" />
      <rect width="4" height="8" fill="#facc15" />
    </pattern>
  </defs>
);
