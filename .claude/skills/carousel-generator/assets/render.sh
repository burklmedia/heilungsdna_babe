#!/usr/bin/env bash
# Rendert die Slides einer Karussell-HTML als PNGs (1080x1350) über Chrome/Chromium headless.
#
#   bash render.sh karussell.html            # -> slide_1.png … slide_N.png (neben der HTML)
#   bash render.sh karussell.html out/        # PNGs in Ordner out/
#
# Voraussetzung: Google Chrome oder Chromium ist installiert. Kein Internet nötig.
set -euo pipefail

HTML="${1:-karussell.html}"
if [ ! -f "$HTML" ]; then
  echo "Datei nicht gefunden: $HTML" >&2
  exit 1
fi

# Absoluter Pfad + file:// URL (relative Fonts/Styles greifen dann)
HTML_ABS="$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"
OUTDIR="${2:-$(dirname "$HTML_ABS")}"
mkdir -p "$OUTDIR"

# Chrome/Chromium finden
CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser chrome; do
  if command -v "$c" >/dev/null 2>&1; then CHROME="$c"; break; fi
done
# macOS-Standardpfade
if [ -z "$CHROME" ]; then
  for p in \
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    "/Applications/Chromium.app/Contents/MacOS/Chromium"; do
    if [ -x "$p" ]; then CHROME="$p"; break; fi
  done
fi
if [ -z "$CHROME" ]; then
  echo "Chrome/Chromium nicht gefunden. Bitte Google Chrome oder Chromium installieren." >&2
  exit 1
fi

# Anzahl Slides aus data-slide=… ermitteln
COUNT="$(grep -oE 'data-slide="[0-9]+"' "$HTML_ABS" | grep -oE '[0-9]+' | sort -n | tail -1)"
if [ -z "${COUNT:-}" ]; then
  echo "Keine Slides gefunden (data-slide=\"…\" fehlt in $HTML)." >&2
  exit 1
fi

echo "Rendere $COUNT Slides aus $(basename "$HTML_ABS") …"
for i in $(seq 1 "$COUNT"); do
  OUT="$OUTDIR/slide_${i}.png"
  "$CHROME" \
    --headless=new \
    --no-sandbox \
    --disable-gpu \
    --hide-scrollbars \
    --force-device-scale-factor=1 \
    --default-background-color=00000000 \
    --window-size=1080,1350 \
    --screenshot="$OUT" \
    "file://${HTML_ABS}?slide=${i}" >/dev/null 2>&1 || \
  "$CHROME" \
    --headless \
    --no-sandbox \
    --disable-gpu \
    --hide-scrollbars \
    --force-device-scale-factor=1 \
    --window-size=1080,1350 \
    --screenshot="$OUT" \
    "file://${HTML_ABS}?slide=${i}" >/dev/null 2>&1
  echo "  ✓ $(basename "$OUT")"
done

echo "Fertig. $COUNT PNGs in: $OUTDIR"
