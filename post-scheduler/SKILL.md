---
name: post-scheduler
description: Turns finished posts into a content calendar and puts each one into your scheduler (Metricool, Buffer or any scheduler you have connected) as a draft at the right time for each platform, or into a calendar file you can bulk-upload. Never publishes. Use when the owner says "schedule these", "plan my week", "put this in Metricool", or "build my content calendar".
---

# Post scheduler

You own one outcome: every finished post has a slot, the right text for its platform and
its files attached, sitting as a draft the owner only has to approve.

## Before you start

1. Load the `brand-brain` skill: platforms, best times, time zone, scheduler.
2. Collect what is ready: files (slides, videos, covers), captions from `caption-writer`,
   and any dates the owner has already promised. Something without a finished caption is
   not ready; list it and move on.
3. Check the scheduler. If a scheduler connector or MCP server is connected, check it can
   **create a draft** (or a post marked as draft or "needs approval"). If it can only
   publish, do not use it: build the calendar file instead and say why.

## The job

1. **Plan the slots.** Use the brain's best times and time zone. One post per platform per
   slot. No two posts of the same format on the same platform on the same day. Leave gaps
   rather than cram. Never put two versions of the same piece on the same platform.
2. **Show the plan first.** A table: date, time, platform, post, format, caption's first
   line, files. Ask the owner to confirm or change it. Do not load anything into the
   scheduler until they say yes.
3. **Load the drafts.** For each row, create a draft in the scheduler with the platform's
   own caption, the files, and the time. Read each one back from the scheduler and check
   the time, the time zone, the platform and the caption match the plan, **and that its
   status is literally a draft (or "needs approval")**, not "scheduled" or "queued". If the
   scheduler has no draft state and a time alone would make it post automatically, do not
   load it: delete nothing, stop, and build the calendar file in step 4 instead. Never set a
   "publish now" or "auto-publish" option.
4. **No scheduler?** Write `content/calendar/YYYY-MM.csv` with the columns most schedulers
   import: date, time, platform, caption, media file path, link. Say which importer to use.

## What you hand back

The final table with each draft's ID or the CSV path, anything that was skipped and why, and
one line: `Drafts: <n>. Platforms: <list>. Nothing is live until you approve it.`

## Never

- Publish, post, send, or set a draft to go live on its own.
- Change or delete posts that were already in the scheduler.
- Load anything before the owner confirms the plan.
