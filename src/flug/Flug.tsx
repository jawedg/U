// POV-Erinnerung „Was, wenn das dein letzter Flug ist?“ – Ich-Sicht in 3D (Blender: blender/qissa/flug.py), gleicher Stil wie QISSAH
// (src/qissa_hijra/QissaHijra.tsx), aber OHNE QISSAH-Logo (Nutzer): großer Frage-Titel, Ort/Zeit-Zeile in Schreibmaschinenschrift,
// Untertitel in Serifenschrift, Dialoge kursiv, Worte des Propheten ﷺ als Zitat (Hall + goldene Schrift),
// Koran als ECHTE Rezitation (Maher al-Muaiqly) mit arabischer Schrift in Gold (Wort für Wort) + deutscher Übersetzung.
// Zeitplan: src/flug/timeline.json (scripts/build_flug.py).
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
export const FLUG_FPS: number = TL.fps;
export const FLUG_FRAMES: number = TL.frames;
const FPS = FLUG_FPS;
const GOLD = "#e8b54d";
const SERIF = "'EB Garamond', 'Liberation Serif', serif";
const MONO = "'JetBrains Mono', monospace";
const SANS = "'Inter Display', Inter, sans-serif";
const ARAB = "Amiri, 'Noto Naskh Arabic', serif";

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

// ---------------------------------------------------------------- Untertitel
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
      if (cur.length >= 4 || /[.!?,:…]\*?$/.test(w.word) || i === words.length - 1) {
        chunks.push({ s: s0, ws: cur });
        cur = [];
      }
    });
    const c = [...chunks].reverse().find((k) => local >= k.s - 0.08);
    if (!c) return null;
    const op = interpolate(local, [c.s - 0.08, c.s + 0.04], [0, 1], clamp);
    let text = c.ws.join(" ");
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

