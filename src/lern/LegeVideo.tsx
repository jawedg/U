// Gemeinschaftskunde – Variante 2: Legetechnik.
// Weißes Papier, gezeichnete Symbole als Papier-Ausschnitte und handgeschriebene Zettel,
// die von einer (gezeichneten) Hand ins Bild geschoben werden.
import "@fontsource/caveat/500.css";
import "@fontsource/caveat/700.css";
import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { DATA, LFPS, Scene, Word, cueFn, durF, info, lead } from "./LernVideo";
import { HandArt, ICON_FOR_TEXT, INK_L, Icon, TOPIC_ICON, iconFor } from "./LegeIcons";

const HF = "Caveat, cursive";
const RED = "#d9482b";
const YELLOW = "#fde68a";
const GREENP = "#e3f2d6";
const GRAY = "#8a8476";
const KB = 5;

type From = "left" | "right" | "top" | "bottom" | "fade";
type Piece = { key: string; x: number; y: number; w: number; h: number; at: number; from: From; rot?: number; hand?: boolean; node: (t: number) => React.ReactNode };
type Extra = (t: number) => React.ReactNode;

const rnd = (seed: number) => {
  const x = Math.sin(seed * 999.13) * 10000;
  return x - Math.floor(x);
};
const ramp = (t: number, a: number, b: number) => interpolate(t, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
const CHW = 0.38; // mittlere Zeichenbreite von Caveat (in em)
const textW = (s: string, size: number) => s.length * size * CHW;

// Schriftgröße so wählen, dass der Text in die Box passt (grobe Zeilenumbruch-Schätzung)
const lines = (text: string, w: number, size: number) => {
  const cpl = Math.max(4, Math.floor(w / (size * CHW)));
  let n = 1, cur = 0;
  for (const word of text.split(" ")) {
    const l = word.length;
    if (cur > 0 && cur + 1 + l > cpl) { n++; cur = l; } else cur += (cur ? 1 : 0) + l;
  }
  return n;
};
const longest = (text: string) => Math.max(...text.split(" ").map((x) => x.length));
const fit = (text: string, w: number, h: number, max: number, min = 26, lh = 1.12) => {
  for (let s = max; s > min; s -= 2) if (lines(text, w, s) * s * lh <= h && longest(text) * s * CHW <= w) return s;
  return min;
};

// Papierstück mit leicht unregelmäßig geschnittenem Rand
const Paper: React.FC<{ w: number; h: number; seed: number; bg?: string; children?: React.ReactNode; pad?: number; style?: React.CSSProperties }> = ({ w, h, seed, bg = "#fff", children, pad = 30, style }) => {
  const pts: string[] = [];
  const j = (k: number) => (rnd(seed * 7 + k) * 5).toFixed(1);
  const n = 5;
  for (let i = 0; i < n; i++) pts.push(`${((w * i) / n).toFixed(0)}px ${j(i)}px`);
  for (let i = 0; i < n; i++) pts.push(`calc(100% - ${j(i + 10)}px) ${((h * i) / n).toFixed(0)}px`);
  for (let i = n; i > 0; i--) pts.push(`${((w * i) / n).toFixed(0)}px calc(100% - ${j(i + 20)}px)`);
  for (let i = n; i > 0; i--) pts.push(`${j(i + 30)}px ${((h * i) / n).toFixed(0)}px`);
  return (
    <div style={{ width: w, height: h, filter: "drop-shadow(2px 5px 4px rgba(0,0,0,0.20))" }}>
      <div style={{ width: w, height: h, background: bg, clipPath: `polygon(${pts.join(",")})`, padding: pad, boxSizing: "border-box", ...style }}>{children}</div>
    </div>
  );
};

const HText: React.FC<{ size: number; color?: string; weight?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ size, color = INK_L, weight = 600, children, style }) => (
  <div style={{ fontFamily: HF, fontSize: size, fontWeight: weight, color, lineHeight: 1.08, ...style }}>{children}</div>
);

// handschriftliches „Schreiben“: Text wird von links nach rechts aufgedeckt
const Write: React.FC<{ t: number; at: number; dur?: number; children: React.ReactNode }> = ({ t, at, dur = 0.5, children }) => {
  const q = ramp(t, at, at + dur);
  return <div style={{ clipPath: `inset(-10px ${(1 - q) * 100}% -10px -10px)` }}>{children}</div>;
};

