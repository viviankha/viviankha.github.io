#!/usr/bin/env python3
"""Stamp every local CSS/JS link with ?v=<content hash>.

Browsers cache these files for 10 minutes, so after an update a returning
visitor could get the new HTML with the old CSS. Changing the URL whenever
the file changes forces a fresh copy. Run this after editing any CSS or JS:

    python3 _tools/asset-versions.py

(Jekyll skips folders starting with "_", so this script is not published.)
"""
import glob
import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.viviankha.com/"
LINK = re.compile(r'((?:href|src)=")([^"?]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')


def version(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def stamp(page):
    def fix(m):
        url = m.group(2)
        if url.startswith(SITE):
            target = os.path.join(ROOT, url[len(SITE):])
        elif "://" in url:
            return m.group(0)  # someone else's file
        else:
            target = os.path.join(os.path.dirname(page), url)
        return "%s%s?v=%s%s" % (m.group(1), url, version(os.path.normpath(target)), m.group(3))

    with open(page) as f:
        old = f.read()
    new = LINK.sub(fix, old)
    if new != old:
        with open(page, "w") as f:
            f.write(new)
        print("updated", os.path.relpath(page, ROOT))


pages = [os.path.join(ROOT, p) for p in ("index.html", "404.html")]
pages += sorted(glob.glob(os.path.join(ROOT, "blog", "*", "index.html")))
for page in pages:
    stamp(page)