// ---------------------------------------------------------------- Zitat des Propheten ﷺ (gesprochen mit Hall, goldene Schrift)
const Quote: React.FC<{ t: number }> = ({ t }) => {
  for (const q of TL.quotes) {
    const local = t - q.start;
    const next = Math.min(...TL.lines.filter((l: any) => l.start > q.start + 0.1).map((l: any) => l.start), Infinity);
    const end = Math.min(q.dur + 0.9, next - q.start - 0.02);
    if (local < -0.1 || local > end) continue;
    const timed: { word: string; start: number }[] = q.words ?? [];
    const words: string[] = timed.map((w) => w.word);
    const reveal = Math.max(1, timed.filter((w) => local >= w.start - 0.05).length);
    const op = interpolate(local, [-0.1, 0.2, end - 0.4, end], [0, 1, 1, 0], clamp);
    return (
      <div style={{ position: "absolute", left: 0, right: 0, top: 880, textAlign: "center", opacity: op }}>
        <div style={{ position: "absolute", left: -100, right: -100, top: -140, bottom: -140,
          background: "radial-gradient(ellipse at 50% 50%, rgba(8,6,4,0.66) 0%, rgba(8,6,4,0.38) 45%, rgba(8,6,4,0) 72%)" }} />
        <div style={{ position: "relative", margin: "0 80px", fontFamily: SERIF, fontStyle: "italic", fontWeight: 500, fontSize: 60,
          lineHeight: 1.22, color: GOLD, textShadow: "0 2px 12px rgba(0,0,0,0.9), 0 0 24px rgba(232,181,77,0.35)" }}>
          {words.map((w, i) => (
            <span key={i} style={{ opacity: i < reveal ? 1 : 0.12 }}>
              {(i === 0 ? "„" : "") + w.replace(/\*/g, "") + (i === words.length - 1 ? "“" : " ")}
            </span>
          ))}
        </div>
        <div style={{ position: "relative", marginTop: 26, fontFamily: MONO, fontSize: 25, letterSpacing: 3, color: "rgba(255,248,235,0.75)",
          textShadow: "0 1px 6px rgba(0,0,0,0.9)", textTransform: "uppercase" }}>
          — <Salawat text={q.by} />
        </div>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- Koran: arabisch in Gold (Wort für Wort zur Rezitation) + Deutsch
const Recite: React.FC<{ t: number }> = ({ t }) => {
  for (const r of TL.recites) {
    const local = t - r.start;
    const end = r.dur + (r.id === "r3" ? 0.2 : 0.6);
    if (local < -0.3 || local > end) continue;
    const words: { word: string; start: number }[] = r.words;
    const reveal = words.filter((w) => local >= w.start - 0.08).length;
    const op = interpolate(local, [-0.3, 0.1, end - 0.5, end], [0, 1, 1, 0], clamp);
    const deOp = interpolate(local, [0.6, 1.4], [0, 1], clamp);
    const big = r.id === "r3";
    const top = big ? 640 : r.id === "r1" ? 560 : 640;
    return (
      <div style={{ position: "absolute", left: 0, right: 0, top, textAlign: "center", opacity: op }}>
        {r.id === "r2" ? (
          <div style={{ position: "absolute", left: -120, right: -120, top: -200, bottom: -260,
            background: "radial-gradient(ellipse at 50% 45%, rgba(6,5,4,0.72) 0%, rgba(6,5,4,0.45) 48%, rgba(6,5,4,0) 74%)" }} />
        ) : null}
        <div style={{ position: "relative", fontFamily: MONO, fontSize: 26, letterSpacing: 8, color: "rgba(255,248,235,0.7)", marginBottom: 30 }}>
          {r.ref.toUpperCase()}
        </div>
        <div dir="rtl" style={{ position: "relative", margin: "0 70px", fontFamily: ARAB, fontWeight: 700, fontSize: big ? 92 : 70,
          lineHeight: big ? 1.6 : 1.75, color: GOLD,
          textShadow: "0 2px 14px rgba(0,0,0,0.9), 0 0 30px rgba(232,181,77,0.35)" }}>
          {words.map((w, i) => {
            const u = i < reveal ? interpolate(local, [w.start - 0.08, w.start + 0.25], [0, 1], clamp) : 0;
            return (
              <span key={i} style={{ opacity: 0.14 + 0.86 * u, display: "inline-block",
                filter: u > 0 && u < 1 ? `drop-shadow(0 0 ${12 * (1 - u)}px rgba(255,220,140,0.9))` : "none" }}>
                {w.word}
                {i < words.length - 1 ? " " : ""}
              </span>
            );
          })}
        </div>
        <div style={{ position: "relative", margin: "44px 90px 0", fontFamily: SERIF, fontStyle: "italic", fontWeight: 500,
          fontSize: big ? 58 : 50, lineHeight: 1.25, color: "#fbf6ec", opacity: deOp, textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>
          „{r.de}“
        </div>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- Titel am Anfang
const Title: React.FC<{ t: number }> = ({ t }) => {
  const first = TL.segments.find((s: any) => s.id === "kabine");
  const end = first ? first.start : 6.0;
  if (t > end + 0.1) return null;
  const op = interpolate(t, [0, 0.12, end - 0.45, end], [0, 1, 1, 0], clamp);
  const pop = spring({ frame: fr(t - 0.05), fps: FPS, config: { damping: 14, stiffness: 160 } });
  const pop2 = spring({ frame: fr(t - 0.25), fps: FPS, config: { damping: 11, stiffness: 150 } });
  return (
    <div style={{ position: "absolute", top: 170, left: 40, right: 40, textAlign: "center", opacity: op }}>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 60, letterSpacing: 1, color: "#fbf6ec", textShadow: "0 2px 14px rgba(0,0,0,0.8)",
        transform: `translateY(${(1 - pop) * 24}px)`, opacity: pop }}>
        WAS, WENN DAS
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 80, lineHeight: 1.05, color: GOLD, textShadow: "0 3px 18px rgba(0,0,0,0.75)",
        transform: `scale(${0.85 + 0.15 * pop2})`, opacity: pop2 }}>
        DEIN LETZTER
        <br />
        FLUG IST?
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
    if (local < 0 || local > 3.8) continue;
    const n = Math.floor(local / 0.045);
    const txt = s.label.slice(0, n);
    const op = interpolate(local, [3.2, 3.8], [1, 0], clamp);
    return (
      <div style={{ position: "absolute", top: 190, left: 0, right: 0, textAlign: "center", fontFamily: MONO, fontSize: 30, letterSpacing: 5,
        color: "#fbf6ec", opacity: op, textShadow: "0 1px 8px rgba(0,0,0,0.9)" }}>
        {txt}
        <span style={{ opacity: Math.floor(local * 3) % 2 ? 0 : 1 }}>▍</span>
      </div>
    );
  }
  return null;
};

// ---------------------------------------------------------------- schwarze Tafeln (Koran) mit leisem Goldstaub
const Dust: React.FC<{ local: number; n?: number }> = ({ local, n = 46 }) => (
  <>
    {Array.from({ length: n }).map((_, i) => {
      const r = (k: number) => {
        const x = Math.sin(i * 12.9898 + k * 78.233) * 43758.5453;
        return x - Math.floor(x);
      };
      const x = r(1) * 1080;
      const y0 = r(2) * 1920;
      const sp = 14 + r(3) * 30;
      const y = (((y0 - local * sp) % 1920) + 1920) % 1920;
      const s = 2 + r(4) * 4;
      const a = 0.15 + 0.5 * r(5) * (0.6 + 0.4 * Math.sin(local * (0.8 + r(6)) + i));
      return (
        <div key={i} style={{ position: "absolute", left: x + Math.sin(local * 0.5 + i) * 12, top: y, width: s, height: s, borderRadius: s,
          background: `rgba(232,181,77,${a})`, boxShadow: `0 0 ${s * 3}px rgba(232,181,77,${a * 0.8})` }} />
      );
    })}
  </>
);

const Card: React.FC<{ s: any; t: number }> = ({ s, t }) => {
  const local = t - s.start;
  const fin = s.id === "ende" ? interpolate(local, [s.dur - 0.6, s.dur], [1, 0], clamp) : 1;
  return (
    <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 44%, #15110a 0%, #060607 62%)",
      opacity: interpolate(local, [0, 0.35], [0, 1], clamp) * fin }}>
      <Dust local={local} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- weiche Übergänge
const XF = TL.xfade ?? 0.4;
const XF_HOOK = 0.2;
const FadeIn: React.FC<{ d: number; children: React.ReactNode }> = ({ d, children }) => {
  const f = useCurrentFrame();
  const u = d > 0 ? Math.min(1, f / d) : 1;
  return <AbsoluteFill style={{ opacity: u * u * (3 - 2 * u) }}>{children}</AbsoluteFill>;
};

// Einstieg: kurzer weißer Blitz + Ruck (wie ein Blitzschlag), dann der Titel
const HookFlash: React.FC<{ t: number }> = ({ t }) => {
  const a = interpolate(t, [0, 0.06, 0.35], [0.85, 0.6, 0], clamp);
  return a > 0 ? <AbsoluteFill style={{ background: `rgba(235,240,255,${a})` }} /> : null;
};

const Grain: React.FC = () => (
  <AbsoluteFill style={{ pointerEvents: "none", background: "radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.5) 100%)" }} />
);

const shotStyle = { width: 1080, height: 1920, filter: "saturate(1.1) contrast(1.06) brightness(1.03)" };

export const FlugVideo: React.FC = () => {
  const f = useCurrentFrame();
  const t = sec(f);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {TL.segments
        .filter((s: any) => s.kind === "clip")
        .map((s: any, i: number) => (
          <Sequence key={s.id} from={fr(s.start)} durationInFrames={fr(s.start + s.dur + XF) - fr(s.start)}>
            <FadeIn d={i === 0 ? 0 : fr(XF_HOOK)}>
              <OffthreadVideo src={staticFile(`flug/shots/${s.src}.mp4`)} muted trimBefore={fr(s.at)} style={shotStyle} />
            </FadeIn>
          </Sequence>
        ))}
      {TL.segments
        .filter((s: any) => s.kind === "shot")
        .map((s: any) => {
          const last = Math.round((s.frames / (TL.render_fps ?? 30)) * FPS) - 2;
          return (
            <Sequence key={s.id} from={fr(s.start)} durationInFrames={Math.min(fr(s.start + s.dur + XF), fr(s.start) + last) - fr(s.start)}>
              <FadeIn d={fr(XF)}>
                <OffthreadVideo src={staticFile(`flug/shots/${s.id}.mp4`)} muted style={shotStyle} />
              </FadeIn>
            </Sequence>
          );
        })}
      {TL.segments
        .filter((s: any) => s.kind === "card")
        .map((s: any) => (
          <Sequence key={s.id} from={fr(s.start)} durationInFrames={fr(s.dur + (s.id === "ende" ? 0 : XF))}>
            <Card s={s} t={t} />
          </Sequence>
        ))}
      <Grain />
      <HookFlash t={t} />
      <Title t={t} />
      <Label t={t} />
      <Quote t={t} />
      <Recite t={t} />
      <Subtitle t={t} />
      {/* Ton: fertig gemischt (Stimmen, Rezitation, Atmo, Effekte, Begrenzer) – scripts/sfx_flug.py */}
      <Audio src={staticFile("flug/master.wav")} />
    </AbsoluteFill>
  );
};
