// Minimalistisches Lern-Design: viel Weißraum, klare Typo, eine Akzentfarbe pro KB.
import React from "react";
import { Appear, Visual, TOPIC, useAppear } from "../wiso/Visuals";
import { GK_MOTION } from "./MinGK";
import { TECH } from "./Tech";

export const BG = "var(--bg, #f8f8f6)";
export const INK = "var(--ink, #111827)";
export const MUTED = "var(--muted, #6b7280)";
export const LINE = "var(--line, #e5e7eb)";
export const SANS = "Inter, sans-serif";
// Fließtext: im Tafel-Design Kreide-Handschrift (per CSS-Variable), Größe per --fscale
export const BODY = "var(--sans, Inter, sans-serif)";
export const fsz = (n: number) => `calc(${n}px * var(--fscale, 1))`;
export const fz = (kb: number) => (kb === 6 ? 1.3 : 1);
export const HEAD = "var(--head, Inter, sans-serif)";
export const LABEL = "var(--label, Inter, sans-serif)";
export const GK_ACCENT = "#2dd4bf";
export const accent = (kb: number) => (kb === 6 ? "#f6dd6b" : kb >= 5 ? GK_ACCENT : TOPIC[kb]);
// zweite Akzentfarbe (Abstand, Steigung …) und Wasserfarbe; Tafel-Design (kb 6) in Kreidefarben
export const accent2 = (kb: number) => (kb === 6 ? "#f4a3a8" : "#fbbf24");
export const water = (kb: number) => (kb === 6 ? "#8fd0f5" : accent(kb));
export const withA = (hex: string, a: number) => hex + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, "0");
export const monoF = (kb: number) => (kb === 6 ? "Caveat, cursive" : "'JetBrains Mono', monospace");
export const BGC = (kb: number) => (kb === 6 ? "#22352c" : "#0d1219");

export type Item = { text: string; cue: string; sub?: string };
export type MinProps = { v: any; t: number; D: number; cue: (c?: string) => number; kb: number; topics: string[]; topicNo: number };

export const Label: React.FC<{ kb: number; children: React.ReactNode }> = ({ kb, children }) => (
  <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: 26, letterSpacing: 6, color: accent(kb), textTransform: "uppercase", marginBottom: 14 }}>{children}</div>
);
export const H: React.FC<{ children: React.ReactNode; size?: number }> = ({ children, size = 64 }) => (
  <div style={{ fontFamily: HEAD, fontWeight: 800, fontSize: size, color: INK, lineHeight: 1.1, letterSpacing: -1, marginBottom: 34 }}>{children}</div>
);
export const Note: React.FC<{ text?: string; at: number; kb: number }> = ({ text, at, kb }) =>
  text ? (
    <Appear at={at} style={{ marginTop: 34 }}>
      <div style={{ display: "inline-block", fontFamily: SANS, fontWeight: 650, fontSize: 32, color: INK, borderLeft: `6px solid ${accent(kb)}`, padding: "6px 0 6px 22px" }}>{text}</div>
    </Appear>
  ) : null;

const Bullet: React.FC<{ item: Item; at: number; kb: number; size?: number }> = ({ item, at, kb, size = 40 }) => (
  <Appear at={at} from="left" style={{ display: "flex", alignItems: "baseline", gap: 26, margin: "14px 0" }}>
    <div style={{ width: 12, height: 12, background: accent(kb), flexShrink: 0, transform: "translateY(-6px)" }} />
    <div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: size, color: INK, lineHeight: 1.25 }}>{item.text}</div>
      {item.sub ? <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: size * 0.7, color: MUTED }}>{item.sub}</div> : null}
    </div>
  </Appear>
);

export const Frame: React.FC<{ children: React.ReactNode; center?: boolean }> = ({ children, center }) => (
  <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: center ? "center" : "flex-start", padding: "0 var(--padx, 180px)", textAlign: center ? "center" : "left" }}>
    {children}
  </div>
);

const ROMAN = ["", "I", "II", "III", "IV"];
export const kbLabel = (kb: number) => (kb === 5 ? "GK" : kb === 6 ? "BT" : `KB ${ROMAN[kb]}`);

