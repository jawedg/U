// QISSA · „Der erste Adhan“ – Ich-Sicht in 3D (Blender: blender/qissa/adhan.py), Stil wie POV-Kurzfilme:
// großer Frage-Titel oben, Orts-/Zeit-Zeile in Schreibmaschinenschrift, Untertitel in Serifenschrift (2–4 Wörter),
// Erzähler + Dialoge (kursiv), Worte von Sahaba und dem Propheten ﷺ als gesprochenes Zitat (Hall) + goldene Schrift,
// schwarze Zwischentafeln, Auswahltafel ① ② am Ende, Logo. Zeitplan: src/qissa_adhan/timeline.json (scripts/build_qissa_adhan.py).
import React from "react";
import {
  AbsoluteFill,
  Audio,
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
export const QISSA_FPS: number = TL.fps;
export const QISSA_FRAMES: number = TL.frames;
const FPS = QISSA_FPS;
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

// ---------------------------------------------------------------- goldene Zitate (gesprochen mit Hall, Wort für Wort)
const Quote: React.FC<{ t: number }> = ({ t }) => {
  for (const q of TL.quotes) {
    const local = t - q.start;
    const end = q.dur + 0.9;
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
          — {q.by}
        </div>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- Titel am Anfang
const Title: React.FC<{ t: number }> = ({ t }) => {
  const gasse = TL.segments.find((s: any) => s.id === "gasse");
  const end = gasse ? gasse.start : 4.2;
  if (t > end + 0.1) return null;
  const op = interpolate(t, [0, 0.12, end - 0.45, end], [0, 1, 1, 0], clamp);
  const pop = spring({ frame: fr(t), fps: FPS, config: { damping: 14, stiffness: 160 } });
  const pop2 = spring({ frame: fr(t - 0.18), fps: FPS, config: { damping: 11, stiffness: 150 } });
  return (
    <div style={{ position: "absolute", top: 150, left: 40, right: 40, textAlign: "center", opacity: op }}>
      <div style={{ fontFamily: MONO, fontSize: 24, letterSpacing: 6, color: "rgba(255,248,235,0.85)", marginBottom: 22 }}>
        <span style={{ color: GOLD }}>◆</span> QISSA · WAHRE GESCHICHTEN
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
        WOHER KOMMT
      </div>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 108,
          lineHeight: 1.05,
          color: GOLD,
          textShadow: "0 3px 18px rgba(0,0,0,0.75)",
          transform: `scale(${0.85 + 0.15 * pop2})`,
          opacity: pop2,
        }}
      >
        DER ADHAN?
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

// ---------------------------------------------------------------- arabischer Takbir während des Adhan
const Takbir: React.FC<{ t: number }> = ({ t }) => {
  // [Start, Dauer, Höhe]: im Einstieg tiefer (oben steht die Titel-Frage)
  const ts: [number, number, number][] = [
    ...(TL.events.takbir_hook != null ? [[TL.events.takbir_hook, 1.75, 560] as [number, number, number]] : []),
    ...TL.events.takbir.map((x: number) => [x, 3.4, 230] as [number, number, number]),
  ];
  for (const [t0, len, top] of ts) {
    const local = t - (t0 - 0.2);
    if (local < 0 || local > len) continue;
    const op = interpolate(local, [0, 0.3, len - 0.5, len], [0, 1, 1, 0], clamp);
    const sc = interpolate(local, [0, len], [0.96, 1.04], clamp);
    return (
      <div style={{ position: "absolute", top, left: 0, right: 0, textAlign: "center", opacity: op, transform: `scale(${sc})` }}>
        <div
          style={{
            fontFamily: "Amiri, serif",
            fontWeight: 700,
            fontSize: 110,
            direction: "rtl",
            color: GOLD,
            textShadow: "0 0 30px rgba(232,181,77,0.55), 0 3px 12px rgba(0,0,0,0.8)",
          }}
        >
          اللّٰهُ أَكْبَرُ
        </div>
        <div style={{ fontFamily: SERIF, fontStyle: "italic", fontSize: 40, color: "#fbf6ec", textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>
          Allah ist größer
        </div>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- schwarze Tafeln
const Card: React.FC<{ s: any; t: number }> = ({ s, t }) => {
  const local = t - s.start;
  if (s.id === "logo") {
    const op = interpolate(local, [0, 0.4], [0, 1], clamp);
    return (
      <AbsoluteFill style={{ background: "#07080a", alignItems: "center", justifyContent: "center", opacity: op }}>
        <div style={{ fontFamily: "Amiri, serif", fontWeight: 700, fontSize: 70, color: GOLD, opacity: 0.85 }}>قصة</div>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 88, letterSpacing: 22, color: GOLD, marginLeft: 22 }}>QISSA</div>
        <div style={{ fontFamily: MONO, fontSize: 24, letterSpacing: 8, color: "rgba(255,248,235,0.6)", marginTop: 18 }}>
          WAHRE GESCHICHTEN
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

export const QissaAdhanVideo: React.FC = () => {
  const f = useCurrentFrame();
  const t = sec(f);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {TL.segments
        .filter((s: any) => s.kind === "shot")
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
                  src={staticFile(`qissa_adhan/shots/${s.id}.mp4`)}
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
            <OffthreadVideo src={staticFile(`qissa_adhan/shots/${s.src}.mp4`)} muted trimBefore={fr(s.at)} style={shotStyle} />
          </Sequence>
        ))}
      <Grain f={f} />
      <Title t={t} />
      <Label t={t} />
      <Takbir t={t} />
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
      {/* Ton: fertig gemischt (Stimmen, Adhan, Atmo, Effekte, Begrenzer) – scripts/sfx_qissa_adhan.py */}
      <Audio src={staticFile("qissa_adhan/master.wav")} />
    </AbsoluteFill>
  );
};
