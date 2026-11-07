// Strichzeichnungen für die Legetechnik (schwarze Linien, als Papier-Ausschnitt mit weißem Rand).
// Jedes Symbol: Liste einfacher Formen in einem 200×200-Raster.
import React from "react";

type Shape =
  | ["p", string, boolean?] // Pfad, gefüllt (weiß)?
  | ["c", number, number, number, boolean?]
  | ["r", number, number, number, number, number?, boolean?]
  | ["e", number, number, number, number, boolean?];

const star = (cx: number, cy: number, r: number) => {
  let d = "";
  for (let i = 0; i < 10; i++) {
    const a = -Math.PI / 2 + (i * Math.PI) / 5;
    const rr = i % 2 ? r * 0.45 : r;
    d += `${i ? "L" : "M"}${(cx + rr * Math.cos(a)).toFixed(1)} ${(cy + rr * Math.sin(a)).toFixed(1)} `;
  }
  return d + "Z";
};
const burst = () => {
  let d = "";
  for (let i = 0; i < 20; i++) {
    const a = (i * Math.PI) / 10;
    const rr = i % 2 ? 38 : 78;
    d += `${i ? "L" : "M"}${(100 + rr * Math.cos(a)).toFixed(1)} ${(100 + rr * Math.sin(a)).toFixed(1)} `;
  }
  return d + "Z";
};
const person = (x: number, y: number, s: number): Shape[] => [
  ["c", x, y - 52 * s, 22 * s, true],
  ["p", `M${x - 40 * s} ${y + 70 * s} Q${x - 40 * s} ${y - 8 * s} ${x} ${y - 12 * s} Q${x + 40 * s} ${y - 8 * s} ${x + 40 * s} ${y + 70 * s} Z`, true],
  ["c", x - 8 * s, y - 55 * s, 2.5 * s, false],
  ["c", x + 8 * s, y - 55 * s, 2.5 * s, false],
  ["p", `M${x - 9 * s} ${y - 42 * s} Q${x} ${y - 35 * s} ${x + 9 * s} ${y - 42 * s}`],
];
const HAND_PALM =
  "M70 175 L68 110 Q50 95 42 75 Q38 64 48 62 Q58 62 66 78 L72 88 L74 40 Q74 30 83 30 Q92 30 92 40 L94 85 L98 28 Q99 18 108 19 Q117 20 116 30 L114 86 L122 40 Q124 31 132 32 Q141 34 139 44 L132 92 L142 62 Q145 54 152 56 Q159 59 157 68 L146 118 Q140 150 128 175 Z";

