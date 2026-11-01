// 2D-Strichzeichnungen im „Früher“-Stil: helle Linien auf dunklem Grund, Gold-Akzente.
// Menschen haben KEINE Gesichter. Gefährten (Sahaba) zusätzlich mit Licht über dem Kopf.
import React from "react";

export const INK = "#efe6d2";
export const DIM = "rgba(239,230,210,0.35)";
export const BG = "#0b0d16";
export const GOLD = "#e6b85c";
export const GREEN = "#7fe0a8";
export const SW = 3; // Strichstärke

export const rand = (seed: number) => () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

const line = { stroke: INK, strokeWidth: SW, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };

// ---------------- Mensch ----------------
export type Pose = "stand" | "walk" | "sit" | "lie" | "ears" | "offer" | "run" | "look" | "climb";

export const Person: React.FC<{
  x: number;
  y: number;
  s?: number;
  pose?: Pose;
  phase?: number; // Laufzyklus
  flip?: boolean;
  head?: "turban" | "shawl" | "cap" | "none";
  glow?: number; // Licht über dem Kopf (Sahaba) 0..1
  color?: string; // Linienfarbe (z. B. grün im Traum)
  cloak?: number; // Umhang zieht hinterher 0..1
  opacity?: number;
  holding?: React.ReactNode; // Gegenstand in der Hand (bei pose offer)
}> = ({ x, y, s = 1, pose = "stand", phase = 0, flip, head = "turban", glow = 0, color = INK, cloak = 0, opacity = 1, holding }) => {
  const st = { ...line, stroke: color };
  const walking = pose === "walk" || pose === "run";
  const amp = pose === "run" ? 20 : 11;
  const sw = walking ? Math.sin(phase) : 0;
  const bob = walking ? Math.abs(Math.cos(phase)) * (pose === "run" ? 6 : 3) : 0;

  if (pose === "sit") {
    return (
      <g transform={`translate(${x},${y}) scale(${flip ? -s : s},${s})`} opacity={opacity}>
        <path d="M -52 0 Q -50 -38 -20 -50 L 20 -50 Q 50 -38 52 0 Z" fill={BG} {...st} />
        <path d="M -22 -50 L -20 -118 Q 0 -126 20 -118 L 22 -50" fill={BG} {...st} />
        <path d="M -20 -105 Q -36 -70 -8 -56 M 20 -105 Q 36 -70 8 -56" fill="none" {...st} />
        <Head y={-140} head={head} st={st} glow={glow} />
      </g>
    );
  }
  if (pose === "lie") {
    return (
      <g transform={`translate(${x},${y}) scale(${flip ? -s : s},${s})`} opacity={opacity}>
        <path d="M -95 -4 L -95 -30 Q -60 -40 40 -34 L 80 -26 L 80 -4 Z" fill={BG} {...st} />
        <path d="M 80 -10 L 108 -8 M 80 -22 L 108 -24" fill="none" {...st} />
        <Head x={-118} y={-20} head="none" st={st} glow={glow} />
      </g>
    );
  }

  // Arme: [Schulter->Ellbogen->Hand] relativ
  let armL = `M -20 -152 L ${-26 - sw * 8} -112 L ${-24 - sw * 14} -78`;
  let armR = `M 20 -152 L ${26 + sw * 8} -112 L ${24 + sw * 14} -78`;
  if (pose === "ears") {
    armL = "M -20 -152 L -44 -150 L -24 -184";
    armR = "M 20 -152 L 44 -150 L 24 -184";
  } else if (pose === "offer") {
    armR = "M 20 -152 L 46 -128 L 78 -132";
  } else if (pose === "look") {
    armR = "M 20 -152 L 40 -170 L 30 -192";
  } else if (pose === "run") {
    armL = `M -20 -152 L ${-30 - sw * 22} -122 L ${-14 - sw * 30} -104`;
    armR = `M 20 -152 L ${30 + sw * 22} -122 L ${14 + sw * 30} -104`;
  } else if (pose === "climb") {
    armL = `M -20 -152 L -30 ${-178 - sw * 10} L -18 ${-206 - sw * 10}`;
    armR = `M 20 -152 L 30 ${-178 + sw * 10} L 18 ${-206 + sw * 10}`;
  }
  const lean = pose === "run" ? -10 : 0;
  return (
    <g transform={`translate(${x},${y - bob}) scale(${flip ? -s : s},${s}) skewX(${lean})`} opacity={opacity}>
      {cloak > 0 ? (
        <path
          d={`M 14 -156 Q ${70 + cloak * 40} ${-120 + Math.sin(phase * 2) * 10} ${120 + cloak * 80} ${-8 + Math.sin(phase * 2 + 1) * 6} L ${60 + cloak * 40} 0 Q 40 -60 18 -100`}
          fill={BG}
          {...st}
          stroke={GOLD}
        />
      ) : null}
      {/* Beine */}
      <path d={`M -10 -30 L ${-10 - sw * amp} 0 M 10 -30 L ${10 + sw * amp} 0`} fill="none" {...st} />
      {/* Gewand */}
      <path d="M -22 -158 Q -26 -100 -36 -28 L 36 -28 Q 26 -100 22 -158 Q 0 -166 -22 -158 Z" fill={BG} {...st} />
      <path d="M 0 -150 L 0 -100" fill="none" {...st} stroke={DIM} />
      <path d={armL} fill="none" {...st} />
      <path d={armR} fill="none" {...st} />
      {pose === "offer" && holding ? <g transform="translate(86,-140)">{holding}</g> : null}
      <Head y={-182} head={head} st={st} glow={glow} />
    </g>
  );
};

