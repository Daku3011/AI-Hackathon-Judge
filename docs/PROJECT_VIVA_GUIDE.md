# AI Project Judge - The Complete "Under the Hood" Guide & Viva Q&A 🎓🤖

This document provides a comprehensive, rigorous technical breakdown of the **AI Hackathon Judge**. It explains the internal engineering mechanics, algorithmic choices, architectural trade-offs, and provides ready-to-use answers for project vivas, presentations, and technical interviews.

---

## 🏗️ 1. Architecture & Feature Deep Dive

The application is architected around a high-concurrency **FastAPI** backend (Python) coupled with a **React 18+ (Vite + Tailwind CSS v4)** frontend. It employs an advanced **Retrieval-Augmented Ingestion (RAI)** pipeline that gathers multi-modal context (source code, live website metadata, video transcripts/video streams, slide decks, and specifications) before delegating evaluation to **Google Gemini 2.5 Flash**.

```
                           ┌───────────────────────────────┐
                           │      User Submission UI       │
                           └───────────────┬───────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
         ┌─────────────────────┐┌──────────────────────┐┌───────────────────┐
         │ GitHub Repository   ││   Live Website URL   ││ Presentation/Docs │
         │   (PyGithub + BFS)  ││ (BeautifulSoup + DOM)││  (pptx + pypdf)   │
         └──────────┬──────────┘└──────────┬───────────┘└─────────┬─────────┘
                    │                      │                      │
                    └──────────────────────┼──────────────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │ Video & Speech Engine│
                                │   (4-Tier Fallback)  │
                                └──────────┬───────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Judge Engine (asyncio.gather)        │
                      │  Parallel Consensus (VC, CTO, UI, ...)  │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │ Scorecard, Markdown Critique & Roadmap  │
                      └─────────────────────────────────────────┘
```

---

### 🔍 Feature A: GitHub Repository Analysis (`github_analyzer.py`)

**Technical Flow:**
1. **URL Normalization**: Parses the input URL to extract the `owner/repo` path.
2. **API Client & Authentication**: Initializes `PyGithub`. If a `GITHUB_TOKEN` is present, it uses authenticated requests (increasing rate limit from 60 to 5,000 requests/hour).
3. **Optimized Breadth-First Search (BFS)**:
   - Traverses repository directories up to **depth 2** and caps inspection at **50 files**.
   - Filters out non-informative directories: `node_modules`, `venv`, `.git`, `dist`, `build`.
4. **Targeted Content Inspection**:
   - **Configuration Files**: Scans `package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, `pom.xml`, etc., to capture runtime dependencies.
   - **Code Samples**: Extracts the first 100 lines of entry points (`main.py`, `App.jsx`, `index.js`, `server.js`).
5. **Static Security & Leak Sweeper**:
   - Executes targeted regular expressions across all processed file contents to detect leaked secrets:
     - AWS Access Keys (`AKIA[0-9A-Z]{16}`)
     - OpenAI API Keys (`sk-...`)
     - GitHub Personal Access Tokens (`gh[pousr]_...`)
     - RSA/SSH Private Keys (`-----BEGIN PRIVATE KEY-----`)
     - Generic credentials (`password = ...`, `api_key = ...`)
6. **Codebase Metrics**:
   - Queries GitHub's language byte API to calculate percentage distributions.
   - Computes **Estimated Lines of Code (LOC)** using language byte weight normalization (`total_bytes // 40`).

---

### 🌐 Feature B: Live Website Analysis (`site_analyzer.py`)

When evaluating deployed web applications or submissions without a public GitHub repository:

1. **DOM Fetch & Asset Profiling**:
   - Sends HTTP requests using browser User-Agent headers with strict 10s timeouts.
   - Calculates total transfer payload size in KB.
   - Inspects the DOM using `BeautifulSoup4` to count total script tags, link stylesheets, and image assets.
2. **Internal Route Mapping ("Pinpoints")**:
   - Parses anchor tags (`<a href>`), normalizes relative URLs against the target domain, strips URL fragments and query parameters, and extracts up to 20 unique internal routes to evaluate site structure.