export const ICONS: Record<string, Shape[]> = {
  ballot: [
    ["r", 70, 22, 60, 78, 4, true], ["p", "M84 42 L116 76 M116 42 L84 76"],
    ["r", 35, 92, 130, 85, 8, true], ["p", "M72 92 L128 92"], ["p", "M60 125 L140 125"],
  ],
  parliament: [
    ["r", 30, 150, 140, 22, 2, true], ["r", 36, 86, 128, 14, 2, true],
    ["p", "M50 100 L50 150 M75 100 L75 150 M100 100 L100 150 M125 100 L125 150 M150 100 L150 150"],
    ["p", "M58 86 Q100 22 142 86 Z", true], ["p", "M100 52 L100 22 L124 29 L100 36"],
  ],
  scales: [
    ["p", "M100 42 L100 168 M66 172 L134 172 M42 62 L158 62"], ["c", 100, 40, 7, true],
    ["p", "M42 62 L24 112 M42 62 L60 112 M158 62 L140 112 M158 62 L176 112"],
    ["p", "M18 112 Q42 140 66 112 Z", true], ["p", "M134 112 Q158 140 182 112 Z", true],
  ],
  badge: [["p", "M100 22 L162 44 Q162 132 100 178 Q38 132 38 44 Z", true], ["p", star(100, 95, 34), true]],
  shield: [["p", "M100 22 L162 44 Q162 132 100 178 Q38 132 38 44 Z", true], ["p", "M72 98 L92 120 L130 76"]],
  newspaper: [
    ["r", 32, 38, 136, 128, 4, true], ["p", "M48 60 L152 60"], ["r", 48, 78, 46, 40, 2, true],
    ["p", "M106 82 L152 82 M106 98 L152 98 M106 114 L152 114 M48 134 L152 134 M48 150 L128 150"],
  ],
  tv: [
    ["r", 28, 56, 144, 96, 14, true], ["r", 42, 68, 116, 72, 6], ["p", "M84 56 L62 24 M116 56 L138 24 M82 152 L70 174 M118 152 L130 174"],
  ],
  phone: [["r", 64, 22, 72, 156, 16, true], ["r", 73, 40, 54, 112, 4], ["c", 100, 164, 5], ["p", "M90 31 L110 31"], ["p", "M100 112 Q82 96 88 86 Q95 78 100 88 Q105 78 112 86 Q118 96 100 112 Z"]],
  globe: [["c", 100, 100, 68, true], ["e", 100, 100, 30, 68], ["p", "M32 100 L168 100 M44 66 Q100 82 156 66 M44 134 Q100 118 156 134"]],
  dove: [
    ["p", "M36 112 Q66 72 118 90 Q148 70 172 78 Q154 94 144 102 Q124 144 70 138 Q52 132 36 112 Z", true],
    ["p", "M88 100 Q96 46 132 34 Q128 80 112 100 Z", true], ["c", 152, 84, 3], ["p", "M168 82 Q180 96 176 108 M176 96 Q186 94 190 100"],
  ],
  helmet: [["p", "M48 122 Q48 52 100 52 Q152 52 152 122 Z", true], ["p", "M32 124 L168 124"], ["p", "M62 124 Q100 168 138 124"], ["p", "M70 84 Q100 70 130 84"]],
  bubbles: [
    ["p", "M24 34 L114 34 Q128 34 128 48 L128 86 Q128 100 114 100 L66 100 L44 122 L46 100 L38 100 Q24 100 24 86 L24 48 Q24 34 38 34 Z", true],
    ["p", "M176 92 L96 92 Q82 92 82 106 L82 142 Q82 156 96 156 L136 156 L158 178 L156 156 L162 156 Q176 156 176 142 Z", true],
    ["p", "M48 60 L104 60 M48 76 L90 76 M102 118 L156 118 M102 134 L140 134"],
  ],
  boom: [["p", burst(), true], ["p", "M100 70 L100 112"], ["c", 100, 130, 5]],
  barrel: [
    ["p", "M56 46 L56 160 Q100 178 144 160 L144 46 Z", true], ["e", 100, 46, 44, 13, true],
    ["p", "M56 86 Q100 100 144 86 M56 126 Q100 140 144 126"], ["p", "M100 96 Q114 112 112 120 Q110 130 100 130 Q90 130 88 120 Q86 112 100 96 Z"],
  ],
  drop: [["p", "M100 26 Q152 98 146 126 Q140 172 100 172 Q60 172 54 126 Q48 98 100 26 Z", true], ["p", "M76 128 Q78 148 96 152"]],
  tree: [["p", "M90 176 L92 118 L108 118 L110 176", true], ["p", "M68 126 Q38 122 44 94 Q38 64 68 60 Q74 28 104 32 Q136 28 140 58 Q166 68 156 96 Q162 126 132 126 Z", true]],
  factory: [
    ["p", "M24 172 L24 92 L60 112 L60 92 L96 112 L96 92 L132 112 L132 172 Z", true], ["r", 132, 40, 26, 132, 2, true],
    ["c", 150, 26, 8], ["c", 166, 12, 9], ["r", 40, 132, 18, 18, 2], ["r", 74, 132, 18, 18, 2], ["r", 106, 132, 18, 18, 2],
  ],
  ship: [
    ["r", 44, 98, 36, 32, 2, true], ["r", 82, 98, 36, 32, 2, true], ["r", 120, 98, 36, 32, 2, true], ["r", 62, 64, 36, 32, 2, true], ["r", 100, 64, 36, 32, 2, true],
    ["p", "M18 130 L182 130 L160 166 L40 166 Z", true], ["p", "M8 184 Q28 172 48 184 T88 184 T128 184 T168 184"],
  ],
  shirt: [["p", "M70 34 L38 50 L18 86 L44 102 L56 86 L56 172 L144 172 L144 86 L156 102 L182 86 L162 50 L130 34 Q100 60 70 34 Z", true]],
  coins: [
    ["e", 70, 156, 44, 13, true], ["p", "M26 156 L26 140 M114 156 L114 140"], ["e", 70, 140, 44, 13, true], ["p", "M26 140 L26 124 M114 140 L114 124"], ["e", 70, 124, 44, 13, true],
    ["c", 132, 76, 46, true], ["p", "M150 56 Q134 46 120 56 Q106 70 118 92 Q132 106 150 96 M106 70 L138 70 M106 82 L134 82"],
  ],
  magnifier: [["c", 86, 86, 50, true], ["p", "M122 122 L172 172"], ["p", "M58 70 Q66 54 84 50"]],
  bulb: [
    ["p", "M100 26 Q152 28 152 78 Q152 104 126 124 L126 146 L74 146 L74 124 Q48 104 48 78 Q48 28 100 26 Z", true],
    ["p", "M80 158 L120 158 M86 170 L114 170 M88 124 L88 100 L100 110 L112 100 L112 124"], ["p", "M100 4 L100 14 M30 30 L38 38 M170 30 L162 38"],
  ],
  megaphone: [
    ["p", "M48 82 L140 40 L140 160 L48 118 Z", true], ["r", 26, 82, 22, 36, 4, true], ["p", "M68 120 L80 156 L98 156 L90 124"],
    ["p", "M156 78 Q170 100 156 122 M168 62 Q194 100 168 138"],
  ],
  document: [
    ["p", "M48 22 L126 22 L156 52 L156 178 L48 178 Z", true], ["p", "M126 22 L126 52 L156 52"],
    ["p", "M66 70 L138 70 M66 90 L138 90 M66 110 L138 110 M66 130 L112 130"], ["p", "M70 158 Q80 140 90 158 T112 156 T132 152"],
  ],
  book: [
    ["p", "M100 54 Q70 38 28 44 L28 160 Q70 154 100 170 Q130 154 172 160 L172 44 Q130 38 100 54 Z", true], ["p", "M100 54 L100 170"],
    ["p", "M44 70 Q66 66 86 74 M44 92 Q66 88 86 96 M114 74 Q134 66 156 70 M114 96 Q134 88 156 92"],
  ],
  cap: [["p", "M56 96 L56 136 Q100 162 144 136 L144 96", true], ["p", "M18 80 L100 44 L182 80 L100 116 Z", true], ["p", "M182 80 L182 124"], ["c", 182, 130, 6]],
  family: [...person(52, 100, 0.8), ...person(148, 100, 0.8), ...person(100, 128, 0.55), ["p", "M100 50 Q86 36 92 28 Q98 22 100 32 Q102 22 108 28 Q114 36 100 50 Z"]],
  heart: [["p", "M100 166 Q28 116 34 74 Q40 38 76 40 Q96 44 100 68 Q104 44 124 40 Q160 38 166 74 Q172 116 100 166 Z", true]],
  lock: [["p", "M64 96 L64 70 Q64 32 100 32 Q136 32 136 70 L136 96"], ["r", 46, 94, 108, 80, 12, true], ["c", 100, 124, 10], ["p", "M100 134 L100 152"]],
  database: [
    ["p", "M52 44 L52 156 Q100 176 148 156 L148 44 Z", true], ["e", 100, 44, 48, 14, true],
    ["p", "M52 82 Q100 98 148 82 M52 120 Q100 136 148 120"], ["c", 128, 66, 3], ["c", 128, 104, 3], ["c", 128, 142, 3],
  ],
  warning: [["p", "M100 26 L178 166 L22 166 Z", true], ["p", "M100 74 L100 122"], ["c", 100, 142, 6]],
  clock: [["c", 100, 100, 68, true], ["p", "M100 100 L100 58 M100 100 L132 116"], ["p", "M100 38 L100 46 M162 100 L154 100 M100 162 L100 154 M38 100 L46 100"]],
  up: [["p", "M32 26 L32 172 L178 172"], ["p", "M44 150 L80 116 L110 128 L160 62"], ["p", "M136 60 L162 60 L162 86"]],
  down: [["p", "M32 26 L32 172 L178 172"], ["p", "M44 52 L80 90 L110 78 L160 146"], ["p", "M136 148 L162 148 L162 122"]],
  elder: [
    ["c", 88, 48, 22, true], ["p", "M90 70 Q104 108 96 132 L80 176 M96 132 L112 176"], ["p", "M92 92 L128 104"], ["p", "M128 104 L134 176 M128 104 Q120 92 112 100"],
    ["p", "M70 40 Q88 18 108 40"],
  ],
  stroller: [["p", "M38 70 Q38 130 110 130 L160 130 L160 74 Z", true], ["p", "M38 70 Q80 30 110 72 L110 130"], ["c", 66, 154, 16, true], ["c", 140, 154, 16, true], ["p", "M160 74 L182 52"]],
  hammer: [["r", 92, 74, 18, 100, 4, true], ["p", "M52 38 L148 38 Q160 38 160 50 L160 64 Q160 76 148 76 L52 76 L38 64 L38 50 Z", true], ["p", "M40 124 L64 100 L52 140 L76 116"]],
  eu: [
    ["c", 100, 100, 74, true], star(100, 40, 10), star(130, 48, 10), star(152, 70, 10), star(160, 100, 10), star(152, 130, 10), star(130, 152, 10),
    star(100, 160, 10), star(70, 152, 10), star(48, 130, 10), star(40, 100, 10), star(48, 70, 10), star(70, 48, 10),
  ].map((s) => (typeof s === "string" ? (["p", s] as Shape) : s)) as Shape[],
  barrier: [["r", 28, 80, 18, 96, 3, true], ["p", "M46 90 L170 30 L176 44 L52 104 Z", true], ["p", "M80 74 L86 88 M112 58 L118 72 M144 43 L150 57"], ["c", 150, 166, 10]],
  plane: [["p", "M100 18 Q112 18 112 40 L112 80 L178 116 L178 132 L112 112 L112 150 L134 166 L134 178 L100 170 L66 178 L66 166 L88 150 L88 112 L22 132 L22 116 L88 80 L88 40 Q88 18 100 18 Z", true]],
  car: [["p", "M24 132 L24 106 L54 100 L76 68 L136 68 L156 100 L178 108 L178 132 Z", true], ["c", 60, 136, 17, true], ["c", 146, 136, 17, true], ["p", "M84 76 L80 100 M104 76 L104 100 M128 76 L144 100 M66 100 L150 100"]],
  road: [["p", "M56 178 L92 26 M144 178 L108 26"], ["p", "M100 160 L100 140 M100 120 L100 100 M100 80 L100 64 M100 50 L100 40"]],
  gender: [["c", 74, 82, 32, true], ["p", "M74 114 L74 168 M54 146 L94 146"], ["c", 128, 112, 30, true], ["p", "M150 90 L180 60 M158 58 L180 58 L180 80"]],
  rings: [["c", 80, 116, 42], ["c", 122, 116, 42], ["p", "M80 74 L70 60 L80 44 L90 60 Z", true]],
  hand: [["p", HAND_PALM, true], ["p", "M80 150 Q100 140 120 150"]],
  calendar: [["r", 32, 46, 136, 124, 10, true], ["p", "M32 78 L168 78 M70 32 L70 58 M130 32 L130 58"], ["c", 66, 104, 5], ["c", 100, 104, 5], ["c", 134, 104, 5], ["c", 66, 138, 5], ["c", 100, 138, 5]],
  percent: [["c", 64, 62, 22, true], ["c", 136, 138, 22, true], ["p", "M148 46 L52 154"]],
  frame: [["r", 26, 34, 148, 132, 6, true], ["c", 76, 104, 22], ["p", "M76 126 L76 150 M98 104 Q118 112 98 118"], ["p", "M104 54 L160 54 Q166 54 166 62 L166 82 Q166 90 160 90 L124 90 L110 102 L112 90 L104 90 Q98 90 98 82 L98 62 Q98 54 104 54 Z", true]],
  pencil: [["p", "M38 162 L50 124 L142 32 L168 58 L76 150 Z", true], ["p", "M50 124 L76 150 M126 48 L152 74"], ["p", "M38 162 L44 144 L56 156 Z"]],
  target: [["c", 96, 104, 66, true], ["c", 96, 104, 42], ["c", 96, 104, 18], ["p", "M96 104 L168 32 M150 30 L170 30 L170 50"]],
  chain: [["r", 22, 74, 96, 52, 26, true], ["r", 82, 74, 96, 52, 26], ["p", "M118 88 L118 112"]],
  medic: [["p", "M78 34 L122 34 L122 78 L166 78 L166 122 L122 122 L122 166 L78 166 L78 122 L34 122 L34 78 L78 78 Z", true]],
  plug: [["r", 74, 30, 52, 64, 10, true], ["r", 88, 44, 24, 12, 4], ["p", "M100 94 Q100 136 70 148 Q40 160 50 186"]],
  tower: [["p", "M100 70 L70 176 M100 70 L130 176 M84 120 L116 120 M78 146 L122 146"], ["c", 100, 62, 8, true], ["p", "M74 40 Q62 62 74 84 M126 40 Q138 62 126 84 M56 26 Q36 62 56 98 M144 26 Q164 62 144 98"]],
  crown: [["p", "M32 150 L24 64 L66 104 L100 44 L134 104 L176 64 L168 150 Z", true], ["p", "M32 170 L168 170"], ["c", 100, 120, 8]],
  flag: [["p", "M50 26 L50 178"], ["p", "M50 34 Q80 22 110 38 T166 38 L166 100 Q140 88 110 102 T50 96 Z", true]],
  people: [...person(52, 112, 0.72), ...person(148, 112, 0.72), ...person(100, 100, 0.82)],
  person: person(100, 100, 1),
  arrow: [["p", "M24 84 L118 84 L118 52 L178 100 L118 148 L118 116 L24 116 Z", true]],
  house: [["p", "M54 96 L54 170 L146 170 L146 96", true], ["p", "M36 104 L100 42 L164 104"], ["r", 88, 128, 24, 42, 2], ["r", 64, 112, 18, 18, 2]],
  check: [["c", 100, 100, 68, true], ["p", "M64 102 L90 128 L140 72"]],
  cross: [["c", 100, 100, 68, true], ["p", "M70 70 L130 130 M130 70 L70 130"]],
  question: [["p", "M64 70 Q64 30 100 30 Q138 30 138 66 Q138 92 104 102 L104 132"], ["c", 104, 160, 8]],
  thumbsUp: [["r", 30, 92, 32, 82, 4, true], ["p", "M62 100 Q84 94 90 66 Q96 36 112 42 Q124 48 116 84 L158 84 Q174 88 168 104 Q176 114 164 122 Q170 134 158 140 Q162 156 146 158 L62 164 Z", true]],
  thumbsDown: [["r", 30, 26, 32, 82, 4, true], ["p", "M62 100 Q84 106 90 134 Q96 164 112 158 Q124 152 116 116 L158 116 Q174 112 168 96 Q176 86 164 78 Q170 66 158 60 Q162 44 146 42 L62 36 Z", true]],
};

