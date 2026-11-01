// Die 15 Szenen. Jede Szene: Bild (draw), Ort-Label, arabischer Text, Atmo und Sound-Effekte.
// Zeiten können an gesprochene Wörter gekoppelt werden: w("Glocke") = Sekunde, in der das Wort fällt.
import React from "react";
import {
  BG, Bell, Bubble, Chain, Coins, Crescent, DIM, Dunes, Fire, GOLD, GREEN, Ground, Horn, House, INK,
  Ladder, Mosque, Mountains, Palm, Person, QMark, Rock, Stars, Sun, rand,
} from "./art";

export type WordFn = (needle: string, fallback?: number) => number;
export type SceneProps = { t: number; D: number; w: WordFn };
export type Sfx = { file: string; at: number; gain?: number };
export type SceneDef = {
  label: string;
  arabic?: (p: SceneProps) => { text: string; sub?: string; o: number } | null;
  amb: string;
  ambGain?: number;
  sfx?: (p: SceneProps) => Sfx[];
  whoosh?: boolean;
  draw: React.FC<SceneProps>;
};

const clamp = (x: number) => Math.min(1, Math.max(0, x));
const ease = (x: number) => {
  const c = clamp(x);
  return c * c * (3 - 2 * c);
};
const fade = (t: number, at: number, len = 0.5) => ease((t - at) / len);
const lerp = (a: number, b: number, p: number) => a + (b - a) * clamp(p);

// Kamera: Zoom/Schwenk um die Bildmitte
const Cam: React.FC<{ z?: number; x?: number; y?: number; children: React.ReactNode }> = ({ z = 1, x = 0, y = 0, children }) => (
  <g transform={`translate(${540 + x},${900 + y}) scale(${z}) translate(-540,-900)`}>{children}</g>
);

// Himmel-Verlauf
const Sky: React.FC<{ mode: "night" | "dawn" | "heat" | "dream"; p?: number }> = ({ mode, p = 1 }) => {
  const id = `sky-${mode}`;
  const stops: Record<string, [string, string, string]> = {
    night: ["#05060d", "#0b0f22", "#141a33"],
    dawn: ["#0b0f22", "#3a2c4a", "#c7845a"],
    heat: ["#5a2a14", "#b5602a", "#f1b46a"],
    dream: ["#04120e", "#0b1f1a", "#0b0d16"],
  };
  const [a, b, c] = stops[mode];
  return (
    <g opacity={p}>
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={a} />
          <stop offset="0.55" stopColor={b} />
          <stop offset="1" stopColor={c} />
        </linearGradient>
      </defs>
      <rect x={-600} y={-600} width={2400} height={2400} fill={`url(#${id})`} />
    </g>
  );
};

// Stadt-Silhouette (Häuser + Palmen) links und rechts
const Town: React.FC<{ y: number; seed: number; t: number; dim?: boolean; gapL?: number; gapR?: number; lit?: number }> = ({
  y, seed, t, dim, gapL = 380, gapR = 700, lit = 0.3,
}) => {
  const r = rand(seed);
  const items: React.ReactNode[] = [];
  let x = -260;
  let k = 0;
  while (x < 1340) {
    if (x > gapL && x < gapR) {
      x = gapR;
      continue;
    }
    const w = 110 + r() * 90;
    const h = 90 + r() * 110;
    if (r() < 0.3) items.push(<Palm key={`p${k}`} x={x + w / 2} y={y} h={170 + r() * 90} sway={Math.sin(t * 0.8 + k)} dim={dim} />);
    const litList = r() < lit ? [0] : [];
    items.push(<House key={`h${k}`} x={x} y={y} w={w} h={h} windows={w > 150 ? 2 : 1} lit={litList} dim={dim} />);
    x += w + 10 + r() * 30;
    k++;
  }
  return <g>{items}</g>;
};