3. **Heuristic Tech Stack Detector**:
   - Analyzes raw HTML markup for distinctive runtime signatures:
     - **React**: `react`, `react-dom`, `_next/static`
     - **Next.js**: `__NEXT_DATA__`, `_next`
     - **Vue**: `vue`, `v-per`
     - **Angular**: `ng-version`, `ng-app`
     - **Tailwind CSS**: `tailwind`
     - **WordPress**: `wp-content`, `wp-includes`
     - **Google Analytics**: `gtag`, `google-analytics.com`

---

### 🎥 Feature C: 4-Tier Resilient Video & Speech Pipeline (`video_analyzer.py`)

Video extraction on cloud platforms (e.g., Render, AWS) often fails due to YouTube bot challenge blocks. We engineered a 4-tier defense architecture:

```
[Tier 1: Client Browser] ──(Success)──> Pass transcript in FormData
       │ (Blocked / Disabled)
       ▼
[Tier 2: Backend API + Cookies] ───────> YouTubeTranscriptApi with cookies.txt
       │ (Failed)
       ▼
[Tier 3: yt-dlp Subtitles] ────────────> Headless subtitle download + regex cleanup
       │ (Failed)
       ▼
[Tier 4: Gemini Multimodal Vision] ────> 480p Video Download -> Gemini File API
```

1. **Tier 1 (Client-Side Fetch)**: The React frontend uses `youtube-transcript` in the user's browser, fetching captions from the user's residential IP before hitting the backend.
2. **Tier 2 (Server API with Cookie Authentication)**: If server-side fetching is needed, the backend checks for `cookies.txt` (including Render Secret Files at `/etc/secrets/cookies.txt`), authenticating the `YouTubeTranscriptApi` session.
3. **Tier 3 (yt-dlp Subtitle Extraction)**: Runs `yt-dlp --write-subs --skip-download` within an isolated `uuid4` temporary directory with custom browser fingerprinting headers.
4. **Tier 4 (Gemini 2.5 Multimodal Vision)**: If subtitles do not exist, the video is downloaded at 480p and uploaded to Google Gemini's File API (`client.files.upload`), allowing the AI to "watch" the demo visually and listen to audio natively.
5. **Speech Analytics Computed**:
   - **Words Per Minute (WPM)**: Estimated from word count over duration (`wc / 140 WPM benchmark`).
   - **Filler Word Density**: Strict regex matching of hesitation markers (`um`, `uh`, `like`, `basically`, `actually`) to evaluate speaker confidence.

---

### 📄 Feature D: Presentation & Specification Parsing (`ppt_analyzer.py`, `doc_analyzer.py`)

- **Slide Decks (`.pptx`, `.ppt`)**: Utilizes `python-pptx` to traverse `Slides → Shapes → TextFrames → Paragraphs → Runs`, plus table rows, deduplicating text across slides.
- **Specifications & Whitepapers (`.pdf`, `.md`, `.txt`)**: Uses `pypdf` for page-by-page text extraction and native UTF-8 decoding for markdown/text specifications.

---

### 🗳️ Feature E: Multi-Judge Consensus Engine (`judge_engine.py`)

1. **Asynchronous Parallel Spawning**: In "Consensus" mode, the engine uses Python's `asyncio.gather` to launch **5 concurrent prompts** to Gemini 2.5 Flash, each configured with an uncompromising persona:
   - **The VC**: Focuses on TAM/SAM, competitive moat, business defensibility, and monetization.
   - **The CTO**: Focuses on code modularity, architectural patterns, tech stack suitability, and security.
   - **The Product Manager**: Focuses on problem-solution fit, user journeys, and UX polish.
   - **The UI/UX Designer**: Focuses on visual hierarchy, accessibility, and design consistency.
   - **The CS Professor**: Focuses on algorithmic complexity, data structures, and theoretical soundness.
2. **Mathematical Aggregation**:
   - Safely parses JSON response payloads and computes the arithmetic mean across 6 core criteria.
   - Aggregates and deduplicates top strengths, weaknesses, and potential interview questions.
   - Preserves individual judge evaluations (`[CTO - 8.2/10] ...`) so users can inspect divergent opinions.
3. **Markdown Output**: The prompt enforces Markdown output (`**bold**`, `*italic*`, `` `code` ``), rendered in the frontend via `react-markdown`.

---

## 💡 2. Architectural Design Decisions ("Why Did You Choose...")

