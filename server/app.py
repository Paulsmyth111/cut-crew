"""Cut Crew server: paste a link, get finished clips.

Run locally:   uvicorn app:app --host 0.0.0.0 --port 8000
Environment:   ANTHROPIC_API_KEY (required), APP_PASSCODE (recommended),
               CUTCREW_MODEL, MAX_MINUTES, YTDLP_COOKIES_FILE, DATA_DIR
"""
from __future__ import annotations

import os
import secrets
import shutil
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

import pipeline as P

DATA = Path(os.environ.get("DATA_DIR", "/tmp/cutcrew-jobs"))
DATA.mkdir(parents=True, exist_ok=True)
PASSCODE = os.environ.get("APP_PASSCODE", "")
KEEP_HOURS = float(os.environ.get("KEEP_HOURS", "12"))
HERE = Path(__file__).parent

app = FastAPI(title="Cut Crew")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

JOBS: dict[str, dict] = {}
LOCK = threading.Lock()
POOL = ThreadPoolExecutor(max_workers=int(os.environ.get("WORKERS", "1")))


class JobIn(BaseModel):
    url: str
    mode: str = "best"      # best | series | single
    count: int = 3


def check(code: str | None):
    if PASSCODE and not secrets.compare_digest(code or "", PASSCODE):
        raise HTTPException(401, "Wrong passcode")


def update(jid: str, **kw):
    with LOCK:
        JOBS[jid].update(kw)


def cleanup():
    cutoff = time.time() - KEEP_HOURS * 3600
    with LOCK:
        old = [j for j, v in JOBS.items() if v["created"] < cutoff]
        for j in old:
            JOBS.pop(j, None)
    for j in old:
        shutil.rmtree(DATA / j, ignore_errors=True)


def work(jid: str, req: JobIn, upload: Path | None = None, title: str = ""):
    d = DATA / jid
    say = lambda m: update(jid, step=m)
    try:
        if upload:
            src = P.Source(upload, title or "your video", P.probe(upload)["duration"], None)
            if src.duration > P.MAX_MINUTES * 60:
                raise P.PipelineError(f"That video is longer than {P.MAX_MINUTES} minutes.")
        else:
            src = P.fetch(req.url.strip(), d / "src", progress=say)
        info = P.probe(src.video)
        update(jid, title=src.title, duration=round(src.duration))
        say("Reading the transcript")
        words = P.transcribe(src, progress=say)
        moments = P.find_moments(words, src.title, src.duration, req.mode, max(1, min(8, req.count)), progress=say)
        update(jid, total=len(moments))
        clips = []
        for i, m in enumerate(moments):
            say(f"Cutting clip {i + 1} of {len(moments)}")
            m.files = P.make_clip(src, info, words, m, i, d)
            c = asdict(m)
            c["start_label"], c["end_label"] = P.fmt_time(m.start), P.fmt_time(m.end)
            clips.append(c)
            update(jid, clips=list(clips))
        shutil.rmtree(d / "src", ignore_errors=True)   # keep the clips, drop the big source file
        update(jid, status="done", step="Done")
    except P.PipelineError as e:
        update(jid, status="error", error=str(e))
    except Exception:
        traceback.print_exc()
        update(jid, status="error", error="Something went wrong making the clips. Try again, or try another video.")


