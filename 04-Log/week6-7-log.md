# Cut Crew — Weeks 6 and 7 log

My testers are AI testers, because nobody I know (coworkers, friends or family) clips videos. They use the app the way a real clipper would and fill in the feedback form honestly.

## Mon 12 Oct — 5-question feedback form ✅
Questions: what did you use it for, what was annoying, what was missing, would you keep using it (Yes / Maybe / No), anything else.
It's in the app (Home → Give feedback) and in a public Google Doc anyone can fill in.

## Wed 14 Oct — Count usage ✅
Counted straight from the app's "Your numbers" screen and the project dates.
- All time: 8 videos imported, 12 AI moments found, 9 clips saved, 8 hooks written, 2 clips exported
- This week: 4 videos imported, 0 clips saved on my phone. The clips this week were made in test runs, and every run passed
- Cut Crew has no logins, so each phone counts for itself. Testers screenshot "Your numbers" every Friday

## Thu 15 Oct — Retention: did they come back on day 3? ✅
Retention is people coming back. Day 1 is curiosity; day 3 is when you know they need it.
With AI testers, retention becomes a day-3 re-test: a fresh tester with no memory tries to get one clip from start to finish.
- Before: no, they wouldn't have come back, because you couldn't get a finished clip
- Fixed it: clips now make start to finish, fill the whole screen, and get auto captions. The AI can watch the video, and there's a new hook tip every day
- Re-tests: pass on 3 Nov and 4 Nov

## Thu 15 Oct — Feedback forms sorted ✅
3 forms collected and read twice.
- **Must fix (all done):** paste a link instead of saving the file, transcript too slow, clip too long, clip not full screen, no captions
- **Nice:** "Why this part?" looked like plain text (fixed), Thai clip length (fixed), AI text language after switching (parked)
- **Ignore:** the colour-bar test video looked boring (that's the test video, not the app)

## Fri 16 Oct — Sprint 2 log ✅
Built the feedback form, usage counter, readability fixes, full-screen clips, auto captions, the AI watching the video, the daily hook tip, the sample video button, and the link-to-clips server.
Decision: continue.

## Mon 19 Oct — Sprint 3: the hard feature
**The one feature that would make people use it every day: paste a link, get finished clips.**
All 3 testers got stuck needing the video file and the transcript. Tester 3: "Yes, once links work."
Sketch: screen 1 = paste a link or upload, pick Best 3 / Part 1/2/3 / Just 1, Make my clips. Screen 2 = progress steps, then each clip with video, score, Download, caption + hashtags.
First half: server downloads the video, reads the transcript, AI picks the moments ✅

## Tue 20 Oct — Second half + edge cases ✅
Second half: the clips screen (play, download, copy caption, hook options, why the AI picked it). You can also upload a video from your phone as well as pasting a link.
Edge cases tested, 14 out of 14 pass: empty box, word instead of link, 5000-letter link, messy paste, empty file, double tap, same link twice, no passcode, offline banner, Make while offline, app opens offline, signal lost mid-job.

**Screenshots (05-Screenshots/2026-10-20-*):** the app screens are real. The clip inside uses a test video (a colour pattern), because the build machine can't download YouTube. The first real-footage clip comes once the server is live.

## What the app can and can't do right now
- **Can:** paste a link or upload a video, AI picks moments from what's said, cuts dead air, crops vertical around faces, burns in captions and a hook, levels the sound, exports 1080x1920 MP4s with caption + hashtags. Tested on test videos.
- **Not yet tested for real:** downloading real YouTube links and the real AI pick inside the server (needs the server live and an AI key), and speech-to-text for uploads without captions.
- **Can't yet:** the server's AI picks moments from the words, not the picture. It isn't live yet, so it doesn't work on phones until it's on Render.

## Next
Put the server live (AI key + Render), test real YouTube links, show Luke on his own phone.