### Q: Why Google Gemini 2.5 Flash over OpenAI GPT-4o?
- **Context Window**: Gemini 2.5 Flash provides a **1 Million+ token context window**, permitting entire codebases, slide texts, and transcripts to fit into a single context without truncation.
- **Native Multimodal Audio & Video**: Gemini natively ingests `.mp4` video files via the File API. GPT-4o requires splitting videos into individual frame images and running Whisper for audio—introducing high complexity, latency, and cost.
- **Inference Speed**: Flash models are optimized for sub-second code reasoning and low-cost parallel calls (vital for 5-persona consensus panels).

### Q: Why FastAPI over Flask or Django?
- **Async Concurrency**: FastAPI is built on ASGI (`Starlette` and `uvicorn`). It handles asynchronous I/O natively, making `asyncio.gather` for parallel AI calls seamless. Flask requires Celery or gevent to achieve similar non-blocking behavior.
- **Pydantic Validation**: Automatic schema enforcement and data serialization with clear validation error responses.

### Q: Why React + Vite + Tailwind CSS v4?
- **Vite's ESM Architecture**: Near-instantaneous Hot Module Replacement (HMR) and lightweight production bundles.
- **Tailwind CSS v4**: Built on modern CSS-first configuration and lightning-fast LightningCSS compiler, enabling sleek glassmorphic aesthetics without heavy component libraries.

### Q: Why implement a 4-tier video analysis strategy?
- YouTube actively defends against automated bot scrapers from cloud datacenters. Having a multi-stage fallback—from client-side browser execution down to native multimodal video uploads—ensures the user almost **always gets a result**.

---

## 🙋 3. Viva & Interview Q&A Cheat Sheet

### Examiner: "How does the system prevent hallucinated scores from the AI?"
**Response:** *"We apply three techniques: First, we supply structured factual context (actual dependencies, file tree, security scan findings, and speaking metrics like WPM and filler word percentage). Second, we enforce a strict JSON output schema. Third, in Consensus mode, we execute five distinct personas independently in parallel and calculate the mathematical average of their numeric ratings, effectively smoothing out individual prompt variance."*

### Examiner: "How do you protect against repository size timeouts on GitHub?"
**Response:** *"We limit repository exploration using a Breadth-First Search constrained to a maximum depth of 2 levels and a 50-file ceiling. We skip heavy directories like `node_modules` and only extract the first 100 lines of key entry points. This keeps payload ingestion under 15KB while giving the AI ample architectural context."*

### Examiner: "How did you solve the YouTube datacenter IP blocking issue on cloud platforms?"
**Response:** *"We implemented a hybrid client-server model. When a user submits a video, the frontend first attempts to fetch the caption transcript directly in the user's browser using `youtube-transcript`. Because this originates from a residential IP, YouTube does not trigger bot mitigation. The extracted text is then transmitted to the backend. As secondary fallbacks, the backend supports authenticated requests via `cookies.txt`, `yt-dlp`, and multimodal Gemini video processing."*

### Examiner: "How does your site analyzer detect technologies without executing JavaScript?"
**Response:** *"It analyzes the static HTML DOM and HTTP response headers for telltale runtime signatures. For instance, Next.js leaves `__NEXT_DATA__` scripts; React includes `react` or `react-dom` asset paths; Tailwind introduces specific utility class naming patterns; and WordPress reveals paths like `wp-content/`. It achieves 80%+ accuracy with minimal overhead."*

### Examiner: "What is your rubric for the overall score and win probability?"
**Response:** *"The overall score evaluates six distinct pillars: Innovation, Technical Implementation, Problem Relevance, UI/UX Design, Impact & Feasibility, and Presentation Quality, factored alongside security vulnerabilities. The Win Probability™ is a composite metric predicted by the judge panel that maps into three tiers: Legendary (>70%), Candidate (40–70%), and Needs Pivot (<40%)."*

### Examiner: "How are API credentials secured in production?"
**Response:** *"Credentials (`GEMINI_API_KEY`, `GITHUB_TOKEN`) are never hardcoded. They are loaded at runtime through environment variables (`os.getenv`). In Docker and Render deployments, they are injected securely as container environment secrets or secret files (`/etc/secrets/cookies.txt`)."*