// gezeichnete Linie (z. B. Unterstreichung, Pfeil), die sich selbst zeichnet
const Draw: React.FC<{ d: string; t: number; at: number; dur?: number; color?: string; sw?: number; len?: number }> = ({ d, t, at, dur = 0.5, color = RED, sw = 7, len = 1400 }) => (
  <path d={d} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - ramp(t, at, at + dur))} />
);

const strip = (key: string, text: string, x: number, y: number, size: number, at: number, from: From, o: { color?: string; bg?: string; weight?: number; seed?: number; maxW?: number; rot?: number; hand?: boolean } = {}): Piece => {
  const w = Math.min(o.maxW ?? 1700, textW(text, size) + 70);
  const ls = lines(text, w - 40, size);
  const h = ls * size * 1.1 + 40;
  return {
    key, x, y, w, h, at, from, rot: o.rot ?? (rnd(o.seed ?? x + y) - 0.5) * 3, hand: o.hand,
    node: () => (
      <Paper w={w} h={h} seed={o.seed ?? x + y} bg={o.bg} pad={20}>
        <HText size={size} color={o.color} weight={o.weight ?? 700} style={{ paddingLeft: 10 }}>{text}</HText>
      </Paper>
    ),
  };
};
const iconPiece = (key: string, name: string, x: number, y: number, size: number, at: number, from: From, rot = 0, hand = true): Piece => ({
  key, x, y, w: size, h: size, at, from, rot, hand, node: () => <Icon name={name} size={size} />,
});
const sideOf = (cx: number): From => (cx < 700 ? "left" : cx > 1220 ? "right" : "bottom");

// Karte: Symbol + Text
const card = (key: string, text: string, x: number, y: number, w: number, h: number, at: number, seed: number, o: { num?: number; icon?: string | null; bg?: string } = {}): Piece => {
  const icon = o.icon === null ? undefined : o.icon ?? iconFor(text);
  const vertical = h >= 280 && w < 720;
  const isz = icon ? (vertical ? Math.min(h * 0.42, w * 0.5, 180) : Math.min(h * 0.72, 150)) : 0;
  const tw = vertical ? w - 60 : w - isz - 90;
  const th = vertical ? h - isz - 70 : h - 50;
  const fs = fit(text, tw, th, 54, 28);
  return {
    key, x, y, w, h, at, from: sideOf(x + w / 2), rot: (rnd(seed) - 0.5) * 3.5,
    node: () => (
      <Paper w={w} h={h} seed={seed} bg={o.bg} pad={22}>
        <div style={{ display: "flex", flexDirection: vertical ? "column" : "row", alignItems: "center", justifyContent: "center", gap: vertical ? 12 : 24, height: "100%", textAlign: vertical ? "center" : "left" }}>
          {icon ? <Icon name={icon} size={isz} cut={false} /> : null}
          <HText size={fs} weight={600} style={{ maxWidth: tw }}>
            {o.num !== undefined ? <span style={{ color: RED, fontWeight: 700 }}>{o.num}. </span> : null}
            {text}
          </HText>
        </div>
      </Paper>
    ),
  };
};

const noteP = (text: string | undefined, at: number, y = 778): Piece[] =>
  text ? [strip("note", text, 120, y, 46, at, "bottom", { bg: YELLOW, weight: 600, rot: -1.2, maxW: 1680 })] : [];

type Built = { pieces: Piece[]; extras: Extra[] };

