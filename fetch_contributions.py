"""Scrape the public contribution calendar (no token needed)."""
import json, os, re, sys, datetime as dt
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GH_USER") or (sys.argv[1] if len(sys.argv) > 1 else "")
if not USER:
    sys.exit("Usage: GH_USER=yourname python scripts/fetch_contributions.py")

html = requests.get(f"https://github.com/users/{USER}/contributions",
                    headers={"User-Agent": "profile-readme-bot"}, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

tips = {t.get("for"): t.get_text(strip=True) for t in soup.find_all("tool-tip")}
days = []
for td in soup.select("td.ContributionCalendar-day[data-date]"):
    text = tips.get(td.get("id"), "")
    m = re.match(r"(\d+)\s+contribution", text)
    days.append({"date": td["data-date"],
                 "count": int(m.group(1)) if m else 0,
                 "level": int(td.get("data-level", 0))})
days.sort(key=lambda d: d["date"])
if not days:
    sys.exit("No contribution cells found - GitHub markup may have changed.")

# stats
total = sum(d["count"] for d in days)
longest = cur = 0
for d in days:
    cur = cur + 1 if d["count"] else 0
    longest = max(longest, cur)
today = dt.date.today().isoformat()
streak = 0
for d in reversed([x for x in days if x["date"] <= today]):
    if d["count"]:
        streak += 1
    elif d["date"] != today:   # today may still be empty
        break
best = max(days, key=lambda d: d["count"])

os.makedirs("data", exist_ok=True)
json.dump({"user": USER, "total": total, "current_streak": streak,
           "longest_streak": longest, "best_day": best, "days": days},
          open("data/contributions.json", "w"), indent=1)
print(f"{USER}: {total} contributions, streak {streak}, longest {longest}")