const Head: React.FC<{ x?: number; y: number; head: string; st: object; glow: number }> = ({ x = 0, y, head, st, glow }) => (
  <g transform={`translate(${x},${y})`}>
    {glow > 0 ? <circle r={44} fill="url(#faceGlow)" opacity={glow} /> : null}
    <circle r={16} fill={glow > 0 ? "#3a2f1c" : BG} {...st} />
    {head === "turban" ? (
      <path d="M -18 -4 Q -20 -22 0 -24 Q 20 -22 18 -4 Q 0 -12 -18 -4 Z M 14 -6 Q 26 6 18 18" fill={BG} {...st} />
    ) : head === "shawl" ? (
      <path d="M -19 4 Q -22 -24 0 -24 Q 22 -24 19 4 L 24 30 M -19 4 L -24 30" fill="none" {...st} />
    ) : head === "cap" ? (
      <path d="M -15 -6 Q 0 -22 15 -6 Z" fill={BG} {...st} />
    ) : null}
    {glow > 0 ? <circle r={15} fill="url(#faceGlowCore)" opacity={glow} /> : null}
  </g>
);

// ---------------- Gebäude & Landschaft ----------------
export const House: React.FC<{
  x: number;
  y: number;
  w: number;
  h: number;
  lit?: number[]; // Indizes leuchtender Fenster
  windows?: number;
  door?: number; // 0 zu … 1 offen (leuchtet)
  dim?: boolean;
}> = ({ x, y, w, h, lit = [], windows = 2, door = -1, dim }) => {
  const st = { ...line, stroke: dim ? DIM : INK };
  const notches = Math.max(2, Math.floor(w / 26));
  const par = Array.from({ length: notches }, (_, i) => {
    const px = x + (w / notches) * i + w / notches / 2 - 5;
    return `M ${px} ${y - h} L ${px} ${y - h - 8} L ${px + 10} ${y - h - 8} L ${px + 10} ${y - h}`;
  }).join(" ");
  return (
    <g>
      <rect x={x} y={y - h} width={w} height={h} fill={BG} {...st} />
      <path d={par} fill="none" {...st} />
      {Array.from({ length: windows }, (_, i) => {
        const wx = x + (w / (windows + 1)) * (i + 1) - 8;
        const on = lit.includes(i);
        return (
          <g key={i}>
            {on ? <circle cx={wx + 8} cy={y - h * 0.62} r={26} fill="url(#warmGlow)" /> : null}
            <rect x={wx} y={y - h * 0.62 - 10} width={16} height={20} rx={6} fill={on ? GOLD : BG} {...st} />
          </g>
        );
      })}
      {door >= 0 ? (
        <g>
          {door > 0 ? <ellipse cx={x + w / 2} cy={y - 26} rx={60 * door} ry={50} fill="url(#warmGlow)" /> : null}
          <path d={`M ${x + w / 2 - 16} ${y} L ${x + w / 2 - 16} ${y - 34} Q ${x + w / 2} ${y - 50} ${x + w / 2 + 16} ${y - 34} L ${x + w / 2 + 16} ${y}`} fill={door > 0 ? GOLD : BG} fillOpacity={door > 0 ? 0.35 + 0.65 * door : 1} {...st} />
        </g>
      ) : null}
    </g>
  );
};