const build = (sc: Scene, cue: (c?: string) => number, D: number, topics: string[], i: number): Built => {
  const v = sc.v;
  const P: Piece[] = [];
  const E: Extra[] = [];
  const seed = i * 31 + 7;
  const title = (text: string, at = 0) => P.push(strip("title", text, 120, 46, 72, at, "top", { seed, rot: -0.8, hand: false }));

  switch (v.type) {
    case "kb": {
      const outro = !!v.outro;
      P.push(strip("sub", outro ? "Alle Themen durch!" : "WiSo-Abschlussprüfung", 960 - 260, 250, 54, 0, "left", { color: "#fff", bg: RED, seed: 3, rot: -2 }));
      const big = outro ? "Geschafft!" : "Gemeinschaftskunde";
      P.push(strip("title", big, 960 - (textW(big, 150) + 70) / 2, 340, 150, 0.3, "top", { seed: 5, rot: 1 }));
      TOPIC_ICON.forEach((ic, k) => {
        const top = k < 5;
        const col = k % 5;
        const x = 150 + col * 340 + (top ? 0 : 80);
        const y = top ? 40 : 600;
        const at = outro ? 0.6 + k * 0.25 : 1.2 + (k * Math.max(4, D * 0.6)) / 10;
        P.push(iconPiece(`ic${k}`, outro ? "check" : ic, x, y, 170, at, top ? "top" : "bottom", (rnd(k + 3) - 0.5) * 12, k % 2 === 0));
      });
      break;
    }
    case "topic": {
      const n = sc.topic;
      P.push(iconPiece("icon", TOPIC_ICON[n - 1] ?? "bulb", 170, 230, 420, 0, "left", -5));
      P.push(strip("num", `Thema ${n}`, 720, 210, 70, 0.15, "top", { color: "#fff", bg: RED, seed: n, rot: -2, hand: false }));
      const name = topics[n - 1];
      const fs = fit(name, 1000, 330, 120, 60);
      P.push(strip("name", name, 720, 340, fs, 0.4, "right", { seed: n + 50, rot: 1, maxW: 1100 }));
      break;
    }
    case "def": {
      const ic = ICON_FOR_TEXT[v.term] ?? iconFor(`${v.term} ${v.text}`) ?? "pencil";
      P.push(iconPiece("icon", ic, 130, 300, 330, 0, "left", -4));
      const ts = fit(v.term, 1150, 130, 104, 60);
      const tw = Math.min(1250, textW(v.term, ts) + 70);
      P.push(strip("term", v.term, 540, 130, ts, 0.15, "top", { seed, rot: -1, maxW: 1250 }));
      E.push((t) => (
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1920} height={900}>
          <Draw d={`M560 ${130 + ts * 1.15 + 56} Q${560 + tw / 2} ${130 + ts * 1.15 + 44} ${540 + tw - 20} ${130 + ts * 1.15 + 58}`} t={t} at={0.75} len={tw + 100} />
        </svg>
      ));
      const fs = fit(v.text, 1160, 400, 62, 34);
      const h = lines(v.text, 1160, fs) * fs * 1.12 + 70;
      const y = 130 + ts * 1.15 + 100;
      P.push({
        key: "def", x: 540, y, w: 1260, h, at: 0.9, from: "right", rot: 0.8,
        node: () => (
          <Paper w={1260} h={h} seed={seed + 3} pad={34}>
            <HText size={fs} weight={500}>{v.text}</HText>
          </Paper>
        ),
      });
      break;
    }
    case "points": {
      title(v.title);
      const items = v.items as { text: string; cue: string }[];
      const n = items.length;
      const hasNote = !!v.note;
      const top = 190, bottom = hasNote ? 750 : 870;
      const c = n <= 3 ? n : n === 4 ? 2 : n <= 6 ? 3 : 4;
      const r = Math.ceil(n / c);
      const gx = 40, gy = 34;
      const cw = (1680 - (c - 1) * gx) / c;
      const ch = Math.min((bottom - top - (r - 1) * gy) / r, n <= 3 ? 470 : 340);
      const y0 = top + (bottom - top - (r * ch + (r - 1) * gy)) / 2;
      items.forEach((it, k) => {
        const row = Math.floor(k / c), col = k % c;
        const inRow = Math.min(c, n - row * c);
        const x0 = 120 + (1680 - (inRow * cw + (inRow - 1) * gx)) / 2;
        P.push(card(`it${k}`, it.text, x0 + col * (cw + gx), y0 + row * (ch + gy), cw, ch, cue(it.cue) || 0.4 + k * 0.3, seed + k));
      });
      P.push(...noteP(v.note, cue(v.cueNote) || 999));
      break;
    }
    case "compare": {
      const hasNote = !!v.note;
      const h = (hasNote ? 745 : 860) - 70;
      const atR = cue(v.cueRight) || 1;
      const sheet = (key: string, s: { title: string; items: string[] }, x: number, at: number, strong: boolean, sd: number, until: number): Piece => {
        const stepT = Math.max(0.45, (until - at - 1.2) / Math.max(1, s.items.length));
        const isPro = /^Pro/.test(s.title), isCon = /^Contra/.test(s.title);
        const ic = isPro ? "thumbsUp" : isCon ? "thumbsDown" : ICON_FOR_TEXT[s.title] ?? iconFor(`${s.title} ${s.items.join(" ")}`);
        const head = s.title.replace(/[➕➖]/g, "").trim();
        let fs = 58;
        while (fs > 28 && s.items.reduce((a, x) => a + lines(x, 660, fs), 0) * fs * 1.12 + s.items.length * 12 > h - 200) fs -= 2;
        const used = Math.min(h, 72 * 1.1 + 40 + s.items.reduce((a, x) => a + lines(x, 660, fs), 0) * fs * 1.12 + s.items.length * 12 + 120);
        const hh = Math.max(used, 420);
        return {
          key, x, y: 70 + (h - hh) / 3, w: 820, h: hh, at, from: x < 900 ? "left" : "right", rot: strong ? 1 : -1,
          node: (t) => (
            <Paper w={820} h={hh} seed={sd} pad={40}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <HText size={72} weight={700} color={strong ? RED : INK_L}>{head}</HText>
                {ic ? <div style={{ marginTop: -14 }}><Icon name={ic} size={130} cut={false} /></div> : null}
              </div>
              <svg width={600} height={16} style={{ display: "block", margin: "2px 0 14px" }}>
                <Draw d="M4 10 Q300 2 596 8" t={t} at={at + 0.35} sw={5} color={strong ? RED : INK_L} len={700} />
              </svg>
              {s.items.map((x2, k) => (
                <Write key={k} t={t} at={at + 0.6 + k * stepT}>
                  <div style={{ display: "flex", gap: 16, alignItems: "baseline", marginBottom: 12 }}>
                    <HText size={fs} weight={700} color={strong ? RED : INK_L}>–</HText>
                    <HText size={fs} weight={500}>{x2}</HText>
                  </div>
                </Write>
              ))}
            </Paper>
          ),
        };
      };
      P.push(sheet("L", v.left, 120, 0, false, seed, atR));
      P.push(sheet("R", v.right, 980, atR, true, seed + 1, Math.min(D * 0.85, (cue(v.cueNote) || 999) - 0.3)));
      P.push(...noteP(v.note, cue(v.cueNote) || 999, 790));
      break;
    }
    case "table": {
      title(v.title);
      const head = v.head as string[];
      const rows = v.rows as { cells: string[]; cue: string }[];
      const fr = head.length === 3 ? [0.27, 0.31, 0.42] : [0.4, 0.6];
      const hasNote = !!v.note;
      const avail = (hasNote ? 750 : 870) - 252;
      const rh = Math.min(170, (avail - (rows.length - 1) * 18) / rows.length);
      P.push({
        key: "head", x: 150, y: 196, w: 1650, h: 50, at: 0.3, from: "fade", hand: false,
        node: () => (
          <div style={{ display: "flex" }}>
            {head.map((h2, k) => <HText key={k} size={38} color={GRAY} weight={700} style={{ width: 1650 * fr[k] }}>{h2}</HText>)}
          </div>
        ),
      });
      rows.forEach((r, k) => {
        const fs = Math.min(...r.cells.map((c2, j) => fit(c2, 1650 * fr[j] - 40, rh - 34, 50, 28)));
        P.push({
          key: `r${k}`, x: 120, y: 252 + k * (rh + 18), w: 1680, h: rh, at: cue(r.cue) || 0.5 + k * 0.4, from: k % 2 ? "left" : "right", rot: (rnd(seed + k) - 0.5) * 1.2,
          node: () => (
            <Paper w={1680} h={rh} seed={seed + k} pad={16}>
              <div style={{ display: "flex", alignItems: "center", height: "100%", paddingLeft: 14 }}>
                {r.cells.map((c2, j) => (
                  <HText key={j} size={fs} weight={j === 0 ? 700 : 500} color={j === 0 ? RED : INK_L} style={{ width: 1650 * fr[j] - 10, paddingRight: 20 }}>{c2}</HText>
                ))}
              </div>
            </Paper>
          ),
        });
      });
      P.push(...noteP(v.note, cue(v.cueNote) || (cue(rows[rows.length - 1].cue) || 2) + 1.2));
      break;
    }
    case "case": {
      P.push(strip("title", v.title, 120, 60, 72, 0, "top", { seed, rot: -1, hand: false, color: RED }));
      const items = v.items as { text: string; cue: string }[];
      const n = items.length;
      const gap = 90;
      const w = (1680 - (n - 1) * gap) / n;
      const h = 440;
      const ats = items.map((it, k) => cue(it.cue) || 0.6 + k * 0.6);
      items.forEach((it, k) => {
        P.push(card(`s${k}`, it.text, 120 + k * (w + gap), 250, w, h, ats[k], seed + k, { num: k + 1 }));
        if (k < n - 1) {
          const x1 = 120 + k * (w + gap) + w + 6, x2 = x1 + gap - 14;
          E.push((t) => (
            <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1920} height={900}>
              <Draw d={`M${x1} 470 Q${(x1 + x2) / 2} 445 ${x2} 470 M${x2 - 18} 455 L${x2} 470 L${x2 - 20} 482`} t={t} at={ats[k + 1] - 0.25} dur={0.35} sw={6} color={INK_L} len={260} />
            </svg>
          ));
        }
      });
      break;
    }
    case "stairs": {
      title(v.title);
      const items = v.items as { text: string; cue: string }[];
      items.forEach((it, k) => {
        P.push(card(`s${k}`, it.text, 110 + k * 340, 670 - k * 118, 330, 170, cue(it.cue) || 0.5 + k * 0.4, seed + k, { num: k + 1, icon: null }));
      });
      break;
    }
    case "merke": {
      const fs = fit(v.text, 1240, 380, 66, 36);
      const h = lines(v.text, 1240, fs) * fs * 1.12 + 190;
      P.push({
        key: "note", x: 250, y: Math.max(60, 420 - h / 2), w: 1400, h, at: 0.1, from: "top", rot: -1.3,
        node: () => (
          <div style={{ position: "relative" }}>
            <Paper w={1400} h={h} seed={seed} bg={YELLOW} pad={56}>
              <HText size={84} weight={700} color={RED} style={{ marginBottom: 14 }}>Merke!</HText>
              <HText size={fs} weight={600}>{v.text}</HText>
            </Paper>
            <div style={{ position: "absolute", left: 60, top: -18, width: 150, height: 44, background: "rgba(230,222,200,0.75)", transform: "rotate(-8deg)" }} />
            <div style={{ position: "absolute", right: 60, top: -18, width: 150, height: 44, background: "rgba(230,222,200,0.75)", transform: "rotate(7deg)" }} />
          </div>
        ),
      });
      P.push(iconPiece("bulb", "bulb", 1590, 560, 230, 0.7, "right", 8));
      break;
    }
    case "big": {
      const bs = Math.min(200, fit(v.big, 1500, 230, 200, 90));
      const bw = textW(v.big, bs) + 80;
      const bx = 960 - bw / 2;
      if (v.sub) P.push(strip("sub", v.sub, 960 - (textW(v.sub, 50) + 70) / 2, 70, 50, 0, "top", { seed: seed + 9, color: GRAY, rot: 1, hand: false }));
      P.push({
        key: "big", x: bx, y: 160, w: bw, h: bs * 1.2, at: 0.15, from: "top", rot: -2,
        node: () => <HText size={bs} weight={700} color={RED} style={{ textShadow: "2px 4px 0 rgba(0,0,0,0.08)", whiteSpace: "nowrap" }}>{v.big}</HText>,
      });
      E.push((t) => (
        <svg style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }} width={1920} height={900}>
          <Draw d={`M${bx - 10} ${160 + bs * 0.6} C${bx - 10} ${120} ${bx + bw + 40} ${110} ${bx + bw + 30} ${160 + bs * 0.6} C${bx + bw + 20} ${170 + bs * 1.25} ${bx - 30} ${180 + bs * 1.25} ${bx - 4} ${150 + bs * 0.5}`} t={t} at={0.7} dur={0.7} sw={6} len={bw * 3 + 800} />
        </svg>
      ));
      (v.items as { text: string; cue: string }[]).forEach((it, k) => {
        const s = 52;
        const w = Math.min(1500, textW(it.text, s) + 70);
        P.push(strip(`it${k}`, it.text, 960 - w / 2, 160 + bs * 1.2 + 70 + k * 120, s, cue(it.cue) || 1 + k * 0.6, k % 2 ? "right" : "left", { seed: seed + k, weight: 600, maxW: 1500 }));
      });
      break;
    }
    case "quiz": {
      const at = cue(v.cueA) || 999;
      P.push(iconPiece("q", "question", 130, 170, 380, 0, "left", -8));
      const qs = fit(v.q, 1080, 300, 68, 40);
      const qh = lines(v.q, 1080, qs) * qs * 1.1 + 70;
      P.push({
        key: "qcard", x: 600, y: 120, w: 1180, h: qh, at: 0.25, from: "right", rot: 1,
        node: () => (
          <Paper w={1180} h={qh} seed={seed} pad={34}>
            <HText size={qs} weight={700}>{v.q}</HText>
          </Paper>
        ),
      });
      E.push((t) =>
        t > 1.2 && t < at ? (
          <div style={{ position: "absolute", left: 640, top: 120 + qh + 50, opacity: 0.55 + 0.45 * Math.sin(t * 4) }}>
            <HText size={56} color={GRAY} weight={600}>Überleg kurz {".".repeat(1 + (Math.floor(t * 2) % 3))}</HText>
          </div>
        ) : null,
      );
      const as = fit(v.a, 900, 200, 58, 34);
      const ah = Math.max(170, lines(v.a, 900, as) * as * 1.12 + 70);
      P.push({
        key: "ans", x: 600, y: 120 + qh + 50, w: 1180, h: ah, at, from: "bottom", rot: -1,
        node: () => (
          <Paper w={1180} h={ah} seed={seed + 4} bg={GREENP} pad={28}>
            <div style={{ display: "flex", alignItems: "center", gap: 26, height: "100%" }}>
              <Icon name="check" size={110} cut={false} />
              <HText size={as} weight={600} style={{ maxWidth: 900 }}>{v.a}</HText>
            </div>
          </Paper>
        ),
      });
      break;
    }
    default:
      break;
  }
  return { pieces: P, extras: E };
};

