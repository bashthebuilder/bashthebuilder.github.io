#!/usr/bin/env python3
"""
Build the MyTh section: one page per entry, the index, and the Atom feed.

Source of truth is myth-content/NNN.html — a metadata header in an HTML
comment, followed by the entry body. Everything else in the MyTh section is
generated from those files and should not be hand-edited.

    Adding MyTh 005
    ---------------
    1. cp myth-content/004.html myth-content/005.html and rewrite it.
    2. python3 build_myth.py
    3. Commit myth-content/005.html and the regenerated files.

Generated: myth-NNN.html (one per entry), myth.html (index), feed.xml,
and the MyTh block of sitemap.xml.
"""

import html
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "myth-content")
SITE = "https://bashthebuilder.github.io"
AUTHOR = "Shoaib Jameel"
EMAIL = "M.S.Jameel@southampton.ac.uk"
OG_IMAGE = f"{SITE}/Shoaib_Profile_ID.jpg"

NAV = """    <nav>
        <div class="container nav-container">
            <a href="index.html" class="nav-logo">SHOAIB JAMEEL</a>
            <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false"><span></span><span></span><span></span></button>
            <div class="nav-links">
                <a href="index.html">Profile</a>
                <a href="timeline.html">Timeline</a>
                <a href="undergraduate.html">Early Work</a>
                <a href="thesis.html">Thesis</a>
                <a href="publications.html">Research</a>
                <a href="cultural-modelling.html">Cultural AI</a>
                <a href="resources.html">Defence AI</a>
                <a href="industry.html">Industry Impact</a>
                <a href="ai-leadership.html">AI Leadership</a>
                <a href="students.html">Mentorship</a>
                <a href="teaching.html">Teaching</a>
                <a href="competitive-programming.html">Competitive Coding</a>
                <a href="press.html">Press</a>
                <a href="myth.html" class="active">MyTh</a>
                <a href="cv.html">CV</a>
            </div>
        </div>
    </nav>
"""

FOOTER = """    <footer>
        <div class="container">
            <p>&copy; 2026 Shoaib Jameel &middot; University of Southampton</p>
        </div>
    </footer>
"""


def strip_tags(s):
    """Plain text for meta descriptions and feed summaries."""
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def load_entries():
    entries = []
    for name in sorted(os.listdir(CONTENT)):
        if not name.endswith(".html"):
            continue
        raw = open(os.path.join(CONTENT, name)).read()
        m = re.match(r"<!--META\n(.*?)\nMETA-->\n(.*)", raw, re.S)
        if not m:
            sys.exit(f"error: {name} has no META header")
        meta = json.loads(m.group(1))
        meta["body"] = m.group(2).strip()
        entries.append(meta)
    # Newest first, by entry number. Numbers are permanent and never reused.
    entries.sort(key=lambda e: int(e["number"]), reverse=True)
    return entries


def rewrite_crossrefs(body):
    """#myth-003 pointed at a section of the old single page; now it is a page."""
    return re.sub(r'href="#myth-(\d+)"', r'href="myth-\1.html"', body)


def meta_tags(title, desc, url, *, article=None, image=OG_IMAGE):
    t = [
        f'    <title>{title}</title>',
        '    <link rel="icon" type="image/svg+xml" href="favicon.svg">',
        f'    <meta name="description" content="{desc}">',
        f'    <link rel="canonical" href="{url}">',
        '    <link rel="alternate" type="application/atom+xml" title="MyTh &mdash; My Thoughts" href="feed.xml">',
        f'    <meta property="og:type" content="{"article" if article else "website"}">',
        '    <meta property="og:site_name" content="Shoaib Jameel">',
        f'    <meta property="og:title" content="{title}">',
        f'    <meta property="og:description" content="{desc}">',
        f'    <meta property="og:image" content="{image}">',
        '    <meta property="og:image:width" content="1200">',
        '    <meta property="og:image:height" content="630">',
        f'    <meta property="og:image:alt" content="{html.escape(strip_tags(title), quote=True)}">',
        f'    <meta property="og:url" content="{url}">',
        '    <meta name="twitter:card" content="summary_large_image">',
        f'    <meta name="twitter:title" content="{title}">',
        f'    <meta name="twitter:description" content="{desc}">',
        f'    <meta name="twitter:image" content="{image}">',
    ]
    if article:
        t += [
            f'    <meta property="article:published_time" content="{article["iso"]}">',
            f'    <meta property="article:author" content="{AUTHOR}">',
        ] + [f'    <meta property="article:tag" content="{tag}">' for tag in article["tags"]]
    return "\n".join(t)


