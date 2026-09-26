"""End-to-end runs of the three scripts. Skipped when Chrome or ffmpeg is missing.
Run: python3 -m pytest tests -q"""
import json
import shutil
import subprocess
import sys
import types

import pytest

from test_scripts import ROOT, render, short, transcribe

HAS_FFMPEG = shutil.which("ffmpeg") is not None


def has_browser() -> bool:
    try:
        render.find_browser()
        return True
    except SystemExit:
        return False


def run_main(module, argv, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", *argv])
    module.main()


@pytest.mark.skipif(not has_browser(), reason="no Chromium-based browser")
def test_render_template_makes_one_png_per_slide(tmp_path, monkeypatch):
    html = tmp_path / "my carousel.html"
    shutil.copy(ROOT / "carousel-studio" / "template.html", html)
    run_main(render, [str(html), "--out", str(tmp_path / "out")], monkeypatch)
    pngs = sorted((tmp_path / "out").glob("slide-*.png"))
    assert [p.name for p in pngs] == ["slide-1.png", "slide-2.png", "slide-3.png"]
    assert pngs[0].read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_refuses_html_without_the_slide_script(tmp_path, monkeypatch):
    html = tmp_path / "x.html"
    html.write_text('<div class="slide">a</div>', encoding="utf-8")
    with pytest.raises(SystemExit):
        run_main(render, [str(html)], monkeypatch)


def test_render_refuses_missing_file(tmp_path, monkeypatch):
    with pytest.raises(SystemExit):
        run_main(render, [str(tmp_path / "nope.html")], monkeypatch)


@pytest.fixture
def clip_inputs(tmp_path):
    video = tmp_path / "in put.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc=size=1920x1080:rate=30:duration=6",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=6", "-shortest", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", str(video)], check=True)
    words = [{"start": 1.0 + i * 0.4, "end": 1.35 + i * 0.4, "text": t} for i, t in enumerate("this is a {tricky} test clip".split())]
    transcript = tmp_path / "transcript.json"
    transcript.write_text(json.dumps({"language": "en", "duration": 6, "words": words}), encoding="utf-8")
    return video, transcript


@pytest.mark.skipif(not HAS_FFMPEG, reason="no ffmpeg")
def test_make_short_outputs_vertical_video_with_audio(tmp_path, monkeypatch, clip_inputs):
    video, transcript = clip_inputs
    out = tmp_path / "out dir" / "short.mp4"
    run_main(short, [str(video), "--start", "0.5", "--end", "4", "--transcript", str(transcript), "--out", str(out)], monkeypatch)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height", "-of", "json", str(out)],
                           capture_output=True, text=True, check=True)
    streams = json.loads(probe.stdout)["streams"]
    video_stream = next(s for s in streams if s["codec_type"] == "video")
    assert (video_stream["width"], video_stream["height"]) == (1080, 1920)
    assert any(s["codec_type"] == "audio" for s in streams)


@pytest.mark.parametrize("args", [
    ["--start", "5", "--end", "2"],
    ["--start", "0", "--end", "500"],
    ["--start", "0", "--end", "3", "--x", "2"],
])
@pytest.mark.skipif(not HAS_FFMPEG, reason="no ffmpeg")
def test_make_short_rejects_bad_ranges(tmp_path, monkeypatch, clip_inputs, args):
    video, transcript = clip_inputs
    with pytest.raises(SystemExit):
        run_main(short, [str(video), *args, "--transcript", str(transcript), "--out", str(tmp_path / "o.mp4")], monkeypatch)


def test_transcribe_writes_json_and_txt_with_a_stub_model(tmp_path, monkeypatch):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"not really a video")

    class FakeWord:
        def __init__(self, start, end, word):
            self.start, self.end, self.word = start, end, word

    class FakeSegment:
        start, text = 3.0, " Hello there. "
        words = [FakeWord(3.0, 3.4, " Hello"), FakeWord(3.4, 3.9, " there."), FakeWord(3.9, 4.0, " ")]

    class FakeModel:
        def __init__(self, *a, **k):
            pass

        def transcribe(self, *a, **k):
            return iter([FakeSegment()]), types.SimpleNamespace(language="en", duration=4.0)

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    run_main(transcribe, [str(video), "--out", str(tmp_path / "t")], monkeypatch)
    data = json.loads((tmp_path / "t" / "transcript.json").read_text(encoding="utf-8"))
    assert [w["text"] for w in data["words"]] == ["Hello", "there."]
    assert (tmp_path / "t" / "transcript.txt").read_text(encoding="utf-8").startswith("[00:03] Hello there.")


def test_transcribe_refuses_missing_file(tmp_path, monkeypatch):
    with pytest.raises(SystemExit):
        run_main(transcribe, [str(tmp_path / "nope.mp4"), "--out", str(tmp_path)], monkeypatch)


def test_make_short_refuses_missing_ffmpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(short.shutil, "which", lambda name: None)
    with pytest.raises(SystemExit, match="ffmpeg"):
        run_main(short, [str(tmp_path / "v.mp4"), "--start", "0", "--end", "1", "--transcript", "t.json", "--out", "o.mp4"], monkeypatch)


@pytest.mark.skipif(not HAS_FFMPEG, reason="no ffmpeg")
def test_make_short_refuses_missing_video(tmp_path, monkeypatch):
    with pytest.raises(SystemExit, match="Not a file"):
        run_main(short, [str(tmp_path / "nope.mp4"), "--start", "0", "--end", "1", "--transcript", "t.json", "--out", "o.mp4"], monkeypatch)


@pytest.mark.skipif(not HAS_FFMPEG, reason="no ffmpeg")
def test_make_short_refuses_a_font_that_could_break_the_subtitle_file(tmp_path, monkeypatch, clip_inputs):
    video, transcript = clip_inputs
    with pytest.raises(SystemExit, match="font"):
        run_main(short, [str(video), "--start", "0", "--end", "2", "--transcript", str(transcript),
                         "--out", str(tmp_path / "o.mp4"), "--font", "Arial,1\nDialogue"], monkeypatch)


def test_find_browser_prefers_chrome_path(tmp_path, monkeypatch):
    fake = tmp_path / "chrome"
    fake.write_text("", encoding="utf-8")
    monkeypatch.setenv("CHROME_PATH", str(fake))
    assert render.find_browser() == str(fake)


def test_find_browser_exits_when_nothing_is_installed(monkeypatch):
    monkeypatch.delenv("CHROME_PATH", raising=False)
    monkeypatch.setattr(render, "CANDIDATES", [])
    monkeypatch.setattr(render.shutil, "which", lambda name: None)
    with pytest.raises(SystemExit):
        render.find_browser()