export const Palm: React.FC<{ x: number; y: number; h: number; sway?: number; dim?: boolean }> = ({ x, y, h, sway = 0, dim }) => {
  const st = { ...line, stroke: dim ? DIM : INK };
  const tx = x + h * 0.12 + sway * 4;
  const ty = y - h;
  const fronds = [-150, -115, -80, -50, -20, 15, 45].map((a, i) => {
    const r = h * (0.42 + (i % 2) * 0.08);
    const rad = ((a + sway * 3) * Math.PI) / 180;
    const ex = tx + Math.cos(rad) * r;
    const ey = ty + Math.sin(rad) * r * 0.55 + r * 0.35;
    const cx = tx + Math.cos(rad) * r * 0.5;
    const cy = ty + Math.sin(rad) * r * 0.5 - r * 0.15;
    return `M ${tx} ${ty} Q ${cx} ${cy} ${ex} ${ey}`;
  });
  const ticks = Array.from({ length: Math.floor(h / 16) }, (_, i) => {
    const p = (i + 1) / (Math.floor(h / 16) + 1);
    const px = x + (tx - x) * p * p;
    const py = y - h * p;
    return `M ${px - 5} ${py} L ${px + 5} ${py - 3}`;
  }).join(" ");
  return (
    <g>
      <path d={`M ${x} ${y} Q ${x + h * 0.02} ${y - h * 0.5} ${tx} ${ty}`} fill="none" {...st} strokeWidth={SW + 1} />
      <path d={ticks} fill="none" {...st} stroke={DIM} />
      <path d={fronds.join(" ")} fill="none" {...st} />
    </g>
  );
};

export const Mosque: React.FC<{ x: number; y: number; s?: number; lights?: number; doorGlow?: number }> = ({ x, y, s = 1, lights = 0, doorGlow = 0 }) => {
  const st = line;
  return (
    <g transform={`translate(${x},${y}) scale(${s})`}>
      {/* Dach aus Palmwedeln hinten */}
      <path d="M -300 -150 L 300 -150" {...st} />
      <path d={Array.from({ length: 30 }, (_, i) => `M ${-296 + i * 20} -150 l 12 -10`).join(" ")} {...st} stroke={DIM} />
      {Array.from({ length: 9 }, (_, i) => (
        <path key={i} d={`M ${-260 + i * 65} -150 L ${-260 + i * 65} -70`} {...st} />
      ))}
      {lights > 0
        ? Array.from({ length: 5 }, (_, i) => <circle key={i} cx={-200 + i * 100} cy={-120} r={40} fill="url(#warmGlow)" opacity={lights} />)
        : null}
      {/* vordere Lehmmauer mit Eingang */}
      <path d="M -330 0 L -330 -80 L -40 -80 L -40 0 M 40 0 L 40 -80 L 330 -80 L 330 0" fill={BG} {...st} />
      <rect x={-330} y={-80} width={290} height={80} fill={BG} {...st} />
      <rect x={40} y={-80} width={290} height={80} fill={BG} {...st} />
      {doorGlow > 0 ? <ellipse cx={0} cy={-40} rx={90} ry={70} fill="url(#warmGlow)" opacity={doorGlow} /> : null}
      <path d="M -40 -80 L 40 -80" {...st} stroke={DIM} strokeDasharray="6 8" />
      {Array.from({ length: 10 }, (_, i) => (
        <path key={i} d={`M ${-320 + i * 30} -40 l 16 0 M ${60 + i * 28} -40 l 16 0`} {...st} stroke={DIM} />
      ))}
    </g>
  );
};

