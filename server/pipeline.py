"""Cut Crew link-to-clips pipeline.

URL -> download video + transcript -> AI picks the moments -> for each moment:
cut it, remove dead air, reframe to 9:16 around faces, burn in captions + hook,
clean up the audio -> finished 1080x1920 MP4 + thumbnail + caption + hashtags.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import statistics
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

OUT_W, OUT_H = 1080, 1920
MAX_MINUTES = int(os.environ.get("MAX_MINUTES", "180"))
MODEL = os.environ.get("CUTCREW_MODEL", "claude-sonnet-5-5")


class PipelineError(Exception):
    """An error with a message that is safe to show the user."""


# ---------------------------------------------------------------- helpers

def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def fmt_time(t: float) -> str:
    t = int(round(t))
    h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_time(s) -> float | None:
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s or "").strip()
    if not s:
        return None
    try:
        parts = [float(p) for p in s.split(":")]
    except ValueError:
        return None
    t = 0.0
    for p in parts:
        t = t * 60 + p
    return t


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    if r.returncode != 0:
        raise PipelineError("Couldn't read the video file.")
    info = json.loads(r.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if not v:
        raise PipelineError("That link has no video in it.")
    return {
        "w": int(v["width"]), "h": int(v["height"]),
        "duration": float(info["format"].get("duration") or 0),
        "has_audio": a is not None,
    }


# ---------------------------------------------------------------- 1. download

@dataclass
class Source:
    video: Path
    title: str
    duration: float
    subs: Path | None


def fetch(url: str, workdir: Path, progress=lambda m: None) -> Source:
    workdir.mkdir(parents=True, exist_ok=True)
    if url.startswith("file://"):
        # Local test mode only (never enabled on the public server).
        if os.environ.get("ALLOW_LOCAL_FILES") != "1":
            raise PipelineError("Paste a YouTube link.")
        src = Path(url[7:])
        dst = workdir / ("video" + src.suffix)
        shutil.copy(src, dst)
        vtt = src.with_suffix(".vtt")
        subs = None
        if vtt.exists():
            subs = workdir / "video.en.vtt"
            shutil.copy(vtt, subs)
        info = probe(dst)
        return Source(dst, src.stem, info["duration"], subs)

    import yt_dlp

    progress("Downloading the video")
    opts = {
        "outtmpl": str(workdir / "video.%(ext)s"),
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]/b",
        "merge_output_format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig", "en-US", "en-GB"],
        "subtitlesformat": "vtt",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "match_filter": yt_dlp.utils.match_filter_func(f"duration <= {MAX_MINUTES * 60}"),
    }
    cookies = os.environ.get("YTDLP_COOKIES_FILE")
    if cookies and Path(cookies).exists():
        opts["cookiefile"] = cookies
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
    except Exception as e:  # yt-dlp raises many types
        msg = str(e)
        if "not a bot" in msg or "Sign in to confirm" in msg:
            raise PipelineError("YouTube blocked the server from downloading. Add YouTube cookies (see the README).")
        if "does not pass filter" in msg:
            raise PipelineError(f"That video is longer than {MAX_MINUTES} minutes.")
        if "Unsupported URL" in msg or "is not a valid URL" in msg:
            raise PipelineError("That doesn't look like a video link.")
        raise PipelineError("Couldn't download that video. Check the link works and isn't private.")
    if not info:
        raise PipelineError(f"That video is longer than {MAX_MINUTES} minutes.")
    videos = sorted(workdir.glob("video.mp4")) or sorted(p for p in workdir.glob("video.*") if p.suffix in (".mp4", ".mkv", ".webm"))
    if not videos:
        raise PipelineError("Couldn't download that video.")
    subs = sorted(workdir.glob("video*.vtt"))
    sub = next((s for s in subs if ".en-orig." in s.name), None) or next((s for s in subs if ".en." in s.name), None) or (subs[0] if subs else None)
    return Source(videos[0], info.get("title") or "video", float(info.get("duration") or probe(videos[0])["duration"]), sub)


# ---------------------------------------------------------------- 2. transcript

@dataclass
class Word:
    t: float      # start, seconds
    e: float      # end, seconds
    w: str


_TS = r"(\d{1,2}:)?\d{2}:\d{2}\.\d{3}"


def _sec(ts: str) -> float:
    p = ts.split(":")
    if len(p) == 2:
        p = ["0"] + p
    return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])


def parse_vtt(text: str) -> list[Word]:
    """Words with timings from a WebVTT file.

    YouTube auto-captions repeat the previous line in every cue and mark the new
    words with inline <00:00:01.234> tags; we keep only the tagged (new) words.
    Manual captions have no tags; their words are spread evenly over the cue.
    """
    words: list[Word] = []
    blocks = re.split(r"\n\s*\n", text.replace("\r", ""))
    has_tags = "<c>" in text or re.search(r"<\d{2}:\d{2}", text) is not None
    last_plain = None
    for b in blocks:
        lines = b.strip().split("\n")
        tl = next((i for i, l in enumerate(lines) if "-->" in l), None)
        if tl is None:
            continue
        m = re.match(rf"\s*({_TS})\s*-->\s*({_TS})", lines[tl])
        if not m:
            continue
        a, z = _sec(m.group(1)), _sec(m.group(3))
        body = [l for l in lines[tl + 1:] if l.strip()]
        if has_tags:
            for l in body:
                if "<" not in l:
                    continue
                pieces = re.split(r"(<\d{1,2}:\d{2}(?::\d{2})?\.\d{3}>)", l)
                cur = a
                for p in pieces:
                    tm = re.fullmatch(r"<(\d{1,2}:\d{2}(?::\d{2})?\.\d{3})>", p)
                    if tm:
                        cur = _sec(tm.group(1))
                        continue
                    clean = re.sub(r"<[^>]+>", "", p).strip()
                    for w in clean.split():
                        words.append(Word(cur, cur, w))
        else:
            txt = " ".join(re.sub(r"<[^>]+>", "", l).strip() for l in body).strip()
            if not txt or txt == last_plain:
                continue
            last_plain = txt
            ws = txt.split()
            step = (z - a) / max(1, len(ws))
            for i, w in enumerate(ws):
                words.append(Word(a + i * step, a + (i + 1) * step, w))
    words.sort(key=lambda w: w.t)
    # end time = next word's start (capped), so captions never linger forever
    for i, w in enumerate(words):
        nxt = words[i + 1].t if i + 1 < len(words) else w.t + 0.6
        w.e = max(w.t + 0.12, min(nxt, w.t + 1.2)) if w.e <= w.t else w.e
    # drop music/applause tags like [Music]
    return [w for w in words if not re.fullmatch(r"\[.*\]", w.w)]


def transcribe(src: Source, progress=lambda m: None) -> list[Word]:
    if src.subs and src.subs.exists():
        words = parse_vtt(src.subs.read_text(encoding="utf-8", errors="ignore"))
        if len(words) > 20:
            return words
    # Fallback: speech-to-text on the server (optional, slower).
    try:
        from faster_whisper import WhisperModel  # type: ignore
    except ImportError:
        raise PipelineError("This video has no captions on YouTube, and speech-to-text isn't switched on for this server.")
    progress("Writing the transcript")
    model = WhisperModel(os.environ.get("WHISPER_MODEL", "base"), device="cpu", compute_type="int8")
    segs, _ = model.transcribe(str(src.video), word_timestamps=True, vad_filter=True)
    out = []
    for s in segs:
        for w in s.words or []:
            out.append(Word(float(w.start), float(w.end), w.word.strip()))
    if len(out) < 10:
        raise PipelineError("Couldn't hear enough speech in this video to find moments.")
    return out


def transcript_text(words: list[Word], every: float = 5.0) -> str:
    lines, cur, start = [], [], None
    for w in words:
        if start is None:
            start = w.t
        if w.t - start >= every and cur:
            lines.append(f"{fmt_time(start)} {' '.join(cur)}")
            cur, start = [], w.t
        cur.append(w.w)
    if cur:
        lines.append(f"{fmt_time(start)} {' '.join(cur)}")
    return "\n".join(lines)


# ---------------------------------------------------------------- 3. AI picks moments

@dataclass
class Moment:
    title: str
    start: float
    end: float
    score: int | None
    why: str
    quote: str
    hooks: list[dict]
    caption: str
    hashtags: list[str]
    part: int | None = None
    files: dict = field(default_factory=dict)


def _prompt(text: str, title: str, duration: float, mode: str, count: int) -> str:
    if mode == "series":
        want = ("Return 3 to 6 moments that work as a continuing story, in the order they happen, not overlapping. "
                "The LAST part must contain the payoff. Every part except the last ends on a cliffhanger. "
                'Titles start "Part 1: ", "Part 2: " and so on.')
    elif mode == "single":
        want = "Return exactly 1 moment: the single best one in the whole video."
    else:
        want = f"Return the {count} best moments, best first. They must not overlap."
    return "\n".join([
        "You are the editor inside Cut Crew, an app that turns long videos into short vertical clips (TikTok, Reels, Shorts).",
        f'Video: "{title}" ({fmt_time(duration)} long). Below is its transcript with timestamps.',
        "Find the moments most likely to make someone stop scrolling and watch to the end: shock, surprise, a confession or juicy line "
        "buried in ordinary chat, conflict, a big reveal, something genuinely funny, an emotional beat, a hot take, a 'wait, what?' moment. "
        "Loud is not the same as good: a calm, unexpected line often beats shouting.",
        want,
        "Rules:",
        "- Each clip 15 to 60 seconds. Start right before the interesting bit (no slow intro); end just after the payoff, "
        "or on a cliffhanger when it's a Part that continues.",
        "- Only use times inside the transcript. Never invent a time.",
        '- "quote": words copied exactly from the transcript, max 25 words. Never make up quotes or change what happened.',
        "- 4 hook options per moment, each a different style (question, curiosity, crazy moment, emotion, wait for it), max 10 words, "
        "teasing the payoff without giving it away. Never lie or put words in anyone's mouth.",
        '- "score" 1-10: how likely viewers watch to the end.',
        '- "caption": a short curiosity post caption (max 15 words) that does not explain the whole clip.',
        '- "hashtags": 5 to 8 relevant hashtags, no #fyp spam.',
        "Reply with only a JSON array, for example:",
        '[{"title":"He beats the pro on the last shot","start":"12:04","end":"12:41","score":9,"why":"one sentence",'
        '"quote":"exact words","hooks":[{"style":"question","text":"Can he really beat a pro?"},{"style":"curiosity","text":"Watch the last shot"},'
        '{"style":"crazy moment","text":"Nobody expected this shot"},{"style":"emotion","text":"The crowd went silent"}],'
        '"caption":"He had one shot left","hashtags":["#football","#challenge"]}]',
        "",
        "TRANSCRIPT:",
        text,
    ])


def _parse_json(text: str):
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1)
    a, b = text.find("["), text.rfind("]")
    if a == -1 or b == -1:
        raise PipelineError("The AI's answer didn't come through properly. Try again.")
    return json.loads(text[a:b + 1])


def find_moments(words: list[Word], title: str, duration: float, mode: str = "best", count: int = 3,
                 progress=lambda m: None) -> list[Moment]:
    progress("AI is finding the best moments")
    text = transcript_text(words)[:180_000]
    prompt = _prompt(text, title, duration, mode, count)
    if os.environ.get("CUTCREW_TEST_AI") == "1":
        raw = _test_ai(words)          # local tests only, never on the live server
    else:
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise PipelineError("The server has no AI key set (ANTHROPIC_API_KEY).")
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        try:
            msg = client.messages.create(model=MODEL, max_tokens=4000, messages=[{"role": "user", "content": prompt}])
        except anthropic.APIError as e:
            raise PipelineError(f"The AI couldn't answer right now ({getattr(e, 'status_code', 'error')}). Try again in a minute.")
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    data = _parse_json(raw)
    out: list[Moment] = []
    for d in data if isinstance(data, list) else []:
        s, e = parse_time(d.get("start")), parse_time(d.get("end"))
        if s is None or e is None or e <= s:
            continue
        s = max(0.0, s)
        e = min(e, duration or e, s + 60)
        if e - s < 5:
            continue
        hooks = [h if isinstance(h, dict) else {"style": "", "text": str(h)} for h in (d.get("hooks") or [])]
        hooks = [{"style": str(h.get("style", "")), "text": str(h.get("text", "")).strip()} for h in hooks if str(h.get("text", "")).strip()][:5]
        tags = [t if str(t).startswith("#") else f"#{t}" for t in (d.get("hashtags") or [])][:10]
        sc = d.get("score")
        try:
            sc = max(1, min(10, int(round(float(sc)))))
        except (TypeError, ValueError):
            sc = None
        out.append(Moment(str(d.get("title") or "Clip")[:140], s, e, sc, str(d.get("why") or "")[:400],
                          str(d.get("quote") or "")[:300], hooks, str(d.get("caption") or "")[:200], tags))
    if mode == "series":
        out.sort(key=lambda m: m.start)
        for i in range(1, len(out)):
            if out[i].start < out[i - 1].end:
                out[i - 1].end = out[i].start
        out = [m for m in out if m.end - m.start >= 5]
        for i, m in enumerate(out):
            m.part = i + 1
    else:
        out.sort(key=lambda m: -(m.score or 0))
        out = out[: (1 if mode == "single" else count)]
    if not out:
        raise PipelineError("The AI couldn't find clear moments in this video.")
    return out


def _test_ai(words: list[Word]) -> str:
    """Stand-in answer for offline tests: picks a slice of the real transcript."""
    total = words[-1].t if words else 60
    s = min(10.0, total / 4)
    e = min(s + 30, total)
    q = " ".join(w.w for w in words if s <= w.t <= s + 6)[:120]
    return json.dumps([{"title": "Test moment", "start": fmt_time(s), "end": fmt_time(e), "score": 7, "why": "test",
                        "quote": q, "hooks": [{"style": "question", "text": "Wait for what happens next"}],
                        "caption": "Test caption", "hashtags": ["#test", "#cutcrew"]}])


# ---------------------------------------------------------------- 4. make the clip

def silences(video: Path, s: float, e: float, min_len: float = 0.7, noise: str = "-35dB") -> list[tuple[float, float]]:
    r = run(["ffmpeg", "-hide_banner", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", str(video), "-vn",
             "-af", f"silencedetect=noise={noise}:d={min_len}", "-f", "null", "-"])
    out, start = [], None
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", line)
        if m:
            start = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and start is not None:
            out.append((start, float(m.group(1))))
            start = None
    if start is not None:
        out.append((start, e - s))
    return out


def keep_parts(length: float, sil: list[tuple[float, float]], pad: float = 0.22) -> list[tuple[float, float]]:
    """Clip-relative time ranges to keep after removing dead air (leaves a short natural pause)."""
    parts, cur = [], 0.0
    for a, b in sil:
        a2, b2 = a + pad, b - pad
        if b2 - a2 < 0.3:
            continue
        if a2 > cur:
            parts.append((cur, a2))
        cur = b2
    if cur < length:
        parts.append((cur, length))
    parts = [(a, b) for a, b in parts if b - a > 0.15]
    return parts or [(0.0, length)]


def face_center(video: Path, s: float, e: float, info: dict) -> float:
    """Horizontal centre (0..1) of the faces in this part of the video, for the vertical crop."""
    try:
        import cv2
    except ImportError:
        return 0.5
    try:
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    except Exception:
        return 0.5
    if cascade.empty():
        return 0.5
    cap = cv2.VideoCapture(str(video))
    xs, n = [], max(4, min(24, int(e - s)))
    for i in range(n):
        t = s + (i + 0.5) * (e - s) / n
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        small = cv2.resize(frame, (640, int(640 * frame.shape[0] / frame.shape[1])))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=6, minSize=(40, 40))
        if len(faces):
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])  # biggest face = main speaker
            xs.append((x + w / 2) / small.shape[1])
    cap.release()
    return statistics.median(xs) if xs else 0.5


def _ass_escape(t: str) -> str:
    return t.replace("\\", "").replace("{", "(").replace("}", ")").replace("\n", " ")


def _ass_time(t: float) -> str:
    t = max(0.0, t)
    h, m = int(t // 3600), int(t % 3600 // 60)
    s = t - h * 3600 - m * 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(words: list[Word], hook: str, part: int | None, length: float, path: Path) -> None:
    """Captions: 3 words at a time, big and bold, each word lights up mint as it's said.
    Hook: top of the screen for the first 4 seconds. Part label: whole clip."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {OUT_W}
