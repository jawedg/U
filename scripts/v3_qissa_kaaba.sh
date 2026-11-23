#!/usr/bin/env bash
# QISSAH Folge 3 v3 (Nutzer-Korrekturen 23.11.): Kind in „zelte“ blieb stehen -> zelte neu gerendert;
# e18/e19 „Kaaba“ ohne „al-“ neu gesprochen + richtige Untertitel-Zeiten -> nur Remotion-Teile 0, 6, 7 neu, dann HEVC.
#   setsid nohup ./scripts/v3_qissa_kaaba.sh > out/kb_v3.log 2>&1 &
set -u
cd "$(dirname "$0")/.."
while [ ! -s public/qissa_kaaba/shots/zelte.mp4 ]; do
  if ! pgrep -f render_qissa_kaaba.sh > /dev/null; then
    echo "▶ zelte neu starten $(date -u +%T)"
    JOBS=2 SAMPLES=2 MID_SHOTS=segen ./scripts/render_qissa_kaaba.sh zelte >> out/kb_v3_zelte.log 2>&1
  fi
  sleep 30
done
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 public/qissa_kaaba/shots/zelte.mp4)
echo "✅ zelte: $n Bilder $(date -u +%T)"
python3 scripts/sfx_qissa_kaaba.py
rm -f out/kb_parts/p0.mp4.ok out/kb_parts/p6.mp4.ok out/kb_parts/p7.mp4.ok
./scripts/finish_qissa_kaaba.sh || echo "❌ finish"
