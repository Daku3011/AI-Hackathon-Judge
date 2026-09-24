# Release Notes

---

## Release Notes v2.1.0 - The "Web Intelligence & Markdown UI" Update 🌐✨

This release expands evaluation capabilities beyond GitHub to live web applications, adds client-side YouTube transcript extraction to overcome cloud IP restrictions, introduces a complete Markdown rendering pipeline, and provides individual score breakdowns for the Multi-Judge Consensus panel.

### 🌟 New Features

- **🌐 Live Website & Web App Analysis Engine (`site_analyzer.py`)**:
  - Evaluate projects that don't yet have an accessible repository.
  - Automatically crawls metadata, page size (KB), internal routes ("pinpoints"), and asset distributions (scripts, stylesheets, images).
  - Built-in heuristic detector for frontend frameworks and libraries: **React**, **Next.js**, **Vue**, **Angular**, **WordPress**, **Tailwind CSS**, **Bootstrap**, and **Google Analytics**.
- **⚡ Client-Side YouTube Transcript Extraction**:
  - Integrated `youtube-transcript` directly into the React frontend.
  - Captions are fetched in the user's browser before submission to the backend, completely bypassing cloud datacenter IP blocks (e.g., on Render, AWS, Heroku) without requiring server-side proxies.
- **📝 End-to-End Markdown AI Feedback**:
  - The AI judge prompts now instruct Gemini 2.5 Flash to format responses in structured Markdown (bold headers, bullet lists, inline code formatting).
  - Integrated `react-markdown` across the UI to render rich text for judge critiques, strengths, weaknesses, suggested Q&A, and mentor roadmaps.
- **🗳️ Individual Consensus Judge Ratings**:
  - Consensus mode now renders individual score badges and styled persona cards for each of the 5 judges (VC, CTO, Product Manager, UI/UX Designer, Professor), showing how each judge scored your project out of 10.
- **📏 Lines of Code (LOC) & Language Breakdown**:
  - Added repository language distribution bar with byte-size percentages.
  - Calculates estimated Lines of Code (LOC) based on language byte weights.
- **📄 Extended Document & Specification Support**:
  - Added support for project specifications in `.markdown`, `.rst`, `.txt`, and `.pdf` formats alongside slide presentations.

### 🛠️ Improvements & Fixes

- **Isolated Temporary File Management**: Replaced static temporary paths with isolated `uuid4` directories and guaranteed cleanup in `finally` blocks for `yt-dlp` subtitles and video downloads.
- **Video Strategy Hierarchy**: Introduced `VIDEO_MODE` configurations (`safe`, `balanced`, `full`) to provide flexible execution modes for constrained environments.
- **Authentication Resilience**: Expanded cookie lookup to automatically detect `cookies.txt` from Render Secret Files (`/etc/secrets/cookies.txt`), root directory, and `backend/`.
- **UI & Accessibility Polish**: Improved scorecard contrast, added one-click clipboard sharing, and made score indicators fully responsive.

---

## Release Notes v2.0.0 - The "Consensus & Vision" Update 🚀

This is a **major release** introducing parallel multi-judge evaluation, native video vision capabilities, and the upgrade to the Gemini 2.5 Flash architecture.

### 🌟 New Features

- **🤖 Multi-Judge Consensus Panel**:
  - Spins up **5 parallel AI Personas** (VC, CTO, Product Manager, UI/UX Designer, Professor) using `asyncio.gather`.
  - Scores are mathematically aggregated to reduce bias.
  - Receive diverse feedback: The VC evaluates market size and monetization, while the CTO inspects architecture and code quality.
- **🧠 Powered by Gemini 2.5 Flash**:
  - Targeted the `gemini-2.5-flash` model family for ultra-low latency and 1M+ token context window.
  - Improved reasoning capabilities for "Why you won't win" predictions and mentor roadmaps.
- **👁️ 3-Layer Video Analysis Engine**:
  - Fast Track: Standard YouTube Transcript API.
  - Stealth Track: `yt-dlp` subtitle extraction with browser spoofing.
  - Vision Track: Multimodal video upload to Gemini File API for visual presentation inspection.
- **📘 Viva & Defense Guide**:
  - Added `docs/PROJECT_VIVA_GUIDE.md`: A comprehensive cheat sheet for hackathon presentations and viva examinations.

### 🛠️ Improvements & Polish

- **Smart Networking**: Added User-Agent spoofing to `yt-dlp` to bypass bot verification challenges.
- **Codebase Refactor**: Cleaned up `main.py` and `services/` with type annotations, docstrings, and robust error handling.
- **UI Updates**: Polished loading screen animations and responsive scorecard layout.

### 🐛 Bug Fixes

- Fixed `404 NOT_FOUND` errors by ensuring API model aliases match the active Gemini model family.
- Fixed video download failures on cloud IPs by standardizing header negotiation and fallback paths.
