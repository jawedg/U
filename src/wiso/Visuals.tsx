// Alle Tafelbilder / Grafiken des Lernvideos. Jede Visualisierung bekommt die aktuelle Zeit t,
// die Szenenlänge D und eine Funktion cue("Wort") = Sekunde, in der das Wort gesprochen wird.
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const INK = "#1f2937";
export const MUTED = "#64748b";
export const PAPER = "#fbf8f1";
export const TOPIC = ["#0f766e", "#2563eb", "#059669", "#7c3aed", "#ea580c", "#b45309"];
export const GREEN = "#16a34a";
export const RED = "#dc2626";
export const AMBER = "#f59e0b";
export const HAND = "Caveat, cursive";
export const SANS = "Inter, sans-serif";

export type Item = { text: string; cue: string; icon?: string; color?: string; why?: string; sub?: string };
export type CueFn = (cue?: string) => number;
export type VProps = { v: any; t: number; D: number; cue: CueFn; topic: number };

const clamp = (x: number) => Math.min(1, Math.max(0, x));

// Einblenden ab Zeitpunkt `at` (Sekunden)
export const useAppear = (at: number, dur = 0.45) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - Math.round(at * fps), fps, config: { damping: 14, stiffness: 140 }, durationInFrames: Math.round(dur * fps * 2) });
  return at <= 0 ? 1 : s;
};

export const Appear: React.FC<{ at: number; children: React.ReactNode; style?: React.CSSProperties; from?: "up" | "left" | "right" | "zoom" }> = ({ at, children, style, from = "up" }) => {
  const p = useAppear(at);
  const tr =
    from === "left" ? `translateX(${(1 - p) * -60}px)` : from === "right" ? `translateX(${(1 - p) * 60}px)` : from === "zoom" ? `scale(${0.7 + 0.3 * p})` : `translateY(${(1 - p) * 30}px)`;
  return <div style={{ opacity: p, transform: tr, ...style }}>{children}</div>;
};

const Card: React.FC<{ children: React.ReactNode; style?: React.CSSProperties; color?: string }> = ({ children, style, color }) => (
  <div
    style={{
      background: "#fff",
      borderRadius: 26,
      boxShadow: "0 10px 30px rgba(15,23,42,0.10), 0 2px 6px rgba(15,23,42,0.06)",
      border: `3px solid ${color ?? "#e2e8f0"}`,
      padding: "28px 36px",
      ...style,
    }}
  >
    {children}
  </div>
);

const Title: React.FC<{ children: React.ReactNode; color: string; size?: number }> = ({ children, color, size = 76 }) => (
  <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: size, color, lineHeight: 1.05, marginBottom: 18 }}>{children}</div>
);

const Row: React.FC<{ item: Item; at: number; color: string; size?: number }> = ({ item, at, color, size = 46 }) => {
  const c = item.color === "green" ? GREEN : item.color === "red" ? RED : INK;
  return (
    <Appear at={at} style={{ display: "flex", alignItems: "center", gap: 22, margin: "14px 0" }}>
      <div style={{ width: 70, height: 70, borderRadius: 18, background: `${color}18`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, flexShrink: 0 }}>
        {item.icon ?? "•"}
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: size, color: c, lineHeight: 1.2 }}>{item.text}</div>
    </Appear>
  );
};

// ---------------- Lukas (Elektroniker) ----------------
export const Lukas: React.FC<{ pose?: string; t: number; size?: number }> = ({ pose = "think", t, size = 1 }) => {
  const bob = Math.sin(t * 2.2) * 4;
  const arms: Record<string, string> = {
    think: "M 70 150 L 48 210 M 130 150 L 150 120 L 118 98",
    happy: "M 70 150 L 30 92 M 130 150 L 170 92",
    worried: "M 70 150 L 58 100 L 78 74 M 130 150 L 142 100 L 122 74",
    neutral: "M 70 150 L 52 220 M 130 150 L 148 220",
  };
  const mouth = pose === "worried" ? "M 88 92 Q 100 84 112 92" : pose === "happy" ? "M 84 86 Q 100 104 116 86" : "M 88 90 Q 100 98 112 90";
  return (
    <svg viewBox="0 0 200 330" width={260 * size} height={430 * size} style={{ transform: `translateY(${bob}px)`, overflow: "visible" }}>
      <ellipse cx="100" cy="322" rx="70" ry="9" fill="rgba(0,0,0,0.08)" />
      <path d="M 78 230 L 72 316 M 122 230 L 128 316" stroke="#1e3a5f" strokeWidth="26" strokeLinecap="round" />
      <path d="M 62 140 Q 100 126 138 140 L 142 240 L 58 240 Z" fill="#2563eb" />
      <path d="M 60 196 L 140 196" stroke="#f97316" strokeWidth="10" />
      <path d="M 100 140 L 100 240" stroke="#1d4ed8" strokeWidth="3" />
      <path d={arms[pose] ?? arms.neutral} stroke="#2563eb" strokeWidth="20" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <circle cx="100" cy="80" r="40" fill="#f3c9a1" />
      <path d="M 60 74 Q 62 30 100 30 Q 140 30 140 74 L 140 64 Q 100 50 60 64 Z" fill="#facc15" stroke="#ca8a04" strokeWidth="3" />
      <rect x="56" y="64" width="88" height="10" rx="5" fill="#eab308" />
      <circle cx="86" cy="80" r="4.5" fill={INK} />
      <circle cx="114" cy="80" r="4.5" fill={INK} />
      <path d={mouth} stroke={INK} strokeWidth="4" fill="none" strokeLinecap="round" />
      {pose === "worried" ? <path d="M 140 70 q 6 10 0 14 q -6 -4 0 -14" fill="#60a5fa" /> : null}
    </svg>
  );
};

const Bubble: React.FC<{ text: string; at?: number }> = ({ text, at = 0.2 }) => (
  <Appear at={at} from="zoom" style={{ position: "relative", background: "#fff", border: `4px solid ${INK}`, borderRadius: 40, padding: "18px 30px", fontFamily: HAND, fontSize: 54, fontWeight: 700, color: INK, maxWidth: 520, textAlign: "center" }}>
    {text}
    <div style={{ position: "absolute", bottom: -26, left: 70, width: 0, height: 0, borderLeft: "16px solid transparent", borderRight: "16px solid transparent", borderTop: `26px solid ${INK}` }} />
  </Appear>
);

// ---------------- Daten ----------------
const BALANCE = [
  { k: "Geld", bp: "Einkommen & Vermögen", icon: "💶", chance: "mehr verdienen · Gewinn gehört mir · eigenes Vermögen", risk: "kein festes Gehalt · Verlust bis zur Insolvenz" },
  { k: "Zeit", bp: "Arbeitsbelastung", icon: "⏰", chance: "Zeit selbst einteilen", risk: "viel Arbeit, auch am Wochenende · wenig Urlaub" },
  { k: "Verantwortung", bp: "Verantwortung", icon: "🧭", chance: "eigener Chef · selbst entscheiden", risk: "für alles verantwortlich – auch für Mitarbeiter" },
  { k: "Absicherung", bp: "soziale Sicherung", icon: "🛡️", chance: "Versicherungen frei wählen", risk: "alles selbst zahlen · keine Lohnfortzahlung · kein bezahlter Urlaub" },
];

const PLAN = ["Geschäftsidee", "Gründerperson", "Kunden & Markt", "Konkurrenz", "Marketing", "Standort", "Rechtsform", "Personal", "Finanzen (Kapitalbedarfsplan)"];

export const FORMS: Record<string, { name: string; long: string; icon: string; persons: string; kapital: string; haftung: string; gf: string; safe: boolean; extra?: string }> = {
  einzel: { name: "Einzelunternehmen", long: "", icon: "🧍", persons: "1 Person", kapital: "keins", haftung: "unbeschränkt – auch mit Privatvermögen", gf: "Inhaber allein", safe: false },
  gbr: { name: "GbR", long: "Gesellschaft bürgerlichen Rechts", icon: "👥", persons: "mind. 2 Personen", kapital: "keins", haftung: "alle unbeschränkt – jeder für alles (gesamtschuldnerisch)", gf: "alle gemeinsam (wenn nicht anders vereinbart)", safe: false },
  gmbh: { name: "GmbH", long: "Gesellschaft mit beschränkter Haftung", icon: "🏢", persons: "ab 1 Person", kapital: "25.000 € (mind. 12.500 € eingezahlt)", haftung: "beschränkt – Privatvermögen geschützt", gf: "Geschäftsführer", safe: true },
  ug: { name: "UG (haftungsbeschränkt)", long: "„Mini-GmbH“", icon: "🏠", persons: "ab 1 Person", kapital: "ab 1 €", haftung: "beschränkt – Privatvermögen geschützt", gf: "Geschäftsführer", safe: true, extra: "25 % vom Gewinn zurücklegen, bis 25.000 €" },
};

const BLOCKS = [
  { name: "Investitionen", icon: "🚐", ex: "Transporter, Werkzeug, Messgeräte, Einrichtung, Computer", note: "einmalig, bleiben lange" },
  { name: "Erstausstattung", icon: "📦", ex: "erstes Material / erste Waren", note: "Kabel, Schalter, Sicherungen" },
  { name: "Gründungskosten", icon: "📝", ex: "Gewerbeanmeldung, Notar, Beratung", note: "einmalig bei Gründung" },
  { name: "Laufende Kosten (Anfangszeit)", icon: "🔁", ex: "Miete, Versicherungen, Werbung, Löhne", note: "× Monate!" },
  { name: "Lebenshaltungskosten", icon: "🏠", ex: "Wohnung, Essen, private Versicherungen", note: "× Monate! oft vergessen" },
  { name: "Reserve", icon: "🛟", ex: "für Unvorhergesehenes", note: "Puffer" },
];