export const ICON_FOR_TEXT: Record<string, string> = {
 "Partei": "flag", "regieren, Verantwortung übernehmen": "crown", "Verband": "people", "Parteien": "flag", "Verbände & Bürgerinitiativen": "megaphone",
 "Familie": "family", "traditionell: Mutter, Vater, Kinder": "family", "gleichgeschlechtliche Paare mit Kindern": "heart", "Alleinerziehende: ein Elternteil mit Kind": "person",
 "Gleichberechtigung": "gender", "seltener in Führungspositionen": "down", "Merkmale einer Demokratie": "crown", "immer begründen": "bubbles",
 "Text-Aufgaben: eigene Worte, nicht abschreiben": "document", "Interpretieren: „Der Karikaturist möchte damit zeigen / kritisieren, dass … Das erkennt man daran, dass …“": "frame",
 "Direkte Demokratie": "people",
 "Indirekte Demokratie": "parliament",
 "unmittelbar – direkt, ohne Zwischenpersonen": "arrow",
 "frei – niemand zwingt dich (ob und wen)": "hand",
 "gleich – jede Stimme zählt gleich viel": "scales",
 "geheim – keiner sieht es (Wahlkabine)": "lock",
 "Erststimme": "person",
 "Zweitstimme": "flag",
 "Baden-Württemberg: Landtag, Kommune, Europa schon ab 16": "calendar",
 "in eine Partei eintreten": "flag",
 "bei einer Bürgerinitiative mitmachen": "people",
 "Wer nicht wählt, lässt andere entscheiden – vielleicht Extremisten": "warning",
 "Es geht um deine Zukunft: Ausbildung, Lohn, Rente": "target",
 "Ideologie – ganz unterschiedliche Werte": "book",
 "Religion – Religionen in Konkurrenz": "bubbles",
 "Rassismus – andere Völker abgewertet": "warning",
 "Umwelt – Streit um Wasser (Dürre)": "drop",
 "5 mit Vetorecht: USA, Russland, China, Großbritannien, Frankreich": "globe",
 "Blauhelme = UNO-Soldaten": "helmet",
 "Wehrpflicht": "helmet",
 "Kriegsdienstverweigerung": "dove",
 "Dienst freiwillig: mind. 6 Monate, ca. 2.600 € im Monat": "coins",
 "Gerechtigkeit, Wohlstand, Menschenrechte, Demokratie": "scales",
 "Konflikte ohne Gewalt lösen": "bubbles",
 "Kultur – Netflix, McDonald's": "tv",
 "Politik – Klimawandel, Pandemien, Terror (Corona)": "parliament",
 "Zölle abgebaut (Freihandel)": "barrier",
 "weniger Regeln für Umwelt- und Arbeitsschutz": "document",
 "neue Kunden direkt vor Ort": "people",
 "Chancen": "up",
 "Risiken": "warning",
 "Gewinner": "up",
 "Verlierer": "down",
 "Firmen: faire Löhne und Umweltschutz bei Zulieferern": "factory",
 "Politik: Lieferkettengesetz (Menschenrechte bei Zulieferern)": "document",
 "Migration": "arrow",
 "Armut, Arbeitslosigkeit": "coins",
 "bessere Bildung, Familie": "cap",
 "Push-Faktoren (drücken weg)": "arrow",
 "Pull-Faktoren (ziehen an)": "house",
 "Sprachkurse": "bubbles",
 "Begegnung: Sportverein, Feste": "people",
 "Vierte Gewalt": "newspaper",
 "Vorteile": "thumbsUp",
 "Nachteile": "thumbsDown",
 "Bei Schockierendem vorsichtig sein": "warning",
 "Extremismus": "warning",
 "Rechtsextremismus – Menschen angeblich nicht gleich viel wert; Staat ohne Demokratie": "warning",
 "Religiöser Extremismus (z. B. Islamismus) – religiöse Regeln über Gesetzen": "warning",
 "Workshops zu Medienkompetenz": "cap",
 "EU": "eu",
 "1968 Zollunion – keine Zölle mehr": "barrier",
 "1995 Schengen – keine Grenzkontrollen": "barrier",
 "1993 Vertrag von Maastricht – Gründung der EU": "eu",
 "Vertiefung": "chain",
 "Erweiterung": "eu",
 "Beide müssen zustimmen (Bsp.: KI-Gesetz)": "check",
 "Verbessert": "up",
 "Noch Schwächen": "warning",
 "Reisen ohne Grenzkontrollen und Geldwechsel (Euro)": "plane",
 "Verbraucherschutz, z. B. USB-C-Ladekabel": "plug",
 "Streit um Verteilung von Flüchtlingen": "people",
 "Demografischer Wandel": "people",
 "Generationenvertrag": "people",
 "Rente: höhere Beiträge, später in Rente (67, vielleicht 70)": "elder",
 "Gesundheit & Pflege: höhere Kosten und Beiträge": "medic",
 "Fachkräftemangel: Pflege, Kita, Handwerk, Elektro": "hammer",
 "zu wenig Kitaplätze und Erzieher": "stroller",
 "Für dich: sicherer Job, gute Chancen auf mehr Lohn": "up",
 "Zuwanderung von Fachkräften": "arrow",
 "Familien fördern: Kitas, Kindergeld, Elternzeit für beide": "family",
 "flexible Arbeit: Homeoffice, Teilzeit": "house",
 "Ausbildung attraktiver: Bezahlung, Werbung": "cap",
 "Technik und KI für einfache Aufgaben": "bulb",
 "Menschenrechte": "heart",
 "Bürgerrechte": "flag"
};

