// QISSAH Folge 5 · „Die Hidschra – der Jäger in der Wüste“ – Ich-Sicht in 3D (Blender: blender/qissa/hijra.py), gleicher Stil wie Folge 1–3
// (src/qissa_adhan/QissaAdhan.tsx):
// großer Frage-Titel oben, Orts-/Zeit-Zeile in Schreibmaschinenschrift, Untertitel in Serifenschrift (2–4 Wörter),
// Erzähler + Dialoge (kursiv), Worte von Sahaba und dem Propheten ﷺ als gesprochenes Zitat (Hall) + goldene Schrift,
// Logo am Ende. Zeitplan: src/qissa_hijra/timeline.json (scripts/build_qissa_hijra.py).
import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
} from "remotion";
import TLj from "./timeline.json";

const TL = TLj as any;
export const HIJRA_FPS: number = TL.fps;
export const HIJRA_FRAMES: number = TL.frames;
const FPS = HIJRA_FPS;
const GOLD = "#e8b54d";
const SERIF = "'EB Garamond', 'Liberation Serif', serif";
const MONO = "'JetBrains Mono', monospace";
const SANS = "'Inter Display', Inter, sans-serif";

// ---------------------------------------------------------------- Schriften (lokal, OFL)
const FONTS: [string, string, string, string][] = [
  ["EB Garamond", "fonts/eb-garamond-latin-500-normal.woff2", "500", "normal"],
  ["EB Garamond", "fonts/eb-garamond-latin-ext-500-normal.woff2", "500", "normal"],
  ["EB Garamond", "fonts/eb-garamond-latin-500-italic.woff2", "500", "italic"],
  ["EB Garamond", "fonts/eb-garamond-latin-600-normal.woff2", "600", "normal"],
  ["Amiri", "fonts/amiri-arabic-700-normal.woff2", "700", "normal"],
];
if (typeof document !== "undefined" && typeof FontFace !== "undefined") {
  const h = delayRender("Schriften laden");
  Promise.all(
    FONTS.map(([fam, file, weight, style]) =>
      new FontFace(fam, `url(${staticFile(file)})`, { weight, style }).load().then((f) => (document as any).fonts.add(f)),
    ),
  )
    .then(() => continueRender(h))
    .catch(() => continueRender(h));
}

const sec = (f: number) => f / FPS;
const fr = (s: number) => Math.round(s * FPS);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// *Wort* = Schlüsselwort (gold)
const Words: React.FC<{ text: string }> = ({ text }) => {
  const parts = text.split(/(\*[^*]+\*)/g).filter(Boolean);
  return (
    <>
      {parts.map((p, i) =>
        p.startsWith("*") ? (
          <span key={i} style={{ color: GOLD }}>
            {p.slice(1, -1)}
          </span>
        ) : (
          <span key={i}>{p}</span>
        ),
      )}
    </>
  );
};

// ---------------------------------------------------------------- Untertitel (gesprochene Sätze)
const Subtitle: React.FC<{ t: number }> = ({ t }) => {
  for (const ln of TL.lines) {
    if (ln.quote) continue;
    const local = t - ln.start;
    if (local < -0.05 || local > ln.dur + 0.15) continue;
    const words: { word: string; start: number }[] = ln.words;
    const chunks: { s: number; ws: string[] }[] = [];
    let cur: string[] = [];
    let s0 = 0;
    words.forEach((w, i) => {
      if (!cur.length) s0 = w.start;
      cur.push(w.word);
      if (cur.length >= 4 || /[.!?,:]\*?$/.test(w.word) || i === words.length - 1) {
        chunks.push({ s: s0, ws: cur });
        cur = [];
      }
    });
    const c = [...chunks].reverse().find((k) => local >= k.s - 0.08);
    if (!c) return null;
    const op = interpolate(local, [c.s - 0.08, c.s + 0.04], [0, 1], clamp);
    let text = c.ws.join(" ");
    // offene *…* über Wortgrenzen schließen
    if ((text.match(/\*/g) || []).length % 2 === 1) text = text.endsWith("*") ? "*" + text : text + "*";
    return (
      <div style={{ position: "absolute", left: 70, right: 70, top: 1130, textAlign: "center", opacity: op }}>
        <span
          style={{
            fontFamily: SERIF,
            fontWeight: 500,
            fontSize: 64,
            lineHeight: 1.2,
            color: ln.dialog ? "#f6ead2" : "#fbf6ec",
            fontStyle: ln.dialog ? "italic" : "normal",
            textShadow: "0 2px 10px rgba(0,0,0,0.85), 0 0 3px rgba(0,0,0,0.9)",
          }}
        >
          <Words text={ln.dialog ? `„${text}“` : text} />
        </span>
      </div>
    );
  }
  return null;
};

