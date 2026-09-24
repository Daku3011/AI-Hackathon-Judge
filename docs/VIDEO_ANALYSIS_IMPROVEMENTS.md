# Video Analysis Architecture & Improvements 🎥⚡

This document details the video analysis pipeline of the **AI Hackathon Judge**, engineered for high reliability, low latency, and resilience against aggressive YouTube bot blocks on cloud providers such as Render.com, AWS, and GCP.

---

## 🎯 The Challenge: Datacenter IP Throttling

Automated video transcription on public cloud platforms faces severe restrictions:
1. **IP Blocking**: YouTube detects datacenter IP addresses (e.g. Render, AWS, DigitalOcean) and blocks unauthenticated requests with `HTTP 429 Too Many Requests` or `"Sign in to confirm you're not a bot"`.
2. **Missing Subtitles**: Many hackathon demo videos lack pre-generated closed captions.
3. **Execution Latency & Resource Constraints**: Downloading full video files inside a 512MB RAM container can cause `OOMKilled` (Out of Memory) crashes or request timeouts.

---

## 🛡️ The Solution: 4-Tier Resilient Fallback Architecture

To guarantee that users always receive evaluation results, we built a 4-tier fallback pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Client-Side Extraction (Browser)                   │
│ Runs `youtube-transcript` in the user's browser (Home IP)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Fails or disabled)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 2: Server-Side API with Cookie Authentication          │
│ `YouTubeTranscriptApi` authenticated with `cookies.txt`     │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Fails)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 3: Headless Subtitle Scraper (`yt-dlp`)                │
│ Uses browser User-Agent spoofing in isolated UUID folders   │
└──────────────────────────────┬──────────────────────────────┘
                               │ (Fails / Full Mode enabled)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ Tier 4: Native Multimodal Vision (Gemini 2.5 Flash)         │
│ Downloads 480p stream -> Uploads to Gemini File API         │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Detailed Tier Breakdown

### Tier 1: Browser-Side Extraction (Frontend Interceptor)
- **Mechanism**: The React client uses `youtube-transcript` before submitting the form.
- **Why it works**: Because the HTTP request originates from the user's personal browser (residential IP), YouTube's bot detection algorithms are not triggered.
- **Payload**: The extracted caption text is injected into `manual_transcript` in the `FormData` submission.

### Tier 2: Authenticated Server-Side API (`fetch_transcript_api`)
- **Mechanism**: Calls `YouTubeTranscriptApi.get_transcript(video_id, cookies=cookies_path)`.
- **Cookie Resolution**: Automatically scans the filesystem for valid cookies:
  1. `YOUTUBE_COOKIES_FILE` environment variable
  2. `cookies.txt` (root directory)
  3. `backend/cookies.txt`
  4. `/etc/secrets/cookies.txt` (Render Secret File mount path)
  5. `/app/cookies.txt` (Docker container path)

### Tier 3: Isolated `yt-dlp` Subtitle Fetching (`fetch_transcript_ytdlp`)
- **Mechanism**: Executes `yt-dlp` with `--skip-download --writesubtitles --writeautomaticsub`.
- **Security & Hygiene**: Executes inside an isolated temporary directory (`/tmp/ytdlp_subs_<UUID>`) and guarantees deletion in a `finally` block to prevent disk leaks.
- **Browser Fingerprinting**: Configures modern desktop Chrome User-Agent strings and Android/Web player client arguments.

### Tier 4: Gemini Multimodal Native Video Vision (`analyze_with_gemini`)
- **Mechanism**: If text transcripts are unavailable, downloads the lowest acceptable resolution video (capped at 480p) to conserve bandwidth.
- **Processing**: Uploads the video file to the **Google Gemini File API** (`client.files.upload`).
- **Poll State**: Monitors file processing state until active, then passes the native file object directly to Gemini 2.5 Flash, allowing the model to "watch" the demo and listen to the audio natively.

---

## 🎛️ Video Execution Modes (`VIDEO_MODE`)

You can control video analysis depth via the `VIDEO_MODE` environment variable:

| Mode | Allowed Strategies | Best Used For |
| :--- | :--- | :--- |
| `safe` | Tier 1 (Browser) + Tier 2 (Server API) | Low-memory instances (512MB RAM), strict bandwidth budgets. |
| `balanced` | Tier 1 + Tier 2 + Tier 3 (`yt-dlp` Subtitles) | Standard cloud instances (Render Free tier, Docker containers). |
| `full` *(default)* | All Tiers (including Tier 4 Multimodal Video Download) | Local development, high-tier cloud servers with 1GB+ RAM. |

---

## 📊 Speech & Presentation Analytics (`analyze_transcript_quality`)

Once transcript text is extracted, the engine runs heuristic speech analysis:

- **Word Count**: Total spoken words.
- **Estimated Duration**: Calculated at an average conversational baseline of 140 WPM (`wc / 140`).
- **Filler Word Detection**: Analyzes exact token occurrences of common hesitation markers (`um`, `uh`, `like`, `basically`, `actually`).
- **Filler Density**: `(filler_count / total_words) * 100`.
  - `< 3%`: Low filler usage (High Confidence score).
  - `3% - 5%`: Medium filler usage.
  - `> 5%`: High filler usage (Flags presentation nervousness).
- **Pacing Score**: Evaluates whether speech was rushed (>170 WPM) or sluggish (<110 WPM).

---

## 🔑 Environment Configuration Reference

```bash
# Video Strategy Setting
VIDEO_MODE=full                                # Options: safe | balanced | full

# Transcript Caching
TRANSCRIPT_CACHE_DIR=/tmp/transcript_cache     # Disk cache directory
TRANSCRIPT_CACHE_EXPIRY=86400                 # 24 hours in seconds
TRANSCRIPT_BLOCK_EXPIRY=21600                 # 6 hours in seconds

# Authentication & Proxy (Optional)
YOUTUBE_COOKIES_FILE=/etc/secrets/cookies.txt  # Explicit path to cookies.txt
YOUTUBE_PROXY=http://user:pass@host:port       # Optional proxy URL
```

---

## 🧪 Testing Video Analysis

Run the unit test suite:
```bash
python3 -m unittest tests.test_video_analyzer -v
```

Run the real-world integration verification test:
```bash
python3 tests/integration_test_video.py
```
