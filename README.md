# Mood Checker — Python web app on Runpod (from GitHub)

A small website written in Python (FastAPI). It shows a front page where visitors type a sentence,
and an AI model replies whether it sounds positive or negative. The code lives on GitHub; GitHub
builds the Docker image automatically; Runpod runs it and gives you an `https://` address.

```
 You edit code on GitHub
        │  (every change)
        ▼
 GitHub Actions builds the Docker image ──► GitHub Container Registry (ghcr.io)
                                                   │  Runpod pulls the image
                                                   ▼
                                    Runpod CPU Pod running your container
                                                   │
                       https://<pod-id>-8000.proxy.runpod.net  ◄── visitors
```

You do **not** need Docker or Git installed on your computer — everything happens in the browser.

## What's in this repo

| File | Purpose |
|---|---|
| `app/main.py` | The Python web server: front page, `/api/mood`, `/ping` |
| `app/static/` | The web page (HTML, CSS, JavaScript) |
| `requirements.txt` | Python libraries |
| `Dockerfile` | Recipe for the container image |
| `.github/workflows/docker-publish.yml` | Tells GitHub to build and publish the image |

---

## Part A — Put the code on GitHub (≈15 min)

1. Create a free account at https://github.com and sign in.
2. Top-right **+** → **New repository**.
   - Name: `runpod-webapp`
   - Visibility: **Public** (simplest; keep secrets out of the code)
   - Tick **Add a README file** → **Create repository**.
3. Unzip `runpod-webapp.zip` on your computer.
4. In the repo, click **Add file → Upload files**. Drag in `Dockerfile`, `requirements.txt`,
   `.dockerignore`, `.gitignore`, `README.md` and the whole `app` folder. Click **Commit changes**.
   (Replace the README when asked.)
5. The `.github` folder is hidden on most computers, so create the workflow by hand:
   - **Add file → Create new file**
   - File name: type exactly `.github/workflows/docker-publish.yml` (the slashes create the folders)
   - Open `docker-publish.yml` from the zip in Notepad/TextEdit, copy everything, paste it in.
   - **Commit changes**.

Check: your repo's front page should list `app`, `.github`, `Dockerfile`, `requirements.txt`.

## Part B — Let GitHub build the Docker image (≈10 min, mostly waiting)

1. Open the **Actions** tab of your repo. A run called *Build and publish Docker image* starts
   automatically after step A5 (if not, click it → **Run workflow**).
2. Wait for the green tick (about 5–10 minutes the first time). A red cross? Click it to read
   the error and check the file names/paths from Part A.
3. Make the image public so Runpod can download it:
   - Click your profile picture → **Your profile → Packages** → `runpod-webapp`.
   - **Package settings** → *Danger Zone* → **Change visibility → Public** → confirm.
4. Your image address is now:
   `ghcr.io/YOUR-GITHUB-USERNAME/runpod-webapp:latest` (all lowercase).

## Part C — Run it on Runpod and get your HTTPS address (≈10 min)

1. Sign in at https://console.runpod.io → **Pods** → **Deploy**.
2. Choose **CPU** (this app doesn't need a GPU — much cheaper). Pick the cheapest option with
   **at least 2 vCPU and 4 GB RAM**.
3. Click **Edit Template** (or **Change Template → custom**) and set:
   - **Container Image:** `ghcr.io/YOUR-GITHUB-USERNAME/runpod-webapp:latest`
   - **Expose HTTP Ports:** `8000`
   - **Container Disk:** `10` GB
   - **Volume Disk:** `0` GB (this app saves nothing, and a volume keeps billing while stopped)
   - Save / Set Overrides.
4. Give the Pod a name (e.g. `mood-checker`) → **Deploy On-Demand**.
5. Wait until the Pod shows **Running**, then give it another 1–2 minutes to download the image
   and load the model (watch the **Logs** — you're ready when you see `Uvicorn running on http://0.0.0.0:8000`).
6. Click **Connect → HTTP Service [Port 8000]**. Your website opens at:

   **`https://<your-pod-id>-8000.proxy.runpod.net`**

   That's your public HTTPS front page — share the link with anyone. Runpod provides the
   HTTPS certificate automatically.

## Part D — Change the website later

1. On GitHub, open a file (e.g. `app/static/index.html`), click the ✏️ pencil, edit, **Commit changes**.
2. The **Actions** tab rebuilds the image automatically (wait for the green tick). Each build
   also gets a unique tag such as `v-1a2b3c4` — find it under **Packages → runpod-webapp**.
3. In Runpod: **Pods** → your Pod → ☰ menu → **Edit Pod** → change the image to the new tag
   (e.g. `ghcr.io/you/runpod-webapp:v-1a2b3c4`) → **Save**. The Pod restarts with the new version.
   If it doesn't pick up the change, terminate the Pod and deploy again (Part C) — note the
   address changes when the Pod ID changes.

## Part E — Control your spend (you have $20)

| Item | Approx. rate | Per day if left on 24 h |
|---|---|---|
| CPU Pod, 2 vCPU / 4 GB RAM | ~$0.06/hour (confirm in the console — prices vary) | ~$1.44 |
| Container disk, 10 GB | $0.10/GB/month | ~$0.03 |
| Data transfer | free | $0 |
| GitHub repo, Actions, ghcr.io (public) | free | $0 |
| **Total** | | **≈ $1.50/day** |

- **$20 lasts roughly 13 days** running non-stop, or much longer if you stop the Pod when not needed.
- **Stop** the Pod (■) to pause billing. With volume disk at 0 GB, a stopped Pod costs nothing.
  Starting it again usually keeps the same address.
- **Terminate** deletes it entirely.
- Pods bill per second for as long as they run, whether or not anyone visits the site.

## Things to know

- **The site is public.** Anyone with the link can use it, and the Pod ID is only light obscurity.
  Don't put private data or secrets in the app; add a login if you later handle anything sensitive.
- **100-second limit.** Runpod's proxy cuts off any request that takes longer than 100 seconds.
- **Bind to 0.0.0.0.** Already done in the Dockerfile — needed for Runpod to reach the app.
- **Custom domain** (e.g. `www.yourname.com`): possible later by putting a service such as
  Cloudflare in front; the `proxy.runpod.net` address works without one.

## Optional — Runpod Serverless straight from GitHub

Runpod can also build directly from this repo for a **Serverless Load Balancer** endpoint
(Settings → Connections → GitHub → Connect; then Serverless → New Endpoint → Import Git Repository,
type **Load Balancer**, CPU or the cheapest GPU). The app already has the `/ping` health check and reads
the `PORT` variable Runpod sets.

Trade-offs for a beginner's public website:
- It scales to zero (cheaper when idle), but the first visitor after a quiet spell waits while a worker starts.
- Runpod's examples call these endpoints with your Runpod API key, so it suits an API behind
  another website more than a public front page.
- Pushing commits doesn't redeploy; you create a GitHub **Release** to trigger a rebuild.

For a simple HTTPS website, the Pod route above is the straightforward choice.

## Run it on your own computer (optional)

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000.