const HAND_W = 230;
const PieceView: React.FC<{ p: Piece; t: number }> = ({ p, t }) => {
  if (p.at > 900 || t < p.at - 0.05) return null;
  const f = Math.round((t - p.at) * LFPS);
  if (p.from === "fade") {
    const o = ramp(t, p.at, p.at + 0.4);
    return <div style={{ position: "absolute", left: p.x, top: p.y, width: p.w, height: p.h, opacity: o }}>{p.node(t)}</div>;
  }
  const s = spring({ frame: f, fps: LFPS, config: { damping: 17, stiffness: 95, mass: 0.9 } });
  const [dx, dy] = off(p);
  const x = p.x + dx * (1 - s), y = p.y + dy * (1 - s);
  const rot = (p.rot ?? 0) + (1 - s) * (p.from === "left" || p.from === "bottom" ? -9 : 9);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: p.w, height: p.h, transform: `rotate(${rot}deg)` }}>{p.node(t)}</div>
  );
};
const off = (p: Piece): [number, number] =>
  p.from === "left" ? [-(p.x + p.w + 280), 0] : p.from === "right" ? [1920 - p.x + 280, 0] : p.from === "top" ? [0, -(p.y + p.h + 520)] : p.from === "bottom" ? [0, 1080 - p.y + 520] : [0, 0];

