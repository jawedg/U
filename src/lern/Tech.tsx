// Technik-Grafiken (dunkles Design): Behälter mit Ultraschallsensor, Schaubild, Skalen (Volt ↔ Digitalwert), Rechenweg.
import React from "react";
import { interpolate } from "remotion";
import type { MinProps } from "./Min";
import { BGC, fz, Frame, HEAD, INK, LABEL, LINE, MUTED, SANS, accent, accent2, monoF, water, withA } from "./Min";
import { FItem, Kicker, nextOf, ramp, sp } from "./MinGK";

const fmt = (x: number, d = 1) => x.toLocaleString("de-DE", { maximumFractionDigits: d });
const at0 = (cue: (c?: string) => number, c?: string | number) => (typeof c === "number" ? c : c ? cue(c) || 999 : 0);

// ------------------------------------------------------------------ Behälter
// v: { title, range (cm), vTop, vBot, levels: [[cue|sek, füllgrad 0..1]], show: {blind, scale, abstand, fuell}, items?, label? }
const Tank: React.FC<MinProps> = ({ v, t, cue, kb }) => {
  const W = 820, H = 800;
  const tx = 230, tw = 300, top = 100, bot = 760, b1 = 180, b2 = 720; // Behälter, Blindzonen
  const show = (k: string) => (v.show?.[k] !== undefined ? ramp(t, at0(cue, v.show[k]), at0(cue, v.show[k]) + 0.5) : 0);
  // Füllgrad aus Keyframes
  const ks: [number, number][] = (v.levels ?? [[0, 0.5]]).map(([c, l]: [string | number, number]) => [at0(cue, c), l]);
  let lvl = ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    const [a, l] = ks[i];
    const e = interpolate(t, [a, a + 1.4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const ee = e < 0.5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2;
    lvl = lvl + (l - lvl) * ee;
  }
  const surf = b2 - lvl * (b2 - b1);
  const wave = Math.sin(t * 3) * 3;
  // Ultraschall-Wellen
  const arcs = [0, 1, 2].map((i) => {
    const per = 1.6;
    const ph = ((t + i * (per / 3)) % per) / per;
    const y = top + 10 + ph * (surf - top - 10);
    return { y, o: Math.sin(ph * Math.PI) };
  });
  const items = (v.items ?? []) as { text: string; cue: string }[];
  const cs = items.map((it) => cue(it.cue));
  const vAt = (frac: number) => v.vTop + (v.vBot - v.vTop) * frac; // Spannung bei Abstand-Anteil
  const sc = show("scale"), ab = show("abstand"), fh = show("fuell"), bl = show("blind");
  const dist = (1 - lvl) * v.range;
  return (
    <div style={{ display: "flex", height: "100%", alignItems: "center", padding: "0 40px 0 60px", gap: 30 }}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{ flexShrink: 0 }}>
        {/* Sensor */}
        <rect x={tx + tw / 2 - 34} y={top - 52} width={68} height={52} rx={8} fill="rgba(0,0,0,0.25)" stroke={INK} strokeWidth={3} />
        <text x={tx + tw / 2} y={top - 62} textAnchor="middle" fontFamily={SANS} fontSize={24 * fz(kb)} fill={MUTED}>Sensor</text>
        {/* Behälter */}
        <rect x={tx} y={top} width={tw} height={bot - top} rx={10} fill="rgba(255,255,255,0.03)" stroke={INK} strokeWidth={4} />
        {/* Flüssigkeit */}
        <path d={`M${tx + 4} ${surf + wave} Q${tx + tw / 2} ${surf - wave * 2} ${tx + tw - 4} ${surf + wave} L${tx + tw - 4} ${bot - 4} L${tx + 4} ${bot - 4} Z`} fill={withA(water(kb), 0.3)} stroke={water(kb)} strokeWidth={3} />
        {/* Blindzonen */}
        <g opacity={bl}>
          <rect x={tx + 3} y={top + 3} width={tw - 6} height={b1 - top - 3} fill={withA(accent2(kb), 0.1)} />
          <rect x={tx + 3} y={b2} width={tw - 6} height={bot - b2 - 3} fill={withA(accent2(kb), 0.1)} />
          <line x1={tx} x2={tx + tw} y1={b1} y2={b1} stroke={accent2(kb)} strokeWidth={2} strokeDasharray="8 8" />
          <line x1={tx} x2={tx + tw} y1={b2} y2={b2} stroke={accent2(kb)} strokeWidth={2} strokeDasharray="8 8" />
          <text x={tx + tw / 2} y={(top + b1) / 2 + 9} textAnchor="middle" fontFamily={SANS} fontSize={24 * fz(kb)} fill={accent2(kb)}>Blindzone</text>
        </g>
        {/* Ultraschall */}
        {arcs.map((a, i) => (
          <path key={i} d={`M${tx + tw / 2 - 50} ${a.y} Q${tx + tw / 2} ${a.y + 22} ${tx + tw / 2 + 50} ${a.y}`} fill="none" stroke={INK} strokeWidth={3} opacity={a.o * 0.6} />
        ))}
        {/* Abstand-Pfeil (von oben) */}
        <g opacity={ab}>
          <line x1={tx - 40} x2={tx - 40} y1={b1} y2={surf} stroke={accent2(kb)} strokeWidth={4} />
          <path d={`M${tx - 50} ${b1 + 14} L${tx - 40} ${b1} L${tx - 30} ${b1 + 14} M${tx - 50} ${surf - 14} L${tx - 40} ${surf} L${tx - 30} ${surf - 14}`} fill="none" stroke={accent2(kb)} strokeWidth={4} />
          <text x={tx - 56} y={(b1 + surf) / 2} textAnchor="end" fontFamily={SANS} fontWeight={700} fontSize={26 * fz(kb)} fill={accent2(kb)}>Abstand</text>
          <text x={tx - 56} y={(b1 + surf) / 2 + 32} textAnchor="end" fontFamily={monoF(kb)} fontSize={24 * fz(kb)} fill={accent2(kb)}>{fmt(dist, 0)} cm</text>
        </g>
        {/* Füllhöhe-Pfeil (von unten) */}
        <g opacity={fh}>
          <line x1={tx - 110} x2={tx - 110} y1={b2} y2={surf} stroke={accent(kb)} strokeWidth={4} />
          <path d={`M${tx - 120} ${b2 - 14} L${tx - 110} ${b2} L${tx - 100} ${b2 - 14} M${tx - 120} ${surf + 14} L${tx - 110} ${surf} L${tx - 100} ${surf + 14}`} fill="none" stroke={accent(kb)} strokeWidth={4} />
          <text x={tx - 118} y={(b2 + surf) / 2 + 8} textAnchor="end" fontFamily={SANS} fontWeight={700} fontSize={26 * fz(kb)} fill={accent(kb)} transform={`rotate(-90 ${tx - 128} ${(b2 + surf) / 2})`}>Füllhöhe</text>
        </g>
        {/* Spannungsskala */}
        <g opacity={sc}>
          {[
            [top, "0 V", ""],
            [b1, `${fmt(v.vTop)} V`, "0 cm"],
            [b2, `${fmt(v.vBot)} V`, `${v.range} cm`],
            [bot, "10 V", ""],
          ].map(([y, a, b], i) => (
            <g key={i}>
              <line x1={tx + tw + 8} x2={tx + tw + 40} y1={y as number} y2={y as number} stroke={MUTED} strokeWidth={3} />
              <text x={tx + tw + 52} y={(y as number) + 9} fontFamily={monoF(kb)} fontWeight={700} fontSize={28 * fz(kb)} fill={INK}>{a}</text>
              <text x={tx + tw + 170} y={(y as number) + 9} fontFamily={monoF(kb)} fontSize={24 * fz(kb)} fill={MUTED}>{b}</text>
            </g>
          ))}
          <line x1={tx + tw + 24} x2={tx + tw + 24} y1={top} y2={bot} stroke={LINE} strokeWidth={3} />
          {/* aktuelle Spannung */}
          <circle cx={tx + tw + 24} cy={surf} r={9} fill={accent(kb)} />
          <text x={tx + tw + 52} y={surf - 14} fontFamily={monoF(kb)} fontWeight={800} fontSize={26 * fz(kb)} fill={accent(kb)}>{fmt(vAt(dist / v.range), 2)} V</text>
        </g>
      </svg>
      <div style={{ flex: 1 }}>
        {v.label ? <Kicker kb={kb} t={t}>{v.label}</Kicker> : null}
        {v.title ? <div style={{ fontFamily: HEAD, fontWeight: 800, fontSize: 50, color: INK, lineHeight: 1.1, marginBottom: 20, opacity: sp(t, 0) }}>{v.title}</div> : null}
        {items.map((it, i) => <FItem key={i} item={it} t={t} at={cs[i]} next={nextOf(cs, i)} kb={kb} size={32} />)}
      </div>
    </div>
  );
};