def jsonld(entry, url, image):
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": strip_tags(entry["title"]),
        "description": strip_tags(entry["dek"]),
        "datePublished": entry["iso"],
        "dateModified": entry["iso"],
        "author": {"@type": "Person", "name": AUTHOR,
                   "email": EMAIL, "url": SITE + "/index.html"},
        "publisher": {"@type": "Person", "name": AUTHOR},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "image": image,
        "keywords": ", ".join(entry["tags"]),
        "isPartOf": {"@type": "Blog", "name": "MyTh — My Thoughts",
                     "@id": SITE + "/myth.html"},
    }
    return ('    <script type="application/ld+json">\n'
            + json.dumps(data, indent=4, ensure_ascii=False)
            + "\n    </script>")


# --------------------------------------------------------------- entry pages

def build_entry_page(entry, newer, older):
    num = entry["number"]
    url = f"{SITE}/myth-{num}.html"
    title = f'MyTh {num} &middot; {entry["title"]} | Shoaib Jameel'
    desc = html.escape(strip_tags(entry["dek"])[:300], quote=True)
    card = f"{SITE}/assets/og/myth-{num}.png"
    body = rewrite_crossrefs(entry["body"])
    body = "\n".join(("            " + l) if l.strip() else l for l in body.split("\n"))

    tags = "".join(f'\n                        <span class="tag">{t}</span>'
                   for t in entry["tags"] + ([entry["readtime"]] if entry["readtime"] else []))

    def navlink(e, label, side):
        if not e:
            return ""
        return (f'                <a class="myth-prevnext {side}" href="myth-{e["number"]}.html">\n'
                f'                    <span class="myth-pn-label">{label}</span>\n'
                f'                    <span class="myth-pn-title">MyTh {e["number"]} &middot; {e["title"]}</span>\n'
                f'                </a>')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
{meta_tags(title, desc, url, article=entry, image=card)}
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="myth.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
{jsonld(entry, url, card)}
</head>
<body>
    <div class="liquid-bg"></div>
    <div class="scroll-progress"></div>

{NAV}
    <main class="container">

        <article class="myth-article reveal">
            <a class="myth-back" href="myth.html">&larr; All MyThs</a>

            <header class="myth-page-head">
                <span class="myth-page-no"><small>MYTH</small>{num}</span>
                <h1>{entry["title"]}</h1>
                <p class="myth-dek">{entry["dek"]}</p>
                <span class="myth-meta">
                    <span class="myth-date">{entry["date"]}</span>{tags}
                </span>
            </header>

            <div class="myth-body">
{body}
            </div>
        </article>

        <nav class="myth-pn-wrap reveal" aria-label="More MyThs">
{navlink(newer, "Newer", "next")}
{navlink(older, "Older", "prev")}
        </nav>

        <section class="reveal" style="margin: 3rem 0 4rem;">
            <div class="card" style="background: linear-gradient(135deg, rgba(99,102,241,.07), rgba(236,72,153,.05)); padding: 2.5rem 3rem;">
                <span class="section-title">Disagree?</span>
                <h2 style="font-size: 1.7rem; margin-bottom: 1.2rem;">If you have better data, that is the most useful thing you can send me.</h2>
                <div style="display:flex; gap:1rem; flex-wrap:wrap;">
                    <a href="mailto:{EMAIL}" class="tag" style="padding: 14px 28px; background:#6366f1; color:#fff; text-decoration:none;">Argue with me</a>
                    <a href="feed.xml" class="tag" style="padding: 14px 28px; background:rgba(255,255,255,0.05); color:#fff; text-decoration:none; border:1px solid var(--glass-border);">Subscribe by RSS</a>
                    <a href="myth.html" class="tag" style="padding: 14px 28px; background:rgba(255,255,255,0.05); color:#fff; text-decoration:none; border:1px solid var(--glass-border);">Every MyTh</a>
                </div>
            </div>
        </section>

    </main>

{FOOTER}
    <script src="reveal.js"></script>
    <script src="nav.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------- index page

