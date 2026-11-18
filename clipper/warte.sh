#!/usr/bin/env bash
# Wartet, bis der Kanal offline ist und die neue Aufzeichnung auf Twitch erscheint, und clippt sie dann.
#   setsid nohup ./clipper/warte.sh ishowspeed 5 > out/clips/warte.log 2>&1 &
K=${1:-ishowspeed}
N=${2:-5}
cd "$(dirname "$0")/.." || exit 1
newest() { yt-dlp --no-warnings --flat-playlist -I 1 --print id "https://www.twitch.tv/$K/videos?filter=archives&sort=time" 2>/dev/null | tail -1; }
OLD=$(newest)
echo "$(date -u +%H:%M) warte auf neue Aufzeichnung von $K (letzte: $OLD)"
while true; do
  if ! yt-dlp --no-warnings --skip-download --print live_status "https://www.twitch.tv/$K" 2>/dev/null | grep -q is_live; then
    NEW=$(newest)
    if [ -n "$NEW" ] && [ "$NEW" != "$OLD" ]; then
      echo "$(date -u +%H:%M) offline – neue Aufzeichnung $NEW, starte Clipper"
      python3 -u clipper/clipper.py "https://www.twitch.tv/videos/${NEW#v}" --anzahl "$N"
      echo "FERTIG"
      exit 0
    fi
    echo "$(date -u +%H:%M) offline, Aufzeichnung noch nicht da"
  else
    echo "$(date -u +%H:%M) noch live"
  fi
  sleep 600
done