// ﷺ (Segenswunsch) immer in Amiri setzen – andere Schriften haben das Zeichen nicht, es sah im Video anders aus
const Salawat: React.FC<{ text: string }> = ({ text }) => (
  <>
    {text.split("ﷺ").map((part, i, arr) => (
      <React.Fragment key={i}>
        {part}
        {i < arr.length - 1 ? (
          <span style={{ fontFamily: "Amiri, serif", fontWeight: 700, fontSize: "1.9em", letterSpacing: 0, verticalAlign: "-0.28em",
            color: GOLD, textTransform: "none", margin: "0 0.15em" }}>
            ﷺ
          </span>
        ) : null}
      </React.Fragment>
    ))}
  </>
);

// ---------------------------------------------------------------- goldene Zitate (gesprochen mit Hall, Wort für Wort)
const Quote: React.FC<{ t: number }> = ({ t }) => {
  for (const q of TL.quotes) {
    const local = t - q.start;
    // ausblenden, bevor der nächste Satz (Untertitel) kommt – sonst überlappen Zitat und Untertitel
    const next = Math.min(...TL.lines.filter((l: any) => l.start > q.start + 0.1).map((l: any) => l.start), Infinity);
    const end = Math.min(q.dur + 0.9, next - q.start - 0.02);
    if (local < -0.1 || local > end) continue;
    const timed: { word: string; start: number }[] = q.words ?? [];
    const words: string[] = timed.length ? timed.map((w) => w.word) : q.text.split(" ");
    const reveal = timed.length
      ? Math.max(1, timed.filter((w) => local >= w.start - 0.05).length)
      : Math.max(1, Math.min(words.length, Math.ceil((local / Math.max(0.6, q.dur * 0.55)) * words.length)));
    const op = interpolate(local, [-0.1, 0.2, end - 0.4, end], [0, 1, 1, 0], clamp);
    return (
      <div style={{ position: "absolute", left: 0, right: 0, top: 900, textAlign: "center", opacity: op }}>
        <div
          style={{
            position: "absolute",
            left: -100,
            right: -100,
            top: -120,
            bottom: -120,
            background: "radial-gradient(ellipse at 50% 50%, rgba(8,6,4,0.62) 0%, rgba(8,6,4,0.35) 45%, rgba(8,6,4,0) 72%)",
          }}
        />
        <div
          style={{
            position: "relative",
            margin: "0 80px",
            fontFamily: SERIF,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 62,
            lineHeight: 1.22,
            color: GOLD,
            textShadow: "0 2px 12px rgba(0,0,0,0.9), 0 0 24px rgba(232,181,77,0.35)",
          }}
        >
          {words.map((w, i) => (
            <span key={i} style={{ opacity: i < reveal ? 1 : 0.12 }}>
              {(i === 0 ? "„" : "") + w + (i === words.length - 1 ? "“" : " ")}
            </span>
          ))}
        </div>
        <div
          style={{
            position: "relative",
            marginTop: 26,
            fontFamily: MONO,
            fontSize: 25,
            letterSpacing: 3,
            color: "rgba(255,248,235,0.75)",
            textShadow: "0 1px 6px rgba(0,0,0,0.9)",
            textTransform: "uppercase",
          }}
        >
          — <Salawat text={q.by} />
        </div>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- Titel am Anfang
const Title: React.FC<{ t: number }> = ({ t }) => {
  const first = TL.segments.find((s: any) => s.id === "mekka");
  const end = first ? first.start : 4.2;
  if (t > end + 0.1) return null;
  const op = interpolate(t, [0, 0.12, end - 0.45, end], [0, 1, 1, 0], clamp);
  const pop = spring({ frame: fr(t), fps: FPS, config: { damping: 14, stiffness: 160 } });
  const pop2 = spring({ frame: fr(t - 0.18), fps: FPS, config: { damping: 11, stiffness: 150 } });
  return (
    <div style={{ position: "absolute", top: 150, left: 40, right: 40, textAlign: "center", opacity: op }}>
      <div style={{ fontFamily: MONO, fontSize: 24, letterSpacing: 6, color: "rgba(255,248,235,0.85)", marginBottom: 22 }}>
        <span style={{ color: GOLD }}>◆</span> QISSAH · WAHRE GESCHICHTEN
      </div>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 600,
          fontSize: 62,
          letterSpacing: 1,
          color: "#fbf6ec",
          textShadow: "0 2px 14px rgba(0,0,0,0.8)",
          transform: `translateY(${(1 - pop) * 24}px)`,
          opacity: pop,
        }}
      >
        WER JAGTE
      </div>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 84,
          lineHeight: 1.05,
          whiteSpace: "nowrap",
          color: GOLD,
          textShadow: "0 3px 18px rgba(0,0,0,0.75)",
          transform: `scale(${0.85 + 0.15 * pop2})`,
          opacity: pop2,
        }}
      >
        DEN PROPHETEN{" "}
        <span style={{ fontFamily: "Amiri, serif", fontWeight: 700, fontSize: "1.05em", verticalAlign: "-0.12em" }}>ﷺ</span>?
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- Ort/Zeit-Zeile (tippt sich)
const Label: React.FC<{ t: number }> = ({ t }) => {
  for (const s of TL.segments) {
    if (s.kind !== "shot" || !s.label) continue;
    const t0 = s.start + 0.3;
    const local = t - t0;
    if (local < 0 || local > 3.6) continue;
    const n = Math.floor(local / 0.05);
    const txt = s.label.slice(0, n);
    const op = interpolate(local, [3.0, 3.6], [1, 0], clamp);
    return (
      <div
        style={{
          position: "absolute",
          top: 190,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: MONO,
          fontSize: 30,
          letterSpacing: 5,
          color: "#fbf6ec",
          opacity: op,
          textShadow: "0 1px 8px rgba(0,0,0,0.9)",
        }}
      >
        {txt}
        <span style={{ opacity: Math.floor(local * 3) % 2 ? 0 : 1 }}>▍</span>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- Zähler: siebenmal zwischen Safa und Marwa
const Counter: React.FC<{ t: number }> = ({ t }) => {
  const cs: [number, number][] = TL.events.count ?? [];
  if (!cs.length) return null;
  const t0 = cs[0][0] - 0.2;
  const t1 = cs[cs.length - 1][0] + 1.6;
  if (t < t0 || t > t1) return null;
  let k = 0;
  cs.forEach(([tc], i) => {
    if (t >= tc - 0.05) k = i;
  });
  const [tc, n] = cs[k];
  const pop = spring({ frame: fr(t - tc + 0.05), fps: FPS, config: { damping: 12, stiffness: 220 } });
  const op = interpolate(t, [t0, t0 + 0.2, t1 - 0.4, t1], [0, 1, 1, 0], clamp);
  const seven = n === 7;
  return (
    <div style={{ position: "absolute", top: 170, left: 0, right: 0, textAlign: "center", opacity: op }}>
      <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 6, color: "rgba(255,248,235,0.85)", textShadow: "0 1px 8px rgba(0,0,0,0.9)" }}>
        SAFA ⇄ MARWA
      </div>
      <div style={{ marginTop: 6, display: "inline-flex", alignItems: "baseline", gap: 14 }}>
        <span
          style={{
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: seven ? 190 : 150,
            lineHeight: 1,
            color: seven ? "#fff3d6" : GOLD,
            transform: `scale(${0.7 + 0.3 * pop})`,
            display: "inline-block",
            textShadow: seven
              ? "0 0 40px rgba(255,220,150,0.8), 0 3px 18px rgba(0,0,0,0.75)"
              : "0 3px 18px rgba(0,0,0,0.75)",
          }}
        >
          {n}
        </span>
        <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 44, color: "rgba(255,248,235,0.8)", textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>
          / 7
        </span>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- schwarze Tafeln
const Card: React.FC<{ s: any; t: number }> = ({ s, t }) => {
  const local = t - s.start;
  if (s.id === "logo") {
    // Kanal-Logo QISSAH (wie Folge 1): Gold-Doppelring zeichnet sich ein, das Q (wie im Profilbild-Entwurf) leuchtet auf,
    // darunter QISSAH + kleines arabisches Wort + „Wahre Geschichten“.
    const ease = (a: number, b: number) => interpolate(local, [a, b], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
    const ring = ease(0.05, 0.95);
    const q = spring({ frame: fr(local - 0.3), fps: FPS, config: { damping: 16, stiffness: 120 } });
    const name = ease(0.75, 1.25);
    const tag = ease(1.05, 1.6);
    const glow = 0.45 + 0.25 * Math.sin(Math.min(1, local / 2.4) * Math.PI);
    const R1 = 330, R2 = 312, C1 = 2 * Math.PI * R1, C2 = 2 * Math.PI * R2;
    return (
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 44%, #16120b 0%, #07080a 58%)", opacity: interpolate(local, [0, 0.25], [0, 1], clamp) }}>
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          <defs>
            <filter id="logoNeon" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="7" result="b1" />
              <feGaussianBlur in="SourceGraphic" stdDeviation="18" result="b2" />
              <feMerge><feMergeNode in="b2" /><feMergeNode in="b1" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>
          <g transform="rotate(-90 540 820)" fill="none" filter="url(#logoNeon)">
            <circle cx={540} cy={820} r={R1} stroke="#e9a93a" strokeWidth={9} strokeDasharray={C1} strokeDashoffset={C1 * (1 - ring)} />
            <circle cx={540} cy={820} r={R2} stroke="#e9a93a" strokeWidth={6} strokeDasharray={C2} strokeDashoffset={C2 * (1 - ring)} />
          </g>
          <g transform="rotate(-90 540 820)" fill="none">
            <circle cx={540} cy={820} r={R1} stroke="#fff0c2" strokeWidth={3} strokeDasharray={C1} strokeDashoffset={C1 * (1 - ring)} />
            <circle cx={540} cy={820} r={R2} stroke="#fff0c2" strokeWidth={2} strokeDasharray={C2} strokeDashoffset={C2 * (1 - ring)} />
          </g>
        </svg>
        <div style={{ position: "absolute", left: 0, right: 0, top: 560, textAlign: "center", lineHeight: 1,
                      fontFamily: SERIF, fontWeight: 600, fontSize: 400, color: GOLD, paddingLeft: 22,
                      opacity: Math.min(1, q * 1.4), transform: `scale(${0.86 + 0.14 * q})`,
                      filter: `drop-shadow(0 0 ${18 * glow}px rgba(232,181,77,${glow})) drop-shadow(0 0 50px rgba(232,181,77,0.18))` }}>Q</div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 1215, textAlign: "center", opacity: name,
                      transform: `translateY(${(1 - name) * 18}px)` }}>
          <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 84, letterSpacing: 24 + (1 - name) * 14, paddingLeft: 24, color: GOLD,
                        filter: "drop-shadow(0 0 10px rgba(232,181,77,0.45))" }}>QISSAH</div>
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, top: 1335, textAlign: "center", opacity: tag }}>
          <div style={{ fontFamily: "Amiri, serif", fontWeight: 700, fontSize: 56, color: GOLD, opacity: 0.85 }}>قصة</div>
          <div style={{ fontFamily: MONO, fontSize: 26, letterSpacing: 9, paddingLeft: 9, color: "rgba(255,248,235,0.65)", marginTop: 10 }}>
            WAHRE GESCHICHTEN
          </div>
        </div>
      </AbsoluteFill>
    );
  }
  const n = Math.floor((local - 0.15) / 0.055);
  return (
    <AbsoluteFill style={{ background: "#050506", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 44, letterSpacing: 8, color: "#fbf6ec" }}>
        {s.text.slice(0, Math.max(0, n))}
        <span style={{ opacity: Math.floor(local * 3) % 2 ? 0 : 1 }}>▍</span>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- Auswahltafel
const Choice: React.FC<{ t: number }> = ({ t }) => {
  const c = TL.choice;
  if (!c) return null;
  const local = t - c.start;
  if (local < 0 || local > c.dur + 0.1) return null;
  const p1 = spring({ frame: fr(local), fps: FPS, config: { damping: 13, stiffness: 170 } });
  const p2 = spring({ frame: fr(local - 0.25), fps: FPS, config: { damping: 13, stiffness: 170 } });
  const box = (n: string, label: string, gold: boolean, p: number) => (
    <div style={{ position: "relative", transform: `scale(${0.6 + 0.4 * p})`, opacity: p }}>
      <div
        style={{
          position: "absolute",
          top: -26,
          left: "50%",
          transform: "translateX(-50%)",
          width: 52,
          height: 52,
          borderRadius: 26,
          background: gold ? GOLD : "#fbf6ec",
          color: "#111",
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 30,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {n}
      </div>
      <div
        style={{
          width: 330,
          height: 170,
          borderRadius: 26,
          border: `5px solid ${gold ? GOLD : "#fbf6ec"}`,
          background: "rgba(10,10,12,0.82)",
          color: gold ? GOLD : "#fbf6ec",
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 56,
          letterSpacing: 2,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {label}
      </div>
    </div>
  );
  return (
    <div style={{ position: "absolute", top: 210, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 78,
          color: "#fbf6ec",
          letterSpacing: 1,
          textShadow: "0 3px 16px rgba(0,0,0,0.85)",
          opacity: p1,
          marginBottom: 64,
        }}
      >
        {c.q}
      </div>
      <div style={{ display: "flex", gap: 46 }}>
        {box("1", c.a, false, p1)}
        {box("2", c.b, true, p2)}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- Vignette (kein Filmkorn: Rauschen wird beim Verkleinern zu Klötzchen)
const Grain: React.FC<{ f: number }> = () => (
  <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.5) 100%)" }} />
);

// ---------------------------------------------------------------- Video
const shotStyle = { width: 1080, height: 1920, filter: "saturate(1.14) contrast(1.06) brightness(1.03)" };

export const QissaHijraVideo: React.FC = () => {
  const f = useCurrentFrame();
  const t = sec(f);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {TL.segments
        .filter((s: any) => s.kind === "shot" && !s.hidden)
        .flatMap((s: any) => {
          // Zeit-Anker: zwischen zwei Ankern konstantes Tempo, an den Ankern stimmt das Bild genau (build_qissa_adhan.py)
          const m: [number, number][] = s.map ?? [[0, 0], [s.dur, s.dur]];
          const last = fr(s.src_dur ?? s.dur) - 1;
          return m.slice(0, -1).map(([a0, b0], i) => {
            const [a1, b1] = m[i + 1];
            const from = fr(s.start + a0);
            const dur = fr(s.start + a1) - from;
            if (dur <= 0) return null;
            const rate = (b1 - b0) / (a1 - a0);
            return (
              <Sequence key={`${s.id}-${i}`} from={from} durationInFrames={dur}>
                <OffthreadVideo
                  src={staticFile(`qissa_hijra/shots/${s.id}.mp4`)}
                  muted
                  trimBefore={Math.min(last, Math.round(b0 * FPS))}
                  playbackRate={Math.abs(rate - 1) < 0.002 ? 1 : rate}
                  style={shotStyle}
                />
              </Sequence>
            );
          });
        })}
      {/* Einstieg: kurze Ausschnitte aus späteren Einstellungen */}
      {TL.segments
        .filter((s: any) => s.kind === "clip")
        .map((s: any) => (
          <Sequence key={s.id} from={fr(s.start)} durationInFrames={fr(s.start + s.dur) - fr(s.start)}>
            <OffthreadVideo src={staticFile(`qissa_hijra/shots/${s.src}.mp4`)} muted trimBefore={fr(s.at)} style={shotStyle} />
          </Sequence>
        ))}
      <Grain f={f} />
      <Title t={t} />
      <Label t={t} />
      <Counter t={t} />
      <Quote t={t} />
      <Subtitle t={t} />
      <Choice t={t} />
      {TL.segments
        .filter((s: any) => s.kind === "card")
        .map((s: any) => (
          <Sequence key={s.id} from={fr(s.start)} durationInFrames={fr(s.dur)}>
            <Card s={s} t={t} />
          </Sequence>
        ))}
      {/* Ton: fertig gemischt (Stimmen, Atmo, Effekte, Begrenzer) – scripts/sfx_qissa_hijra.py */}
      <Audio src={staticFile("qissa_hijra/master.wav")} />
    </AbsoluteFill>
  );
};
