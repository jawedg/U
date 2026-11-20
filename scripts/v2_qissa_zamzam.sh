#!/usr/bin/env bash
# QISSAH Folge 2, Korrekturen nach Nutzer-Feedback: Kopfschwenk (abschied 1–165), Wasser-Becken höher (wall 1–135,
# quelle 175–248 + Zwischenbilder), Pilger nicht durch Säulen (heute komplett). Gelöschte Bilder werden neu gerendert, dann
# werden die 4 Einstellungen neu kodiert. Fortsetzbar (0-Byte-Platzhalter werden vorher gelöscht).
set -u
cd "$(dirname "$0")/.."
find out/zz_frames -name '*.png' -size -1k -delete 2>/dev/null
JOBS=2 SAMPLES=2 MID_SHOTS="quelle" ./scripts/render_qissa_zamzam.sh abschied wall quelle heute
echo "✅ v2 Bilder fertig $(date -u +%T)"
