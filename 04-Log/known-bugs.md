# Cut Crew — Known bugs

Last updated: Fri 6 Nov 2026

## Open

| # | Bug | How bad | Plan |
|---|-----|---------|------|
| 1 | Thai text has never been checked by a native speaker | Medium | Ask a Thai colleague to go through it |
| 2 | Link-to-clips server isn't live yet, so real YouTube links haven't been tested | High | Sign up for the AI key + Render, go live, test real links |
| 3 | YouTube can block downloads from servers | Medium | Cookies fix is in the server README; run on a laptop as backup |
| 4 | Speech-to-text (uploads with no captions) only runs once live | Medium | Test with an uploaded phone video once live |
| 5 | The AI in the server picks moments from what's said, not from the picture | Low | Add "AI watches the video" to the server like the in-app version |
| 6 | AI text stays in the first language after switching EN/TH | Low | Tap Redo for now |
| 7 | Learn, Community and some tool tiles not built (marked SOON) | Low | Parked |

## Fixed

| Bug | Fixed |
|-----|-------|
| Edge cases: empty box, word instead of link, very long link, messy paste, empty file, double tap, same link twice | Fri 6 Nov |
| App didn't open with no internet; jobs lost when signal dropped | Fri 6 Nov |
| Needed the video file saved on your phone (now: paste a link or upload) | Wed 4 Nov (server built) |
| Needed a transcript (AI can watch the video, server reads captions itself) | Wed 4 Nov |
| Clip was a thin strip with blur, not full screen | Wed 4 Nov |
| No captions on the clip | Wed 4 Nov |
| Clips saved as VP9 "MP4" that iPhone/TikTok often reject (now real H.264) | Tue 3 Nov |
| Clip making failed on phones that block playback without a fresh tap | Tue 3 Nov |
| AI moment finder only tested with a stand-in (now tested with the real AI) | Tue 3 Nov |
| Clip came out over 60 seconds | Oct |
| "Why this part?" looked like plain text | Oct |
| Clip length in English on the Thai screen | Oct |
| No real clip video: Export only saved text | Fri 16 Oct |
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