export const Ground: React.FC<{ y: number; dim?: boolean }> = ({ y, dim }) => (
  <g>
    <rect x={-2000} y={y} width={6000} height={3000} fill={BG} />
    <path d={`M -2000 ${y} L 4000 ${y}`} {...line} stroke={dim ? DIM : INK} />
  </g>
);

export const Dunes: React.FC<{ y: number; seed?: number; color?: string }> = ({ y, seed = 1, color = DIM }) => {
  const r = rand(seed);
  const d = Array.from({ length: 6 }, (_, i) => {
    const x0 = -400 + i * 380 + r() * 80;
    const hgt = 40 + r() * 70;
    return `M ${x0} ${y} Q ${x0 + 200} ${y - hgt} ${x0 + 420} ${y}`;
  }).join(" ");
  return <path d={d} fill="none" {...line} stroke={color} />;
};

export const Mountains: React.FC<{ y: number }> = ({ y }) => (
  <path
    d={`M -200 ${y} L 80 ${y - 180} L 240 ${y - 90} L 420 ${y - 260} L 620 ${y - 120} L 760 ${y - 200} L 1000 ${y - 60} L 1300 ${y}`}
    fill="none"
    {...line}
    stroke={DIM}
  />
);

export const Stars: React.FC<{ t: number; count?: number; opacity?: number; maxY?: number }> = ({ t, count = 90, opacity = 1, maxY = 1100 }) => {
  const r = rand(11);
  return (
    <g opacity={opacity}>
      {Array.from({ length: count }, (_, i) => {
        const x = r() * 1080;
        const y = r() * maxY;
        const tw = 0.5 + 0.5 * Math.sin(t * (1 + r() * 2) + i);
        return <circle key={i} cx={x} cy={y} r={1 + r() * 1.8} fill={INK} opacity={0.3 + 0.7 * tw} />;
      })}
    </g>
  );
};

export const Crescent: React.FC<{ x: number; y: number; r: number }> = ({ x, y, r }) => (
  <g>
    <circle cx={x} cy={y} r={r * 3} fill="url(#moonGlow)" />
    <path
      d={`M ${x + r * 0.3} ${y - r} A ${r} ${r} 0 1 0 ${x + r * 0.3} ${y + r} A ${r * 0.8} ${r * 0.8} 0 1 1 ${x + r * 0.3} ${y - r} Z`}
      fill={GOLD}
      stroke={GOLD}
      strokeWidth={2}
    />
  </g>
);

export const Sun: React.FC<{ x: number; y: number; r: number; t: number }> = ({ x, y, r, t }) => (
  <g>
    <circle cx={x} cy={y} r={r * 4} fill="url(#sunGlow)" />
    <circle cx={x} cy={y} r={r} fill="none" {...line} stroke={GOLD} strokeWidth={4} />
    {Array.from({ length: 16 }, (_, i) => {
      const a = (i / 16) * Math.PI * 2 + t * 0.2;
      const l = r * (1.3 + 0.15 * Math.sin(t * 3 + i));
      return <path key={i} d={`M ${x + Math.cos(a) * r * 1.15} ${y + Math.sin(a) * r * 1.15} L ${x + Math.cos(a) * l} ${y + Math.sin(a) * l}`} {...line} stroke={GOLD} />;
    })}
  </g>
);