const HandView: React.FC<{ p: Piece; t: number }> = ({ p, t }) => {
  if (p.hand === false || p.from === "fade" || p.at > 900 || t < p.at || t > p.at + 1.35) return null;
  const s = spring({ frame: Math.round((t - p.at) * LFPS), fps: LFPS, config: { damping: 17, stiffness: 95, mass: 0.9 } });
  const [dx, dy] = off(p);
  const r = Math.pow(ramp(t, p.at + 0.6, p.at + 1.3), 2);
  const x = p.x + dx * (1 - s) + dx * r * 1.1, y = p.y + dy * (1 - s) + dy * r * 1.1;
  const ins = Math.min(70, Math.min(p.w, p.h) * 0.3);
  const [ax, ay, rot] =
    p.from === "left" ? [x + ins, y + p.h / 2, 90] : p.from === "right" ? [x + p.w - ins, y + p.h / 2, -90] : p.from === "top" ? [x + p.w / 2, y + ins, 180] : [x + p.w / 2, y + p.h - ins, 0];
  const H = (HAND_W * 420) / 200;
  return (
    <div style={{ position: "absolute", left: ax, top: ay, width: 0, height: 0, transform: `rotate(${rot}deg)` }}>
      <div style={{ position: "absolute", left: -HAND_W * 0.56, top: -H * 0.07 }}>
        <HandArt w={HAND_W} />
      </div>
    </div>
  );
};

