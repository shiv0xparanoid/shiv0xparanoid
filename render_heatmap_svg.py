"""Render data/contributions.json as an animated 53x7 SVG heatmap."""
import json, datetime as dt

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP, PAD_L, PAD_T = 13, 4, 36, 40
data = json.load(open("data/contributions.json"))
days = data["days"]

first = dt.date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7            # Sunday = row 0
weeks = (len(days) + offset + 6) // 7
W = PAD_L + weeks * (CELL + GAP) + 20
H = PAD_T + 7 * (CELL + GAP) + 50

rects = []
for i, d in enumerate(days):
    col, row = (i + offset) // 7, (i + offset) % 7
    x, y = PAD_L + col * (CELL + GAP), PAD_T + row * (CELL + GAP)
    lvl = min(d["level"], 4) if d["count"] < 15 or d["level"] < 4 else 5
    delay = (col + row) * 0.02
    rects.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                 f'rx="3" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.2f}s">'
                 f'<title>{d["count"]} on {d["date"]}</title></rect>')

months, last = [], None
for i, d in enumerate(days):
    m = d["date"][5:7]
    col = (i + offset) // 7
    if m != last and (i + offset) % 7 < 3:
        months.append(f'<text x="{PAD_L + col*(CELL+GAP)}" y="28" class="t">'
                      f'{dt.date.fromisoformat(d["date"]).strftime("%b")}</text>')
        last = m

legend_x = W - 20 - 6 * (CELL + 4) - 70
legend = "".join(f'<rect x="{legend_x+40+i*(CELL+4)}" y="{H-30}" width="{CELL}" '
                 f'height="{CELL}" rx="3" fill="{c}"/>' for i, c in enumerate(PALETTE))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
.t{{font:11px ui-monospace,Menlo,monospace;fill:#8b949e}}
.c{{opacity:0;transform:translateY(-8px);animation:in .5s ease-out forwards}}
@keyframes in{{to{{opacity:1;transform:translateY(0)}}}}
</style>
<rect width="100%" height="100%" rx="10" fill="#0d1117"/>
{"".join(months)}
{"".join(rects)}
<text x="{PAD_L}" y="{H-19}" class="t">{data["total"]:,} contributions in the last year · streak {data["current_streak"]}d · longest {data["longest_streak"]}d</text>
<text x="{legend_x}" y="{H-19}" class="t">Less</text>{legend}
<text x="{legend_x+40+6*(CELL+4)}" y="{H-19}" class="t">More</text>
</svg>'''
open("contrib-heatmap.svg", "w").write(svg)
print("wrote contrib-heatmap.svg")
