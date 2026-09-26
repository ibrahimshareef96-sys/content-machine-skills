---
name: carousel-studio
description: Builds a finished Instagram or LinkedIn carousel in your brand from a brief, a topic or a format-teardown, as one HTML file with one slide per page, then renders every slide to a 1080x1350 PNG ready to post. Calm layouts (one headline, at most three short lines per slide), your colours and fonts, optional AI-made scenes with no people and no text in them. Use when the owner says "make a carousel", "turn this into slides", or after format-teardown writes a brief.
---

# Carousel studio

You own one outcome: a set of slide images the owner can post today, that look like their
brand and say one thing per slide.

## Before you start

1. Load the `brand-brain` skill: colours, fonts, handle, call to action, voice.
2. Get the brief. Best is a `format-teardown` brief. Otherwise ask for the topic, the
   number of slides (default 7: a cover, five points, a closer) and the one thing the
   reader should take away.
3. Know where you are running:
   - **Claude Code:** you can write files and run `render.py` in this skill's folder.
   - **Claude app:** build the HTML as a file or artifact; tell the owner to run the render
     step on their computer, or to screenshot each slide at 1080x1350.

## The job

1. **Write the slides as words first.** For each slide: one headline (under 10 words), at
   most three short lines, and at most one small label or chip. The cover is the hook. The
   last slide is the call to action from the brain. Every fact, number and result comes
   from the brain or the brief; anything else is `[ASK OWNER]`. Show the owner the words
   before you design if there is any `[ASK OWNER]` left.
2. **Build the HTML.** Copy `template.html` from this skill's folder into the working folder
   (default `content/carousels/<topic>/index.html`). Put the brain's colours and fonts into
   the `:root` tokens. One `<div class="slide">` per slide. Keep the script at the bottom;
   the renderer needs it. Accent colour on one word or one shape per slide, never more.
   Never add any other `<script>`, and no remote file except a Google Fonts link; the
   renderer blocks everything else anyway.
3. **Pictures (optional).** If the owner has an image generator connected, generate one
   scene per slide: same character or object across all slides, a plain empty top half for
   the text, **no people's faces, no text, no logos in the image**. Use the first image as
   the reference for the rest so they match. The owner's own photos are used as they are,
   never edited. Save them in `assets/` and reference them with
   `<img class="scene" src="assets/...">`.
4. **Render** (Claude Code): `python3 <this skill's folder>/render.py content/carousels/<topic>/index.html`.
   It needs Chrome, Edge, Brave or Chromium installed and nothing else.
5. **Check every PNG yourself** (open them): no text over a face or the main subject, no text
   cut off, nothing smaller than 24 px, the accent used once per slide, the page count right.
   Fix the HTML and render again until all pass.

## What you hand back

The PNG paths in order, the HTML path, and a line per slide with its headline. Then suggest
`caption-writer` for the caption.

## Never

- Put more than one idea on a slide or more than three lines under a headline.
- Generate or edit a real person's face, or copy another creator's images or characters.
- Invent a number, result or quote to fill a slide.