const KEYS: [RegExp, string][] = [
  [/datenschutz|persönliche/, "lock"],
  [/big data|\bdaten\b/, "database"],
  [/wahlkabine|wahl|wähl|stimme|abstimm|volksentscheid/, "ballot"],
  [/bundestag|parlament|legislativ|bundesrat|abgeordnete/, "parliament"],
  [/gewaltenteilung|macht ist verteilt|gegenseitig/, "scales"],
  [/gericht|judikativ|recht sprechen|rechtsstaat|verfahren|scheidung/, "scales"],
  [/polizei|exekutiv|regierung/, "badge"],
  [/zeitung|presse|medien|information/, "newspaper"],
  [/fernseh|tagesschau|talkshow/, "tv"],
  [/handy|social|tiktok|whatsapp|internet|bildschirm/, "phone"],
  [/uno|vereinte|welt|global|international|osze/, "globe"],
  [/frieden|diplomatie|vorbild|gandhi/, "dove"],
  [/nato|verteidig|schutz|geschützt|sicherheit/, "shield"],
  [/soldat|bundeswehr|blauhelm|wehr|musterung|militär|armee|auslandseins/, "helmet"],
  [/vermittel|gespräch|lobby|meinung|kontakt/, "bubbles"],
  [/krieg|gewalt|terror|konflikt|angriff|blockiert|sanktion/, "boom"],
  [/öl|rohstoff/, "barrel"],
  [/wasser|dürre|überschwemm/, "drop"],
  [/umwelt|klima|nachhaltig|generationen/, "tree"],
  [/firma|firmen|produ|fabrik|wirtschaft|exportl|märkte/, "factory"],
  [/transport|schiff|container|lieferkett/, "ship"],
  [/t-shirt|kleidung|näherin|second hand|fairtrade/, "shirt"],
  [/geld|lohn|löhne|euro|kosten|steuer|billig|kindergeld|bezahlung|gehält|verdien|schulden|beitr|waren/, "coins"],
  [/prüfen|quelle|faktencheck|erkenn|kontroll|aufdeck|sehen/, "magnifier"],
  [/tipp|idee|lösung|aufklärung/, "bulb"],
  [/kampagne|öffentlich|werbung|plakat|demo|petition|mitbestimm/, "megaphone"],
  [/gesetz|vertrag|fragebogen|unterschr|beschreiben|interpretieren|lesen/, "document"],
  [/grundgesetz|art\.|artikel|grundrecht/, "book"],
  [/schule|smv|ausbildung|studi|workshop|kita|erzieher|wissen|lernen/, "cap"],
  [/familie|eltern|alleinerzieh|patchwork/, "family"],
  [/würde|menschenrecht/, "heart"],
  [/extrem|fake|hass|gefahr|risiko|sucht|stress|mobbing|vorurteil|rassismus|populist|ausbeutung|manipulation/, "warning"],
  [/rente|ältere|alte |pflege|lebenserwartung|leben länger/, "elder"],
  [/geburt|kinder/, "stroller"],
  [/handwerk|elektr|fachkr|arbeit|job|beruf|elektron/, "hammer"],
  [/ eu|^eu|eu-|europa|europäisch|kommission|rat der|binnenmarkt|maastricht|lissabon|zollunion|römisch/, "eu"],
  [/grenz|zölle|schengen/, "barrier"],
  [/reisen|flug/, "plane"],
  [/adac|auto/, "car"],
  [/straße/, "road"],
  [/frau|männer|gender|gleichberecht|quote|girls/, "gender"],
  [/\behe\b|ehe für/, "rings"],
  [/mitmach|beteilig|veto|nein|engagier|eintreten/, "hand"],
  [/zeit|später|seit|jahrzehnt|monat|dauer/, "clock"],
  [/steig|wachs|höher|stärker|mehr frauen/, "up"],
  [/weniger|sinkt|fallen weg|fehlen/, "down"],
  [/prozent|%|hürde/, "percent"],
  [/karikatur|zeichner|stolpern|aussage/, "frame"],
  [/satz|sätze|schreib|antwort|begründ|fazit|argument|stellung|definition/, "pencil"],
  [/ziel/, "target"],
  [/verbunden|verflecht|zusammenarb/, "chain"],
  [/corona|pandemie|gesundheit|ärzt|medizin|kranken|humanit/, "medic"],
  [/usb|ladekabel/, "plug"],
  [/roaming/, "tower"],
  [/macht|souverän|herrschaft/, "crown"],
  [/partei|kandidat|opposition/, "flag"],
  [/migration|heimat|zielland|zuwander|push|pull/, "arrow"],
  [/wohnung/, "house"],
  [/volk|bürger|menschen|gruppe|verband|jeder|alle |gemeinsam|gesellschaft|bevölkerung|anwohner|mitglieder|interessen/, "people"],
  [/person|politiker|jugendlich|jung/, "person"],
  [/jahr|alter|ab 1[68]|18-jährig/, "calendar"],
];

