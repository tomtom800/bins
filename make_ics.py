#!/usr/bin/env python3
"""Fetch North Yorkshire Council (Hambleton) bin collections and write an ICS feed.

Usage:
  UPRN=10001286457 python make_ics.py            # fetch live, write bins.ics
  python make_ics.py --from-file sample.html     # parse a saved response (testing)
"""
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta

AREA = os.environ.get("AREA", "Hambleton")
URL = "https://www.northyorks.gov.uk/bin-calendar/{area}/results/{uprn}/ajax?_wrapper_format=drupal_ajax"
OUT = os.environ.get("OUT", "bins.ics")
EMOJI = {"household": "🗑️", "recycling": "♻️", "garden": "🍃", "food": "🍎", "glass": "🍾"}


def fetch(uprn: str) -> str:
    req = urllib.request.Request(
        URL.format(area=AREA, uprn=uprn),
        data=b"",
        method="POST",
        headers={"User-Agent": "Mozilla/5.0 (bin-calendar-ics)", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        commands = json.loads(r.read().decode("utf-8"))
    return "".join(c.get("data", "") for c in commands if c.get("command") == "insert")


def parse(markup: str):
    tbody = re.search(r"<tbody>(.*?)</tbody>", markup, re.S)
    if not tbody:
        return []
    events = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", tbody.group(1), re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
        if len(cells) < 3:
            continue
        date = datetime.strptime(html.unescape(cells[0]).strip(), "%d %B %Y").date()
        for part in re.split(r"<br\s*/?>", cells[2]):
            name = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", part)).split())
            if name:
                events.append((date, name))
    return events


def to_ics(events) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//bins//North Yorkshire bin collections//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Bin collections",
        "X-PUBLISHED-TTL:PT12H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
    ]
    for date, name in sorted(events):
        emoji = next((e for k, e in EMOJI.items() if k in name.lower()), "🗑️")
        d = date.strftime("%Y%m%d")
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{d}-{slug}@bins",
            f"DTSTAMP:{d}T000000Z",  # fixed so the file only changes when collections do
            f"DTSTART;VALUE=DATE:{d}",
            f"DTEND;VALUE=DATE:{(date + timedelta(days=1)).strftime('%Y%m%d')}",
            f"SUMMARY:{emoji} {name}",
            "TRANSP:TRANSPARENT",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--from-file":
        markup = open(sys.argv[2], encoding="utf-8").read()
    else:
        uprn = os.environ.get("UPRN")
        if not uprn:
            sys.exit("UPRN environment variable is required")
        markup = fetch(uprn)
    events = parse(markup)
    if not events:
        sys.exit("No collections parsed - leaving existing calendar untouched")
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write(to_ics(events))
    print(f"Wrote {len(events)} collections to {OUT}")


if __name__ == "__main__":
    main()
