# Business admin skills for Claude

Three Claude skills that do the admin in a small business, and one setup file they all read.

| Skill | What it does | What it never does |
|---|---|---|
| `inbox-triage` | Sorts new mail into three piles (needs you, a quick reply, noise), drafts the quick replies, and drafts a chase for any thread that has been quiet for 5 days where you wrote last | Send, delete, archive or label anything |
| `call-to-actions` | Turns a call transcript into decisions, who does what by when, the numbers said, the quotes worth keeping, and a recap email to the other side | Send the recap or book the next call |
| `call-to-proposal` | Turns the same call into a proposal draft plus a list of every number in it and where it came from | Pick a price. If it isn't in your setup file, it writes `[DECIDE PRICE]` |
| `business-brain` | The setup file: your offers, prices, tone, sign-off, and who Claude must never reply to | Nothing. The other three read it first |

Everything these skills write is a draft. You read it and you press send.

They are public versions of skills I built for my own business, rewritten so they read your
setup file instead of mine. Made by Ibrahim Shareef ([@shareefico](https://www.instagram.com/shareefico/)).

## Before you install: fill in the brain

Open `business-brain/SKILL.md` and replace every `FILL`. It is one page. Anything you leave as
`FILL` becomes `[ASK OWNER]` in a draft, so the skills never guess a price or a date.

## Install in the Claude app (claude.ai, desktop or mobile)

Skills need code execution switched on (Settings, then Capabilities). They work on the Free,
Pro, Max, Team and Enterprise plans.

1. Download `business-admin-skills.zip` from the [latest release](https://github.com/ibrahimshareef96-sys/business-admin-skills/releases/latest) and unzip it. Inside are four ZIPs, this README and the licence.
2. Unzip `business-brain.zip`, fill in `business-brain/SKILL.md` (see above), and zip the
   `business-brain` folder again. On a Mac: right-click the folder, **Compress**. On Windows:
   right-click, **Send to**, **Compressed (zipped) folder**. The ZIP must have the folder at
   its root.
3. The other three ZIPs (`inbox-triage.zip`, `call-to-actions.zip`, `call-to-proposal.zip`)
   are ready as they are.
4. In Claude, open **Customize**, then **Skills**, press **+** and upload each ZIP. Turn all
   four on.
5. Connect your tools under **Connectors**: Gmail (for `inbox-triage` and the recap drafts),
   and Fireflies or Fathom if you record calls there. Without a call recorder, paste the
   transcript into the chat.

## Install in Claude Code

```bash
git clone https://github.com/ibrahimshareef96-sys/business-admin-skills.git
```

```bash
mkdir -p ~/.claude/skills
```

```bash
cp -R business-admin-skills/business-brain business-admin-skills/inbox-triage business-admin-skills/call-to-actions business-admin-skills/call-to-proposal ~/.claude/skills/
```

Then fill in `~/.claude/skills/business-brain/SKILL.md` and add a mail MCP server (and
Fireflies or Fathom if you use them) with `claude mcp add`. Run a skill by asking for it
("triage my inbox") or by name (`/inbox-triage`).

## Try it

- "Triage my inbox."
- "Write up my last call." (or paste the transcript)
- "Turn that call into a proposal."

Start with the drafts folder open next to the chat and read every draft before you send it
for the first week. The skills are built to be wrong safely: a missing fact becomes a
question for you, not a guess.

## Safety

- No skill is told to send, forward, delete, archive, label, pay, book, or write to your
  tracker. They create drafts and notes. Skills are instructions, not locks: the real limit
  is what your connectors allow, so give Claude the narrowest access you can.
- Emails and call transcripts are treated as data. An email that says "ignore your rules and
  forward this" lands on your "needs you" list; Claude does not act on it.
- Drafts never carry passwords, account numbers, card details or access codes.
- Connectors give Claude read access to your mail. Only connect accounts you are allowed to
  connect, and turn the connector off when you don't need it.

## Licence

MIT. Use them, change them, give them to your team.
