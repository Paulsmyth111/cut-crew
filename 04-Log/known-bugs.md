# Cut Crew — Known bugs

Last updated: Fri 16 Oct 2026

## Open

| # | Bug | How bad | Plan |
|---|-----|---------|------|
| 1 | Thai text has never been checked by a native speaker | Medium | Ask a Thai colleague to go through it |
| 2 | "Add to Home Screen" not tested on a real phone from the claude.ai link (may save with the Claude icon) | Medium | Try it on my phone; full install needs its own website (week 10) |
| 3 | AI moment finder only tested with a stand-in answer, not the real AI | High | Run it once for real inside Claude on a podcast transcript |
| 4 | YouTube video can't play inside the app; thumbnail may not load on some devices | Medium | Can't fix inside Claude. Video card + "Copy video link" as backup |
| 5 | Getting the transcript from YouTube is an extra manual step | Medium | Watch if testers manage it alone; auto-fetch needs a server |
| 6 | The AI reads words only — a crazy moment with no talking can be missed | Medium | Needs video AI on a server, later |
| 7 | Testers need a Claude account for the AI | Medium | Tell testers up front (tester-kit.md) |
| 8 | Video files have to be added again after closing the app (too big to keep) | Low | Keep it simple for now |
| 9 | Upload File, 7 tool tiles, Learn and Community not built (marked SOON) | Low | Parked |

## Fixed

| Bug | Fixed |
|-----|-------|
| No real clip video: Export only saved text. Now "Make clip video" cuts a vertical MP4 with the hook on it (needs the video file) | Fri 16 Oct |
| Hard to get the transcript ("...more" not found) | Fri 16 Oct (picture guide) |
| Words breaking mid-word in small text | Wed 14 Oct |
| Low-contrast grey text, small buttons, iPhone zoom on text boxes | Wed 14 Oct |
| "Coming soon" dead ends on the main tiles and Fetch Caption | Wed 14 Oct |
| Long timestamps crowding the clip card | Wed 14 Oct |
| Thumbnail showed as an empty black box | Fri 9 Oct |
| Settings, backup and restore messages had no Thai | Mon 5 Oct |
| Settings boxes had no styling | Mon 5 Oct |
| Empty screens were one grey line with no next step | Mon 5 Oct |
| Backup/Export downloads silently failed on the hosted page | Sun 4 Oct |
| YouTube embed showed a blocked error | Sun 4 Oct |