// Licht für den Propheten ﷺ (er wird NICHT dargestellt)
const HolyLight: React.FC<{ x: number; y: number; r: number; o: number; t: number }> = ({ x, y, r, o, t }) => (
  <g opacity={o}>
    <circle cx={x} cy={y} r={r * (1 + 0.04 * Math.sin(t * 2))} fill="url(#holyLight)" />
  </g>
);

export const SCENES: Record<string, SceneDef> = {
  hook: {
    label: "DER ERSTE ADHAN",
    arabic: () => ({ text: "الأَذَان", o: 1 }),
    amb: "amb_night",
    draw: ({ t, D }) => (
      <Cam z={lerp(1, 1.1, t / D)} y={lerp(0, -20, t / D)}>
        <Sky mode="night" />
        <Stars t={t} />
        <Crescent x={790} y={720} r={40} />
        <Mountains y={1180} />
        <Ground y={1260} />
        <Town y={1260} seed={4} t={t} gapL={300} gapR={780} lit={0.5} />
        <Mosque x={540} y={1260} s={0.68} lights={0.8} />
        <Palm x={250} y={1260} h={260} sway={Math.sin(t)} />
        <Palm x={850} y={1260} h={230} sway={Math.sin(t + 1)} />
      </Cam>
    ),
  },
  mosque: {
    label: "MEDINA · 622 n. Chr.",
    arabic: () => ({ text: "المَدِينَة", o: 1 }),
    amb: "amb_city",
    sfx: () => [{ file: "footsteps", at: 0.6, gain: 0.5 }],
    draw: ({ t, D }) => (
      <Cam z={lerp(1.0, 1.15, t / D)}>
        <Sky mode="night" />
        <Stars t={t} count={60} maxY={700} />
        <Ground y={1280} />
        <Mosque x={540} y={1280} s={1.3} lights={1} doorGlow={0.6} />
        <Palm x={60} y={1280} h={300} sway={Math.sin(t)} />
        <Palm x={1010} y={1280} h={330} sway={Math.sin(t + 2)} />
        <Person x={lerp(-40, 470, t / D)} y={1300} s={0.75} pose="walk" phase={t * 7} head="turban" />
        <Person x={lerp(1120, 610, (t - 0.8) / D)} y={1305} s={0.75} pose="walk" phase={t * 7 + 1} head="shawl" flip />
        <Person x={lerp(-160, 330, (t - 1.5) / D)} y={1310} s={0.72} pose="walk" phase={t * 7 + 2} head="cap" />
      </Cam>
    ),
  },
  courtyard: {
    label: "WANN IST GEBETSZEIT?",
    amb: "amb_city",
    ambGain: 0.7,
    draw: ({ t, D }) => {
      const sunA = lerp(Math.PI * 0.95, Math.PI * 0.15, t / D);
      return (
        <Cam z={lerp(1.05, 1, t / D)}>
          <Sky mode="dawn" p={0.45} />
          <path d="M 160 900 A 380 220 0 0 1 920 900" fill="none" stroke={DIM} strokeWidth={2} strokeDasharray="4 12" />
          <Sun x={540 + Math.cos(sunA) * 380} y={900 - Math.sin(sunA) * 220} r={24} t={t} />
          <Ground y={1300} />
          {/* Palmsäulen & Dach */}
          <path d="M 0 960 L 1080 960" stroke={INK} strokeWidth={3} />
          <path d={Array.from({ length: 55 }, (_, i) => `M ${i * 20} 960 l 12 -12`).join(" ")} stroke={DIM} strokeWidth={3} />
          {[90, 300, 510, 720, 930].map((x) => (
            <g key={x}>
              <path d={`M ${x} 960 L ${x} 1300`} stroke={INK} strokeWidth={6} />
              <path d={`M ${x} 1300 L ${x - 60 + Math.cos(sunA) * 120} 1300`} stroke="rgba(0,0,0,0.6)" strokeWidth={10} />
            </g>
          ))}
          <Person x={200} y={1330} s={0.85} pose="look" head="turban" />
          <Person x={420} y={1345} s={0.85} head="shawl" flip />
          <Person x={640} y={1335} s={0.85} pose="look" head="cap" flip />
          <Person x={lerp(1150, 860, (t - D * 0.5) / (D * 0.4))} y={1340} s={0.85} pose="walk" phase={t * 7} head="turban" flip />
          <QMark x={215} y={1035} o={fade(t, 0.8)} />
          <QMark x={655} y={1040} o={fade(t, 1.6)} />
          <QMark x={430} y={1060} o={fade(t, 2.6)} />
        </Cam>
      );
    },
  },
  council: {
    label: "DIE BERATUNG",
    amb: "amb_city",
    ambGain: 0.6,
    draw: ({ t, D }) => <Council t={t} D={D} />,
  },
  symbols: {
    label: "GLOCKE? HORN? FEUER?",
    amb: "amb_city",
    ambGain: 0.5,
    sfx: ({ w }) => [
      { file: "bell", at: w("Glocke"), gain: 0.55 },
      { file: "horn", at: w("Horn"), gain: 0.45 },
      { file: "fire", at: w("Feuer"), gain: 0.6 },
    ],
    draw: ({ t, D, w }) => (
      <Council t={t} D={D} zoom={1.08}>
        <Bubble x={250} y={850} o={fade(t, w("Glocke") - 0.15, 0.35)} tailX={-40}>
          <Bell s={1.1} swing={Math.sin(t * 6) * 12 * clamp(1 - (t - w("Glocke")) / 2)} />
        </Bubble>
        <Bubble x={830} y={850} o={fade(t, w("Horn") - 0.15, 0.35)} tailX={40}>
          <Horn s={1.1} />
        </Bubble>
        <Bubble x={540} y={700} o={fade(t, w("Feuer") - 0.15, 0.35)}>
          <g transform="translate(0,25)">
            <Fire s={0.9} t={t} />
          </g>
        </Bubble>
      </Council>
    ),
  },
  house: {
    label: "ABDULLAH IBN ZAID",
    arabic: () => ({ text: "عَبْدُ اللّٰهِ بْنُ زَيْد", o: 1 }),
    amb: "amb_night",
    sfx: ({ D }) => [
      { file: "footsteps", at: 0.2, gain: 0.6 },
      { file: "door", at: D * 0.55, gain: 0.5 },
    ],
    draw: ({ t, D }) => {
      const arrive = D * 0.55;
      return (
        <Cam z={lerp(1, 1.12, t / D)} x={lerp(0, -40, t / D)}>
          <Sky mode="night" />
          <Stars t={t} maxY={800} />
          <Crescent x={250} y={700} r={32} />
          <Ground y={1300} />
          <House x={-60} y={1300} w={260} h={190} lit={[0]} />
          <Palm x={260} y={1300} h={280} sway={Math.sin(t)} />
          <House x={640} y={1300} w={330} h={240} windows={2} lit={t > arrive + 0.8 ? [0, 1] : []} door={t > arrive ? fade(t, arrive, 0.6) * (1 - fade(t, arrive + 1.4, 0.6)) : 0} />
          <Person
            x={lerp(60, 805, t / arrive)}
            y={1320}
            s={0.8}
            pose={t < arrive ? "walk" : "stand"}
            phase={t * 6}
            head="turban"
            glow={1}
            opacity={1 - fade(t, arrive + 0.6, 0.6)}
          />
        </Cam>
      );
    },
  },
  dream: {
    label: "IM TRAUM",
    amb: "amb_dream",
    whoosh: true,
    sfx: ({ w }) => [
      { file: "shimmer", at: 0, gain: 0.5 },
      { file: "bell", at: w("Glocke"), gain: 0.35 },
    ],
    draw: ({ t, D, w }) => <Dream t={t} D={D} bellO={1} gold={0} ring={w("Glocke")} />,
  },
  words: {
    label: "IM TRAUM",
    arabic: ({ t, D }) => ({ text: "اللّٰهُ أَكْبَرُ", sub: "Allahu Akbar", o: fade(t, D * 0.55, 0.8) }),
    amb: "amb_dream",
    sfx: ({ w }) => [{ file: "shimmer", at: w("Worte") - 0.4, gain: 0.6 }],
    draw: ({ t, D }) => <Dream t={t} D={D} bellO={1 - fade(t, D * 0.3, D * 0.2)} gold={fade(t, D * 0.4, D * 0.3)} ring={-10} />,
  },
  morning: {
    label: "AM NÄCHSTEN MORGEN",
    arabic: ({ t, w }) => ({ text: "إِنَّهَا لَرُؤْيَا حَقٌّ", sub: "„Es ist ein wahrer Traum.“ – Abu Dawud 499", o: fade(t, w("wahrer") - 0.6, 0.6) }),
    amb: "amb_dawn",
    whoosh: true,
    sfx: () => [{ file: "footsteps", at: 0.3, gain: 0.5 }],
    draw: ({ t, D, w }) => {
      const bilal = fade(t, w("Bilal") - 0.2, 0.6);
      return (
        <Cam z={lerp(1, 1.1, t / D)}>
          <Sky mode="dawn" p={lerp(0.6, 1, t / D)} />
          <Stars t={t} opacity={lerp(0.6, 0.1, t / D)} maxY={600} />
          <circle cx={300} cy={1270} r={lerp(30, 70, t / D)} fill="url(#sunGlow)" />
          <Ground y={1300} />
          <Town y={1300} seed={9} t={t} gapL={200} gapR={1100} dim />
          <Mosque x={760} y={1300} s={0.9} doorGlow={1} />
          <HolyLight x={760} y={1225} r={110} o={0.9} t={t} />
          <Person x={lerp(80, 560, t / (D * 0.5))} y={1320} s={0.8} pose={t < D * 0.5 ? "walk" : "stand"} phase={t * 6} head="turban" glow={1} />
          <Person x={950} y={1320} s={0.85} head="cap" glow={bilal} opacity={bilal} flip />
        </Cam>
      );
    },
  },
  desert: {
    label: "MEKKA · BILAL",
    arabic: ({ t, w }) => ({ text: "أَحَدٌ  أَحَدٌ", sub: "„Einer, Einer“", o: fade(t, w("Ahad") - 0.2, 0.4) }),
    amb: "amb_desert",
    whoosh: true,
    sfx: ({ w }) => [
      { file: "heat", at: 0, gain: 0.5 },
      { file: "thud", at: w("Felsen") - 0.1, gain: 0.8 },
    ],
    draw: ({ t, D, w }) => {
      const rockIn = fade(t, w("Felsen") - 0.4, 0.4);
      return (
        <Cam z={lerp(1, 1.12, t / D)} y={lerp(0, -30, t / D)}>
          <Sky mode="heat" />
          <Sun x={540} y={780} r={80} t={t} />
          {Array.from({ length: 7 }, (_, i) => (
            <path
              key={i}
              d={`M ${120 + i * 140} 1180 q 15 -25 0 -50 q -15 -25 0 -50`}
              fill="none"
              stroke="rgba(255,220,160,0.35)"
              strokeWidth={3}
              transform={`translate(0,${-((t * 60 + i * 37) % 140)})`}
            />
          ))}
          <Dunes y={1200} seed={5} color="rgba(60,25,10,0.6)" />
          <Ground y={1300} />
          <Person x={560} y={1310} s={1} pose="lie" glow={1} />
          <g transform={`translate(${520},${1288 - (1 - rockIn) * 300})`} opacity={rockIn}>
            <Rock s={1.15} />
          </g>
          <Person x={860} y={1320} s={0.95} head="turban" flip />
          <path d="M 812 1205 L 760 1150" stroke={INK} strokeWidth={4} strokeLinecap="round" />
        </Cam>
      );
    },
  },
  rooftop: {
    label: "BILAL IBN RABAH",
    arabic: () => ({ text: "بِلَال", o: 1 }),
    amb: "amb_night",
    sfx: ({ w }) => [
      { file: "coins", at: w("kaufte") - 0.1, gain: 0.6 },
      { file: "chains", at: w("frei") - 0.1, gain: 0.6 },
      { file: "footsteps", at: w("stieg"), gain: 0.4 },
    ],
    draw: ({ t, D, w }) => {
      const partB = fade(t, w("Und") - 0.3, 0.5);
      const broken = fade(t, w("frei") - 0.1, 0.5);
      const climb = clamp((t - w("stieg")) / 2.6);
      return (
        <g>
          <g opacity={1 - partB}>
            <Sky mode="night" />
            <Stars t={t} maxY={700} />
            <Ground y={1300} />
            <Person x={540} y={1320} s={1.1} head="cap" glow={1} />
            <g transform="translate(540,1150)">
              <Chain broken={broken} />
            </g>
            <g transform={`translate(380,${lerp(700, 1080, (t - w("kaufte") + 0.3) / 0.6)})`} opacity={fade(t, w("kaufte") - 0.3, 0.3)}>
              <Coins t={t} />
            </g>
            <Person x={260} y={1320} s={0.95} pose="offer" head="turban" glow={1} />
          </g>
          <g opacity={partB}>
            <Cam z={lerp(1, 1.15, (t - w("Und")) / 4)} y={lerp(0, 60, climb)}>
              <Sky mode="dawn" p={0.4} />
              <Stars t={t} maxY={700} />
              <Ground y={1350} />
              <Town y={1350} seed={13} t={t} gapL={300} gapR={760} dim />
              <House x={360} y={1350} w={340} h={520} windows={2} />
              <Ladder x={300} y={1350} h={525} />
              <Person x={lerp(318, 360, clamp(climb * 1.4 - 0.4))} y={lerp(1350, 830, climb)} s={0.8} pose={climb < 0.98 ? "climb" : "stand"} phase={t * 8} head="cap" glow={1} />
            </Cam>
          </g>
        </g>
      );
    },
  },
  athan: {
    label: "DER ERSTE ADHAN",
    arabic: ({ t }) => ({ text: "اللّٰهُ أَكْبَرُ  اللّٰهُ أَكْبَرُ", sub: "Allahu Akbar · Allah ist der Größte", o: fade(t, 0.8, 0.8) }),
    amb: "amb_dawn",
    ambGain: 0.5,
    draw: ({ t, D }) => (
      <Cam z={lerp(1.15, 0.95, t / D)} y={lerp(40, 0, t / D)}>
        <Sky mode="dawn" p={lerp(0.5, 1, t / D)} />
        <Stars t={t} opacity={lerp(0.8, 0.1, t / D)} maxY={650} />
        {Array.from({ length: 6 }, (_, i) => {
          const age = (t * 0.9 + i * 1.5) % 9;
          const r = 40 + age * 95;
          return (
            <circle key={i} cx={530} cy={810} r={r} fill="none" stroke={GOLD} strokeWidth={3} opacity={clamp(t / 1) * clamp(1 - age / 9) * 0.8} />
          );
        })}
        <Ground y={1350} />
        <Town y={1350} seed={13} t={t} gapL={300} gapR={760} lit={0.6} />
        <House x={360} y={1350} w={340} h={520} windows={2} lit={[0, 1]} />
        <Person x={530} y={830} s={0.8} pose="ears" head="cap" glow={1} />
        {[150, 860, 960].map((x, i) => (
          <Person key={x} x={x} y={1370} s={0.6} head={i % 2 ? "shawl" : "turban"} pose="look" flip={x > 540} opacity={fade(t, 4 + i * 1.5, 1)} />
        ))}
      </Cam>
    ),
  },
  umar: {
    label: "UMAR IBN AL-KHATTAB",
    arabic: () => ({ text: "عُمَر", o: 1 }),
    amb: "amb_dawn",
    sfx: () => [
      { file: "door", at: 0.15, gain: 0.6 },
      { file: "rush", at: 0.6, gain: 0.7 },
    ],
    draw: ({ t, D }) => {
      const run = clamp((t - 0.7) / (D * 0.45));
      return (
        <Cam z={lerp(1.08, 1, t / D)}>
          <Sky mode="dawn" p={0.85} />
          <Ground y={1320} />
          <Town y={1320} seed={21} t={t} gapL={120} gapR={1180} dim />
          <House x={60} y={1320} w={360} h={260} windows={1} door={fade(t, 0.2, 0.4)} />
          <Person
            x={lerp(240, 760, run)}
            y={1340}
            s={0.9}
            pose={run > 0 && run < 1 ? "run" : "stand"}
            phase={t * 12}
            head="turban"
            glow={1}
            cloak={run > 0 ? 1 : 0}
            opacity={fade(t, 0.5, 0.3)}
          />
        </Cam>
      );
    },
  },
  globe: {
    label: "BIS HEUTE",
    arabic: () => ({ text: "حَيَّ عَلَى الصَّلَاة", sub: "Kommt zum Gebet", o: 1 }),
    amb: "amb_night",
    ambGain: 0.6,
    whoosh: true,
    draw: ({ t, D }) => <Globe t={t} D={D} />,
  },
  outro: {
    label: "",
    amb: "amb_night",
    draw: ({ t }) => (
      <g>
        <Sky mode="night" />
        <Stars t={t} />
        <Crescent x={540} y={760} r={80} />
        <Ground y={1250} />
        <Mosque x={540} y={1250} s={0.9} lights={1} />
        <Palm x={140} y={1250} h={300} sway={Math.sin(t)} />
        <Palm x={940} y={1250} h={280} sway={Math.sin(t + 1)} />
      </g>
    ),
  },
};

