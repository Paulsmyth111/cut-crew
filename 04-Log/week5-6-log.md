# Cut Crew — Log, weeks 5–6

## Wed 7 Oct — The job to be done
**The idea:** the job is what the customer is trying to get done, in their own words — not what the app *is*.
❌ "An AI clipping app."
✅ **"Find me the craziest bits of this video and tell me what to say at the start, so my clips get views without me watching the whole thing."**

## Commit + screenshot ✅
- All of Sprint 2 committed to GitHub (`Paulsmyth111/cut-crew`) and merged into `main` — pull request #1
- Screenshots of every screen in `05-Screenshots/` (home, new project, AI moments, clip list, ready to post, settings numbers, feedback form, Thai)
- From now on: Claude commits and screenshots after every change

## Tue 6 Oct — Phone home-screen app (PWA) ✅ (finished Wed 14 Oct)
- Cut Crew has its own website: **paulsmyth111.github.io/cut-crew** (GitHub Pages, from the `main` branch)
- Installed on my iPhone with **Add to Home Screen** — it opens full-screen with the teal scissors icon
- The AI moment finder only works in the Claude version; everything else works in the phone app

## Fri 9 Oct — Sprint 2 log entry (week 5)
**What I built:**
- Story 1 — Mark the moment: start/end times on every clip, length shown, warns over 60s
- Story 2 — Ready to post: hook, caption and hashtags per clip; "Copy post text" in one tap
- Story 3 — AI moment finder: paste a YouTube transcript → AI finds the shocking / intriguing moments, scores them out of 10, gives times, the exact quote and 3 hook options → one tap saves it as a clip
- Better empty screens, installable as a phone app (PWA), dead "coming soon" tiles now go somewhere real or are marked SOON

**Why:** my app is for clipping YouTube videos to get views, not editing. The thing that gets views is finding the "wait, what?" moment and a strong hook — so I built that, and swapped out "cut the dead air" (that's editing).

**Who tested it:** nobody yet — I fell behind on the user tests. Tested by me with a 10-step test script (10/10 passing).

**What changed:** the plan. I dropped "cut dead air" and "Part 1/2/3" and moved the AI moment finder up, because the AI finding the moments is the reason someone would use Cut Crew over watching the video themselves.

**Numbers:** 3 stories built · 10/10 test steps passing · 0 users tested (yet) · 7 known bugs, 3 fixed this week.

**Next week:** get 3 real clippers using it for a week, collect the feedback forms, fix what they hit.

**Where I'm stuck:**
- The app can't play YouTube or cut the actual video file inside Claude — that needs its own website and a server (week 10).
- Testers need a Claude account for the AI to work.

### Copy-paste Friday update for Luke
> Hi Luke — Sprint 2 update. Built all 3 stories: (1) mark where each clip starts/ends, (2) hook + caption + hashtags ready to post, (3) an AI moment finder — paste a YouTube transcript and the AI finds the most shocking moments, scores them and writes 3 hooks each. I changed the plan to focus on views not editing, so I dropped "cut dead air". Honest bit: I haven't done the user tests yet — that's my focus this week with 3 clippers. Stuck on: the app can't cut the real video inside Claude, that needs a server later. Test script 10/10 passing. — Paul

## Mon 12 Oct — Feedback form + send feedback button ✅
**5 questions in the app** (Settings → Send feedback, or the "Send feedback" bar on Home):
1. Did the AI find moments you'd actually post? (Yes / Some / No / Didn't try AI)
2. What was confusing or annoying?
3. How long did it take to get one clip ready to post?
4. What one thing would make you use Cut Crew every day?
5. How likely are you to use it again for real clipping? (1–5)

**Send feedback button:** one tap on Home opens an email to me (templevalleygeneticspauljr@gmail.com) with the subject **"Cut Crew feedback"** already filled in, so testers can moan easily. The 5-question form sends its answers to the same email. Proof: `05-Screenshots/2026-10-14-12-send-feedback-button.png` and `-13-feedback-form-email.png`.

## Tue 13 Oct — Readability + make it look like one thing ✅
**The basics:** strong contrast, one font, big buttons, no walls of text.
Applied:
- Grey labels and small text made lighter so they're readable on black (contrast)
- All text boxes 16px (stops iPhones zooming in when you tap them)
- Every button and text box at least 46px tall — easy to hit with a thumb
- Tile labels bigger (10.5px instead of 9.5px)
- Fixed words breaking in the middle ("quest-ions")
- Same rounded corners, same section labels, same button styles on every screen

## Wed 14 Oct — Count usage ✅ (the counter — real numbers come from testers)
Settings now shows **Your numbers**: videos imported, AI moments found, clips saved, clips from AI, hooks written, clips exported. Ask each tester to screenshot this on Friday — that's your usage number for Luke.

## Wed 14 Oct — Cannabis hour (needs you)
**Your part:** read one real TVG SOP (30 min). I can't open TVG's documents.
**App idea to write next to it (draft — check it against the SOP you read):**
> TVG makes long videos — grow walkthroughs, staff training, events. The same Cut Crew idea could clip them into short pieces for staff training or marketing: AI finds the useful moment ("how to check trichomes", "the drying step") and writes a title. Big catch: Thai rules on cannabis advertising are strict, so marketing clips would need a compliance check before posting — training clips for staff are the safer first use.