def build_index(entries):
    url = f"{SITE}/myth.html"
    title = "MyTh &mdash; My Thoughts | Shoaib Jameel"
    desc = ("MyTh &mdash; My Thoughts. Numbered, dated essays by Shoaib Jameel on research, "
            "universities, technology and whatever else is worth an argument. Evidence-led, "
            "sourced, and occasionally political.")

    cards = []
    for e in entries:
        tags = "".join(f'\n                        <span class="tag">{t}</span>'
                       for t in e["tags"] + ([e["readtime"]] if e["readtime"] else []))
        cards.append(f"""        <a class="myth myth-card reveal" href="myth-{e['number']}.html" id="myth-{e['number']}">
            <span class="myth-no"><small>MYTH</small>{e['number']}</span>
            <span class="myth-head">
                <h3>{e['title']}</h3>
                <p class="myth-dek">{e['dek']}</p>
                <span class="myth-meta">
                    <span class="myth-date">{e['date']}</span>{tags}
                </span>
            </span>
            <span class="myth-chev" aria-hidden="true">&rarr;</span>
        </a>""")

    listing = "\n\n".join(cards)
    blog_ld = {
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "MyTh — My Thoughts",
        "url": url,
        "description": strip_tags(desc),
        "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/index.html"},
        "blogPost": [{"@type": "BlogPosting",
                      "headline": strip_tags(e["title"]),
                      "url": f"{SITE}/myth-{e['number']}.html",
                      "datePublished": e["iso"],
                      "description": strip_tags(e["dek"])} for e in entries],
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
{meta_tags(title, desc, url)}
    <link rel="stylesheet" href="style.css">
    <link rel="stylesheet" href="myth.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <script type="application/ld+json">
{json.dumps(blog_ld, indent=4, ensure_ascii=False)}
    </script>
</head>
<body>
    <div class="liquid-bg"></div>
    <div class="scroll-progress"></div>

{NAV}
    <main class="container">

        <section class="my-hero reveal">
            <span class="section-title">MyTh &middot; My Thoughts</span>
            <h1><span class="liquid-text my-mark">MyTh</span></h1>
            <p class="lead">Short for <strong style="color:#fff;">My Thoughts</strong>. Numbered, dated, and argued in public &mdash; research, universities, technology, policy, and anything else that will not leave me alone. Where I make a factual claim, I cite where it came from.</p>
        </section>

        <section class="my-about reveal" data-reveal-delay="80">
            <div>
                <h2>What this is</h2>
                <p>One thought per entry, numbered <strong style="color:#fff;">MyTh 001</strong> onwards and listed newest first. Each has its own page. Nothing is ever renumbered.</p>
            </div>
            <div>
                <h2>House rule</h2>
                <p>Every number, quote and claim carries a citation to a named source. If I am wrong, the source is right there for you to check.</p>
            </div>
            <div>
                <h2>Whose views</h2>
                <p>Mine alone, written in a personal capacity. Not the position of the University of Southampton or any body I sit on.</p>
            </div>
            <div>
                <h2>Corrections</h2>
                <p>Email me and I will correct the text and say what changed. Arguments welcome; I would rather be corrected than quoted approvingly.</p>
            </div>
        </section>

        <div class="my-bar reveal">
            <span class="my-count"><span class="counter" data-count="{len(entries)}">0</span> thoughts published</span>
            <a class="filter-pill" href="feed.xml">Subscribe by RSS</a>
        </div>

{listing}

        <section class="reveal" style="margin: 4rem 0;">
            <div class="card" style="background: linear-gradient(135deg, rgba(99,102,241,.07), rgba(236,72,153,.05)); padding: 2.5rem 3rem;">
                <span class="section-title">Next</span>
                <h2 style="font-size: 2rem; margin-bottom: 1.2rem;">MyTh {int(entries[0]['number']) + 1:03d} is being argued with itself.</h2>
                <p style="color: var(--text-muted); margin-bottom: 2rem; max-width: 64ch;">These arrive when a thought is finished rather than on a schedule. If you want to disagree with one &mdash; particularly if you have better data &mdash; that is the most useful thing you can send me.</p>
                <div style="display:flex; gap:1rem; flex-wrap:wrap;">
                    <a href="mailto:{EMAIL}" class="tag" style="padding: 14px 28px; background:#6366f1; color:#fff; text-decoration:none;">Argue with me</a>
                    <a href="feed.xml" class="tag" style="padding: 14px 28px; background:rgba(255,255,255,0.05); color:#fff; text-decoration:none; border:1px solid var(--glass-border);">Subscribe by RSS</a>
                    <a href="publications.html" class="tag" style="padding: 14px 28px; background:rgba(255,255,255,0.05); color:#fff; text-decoration:none; border:1px solid var(--glass-border);">The peer-reviewed version</a>
                </div>
            </div>
        </section>

    </main>

{FOOTER}
    <script src="reveal.js"></script>
    <script src="nav.js"></script>
    <script>
    /* Entries used to be <details> sections of this page, so links of the form
       myth.html#myth-003 exist in the wild. Send them to the entry's own page. */
    (function () {{
        'use strict';
        var m = /^#myth-(\\d+)$/.exec(window.location.hash);
        if (m) {{ window.location.replace('myth-' + m[1] + '.html'); }}
    }})();
    </script>