// ---------------- Gegenstände ----------------
export const Bell: React.FC<{ s?: number; color?: string; swing?: number }> = ({ s = 1, color = GOLD, swing = 0 }) => (
  <g transform={`scale(${s}) rotate(${swing})`}>
    <path d="M 0 -50 m -6 0 a 6 6 0 1 0 12 0 a 6 6 0 1 0 -12 0" fill="none" stroke={color} strokeWidth={SW} />
    <path d="M -10 -44 Q -26 -40 -28 -10 Q -30 10 -40 18 L 40 18 Q 30 10 28 -10 Q 26 -40 10 -44 Z" fill={BG} stroke={color} strokeWidth={SW} strokeLinejoin="round" />
    <circle cx={0} cy={24} r={6} fill={color} />
  </g>
);

export const Horn: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <g transform={`scale(${s})`}>
    <path d="M -50 10 Q -20 -10 10 -20 Q 40 -30 46 -60 L 64 -52 Q 56 -18 20 0 Q -10 16 -48 22 Z" fill={BG} stroke={INK} strokeWidth={SW} strokeLinejoin="round" />
    <path d="M -20 4 L -16 16 M 0 -4 L 6 8 M 20 -14 L 28 -2" stroke={DIM} strokeWidth={SW} />
  </g>
);

export const Fire: React.FC<{ s?: number; t: number }> = ({ s = 1, t }) => {
  const f = (k: number) => 1 + 0.12 * Math.sin(t * 12 + k);
  return (
    <g transform={`scale(${s})`}>
      <circle cx={0} cy={-20} r={60} fill="url(#fireGlow)" />
      <path d={`M 0 ${-70 * f(0)} Q 30 -30 22 0 L -22 0 Q -30 -30 0 ${-70 * f(0)} Z`} fill={BG} stroke="#ff9a3c" strokeWidth={SW} />
      <path d={`M 0 ${-40 * f(2)} Q 14 -16 10 0 L -10 0 Q -14 -16 0 ${-40 * f(2)} Z`} fill="#ffcf5a" opacity={0.85} />
      <path d="M -34 6 L 34 -4 M -34 -4 L 34 6" stroke={INK} strokeWidth={SW + 1} strokeLinecap="round" />
    </g>
  );
};

export const Rock: React.FC<{ s?: number }> = ({ s = 1 }) => (
  <g transform={`scale(${s})`}>
    <path d="M -60 0 L -50 -40 L -10 -60 L 40 -50 L 64 -14 L 56 0 Z" fill={BG} {...line} />
    <path d="M -10 -60 L 0 -24 L 40 -50 M 0 -24 L -50 -40" fill="none" {...line} stroke={DIM} />
  </g>
);

export const Ladder: React.FC<{ x: number; y: number; h: number }> = ({ x, y, h }) => (
  <g>
    <path d={`M ${x} ${y} L ${x + 6} ${y - h} M ${x + 34} ${y} L ${x + 40} ${y - h}`} {...line} />
    <path
      d={Array.from({ length: Math.floor(h / 30) }, (_, i) => `M ${x + 1 + (i * 30 * 6) / h} ${y - 15 - i * 30} L ${x + 35 + (i * 30 * 6) / h} ${y - 15 - i * 30}`).join(" ")}
      {...line}
      stroke={DIM}
    />
  </g>
);

export const Coins: React.FC<{ t: number }> = ({ t }) => (
  <g>
    {[0, 1, 2, 3].map((i) => (
      <ellipse key={i} cx={i * 16 - 24} cy={-i * 7 + Math.sin(t * 4 + i) * 2} rx={14} ry={6} fill={BG} stroke={GOLD} strokeWidth={SW} />
    ))}
  </g>
);

