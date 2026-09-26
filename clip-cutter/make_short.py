#!/usr/bin/env python3
"""Cut one vertical short (1080x1920) from a longer video, with burned-in word captions.

    python3 make_short.py talk.mp4 --start 125.4 --end 171.0 \
        --transcript content/clips/talk/transcript.json --out content/clips/talk/short-1.mp4

Captions come from transcript.json (made by transcribe.py): 3 words at a time, the spoken
word in the accent colour. Crop is centred; move it with --x (0 = left edge, 1 = right edge).
Needs ffmpeg built with libass (the Homebrew and most Linux builds are).
"""
import argparse
import json
import re
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import NamedTuple

WIDTH, HEIGHT = 1080, 1920


class Word(NamedTuple):
    start: float
    end: float
    text: str


def hex_to_ass(hex_colour: str) -> str:
    """#RRGGBB -> &H00BBGGRR (ASS colour order, fully opaque)."""
    h = hex_colour.lstrip("#")
    if len(h) != 6 or any(c not in "0123456789abcdefABCDEF" for c in h):
        raise ValueError(f"Not a #RRGGBB colour: {hex_colour}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    cs = int(round(seconds * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def words_in_range(words: list[Word], start: float, end: float) -> list[Word]:
    """Words heard inside [start, end], re-timed so the clip starts at 0.

    A word is kept when most of it plays inside the clip, so a cut a fraction of a second
    off a word boundary does not leave a spoken word without a caption."""
    kept = []
    for w in words:
        mid = (w.start + w.end) / 2
        if start <= mid <= end:
            kept.append(Word(max(0.0, w.start - start), min(w.end, end) - start, w.text))
    return kept


def group(words: list[Word], size: int) -> list[list[Word]]:
    return [words[i:i + size] for i in range(0, len(words), size)]


def build_ass(words: list[Word], font: str, text_hex: str, accent_hex: str, per_line: int = 3) -> str:
    text_c, accent_c = hex_to_ass(text_hex), hex_to_ass(accent_hex)
    header = (
        "[Script Info]\nScriptType: v4.00+\n"
        f"PlayResX: {WIDTH}\nPlayResY: {HEIGHT}\nWrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        f"Style: Cap,{font},84,{text_c},{text_c},&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,3,2,80,80,360,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events = []
    for chunk in group(words, per_line):
        for i, w in enumerate(chunk):
            nxt = chunk[i + 1].start if i + 1 < len(chunk) else w.end
            parts = [
                f"{{\\c{accent_c}}}{ass_escape(x.text)}{{\\c{text_c}}}" if j == i else ass_escape(x.text)
                for j, x in enumerate(chunk)
            ]
            events.append(f"Dialogue: 0,{ass_time(w.start)},{ass_time(max(nxt, w.start + 0.05))},Cap,,0,0,0,,{' '.join(parts)}")
    return header + "\n".join(events) + "\n"


def load_words(path: pathlib.Path) -> list[Word]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Word(float(w["start"]), float(w["end"]), str(w["text"])) for w in data["words"]]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=pathlib.Path)
    ap.add_argument("--start", type=float, required=True, help="seconds")
    ap.add_argument("--end", type=float, required=True, help="seconds")
    ap.add_argument("--transcript", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--x", type=float, default=0.5, help="horizontal crop centre, 0 to 1 (default 0.5)")
    ap.add_argument("--font", default="Arial", help="an installed font name")
    ap.add_argument("--text-colour", default="#FFFFFF")
    ap.add_argument("--accent-colour", default="#D7FD64")
    args = ap.parse_args()

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg is not installed.")
    if not args.video.is_file():
        sys.exit(f"Not a file: {args.video}")
    if not 0 <= args.start < args.end:
        sys.exit("--start must be 0 or more and before --end.")
    if args.end - args.start > 180:
        sys.exit("A short is at most 180 seconds.")
    if not 0 <= args.x <= 1:
        sys.exit("--x must be between 0 and 1.")
    if not re.fullmatch(r"[A-Za-z0-9 _-]{1,64}", args.font):
        sys.exit("--font may only contain letters, numbers, spaces, - and _.")

    words = words_in_range(load_words(args.transcript), args.start, args.end)
    ass = build_ass(words, args.font, args.text_colour, args.accent_colour)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        sub = pathlib.Path(tmp) / "captions.ass"
        sub.write_text(ass, encoding="utf-8")
        crop = (f"scale=-2:{HEIGHT},crop='min(iw,{WIDTH})':{HEIGHT}:'(iw-min(iw,{WIDTH}))*{args.x}':0,"
                f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:0,setsar=1")
        vf = f"{crop},ass=filename=captions.ass"  # relative name: no drive letters or colons in the filter
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-ss", f"{args.start:.3f}", "-i", str(args.video.resolve()), "-t", f"{args.end - args.start:.3f}",
               "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(args.out.resolve())]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=tmp, timeout=1800)
        except subprocess.TimeoutExpired:
            sys.exit("ffmpeg took longer than 30 minutes and was stopped.")
        if result.returncode != 0:
            sys.exit(f"ffmpeg failed: {result.stderr.strip()[:600]}")
    print(f"done: {args.out} ({args.end - args.start:.1f}s, {len(words)} caption words)")


if __name__ == "__main__":
    main()
