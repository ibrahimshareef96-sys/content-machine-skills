"""Unit tests for the helper scripts. Run: python3 -m pytest tests -q"""
import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


short = load("clip-cutter/make_short.py")
render = load("carousel-studio/render.py")
transcribe = load("clip-cutter/transcribe.py")


def test_hex_to_ass_reverses_to_bgr():
    assert short.hex_to_ass("#D7FD64") == "&H0064FDD7"
    assert short.hex_to_ass("ffffff") == "&H00FFFFFF"


@pytest.mark.parametrize("bad", ["#FFF", "#GGGGGG", "", "#1234567"])
def test_hex_to_ass_rejects_bad_colours(bad):
    with pytest.raises(ValueError):
        short.hex_to_ass(bad)


def test_ass_time_formats_and_clamps():
    assert short.ass_time(0) == "0:00:00.00"
    assert short.ass_time(61.234) == "0:01:01.23"
    assert short.ass_time(3725.5) == "1:02:05.50"
    assert short.ass_time(-3) == "0:00:00.00"


def test_ass_escape_neutralises_override_braces():
    assert short.ass_escape("a{\\b1}b") == "a(\\\\b1)b"


def test_words_in_range_keeps_a_word_that_straddles_the_start():
    words = [short.Word(9.95, 10.30, "straddle"), short.Word(9.0, 9.9, "before")]
    got = short.words_in_range(words, 10.0, 12.0)
    assert [w.text for w in got] == ["straddle"]
    assert got[0].start == 0.0


def test_words_in_range_retimes_and_filters():
    words = [short.Word(1.0, 1.5, "a"), short.Word(10.0, 10.4, "b"), short.Word(10.5, 11.0, "c"), short.Word(20, 21, "d")]
    got = short.words_in_range(words, 10.0, 11.0)
    assert [w.text for w in got] == ["b", "c"]
    assert got[0].start == 0.0


def test_build_ass_highlights_one_word_per_event():
    words = [short.Word(0.0, 0.3, "one"), short.Word(0.3, 0.6, "two"), short.Word(0.6, 0.9, "three"), short.Word(0.9, 1.2, "four")]
    ass = short.build_ass(words, "Arial", "#FFFFFF", "#D7FD64", per_line=3)
    events = [line for line in ass.splitlines() if line.startswith("Dialogue:")]
    assert len(events) == 4
    assert all(e.count("&H0064FDD7") == 1 for e in events)
    assert "PlayResX: 1080" in ass and "PlayResY: 1920" in ass


def test_build_ass_with_no_words_has_no_events():
    assert "Dialogue:" not in short.build_ass([], "Arial", "#FFFFFF", "#D7FD64")


def test_count_slides_ignores_comments_and_other_classes():
    html = ('<!-- <div class="slide"> --><div class="slide">a</div><div class="slide cover">b</div>'
            '<div class="slides">c</div><div id="x" class=\'frame slide\'>d</div><div class="slideshow">e</div>')
    assert render.count_slides(html) == 3


def test_fmt_clock():
    assert transcribe.fmt_clock(65) == "01:05"
    assert transcribe.fmt_clock(3725) == "1:02:05"
