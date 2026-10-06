"""source-prepped.png -> self-typing monochrome ASCII portrait (avi-ascii.svg).
Bright pixels -> dense glyphs, black -> blank, drawn on a dark card."""
import cv2, numpy as np
from xml.sax.saxutils import escape

COLS = 100
RAMP = " .`:-=+*cs#%@"          # blank -> dense
CHAR_W, LINE_H, FONT = 6.0, 10.0, 10   # glyph cell in SVG px
FILL, BG = "#c9d1d9", "#0d1117"

img = cv2.imread("source-prepped.png", 0)
h, w = img.shape
rows = int(COLS * h / w * (CHAR_W / LINE_H))
small = cv2.resize(img, (COLS, rows), interpolation=cv2.INTER_AREA).astype(float) / 255
fgv = small[small > 0.04]
lo, hi = np.percentile(fgv, 4), np.percentile(fgv, 99)
small = np.where(small > 0.04, np.clip((small - lo) / (hi - lo), 0, 1) ** 1.25, 0)  # push midtones down so features read
idx = (small * (len(RAMP) - 1)).round().astype(int)
lines = ["".join(RAMP[i] for i in r).rstrip() for r in idx]

W, H = COLS * CHAR_W + 20, rows * LINE_H + 20
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">',
       f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>', "<defs>"]
for i in range(rows):
    t = i * 0.07
    out.append(f'<clipPath id="r{i}"><rect x="10" y="{10+i*LINE_H-1:.1f}" width="0" height="{LINE_H+1}">'
               f'<animate attributeName="width" from="0" to="{COLS*CHAR_W:.0f}" dur="0.55s" begin="{t:.2f}s" fill="freeze"/>'
               f'</rect></clipPath>')
out.append("</defs>")
for i, ln in enumerate(lines):
    if not ln.strip():
        continue
    y = 10 + (i + 1) * LINE_H - 2
    out.append(f'<text x="10" y="{y:.1f}" font-family="ui-monospace,Menlo,Consolas,\'DejaVu Sans Mono\',monospace" '
               f'font-size="{FONT}" fill="{FILL}" xml:space="preserve" textLength="{len(ln)*CHAR_W:.0f}" '
               f'lengthAdjust="spacing" clip-path="url(#r{i})">{escape(ln)}</text>')
    t = i * 0.07   # block cursor riding the wipe edge, then vanishing
    out.append(f'<rect y="{10+i*LINE_H:.1f}" width="{CHAR_W}" height="{LINE_H-1}" fill="{FILL}" opacity="0">'
               f'<animate attributeName="x" from="10" to="{10+COLS*CHAR_W:.0f}" dur="0.55s" begin="{t:.2f}s" fill="freeze"/>'
               f'<animate attributeName="opacity" values="0.9;0.9;0" keyTimes="0;0.95;1" dur="0.55s" begin="{t:.2f}s" fill="freeze"/></rect>')
out.append("</svg>")
open("avi-ascii.svg", "w").write("\n".join(out))
open("ascii-preview.txt", "w").write("\n".join(lines))
print(f"wrote avi-ascii.svg  ({COLS}x{rows})")