export const iconFor = (text: string): string | undefined => {
  if (ICON_FOR_TEXT[text.trim()]) return ICON_FOR_TEXT[text.trim()];
  const s = ` ${text.toLowerCase()} `;
  for (const [re, k] of KEYS) if (re.test(s)) return k;
  return undefined;
};

export const TOPIC_ICON = ["ballot", "dove", "globe", "phone", "eu", "elder", "scales", "megaphone", "family", "bulb"];

export const INK_L = "#1d1d1b";

const renderShape = (s: Shape, i: number, stroke: string, sw: number, backing: boolean) => {
  const fillOn = s[0] === "p" ? s[2] : s[0] === "c" ? s[4] : s[0] === "r" ? s[6] : s[5];
  const fill = backing ? "#fff" : fillOn ? "#fff" : "none";
  const common = { stroke, strokeWidth: sw, fill, strokeLinecap: "round" as const, strokeLinejoin: "round" as const };
  if (s[0] === "p") return <path key={i} d={s[1]} {...common} />;
  if (s[0] === "c") return <circle key={i} cx={s[1]} cy={s[2]} r={s[3]} {...common} />;
  if (s[0] === "r") return <rect key={i} x={s[1]} y={s[2]} width={s[3]} height={s[4]} rx={s[5] ?? 0} {...common} />;
  return <ellipse key={i} cx={s[1]} cy={s[2]} rx={s[3]} ry={s[4]} {...common} />;
};