PlayResY: {OUT_H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,86,&H00BCE35F,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,2,2,60,60,560,1
Style: Hook,DejaVu Sans,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&HC0000000,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,230,1
Style: Part,DejaVu Sans,46,&H00062018,&H00062018,&H00BCE35F,&H00BCE35F,-1,0,0,0,100,100,0,0,3,12,0,7,60,60,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    if hook:
        ev.append(f"Dialogue: 1,{_ass_time(0)},{_ass_time(min(4.0, length))},Hook,,0,0,0,,{_ass_escape(hook.upper())}")
    if part:
        ev.append(f"Dialogue: 2,{_ass_time(0)},{_ass_time(length)},Part,,0,0,0,,PART {part}")
    chunk: list[Word] = []

    def flush():
        if not chunk:
            return
        a, z = chunk[0].t, max(chunk[-1].e, chunk[-1].t + 0.25)
        txt = ""
        for i, w in enumerate(chunk):
            nxt = chunk[i + 1].t if i + 1 < len(chunk) else z
            k = max(1, int(round((nxt - w.t) * 100)))
            txt += f"{{\\kf{k}}}{_ass_escape(w.w.upper())} "
        ev.append(f"Dialogue: 0,{_ass_time(a)},{_ass_time(min(z, length))},Cap,,0,0,0,,{txt.strip()}")
        chunk.clear()

    for w in words:
        if chunk and (len(chunk) >= 3 or w.t - chunk[-1].e > 0.6 or re.search(r"[.!?]$", chunk[-1].w)):
            flush()
        chunk.append(w)
    flush()
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def remap_words(words: list[Word], s: float, parts: list[tuple[float, float]]) -> list[Word]:
    out, offset = [], 0.0
    for a, b in parts:
        for w in words:
            rel = w.t - s
            if a <= rel < b:
                out.append(Word(offset + rel - a, offset + min(w.e - s, b) - a, w.w))
        offset += b - a
    return out


def make_clip(src: Source, info: dict, words: list[Word], m: Moment, idx: int, outdir: Path,
              hook_index: int = 0, progress=lambda msg: None) -> dict:
    s, e = m.start, m.end
    length = e - s
    # 1) dead air
    parts = keep_parts(length, silences(src.video, s, e)) if info["has_audio"] else [(0.0, length)]
    new_len = sum(b - a for a, b in parts)
    # 2) reframe
    W, H = info["w"], info["h"]
    if W / H > OUT_W / OUT_H:
        cw, ch = int(H * OUT_W / OUT_H) // 2 * 2, H
        cx = face_center(src.video, s, e, info)
        x = int(min(max(cx * W - cw / 2, 0), W - cw))
        crop = f"crop={cw}:{ch}:{x}:0"
    else:
        cw, ch = W, int(W * OUT_H / OUT_W) // 2 * 2
        crop = f"crop={cw}:{min(ch, H)}:0:{max(0, (H - ch) // 2)}"
    # 3) captions + hook
    hook = m.hooks[hook_index]["text"] if m.hooks and hook_index < len(m.hooks) else ""
    clip_words = [w for w in words if s - 0.2 <= w.t < e]
    ass = outdir / f"clip{idx}.ass"
    build_ass(remap_words(clip_words, s, parts), hook, m.part, new_len, ass)
    # 4) render
    fc, vlabels = [], []
    for i, (a, b) in enumerate(parts):
        fc.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        if info["has_audio"]:
            fc.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
            vlabels.append(f"[v{i}][a{i}]")
        else:
            vlabels.append(f"[v{i}]")
    n = len(parts)
    if info["has_audio"]:
        fc.append(f"{''.join(vlabels)}concat=n={n}:v=1:a=1[vc][ac]")
        fc.append("[ac]highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=11[ao]")
    else:
        fc.append(f"{''.join(vlabels)}concat=n={n}:v=1:a=0[vc]")
    fc.append(f"[vc]{crop},scale={OUT_W}:{OUT_H}:flags=lanczos,setsar=1,ass={ass.name}[vo]")
    out = outdir / f"clip{idx}.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{s:.3f}", "-to", f"{e:.3f}", "-i", str(src.video.resolve()),
           "-filter_complex", ";".join(fc), "-map", "[vo]"]
    if info["has_audio"]:
        cmd += ["-map", "[ao]", "-c:a", "aac", "-b:a", "160k", "-ar", "48000"]
    cmd += ["-c:v", "libx264", "-preset", os.environ.get("X264_PRESET", "veryfast"), "-crf", "20", "-pix_fmt", "yuv420p",
            "-r", "30", "-movflags", "+faststart", out.name]
    r = run(cmd, cwd=outdir)
    if r.returncode != 0 or not out.exists():
        raise PipelineError(f"Couldn't cut clip {idx + 1}. ({r.stderr.strip()[-200:]})")
    thumb = outdir / f"clip{idx}.jpg"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "1.0", "-i", out.name, "-frames:v", "1", "-q:v", "3", thumb.name], cwd=outdir)
    return {"video": out.name, "thumb": thumb.name if thumb.exists() else None,
            "length": round(new_len, 1), "cut_seconds": round(length - new_len, 1)}
