# AI Project Judge - The Complete "Under the Hood" Guide & Viva Q&A

This document explains **exactly** how the AI Project Judge works, why specific technologies were chosen, and answers common questions you might face during a project viva or technical interview.

---

## 🏗️ 1. Architecture & Feature Deep Dive

The project is built on a **FastAPI** backend (Python) and a **React** frontend. It uses a "Retrieval Augmented Generation" (RAG) style approach where we fetch data from various sources (GitHub, YouTube, Docs), feed it into a large context window, and ask an LLM (Gemini 1.5 Flash) to act as a specific persona.

### 🔍 Feature A: GitHub Repository Analysis
**How it works:**
1.  **Input:** Takes a GitHub URL (e.g., `github.com/user/repo`).
2.  **API Client:** Uses `PyGithub` to interact with the official GitHub API.
3.  **Discovery Phase:**
    -   Fetches `README.md` first (contains the most project context).
    -   Uses a **Breadth-First Search (BFS)** algorithm to traverse the file tree.
    -   *Optimization:* We limit the search depth to 2 levels and max 50 files to prevent timeout on massive repos.
    -   *Filtering:* Ignored directories include `node_modules`, `venv`, `target`, `.git` (too large/irrelevant).
4.  **Content Extraction:**
    -   It doesn't read *every* line. It looks for specific "high-value" files:
        -   **Config:** `package.json`, `requirements.txt` (to understand tech stack).
        -   **Entry Points:** `main.py`, `App.jsx`, `index.js` (to see code style/structure).
    -   **Security Scan:** It runs Regex matching on file contents to find hardcoded secrets (AWS Keys, OpenAI keys).
5.  **Output:** A compressed text summary of the file structure, dependencies, and code snippets is generated.

### 🎥 Feature B: Video Analysis (The "Smart" Pipeline)
Video analysis is complex because YouTube aggressively blocks bots. We implemented a **3-Layer Fallback Strategy**:

**Level 1: Fast Transcript (Standard API)**
-   **Tool:** `youtube-transcript-api`.
-   **Mechanism:** Tries to fetch hidden caption JSON directly from YouTube's internal API.
-   **Pros/Cons:** Fastest (<1s), but often blocked by IP restrictions or captcha.

**Level 2: Robust Text Fetch (The "yt-dlp" Hack)**
-   **Tool:** `yt-dlp` (Command Line Utility wrapper).
-   **Mechanism:** If Level 1 fails, we run `yt-dlp --write-subs --skip-download`. This mimics a real user browser to extract just the subtitle file without downloading the video.
-   **Pros/Cons:** Very robust, still fast (2-3s).

**Level 3: Native Multimodal Analysis (The "Nuclear" Option)**
-   **Tool:** `yt-dlp` (Download) + `Google Gemini File API`.
-   **Mechanism:** If text extraction completely fails (or if we need visual context), we:
    1.  **Download** the video (limited to 480p to save bandwidth/time).
    2.  **Upload** the actual video file to Google Gemini.
    3.  **Multimodal:** Gemini watches the video and listens to the audio natively.
-   **Pros/Cons:** Most powerful (understands visuals/emotion), but slow (30s+).

**Metrics Calculated:**
-   **Words Per Minute (WPM):** To measure pacing.
-   **Filler Words:** We count "um", "uh", "like" vs. total word count to judge confidence.

### 📄 Feature C: Presentation (PPT/PDF) Analysis
**How it works:**
1.  **PPTX:** Uses `python-pptx`. Ideally, a slide deck is a zip of XML files. We traverse `Slides -> Shapes -> TextFrames -> Paragraphs -> Runs` to extract all text linearly.
2.  **PDF:** Uses `pypdf`. Extracts raw text strings from pages.
3.  **Context:** The text is appended to the prompt so the AI knows the business logic/pitch deck often missing from code.

---

## 💡 2. "Why Did You Use..." (Design Decisions)

**Q: Why Gemini 1.5 Flash? Why not GPT-4?**
-   **Context Window:** Gemini 1.5 Flash has a **1 Million Token** context window. We can dump entire codebases and long transcripts into it without "truncating" data. GPT-4 is often limited or expensive for this volume.
-   **Native Multimodal:** Gemini can "watch" videos and "look" at images natively. GPT-4 usually requires frame-by-frame sampling which is complex to build.
-   **Speed/Cost:** "Flash" is optimized for low-latency code tasks.

**Q: Why FastAPI instead of Flask/Django?**
-   **Async:** FastAPI supports `async/await` natively. This is critical when calling external APIs (GitHub, Gemini) or running file downloads. Flask is synchronous (blocking) by default.
-   **Type Safety:** Uses Pydantic for data validation. If the frontend sends bad data, FastAPI rejects it automatically with clear errors.

**Q: Why React + Vite?**
-   **Vite:** Instant server start (HMR). Webpack (Create React App) is slow.
-   **Component Reusability:** We built reusable UI cards for the "Score", "Feedback", and "Roast" sections.

**Q: Why do you have a caching system (`TRANSCRIPT_CACHE`)?**
-   **Rate Limits:** YouTube and GitHub rate-limit aggressive requests.
-   **Cost/Time:** If a user clicks "Analyze" twice on the same video, we shouldn't re-download it. We hash the Video ID and store the result in a local JSON file for 24 hours.

---

## 🙋 3. Viva / Interview Q&A Cheat Sheet

**Examiner:** "How do you handle large repositories? Won't the API timeout?"
**You:** "Great question. We implemented two safeguards. First, we limit the file traversal depth to 2 levels and max 50 files. Second, we only extract snippet headers (first 100 lines) of code files, not the whole file. This fits within the context window while giving the AI enough 'flavor' of the code style."

**Examiner:** "How does the 'Consensus' mode work?"
**You:** "It uses `asyncio.gather` to spawn 5 parallel API calls to Gemini. Each call has a different 'System Prompt' (Persona). One is told to be a VC, another a CTO, etc. We then collect all 5 JSON responses and mathematically average their scores (mean) to produce the final 'Consensus Score'. It prevents bias from a single perspective."

**Examiner:** "What happens if the GitHub Link is private?"
**You:** "The backend checks for 404/403 errors. If it catches one, it returns a specific error message explaining 'Repo not found or Private'. For private repos, we would typically need OAuth implementation, but for this Hackathon version, we support public repos only."

**Examiner:** "Can this system detect plagiarism?"
**You:** "It performs a 'basic' check. The AI is prompted to look for generic 'Create-React-App' boilerplate or identical structures to known tutorials. However, true plagiarism detection requires a database of millions of papers/projects, which is outside the scope. We focus on *Project Quality* and *Uniqueness*."

**Examiner:** "What is the most innovative part of your code?"
**You:** "The Multi-Layer Video Fallback. Getting transcripts reliably without an official YouTube API key is hard. We engineered a system that degrades gracefully from 'Fast API' -> 'Scraping (yt-dlp)' -> 'Full Download & AI Vision'. It ensures the user almost *always* gets a result, no matter what."

**Examiner:** "How do you secure the API Keys?"
**You:** "They are stored in a `.env` file and loaded via `os.getenv`. They are never hardcoded in the source code. In a production environment, we would inject these as secrets into the Docker container."
