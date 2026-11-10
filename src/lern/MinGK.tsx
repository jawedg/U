// Gemeinschaftskunde – Variante 1: dunkles Minimal-Design MIT Bewegung.
// Elemente fliegen gefedert ein, das gerade gesprochene Element wird hervorgehoben (Fokus), Rest wird gedimmt.
import React from "react";
import { interpolate, spring } from "remotion";
import type { Item, MinProps } from "./Min";
import { Frame, HEAD, INK, LABEL, LINE, MUTED, SANS, accent } from "./Min";

const FPS = 25;
export const sp = (t: number, at: number, damping = 13, stiffness = 150) =>
  at > 900 ? 0 : spring({ frame: Math.round((t - at) * FPS), fps: FPS, config: { damping, stiffness } });
export const ramp = (t: number, a: number, b: number) => interpolate(t, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
export const focus = (t: number, at: number, next: number) => ramp(t, at, at + 0.3) * (1 - ramp(t, next, next + 0.3));

// Wörter nacheinander einblenden
export const Words: React.FC<{ text: string; t: number; at: number; step?: number; style?: React.CSSProperties; color?: (w: string, i: number) => string | undefined }> = ({
  text, t, at, step = 0.07, style, color,
}) => (
  <div style={style}>
    {text.split(" ").map((w, i) => {
      const p = sp(t, at + i * step, 15, 170);
      return (
        <span key={i} style={{ display: "inline-block", opacity: p, transform: `translateY(${(1 - p) * 28}px)`, marginRight: "0.26em", color: color?.(w, i) }}>
          {w}
        </span>
      );
    })}
  </div>
);

export const Kicker: React.FC<{ kb: number; t: number; at?: number; children: React.ReactNode }> = ({ kb, t, at = 0, children }) => {
  const p = sp(t, at);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 18, opacity: p }}>
      <div style={{ width: 36 * p, height: 3, background: accent(kb) }} />
      <div style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 24, letterSpacing: 5, color: accent(kb), textTransform: "uppercase" }}>{children}</div>
    </div>
  );
};

export const Title: React.FC<{ text: string; t: number; size?: number }> = ({ text, t, size = 64 }) => (
  <Words text={text} t={t} at={0} step={0.06} style={{ fontFamily: HEAD, fontWeight: 800, fontSize: size, color: INK, lineHeight: 1.1, letterSpacing: -1, marginBottom: 30 }} />
);

// Listenpunkt mit Fokus-Hervorhebung
export const FItem: React.FC<{ item: Item; t: number; at: number; next: number; kb: number; size: number; num?: number; indent?: number }> = ({ item, t, at, next, kb, size, num, indent = 0 }) => {
  const p = sp(t, at);
  const f = focus(t, at, next);
  const past = ramp(t, next, next + 0.3);
  return (
    <div
      style={{
        display: "flex", alignItems: "center", gap: 22, margin: "7px 0", marginLeft: indent, padding: "10px 22px 10px 18px", borderRadius: 14,
        opacity: p * (1 - past * 0.45), transform: `translateX(${(1 - p) * -90}px) scale(${1 + f * 0.015})`, transformOrigin: "left center",
        background: `rgba(45,212,191,${0.1 * f})`, boxShadow: f > 0.01 ? `inset 5px 0 0 ${accent(kb)}` : "none",
      }}
    >
      {num !== undefined ? (
        <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: size * 0.8, color: accent(kb), width: size * 1.1, flexShrink: 0 }}>{String(num).padStart(2, "0")}</div>
      ) : (
        <div style={{ width: 12, height: 12, borderRadius: 3, background: accent(kb), flexShrink: 0, transform: `scale(${0.6 + p * 0.4 + f * 0.4}) rotate(${(1 - p) * 90}deg)` }} />
      )}
      <div>
        <div style={{ fontFamily: SANS, fontWeight: 600 + Math.round(f * 1.5) * 100, fontSize: size, color: INK, lineHeight: 1.25 }}>{item.text}</div>
        {item.sub ? <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: size * 0.7, color: MUTED }}>{item.sub}</div> : null}
      </div>
    </div>
  );
};

export const nextOf = (cs: number[], i: number) => (i + 1 < cs.length && cs[i + 1] > 0 ? cs[i + 1] : 999);