// ---------- zusammengesetzte Szenen ----------
const Council: React.FC<{ t: number; D: number; zoom?: number; children?: React.ReactNode }> = ({ t, D, zoom = 1, children }) => (
  <Cam z={lerp(zoom, zoom + 0.05, t / D)}>
    <Sky mode="night" />
    <Stars t={t} count={40} maxY={600} />
    <path d="M -100 1000 L 1180 1000" stroke={INK} strokeWidth={3} />
    <path d={Array.from({ length: 70 }, (_, i) => `M ${-100 + i * 20} 1000 l 12 -12`).join(" ")} stroke={DIM} strokeWidth={3} />
    {[80, 330, 750, 1000].map((x) => (
      <path key={x} d={`M ${x} 1000 L ${x} 1300`} stroke={INK} strokeWidth={6} />
    ))}
    {[200, 540, 880].map((x) => (
      <circle key={x} cx={x} cy={1040} r={50} fill="url(#warmGlow)" opacity={0.8 + 0.2 * Math.sin(t * 6 + x)} />
    ))}
    <Ground y={1300} />
    <HolyLight x={540} y={1200} r={120} o={0.95} t={t} />
    <Person x={230} y={1330} s={0.8} pose="sit" head="turban" />
    <Person x={380} y={1350} s={0.8} pose="sit" head="shawl" />
    <Person x={700} y={1350} s={0.8} pose="sit" head="cap" flip />
    <Person x={850} y={1330} s={0.8} pose="sit" head="turban" flip />
    <Person x={130} y={1380} s={0.85} pose="sit" head="cap" />
    <Person x={950} y={1380} s={0.85} pose="sit" head="shawl" flip />
    {children}
  </Cam>
);

