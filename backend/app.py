import glob
import os
import shutil
import tempfile
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.version import __version__ as YTDLP_VERSION
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

app = Flask(__name__)

# Set ALLOWED_ORIGIN to your Netlify URL (e.g. https://my-site.netlify.app) to lock it down.
CORS(app, origins=os.environ.get("ALLOWED_ORIGIN", "*"), expose_headers=["Content-Disposition"])

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be"}
HAS_FFMPEG = shutil.which("ffmpeg") is not None

# Optional: paste the contents of a cookies.txt into the COOKIES_TXT env var
# to get past "confirm you're not a bot" errors on cloud servers.
COOKIE_FILE = None
if os.environ.get("COOKIES_TXT"):
    COOKIE_FILE = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
    with open(COOKIE_FILE, "w") as f:
        f.write(os.environ["COOKIES_TXT"])

FORMATS = {
    "best": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b",
    "1080": "bv*[height<=1080]+ba/b[height<=1080]",
    "720": "bv*[height<=720]+ba/b[height<=720]",
    "480": "bv*[height<=480]+ba/b[height<=480]",
    "360": "bv*[height<=360]+ba/b[height<=360]",
    "mp3": "bestaudio/best",
}


def valid_url(url):
    try:
        return urlparse(url).hostname in ALLOWED_HOSTS
    except Exception:
        return False


@app.get("/")
def health():
    return jsonify(ok=True, ffmpeg=HAS_FFMPEG, deno=shutil.which("deno") is not None, yt_dlp=YTDLP_VERSION)


@app.get("/info")
def info():
    url = request.args.get("url", "").strip()
    if not valid_url(url):
        return jsonify(error="Please provide a valid YouTube URL."), 400
    try:
        info_opts = {"quiet": True, "noplaylist": True, "skip_download": True}
        if COOKIE_FILE:
            info_opts["cookiefile"] = COOKIE_FILE
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            d = ydl.extract_info(url, download=False)
        return jsonify(
            title=d.get("title"),
            thumbnail=d.get("thumbnail"),
            duration=d.get("duration"),
            uploader=d.get("uploader"),
        )
    except Exception as e:
        return jsonify(error=str(e).replace("ERROR: ", "")[:300]), 400


@app.get("/download")
def download():
    url = request.args.get("url", "").strip()
    quality = request.args.get("quality", "best")
    if not valid_url(url):
        return jsonify(error="Please provide a valid YouTube URL."), 400
    if quality not in FORMATS:
        quality = "best"
    if quality == "mp3" and not HAS_FFMPEG:
        return jsonify(error="MP3 needs ffmpeg on the server."), 400

    tmp = tempfile.mkdtemp(prefix="yt_")
    fmt = FORMATS[quality]
    if not HAS_FFMPEG and quality != "mp3":
        fmt = "b[ext=mp4]/b"

    opts = {
        "format": fmt,
        "outtmpl": os.path.join(tmp, "%(title).120B.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "windowsfilenames": True,
    }
    if COOKIE_FILE:
        opts["cookiefile"] = COOKIE_FILE
    if quality == "mp3":
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
    elif HAS_FFMPEG:
        opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        files = [f for f in glob.glob(os.path.join(tmp, "*")) if os.path.isfile(f)]
        if not files:
            raise RuntimeError("No file was produced.")
        path = max(files, key=os.path.getsize)
        resp = send_file(path, as_attachment=True, download_name=os.path.basename(path))
        resp.call_on_close(lambda: shutil.rmtree(tmp, ignore_errors=True))
        return resp
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        return jsonify(error=str(e).replace("ERROR: ", "")[:300]), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
