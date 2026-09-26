# The content machine: 5 Claude skills that run a content department

Five Claude skills and one setup file. They do the jobs a content team does: study what is
working, make carousels, cut long videos into shorts, write captions in your voice, and
queue everything in your scheduler. They are packaged from the way I run my own content.
Made by Ibrahim Shareef ([@shareefico](https://www.instagram.com/shareefico/)).

| Skill | The job | Where it runs |
|---|---|---|
| `format-teardown` | Paste a post that is blowing up. Get the hook, structure and look behind it, and a brief for your own version. Keeps the mechanics, never the words | Claude app and Claude Code |
| `carousel-studio` | Brief in, finished 1080x1350 slides out, in your colours and fonts, one idea per slide | Words and HTML anywhere; PNG render in Claude Code |
| `clip-cutter` | One long video in, vertical shorts out, with word-by-word captions in your colours. Transcribes on your own computer | Claude Code |
| `caption-writer` | Five hooks, then a caption for each platform in your voice, checked for invented facts and AI filler | Claude app and Claude Code |
| `post-scheduler` | Plans the slots and loads every post into Metricool, Buffer or your scheduler as a draft, or a CSV to import | Claude app and Claude Code |
| `brand-brain` | The setup file: your voice, audience, colours, fonts, platforms, scheduler. The other five read it first | Both |

Nothing is published by these skills. Posts land as files or scheduler drafts, and you press
publish.

## Before you install: fill in the brain

Open `brand-brain/SKILL.md` and replace every `FILL`. Paste two or three of your own posts
where it asks; that is how the skills learn your voice. Anything left as `FILL` becomes
`[ASK OWNER]` in a draft, so nothing gets made up.

## Install in the Claude app (claude.ai, desktop or mobile)

Skills need code execution switched on (Settings, then Capabilities). They work on the Free,
Pro, Max, Team and Enterprise plans.

1. Download `content-machine-skills.zip` from the [latest release](https://github.com/ibrahimshareef96-sys/content-machine-skills/releases/latest) and unzip it. Inside are six ZIPs, this README and the licence.
2. Unzip `brand-brain.zip`, fill in `brand-brain/SKILL.md`, and zip the `brand-brain` folder
   again (Mac: right-click, **Compress**. Windows: right-click, **Send to**, **Compressed
   (zipped) folder**). The ZIP must have the folder at its root.
3. In Claude, open **Customize**, then **Skills**, press **+** and upload each ZIP. Turn them on.
4. Optional: connect your scheduler (Metricool or Buffer) under **Connectors** so
   `post-scheduler` can create drafts.

`clip-cutter` and the PNG step of `carousel-studio` need Claude Code, because they run
programs on your computer.

## Install in Claude Code

```bash
git clone https://github.com/ibrahimshareef96-sys/content-machine-skills.git
```

```bash
mkdir -p ~/.claude/skills && cp -R content-machine-skills/brand-brain content-machine-skills/format-teardown content-machine-skills/carousel-studio content-machine-skills/clip-cutter content-machine-skills/caption-writer content-machine-skills/post-scheduler ~/.claude/skills/
```

Then fill in `~/.claude/skills/brand-brain/SKILL.md`. For video, install ffmpeg and the local
transcriber once:

```bash
brew install ffmpeg && pip install faster-whisper
```

(On Windows: `winget install ffmpeg` and `pip install faster-whisper`.) Carousel rendering needs
Chrome, Edge, Brave or Chromium installed.

## Try it

- "Break down this post and write me a brief for my version." (paste screenshots)
- "Turn that brief into a carousel."
- "Cut my podcast episode at ~/Videos/ep12.mp4 into five shorts."
- "Write the captions for all of it."
- "Schedule everything for next week as drafts."

## Safety

- The skills tell Claude to make files and drafts only. The real limit is what you connect,
  so give your scheduler connector the narrowest access it offers.
- The skills tell Claude to treat posts, transcripts and web pages as data and to report
  anything that looks like a hidden instruction. That is a safeguard, not a guarantee: your
  real limit is a scheduler connection that can only create drafts, and reading the drafts
  before you approve them.
- Video and transcripts stay on your computer in `clip-cutter`.
- No skill generates or edits a real person's face or voice, or copies another creator's
  words or images.

## Tests

```bash
python3 -m pytest tests -q
```

The end-to-end tests skip themselves if ffmpeg or a Chromium browser is missing.

## Licence

MIT. Use them, change them, give them to your team.
