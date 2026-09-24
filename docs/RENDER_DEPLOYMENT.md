# Deployment Guide for Render.com 🚀

This guide walks you through deploying the **AI Hackathon Judge** on [Render.com](https://render.com) using its native Docker environment, with full support for GitHub repo analysis, website inspection, presentation parsing, and robust video transcription.

---

## 📋 Prerequisites

- A [Render.com](https://render.com) account (Free or Starter tier)
- A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)
- A **GitHub Personal Access Token** (optional, recommended to prevent GitHub rate limits)

---

## 🛠️ Step 1: Connect Repository to Render

1. Push your latest code to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New +** → **Web Service**.
3. Select your repository: `AI-Hackathon-Judge`.
4. Configure the service settings:
   - **Name**: `ai-hackathon-judge` (or your choice)
   - **Region**: Choose the closest location to your audience (e.g., Oregon, Frankfurt, Singapore)
   - **Branch**: `master` (or `main`)
   - **Root Directory**: *Leave blank* (uses repo root)
   - **Runtime**: `Docker`
   - **Instance Type**: `Free` (512 MB RAM) or `Starter` ($7/mo recommended for continuous uptime)

Render will automatically locate the multi-stage `./Dockerfile` in your repository.

---

## 🔑 Step 2: Configure Environment Variables

Navigate to the **Environment** tab in your Render Web Service settings and configure:

### Required Variables

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `AIzaSy...` | Required. Access token for Gemini 2.5 Flash. |

### Recommended Variables

| Key | Example Value | Description |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | `ghp_...` | Recommended. Avoids the 60 requests/hr unauthenticated GitHub rate limit. |
| `VIDEO_MODE` | `balanced` | Set to `balanced` or `safe` on Render Free tier (512MB RAM) to prevent memory spikes from full video downloads. Set to `full` on paid tiers. |
| `TRANSCRIPT_CACHE_DIR` | `/tmp/transcript_cache` | Temporary storage for transcript caching. |
| `TRANSCRIPT_CACHE_EXPIRY` | `86400` | 24-hour cache duration (in seconds). |

---

## 🎬 Step 3: Overcoming YouTube Datacenter IP Blocks on Render

Cloud hosting providers (including Render, AWS, and GCP) use shared datacenter IP pools. YouTube actively blocks server-side requests from these IPs with *"Sign in to confirm you're not a bot"*.

The AI Hackathon Judge resolves this on Render through four independent layers:

### Layer 1: Automatic Browser-Side Caption Fetching (No Setup Required!)
When a user submits a YouTube URL on the frontend, the browser client runs `youtube-transcript` locally on the user's home network, extracts the caption text, and bundles it into the submission `FormData`. Because the request originates from the user's residential IP, **Render's datacenter IP is never exposed to YouTube**.

### Layer 2: Render Secret File (`cookies.txt`)
If you want server-side fallback fetching to work reliably:
1. Use a browser extension (such as *Get cookies.txt LOCALLY*) while logged into YouTube.
2. Export your cookies to a file named `cookies.txt`.
3. In your Render Dashboard, click **Environment** → **Secret Files** → **Add Secret File**.
   - **Filename**: `cookies.txt`
   - **Contents**: Paste the content of your `cookies.txt` file.
   - Render mounts secret files at `/etc/secrets/cookies.txt`. The backend automatically detects this path!

### Layer 3: Manual Transcript Textarea
Users can always paste speaker notes or transcript text directly into the "Manual Transcript" field on the submission form.

---

## 🚀 Step 4: Deploy and Verify

1. Click **Create Web Service** (or **Manual Deploy** → **Deploy latest commit**).
2. Render will execute the multi-stage Docker build:
   - Build frontend assets with Node 20.
   - Install Python dependencies (including FastAPI, BeautifulSoup4, PyGithub, google-genai).
   - Expose port `8000` (Render binds to `$PORT` automatically).
3. Once the service transitions to `Live`:
   - Open your assigned URL (`https://your-service.onrender.com`).
   - Submit a test public repository or website URL.
   - Verify that scorecards, Markdown feedback, and judge personas render correctly.

---

## 💡 Performance Optimization & Free Tier Considerations

- **Cold Starts**: Render's free tier spins down instances after 15 minutes of inactivity. The first wake-up request may take 30–50 seconds.
- **Memory Management**: Render's free tier provides 512 MB of RAM. Using `VIDEO_MODE=balanced` or relying on browser-side caption extraction avoids downloading large 480p video files into container memory.
- **Disk Storage**: `/tmp/transcript_cache` uses ephemeral disk storage that resets when the container restarts. Transcripts cached during the active lifecycle provide sub-second retrieval for repeat evaluations.

---

## 🛠️ Common Troubleshooting

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| `GEMINI_API_KEY missing` | Environment variable not set. | Add `GEMINI_API_KEY` under the Environment tab and trigger a redeploy. |
| `GitHub Error 403: Rate limit exceeded` | Unauthenticated GitHub API requests hit 60 req/hr limit. | Provide a personal `GITHUB_TOKEN` in environment variables. |
| `Transcript unavailable (All methods failed)` | Video has no captions or YouTube IP block occurred on server. | Ensure browser-side transcript extraction succeeded, paste text manually, or configure a `cookies.txt` secret file. |
| Container crashes with `OOMKilled` (Out of Memory) | `yt-dlp` downloaded a large video in `full` mode on a 512MB container. | Set `VIDEO_MODE=balanced` in Render environment variables. |
