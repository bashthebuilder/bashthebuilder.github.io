#!/usr/bin/env python3
"""
Generate the OpenGraph card for each MyTh entry.

One 1200x630 PNG per entry, written to assets/og/myth-NNN.png. These are what
LinkedIn, Bluesky, Slack and X render when someone shares an entry, so they
carry the entry's own number and title rather than a portrait that is identical
for every essay.

Reads the same myth-content/NNN.html sources as build_myth.py. Run either
script directly, or build_myth.py, which calls this one.
"""

import html
import json
import os
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("error: Pillow is required — pip3 install --user Pillow")

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "myth-content")
OUT = os.path.join(ROOT, "assets", "og")

W, H = 1200, 630
PAD = 92
BAR = 12                      # left accent bar, echoing .myth::before

BG = (8, 10, 15)              # --bg-dark
WHITE = (248, 250, 252)       # --text-primary
MUTED = (148, 163, 184)       # --text-muted
INDIGO = (129, 140, 248)
# --accent-liquid: 135deg, #6366f1 -> #a855f7 -> #ec4899
STOPS = [(0.0, (99, 102, 241)), (0.5, (168, 85, 247)), (1.0, (236, 72, 153))]

SF = "/System/Library/Fonts/SFNS.ttf"

# Words a truncated line should never end on.
DANGLING = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "is",
            "it", "of", "on", "or", "that", "the", "their", "to", "was", "were",
            "what", "when", "which", "who", "with", "its", "into", "than", "then"}


def font(size, weight="Regular"):
    f = ImageFont.truetype(SF, size)
    try:
        f.set_variation_by_name(weight)
    except Exception:
        pass
    return f


def ramp(t):
    """Colour at position t along the accent gradient."""
    t = max(0.0, min(1.0, t))
    for (t0, c0), (t1, c1) in zip(STOPS, STOPS[1:]):
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            return tuple(round(a + (b - a) * k) for a, b in zip(c0, c1))
    return STOPS[-1][1]


def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def background():
    """Base colour, a diagonal accent wash, and a soft glow behind the number."""
    img = Image.new("RGB", (W, H), BG)

    wash = Image.new("RGB", (W, H))
    wd = ImageDraw.Draw(wash)
    for x in range(W):
        wd.line([(x, 0), (x, H)], fill=ramp(x / W))
    # Fade the wash in from the left so the type stays legible over it.
    mask = Image.new("L", (W, H))
    md = ImageDraw.Draw(mask)
    for x in range(W):
        md.line([(x, 0), (x, H)], fill=int(10 + 46 * (x / W) ** 1.7))
    img = Image.composite(wash, img, mask)

    # Radial glow, upper right, well away from the title block.
    glow = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(glow)
    cx, cy, r = 1020, 150, 430
    for i in range(28, 0, -1):
        k = i / 28
        gd.ellipse([cx - r * k, cy - r * k, cx + r * k, cy + r * k],
                   fill=tuple(round(b + (g - b) * (1 - k) * 0.5)
                              for b, g in zip(BG, (99, 102, 241))))
    img = Image.blend(img, glow, 0.5)

    d = ImageDraw.Draw(img)
    for y in range(H):                       # left accent bar
        d.line([(0, y), (BAR, y)], fill=ramp(y / H))
    return img


