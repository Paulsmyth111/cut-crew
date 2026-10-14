# Cut Crew

**Turn long YouTube videos into clips that get views.**
Paste a video, and the AI finds the shocking, intriguing "wait, what?" moments — with times, a score and hook options — ready to post on TikTok, Reels and Shorts.

Built by Paul as part of Paul's Path (Luke's 15-week app-building program).

## What it does now
- **AI moment finder** — paste a YouTube transcript, the AI finds the best moments and writes 3 hooks each
- **Mark the moment** — save where each clip starts and ends
- **Ready to post** — hook, caption and hashtags per clip, copied in one tap
- Thai / English, backup & restore, feedback form, usage numbers, installs as a phone app (PWA)

## Files
- `index.html` — the whole app
- `manifest.webmanifest`, `sw.js`, `icon-*.png` — make it installable on a phone
- `04-Log/` — sprint plans, weekly log, test script, known bugs, tester kit
- `05-Screenshots/` — a screenshot of the app for each step

## Known limits
The AI moment finder only runs when the app is opened inside Claude. Cutting the actual video file needs a server (planned later). See `04-Log/known-bugs.md`.
