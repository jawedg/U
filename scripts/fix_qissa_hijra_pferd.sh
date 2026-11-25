#!/usr/bin/env bash
# Folge 5, Nachbesserung: Einstellung "pferd" (Aufsteigen) neu rendern, nur Remotion-Teil 2 neu, dann Kleinversion.
cd /home/user/U
if [ ! -s public/qissa_hijra/shots/pferd.mp4 ] || [ ! -f out/hj_fix_pferd.rendered ]; then
  rm -f public/qissa_hijra/shots/pferd.mp4
  find out/hj_frames -name '*.png' -size -1k -delete 2>/dev/null
  SAMPLES=2 MID_SHOTS="pferd" ./scripts/render_qissa_hijra.sh pferd >> out/hj_render.log 2>&1
  [ -s public/qissa_hijra/shots/pferd.mp4 ] || { echo "❌ pferd nicht fertig"; exit 1; }
  touch out/hj_fix_pferd.rendered
  rm -f out/hj_parts/p2.mp4.ok
fi
./scripts/finish_qissa_hijra.sh && echo "✅ fertig: out/qissah-hijra-klein.mp4 $(date +%T)"
