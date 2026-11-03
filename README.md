# YT Downloader

A small website that turns a YouTube link into an MP4 or MP3 file.

It has two parts, because Netlify can only host static pages and can't run the tools that do the downloading:

| Part | Folder | Runs on | Job |
|------|--------|---------|-----|
| Website | `frontend/` | Netlify | The page you see and use |
| Server | `backend/` | Render (Docker) | Runs yt-dlp and ffmpeg and sends the file back |

```
yt-downloader/
├── README.md
├── netlify.toml          # tells Netlify to publish the frontend folder
├── .gitignore
├── frontend/
│   └── index.html        # the whole website
└── backend/
    ├── app.py            # Flask server using yt-dlp
    ├── requirements.txt
    └── Dockerfile        # installs Python and ffmpeg
```

> Only download videos you own or have permission to save. Check your school or network rules before using this on a school device.

---

## Setup

You can do all of this in a browser. You don't need to install anything.

### 1. Put the files on GitHub

1. Create a new repository on [github.com](https://github.com/new) (public or private).
2. Click **Add file → Upload files** and drag in everything from this folder, keeping the folder structure: `README.md`, `netlify.toml`, `.gitignore`, `frontend/`, and `backend/`.
3. Click **Commit changes**.

### 2. Deploy the server on Render

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New → Web Service** and pick your repository.
3. Set these options:
   - **Root Directory:** `backend`
   - **Language / Runtime:** `Docker`
   - **Instance type:** Free
4. Click **Deploy**. The first build takes a few minutes because it installs ffmpeg.
5. Copy the URL Render gives you, for example `https://yt-downloader-abc1.onrender.com`.
6. Open that URL in a new tab. You should see `{"ffmpeg":true,"ok":true}`.

The free plan goes to sleep when idle, so the first request after a break can take about a minute.

### 3. Deploy the website on Netlify

1. Go to [netlify.com](https://www.netlify.com) and sign in with GitHub.
2. Click **Add new site → Import an existing project** and pick the same repository.
3. Netlify reads `netlify.toml` and publishes the `frontend` folder. Leave the build command empty and click **Deploy**.

Prefer drag and drop? Drag just the `frontend` folder onto [app.netlify.com/drop](https://app.netlify.com/drop).

### 4. Connect them

Open your Netlify site, click **Server settings** at the bottom, and paste your Render URL. It's saved in your browser.

To skip this step on every device, open `frontend/index.html`, set `DEFAULT_API` near the top of the script to your Render URL, and commit the change:

```js
const DEFAULT_API = "https://yt-downloader-abc1.onrender.com";
```

---

## Using it

1. Paste a YouTube link. A preview appears.
2. Pick a quality. **Best** gives the highest-quality MP4, and **MP3 audio** gives audio only.
3. Click **Download**. The server prepares the file, then your browser saves it.

Playlists aren't supported. Each link downloads a single video.

---

## Settings (optional)

Set these on Render under **Environment**:

| Variable | What it does |
|----------|--------------|
| `ALLOWED_ORIGIN` | Your Netlify URL, for example `https://my-site.netlify.app`. Stops other websites from using your server. Defaults to any site. |
| `COOKIES_TXT` | The contents of a YouTube `cookies.txt` file. See below. |

---

## Troubleshooting

**"Sign in to confirm you’re not a bot"**
YouTube often blocks traffic from cloud servers like Render. The usual fix is to give yt-dlp cookies from a logged-in browser:

1. Use a throwaway Google account, not your main one. YouTube can flag accounts used this way.
2. Export your YouTube cookies in Netscape format with a browser extension such as *Get cookies.txt LOCALLY*.
3. Paste the whole file into the `COOKIES_TXT` environment variable on Render and redeploy.

Cookies expire, so you may need to refresh them every so often.

**Downloads suddenly stop working**
YouTube changes things often, and yt-dlp releases fixes quickly. On Render, click **Manual Deploy → Clear build cache & deploy** to pull the latest yt-dlp.

**"Couldn’t reach the server"**
Check the address in Server settings (no trailing path), and open it in a tab to wake it up if it's on the free plan.

**Very large videos fail**
The file is held in memory in your browser while it downloads, and free servers have limited disk space. Try a lower quality.

**The site won’t load at school**
Network filters may block Netlify, Render, or GitHub. That's a network rule, and this project doesn't work around it.

---

## Run it locally (optional)

If you have Python and ffmpeg installed:

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `frontend/index.html` in your browser and set the server address to `http://localhost:5000`.

---

## Credits

Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), [ffmpeg](https://ffmpeg.org), and [Flask](https://flask.palletsprojects.com).
