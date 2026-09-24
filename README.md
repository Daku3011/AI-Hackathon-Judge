# AI Hackathon Judge 🤖⚖️

Evaluate your hackathon project locally before the real judges do. Point the app at your GitHub repository or live website, slide deck, and demo video to get instant multi-persona scores, deep technical critique, security vulnerability alerts, and a brutally honest "why you won't win" reality check.

<div align="center">
  <img src="screenshots/Submisstion.png" alt="Home Screen" width="800"/>
  <p><em>Simulate top judges (VC, CTO, Product Manager, UI/UX Designer, Professor, or Roast Master) before demo day.</em></p>
</div>

---

## ✨ Key Features & Capabilities

- **🗳️ Multi-Judge Consensus Panel**: Five AI personas (The VC, The CTO, Product Manager, UI/UX Designer, CS Professor) evaluate your project in parallel via asynchronous execution (`asyncio.gather`), mathematically aggregating scores to eliminate single-judge bias while giving you persona-attributed critiques.
- **🌐 Dual-Source Code & Web Analysis**:
  - **GitHub Repositories**: BFS file tree analysis, dependency inspection (`package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`, etc.), key entry points, language breakdown percentages, and estimated Lines of Code (LOC).
  - **Live Web Applications**: Direct URL inspection analyzing page weight, DOM asset counts (scripts, stylesheets, images), route mapping, and automated tech stack detection (React, Next.js, Vue, Angular, WordPress, Tailwind, etc.).
- **🛡️ Static Security & Secret Sweeper**: Proactive regex audits for leaked credentials (AWS access keys, OpenAI API keys, GitHub tokens, SSH/RSA private keys, and generic secrets).
- **🎥 4-Layer Resilient Video Analysis**:
  1. *Browser-Side Fast Fetch*: Extracts YouTube captions directly in the client browser, eliminating datacenter IP blocks on cloud hosts.
  2. *Server API with Cookie Auth*: Secure authenticated transcript fetching with YouTube session cookies (`cookies.txt`).
  3. *Stealth Subtitle Extractor*: Headless subtitle extraction via `yt-dlp` with browser fingerprint spoofing.
  4. *Gemini 2.5 Multimodal Vision*: Downloads video (480p) and streams to Google Gemini to "watch" the demo, analyzing presentation confidence, clarity, visual bugs, and speaking pace (WPM & filler words).
- **📑 Document & Pitch Deck Parsing**: Native extraction of slides, tables, and speaker content from `.pptx`, `.ppt`, and `.pdf` presentations, plus `.md`, `.txt`, and `.pdf` technical documentation or PRDs.
- **📊 Win Probability™ & Scorecard**: Clear rubric breakdown across 6 core criteria (Innovation, Technical Implementation, Problem Relevance, UI/UX, Impact & Feasibility, Presentation), alongside a winning probability percentage and a blunt "Why You Won't Win" reality check.
- **🚀 Mentor Mode Roadmap**: Actionable, phased step-by-step milestones to transition your hackathon prototype into a production-grade product.
- **🎨 Glassmorphic Markdown UI**: High-polish responsive interface with full Markdown formatting for code snippets, bold highlights, bullet lists, and individual judge score chips.

---

## 📚 Documentation & Guides

- **[Viva & Technical Defense Guide](docs/PROJECT_VIVA_GUIDE.md)** - Architecture deep dive, technical decisions, and examiner Q&A cheat sheet.
- **[Render.com Cloud Deployment Guide](docs/RENDER_DEPLOYMENT.md)** - Step-by-step production deployment instructions with video workaround tips.
- **[Video Analysis Improvements](docs/VIDEO_ANALYSIS_IMPROVEMENTS.md)** - Detailed technical guide to the 4-layer video pipeline and caching engine.
- **[Standalone Build Instructions](docs/BUILD_INSTRUCTIONS.md)** - Building standalone executables for Linux and Windows.
- **[Implementation Summary](docs/IMPLEMENTATION_SUMMARY.md)** - Architectural specifications and system capabilities overview.
- **[Release Notes](RELEASE_NOTES.md)** - Full version history and recent changelog.
- **[Frontend Guide](frontend/README.md)** - Frontend component structure and development workflow.