def tracked(d, xy, text, f, fill, track):
    """PIL has no letter-spacing; draw glyph by glyph."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + track
    return x


def wrap(d, text, f, width, max_lines):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        while lines[-1] and d.textlength(lines[-1] + "…", font=f) > width:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else lines[-1][:-1]
        # "...that grew and…" reads as a bug; step back off dangling words.
        while " " in lines[-1] and lines[-1].rsplit(" ", 1)[1].lower().strip(",;:") in DANGLING:
            lines[-1] = lines[-1].rsplit(" ", 1)[0]
        lines[-1] = lines[-1].rstrip(" ,;:—-")
        if not lines[-1].endswith((".", "!", "?")):
            lines[-1] += "…"
    return lines


def sentences(text, d, f, width, max_lines):
    """Prefer whole sentences: a standfirst cut mid-clause reads as an error."""
    parts = re.findall(r"[^.!?]+[.!?]*", text)
    kept = ""
    for p in parts:
        trial = (kept + p).strip()
        if len(wrap(d, trial, f, width, max_lines + 1)) > max_lines:
            break
        kept = re.sub(r"\s+", " ", trial) + " "
    kept = kept.strip()
    return wrap(d, kept or text, f, width, max_lines)


def card(entry):
    img = background()
    d = ImageDraw.Draw(img)
    x = PAD
    avail = W - PAD - 150
    TOP, FLOOR = 150, H - 148       # title starts here; nothing may cross FLOOR

    # Eyebrow: MYTH · 004
    ef = font(27, "Bold")
    end = tracked(d, (x, 78), "MYTH", ef, MUTED, 5.5)
    end = tracked(d, (end + 14, 78), "·", ef, INDIGO, 5.5)
    tracked(d, (end + 14, 78), entry["number"], ef, INDIGO, 5.5)

    # Fit the title and standfirst together: step the title down, and drop the
    # standfirst to one line, until the whole block clears the footer.
    title = strip_tags(entry["title"])
    dek = strip_tags(entry["dek"])
    df = font(27, "Regular")

    for dek_lines in (2, 1):
        for size, maxlines in ((80, 3), (72, 3), (66, 3), (60, 4), (54, 4)):
            tf = font(size, "Black")
            lines = wrap(d, title, tf, avail, maxlines)
            if lines[-1].endswith("…"):
                continue
            dlines = sentences(dek, d, df, avail, dek_lines)
            lh = int(size * 1.14)
            bottom = TOP + lh * len(lines) + 18 + 30 + 38 * len(dlines)
            if bottom <= FLOOR:
                break
        else:
            continue
        break

    # Centre the block in the space between eyebrow and footer, so a short
    # title does not leave the card bottom-heavy with dead space.
    block = lh * len(lines) + 18 + 30 + 38 * len(dlines)
    y = TOP + max(0, (FLOOR - TOP - block) // 2)

    for ln in lines:
        d.text((x, y), ln, font=tf, fill=WHITE)
        y += lh

    # Rule, then the standfirst.
    y += 18
    d.line([(x, y), (x + 108, y)], fill=INDIGO, width=4)
    y += 30
    for ln in dlines:
        d.text((x, y), ln, font=df, fill=MUTED)
        y += 38

    # Footer, pinned to the baseline.
    fy = H - 78
    nf, mf = font(26, "Bold"), font(25, "Regular")
    d.text((x, fy), "Shoaib Jameel", font=nf, fill=WHITE)
    off = d.textlength("Shoaib Jameel", font=nf)
    d.text((x + off + 16, fy + 1), "· University of Southampton", font=mf, fill=MUTED)

    meta = entry["date"] + (f'  ·  {entry["readtime"]}' if entry.get("readtime") else "")
    d.text((W - PAD - d.textlength(meta, font=mf), fy + 1), meta, font=mf, fill=MUTED)
    return img


def load_entries():
    entries = []
    for name in sorted(os.listdir(CONTENT)):
        if name.endswith(".html"):
            raw = open(os.path.join(CONTENT, name)).read()
            m = re.match(r"<!--META\n(.*?)\nMETA-->", raw, re.S)
            if m:
                entries.append(json.loads(m.group(1)))
    return sorted(entries, key=lambda e: int(e["number"]), reverse=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for e in load_entries():
        path = os.path.join(OUT, f"myth-{e['number']}.png")
        card(e).save(path, "PNG", optimize=True)
        print(f"  {os.path.relpath(path, ROOT):<32} {os.path.getsize(path):>7,} bytes  "
              f"{strip_tags(e['title'])[:44]}")


if __name__ == "__main__":
    main()
