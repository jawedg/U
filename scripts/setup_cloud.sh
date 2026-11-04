#!/usr/bin/env bash
# Richtet eine frische Cloud-Sitzung ein (idempotent): Node-Pakete, Python-Pakete, Whisper-Modell.
set -e
cd "$(dirname "$0")/.."
[ -d node_modules ] || npm install --no-audit --no-fund
python3 -c "import sherpa_onnx, soundfile" 2>/dev/null || pip install -q "sherpa-onnx==1.12.40" soundfile numpy
if [ ! -d models/sherpa-onnx-whisper-base ] && [ ! -d /tmp/models/sherpa-onnx-whisper-base ]; then
  mkdir -p models && cd models
  curl -sSL -o wb.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-base.tar.bz2
  tar xjf wb.tar.bz2 && rm wb.tar.bz2 && cd ..
fi
if [ -z "$GEMINI_API_KEY" ] && [ ! -f /tmp/gem/key ]; then
  echo "⚠️  Kein GEMINI_API_KEY – bitte als Secret in den Umgebungs-Einstellungen eintragen."
fi
echo "✅ Einrichtung fertig"