---

## 🎭 Judge Personas

| Persona | Focus Areas & Evaluation Style |
| :--- | :--- |
| ⚖️ **Standard Judge** | Objective, balanced evaluation across all hackathon criteria. |
| 🗳️ **Consensus Panel** | 5 judges run concurrently; scores are mathematically averaged with individual persona breakdowns. |
| 💸 **The VC** | Market size, TAM/SAM, competitive moat, monetization, and business defensibility. |
| 🧔🏻‍♂️ **The Grumpy CTO** | Architecture patterns, code modularity, engineering rigor, scalability, and technical debt. |
| 📦 **Product Manager** | User personas, problem-solution fit, user journeys, edge-case coverage, and feature utility. |
| 🎨 **UI/UX Designer** | Visual hierarchy, typography, accessibility, component consistency, and interaction polish. |
| 🎓 **The CS Professor** | Algorithmic complexity (Big-O), theoretical correctness, data structures, and academic rigor. |
| 🔥 **Roast Master** | Ruthless, satirical, and brutally honest critique pointing out every flaw. |

---

## 🗂️ What You Can Submit

1. **Code Source**:
   - Public GitHub repository URL (`https://github.com/owner/repo`)
   - **OR** Live Web Application URL (`https://myproject.vercel.app`)
2. **Demo Video**:
   - YouTube video URL (standard, shortened `youtu.be`, or embed formats)
   - **Manual Transcript Option**: Optional fallback textarea if video captions are restricted.
3. **Presentation / Pitch Deck**:
   - Files supported: `.pptx`, `.ppt`, `.pdf`
4. **Project Specification / Docs**:
   - Files supported: `.pdf`, `.md`, `.txt`, `.markdown`, `.rst`

---

## 🛠️ Tech Stack Architecture

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) with Uvicorn ASGI server
- **AI Core**: Google Gemini 2.5 Flash (`gemini-2.5-flash` via official `google-genai` SDK)
- **Repository Analysis**: `PyGithub`, regex security scanners, dynamic LOC estimation
- **Web Scraping**: `BeautifulSoup4`, `requests`, URL normalization & tech stack heuristics
- **Video & Speech Analytics**: `youtube-transcript-api`, `yt-dlp`, `google-genai` File API
- **Document Extractors**: `python-pptx`, `pypdf`

