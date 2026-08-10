#!/usr/bin/env python3
"""
Measure the tokenizer tax, and write the data behind tokenizer-tax.html.

Method
------
Article 1 of the Universal Declaration of Human Rights is used as the parallel
text: it is public domain, professionally translated, and says the same thing in
every language, so differences in token count are differences in encoding rather
than in content. Translations come from the Unicode UDHR in XML project.

Each translation is encoded with two OpenAI tokenizers via tiktoken:
cl100k_base (GPT-3.5/GPT-4) and o200k_base (GPT-4o and later). The multiplier
is that language's token count over English's, per tokenizer.

    python3 build_tokenizer_tax.py          # refetch, re-measure, rewrite JSON

Writes assets/tokenizer-tax.json. Requires tiktoken (pip3 install --user tiktoken)
and network access on first run; sources are cached in .cache/udhr/.
"""

import json
import os
import sys
import urllib.request
import xml.dom.minidom
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, ".cache", "udhr")
OUT = os.path.join(ROOT, "assets", "tokenizer-tax.json")
SRC = "https://raw.githubusercontent.com/eric-muller/udhr/master/data/udhr"

# (UDHR file code, display name, script). Chosen to span writing systems and to
# include every language MyTh 002 names in the text.
LANGS = [
    ("eng", "English", "Latin"),
    ("cym", "Welsh", "Latin"),
    ("spa", "Spanish", "Latin"),
    ("fra", "French", "Latin"),
    ("deu_1996", "German", "Latin"),
    ("swh", "Swahili", "Latin"),
    ("vie", "Vietnamese", "Latin"),
    ("zul", "Zulu", "Latin"),
    ("nhn", "Nahuatl (Central)", "Latin"),
    ("rus", "Russian", "Cyrillic"),
    ("arb", "Arabic", "Arabic"),
    ("amh", "Amharic", "Ethiopic"),
    ("hin", "Hindi", "Devanagari"),
    ("ben", "Bengali", "Bengali"),
    ("tel", "Telugu", "Telugu"),
    ("tha", "Thai", "Thai"),
    ("cmn_hans", "Chinese (Simplified)", "Han"),
    ("jpn", "Japanese", "Japanese"),
    ("kor", "Korean", "Hangul"),
]

RTL = {"arb"}


def fetch(code):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{code}.xml")
    if not os.path.exists(path):
        with urllib.request.urlopen(f"{SRC}/udhr_{code}.xml", timeout=30) as r:
            open(path, "wb").write(r.read())
    return path


def article_one(path):
    doc = xml.dom.minidom.parse(path)
    for art in doc.getElementsByTagName("article"):
        if art.getAttribute("number") == "1":
            return " ".join(p.firstChild.data.strip()
                            for p in art.getElementsByTagName("para") if p.firstChild)
    return None


def main():
    try:
        import tiktoken
    except ImportError:
        sys.exit("error: tiktoken is required — pip3 install --user tiktoken")

    encs = {"cl100k": tiktoken.get_encoding("cl100k_base"),
            "o200k": tiktoken.get_encoding("o200k_base")}

    rows = []
    for code, name, script in LANGS:
        text = article_one(fetch(code))
        if not text:
            print(f"  skipped {code}: no Article 1 in source")
            continue
        rows.append({
            "code": code.split("_")[0], "name": name, "script": script,
            "rtl": code in RTL, "text": text, "chars": len(text),
            "cl100k": len(encs["cl100k"].encode(text)),
            "o200k": len(encs["o200k"].encode(text)),
        })

    base = {k: next(r[k] for r in rows if r["code"] == "eng") for k in ("cl100k", "o200k")}
    for r in rows:
        for k in ("cl100k", "o200k"):
            r[f"x_{k}"] = round(r[k] / base[k], 2)
    rows.sort(key=lambda r: -r["cl100k"])

    data = {
        "generated": date.today().isoformat(),
        "passage": "Universal Declaration of Human Rights, Article 1",
        "source": "Unicode UDHR in XML (github.com/eric-muller/udhr)",
        "tokenizers": {
            "cl100k": {"label": "cl100k_base", "note": "GPT-3.5 and GPT-4"},
            "o200k": {"label": "o200k_base", "note": "GPT-4o and later"},
        },
        "baseline": base,
        "languages": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=1)

    print(f"  {'language':<22}{'chars':>7}{'cl100k':>8}{'x':>7}{'o200k':>8}{'x':>7}")
    for r in rows:
        print(f"  {r['name']:<22}{r['chars']:>7}{r['cl100k']:>8}"
              f"{r['x_cl100k']:>7}{r['o200k']:>8}{r['x_o200k']:>7}")
    print(f"\n  wrote {os.path.relpath(OUT, ROOT)} ({os.path.getsize(OUT):,} bytes), "
          f"{len(rows)} languages")


if __name__ == "__main__":
    main()