const KAPITAL = [
  { label: "Transporter", calc: "", amount: 18000, cue: "Transporter", block: 0 },
  { label: "Werkzeug & Messgeräte", calc: "", amount: 7000, cue: "Werkzeug", block: 0 },
  { label: "Einrichtung Büro & Lager", calc: "", amount: 4000, cue: "Einrichtung", block: 0 },
  { label: "Computer & Software", calc: "", amount: 2000, cue: "Computer", block: 0 },
  { label: "Erstes Material", calc: "", amount: 6000, cue: "Material", block: 1 },
  { label: "Gründungskosten", calc: "", amount: 1000, cue: "Gründungskosten", block: 2 },
  { label: "Miete", calc: "800 € × 6", amount: 4800, cue: "Miete", block: 3 },
  { label: "Versicherungen & Werbung", calc: "400 € × 6", amount: 2400, cue: "Versicherungen", block: 3 },
  { label: "Lebenshaltung", calc: "1.600 € × 6", amount: 9600, cue: "Lebenshaltung", block: 4 },
  { label: "Reserve", calc: "", amount: 5000, cue: "Reserve", block: 5 },
];

const eur = (n: number) => `${Math.round(n).toLocaleString("de-DE")} €`;

// ---------------- Visualisierungen ----------------
const V: Record<string, React.FC<VProps>> = {
  title: ({ v, t, topic }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
      <Appear at={0}>
        <div style={{ display: "inline-block", fontFamily: SANS, fontWeight: 800, fontSize: 34, letterSpacing: 4, color: "#fff", background: TOPIC[topic], padding: "10px 26px", borderRadius: 40 }}>{v.badge}</div>
      </Appear>
      <Appear at={0.25} from="zoom">
        <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 150, color: INK, marginTop: 20 }}>{v.title}</div>
      </Appear>
      <Appear at={0.6}>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 50, color: MUTED, maxWidth: 1400 }}>{v.subtitle}</div>
      </Appear>
      <div style={{ fontSize: 80, marginTop: 30, transform: `rotate(${Math.sin(t * 3) * 8}deg)` }}>⚡</div>
    </div>
  ),

  topic: ({ v, t }) => {
    const n = v.n as number;
    const sweep = clamp(t / 0.7);
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "relative", textAlign: "center" }}>
          <div style={{ position: "absolute", left: -80, right: -80, top: 120, height: 150, background: `${TOPIC[n]}22`, transform: `scaleX(${sweep})`, transformOrigin: "left", borderRadius: 30 }} />
          <Appear at={0} from="zoom"><div style={{ fontSize: 150 }}>{v.icon}</div></Appear>
          <Appear at={0.15}>
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 52, letterSpacing: 10, color: TOPIC[n] }}>{v.label ?? (n <= 4 ? `THEMA ${n} VON 4` : "SPICKZETTEL")}</div>
          </Appear>
          <Appear at={0.35}><div style={{ position: "relative", fontFamily: HAND, fontWeight: 700, fontSize: 150, color: INK }}>{v.title}</div></Appear>
        </div>
      </div>
    );
  },

  roadmap: ({ v, t, cue }) => {
    const names: string[][] = v.names ?? [["🧑‍💼", "Selbstständigkeit", "Passt das zu mir?"], ["🗺️", "Geschäftsplan & Standort", "Plan + Ort"], ["⚖️", "Rechtsformen", "Wer haftet?"], ["🧮", "Kapitalbedarfsplan", "Wie viel Geld?"]];
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 18 }}>
        {names.map(([ic, n, s], i) => {
          const at = cue(v.cues[i]);
          const on = t >= at;
          return (
            <React.Fragment key={i}>
              <Appear at={v.flow ? at : 0.1 + i * 0.12} from="zoom">
                <div style={{ width: 360, height: 360, borderRadius: 32, background: on ? TOPIC[i + 1] : "#fff", color: on ? "#fff" : INK, border: `4px solid ${TOPIC[i + 1]}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: 20, transform: `scale(${on ? 1.04 : 1})`, boxShadow: on ? `0 18px 40px ${TOPIC[i + 1]}55` : "none", transition: "none" }}>
                  <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, opacity: 0.8 }}>{i + 1}</div>
                  <div style={{ fontSize: 90 }}>{ic}</div>
                  <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 38, lineHeight: 1.15 }}>{n}</div>
                  <div style={{ fontFamily: HAND, fontSize: 40, marginTop: 6 }}>{s}</div>
                </div>
              </Appear>
              {i < 3 ? <div style={{ fontSize: 60, color: MUTED, opacity: v.flow ? clamp((t - cue(v.cues[i + 1]) + 0.4) / 0.4) : 1 }}>➜</div> : null}
            </React.Fragment>
          );
        })}
      </div>
    );
  },

  lukas: ({ v, t, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", gap: 60, padding: "0 60px" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-start", gap: 30, width: 600 }}>
        {v.bubble ? <Bubble text={v.bubble} /> : null}
        <div style={{ marginLeft: 30 }}><Lukas pose={v.pose} t={t} /></div>
      </div>
      <Card style={{ flex: 1 }} color={`${TOPIC[topic]}55`}>
        {v.title ? <Title color={TOPIC[topic]}>{v.title}</Title> : <Title color={TOPIC[topic]}>Lukas</Title>}
        {(v.items as Item[]).map((it, i) => <Row key={i} item={it} at={cue(it.cue)} color={TOPIC[topic]} />)}
      </Card>
    </div>
  ),

  board: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card style={{ width: 1450 }} color={`${TOPIC[topic]}55`}>
        <Title color={TOPIC[topic]} size={84}>{v.title}</Title>
        {(v.items as Item[]).map((it, i) => <Row key={i} item={it} at={cue(it.cue)} color={TOPIC[topic]} size={50} />)}
      </Card>
    </div>
  ),

  compare: ({ v, cue, topic }) => {
    const side = (s: any, at: number, col: string) => (
      <Appear at={at} style={{ flex: 1 }} from={at > 0 ? "right" : "left"}>
        <Card color={col} style={{ height: 500 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            <div style={{ fontSize: 80 }}>{s.icon}</div>
            <Title color={col} size={78}>{s.title}</Title>
          </div>
          {s.items.map((x: string, i: number) => (
            <div key={i} style={{ fontFamily: SANS, fontWeight: 600, fontSize: s.items.length > 4 ? 36 : 42, color: INK, margin: s.items.length > 4 ? "10px 0" : "16px 0", display: "flex", gap: 16 }}>
              <span style={{ color: col }}>●</span>
              {x}
            </div>
          ))}
        </Card>
      </Appear>
    );
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 70px", gap: 24 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 50 }}>
          {side(v.left, 0, TOPIC[topic])}
          <div style={{ fontFamily: HAND, fontSize: 90, color: MUTED }}>vs.</div>
          {side(v.right, cue(v.cueRight), AMBER)}
        </div>
        {v.footer ? <Note text={v.footer} at={cue(v.cueFooter)} color={TOPIC[topic]} /> : null}
      </div>
    );
  },

  tip: ({ v, t, cue }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card color={AMBER} style={{ width: 1400, background: "#fffbeb", textAlign: "center", padding: 50 }}>
        <div style={{ fontSize: 110, transform: `rotate(${Math.sin(t * 4) * 6}deg)` }}>💡</div>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 46, letterSpacing: 8, color: AMBER }}>{v.title.toUpperCase()}</div>
        <Appear at={cue(v.cue)} from="zoom">
          <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 130, color: INK }}>{v.text}</div>
          <div style={{ fontFamily: SANS, fontStyle: "italic", fontWeight: 500, fontSize: 44, color: MUTED, marginTop: 10 }}>{v.example}</div>
        </Appear>
      </Card>
    </div>
  ),

  traits: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", gap: 36, padding: "0 120px" }}>
      <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 80, color: TOPIC[topic] }}>Unternehmereigenschaften – mit Begründung</div>
      {(v.items as Item[]).map((it, i) => (
        <Appear key={i} at={cue(it.cue)} from="left">
          <Card color={`${TOPIC[topic]}66`} style={{ display: "flex", alignItems: "center", gap: 36 }}>
            <div style={{ fontSize: 90 }}>{it.icon}</div>
            <div>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 56, color: INK }}>{it.text}</div>
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 42, color: MUTED, marginTop: 6 }}>
                <span style={{ color: TOPIC[topic], fontWeight: 800 }}>weil </span>
                {it.why}
              </div>
            </div>
          </Card>
        </Appear>
      ))}
    </div>
  ),

  balance: ({ v, t, cue }) => {
    if (v.row === -1) {
      return (
        <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
          <div style={{ fontSize: 150, transform: `rotate(${Math.sin(t * 2) * 6}deg)` }}>⚖️</div>
          <div style={{ display: "flex", gap: 30 }}>
            {BALANCE.map((b) => (
              <Appear key={b.k} at={cue(b.k)} from="zoom">
                <div style={{ width: 330, background: "#fff", border: `4px solid ${TOPIC[1]}`, borderRadius: 28, padding: 26, textAlign: "center" }}>
                  <div style={{ fontSize: 80 }}>{b.icon}</div>
                  <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: b.k.length > 8 ? 52 : 70, color: TOPIC[1] }}>{b.k}</div>
                  <div style={{ fontFamily: SANS, fontSize: 30, color: MUTED }}>{b.bp}</div>
                </div>
              </Appear>
            ))}
          </div>
          <Appear at={cue("Geld") + 0.2}>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 44, color: INK }}>Merktrick: <span style={{ color: TOPIC[1] }}>Geld – Zeit – Verantwortung – Absicherung</span></div>
          </Appear>
        </div>
      );
    }
    const rows = BALANCE.map((b, i) => {
      let show = 0, ch = 0, rk = 0;
      if (v.summaryMode) {
        const at = cue(v.cues[i]);
        show = ch = rk = t >= at ? 1 : 0;
        if (at <= 0) show = ch = rk = 1;
      } else if (i < v.row) {
        show = ch = rk = 1;
      } else if (i === v.row) {
        show = 1;
        ch = t >= cue(v.cueChance) ? 1 : 0;
        rk = t >= cue(v.cueRisk) && cue(v.cueRisk) >= cue(v.cueChance) ? 1 : t >= cue(v.cueRisk) + 3 ? 1 : 0;
      }
      return { b, i, show, ch, rk, cur: i === v.row };
    });
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 80px", gap: 14 }}>
        <div style={{ display: "grid", gridTemplateColumns: "340px 1fr 1fr", gap: 14, fontFamily: SANS, fontWeight: 900, fontSize: 36 }}>
          <div />
          <div style={{ color: GREEN, textAlign: "center" }}>➕ CHANCE</div>
          <div style={{ color: RED, textAlign: "center" }}>➖ RISIKO</div>
        </div>
        {rows.map(({ b, i, show, ch, rk, cur }) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "340px 1fr 1fr", gap: 14, opacity: show ? (cur || v.summaryMode ? 1 : 0.55) : 0.15 }}>
            <div style={{ background: cur ? TOPIC[1] : "#fff", color: cur ? "#fff" : INK, border: `3px solid ${TOPIC[1]}`, borderRadius: 20, padding: "14px 20px", display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 50 }}>{b.icon}</span>
              <div>
                <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 36 }}>{b.k}</div>
                <div style={{ fontFamily: SANS, fontSize: 24, opacity: 0.85 }}>{b.bp}</div>
              </div>
            </div>
            <div style={{ background: "#f0fdf4", border: `3px solid ${GREEN}`, borderRadius: 20, padding: "14px 20px", fontFamily: SANS, fontWeight: 650, fontSize: 32, color: INK, opacity: ch, display: "flex", alignItems: "center" }}>{b.chance}</div>
            <div style={{ background: "#fef2f2", border: `3px solid ${RED}`, borderRadius: 20, padding: "14px 20px", fontFamily: SANS, fontWeight: 650, fontSize: 32, color: INK, opacity: rk, display: "flex", alignItems: "center" }}>{b.risk}</div>
          </div>
        ))}
        {v.extra ? (
          <div style={{ display: "flex", gap: 16, marginTop: 10 }}>
            {(v.extra as Item[]).map((e, k) => (
              <Appear key={k} at={cue(e.cue)} style={{ flex: 1 }}>
                <div style={{ background: "#fff", border: "3px dashed #94a3b8", borderRadius: 18, padding: "12px 18px", fontFamily: SANS, fontWeight: 650, fontSize: 28, color: INK }}>{e.text}</div>
              </Appear>
            ))}
          </div>
        ) : null}
      </div>
    );
  },

  links: ({ v, cue, topic }) => {
    const pos = [[330, 170], [1210, 170], [330, 480], [1210, 480]];
    return (
      <div style={{ height: "100%", position: "relative" }}>
        <svg width="1920" height="760" style={{ position: "absolute", left: 0, top: 0 }}>
          <defs>
            <marker id="ar" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill={TOPIC[topic]} /></marker>
          </defs>
          {(v.edges as any[]).map((e, i) => {
            const a = pos[e.from], b = pos[e.to];
            const p = clamp((useAppearT(cue(e.cue))));
            const x1 = a[0] + 190, y1 = a[1] + 55, x2 = b[0] + 190, y2 = b[1] + 55;
            const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy);
            const sx = x1 + (dx / L) * 210, sy = y1 + (dy / L) * 70, ex = x2 - (dx / L) * 210, ey = y2 - (dy / L) * 70;
            return (
              <g key={i} opacity={p}>
                <line x1={sx} y1={sy} x2={sx + (ex - sx) * p} y2={sy + (ey - sy) * p} stroke={TOPIC[topic]} strokeWidth={6} markerEnd="url(#ar)" />
                <text x={(sx + ex) / 2} y={(sy + ey) / 2 - 16} textAnchor="middle" fontFamily={HAND} fontWeight={700} fontSize={48} fill={INK}>{e.label}</text>
              </g>
            );
          })}
        </svg>
        {(v.nodes as string[]).map((n, i) => (
          <Appear key={i} at={0.1 + i * 0.1} from="zoom" style={{ position: "absolute", left: pos[i][0], top: pos[i][1] }}>
            <div style={{ width: 380, height: 110, borderRadius: 24, background: "#fff", border: `4px solid ${TOPIC[topic]}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 800, fontSize: 40, color: INK, textAlign: "center" }}>{n}</div>
          </Appear>
        ))}
        {v.notes ? (
          <div style={{ position: "absolute", left: 120, right: 120, top: 640, display: "flex", gap: 20, justifyContent: "center" }}>
            {(v.notes as Item[]).map((nn, k) => (
              <Appear key={k} at={cue(nn.cue)}>
                <div style={{ background: `${TOPIC[topic]}15`, borderRadius: 16, padding: "12px 22px", fontFamily: SANS, fontWeight: 700, fontSize: 32, color: INK }}>{nn.text}</div>
              </Appear>
            ))}
          </div>
        ) : null}
      </div>
    );
  },

  exam: ({ v, t, cue }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card color={AMBER} style={{ width: 1500, background: "#fffbeb", position: "relative" }}>
        <div style={{ position: "absolute", right: 40, top: 30, transform: `rotate(-12deg) scale(${useAppear(0.3)})`, border: `6px solid ${RED}`, color: RED, borderRadius: 16, padding: "6px 22px", fontFamily: SANS, fontWeight: 900, fontSize: 52 }}>AP2!</div>
        <Title color="#b45309" size={90}>🎯 Prüfungswissen</Title>
        {(v.items as Item[]).map((it, i) => {
          const at = cue(it.cue);
          const done = t >= at + 0.6;
          return (
            <Appear key={i} at={at} style={{ display: "flex", alignItems: "center", gap: 22, margin: "16px 0" }}>
              <div style={{ width: 58, height: 58, borderRadius: 14, border: `4px solid ${GREEN}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 44, color: GREEN, fontWeight: 900, flexShrink: 0 }}>{done ? "✓" : ""}</div>
              <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 44, color: INK }}>{it.text}</div>
            </Appear>
          );
        })}
      </Card>
    </div>
  ),

  definition: ({ v, t, D, cue, topic }) => {
    const t2 = v.text2 ? cue(v.cue2) : D;
    const typed = Math.floor((v.text as string).length * clamp((t - 0.6) / Math.max(1, (t2 > 0 ? t2 : D) * 0.85 - 0.6)));
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 1500, background: "#fef9c3", borderRadius: 18, padding: "44px 60px", boxShadow: "0 16px 40px rgba(0,0,0,0.14)", transform: "rotate(-1deg)", backgroundImage: "repeating-linear-gradient(transparent, transparent 62px, #fde68a 62px, #fde68a 64px)" }}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 34, letterSpacing: 6, color: "#a16207" }}>📌 PRÜFUNGSREIFE DEFINITION</div>
          <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 96, color: TOPIC[topic], margin: "6px 0 10px" }}>{v.term}</div>
          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 46, lineHeight: 1.38, color: INK, minHeight: 190 }}>
            {(v.text as string).slice(0, typed)}
            <span style={{ opacity: typed < (v.text as string).length ? 1 : 0 }}>▍</span>
          </div>
          {v.text2 ? (
            <Appear at={cue(v.cue2)}>
              <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 42, lineHeight: 1.35, color: TOPIC[topic], marginTop: 18, borderTop: "3px dashed #eab308", paddingTop: 16 }}>{v.text2}</div>
            </Appear>
          ) : null}
        </div>
      </div>
    );
  },

  analogy: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 60 }}>
      {[v.left, v.right].map((s: any, i: number) => (
        <Appear key={i} at={i ? cue(v.cue) : 0} from="zoom">
          <Card color={i ? TOPIC[topic] : "#94a3b8"} style={{ width: 620, textAlign: "center", padding: 46 }}>
            <div style={{ fontSize: 150 }}>{s.icon}</div>
            <Title color={i ? TOPIC[topic] : MUTED} size={96}>{s.title}</Title>
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 42, color: INK }}>{s.text}</div>
          </Card>
        </Appear>
      )).reduce((acc: React.ReactNode[], el, i) => (i ? [...acc, <div key="eq" style={{ fontFamily: HAND, fontSize: 140, color: INK }}>≙</div>, el] : [el]), [])}
    </div>
  ),

  plan: ({ v, t, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 70 }}>
      <div style={{ width: 760, background: "#fff", borderRadius: 14, boxShadow: "0 18px 40px rgba(0,0,0,0.15)", padding: "34px 46px", borderTop: `16px solid ${TOPIC[topic]}` }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 46, color: INK }}>📘 Geschäftsplan</div>
        <div style={{ fontFamily: HAND, fontSize: 40, color: MUTED, marginBottom: 10 }}>Lukas Elektrotechnik</div>
        {PLAN.slice(0, v.upto).map((p, i) => {
          const at = cue(v.cues[i] ?? "");
          const on = t >= at + 0.3;
          return (
            <Appear key={i} at={at} style={{ display: "flex", alignItems: "center", gap: 18, margin: "8px 0" }}>
              <div style={{ width: 44, height: 44, borderRadius: 10, border: `3px solid ${TOPIC[topic]}`, display: "flex", alignItems: "center", justifyContent: "center", color: TOPIC[topic], fontWeight: 900, fontSize: 32 }}>{on ? "✓" : ""}</div>
              <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 38, color: INK }}>{i + 1}. {p}</div>
            </Appear>
          );
        })}
      </div>
      <div style={{ width: 640 }}>
        <Title color={TOPIC[topic]} size={80}>Inhalt</Title>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 40, color: MUTED, lineHeight: 1.4 }}>Was steht im Geschäftsplan?<br />Alles, was die Bank wissen will – und was Lukas selbst durchdenken muss.</div>
      </div>
    </div>
  ),

  addressees: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 80 }}>
      <Appear at={0} from="zoom">
        <div style={{ width: 380, height: 480, background: "#fff", borderRadius: 14, boxShadow: "0 18px 40px rgba(0,0,0,0.15)", borderTop: `16px solid ${TOPIC[topic]}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
          <div style={{ fontSize: 140 }}>📘</div>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 44, color: INK }}>Geschäftsplan</div>
          <div style={{ fontFamily: HAND, fontSize: 44, color: MUTED }}>Wer liest ihn?</div>
        </div>
      </Appear>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 30 }}>
        {(v.items as Item[]).map((it, i) => (
          <Appear key={i} at={cue(it.cue)} from="right">
            <Card color={i === 0 ? AMBER : `${TOPIC[topic]}66`} style={{ width: 470, display: "flex", alignItems: "center", gap: 22 }}>
              <div style={{ fontSize: 80 }}>{it.icon}</div>
              <div>
                <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 44, color: INK }}>{it.text}{i === 0 ? " ⭐" : ""}</div>
                <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 32, color: MUTED }}>{it.sub}</div>
              </div>
            </Card>
          </Appear>
        ))}
      </div>
    </div>
  ),

  factors: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
      <Title color={TOPIC[topic]} size={90}>📍 Standortfaktoren</Title>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 480px)", gap: 30 }}>
        {(v.items as Item[]).map((it, i) => (
          <Appear key={i} at={cue(it.cue)} from="zoom">
            <Card color={`${TOPIC[topic]}66`} style={{ height: 200, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center" }}>
              <div style={{ fontSize: 80 }}>{it.icon}</div>
              <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 40, color: INK }}>{it.text}</div>
            </Card>
          </Appear>
        ))}
      </div>
    </div>
  ),

  steps: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 1500 }}>
        <Title color={TOPIC[topic]} size={88}>{v.title}</Title>
        {(v.items as Item[]).map((it, i) => (
          <Appear key={i} at={cue(it.cue)} from="left" style={{ display: "flex", alignItems: "center", gap: 28, margin: "22px 0" }}>
            <div style={{ width: 90, height: 90, borderRadius: 45, background: TOPIC[topic], color: "#fff", fontFamily: SANS, fontWeight: 900, fontSize: 50, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i + 1}</div>
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 46, color: INK, background: "#fff", borderRadius: 20, padding: "18px 28px", flex: 1, boxShadow: "0 6px 16px rgba(0,0,0,0.07)" }}>{it.text}</div>
          </Appear>
        ))}
      </div>
    </div>
  ),

  standort: ({ v, t, D, cue, topic }) => {
    const rows = [["Kunden in der Nähe", 5, 3], ["Konkurrenz (wenig = gut)", 2, 4], ["Kosten (günstig = gut)", 1, 5], ["Erreichbarkeit / Parken", 2, 5], ["Größe & Lager", 1, 4]] as const;
    const res = cue(v.cueResult);
    const fill = (i: number) => clamp((t - 1 - i * ((res - 1.5) / rows.length)) / 0.6);
    const sumA = rows.reduce((a, r, i) => a + r[1] * fill(i), 0);
    const sumB = rows.reduce((a, r, i) => a + r[2] * fill(i), 0);
    const showRes = t >= res;
    const dots = (n: number, p: number, col: string) => (
      <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
        {Array.from({ length: 5 }, (_, k) => <div key={k} style={{ width: 30, height: 30, borderRadius: 15, background: k < n && p > k / n ? col : "#e2e8f0" }} />)}
      </div>
    );
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Card style={{ width: 1500, padding: "26px 40px" }} color={`${TOPIC[topic]}66`}>
          <div style={{ display: "grid", gridTemplateColumns: "560px 1fr 1fr", rowGap: 14, alignItems: "center", fontFamily: SANS }}>
            <div style={{ fontWeight: 900, fontSize: 34, color: MUTED }}>FAKTOR</div>
            <div style={{ fontWeight: 900, fontSize: 38, textAlign: "center" }}>🏙️ Innenstadt</div>
            <div style={{ fontWeight: 900, fontSize: 38, textAlign: "center" }}>🏭 Gewerbegebiet</div>
            {rows.map((r, i) => (
              <React.Fragment key={i}>
                <div style={{ fontWeight: 700, fontSize: 38, color: INK }}>{r[0]}</div>
                {dots(r[1], fill(i), "#94a3b8")}
                {dots(r[2], fill(i), TOPIC[topic])}
              </React.Fragment>
            ))}
            <div style={{ fontWeight: 900, fontSize: 44, color: INK, borderTop: "4px solid #cbd5e1", paddingTop: 12 }}>Summe</div>
            <div style={{ fontWeight: 900, fontSize: 56, textAlign: "center", borderTop: "4px solid #cbd5e1", paddingTop: 8 }}>{Math.round(sumA)}</div>
            <div style={{ fontWeight: 900, fontSize: 56, textAlign: "center", color: TOPIC[topic], borderTop: "4px solid #cbd5e1", paddingTop: 8 }}>{Math.round(sumB)} {showRes ? "👑" : ""}</div>
          </div>
          {showRes ? (
            <Appear at={res} style={{ marginTop: 14, background: `${TOPIC[topic]}15`, borderRadius: 16, padding: "12px 20px", fontFamily: SANS, fontWeight: 700, fontSize: 34, color: INK }}>
              ✅ Empfehlung: Gewerbegebiet – Lukas braucht keine Laufkundschaft, aber günstigen Platz & gute Anbindung.
            </Appear>
          ) : null}
        </Card>
      </div>
    );
  },

  pots: ({ v, t, cue }) => {
    const Pot: React.FC<{ label: string; items: string; col: string; shield?: number; hit?: number }> = ({ label, items, col, shield = 0, hit = 0 }) => (
      <div style={{ position: "relative", width: 330, textAlign: "center" }}>
        <div style={{ height: 230, background: `${col}22`, border: `5px solid ${col}`, borderRadius: "20px 20px 120px 120px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 64, transform: `rotate(${hit * Math.sin(t * 30) * 2}deg)` }}>{items}</div>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 36, color: INK, marginTop: 10 }}>{label}</div>
        {shield > 0 ? <div style={{ position: "absolute", top: -40, right: -40, fontSize: 110, opacity: shield, transform: `scale(${0.6 + 0.4 * shield})` }}>🛡️</div> : null}
      </div>
    );
    if (v.mode === "intro") {
      return (
        <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 160 }}>
          <Appear at={cue("Geschäftsvermögen")} from="zoom"><Pot label="Geschäftsvermögen" items="🧰🚐💶" col={TOPIC[3]} /></Appear>
          <Appear at={cue("Privatvermögen")} from="zoom"><Pot label="Privatvermögen" items="🚗🐷🏠" col={AMBER} /></Appear>
        </div>
      );
    }
    const lim = cue(v.cueLimited);
    const panel = (title: string, col: string, safe: boolean, at: number) => (
      <Appear at={at} style={{ flex: 1 }}>
        <Card color={col} style={{ textAlign: "center", padding: "24px 20px" }}>
          <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 72, color: col }}>{title}</div>
          <div style={{ fontSize: 70, margin: "0 0 6px" }}>🧾 Gläubiger</div>
          <div style={{ fontFamily: SANS, fontSize: 60, color: col, marginBottom: 6 }}>{safe ? "↓" : "↙   ↘"}</div>
          <div style={{ display: "flex", justifyContent: "center", gap: 40 }}>
            <Pot label="Geschäft" items="🧰🚐💶" col={TOPIC[3]} hit={1} />
            <Pot label="Privat" items="🚗🐷🏠" col={AMBER} hit={safe ? 0 : 1} shield={safe ? useAppear(at + 0.6) : 0} />
          </div>
        </Card>
      </Appear>
    );
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", gap: 40, padding: "0 60px" }}>
        {panel("unbeschränkt: beide Töpfe", RED, false, 0)}
        {panel("beschränkt: nur Geschäft", GREEN, true, lim)}
      </div>
    );
  },

  form: ({ v, cue }) => {
    const f = FORMS[v.form];
    const col = f.safe ? GREEN : RED;
    const rows = [["💰 Mindestkapital", f.kapital], ["🛡️ Haftung", f.haftung], ["🧭 Geschäftsführung", f.gf]];
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 50 }}>
        <Appear at={0} from="left">
          <div style={{ width: 430, textAlign: "center" }}>
            <div style={{ fontSize: 180 }}>{f.icon}</div>
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: f.name.length > 12 ? 46 : 64, color: TOPIC[3], lineHeight: 1.05 }}>{f.name}</div>
            {f.long ? <div style={{ fontFamily: HAND, fontSize: 46, color: MUTED }}>{f.long}</div> : null}
            <div style={{ display: "inline-block", marginTop: 14, background: `${TOPIC[3]}18`, borderRadius: 30, padding: "8px 24px", fontFamily: SANS, fontWeight: 800, fontSize: 36, color: INK }}>{f.persons}</div>
          </div>
        </Appear>
        <div style={{ width: 1100 }}>
          {rows.map(([k, val], i) => (
            <Appear key={i} at={cue(v.cues[i])} from="right" style={{ marginBottom: 20 }}>
              <div style={{ display: "flex", background: "#fff", borderRadius: 22, boxShadow: "0 6px 18px rgba(0,0,0,0.08)", overflow: "hidden" }}>
                <div style={{ width: 380, background: `${TOPIC[3]}14`, padding: "22px 26px", fontFamily: SANS, fontWeight: 800, fontSize: 36, color: INK }}>{k}</div>
                <div style={{ flex: 1, padding: "22px 26px", fontFamily: SANS, fontWeight: 700, fontSize: 38, color: i === 1 ? col : INK }}>{val}</div>
              </div>
            </Appear>
          ))}
          {f.extra ? (
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, color: "#b45309", background: "#fffbeb", borderRadius: 16, padding: "12px 20px", border: "3px dashed #f59e0b" }}>⚠️ {f.extra}</div>
          ) : null}
          {v.story ? (
            <Appear at={cue(v.cueStory)} style={{ marginTop: 16 }}>
              <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 52, color: INK, background: "#fef9c3", borderRadius: 16, padding: "14px 24px", transform: "rotate(-0.8deg)" }}>Beispiel: {v.story}</div>
            </Appear>
          ) : null}
        </div>
      </div>
    );
  },

  ugbar: ({ t, D, cue }) => {
    const p = clamp((t - cue("fünfundzwanzig")) / (D * 0.55));
    const years = Math.min(5, Math.floor(p * 5 + 0.0001));
    const done = p >= 0.999;
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 30 }}>
        <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 90, color: TOPIC[3] }}>UG: Sparstufe zur GmbH</div>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 44, color: INK }}>Jedes Jahr <span style={{ color: AMBER }}>25 % vom Gewinn</span> in die Rücklage …</div>
        <div style={{ width: 1400, height: 110, background: "#e2e8f0", borderRadius: 55, overflow: "hidden", position: "relative" }}>
          <div style={{ width: `${p * 100}%`, height: "100%", background: `linear-gradient(90deg, ${AMBER}, ${GREEN})` }} />
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 900, fontSize: 48, color: INK }}>{eur(25000 * p)} / 25.000 €</div>
        </div>
        <div style={{ display: "flex", gap: 20 }}>
          {Array.from({ length: 5 }, (_, k) => <div key={k} style={{ fontSize: 60, opacity: k < years ? 1 : 0.2 }}>🐷</div>)}
        </div>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 64, color: done ? GREEN : "#cbd5e1" }}>🏠 UG ➜ 🏢 GmbH {done ? "✅" : ""}</div>
      </div>
    );
  },

  formtable: ({ v, t, cue }) => {
    const keys = ["einzel", "gbr", "gmbh", "ug"];
    const g1 = cue(v.cueGroup1), g2 = cue(v.cueGroup2);
    const hl = (k: string) => (v.highlight ? v.highlight.includes(k) : true);
    const rows: [string, (f: any) => string][] = [["Personen", (f) => f.persons], ["Mindestkapital", (f) => f.kapital.replace(" (mind. 12.500 € eingezahlt)", "\n(½ eingezahlt)")], ["Haftung", (f) => (f.safe ? "beschränkt\nPrivat geschützt 🛡️" : "unbeschränkt\nauch privat ⚠️")], ["Geschäftsführung", (f) => f.gf.replace(" (wenn nicht anders vereinbart)", "")]];
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <div style={{ display: "grid", gridTemplateColumns: "330px repeat(4, 360px)", gap: 10, fontFamily: SANS }}>
          <div />
          {keys.map((k, i) => {
            const f = FORMS[k];
            const grp = i < 2 ? g1 : g2;
            const lit = t >= grp && hl(k);
            return (
              <div key={k} style={{ background: lit ? (i < 2 ? RED : GREEN) : TOPIC[3], color: "#fff", borderRadius: "18px 18px 0 0", padding: "14px 10px", textAlign: "center", fontWeight: 900, fontSize: 36, opacity: hl(k) ? 1 : 0.35 }}>
                {f.icon} {k === "ug" ? "UG" : f.name.replace("unternehmen", "-U.")}
              </div>
            );
          })}
          {rows.map(([label, fn], r) => (
            <React.Fragment key={r}>
              <div style={{ background: `${TOPIC[3]}14`, borderRadius: 14, padding: "16px 18px", fontWeight: 800, fontSize: 32, color: INK, display: "flex", alignItems: "center" }}>{label}</div>
              {keys.map((k) => (
                <Appear key={k} at={0.15 + r * 0.25} style={{ background: "#fff", borderRadius: 14, padding: "14px 12px", fontWeight: 700, fontSize: 29, color: INK, textAlign: "center", whiteSpace: "pre-line", opacity: hl(k) ? 1 : 0.35, display: "flex", alignItems: "center", justifyContent: "center" }}>{fn(FORMS[k])}</Appear>
              ))}
            </React.Fragment>
          ))}
        </div>
        <div style={{ display: "flex", gap: 30, marginTop: 24 }}>
          <Appear at={g1 > 0 ? g1 : 999}><div style={{ background: "#fef2f2", border: `4px solid ${RED}`, borderRadius: 18, padding: "12px 26px", fontFamily: SANS, fontWeight: 800, fontSize: 36, color: RED }}>Einzel + GbR: kein Kapital, aber privat haften</div></Appear>
          <Appear at={g2 > 0 ? g2 : 999}><div style={{ background: "#f0fdf4", border: `4px solid ${GREEN}`, borderRadius: 18, padding: "12px 26px", fontFamily: SANS, fontWeight: 800, fontSize: 36, color: GREEN }}>GmbH (25.000 €) + UG (1 €): privat geschützt</div></Appear>
        </div>
      </div>
    );
  },

  blocks: ({ v, cue }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 110px" }}>
      <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 84, color: TOPIC[4] }}>Die 6 Bausteine des Kapitalbedarfsplans</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 26, marginTop: 10 }}>
        {BLOCKS.map((b, i) => {
          const visible = i < v.upto;
          const at = cue(v.cues[i] ?? "");
          return (
            <div key={i} style={{ opacity: visible ? 1 : 0.18 }}>
              <Appear at={visible ? at : 0} from="zoom">
                <div style={{ background: visible ? "#fff" : "#f1f5f9", border: `4px solid ${visible ? TOPIC[4] : "#cbd5e1"}`, borderRadius: 24, padding: "20px 24px", height: 250 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ width: 62, height: 62, borderRadius: 31, background: TOPIC[4], color: "#fff", fontFamily: SANS, fontWeight: 900, fontSize: 36, display: "flex", alignItems: "center", justifyContent: "center" }}>{i + 1}</div>
                    <div style={{ fontSize: 64 }}>{b.icon}</div>
                  </div>
                  <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 38, color: INK, marginTop: 8 }}>{b.name}</div>
                  <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 28, color: MUTED }}>{b.ex}</div>
                  <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 38, color: TOPIC[4] }}>{b.note}</div>
                </div>
              </Appear>
            </div>
          );
        })}
      </div>
    </div>
  ),

  calc: ({ v, cue }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
      <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 90, color: TOPIC[4] }}>Monatliche Kosten × Monate!</div>
      <Appear at={cue(v.cue)} from="zoom">
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 110, color: INK, background: "#fff", borderRadius: 30, padding: "30px 60px", boxShadow: "0 12px 30px rgba(0,0,0,0.1)" }}>{v.line}</div>
      </Appear>
      <Appear at={cue(v.cueWarn)} from="zoom">
        <div style={{ border: `7px solid ${RED}`, color: RED, borderRadius: 20, padding: "10px 40px", fontFamily: SANS, fontWeight: 900, fontSize: 64, transform: "rotate(-4deg)" }}>⚠️ {v.warn}</div>
      </Appear>
    </div>
  ),

  formula: ({ v, cue }) => {
    const parts = [["Kapitalbedarf", TOPIC[4]], ["−", INK], ["Eigenkapital", GREEN], ["=", INK], ["Fremdkapital (Kredit)", RED]];
    const at = [cue(v.cues[0]), cue(v.cues[1]) - 0.1, cue(v.cues[1]), cue(v.cues[2]) - 0.1, cue(v.cues[2])];
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 50 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 26, background: "#fff", borderRadius: 36, padding: "40px 60px", boxShadow: "0 14px 34px rgba(0,0,0,0.12)" }}>
          {parts.map(([p, c], i) => (
            <Appear key={i} at={at[i]} from="zoom">
              <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 66, color: c, whiteSpace: "nowrap" }}>{p}</div>
            </Appear>
          ))}
        </div>
        <div style={{ display: "flex", gap: 40 }}>
          {(v.explain as Item[]).map((e, i) => (
            <Appear key={i} at={cue(e.cue)}>
              <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 40, color: INK, background: i ? "#fef2f2" : "#f0fdf4", border: `3px solid ${i ? RED : GREEN}`, borderRadius: 18, padding: "16px 26px" }}>{e.text}</div>
            </Appear>
          ))}
        </div>
      </div>
    );
  },

  kapital: ({ v, t, cue }) => {
    const prevUpto = v.upto === 6 ? 0 : 6;
    const visibleAt = (i: number) => (i < prevUpto || v.showKredit ? 0 : cue(KAPITAL[i].cue));
    const shown = KAPITAL.slice(0, v.upto).map((r, i) => ({ ...r, at: visibleAt(i) }));
    const total = shown.reduce((a, r) => a + (t >= r.at ? r.amount : 0), 0);
    const showTotal = v.showTotal !== undefined && (v.showTotal === "" || t >= cue(v.showTotal));
    const kAt = v.showKredit ? cue(v.showKredit) : 999;
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 50 }}>
        <Card style={{ width: 1050, padding: "20px 36px" }} color={`${TOPIC[4]}66`}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 36, color: TOPIC[4], marginBottom: 6 }}>🧮 Kapitalbedarfsplan – Lukas Elektrotechnik</div>
          {shown.map((r, i) => (
            <Appear key={i} at={r.at} from="left">
              <div style={{ display: "grid", gridTemplateColumns: "60px 1fr 220px 200px", alignItems: "center", fontFamily: SANS, fontSize: 31, padding: "5px 0", borderBottom: "2px solid #f1f5f9" }}>
                <div style={{ fontSize: 30 }}>{BLOCKS[r.block].icon}</div>
                <div style={{ fontWeight: 700, color: INK }}>{r.label}</div>
                <div style={{ fontWeight: 700, color: r.calc ? RED : MUTED }}>{r.calc}</div>
                <div style={{ fontWeight: 800, color: INK, textAlign: "right" }}>{eur(r.amount)}</div>
              </div>
            </Appear>
          ))}
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: SANS, fontWeight: 900, fontSize: 42, marginTop: 10, color: showTotal ? TOPIC[4] : INK, borderTop: `4px solid ${INK}`, paddingTop: 8 }}>
            <span>= Kapitalbedarf</span>
            <span>{eur(total)}</span>
          </div>
        </Card>
        <div style={{ width: 560 }}>
          <Appear at={kAt}>
            <Card color={RED} style={{ fontFamily: SANS }}>
              <div style={{ fontWeight: 800, fontSize: 38, color: INK }}>Kapitalbedarf <span style={{ float: "right" }}>59.800 €</span></div>
              <div style={{ fontWeight: 800, fontSize: 38, color: GREEN }}>− Eigenkapital <span style={{ float: "right" }}>20.000 €</span></div>
              <div style={{ borderTop: `4px solid ${INK}`, marginTop: 10, paddingTop: 10, fontWeight: 900, fontSize: 46, color: RED }}>= Kredit <span style={{ float: "right" }}>39.800 €</span></div>
              <div style={{ fontSize: 80, textAlign: "center", marginTop: 10 }}>🏦</div>
            </Card>
          </Appear>
        </div>
      </div>
    );
  },

  check: ({ v, cue }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Card color={GREEN} style={{ width: 1100, padding: 50 }}>
        <Title color={GREEN} size={84}>{v.title}</Title>
        {(v.lines as string[]).map((l, i) => (
          <Appear key={i} at={cue(v.cue) + i * 1.6}>
            <div style={{ fontFamily: SANS, fontWeight: i === 2 ? 900 : 700, fontSize: 64, color: i === 2 ? GREEN : INK, margin: "10px 0", borderTop: i === 2 ? `4px solid ${INK}` : "none", paddingTop: i === 2 ? 10 : 0 }}>{l}</div>
          </Appear>
        ))}
      </Card>
    </div>
  ),

  circle: ({ v, t, cue }) => {
    const nodes = [["1", "Selbstständigkeit", "Risiko", 960, 150], ["2", "Geschäftsplan", "& Standort", 1500, 420], ["3", "Rechtsform", "", 960, 660], ["4", "Kapitalbedarfsplan", "", 420, 420]] as const;
    const edges = [[3, 1, "Finanzteil von", v.cues[0]], [1, 3, "Miete fließt ein", v.cues[1]], [3, 2, "Eigenkapital ➜ Wahl", v.cues[2]], [3, 0, "Kredit = Risiko", v.cues[3]]] as const;
    return (
      <div style={{ height: "100%", position: "relative" }}>
        <svg width="1920" height="780" style={{ position: "absolute" }}>
          {edges.map(([a, b, label, c], i) => {
            const p = clamp(useAppearT(cue(c)));
            const A = nodes[a], B = nodes[b];
            const off = a === 3 && b === 1 ? -40 : a === 1 && b === 3 ? 40 : 0;
            const x1 = A[3], y1 = A[4] + off, x2 = B[3], y2 = B[4] + off;
            const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
            return (
              <g key={i} opacity={p}>
                <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * p} y2={y1 + (y2 - y1) * p} stroke={TOPIC[i % 2 ? 2 : 4]} strokeWidth={7} strokeDasharray="14 10" />
                <rect x={mx - 190} y={my - 34 + off * 0.6} width={380} height={64} rx={18} fill="#fff" stroke={TOPIC[4]} strokeWidth={3} />
                <text x={mx} y={my + 10 + off * 0.6} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={32} fill={INK}>{label}</text>
              </g>
            );
          })}
        </svg>
        {nodes.map(([n, a, b, x, y], i) => (
          <div key={i} style={{ position: "absolute", left: x - 180, top: y - 70, width: 360, height: 140, borderRadius: 30, background: TOPIC[+n], color: "#fff", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", fontFamily: SANS, fontWeight: 900, fontSize: 36, boxShadow: "0 12px 30px rgba(0,0,0,0.15)", transform: `scale(${1 + 0.03 * Math.sin(t * 3 + i)})` }}>
            <div style={{ fontSize: 28, opacity: 0.8 }}>Thema {n}</div>
            {a}
            {b ? <div style={{ fontSize: 26 }}>{b}</div> : null}
          </div>
        ))}
      </div>
    );
  },

  sum: ({ v, t, cue }) => (
    <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 1600, background: "#fff", borderRadius: 26, borderLeft: `22px solid ${TOPIC[v.n]}`, boxShadow: "0 14px 34px rgba(0,0,0,0.1)", padding: "30px 46px" }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 30, letterSpacing: 6, color: TOPIC[v.n] }}>📝 SPICKZETTEL</div>
        <Title color={INK} size={84}>{v.title}</Title>
        {(v.items as Item[]).map((it, i) => (
          <Appear key={i} at={cue(it.cue)} style={{ display: "flex", gap: 18, alignItems: "flex-start", margin: "10px 0" }}>
            <div style={{ color: TOPIC[v.n], fontSize: 42, fontWeight: 900, lineHeight: 1.2 }}>✔</div>
            <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: (v.items as Item[]).length > 5 ? 37 : 42, color: INK, lineHeight: 1.3 }}>{it.text}</div>
          </Appear>
        ))}
      </div>
    </div>
  ),

  deflist: ({ v, cue }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", gap: 20 }}>
      <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 34, letterSpacing: 6, color: "#a16207" }}>📌 DEFINITIONEN ZUM AUSWENDIGLERNEN</div>
      {(v.items as Item[]).map((it, i) => (
        <Appear key={i} at={cue(it.cue)} from="left">
          <div style={{ width: 1600, background: "#fef9c3", borderRadius: 14, padding: "18px 30px", fontFamily: SANS, fontWeight: 650, fontSize: 38, color: INK, boxShadow: "0 6px 16px rgba(0,0,0,0.08)", transform: `rotate(${i % 2 ? 0.5 : -0.5}deg)` }}>
            <b style={{ color: TOPIC[5] }}>{it.text.split(":")[0]}:</b>
            {it.text.slice(it.text.indexOf(":") + 1)}
          </div>
        </Appear>
      ))}
    </div>
  ),
  grid: ({ v, cue, topic }) => {
    const items = v.items as Item[];
    const cols = items.length <= 3 ? items.length : items.length === 4 ? 2 : 3;
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 22 }}>
        <Title color={TOPIC[topic]} size={80}>{v.title}</Title>
        <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, ${cols === 2 ? 720 : 520}px)`, gap: 24 }}>
          {items.map((it, i) => (
            <Appear key={i} at={cue(it.cue)} from="zoom">
              <Card color={`${TOPIC[topic]}66`} style={{ minHeight: 150, display: "flex", alignItems: "center", gap: 22, padding: "20px 28px" }}>
                <div style={{ fontSize: 70 }}>{it.icon}</div>
                <div style={{ fontFamily: SANS, fontWeight: 750, fontSize: 36, color: INK, lineHeight: 1.2 }}>{it.text}</div>
              </Card>
            </Appear>
          ))}
        </div>
        {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
      </div>
    );
  },

  pillars: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10 }}>
      <Title color={TOPIC[topic]} size={80}>{v.title}</Title>
      <div style={{ width: 1600, height: 40, background: TOPIC[topic], borderRadius: "20px 20px 0 0", clipPath: "polygon(4% 100%, 50% 0, 96% 100%)" }} />
      <div style={{ display: "flex", gap: 26 }}>
        {(v.items as Item[]).map((it, i) => (
          <Appear key={i} at={cue(it.cue)} from="up">
            <div style={{ width: 290, height: 380, background: "#fff", border: `5px solid ${TOPIC[topic]}`, borderRadius: 14, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: 14 }}>
              <div style={{ fontSize: 90 }}>{it.icon}</div>
              <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, color: INK }}>{it.text}</div>
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 24, color: MUTED }}>versicherung</div>
              <div style={{ fontFamily: HAND, fontWeight: 700, fontSize: 34, color: TOPIC[topic], marginTop: 10 }}>{it.sub}</div>
            </div>
          </Appear>
        ))}
      </div>
      <div style={{ width: 1600, height: 26, background: TOPIC[topic], borderRadius: 8 }} />
      {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
    </div>
  ),

  table: ({ v, cue, topic }) => {
    const head = v.head as string[];
    const cols = head.length === 2 ? "1fr 1.4fr" : head.length === 3 ? "1.1fr 1fr 1.3fr" : "1fr 0.7fr 1.2fr 1.3fr";
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 14 }}>
        <Title color={TOPIC[topic]} size={76}>{v.title}</Title>
        <div style={{ width: 1600, display: "grid", gridTemplateColumns: cols, gap: 8 }}>
          {head.map((h, i) => (
            <div key={i} style={{ background: TOPIC[topic], color: "#fff", fontFamily: SANS, fontWeight: 900, fontSize: 32, padding: "12px 20px", borderRadius: i === 0 ? "16px 0 0 0" : i === head.length - 1 ? "0 16px 0 0" : 0 }}>{h}</div>
          ))}
          {(v.rows as any[]).map((r, i) => (
            <React.Fragment key={i}>
              {(r.cells as string[]).map((c, k) => (
                <Appear key={k} at={cue(r.cue)} style={{ background: r.hl ? "#dcfce7" : "#fff", border: r.hl ? `3px solid ${GREEN}` : "none", fontFamily: SANS, fontWeight: k === 0 ? 800 : 600, fontSize: (v.rows as any[]).length > 5 ? 30 : 34, color: INK, padding: "14px 20px", boxShadow: "0 3px 10px rgba(0,0,0,0.05)" }}>{c}</Appear>
              ))}
            </React.Fragment>
          ))}
        </div>
        {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
      </div>
    );
  },

  flow: ({ v, cue, topic }) => {
    const items = v.items as Item[];
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <Title color={TOPIC[topic]} size={84}>{v.title}</Title>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          {items.map((it, i) => (
            <React.Fragment key={i}>
              <Appear at={cue(it.cue)} from="zoom">
                <div style={{ width: items.length > 4 ? 300 : 360, height: 300, background: "#fff", border: `4px solid ${TOPIC[topic]}`, borderRadius: 26, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: 18, boxShadow: "0 10px 24px rgba(0,0,0,0.08)" }}>
                  <div style={{ fontSize: 86 }}>{it.icon}</div>
                  <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: items.length > 4 ? 32 : 36, color: INK, lineHeight: 1.2 }}>{it.text}</div>
                </div>
              </Appear>
              {i < items.length - 1 ? <Appear at={cue(items[i + 1].cue)}><div style={{ fontSize: 56, color: TOPIC[topic] }}>➜</div></Appear> : null}
            </React.Fragment>
          ))}
        </div>
        {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
      </div>
    );
  },

  stairs: ({ v, cue, topic }) => {
    const items = v.items as Item[];
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", padding: "0 140px", gap: 12 }}>
        <Title color={TOPIC[topic]} size={80}>{v.title}</Title>
        {items.map((it, i) => (
          <Appear key={i} at={cue(it.cue)} from="left" style={{ marginLeft: i * 90 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 24, background: "#fff", borderLeft: `14px solid ${TOPIC[topic]}`, borderRadius: 18, padding: "14px 26px", width: 1250 - i * 90, boxShadow: "0 6px 16px rgba(0,0,0,0.08)" }}>
              <div style={{ width: 66, height: 66, borderRadius: 33, background: TOPIC[topic], color: "#fff", fontFamily: SANS, fontWeight: 900, fontSize: 36, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i + 1}</div>
              <div>
                <div style={{ fontFamily: SANS, fontWeight: 850, fontSize: 40, color: INK }}>{it.text}</div>
                {it.sub ? <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 30, color: MUTED }}>{it.sub}</div> : null}
              </div>
            </div>
          </Appear>
        ))}
        {v.note ? <div style={{ marginTop: 10 }}><Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /></div> : null}
      </div>
    );
  },

  ledger: ({ v, t, cue, topic }) => {
    const rows = v.rows as any[];
    let run = 0;
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16 }}>
        <Card style={{ width: 1500, padding: "24px 44px" }} color={`${TOPIC[topic]}66`}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, color: TOPIC[topic], marginBottom: 8 }}>{v.title}</div>
          {rows.map((r, i) => {
            const at = cue(r.cue);
            const on = t >= at;
            if (!r.total && typeof r.amount === "number" && on) run += r.amount;
            const val = r.total ? run : r.amount;
            return (
              <Appear key={i} at={at} from="left">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 30, padding: "10px 0", borderTop: r.total ? `4px solid ${INK}` : "2px solid #f1f5f9", fontFamily: SANS }}>
                  <div style={{ fontWeight: r.total ? 900 : 700, fontSize: r.total ? 42 : 36, color: r.total ? TOPIC[topic] : INK }}>{r.label}</div>
                  {v.plain ? (
                    <div style={{ fontWeight: 600, fontSize: 30, color: MUTED, textAlign: "right", maxWidth: 820 }}>{r.text}</div>
                  ) : (
                    <div style={{ fontWeight: 900, fontSize: r.total ? 46 : 38, color: r.total ? TOPIC[topic] : val < 0 ? RED : INK }}>{val.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €</div>
                  )}
                </div>
              </Appear>
            );
          })}
        </Card>
        {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
      </div>
    );
  },

  timeline: ({ v, t, cue, topic }) => {
    const at = cue(v.cue);
    const p = clamp((t - at) / 4);
    const pts = v.points as string[];
    return (
      <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 60 }}>
        <Title color={TOPIC[topic]} size={80}>{v.title}</Title>
        <div style={{ position: "relative", width: 1500, height: 220 }}>
          <div style={{ position: "absolute", top: 60, left: 0, right: 0, height: 10, background: "#e2e8f0", borderRadius: 5 }} />
          <div style={{ position: "absolute", top: 60, left: 0, width: `${p * 100}%`, height: 10, background: TOPIC[topic], borderRadius: 5 }} />
          {pts.map((x, i) => {
            const pos = i === 0 ? 0.08 : i === 1 ? 0.38 : 0.92;
            const on = p >= pos - 0.02;
            return (
              <div key={i} style={{ position: "absolute", left: `${pos * 100}%`, top: 40, transform: "translateX(-50%)", textAlign: "center", width: 360 }}>
                <div style={{ width: 50, height: 50, borderRadius: 25, margin: "0 auto", background: on ? (i === 2 ? RED : TOPIC[topic]) : "#cbd5e1" }} />
                <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32, color: on ? INK : "#94a3b8", marginTop: 16 }}>{x}</div>
              </div>
            );
          })}
        </div>
      </div>
    );
  },

  triangle: ({ v, cue, topic }) => {
    const pos = [[560, 40], [120, 560], [1000, 560]];
    return (
      <div style={{ height: "100%", position: "relative" }}>
        <svg width="1920" height="780" style={{ position: "absolute" }}>
          <polygon points="760,150 320,640 1200,640" fill={`${TOPIC[topic]}12`} stroke={TOPIC[topic]} strokeWidth={6} strokeDasharray="16 10" />
          <text x="760" y="520" textAnchor="middle" fontFamily={HAND} fontWeight={700} fontSize={64} fill={INK}>magisches Dreieck</text>
          <text x="760" y="575" textAnchor="middle" fontFamily={SANS} fontWeight={600} fontSize={28} fill={MUTED}>nie alle drei gleichzeitig maximal</text>
        </svg>
        {(v.corners as string[][]).map(([name, icon, c], i) => (
          <Appear key={i} at={cue(c)} from="zoom" style={{ position: "absolute", left: pos[i][0], top: pos[i][1] }}>
            <div style={{ width: 400, height: 170, background: "#fff", border: `5px solid ${TOPIC[topic]}`, borderRadius: 28, display: "flex", alignItems: "center", justifyContent: "center", gap: 16, fontFamily: SANS, fontWeight: 900, fontSize: 44, color: INK }}>
              <span style={{ fontSize: 64 }}>{icon}</span>{name}
            </div>
          </Appear>
        ))}
        <div style={{ position: "absolute", right: 30, top: 200, display: "flex", flexDirection: "column", gap: 16 }}>
          {(v.compare as any[]).map((c, i) => (
            <Appear key={i} at={cue(c.cue)} from="right">
              <div style={{ width: 400, background: "#fff", borderRadius: 18, padding: "14px 20px", boxShadow: "0 6px 16px rgba(0,0,0,0.1)", fontFamily: SANS }}>
                <div style={{ fontWeight: 900, fontSize: 32, color: TOPIC[topic] }}>{c.name}</div>
                {["Sicherheit", "Liquidität", "Rendite"].map((k, j) => (
                  <div key={k} style={{ fontSize: 29, fontWeight: 650, color: INK }}>{k}: <b>{c.vals[j]}</b></div>
                ))}
              </div>
            </Appear>
          ))}
        </div>
      </div>
    );
  },

  chart: ({ v, t, cue, topic }) => {
    // Achsen: x = Menge (0..100), y = Preis (0..6); Kurven als Geraden
    const X = (q: number) => 190 + q * 10;
    const Y = (p: number) => 690 - p * 105;
    const dem = (sh: number) => `M ${X(10 + sh)} ${Y(5.5)} L ${X(100 + sh * 0.6)} ${Y(0.5)}`;
    const sup = (sh: number) => `M ${X(10 + sh)} ${Y(0.5)} L ${X(100 + sh * 0.6)} ${Y(5.5)}`;
    const basic = v.mode === "basic";
    const pe = basic ? clamp((t - cue(v.cueEq)) / 0.6) : 1;
    const shD = basic ? 0 : 22 * clamp((t - cue(v.cueDemand)) / 1.2) * (t < cue(v.cueSupply) ? 1 : clamp(1 - (t - cue(v.cueSupply)) / 0.8));
    const shS = basic ? 0 : 22 * clamp((t - cue(v.cueSupply)) / 1.2);
    const over = basic && t >= cue(v.cueOver);
    const under = basic && t >= cue(v.cueUnder);
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 40 }}>
        <svg width="1380" height="760">
          <line x1={X(0)} y1={Y(0)} x2={X(110)} y2={Y(0)} stroke={INK} strokeWidth={4} />
          <line x1={X(0)} y1={Y(0)} x2={X(0)} y2={Y(6.2)} stroke={INK} strokeWidth={4} />
          <text x={X(108)} y={Y(0) + 46} fontFamily={SANS} fontWeight={800} fontSize={32} fill={INK} textAnchor="end">Menge</text>
          <text x={X(0) - 20} y={Y(6.1)} fontFamily={SANS} fontWeight={800} fontSize={32} fill={INK} textAnchor="end">Preis</text>
          <path d={dem(0)} stroke="#2563eb" strokeWidth={7} opacity={shD > 0 ? 0.25 : 1} />
          <path d={sup(0)} stroke="#ea580c" strokeWidth={7} opacity={shS > 0 ? 0.25 : 1} />
          {shD > 0 ? <path d={dem(shD)} stroke="#2563eb" strokeWidth={7} /> : null}
          {shS > 0 ? <path d={sup(shS)} stroke="#ea580c" strokeWidth={7} /> : null}
          <text x={X(102)} y={Y(0.4)} fontFamily={SANS} fontWeight={900} fontSize={36} fill="#2563eb">N</text>
          <text x={X(102)} y={Y(5.6)} fontFamily={SANS} fontWeight={900} fontSize={36} fill="#ea580c">A</text>
          {basic ? (
            <g opacity={pe}>
              <line x1={X(0)} y1={Y(3)} x2={X(55)} y2={Y(3)} stroke={GREEN} strokeWidth={3} strokeDasharray="10 8" />
              <line x1={X(55)} y1={Y(0)} x2={X(55)} y2={Y(3)} stroke={GREEN} strokeWidth={3} strokeDasharray="10 8" />
              <circle cx={X(55)} cy={Y(3)} r={16} fill={GREEN} />
              <text x={X(0) - 14} y={Y(3) + 10} textAnchor="end" fontFamily={SANS} fontWeight={900} fontSize={30} fill={GREEN}>GG-Preis</text>
              <text x={X(55)} y={Y(0) + 40} textAnchor="middle" fontFamily={SANS} fontWeight={900} fontSize={30} fill={GREEN}>GG-Menge</text>
            </g>
          ) : null}
          {over ? (
            <g>
              <line x1={X(30)} y1={Y(4.4)} x2={X(80)} y2={Y(4.4)} stroke={RED} strokeWidth={5} />
              <text x={X(55)} y={Y(4.4) - 16} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={30} fill={RED}>Angebotsüberhang ➜ Preis ↓</text>
            </g>
          ) : null}
          {under ? (
            <g>
              <line x1={X(30)} y1={Y(1.6)} x2={X(80)} y2={Y(1.6)} stroke={AMBER} strokeWidth={5} />
              <text x={X(55)} y={Y(1.6) + 44} textAnchor="middle" fontFamily={SANS} fontWeight={800} fontSize={30} fill="#b45309">Nachfrageüberhang ➜ Preis ↑</text>
            </g>
          ) : null}
        </svg>
        {!basic ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 20, width: 420 }}>
            <Appear at={cue(v.cueDemand)}><Card color="#2563eb" style={{ padding: "16px 22px" }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32 }}>Nachfrage ↑ (Hitzewelle 🍦)</div><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, color: GREEN }}>Preis ↑ · Menge ↑</div></Card></Appear>
            <Appear at={cue(v.cueSupply)}><Card color="#ea580c" style={{ padding: "16px 22px" }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32 }}>Angebot ↑ (Rekordernte 🌾)</div><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, color: GREEN }}>Preis ↓ · Menge ↑</div></Card></Appear>
            <Appear at={cue(v.cueSupply) + 3}><Card color={RED} style={{ padding: "16px 22px" }}><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32 }}>Angebot ↓ (Missernte)</div><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, color: RED }}>Preis ↑ · Menge ↓</div></Card></Appear>
          </div>
        ) : null}
      </div>
    );
  },

  formula2: ({ v, cue, topic }) => (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 46 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 24, background: "#fff", borderRadius: 36, padding: "36px 50px", boxShadow: "0 14px 34px rgba(0,0,0,0.12)" }}>
        {(v.parts as string[][]).map(([p, c, cu], i) => (
          <Appear key={i} at={cue(cu)} from="zoom">
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 64, color: c, whiteSpace: "nowrap" }}>{p}</div>
          </Appear>
        ))}
      </div>
      {v.note ? <Note text={v.note} at={cue(v.cueNote)} color={TOPIC[topic]} /> : null}
    </div>
  ),

  cycle: ({ v, t, cue, topic }) => {
    const X0 = 140, W = 1640, Y0 = 380, A = 190;
    const pts = Array.from({ length: 161 }, (_, i) => {
      const x = i / 160;
      return [X0 + x * W, Y0 - x * 90 - Math.sin(x * Math.PI * 2 * 1.25 - Math.PI / 2) * A] as const;
    });
    const firstCue = cue(v.cues[0]);
    const draw = clamp((t - firstCue + 0.5) / 5);
    const n = Math.max(2, Math.round(draw * 160));
    const d = pts.slice(0, n).map(([x, y], i) => `${i ? "L" : "M"} ${x} ${y}`).join(" ");
    const labels = [["Aufschwung", 0.12, "📈"], ["Hochkonjunktur", 0.4, "🔝"], ["Abschwung", 0.6, "📉"], ["Tiefstand", 0.8, "🕳️"]] as const;
    return (
      <div style={{ height: "100%", position: "relative" }}>
        <svg width="1920" height="620" style={{ position: "absolute", top: 0 }}>
          <line x1={X0} y1={Y0} x2={X0 + W} y2={Y0 - 90} stroke="#94a3b8" strokeWidth={4} strokeDasharray="14 10" />
          <text x={X0 + W - 10} y={Y0 - 110} textAnchor="end" fontFamily={HAND} fontWeight={700} fontSize={44} fill={MUTED}>Trend</text>
          <path d={d} stroke={TOPIC[topic]} strokeWidth={9} fill="none" strokeLinecap="round" />
          {labels.map(([l, x], i) => {
            const at = cue(v.cues[i]);
            if (t < at) return null;
            const [px, py] = pts[Math.round(x * 160)];
            return (
              <g key={i}>
                <circle cx={px} cy={py} r={16} fill={TOPIC[topic]} />
                <text x={px} y={py + (i === 1 ? -36 : i === 3 ? 60 : -30)} textAnchor="middle" fontFamily={SANS} fontWeight={900} fontSize={38} fill={INK}>{labels[i][2]} {l}</text>
              </g>
            );
          })}
        </svg>
        <div style={{ position: "absolute", top: 600, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 24 }}>
          {(v.ind as Item[]).map((it, i) => (
            <Appear key={i} at={cue(it.cue)}>
              <div style={{ background: "#fff", border: `3px solid ${TOPIC[topic]}`, borderRadius: 18, padding: "12px 22px", fontFamily: SANS, fontWeight: 800, fontSize: 32, color: INK }}>{it.text}</div>
            </Appear>
          ))}
        </div>
      </div>
    );
  },
};

const Note: React.FC<{ text: string; at: number; color: string }> = ({ text, at, color }) => (
  <Appear at={at}>
    <div style={{ background: `${color}14`, border: `3px dashed ${color}`, borderRadius: 18, padding: "12px 26px", fontFamily: SANS, fontWeight: 750, fontSize: 32, color: INK, textAlign: "center", maxWidth: 1600 }}>💡 {text}</div>
  </Appear>
);

// Fortschritt 0..1 einer Linie, die ab `at` gezeichnet wird
function useAppearT(at: number) {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (at <= 0) return 1;
  return interpolate(frame / fps, [at, at + 0.6], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
}

export const Visual: React.FC<VProps> = (p) => {
  const C = V[p.v.type];
  if (!C) return <div style={{ fontSize: 60 }}>Unbekannt: {p.v.type}</div>;
  return <C {...p} />;
};

// alle Cue-Wörter einer Visualisierung (für Pop-Sounds)
export const collectCues = (v: any): string[] => {
  const out: string[] = [];
  const walk = (x: any, key = "") => {
    if (typeof x === "string") {
      if (key.startsWith("cue") && x) out.push(x);
      return;
    }
    if (Array.isArray(x)) {
      x.forEach((y) => walk(y, key === "cues" ? "cue" : key));
      return;
    }
    if (x && typeof x === "object") Object.entries(x).forEach(([k, y]) => walk(y, k));
  };
  walk(v);
  return out;
};