const M: Record<string, React.FC<MinProps>> = {
  kb: ({ v, kb, topics, t }) => {
    if (kb >= 5)
      return (
        <Frame>
          <Appear at={0}><Label kb={kb}>{v.outro ? "Alle Themen durch" : v.kicker ?? "WiSo-Abschlussprüfung"}</Label></Appear>
          <Appear at={0.15}>
            <div style={{ fontFamily: HEAD, fontWeight: 900, fontSize: 150, color: INK, lineHeight: 0.95, letterSpacing: -5 }}>{v.outro ? "Geschafft." : v.hero ?? "Gemeinschafts­kunde"}</div>
          </Appear>
          <Appear at={0.5}>
            <div style={{ display: "flex", gap: 18, marginTop: 50 }}>
              {((v.chips as string[] | undefined) ?? [`${topics.length - 1} Themen`, "Erklärt wie im Unterricht", "Prüfungstipps"]).map((x, i) => (
                <div key={i} style={{ fontFamily: LABEL, fontSize: 24, color: i === 0 ? accent(kb) : MUTED, border: `2px solid ${i === 0 ? accent(kb) : LINE}`, borderRadius: 40, padding: "10px 24px" }}>{x}</div>
              ))}
            </div>
          </Appear>
        </Frame>
      );
    const two = topics.length > 9;
    return (
      <div style={{ height: "100%", display: "flex", alignItems: "center", padding: "0 160px", gap: 110 }}>
        <div style={{ width: 620 }}>
          <Appear at={0}>
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 230, color: accent(kb), lineHeight: 0.9, letterSpacing: -6 }}>{kbLabel(kb)}</div>
          </Appear>
          <Appear at={0.3}>
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 54, color: INK, lineHeight: 1.15, marginTop: 30 }}>{v.outro ? "Geschafft! ✓" : ""}</div>
          </Appear>
        </div>
        <div style={{ flex: 1, display: "grid", gridTemplateColumns: two ? "1fr 1fr" : "1fr", columnGap: 60, rowGap: 6 }}>
          {topics.map((x, i) => (
            <Appear key={i} at={0.4 + i * (v.outro ? 0.08 : 0.18)} from="left">
              <div style={{ display: "flex", gap: 20, alignItems: "baseline", borderBottom: `1px solid ${LINE}`, padding: "8px 0" }}>
                <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, color: accent(kb), width: 40 }}>{v.outro ? "✓" : String(i + 1).padStart(2, "0")}</div>
                <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: topics.length > 12 ? 28 : 32, color: INK }}>{x}</div>
              </div>
            </Appear>
          ))}
        </div>
      </div>
    );
  },

  topic: ({ kb, topics, topicNo, t }) => {
    const w = useAppear(0.3);
    if (kb >= 5)
      return (
        <Frame>
          <Appear at={0}>
            <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: 190, color: accent(kb), lineHeight: 1, letterSpacing: -8 }}>{String(topicNo).padStart(2, "0")}</div>
          </Appear>
          <div style={{ width: 1100 * w, height: 2, background: LINE, margin: "26px 0 34px" }} />
          <Appear at={0.15}>
            <div style={{ fontFamily: HEAD, fontWeight: 850, fontSize: 96, color: INK, lineHeight: 1.04, letterSpacing: -3, maxWidth: 1200 }}>{topics[topicNo - 1]}</div>
          </Appear>
        </Frame>
      );
    return (
      <Frame>
        <Appear at={0}>
          <Label kb={kb}>Thema {topicNo} / {topics.length}</Label>
        </Appear>
        <Appear at={0.12}>
          <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 120, color: INK, lineHeight: 1.02, letterSpacing: -3, maxWidth: 1500 }}>{topics[topicNo - 1]}</div>
        </Appear>
        <div style={{ width: 260 * w, height: 10, background: accent(kb), marginTop: 40 }} />
      </Frame>
    );
  },

  points: ({ v, cue, kb }) => {
    const items = v.items as Item[];
    const size = items.length > 5 ? 36 : 42;
    return (
      <Frame>
        {v.label ? <Label kb={kb}>{v.label}</Label> : null}
        <H>{v.title}</H>
        {items.map((it, i) => <Bullet key={i} item={it} at={cue(it.cue)} kb={kb} size={size} />)}
        <Note text={v.note} at={cue(v.cueNote)} kb={kb} />
      </Frame>
    );
  },

  def: ({ v, kb }) => (
    <Frame>
      <Label kb={kb}>Definition</Label>
      <Appear at={0.1}><H size={84}>{v.term}</H></Appear>
      <Appear at={0.5}>
        <div style={{ borderLeft: `8px solid ${accent(kb)}`, paddingLeft: 36, fontFamily: SANS, fontWeight: 500, fontSize: 52, lineHeight: 1.35, color: INK, maxWidth: 1450 }}>{v.text}</div>
      </Appear>
    </Frame>
  ),

  compare: ({ v, cue, kb }) => {
    const col = (s: any, at: number, strong: boolean) => (
      <Appear at={at} style={{ flex: 1 }} from={strong ? "right" : "left"}>
        <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 52, color: strong ? accent(kb) : INK, marginBottom: 24 }}>{s.title}</div>
        {s.items.map((x: string, i: number) => (
          <div key={i} style={{ fontFamily: SANS, fontWeight: 550, fontSize: s.items.length > 4 ? 32 : 38, color: INK, padding: "12px 0", borderTop: `1px solid ${LINE}` }}>{x}</div>
        ))}
      </Appear>
    );
    return (
      <Frame>
        <div style={{ display: "flex", gap: 90, width: "100%" }}>
          {col(v.left, 0, false)}
          <div style={{ width: 2, background: LINE }} />
          {col(v.right, cue(v.cueRight), true)}
        </div>
        <Note text={v.note} at={cue(v.cueNote ?? v.cueRight)} kb={kb} />
      </Frame>
    );
  },

  table: ({ v, cue, kb }) => {
    const head = v.head as string[];
    const rows = v.rows as any[];
    const cols = head.length === 2 ? "1fr 1.3fr" : head.length === 3 ? "1fr 1fr 1.4fr" : "1.6fr 0.6fr 0.4fr 0.4fr";
    const fs = rows.length > 5 ? 30 : 34;
    return (
      <Frame>
        <H size={58}>{v.title}</H>
        <div style={{ width: "100%", display: "grid", gridTemplateColumns: cols, columnGap: 30 }}>
          {head.map((h, i) => (
            <div key={i} style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, letterSpacing: 4, color: MUTED, textTransform: "uppercase", paddingBottom: 12, borderBottom: `3px solid ${INK}` }}>{h}</div>
          ))}
          {rows.map((r, i) => (
            <React.Fragment key={i}>
              {(r.cells as string[]).map((c, k) => (
                <Appear key={k} at={cue(r.cue)} style={{ fontFamily: SANS, fontWeight: k === 0 ? 750 : 500, fontSize: fs, color: r.hl ? accent(kb) : INK, padding: "16px 0", borderBottom: `1px solid ${LINE}`, background: r.hl ? `${accent(kb)}10` : "transparent" }}>{c}</Appear>
              ))}
            </React.Fragment>
          ))}
        </div>
        <Note text={v.note} at={cue(v.cueNote) || cue(rows[rows.length - 1]?.cue) + 1} kb={kb} />
      </Frame>
    );
  },

  case: ({ v, cue, kb }) => {
    const items = v.items as Item[];
    const vertical = items.length > 4;
    return (
      <Frame>
        <Label kb={kb}>{v.title}</Label>
        <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", gap: vertical ? 10 : 22, alignItems: vertical ? "flex-start" : "stretch", width: "100%" }}>
          {items.map((it, i) => (
            <React.Fragment key={i}>
              <Appear at={cue(it.cue)} from={vertical ? "left" : "up"} style={{ flex: vertical ? undefined : 1 }}>
                <div style={{ display: "flex", alignItems: vertical ? "center" : "flex-start", flexDirection: vertical ? "row" : "column", gap: vertical ? 24 : 18 }}>
                  <div style={{ width: vertical ? 54 : 64, height: vertical ? 54 : 64, borderRadius: 40, border: `3px solid ${accent(kb)}`, color: accent(kb), fontFamily: SANS, fontWeight: 800, fontSize: vertical ? 26 : 30, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>{i + 1}</div>
                  <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: vertical ? 34 : 38, color: INK, lineHeight: 1.25 }}>{it.text}</div>
                </div>
              </Appear>
              {!vertical && i < items.length - 1 ? <div style={{ fontFamily: SANS, fontSize: 40, color: LINE, alignSelf: "flex-start", marginTop: 8 }}>→</div> : null}
            </React.Fragment>
          ))}
        </div>
      </Frame>
    );
  },

  merke: ({ v, kb }) => (
    <Frame>
      <Appear at={0}><Label kb={kb}>Merke</Label></Appear>
      <Appear at={0.25}>
        <div style={{ background: `${accent(kb)}0f`, borderLeft: `12px solid ${accent(kb)}`, padding: "40px 50px", fontFamily: SANS, fontWeight: 750, fontSize: 54, lineHeight: 1.3, color: INK, maxWidth: 1560 }}>{v.text}</div>
      </Appear>
    </Frame>
  ),

  big: ({ v, cue, kb }) => (
    <Frame>
      {v.sub ? <Label kb={kb}>{v.sub}</Label> : null}
      <Appear at={0.1}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 150, color: accent(kb), letterSpacing: -2, lineHeight: 1 }}>{v.big}</div>
      </Appear>
      <div style={{ marginTop: 30 }}>
        {(v.items as Item[]).map((it, i) => <Bullet key={i} item={it} at={cue(it.cue)} kb={kb} size={34} />)}
      </div>
    </Frame>
  ),

  formula: ({ v, cue, kb }) => (
    <Frame>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "10px 28px", alignItems: "baseline" }}>
        {(v.parts as string[][]).map(([p, c, cu], i) => (
          <Appear key={i} at={cue(cu)} from="up">
            <div style={{ fontFamily: SANS, fontWeight: 850, fontSize: 76, color: c || INK, letterSpacing: -1 }}>{p}</div>
          </Appear>
        ))}
      </div>
      <Note text={v.note} at={cue((v.parts as string[][]).slice(-1)[0][2]) + 0.8} kb={kb} />
    </Frame>
  ),
  stairs: ({ v, cue, kb }) => (
    <Frame>
      <H size={58}>{v.title}</H>
      {(v.items as Item[]).map((it, i) => (
        <Appear key={i} at={cue(it.cue)} from="left" style={{ marginLeft: i * 70, marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 28, borderLeft: `8px solid ${accent(kb)}`, paddingLeft: 26 }}>
            <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 60, color: accent(kb), width: 50 }}>{i + 1}</div>
            <div>
              <div style={{ fontFamily: SANS, fontWeight: 750, fontSize: 40, color: INK }}>{it.text}</div>
              {it.sub ? <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 30, color: MUTED }}>{it.sub}</div> : null}
            </div>
          </div>
        </Appear>
      ))}
    </Frame>
  ),

  quiz: ({ v, t, cue, kb }) => {
    const at = cue(v.cueA) || 999;
    const shown = t >= at;
    return (
      <Frame>
        <Appear at={0}><Label kb={kb}>Kurze Frage an dich</Label></Appear>
        <Appear at={0.2}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 62, color: INK, lineHeight: 1.2, maxWidth: 1500 }}>{v.q}</div>
        </Appear>
        <div style={{ marginTop: 50, minHeight: 140 }}>
          {shown ? (
            <Appear at={at}>
              <div style={{ display: "flex", gap: 24, alignItems: "baseline" }}>
                <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 30, letterSpacing: 4, color: accent(kb) }}>ANTWORT</div>
                <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: 48, color: INK, lineHeight: 1.3, maxWidth: 1300 }}>{v.a}</div>
              </div>
            </Appear>
          ) : (
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 34, color: MUTED }}>Überleg kurz … 🤔</div>
          )}
        </div>
      </Frame>
    );
  },

  ledger: ({ v, t, cue, kb }) => {
    let run = 0;
    return (
      <Frame>
        <H size={52}>{v.title}</H>
        <div style={{ width: 1450 }}>
          {(v.rows as any[]).map((r, i) => {
            const at = cue(r.cue);
            if (!r.total && typeof r.amount === "number" && t >= at) run += r.amount;
            const val = r.total ? run : r.amount;
            return (
              <Appear key={i} at={at} from="left">
                <div style={{ display: "flex", justifyContent: "space-between", fontFamily: SANS, padding: "11px 0", borderTop: r.total ? `3px solid ${INK}` : `1px solid ${LINE}` }}>
                  <div style={{ fontWeight: r.total ? 850 : 550, fontSize: r.total ? 38 : 33, color: r.total ? accent(kb) : INK }}>{r.label}</div>
                  <div style={{ fontWeight: 800, fontSize: r.total ? 40 : 34, color: r.total ? accent(kb) : val < 0 ? "#dc2626" : INK, fontVariantNumeric: "tabular-nums" }}>
                    {val.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €
                  </div>
                </div>
              </Appear>
            );
          })}
        </div>
        <Note text={v.note} at={cue(v.cueNote)} kb={kb} />
      </Frame>
    );
  },
};

export const MinVisual: React.FC<MinProps> = (p) => {
  const G = p.kb >= 5 ? TECH[p.v.type] ?? GK_MOTION[p.v.type] : undefined;
  if (G) return <G {...p} />;
  const C = M[p.v.type];
  if (C) return <C {...p} />;
  // Grafiken (Kurve, Konjunktur, Dreieck, Stufen, Zeitstrahl, Rechnung) aus dem bestehenden Baukasten
  return <Visual v={p.v} t={p.t} D={p.D} cue={p.cue} topic={p.kb} />;
};