export const GNote: React.FC<{ text?: string; t: number; at: number; kb: number }> = ({ text, t, at, kb }) => {
  if (!text) return null;
  const p = sp(t, at);
  return (
    <div style={{ marginTop: 26, opacity: p, transform: `translateY(${(1 - p) * 30}px)` }}>
      <div style={{ display: "inline-flex", gap: 16, alignItems: "center", fontFamily: SANS, fontWeight: 650, fontSize: 31, color: INK, background: "rgba(255,255,255,0.04)", border: `1px solid ${LINE}`, borderRadius: 14, padding: "14px 24px" }}>
        <span style={{ color: accent(kb), fontFamily: LABEL, fontWeight: 800 }}>→</span>
        {text}
      </div>
    </div>
  );
};

export const GK_MOTION: Record<string, React.FC<MinProps>> = {
  topic: ({ kb, topics, topicNo, t }) => {
    const p = sp(t, 0, 16, 120);
    const w = ramp(t, 0.2, 0.9);
    return (
      <Frame>
        <div style={{ overflow: "hidden", height: 200 }}>
          <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: 190, color: accent(kb), lineHeight: 1, letterSpacing: -8, transform: `translateY(${(1 - p) * 200}px)` }}>
            {String(topicNo).padStart(2, "0")}
          </div>
        </div>
        <div style={{ width: 1100 * w, height: 3, background: `linear-gradient(90deg, ${accent(kb)}, transparent)`, margin: "26px 0 34px" }} />
        <Words text={topics[topicNo - 1]} t={t} at={0.25} step={0.09} style={{ fontFamily: HEAD, fontWeight: 850, fontSize: 96, color: INK, lineHeight: 1.04, letterSpacing: -3, maxWidth: 1200 }} />
      </Frame>
    );
  },

  points: ({ v, t, cue, kb }) => {
    const items = v.items as Item[];
    const size = items.length > 5 ? 34 : 40;
    const cs = items.map((it) => cue(it.cue));
    return (
      <Frame>
        {v.label ? <Kicker kb={kb} t={t}>{v.label}</Kicker> : null}
        <Title text={v.title} t={t} />
        {items.map((it, i) => <FItem key={i} item={it} t={t} at={cs[i]} next={nextOf(cs, i)} kb={kb} size={size} />)}
        <GNote text={v.note} t={t} at={cue(v.cueNote) || 999} kb={kb} />
      </Frame>
    );
  },

  stairs: ({ v, t, cue, kb }) => {
    const items = v.items as Item[];
    const cs = items.map((it) => cue(it.cue));
    return (
      <Frame>
        <Title text={v.title} t={t} size={58} />
        {items.map((it, i) => <FItem key={i} item={it} t={t} at={cs[i]} next={nextOf(cs, i)} kb={kb} size={38} num={i + 1} indent={i * 60} />)}
      </Frame>
    );
  },

  big: ({ v, t, cue, kb }) => {
    const p = sp(t, 0.1, 9, 120);
    const glow = 0.5 + 0.5 * Math.sin(t * 2.2);
    const items = v.items as Item[];
    const cs = items.map((it) => cue(it.cue));
    return (
      <Frame>
        {v.sub ? <Kicker kb={kb} t={t}>{v.sub}</Kicker> : null}
        <div style={{ fontFamily: HEAD, fontWeight: 900, fontSize: 150, color: accent(kb), letterSpacing: -3, lineHeight: 1, transform: `scale(${0.5 + 0.5 * p})`, transformOrigin: "left center", opacity: Math.min(1, p * 1.5), textShadow: `0 0 ${30 + glow * 30}px rgba(45,212,191,0.35)` }}>
          {v.big}
        </div>
        <div style={{ marginTop: 26 }}>
          {items.map((it, i) => <FItem key={i} item={it} t={t} at={cs[i]} next={nextOf(cs, i)} kb={kb} size={34} />)}
        </div>
      </Frame>
    );
  },

  def: ({ v, t, kb }) => {
    const u = ramp(t, 0.35, 1.0);
    return (
      <Frame>
        <Kicker kb={kb} t={t}>Definition</Kicker>
        <Words text={v.term} t={t} at={0.1} style={{ fontFamily: HEAD, fontWeight: 850, fontSize: 84, color: INK, lineHeight: 1.05, letterSpacing: -2 }} />
        <div style={{ width: 220 * u, height: 6, borderRadius: 3, background: accent(kb), margin: "16px 0 34px" }} />
        <Words text={v.text} t={t} at={0.6} step={0.045} style={{ fontFamily: SANS, fontWeight: 500, fontSize: 46, lineHeight: 1.38, color: INK, maxWidth: 1240 }} />
      </Frame>
    );
  },

  merke: ({ v, t, kb }) => {
    const h = ramp(t, 0.1, 0.6);
    const pulse = 0.5 + 0.5 * Math.sin(t * 5);
    return (
      <Frame>
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 20 }}>
          <div style={{ width: 16, height: 16, borderRadius: 8, background: accent(kb), boxShadow: `0 0 ${8 + pulse * 14}px ${accent(kb)}` }} />
          <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: 26, letterSpacing: 6, color: accent(kb) }}>MERKE</div>
        </div>
        <div style={{ position: "relative", padding: "38px 46px", background: "rgba(45,212,191,0.07)", borderRadius: 18, maxWidth: 1280 }}>
          <div style={{ position: "absolute", left: 0, top: 0, width: 10, height: `${h * 100}%`, background: accent(kb), borderRadius: 5 }} />
          <Words text={v.text} t={t} at={0.35} step={0.05} style={{ fontFamily: HEAD, fontWeight: 750, fontSize: 50, lineHeight: 1.3, color: INK }} />
        </div>
      </Frame>
    );
  },

  quiz: ({ v, t, cue, kb }) => {
    const at = cue(v.cueA) || 999;
    const shown = t >= at;
    const prog = shown ? 1 : ramp(t, 1.0, Math.max(1.5, at));
    const r = 40;
    const C = 2 * Math.PI * r;
    const pa = sp(t, at);
    return (
      <Frame>
        <Kicker kb={kb} t={t}>Kurze Frage an dich</Kicker>
        <Words text={v.q} t={t} at={0.2} step={0.06} style={{ fontFamily: HEAD, fontWeight: 800, fontSize: 60, color: INK, lineHeight: 1.2, maxWidth: 1250 }} />
        <div style={{ marginTop: 50, minHeight: 150, display: "flex", alignItems: "center", gap: 34 }}>
          <svg width={110} height={110} viewBox="0 0 110 110" style={{ flexShrink: 0 }}>
            <circle cx={55} cy={55} r={r} fill="none" stroke={LINE} strokeWidth={8} />
            <circle cx={55} cy={55} r={r} fill={shown ? "rgba(45,212,191,0.15)" : "none"} stroke={accent(kb)} strokeWidth={8} strokeLinecap="round"
              strokeDasharray={C} strokeDashoffset={C * (1 - prog)} transform="rotate(-90 55 55)" />
            {shown ? <path d="M36 56 L50 70 L76 42" fill="none" stroke={accent(kb)} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={70} strokeDashoffset={70 * (1 - pa)} /> : (
              <text x={55} y={68} textAnchor="middle" fontFamily="JetBrains Mono" fontWeight={800} fontSize={36} fill={MUTED}>?</text>
            )}
          </svg>
          {shown ? (
            <div style={{ opacity: pa, transform: `translateX(${(1 - pa) * 60}px)` }}>
              <div style={{ fontFamily: LABEL, fontWeight: 800, fontSize: 24, letterSpacing: 5, color: accent(kb), marginBottom: 8 }}>ANTWORT</div>
              <div style={{ fontFamily: SANS, fontWeight: 650, fontSize: 44, color: INK, lineHeight: 1.3, maxWidth: 1050 }}>{v.a}</div>
            </div>
          ) : (
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 34, color: MUTED, opacity: 0.6 + 0.4 * Math.sin(t * 4) }}>Überleg kurz …</div>
          )}
        </div>
      </Frame>
    );
  },

  case: ({ v, t, cue, kb }) => {
    const items = v.items as Item[];
    const cs = items.map((it) => cue(it.cue));
    const n = items.length;
    return (
      <Frame>
        <Kicker kb={kb} t={t}>{v.title}</Kicker>
        <div style={{ position: "relative", display: "flex", gap: 30, width: "100%", marginTop: 20 }}>
          {items.map((it, i) => {
            const p = sp(t, cs[i], 10, 160);
            const f = focus(t, cs[i], nextOf(cs, i));
            const lineW = i < n - 1 ? ramp(t, cs[i] + 0.2, (cs[i + 1] || cs[i] + 1) ) : 0;
            return (
              <div key={i} style={{ flex: 1, position: "relative" }}>
                {i < n - 1 ? (
                  <div style={{ position: "absolute", top: 40, left: 90, right: -20, height: 3, background: LINE }}>
                    <div style={{ width: `${lineW * 100}%`, height: 3, background: accent(kb) }} />
                  </div>
                ) : null}
                <div style={{ width: 80, height: 80, borderRadius: 40, border: `4px solid ${accent(kb)}`, background: f > 0.05 ? accent(kb) : "#0d1219", color: f > 0.5 ? "#0d1219" : accent(kb),
                  display: "flex", alignItems: "center", justifyContent: "center", fontFamily: LABEL, fontWeight: 800, fontSize: 34, transform: `scale(${p * (1 + f * 0.12)})`, position: "relative", boxShadow: f > 0.05 ? `0 0 ${30 * f}px rgba(45,212,191,0.5)` : "none" }}>
                  {i + 1}
                </div>
                <div style={{ marginTop: 26, fontFamily: SANS, fontWeight: 650, fontSize: n > 3 ? 32 : 36, color: INK, lineHeight: 1.3, opacity: p, transform: `translateY(${(1 - p) * 30}px)`, paddingRight: 10 }}>{it.text}</div>
              </div>
            );
          })}
        </div>
      </Frame>
    );
  },

  table: ({ v, t, cue, kb }) => {
    const head = v.head as string[];
    const rows = v.rows as any[];
    const cs = rows.map((r) => cue(r.cue));
    const cols = head.length === 4 ? "1fr 1fr 1fr 1fr" : head.length === 3 ? "1fr 1fr 1.3fr" : "1fr 1.3fr";
    return (
      <Frame>
        <Title text={v.title} t={t} size={56} />
        <div style={{ width: "100%", display: "grid", gridTemplateColumns: cols, columnGap: 0 }}>
          {head.map((h, i) => (
            <div key={i} style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 20, letterSpacing: 4, color: MUTED, textTransform: "uppercase", padding: "0 18px 12px", borderBottom: `2px solid ${LINE}`, opacity: sp(t, 0.2) }}>{h}</div>
          ))}
          {rows.map((r, i) => {
            const p = sp(t, cs[i]);
            const f = focus(t, cs[i], nextOf(cs, i));
            return (r.cells as string[]).map((c, k) => (
              <div key={`${i}-${k}`} style={{ fontFamily: SANS, fontWeight: k === 0 ? 750 : 500, fontSize: 32, color: k === 0 && f > 0.3 ? accent(kb) : INK, padding: "16px 18px", borderBottom: `1px solid ${LINE}`,
                opacity: p * (1 - ramp(t, nextOf(cs, i), nextOf(cs, i) + 0.3) * 0.35), transform: `translateX(${(1 - p) * (80 + k * 40)}px)`, background: `rgba(45,212,191,${0.09 * f})` }}>{c}</div>
            ));
          })}
        </div>
        <GNote text={v.note} t={t} at={cue(v.cueNote) || (cs[cs.length - 1] || 0) + 1.2} kb={kb} />
      </Frame>
    );
  },

  compare: ({ v, t, cue, kb }) => {
    const atR = cue(v.cueRight);
    const col = (s: any, at: number, strong: boolean) => {
      const p = sp(t, at);
      return (
        <div style={{ flex: 1, opacity: p, transform: `translateX(${(1 - p) * (strong ? 100 : -100)}px)` }}>
          <div style={{ fontFamily: HEAD, fontWeight: 800, fontSize: 48, color: strong ? accent(kb) : INK, marginBottom: 20 }}>{s.title}</div>
          {s.items.map((x: string, i: number) => {
            const q = sp(t, at + 0.25 + i * 0.18);
            return (
              <div key={i} style={{ fontFamily: SANS, fontWeight: 550, fontSize: s.items.length > 3 ? 31 : 35, color: INK, padding: "12px 0", borderTop: `1px solid ${LINE}`, opacity: q, transform: `translateY(${(1 - q) * 20}px)` }}>{x}</div>
            );
          })}
        </div>
      );
    };
    const d = ramp(t, 0.1, 0.8);
    return (
      <Frame>
        <div style={{ display: "flex", gap: 70, width: "100%" }}>
          {col(v.left, 0, false)}
          <div style={{ width: 3, background: LINE, position: "relative" }}>
            <div style={{ position: "absolute", top: 0, width: 3, height: `${d * 100}%`, background: `linear-gradient(${accent(kb)}, transparent)` }} />
          </div>
          {col(v.right, atR, true)}
        </div>
        <GNote text={v.note} t={t} at={cue(v.cueNote) || 999} kb={kb} />
      </Frame>
    );
  },
};