const Dream: React.FC<{ t: number; D: number; bellO: number; gold: number; ring: number }> = ({ t, D, bellO, gold, ring }) => {
  const r = rand(5);
  const letters = ["ا", "ل", "ه", "أ", "ك", "ب", "ر", "ش", "د", "ح", "ي", "ص", "ة", "ف"];
  return (
    <Cam z={lerp(1, 1.08, t / D)}>
      <Sky mode="dream" />
      <Stars t={t} count={120} maxY={1900} opacity={0.7} />
      {/* Traumwolken-Rahmen */}
      {Array.from({ length: 14 }, (_, i) => {
        const a = (i / 14) * Math.PI * 2 + t * 0.05;
        return <circle key={i} cx={540 + Math.cos(a) * 470} cy={1000 + Math.sin(a) * 620} r={130} fill="none" stroke={DIM} strokeWidth={2} />;
      })}
      <circle cx={680} cy={1080} r={260} fill="url(#greenGlow)" opacity={1 - gold * 0.6} />
      <circle cx={680} cy={1060} r={80 + 420 * gold} fill="url(#holyLight)" opacity={gold} />
      <Ground y={1300} dim />
      {/* Mann in grüner Kleidung (ohne Gesicht) */}
      <Person x={700} y={1300} s={1.05} pose={bellO > 0.05 ? "offer" : "stand"} head="shawl" color={GREEN} flip
        holding={<g opacity={bellO}><Bell s={0.7} swing={t > ring && t < ring + 2 ? Math.sin((t - ring) * 10) * 20 * (1 - (t - ring) / 2) : Math.sin(t * 1.5) * 4} /></g>} />
      {/* Abdullah */}
      <Person x={310} y={1300} s={1.05} head="turban" glow={1} pose={gold > 0.3 ? "look" : "stand"} />
      {/* goldene Buchstaben fliegen zu Abdullah */}
      {gold > 0
        ? letters.map((L, i) => {
            const p = ((t * 0.35 + r()) % 1);
            const x = lerp(640, 330, p);
            const y = lerp(1060, 1110, p) + Math.sin(p * Math.PI * 2 + i) * 60 - 40;
            return (
              <text key={i} x={x} y={y} fill={GOLD} fontSize={40 + r() * 20} fontFamily="Amiri, serif" opacity={gold * Math.sin(p * Math.PI)} textAnchor="middle">
                {L}
              </text>
            );
          })
        : null}
    </Cam>
  );
};