### Frontend
- **Framework**: React 18+ powered by [Vite](https://vitejs.dev/)
- **Styling**: Tailwind CSS v4 with glassmorphic cards and responsive flex/grid layouts
- **Client Utilities**: `youtube-transcript` (browser-side caption fetching), `react-markdown` (formatted rich text feedback), `lucide-react`

### Deployment & Packaging
- **Containerization**: Multi-stage Docker & Docker Compose
- **Desktop Bundling**: PyInstaller standalone binaries for Linux and Windows

---

## 🚀 Quickstart

### Option A: Docker (Recommended)

1. Clone repository:
   ```bash
   git clone https://github.com/Daku3011/AI-Hackathon-Judge.git
   cd AI-Hackathon-Judge
   ```
2. Create `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_personal_access_token_here   # Recommended to avoid rate limits
   ```
3. Build and launch:
   ```bash
   docker-compose up --build
   ```
4. Access the application in your browser at:
   ```
   http://localhost:8000
   ```

---

### Option B: Local Development Setup

#### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` for the frontend development server (configured with proxy/CORS to talk to backend at `http://localhost:8000`).

---

### Option C: Standalone Executable

- **Linux**: Run `python3 build.py` to produce `./dist/project_judge/project_judge`.
- **Windows**: Run `build_windows.bat` to produce `dist\project_judge\project_judge.exe`.
- Ensure your `.env` file resides next to the generated executable.

---

## 🔑 Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | **Yes** | — | Google Gemini API key (Makersuite / Google AI Studio). |
| `GITHUB_TOKEN` | No | — | GitHub Personal Access Token (prevents rate limits and reads public repo contents). |
| `PORT` | No | `8000` | HTTP port for the FastAPI web server. |
| `VIDEO_MODE` | No | `full` | Strategy for video processing: `safe` (API only), `balanced` (API + yt-dlp subtitles), or `full` (API + yt-dlp subtitles + Gemini video vision). |
| `TRANSCRIPT_CACHE_DIR` | No | `/tmp/transcript_cache` | Filesystem path for caching extracted video transcripts. |
| `TRANSCRIPT_CACHE_EXPIRY` | No | `86400` (24h) | Time in seconds before cached video transcripts expire. |
| `TRANSCRIPT_BLOCK_EXPIRY` | No | `21600` (6h) | Time in seconds before temporary blocks on failed video fetches expire. |
| `YOUTUBE_COOKIES_FILE` | No | Auto-detect | Path to `cookies.txt` for authenticated YouTube requests (checks `/etc/secrets/cookies.txt`, `cookies.txt`, `backend/cookies.txt`). |
| `YOUTUBE_PROXY` | No | — | Optional HTTP/HTTPS proxy to route YouTube queries. |
| `VITE_API_URL` | No | `""` (relative) | Backend base URL for frontend builds (leave blank for same-origin). |

---

## 🎬 Video Analysis & Cloud IP Workarounds

Cloud hosts like Render, AWS, and Heroku have shared datacenter IP ranges that YouTube frequently throttles with *"Sign in to confirm you're not a bot"*. The AI Hackathon Judge resolves this using a 4-tier strategy:

1. **Browser-Side Fetch**: The frontend fetches captions in the user's browser via `youtube-transcript`, sending the raw text directly to the backend.
2. **YouTube Cookie Injection**: Export YouTube cookies via a browser extension (e.g. *Get cookies.txt LOCALLY*) into a file named `cookies.txt` in the `backend/` folder or as a Render Secret File at `/etc/secrets/cookies.txt`.
3. **Manual Transcript Box**: Paste presentation transcript or speaker notes directly into the UI.
4. **Local Execution**: Running locally on your residential IP works out-of-the-box without proxies.

---

## 🧪 Testing & Verification

Run the backend unit test suite:
```bash
python3 -m unittest discover tests -v
```

Run the video analyzer integration verification:
```bash
python3 tests/integration_test_video.py
```

Run frontend linting:
```bash
cd frontend
npm run lint
```

---

## 🖼️ UI Gallery

| Submission & Persona Selection | Detailed Scorecard & Criteria | Strengths vs Weaknesses |
| :---: | :---: | :---: |
| <img src="screenshots/Submisstion.png" width="410" alt="Submission Screen" /> | <img src="screenshots/Detailed_Scorecard.png" width="310" alt="Detailed Scorecard" /> | <img src="screenshots/Strengths_Weaknesses.png" width="310" alt="Strengths and Weaknesses" /> |

| Suggested Q&A Questions | Video Pitch Quality Metrics | AI Final Verdict |
| :---: | :---: | :---: |
| <img src="screenshots/Suggested_Questions.png" width="310" alt="Suggested Questions" /> | <img src="screenshots/Video_Presentation_Analysis.png" width="310" alt="Video Analysis" /> | <img src="screenshots/AI_Verdict_New.png" width="310" alt="AI Verdict" /> |

<div align="center">
  <h3>Brutal Reality Check</h3>
  <img src="screenshots/Why_It_Wont_Win.png" width="450" alt="Why It Won't Win" />
</div>

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.