export const Chain: React.FC<{ broken?: number }> = ({ broken = 0 }) => (
  <g>
    {Array.from({ length: 7 }, (_, i) => {
      const off = i < 3 ? -broken * 40 : i > 3 ? broken * 40 : 0;
      const fall = i === 3 ? broken * 80 : broken * 20 * Math.abs(i - 3);
      return (
        <ellipse key={i} cx={i * 26 - 78 + off} cy={fall} rx={14} ry={8} fill="none" stroke={INK} strokeWidth={SW} transform={`rotate(${i % 2 ? 90 : 0} ${i * 26 - 78 + off} ${fall})`} opacity={i === 3 ? 1 - broken : 1} />
      );
    })}
  </g>
);

export const QMark: React.FC<{ x: number; y: number; o: number }> = ({ x, y, o }) => (
  <text x={x} y={y} fill={GOLD} opacity={o} fontSize={64} fontWeight={800} fontFamily="Inter, sans-serif" textAnchor="middle">
    ?
  </text>
);

export const Bubble: React.FC<{ x: number; y: number; o: number; children: React.ReactNode; tailX?: number }> = ({ x, y, o, children, tailX = 0 }) => (
  <g transform={`translate(${x},${y}) scale(${0.6 + 0.4 * o})`} opacity={o}>
    <circle cx={tailX * 0.4} cy={120} r={8} fill={BG} stroke={INK} strokeWidth={SW} />
    <circle cx={tailX * 0.2} cy={92} r={13} fill={BG} stroke={INK} strokeWidth={SW} />
    <ellipse cx={0} cy={0} rx={110} ry={80} fill={BG} stroke={INK} strokeWidth={SW} />
    <g transform="translate(0,20)">{children}</g>
  </g>
);

// Gemeinsame Verläufe/Filter
export const Defs: React.FC = () => (
  <defs>
    <radialGradient id="faceGlow">
      <stop offset="0" stopColor="#fff2c8" stopOpacity="0.95" />
      <stop offset="0.45" stopColor={GOLD} stopOpacity="0.45" />
      <stop offset="1" stopColor={GOLD} stopOpacity="0" />
    </radialGradient>
    <radialGradient id="faceGlowCore">
      <stop offset="0" stopColor="#fffaf0" stopOpacity="1" />
      <stop offset="1" stopColor="#ffe6a8" stopOpacity="0.85" />
    </radialGradient>
    <radialGradient id="warmGlow">
      <stop offset="0" stopColor="#ffc46b" stopOpacity="0.55" />
      <stop offset="1" stopColor="#ffc46b" stopOpacity="0" />
    </radialGradient>
    <radialGradient id="moonGlow">
      <stop offset="0" stopColor="#ffe9b0" stopOpacity="0.25" />
      <stop offset="1" stopColor="#ffe9b0" stopOpacity="0" />
    </radialGradient>
    <radialGradient id="sunGlow">
      <stop offset="0" stopColor="#ffd27a" stopOpacity="0.55" />
      <stop offset="1" stopColor="#ff8a3a" stopOpacity="0" />
    </radialGradient>
    <radialGradient id="fireGlow">
      <stop offset="0" stopColor="#ff9a3c" stopOpacity="0.6" />
      <stop offset="1" stopColor="#ff9a3c" stopOpacity="0" />
    </radialGradient>
    <radialGradient id="greenGlow">
      <stop offset="0" stopColor={GREEN} stopOpacity="0.45" />
      <stop offset="1" stopColor={GREEN} stopOpacity="0" />
    </radialGradient>
    <radialGradient id="holyLight">
      <stop offset="0" stopColor="#fffaf0" stopOpacity="1" />
      <stop offset="0.3" stopColor="#ffe6a8" stopOpacity="0.6" />
      <stop offset="1" stopColor={GOLD} stopOpacity="0" />
    </radialGradient>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="3" />
      <feColorMatrix values="0 0 0 0 0.9  0 0 0 0 0.85  0 0 0 0 0.75  0 0 0 0.06 0" />
    </filter>
  </defs>
);