const Sub: React.FC<{ words: Word[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (!words.length || t < words[0].start - 0.1) return null;
  const sents: Word[][] = [[]];
  words.forEach((w) => {
    sents[sents.length - 1].push(w);
    if (/[.!?]$/.test(w.word.replace(/\*/g, "")) || (sents[sents.length - 1].length > 20 && /[,:]$/.test(w.word))) sents.push([]);
  });
  const cur = sents.filter((x) => x.length).reduce((acc, x) => (t >= x[0].start - 0.1 ? x : acc), sents[0]);
  return (
    <AbsoluteFill style={{ top: 925, height: 135, alignItems: "center", justifyContent: "center" }}>
      <div style={{ maxWidth: 1600, textAlign: "center", fontFamily: "Inter, sans-serif", fontWeight: 550, fontSize: 34, lineHeight: 1.35 }}>
        {cur.map((w, i) => {
          const key = w.word.includes("*");
          return (
            <span key={i} style={{ color: key ? RED : INK_L, fontWeight: key ? 800 : 550, opacity: t >= w.start ? 1 : 0.28 }}>
              {w.word.replace(/\*/g, "")}{" "}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const LegeScene: React.FC<{ i: number; dur: number; start: number; total: number }> = ({ i, dur, start, total }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { s } = DATA[KB];
  const sc = s.sentences[i];
  const ln = info(KB, i);
  const t = frame / fps;
  const D = dur / fps;
  const { pieces, extras } = React.useMemo(() => build(sc, cueFn(ln.words), D, s.topics, i), [i]);
  const e = Math.pow(ramp(t, D - 0.4, D), 2);
  const p = (start + frame) / total;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", right: 70, top: 26, textAlign: "right" }}>
        <HText size={36} color={GRAY} weight={600}>{sc.topic > 0 ? `Thema ${sc.topic}/${s.topics.length} · ${sc.tname}` : "Gemeinschaftskunde"}</HText>
        <svg width={320} height={14} style={{ display: "block", marginLeft: "auto" }}>
          <path d="M4 8 L316 8" stroke="#d8d2c4" strokeWidth={5} strokeLinecap="round" />
          <path d={`M4 8 L${4 + 312 * p} 8`} stroke={RED} strokeWidth={5} strokeLinecap="round" />
        </svg>
      </div>
      <AbsoluteFill style={{ height: 910, transform: `translateX(${-e * 2300}px)` }}>
        {extras.map((x, k) => <React.Fragment key={`e${k}`}>{x(t)}</React.Fragment>)}
        {pieces.map((pc) => <PieceView key={pc.key} p={pc} t={t} />)}
        {pieces.map((pc) => <HandView key={`h${pc.key}`} p={pc} t={t} />)}
      </AbsoluteFill>
      <Sub words={ln.words} />
    </AbsoluteFill>
  );
};

export const LegeVideo: React.FC = () => {
  const { fps } = useVideoConfig();
  const { s } = DATA[KB];
  let total = 0;
  s.sentences.forEach((_, i) => (total += durF(KB, i)));
  let from = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: "#f6f3ec" }}>
      <Img src={staticFile("lege/paper.jpg")} style={{ position: "absolute", width: 1920, height: 1080 }} />
      {s.sentences.map((sc, i) => {
        const ln = info(KB, i);
        const dur = durF(KB, i);
        const start = from;
        from += dur;
        const l = lead(sc);
        const D = dur / fps;
        const slides = build(sc, cueFn(ln.words), D, s.topics, i).pieces.filter((pc) => pc.from !== "fade" && pc.at < D).map((pc) => pc.at);
        return (
          <Sequence key={i} from={start} durationInFrames={dur}>
            <LegeScene i={i} dur={dur} start={start} total={total} />
            {ln.file ? (
              <Sequence from={l}>
                <Audio src={staticFile(ln.file)} />
              </Sequence>
            ) : null}
            {slides.map((a, k) => (
              <Sequence key={k} from={Math.max(0, Math.round(a * fps))}>
                <Audio src={staticFile("lege/slide.wav")} volume={0.22} />
              </Sequence>
            ))}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