@app.post("/api/jobs")
def create_job(req: JobIn, x_passcode: str | None = Header(default=None)):
    check(x_passcode)
    url = req.url.strip()
    if not url:
        raise HTTPException(400, "Paste a video link")
    if len(url) > 2000:
        raise HTTPException(400, "That link is too long. Copy just the video link.")
    if not url.lower().startswith(("http://", "https://")) and not (url.startswith("file://") and os.environ.get("ALLOW_LOCAL_FILES") == "1"):
        raise HTTPException(400, "Paste the full link, starting with https://")
    req.url = url
    req.mode = req.mode if req.mode in ("best", "series", "single") else "best"
    req.count = max(1, min(8, req.count))
    cleanup()
    with LOCK:  # tapped twice, or pasted the same link again while it's still working: reuse that job
        for j in JOBS.values():
            if j["status"] == "working" and j["url"] == url and j["mode"] == req.mode:
                return {"id": j["id"], "existing": True}
    jid = secrets.token_urlsafe(8)
    with LOCK:
        JOBS[jid] = {"id": jid, "status": "working", "step": "Starting", "url": req.url, "mode": req.mode,
                     "clips": [], "total": None, "title": None, "error": None, "created": time.time()}
    POOL.submit(work, jid, req)
    return {"id": jid}


MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "2000"))
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".3gp"}


@app.post("/api/upload")
def upload_job(file: UploadFile = File(...), mode: str = Form("best"), count: int = Form(3),
               x_passcode: str | None = Header(default=None)):
    check(x_passcode)
    ext = Path(file.filename or "video.mp4").suffix.lower()
    if ext not in VIDEO_EXT and not (file.content_type or "").startswith("video/"):
        raise HTTPException(400, "That file isn't a video")
    cleanup()
    jid = secrets.token_urlsafe(8)
    dst = DATA / jid / "src" / ("video" + (ext if ext in VIDEO_EXT else ".mp4"))
    dst.parent.mkdir(parents=True, exist_ok=True)
    size = 0
    with open(dst, "wb") as f:
        while chunk := file.file.read(1 << 20):
            size += len(chunk)
            if size > MAX_UPLOAD_MB * 1024 * 1024:
                f.close()
                shutil.rmtree(DATA / jid, ignore_errors=True)
                raise HTTPException(413, f"That file is bigger than {MAX_UPLOAD_MB} MB")
            f.write(chunk)
    if size == 0:
        shutil.rmtree(DATA / jid, ignore_errors=True)
        raise HTTPException(400, "That file is empty")
    title = Path(file.filename or "your video").stem[:80]
    mode = mode if mode in ("best", "series", "single") else "best"
    req = JobIn(url="upload", mode=mode, count=max(1, min(8, count)))
    with LOCK:
        JOBS[jid] = {"id": jid, "status": "working", "step": "Reading the transcript", "url": "upload", "mode": mode,
                     "clips": [], "total": None, "title": title, "error": None, "created": time.time()}
    POOL.submit(work, jid, req, dst, title)
    return {"id": jid}


@app.get("/api/jobs/{jid}")
def get_job(jid: str, x_passcode: str | None = Header(default=None)):
    check(x_passcode)
    j = JOBS.get(jid)
    if not j:
        raise HTTPException(404, "That job has expired")
    return j


@app.get("/files/{jid}/{name}")
def get_file(jid: str, name: str, dl: int = 0):
    # File names are random job ids + fixed names, so they're not guessable.
    if "/" in name or ".." in name or jid not in JOBS:
        raise HTTPException(404)
    p = DATA / jid / name
    if not p.exists():
        raise HTTPException(404)
    title = (JOBS[jid].get("title") or "clip")[:40]
    fname = f"cut-crew-{''.join(c if c.isalnum() else '-' for c in title)}-{name}" if dl else None
    return FileResponse(p, filename=fname)


@app.get("/api/health")
def health():
    return {"ok": True, "ai": bool(os.environ.get("ANTHROPIC_API_KEY")), "passcode": bool(PASSCODE),
            "jobs": len(JOBS)}


@app.get("/", response_class=HTMLResponse)
def home():
    return (HERE / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/sw.js")
def service_worker():
    return FileResponse(HERE / "static" / "sw.js", media_type="text/javascript", headers={"Cache-Control": "no-cache"})


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(HERE / "static" / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/icon-{size}.png")
def icon(size: str):
    p = HERE / "static" / f"icon-{size}.png"
    if not p.exists():
        raise HTTPException(404)
    return FileResponse(p)
