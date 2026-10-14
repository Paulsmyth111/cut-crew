# Cut Crew — 10-step test script

Run this before every demo. Each step: do it, check the result. If a check fails, write it on known-bugs.md.

| # | Do this | It should… |
|---|---------|------------|
| 1 | Open Cut Crew fresh (no projects) | Show "No projects yet" with a 1-2-3 guide and a "Paste your first link" button |
| 2 | Paste a YouTube link and tap **Import** | Go straight into the project, with the video card and the AI moment finder showing |
| 3 | Tap **Find the moments** with an empty transcript box | Say the transcript looks too short — no crash |
| 4 | Paste a real transcript (with times) | Show "… characters · N timestamps found" |
| 5 | Tap **Find the moments** | Show "Reading the whole video…", then a list of moments, best score first, each with times, why, quote and hooks |
| 6 | Pick the 2nd hook on the top moment, tap **Save as clip** | Clip appears in the list with the right times; the moment says "Saved as a clip ✓" |
| 7 | Open that clip | Start/end, length and the hook you picked are already filled in |
| 8 | Add a caption and hashtags `podcast funny`, tap **Save changes**, then **Copy post text** | Hashtags become `#podcast #funny`; pasting shows hook + caption + hashtags |
| 9 | Tap **EN/ไทย**, then back | All screen text switches to Thai and back |
| 10 | Reload the app | Everything is still there: project, transcript, moments, clip, hook |

## Last run
**Wed 14 Oct 2026** — automated run in a test browser, with a stand-in AI answer for step 5 (the real AI only runs inside Claude).
Result: **10 / 10 passed**, no errors. Still to do by hand: step 5 with the real AI inside Claude.
