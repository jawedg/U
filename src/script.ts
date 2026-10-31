// ✏️ HIER DEINEN TEXT ÄNDERN.
// Jede Szene = ein Bildschirm. Wörter in *Sternchen* werden farbig hervorgehoben.
// Danach: `npm run video` (Stimme erzeugen + rendern) oder nur `npm run render` (ohne Stimme).

export type Scene = {
  text: string;
  emoji?: string;
};

export const TITLE = "KI-Videos gratis";

export const SCENES: Scene[] = [
  { emoji: "🤯", text: "Du kannst solche *Videos* komplett *kostenlos* machen." },
  { emoji: "🤖", text: "Claude schreibt das *Skript* und den *Code* für das Video." },
  { emoji: "🎬", text: "*Remotion* macht daraus eine fertige *MP4*." },
  { emoji: "🎙️", text: "Die Stimme kommt *gratis* von *Edge TTS*." },
  { emoji: "📱", text: "Format *9:16* – perfekt für *TikTok*." },
  { emoji: "👉", text: "Folg mir für den *ganzen Ablauf*!" },
];