// Papier-Ausschnitt: dicker weißer Rand + Schatten, darauf die schwarzen Linien
export const Icon: React.FC<{ name: string; size: number; color?: string; cut?: boolean }> = ({ name, size, color = INK_L, cut = true }) => {
  const shapes = ICONS[name];
  if (!shapes) return null;
  return (
    <svg width={size} height={size} viewBox="-20 -20 240 240" style={{ overflow: "visible", filter: cut ? "drop-shadow(2px 4px 3px rgba(0,0,0,0.22))" : undefined }}>
      {cut ? shapes.map((s, i) => renderShape(s, i, "#fff", 30, true)) : null}
      {shapes.map((s, i) => renderShape(s, i + 100, color, 6, false))}
    </svg>
  );
};

// gezeichnete Hand (von oben, Finger zeigen nach oben); Fingerspitzen bei (100, 20) im 200×420-Raster
export const HandArt: React.FC<{ w: number }> = ({ w }) => (
  <svg width={w} height={(w * 420) / 200} viewBox="0 0 200 420" style={{ overflow: "visible", filter: "drop-shadow(6px 10px 8px rgba(0,0,0,0.25))" }}>
    <path
      d="M58 420 L56 250 Q34 226 22 196 Q16 180 30 176 Q42 174 52 192 L64 214 L62 78 Q62 60 77 60 Q92 60 92 78 L94 196 L96 44 Q96 24 112 24 Q128 24 128 44 L126 196 L132 66 Q133 48 148 49 Q162 51 160 68 L154 204 L164 112 Q166 97 178 99 Q190 102 188 117 L174 252 Q168 300 160 330 L156 420 Z"
      fill="#f3d2b5" stroke={INK_L} strokeWidth={5} strokeLinejoin="round"
    />
    <path d="M92 196 L94 214 M126 196 L126 214 M154 204 L152 220" stroke={INK_L} strokeWidth={4} strokeLinecap="round" fill="none" />
    <path d="M70 300 Q110 312 150 300" stroke="#d9b08f" strokeWidth={5} fill="none" strokeLinecap="round" />
  </svg>
);
