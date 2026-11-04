# Cut Crew server: paste a link, get clips

Paste a YouTube link on your phone or laptop and get back finished vertical clips.

What happens to every video:

1. **Download.** Gets the video and YouTube's captions.
2. **Transcript.** Reads every word with its exact timing.
3. **AI picks the moments.** Looks for shock, surprise, confessions, conflict, big reveals, funny bits and "wait, what?" moments, then scores each one 1–10.
4. **Cuts each clip.** Starts right on the moment and ends after the payoff, or on a cliffhanger for Part 1/2/3.
5. **Removes dead air.** Silences longer than 0.7 seconds are cut down to a short natural pause.
6. **Reframes to 9:16.** Finds the speaker's face and centres the crop on it.
7. **Captions.** Big bold captions, 3 words at a time, each word lighting up as it's said.
8. **Hook.** The AI's hook goes at the top for the first 4 seconds. It gives 4 hook options per clip.
9. **Audio.** Levelled to TikTok loudness, with low rumble cleaned up.
10. **Export.** 1080×1920 MP4 plus a thumbnail, a curiosity caption and 5–8 hashtags.

Only clip videos you have the right to use: your own, or creators who allow clipping.

---

## Go live (about 15 minutes)

### 1. Get an AI key
1. Go to **console.anthropic.com** and sign up.
2. Add some credit. $5 is plenty to start; one 20-minute video costs a few cents.
3. Open **API keys**, then **Create key**, and copy it. It starts with `sk-ant-`.

### 2. Put the server on Render
1. Go to **render.com** and sign up with your GitHub account.
2. Click **New**, then **Blueprint**, and pick the **cut-crew** repo. Render reads `render.yaml` and sets everything up.
3. When it asks for settings:
   - `ANTHROPIC_API_KEY`: paste the key from step 1.
   - `APP_PASSCODE`: make up a passcode. Without it, anyone with the link could spend your AI credit.
4. Click **Apply**. The first build takes about 5 minutes.
5. Open the link Render gives you (for example `https://cut-crew.onrender.com`). On your iPhone, tap **Share**, then **Add to Home Screen**.

The **Starter** plan costs $7 a month and is always on. The **Free** plan also works, but it sleeps when nobody's using it, so the first video after a break takes about a minute longer to start.

### 3. If YouTube blocks the server
YouTube sometimes blocks downloads coming from servers. If you see "YouTube blocked the server":
1. On your laptop, install the **Get cookies.txt LOCALLY** browser extension, open youtube.com while signed in, and export `cookies.txt`.
2. In Render, go to your service, then **Environment**, then **Secret Files**, and add a file named `cookies.txt` with what you exported.
3. Add a setting: `YTDLP_COOKIES_FILE` = `/etc/secrets/cookies.txt`.

## Or run it on your own laptop
Downloads from a home connection get blocked much less often.

```
cd server
pip install -r requirements.txt     # also needs ffmpeg installed
export ANTHROPIC_API_KEY=sk-ant-...
export APP_PASSCODE=pick-one
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`. From your phone on the same Wi-Fi, open `http://<your-laptop's-IP>:8000`.

## Settings

| Setting | What it does | Default |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | AI key (required) | none |
| `APP_PASSCODE` | Passcode needed to make clips | none |
| `CUTCREW_MODEL` | Which Claude model picks the moments | `claude-sonnet-5-5` |
| `MAX_MINUTES` | Longest video allowed | 180 |
| `YTDLP_COOKIES_FILE` | YouTube cookies, if downloads get blocked | none |
| `KEEP_HOURS` | How long finished clips stay on the server | 12 |
| `WORKERS` | Videos processed at the same time | 1 |

## Tested
Run end to end on a test video with pauses and YouTube-style captions. It produced a 1080×1920 H.264/AAC clip, cut 4.1 seconds of dead air exactly where the pauses were, and showed word-by-word captions, the hook and the Part label. The phone page was tested too: progress, playback, download, copy caption.

Two things can only be tested once the server is live, because YouTube is blocked from the build machine: downloading a real YouTube link, and the AI picking moments with a real key.
