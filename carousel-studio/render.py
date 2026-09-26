#!/usr/bin/env python3
"""Render every <div class="slide"> in a carousel HTML file to slide-1.png, slide-2.png, ...

Uses a Chromium-based browser in headless mode (Chrome, Edge, Brave or Chromium) and the
Python standard library only. Each slide is 1080x1350 unless --width/--height say otherwise.

    python3 render.py path/to/carousel.html
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
# Slides never need the network except for Google Fonts; block every other host.
BLOCK_NETWORK = "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE fonts.googleapis.com, EXCLUDE fonts.gstatic.com"
PATH_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"]


def find_browser() -> str:
    env = os.environ.get("CHROME_PATH")
    if env and pathlib.Path(env).exists():
        return env
    for c in CANDIDATES:
        if pathlib.Path(c).exists():
            return c
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    sys.exit("No Chrome, Edge, Brave or Chromium found. Install one, or set CHROME_PATH.")


def count_slides(html: str) -> int:
    without_comments = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    return len(re.findall(r"""<div\s[^>]*class\s*=\s*["'](?:[^"']*\s)?slide(?:\s[^"']*)?["']""", without_comments))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=pathlib.Path)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    ap.add_argument("--out", type=pathlib.Path, help="output folder (default: next to the HTML)")
    args = ap.parse_args()

    src = args.html.resolve()
    if not src.is_file():
        sys.exit(f"Not a file: {src}")
    html = src.read_text(encoding="utf-8")
    n = count_slides(html)
    if n == 0:
        sys.exit('No <div class="slide"> found in the HTML.')
    if "URLSearchParams" not in html:
        sys.exit("The HTML is missing the ?slide= script at the bottom of template.html; copy it in first.")

    out = (args.out or src.parent).resolve()
    out.mkdir(parents=True, exist_ok=True)
    browser = find_browser()

    for i in range(n):
        png = out / f"slide-{i + 1}.png"
        url = f"{src.as_uri()}?slide={i}"
        cmd = [browser, "--headless=new", "--disable-gpu", "--hide-scrollbars", BLOCK_NETWORK,
               "--force-device-scale-factor=1", "--virtual-time-budget=5000",
               f"--window-size={args.width},{args.height}", f"--screenshot={png}", url]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            sys.exit(f"Rendering slide {i + 1} took over 2 minutes. Check the HTML for a slow or missing image.")
        if result.returncode != 0 or not png.exists():
            sys.exit(f"Render failed on slide {i + 1}: {result.stderr.strip()[:400]}")
        print(f"slide {i + 1}/{n} -> {png}")
    print(f"done: {n} slides in {out}")


if __name__ == "__main__":
    main()