// ------------------------------------------------------------------ Schaubild
// v: { title, xMax, xStep, yMax, xLabel, yLabel, points: [{x,y,cue,label}], lineCue, slope: {cue, dx, dy}, mark: {x, cue, label}, formula: {text, cue} }
const Graph: React.FC<MinProps> = ({ v, t, cue, kb }) => {
  const W = 1180, H = 700, ox = 120, oy = 600, aw = 820, ah = 520;
  const X = (x: number) => ox + (x / v.xMax) * aw;
  const Y = (y: number) => oy - (y / v.yMax) * ah;
  const ax = ramp(t, 0, 0.8);
  const pts = (v.points ?? []) as { x: number; y: number; cue: string; label: string }[];
  const lc = at0(cue, v.lineCue);
  const lineP = ramp(t, lc, lc + 0.9);
  const [p1, p2] = pts;
  const sl = v.slope ? ramp(t, at0(cue, v.slope.cue), at0(cue, v.slope.cue) + 0.8) : 0;
  const mk = v.mark ? ramp(t, at0(cue, v.mark.cue), at0(cue, v.mark.cue) + 1.0) : 0;
  const yAt = (x: number) => p1.y + ((p2.y - p1.y) * (x - p1.x)) / (p2.x - p1.x);
  const fo = v.formula ? sp(t, at0(cue, v.formula.cue)) : 0;
  const xs: number[] = [];
  for (let x = 0; x <= v.xMax; x += v.xStep) xs.push(x);
  return (
    <div style={{ height: "100%", padding: kb === 6 ? "0 0 0 330px" : "0 0 0 90px", display: "flex", flexDirection: "column", justifyContent: "center" }}>
      {v.title ? <Kicker kb={kb} t={t}>{v.title}</Kicker> : null}
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`}>
        {/* Gitter */}
        {xs.map((x) => <line key={`gx${x}`} x1={X(x)} x2={X(x)} y1={oy} y2={oy - ah * ax} stroke={LINE} strokeWidth={1} />)}
        {Array.from({ length: v.yMax + 1 }, (_, y) => <line key={`gy${y}`} x1={ox} x2={ox + aw * ax} y1={Y(y)} y2={Y(y)} stroke={LINE} strokeWidth={1} />)}
        {/* Achsen */}
        <line x1={ox} x2={ox + (aw + 30) * ax} y1={oy} y2={oy} stroke={INK} strokeWidth={3} />
        <line x1={ox} x2={ox} y1={oy} y2={oy - (ah + 30) * ax} stroke={INK} strokeWidth={3} />
        <text x={ox + aw + 20} y={oy + 60} textAnchor="end" fontFamily={SANS} fontWeight={700} fontSize={26 * fz(kb)} fill={INK} opacity={ax}>{v.xLabel}</text>
        <text x={ox - 14} y={oy - ah - 44} fontFamily={SANS} fontWeight={700} fontSize={26 * fz(kb)} fill={INK} opacity={ax}>{v.yLabel}</text>
        {xs.map((x) => <text key={`tx${x}`} x={X(x)} y={oy + 34} textAnchor="middle" fontFamily={monoF(kb)} fontSize={22 * fz(kb)} fill={MUTED} opacity={ax}>{x}</text>)}
        {Array.from({ length: v.yMax + 1 }, (_, y) => <text key={`ty${y}`} x={ox - 16} y={Y(y) + 8} textAnchor="end" fontFamily={monoF(kb)} fontSize={22 * fz(kb)} fill={MUTED} opacity={ax}>{y}</text>)}
        {/* Gerade */}
        {p1 && p2 ? (
          <line x1={X(p1.x)} y1={Y(p1.y)} x2={X(p1.x + (p2.x - p1.x) * lineP)} y2={Y(p1.y + (p2.y - p1.y) * lineP)} stroke={accent(kb)} strokeWidth={6} strokeLinecap="round" />
        ) : null}
        {/* Steigungsdreieck */}
        {v.slope && sl > 0 ? (
          <g opacity={sl}>
            <line x1={X(p1.x)} y1={Y(p1.y)} x2={X(p2.x)} y2={Y(p1.y)} stroke={accent2(kb)} strokeWidth={3} strokeDasharray="10 8" />
            <line x1={X(p2.x)} y1={Y(p1.y)} x2={X(p2.x)} y2={Y(p2.y)} stroke={accent2(kb)} strokeWidth={3} strokeDasharray="10 8" />
            <text x={(X(p1.x) + X(p2.x)) / 2} y={Y(p1.y) - 16} textAnchor="middle" fontFamily={monoF(kb)} fontWeight={700} fontSize={26 * fz(kb)} fill={accent2(kb)}>{v.slope.dx}</text>
            <text x={X(p2.x) + 14} y={(Y(p1.y) + Y(p2.y)) / 2} fontFamily={monoF(kb)} fontWeight={700} fontSize={26 * fz(kb)} fill={accent2(kb)}>{v.slope.dy}</text>
          </g>
        ) : null}
        {/* Ablesen */}
        {v.mark && mk > 0 ? (
          <g>
            <line x1={X(v.mark.x)} y1={oy} x2={X(v.mark.x)} y2={oy - (oy - Y(yAt(v.mark.x))) * Math.min(1, mk * 2)} stroke={INK} strokeWidth={3} strokeDasharray="8 8" />
            {mk > 0.5 ? <line x1={X(v.mark.x)} y1={Y(yAt(v.mark.x))} x2={X(v.mark.x) - (X(v.mark.x) - ox) * (mk - 0.5) * 2} y2={Y(yAt(v.mark.x))} stroke={INK} strokeWidth={3} strokeDasharray="8 8" /> : null}
            <circle cx={X(v.mark.x)} cy={Y(yAt(v.mark.x))} r={10 * Math.min(1, mk * 2)} fill={INK} />
            <text x={X(v.mark.x) + 18} y={Y(yAt(v.mark.x)) - 16} fontFamily={monoF(kb)} fontWeight={800} fontSize={28 * fz(kb)} fill={INK} opacity={mk}>{v.mark.label}</text>
          </g>
        ) : null}
        {/* Punkte */}
        {pts.map((p, i) => {
          const s = sp(t, at0(cue, p.cue), 9, 170);
          return (
            <g key={i} opacity={Math.min(1, s * 1.5)}>
              <line x1={ox} x2={X(p.x)} y1={Y(p.y)} y2={Y(p.y)} stroke={accent(kb)} strokeWidth={2} strokeDasharray="6 8" opacity={0.6} />
              <line x1={X(p.x)} x2={X(p.x)} y1={oy} y2={Y(p.y)} stroke={accent(kb)} strokeWidth={2} strokeDasharray="6 8" opacity={0.6} />
              <circle cx={X(p.x)} cy={Y(p.y)} r={14 * s} fill={accent(kb)} stroke={BGC(kb)} strokeWidth={4} />
              <text x={X(p.x) + (p.x > v.xMax * 0.7 ? -22 : 22)} y={Y(p.y) + (p.x > v.xMax * 0.7 ? 46 : -22)} textAnchor={p.x > v.xMax * 0.7 ? "end" : "start"} fontFamily={monoF(kb)} fontWeight={800} fontSize={28 * fz(kb)} fill={accent(kb)}>{p.label}</text>
            </g>
          );
        })}
      </svg>
      {v.formula ? (
        <div style={{ marginTop: -10, marginLeft: 120, opacity: fo, transform: `translateY(${(1 - fo) * 20}px)`, fontFamily: monoF(kb), fontWeight: 700, fontSize: 34, color: INK, background: withA(accent(kb), 0.08), border: `1px solid ${LINE}`, borderRadius: 12, padding: "12px 22px", display: "inline-block", alignSelf: "flex-start" }}>
          {v.formula.text}
        </div>
      ) : null}
    </div>
  );
};

// ------------------------------------------------------------------ Skalen Volt ↔ Digitalwert
// v: { title, markers: [{v, cue, top, bottom}] }
const Scales: React.FC<MinProps> = ({ v, t, cue, kb }) => {
  const x0 = 140, len = 1100, yV = 230, yD = 520;
  const ax = ramp(t, 0, 0.9);
  const X = (u: number) => x0 + (u / 10) * len;
  const ms = (v.markers ?? []) as { v: number; cue: string; top: string; bottom: string }[];
  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "center", paddingLeft: 40 }}>
      {v.title ? <div style={{ paddingLeft: 80 }}><Kicker kb={kb} t={t}>{v.title}</Kicker></div> : null}
      <svg width={1400} height={700} viewBox="0 0 1400 700">
        {[[yV, "Spannung"], [yD, "Digitalwert"]].map(([y, l], i) => (
          <g key={i}>
            <text x={x0} y={(y as number) - (i === 0 ? 100 : 60)} fontFamily={SANS} fontWeight={700} fontSize={28 * fz(kb)} fill={MUTED}>{l}</text>
            <rect x={x0} y={(y as number) - 16} width={len * ax} height={32} rx={16} fill="rgba(255,255,255,0.05)" stroke={LINE} strokeWidth={2} />
          </g>
        ))}
        {Array.from({ length: 11 }, (_, u) => (
          <g key={u} opacity={ax}>
            <line x1={X(u)} x2={X(u)} y1={yV - 22} y2={yV + 22} stroke={MUTED} strokeWidth={2} />
            <text x={X(u)} y={yV + 56} textAnchor="middle" fontFamily={monoF(kb)} fontSize={22 * fz(kb)} fill={MUTED}>{u} V</text>
          </g>
        ))}
        {[0, 5, 10].map((u) => (
          <g key={`d${u}`} opacity={ax}>
            <line x1={X(u)} x2={X(u)} y1={yD - 22} y2={yD + 22} stroke={MUTED} strokeWidth={2} />
            <text x={X(u)} y={yD + 56} textAnchor="middle" fontFamily={monoF(kb)} fontSize={22 * fz(kb)} fill={MUTED}>{fmt(u * 2764.8, 0)}</text>
          </g>
        ))}
        {ms.map((m, i) => {
          const p = sp(t, at0(cue, m.cue));
          const d = ramp(t, at0(cue, m.cue) + 0.2, at0(cue, m.cue) + 0.9);
          return (
            <g key={i} opacity={Math.min(1, p * 1.4)}>
              <line x1={X(m.v)} x2={X(m.v)} y1={yV} y2={yV + (yD - yV) * d} stroke={accent(kb)} strokeWidth={4} strokeDasharray="12 10" />
              <circle cx={X(m.v)} cy={yV} r={13 * p} fill={accent(kb)} />
              <circle cx={X(m.v)} cy={yD} r={13 * d} fill={accent2(kb)} />
              <text x={X(m.v)} y={yV - 34} textAnchor="middle" fontFamily={monoF(kb)} fontWeight={800} fontSize={32 * fz(kb)} fill={accent(kb)}>{m.top}</text>
              <text x={X(m.v)} y={yD + 100} textAnchor="middle" fontFamily={monoF(kb)} fontWeight={800} fontSize={32 * fz(kb)} fill={accent2(kb)} opacity={d}>{m.bottom}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

// ------------------------------------------------------------------ Rechenweg
// v: { title, lines: [{t, cue, kind: "step"|"result"|"note"}] }
const Calc: React.FC<MinProps> = ({ v, t, cue, kb }) => {
  const lines = (v.lines ?? []) as { t: string; cue: string | number; kind?: string }[];
  return (
    <Frame>
      {v.title ? <Kicker kb={kb} t={t}>{v.title}</Kicker> : null}
      {v.head ? <div style={{ fontFamily: HEAD, fontWeight: 800, fontSize: 52, color: INK, marginBottom: 26, opacity: sp(t, 0) }}>{v.head}</div> : null}
      {lines.map((ln, i) => {
        const a = at0(cue, ln.cue);
        const p = sp(t, a);
        const typed = Math.round(ln.t.length * ramp(t, a, a + Math.min(1.2, 0.03 * ln.t.length)));
        const res = ln.kind === "result";
        const note = ln.kind === "note";
        return (
          <div key={i} style={{ opacity: Math.min(1, p * 1.5), transform: `translateX(${(1 - p) * -40}px)`, margin: res ? "16px 0" : "8px 0" }}>
            <div style={{
              display: "inline-block", fontFamily: note ? SANS : monoF(kb), fontWeight: res ? 800 : 600, fontSize: (note ? 32 : res ? 44 : 40) * (kb === 6 && !note ? 1.4 : 1), color: res ? accent(kb) : note ? MUTED : INK,
              padding: res ? "12px 26px" : "4px 0", border: res ? `3px solid ${accent(kb)}` : "none", borderRadius: 14, background: res ? withA(accent(kb), 0.08) : "transparent",
              boxShadow: res ? `0 0 ${24 * p}px ${withA(accent(kb), 0.25)}` : "none", whiteSpace: "pre",
            }}>
              {ln.t.slice(0, typed)}
              {typed < ln.t.length ? <span style={{ color: accent(kb) }}>▍</span> : null}
            </div>
          </div>
        );
      })}
    </Frame>
  );
};

export const TECH: Record<string, React.FC<MinProps>> = { tank: Tank, graph: Graph, scales: Scales, calc: Calc };