const Globe: React.FC<{ t: number; D: number }> = ({ t, D }) => {
  const R = 250;
  const cx = 540;
  const cy = 1030;
  const rot = t * 0.5;
  const r = rand(17);
  const pins = Array.from({ length: 22 }, () => ({ lat: (r() - 0.4) * 1.6, lon: r() * Math.PI * 2, at: r() * D * 0.8 }));
  return (
    <Cam z={lerp(0.92, 1.05, t / D)}>
      <Sky mode="night" />
      <Stars t={t} count={120} maxY={1900} />
      <circle cx={cx} cy={cy} r={R + 60} fill="url(#moonGlow)" />
      <circle cx={cx} cy={cy} r={R} fill={BG} stroke={INK} strokeWidth={3} />
      {Array.from({ length: 6 }, (_, i) => {
        const ph = rot + (i / 6) * Math.PI;
        const rx = Math.abs(Math.cos(ph)) * R;
        return <ellipse key={`m${i}`} cx={cx} cy={cy} rx={rx} ry={R} fill="none" stroke={DIM} strokeWidth={2} />;
      })}
      {[-0.6, -0.3, 0, 0.3, 0.6].map((l) => (
        <ellipse key={l} cx={cx} cy={cy + Math.sin(l) * R} rx={Math.cos(l) * R} ry={Math.cos(l) * R * 0.12} fill="none" stroke={DIM} strokeWidth={2} />
      ))}
      {pins.map((p, i) => {
        const lon = p.lon + rot;
        const z = Math.cos(p.lat) * Math.cos(lon);
        if (z < 0.05) return null;
        const x = cx + Math.cos(p.lat) * Math.sin(lon) * R;
        const y = cy - Math.sin(p.lat) * R;
        const o = fade(t, p.at, 0.4) * z;
        return (
          <g key={i} opacity={o} transform={`translate(${x},${y})`}>
            <circle r={26} fill="url(#warmGlow)" />
            <path d="M 0 -26 L 0 -6 M -5 -6 L 5 -6 L 4 4 L -4 4 Z" stroke={GOLD} strokeWidth={2.5} fill={BG} />
            <circle cy={-30} r={3} fill={GOLD} />
          </g>
        );
      })}
    </Cam>
  );
};
