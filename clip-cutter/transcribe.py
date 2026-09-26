#!/usr/bin/env python3
"""Transcribe a video with word-level timestamps, locally, with faster-whisper.

Writes <out>/transcript.json (every word with start and end seconds) and
<out>/transcript.txt (one line per sentence, "[mm:ss] text") for picking clips.

    python3 transcribe.py talk.mp4 --out content/clips/talk
Needs: pip install faster-whisper   (runs on the CPU; nothing leaves the computer)
"""
import argparse
import json
import pathlib
import sys


def fmt_clock(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, required=True, help="folder for transcript.json and transcript.txt")
    ap.add_argument("--model", default="small", choices=["tiny", "base", "small", "medium", "large-v3"])
    ap.add_argument("--language", default=None, help="language code such as en or ar; default: detect")
    args = ap.parse_args()

    if not args.video.is_file():
        sys.exit(f"Not a file: {args.video}")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed. Run: pip install faster-whisper")

    args.out.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(args.video), language=args.language, word_timestamps=True, vad_filter=True)

    words, lines = [], []
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if text:
                words.append({"start": round(w.start, 3), "end": round(w.end, 3), "text": text})
        lines.append(f"[{fmt_clock(seg.start)}] {seg.text.strip()}")
        print(lines[-1], flush=True)

    (args.out / "transcript.json").write_text(
        json.dumps({"language": info.language, "duration": info.duration, "words": words}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    (args.out / "transcript.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"done: {len(words)} words, language {info.language}, saved in {args.out}")


if __name__ == "__main__":
    main()