</body>
</html>
"""


# ---------------------------------------------------------------------- feed

def build_feed(entries):
    updated = max(e["iso"] for e in entries)
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom">',
           '  <title>MyTh — My Thoughts</title>',
           '  <subtitle>Numbered, dated essays by Shoaib Jameel on research, universities, '
           'technology — and whatever else is worth an argument.</subtitle>',
           f'  <link href="{SITE}/feed.xml" rel="self" type="application/atom+xml"/>',
           f'  <link href="{SITE}/myth.html" rel="alternate" type="text/html"/>',
           f'  <id>{SITE}/myth.html</id>',
           f'  <updated>{updated}</updated>',
           f'  <author><name>{AUTHOR}</name><email>{EMAIL}</email>'
           f'<uri>{SITE}/index.html</uri></author>',
           f'  <icon>{SITE}/favicon.svg</icon>',
           f'  <logo>{OG_IMAGE}</logo>',
           '  <rights>© 2026 Shoaib Jameel</rights>',
           '  <generator uri="https://bashthebuilder.github.io/">build_myth.py</generator>']

    for e in entries:
        url = f"{SITE}/myth-{e['number']}.html"
        # Relative links only resolve in a reader if they are made absolute.
        content = re.sub(r'(href|src)="(?!https?:|mailto:|#)([^"]+)"',
                         lambda m: f'{m.group(1)}="{SITE}/{m.group(2)}"',
                         rewrite_crossrefs(e["body"]))
        out += [
            '  <entry>',
            f'    <title>MyTh {e["number"]} · {strip_tags(e["title"])}</title>',
            f'    <link href="{url}" rel="alternate" type="text/html"/>',
            f'    <id>{url}</id>',
            f'    <published>{e["iso"]}</published>',
            f'    <updated>{e["iso"]}</updated>',
            f'    <summary type="text">{html.escape(strip_tags(e["dek"]))}</summary>',
        ]
        out += [f'    <category term="{html.escape(t)}"/>' for t in e["tags"]]
        out += [f'    <content type="html">{html.escape(content)}</content>',
                '  </entry>']
    out.append('</feed>')
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ sitemap

def update_sitemap(entries):
    path = os.path.join(ROOT, "sitemap.xml")
    src = open(path).read()
    # Drop any previously generated MyTh entry lines, then re-add them.
    src = re.sub(r'\s*<url><loc>[^<]*myth-\d+\.html</loc>[^\n]*</url>', "", src)
    lines = "".join(
        f'\n  <url><loc>{SITE}/myth-{e["number"]}.html</loc>'
        f'<lastmod>{e["iso"][:10]}</lastmod><priority>0.7</priority></url>'
        for e in entries)
    # Match the index line whatever priority it currently carries, so that
    # rebuilding is idempotent rather than silently dropping the entries.
    new, n = re.subn(r'<url><loc>' + re.escape(SITE) + r'/myth\.html</loc>'
                     r'<priority>[\d.]+</priority></url>',
                     f'<url><loc>{SITE}/myth.html</loc><priority>0.8</priority></url>{lines}',
                     src)
    if n != 1:
        sys.exit(f"error: expected 1 myth.html line in sitemap.xml, found {n}")
    open(path, "w").write(new)
    return len(entries)


def main():
    entries = load_entries()
    if not entries:
        sys.exit("error: no entries found in myth-content/")

    for i, e in enumerate(entries):
        newer = entries[i - 1] if i > 0 else None
        older = entries[i + 1] if i + 1 < len(entries) else None
        path = os.path.join(ROOT, f"myth-{e['number']}.html")
        open(path, "w").write(build_entry_page(e, newer, older))
        print(f"  myth-{e['number']}.html   {os.path.getsize(path):>7,} bytes   {strip_tags(e['title'])[:52]}")

    for name, text in (("myth.html", build_index(entries)), ("feed.xml", build_feed(entries))):
        open(os.path.join(ROOT, name), "w").write(text)
        print(f"  {name:<16} {os.path.getsize(os.path.join(ROOT, name)):>7,} bytes")

    try:
        import build_og
        print()
        build_og.main()
        print()
    except SystemExit as e:
        print(f"  (OG cards skipped: {e})")

    n = update_sitemap(entries)
    print(f"  sitemap.xml      {n} MyTh entries listed")
    print(f"\n{len(entries)} entries built at {datetime.now(timezone.utc).isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
