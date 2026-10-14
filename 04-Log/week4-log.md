# Cut Crew — Sprint 1 log entry (week 4, 28 Sep – 2 Oct 2026)

**What I built**
- **Thai / English toggle** (top right). Every word in the app has Thai. No Thai colleague was in on Monday, so Claude drafted the Thai, and it still needs checking by a native speaker
- **The expected basics:** edit a video link and a clip's name/date, delete with "are you sure?", search/filter projects, today's date filled in automatically
- **Watch the video in the app:** I tried embedding the YouTube player. The hosting site blocks it, so it now shows the video thumbnail plus a "Copy video link" button
- **Backup and restore** (Settings): download everything as a file and load it back. Tested by wiping the app and restoring it
- **Polish:** a warning if the app can't save (e.g. private browsing), phone home-screen tags, and Export now downloads a real file with the clip's info
- **Design:** rebuilt the home screen to match my sketch: dark background, mint accent, "Every idea is a hook", big IMPORT box, tool tiles, recent projects, bottom nav with a raised + button

**Why**
Cut Crew is for clippers who post on TikTok, Reels and Shorts, and TVG apps need to be bilingual. Edit, delete, search and backup are what people expect from any real app. Without them nobody trusts it with their work.

**Who tested it**
Only me. I didn't get the first real user test done this week. That's the biggest thing I missed.

**What changed**
- The video player idea had to change: YouTube can't play inside the hosted app, so it shows a thumbnail and a copy-link button instead
- The app went from a plain list to the look of my mockup and hand sketch

**The numbers**
- 3 screens working (Home, Review clips, Clip detail) plus Settings
- Main job ("save a clip from a video"): 4 taps. Import link → open project → name clip → Save
- 0 users tested
- Every screen's words in Thai, 0 checked by a native speaker yet

**Next week (Sprint 2)**
Make it about getting views, not just saving links: mark where each clip starts and ends, write the hook, caption and hashtags, and get the AI to find the best moments for me. Then get real people using it.

**Where I'm stuck**
- YouTube won't play or open inside the app (blocked by the hosting site, not my code)
- I need a Thai speaker to check the translations
- I need to actually book user tests and stop putting them off

---

### Copy-paste Friday update for Luke
> Hi Luke, Sprint 1 update (week 4). Built: a Thai/English toggle (Thai still needs a native check), edit / delete-with-confirm / search / auto date, backup & restore, and redid the home screen to match my sketch. Tried putting a YouTube player in the app but the hosting site blocks it, so it shows the thumbnail + copy link instead. Honest bit: I didn't do the user test this week, only tested it myself. Main job is 4 taps. Next sprint: start/end times, hooks + captions, and AI finding the best moments, plus real users. Stuck on: the YouTube block and getting the Thai checked. Paul
