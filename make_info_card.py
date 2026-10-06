"""Neofetch-style info card (info-card.svg). Edit ROWS, then re-run.
STATIC=1 python scripts/make_info_card.py  -> frozen frame (no animation)."""
import os, textwrap
from xml.sax.saxutils import escape

STATIC = os.environ.get("STATIC") == "1"
W, H = 490, 465
KEYW, WRAP = 11, 55
BG, BAR, FG, DIM = "#0d1117", "#161b22", "#c9d1d9", "#8b949e"
KEY, ACC = "#39d353", "#e8c468"

TITLE = "shiv@github ~ $ neofetch"
ROWS = [
    ("Name",    "Shivang  (shiv0xparanoid)"),
    ("Now",     "Solo founder, HOLO✦PAD Industries · B.Tech AI & ML, NIMS University Jaipur"),
    ("Building","HOLO✦PAD (WebGL 3D platform) · QVANTA for SIH 2026 · Samvaad (RAG chatbot)"),
    ("Prev",    "SDE Intern @ Google · Backend Engineer Intern @ Nintendo, Kyoto"),
    ("Stack",   "Python · PyTorch · OpenCV · Three.js · WebGL · React · FastAPI · Docker"),
    ("Honors",  "Techfest IIT Bombay '25 · Google for Startups Accelerator India · NVIDIA Developer Program"),
    ("Papers",  "Virtual Humans in WebGL · HOLO✦PAD: Perception-Driven Holographic Visualization"),
    ("Web",     "holopad.netlify.app · toodumb.netlify.app"),
]

FONT = "ui-monospace,Menlo,Consolas,'DejaVu Sans Mono',monospace"
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       f'<style>.l{{font:12px {FONT};fill:{FG}}}.k{{fill:{KEY};font-weight:bold}}'
       + ("" if STATIC else ".r{opacity:0;animation:in .45s ease-out forwards}"
          "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}")
       + '</style>',
       f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>',
       f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v22H0z" fill="{BAR}"/>',
       '<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="36" cy="16" r="5" fill="#ffbd2e"/>'
       '<circle cx="54" cy="16" r="5" fill="#27c93f"/>',
       f'<text x="{W/2}" y="20" text-anchor="middle" class="l" style="fill:{DIM}">{escape(TITLE)}</text>']

y, n = 58, 0
def row(inner):
    global n
    delay = "" if STATIC else f' style="animation-delay:{0.4 + n*0.18:.2f}s"'
    out.append(f'<text class="l r" x="20" y="{y}" xml:space="preserve"{delay}>{inner}</text>')
    n += 1

row(f'<tspan fill="{ACC}">shiv</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{ACC}">github</tspan>')
y += 16
row(f'<tspan fill="{DIM}">{"─"*34}</tspan>')
y += 24
for key, val in ROWS:
    lines = textwrap.wrap(val, WRAP - KEYW) or [""]
    for i, ln in enumerate(lines):
        k = f'{key+":":<{KEYW}}' if i == 0 else " " * KEYW
        row(f'<tspan class="k">{escape(k)}</tspan>{escape(ln)}')
        y += 17
    y += 9
# colour palette strip, like neofetch
y += 2
cols = ["#ff5f56", "#ffbd2e", "#27c93f", "#39d353", "#58a6ff", "#bc8cff", "#e8c468", "#c9d1d9"]
delay = "" if STATIC else f' style="animation-delay:{0.4 + n*0.18:.2f}s"'
out.append(f'<g class="r"{delay}>' + "".join(
    f'<rect x="{20+i*26}" y="{y-10}" width="24" height="12" rx="2" fill="{c}"/>' for i, c in enumerate(cols)) + '</g>')
assert y < H, f"content overflows card: y={y} > {H}"
out.append("</svg>")
open("info-card.svg", "w").write("\n".join(out))
print("wrote info-card.svg, last y =", y)
