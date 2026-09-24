# System Architecture & Implementation Summary 📋

## Project Overview

The **AI Hackathon Judge** is a full-stack, AI-powered automated evaluation system designed to stress-test hackathon submissions before live presentation day. It ingests multi-source project artifacts (GitHub repositories, live website URLs, pitch decks, specifications, and demo videos), runs static security and quality audits, and dispatches parallel LLM persona evaluations using **Google Gemini 2.5 Flash**.

---

## 🏗️ Architectural Topology

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React 18 + Vite)                     │
│  • InputForm: Validates URLs, uploads decks (.pptx/.pdf) & specs       │
│  • youtube-transcript: Client-side caption fetcher to avoid cloud blocks│
│  • Scorecard: Interactive circular gauge & 6-criteria progress bars    │
│  • FeedbackSection: Markdown-formatted consensus cards & roadmap HUD   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP POST /analyze (FormData)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI + Uvicorn)                       │
│                                                                        │
│  ┌───────────────────────┐  ┌───────────────────────┐                 │
│  │  github_analyzer.py   │  │   site_analyzer.py    │                 │
│  │  • PyGithub client    │  │   • BeautifulSoup4    │                 │
│  │  • BFS file search    │  │   • DOM asset stats   │                 │
│  │  • Secret regex scan  │  │   • Route mapping     │                 │
│  │  • Language & LOC     │  │   • Tech stack detect │                 │
│  └──────────┬────────────┘  └───────────┬───────────┘                 │
│             │                           │                             │
│  ┌──────────▼────────────┐  ┌───────────▼───────────┐                 │
│  │   doc_analyzer.py     │  │    ppt_analyzer.py    │                 │
│  │   • pypdf text parser │  │    • python-pptx      │                 │
│  │   • Markdown / text   │  │    • Slide & tables   │                 │
│  └──────────┬────────────┘  └───────────┬───────────┘                 │
│             │                           │                             │
│  ┌──────────▼───────────────────────────▼───────────┐                 │
│  │               video_analyzer.py                  │                 │
│  │   • 4-tier fallback (Browser, API, yt-dlp, Vision)│                 │
│  │   • Cookie jar discovery & transcript cache      │                 │
│  │   • Speech metrics (WPM, filler word density)    │                 │
│  └──────────────────────┬───────────────────────────┘                 │
│                         │                                             │
│                         ▼                                             │
│  ┌──────────────────────────────────────────────────┐                 │
│  │               judge_engine.py                    │                 │
│  │   • Parallel consensus via asyncio.gather        │                 │
│  │   • Personas: VC, CTO, Product, UI/UX, Professor │                 │
│  │   • Mathematical score normalization & Markdown  │                 │
│  └──────────────────────────────────────────────────┘                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Services Specification

### 1. `backend/services/github_analyzer.py`
- **Purpose**: Clones repository intelligence via the GitHub API without cloning full git objects.
- **Traversal Strategy**: Constrained Breadth-First Search (BFS) capped at depth 2 and maximum 50 files.
- **Security Scan**: Regex audit checking for leaked credentials (AWS, OpenAI, GitHub PATs, Private Keys, Generic Secrets).
- **Codebase Metrics**: Calculates exact byte percentages per language and estimates Lines of Code (LOC) via byte-weight heuristics (`bytes // 40`).

### 2. `backend/services/site_analyzer.py`
- **Purpose**: Evaluates deployed applications when a GitHub repository is not available.
- **DOM & Asset Profiling**: Measures page weight (KB), scripts, stylesheets, and images.
- **Route Crawler**: Maps up to 20 unique internal routes ("pinpoints") within the target domain.
- **Stack Detection**: Identifies React, Next.js, Vue, Angular, WordPress, Tailwind CSS, Bootstrap, and Google Analytics from DOM markers and asset patterns.

### 3. `backend/services/video_analyzer.py`
- **Purpose**: High-reliability presentation extraction with a 4-tier fallback system.
- **Tier 1**: Client-side `youtube-transcript` extraction from the user's browser.
- **Tier 2**: Server-side `YouTubeTranscriptApi` with automatic cookie discovery (`cookies.txt`, `/etc/secrets/cookies.txt`).
- **Tier 3**: Headless subtitle extraction via `yt-dlp` in isolated `uuid4` temporary directories.
- **Tier 4**: Multimodal upload to Google Gemini 2.5 Flash File API for visual presentation analysis.
- **Speech Metrics**: Evaluates Words Per Minute (WPM) and filler word frequencies (`um`, `uh`, `like`, `basically`, `actually`).

### 4. `backend/services/ppt_analyzer.py` & `doc_analyzer.py`
- **Purpose**: Ingests pitch decks (`.pptx`, `.ppt`, `.pdf`) and technical specifications (`.pdf`, `.md`, `.txt`, `.rst`).
- **Features**: Linear slide and table extraction without duplicate runs, structured page-by-page PDF extraction.

### 5. `backend/services/judge_engine.py`
- **Purpose**: Orchestrates AI evaluations using Google Gemini 2.5 Flash.
- **Multi-Judge Consensus**: Dispatches 5 concurrent calls with specialized system personas (VC, CTO, Product Manager, UI/UX Designer, CS Professor) via `asyncio.gather`.
- **Score Normalization**: Averages scores across 6 criteria (Innovation, Technical, Relevance, UI/UX, Impact, Presentation) and parses individual judge verdicts (`[CTO - 8.2/10]`).
- **Markdown Formatting**: Guides the model to output rich text, rendered directly on the frontend.

---

## 📡 API Contract (`POST /analyze`)

### Request (`multipart/form-data`)
- `github_url`: (Optional string) GitHub repository URL or live website URL.
- `video_url`: (Optional string) YouTube demo link.
- `manual_transcript`: (Optional string) Pasted transcript or speaker notes (or browser-extracted text).
- `persona`: (Optional string) `standard`, `consensus`, `vc`, `cto`, `product`, `uiux`, `professor`, or `roast`. Default: `standard`.
- `ppt_file`: (Optional file) `.ppt`, `.pptx`, or `.pdf`.
- `doc_file`: (Optional file) `.pdf`, `.md`, `.txt`, `.markdown`, or `.rst`.

### Response (`application/json`)
```json
{
  "scores": {
    "innovation": 8.5,
    "technical": 9.0,
    "relevance": 8.0,
    "uiux": 7.5,
    "impact": 8.5,
    "presentation": 8.0
  },
  "strengths": [
    "Clean microservices architecture with isolated responsibilities",
    "Effective 4-tier fallback handling YouTube bot protection"
  ],
  "improvements": [
    "Add automated CI integration tests for edge-case payloads",
    "Implement rate-limiting middleware on the /analyze endpoint"
  ],
  "questions": [
    "How does your architecture handle concurrent video downloads under memory constraints?",
    "What is your strategy for scaling the consensus panel to additional personas?"
  ],
  "feedback": "[CTO - 8.8/10] Strong architectural foundations...\n\n[VC - 8.2/10] Compelling market opportunity...",
  "whyWontWin": "Lack of production telemetry and monitoring for user conversion funnels.",
  "win_probability": 78.5,
  "project_roadmap": [
    "Step 1: Set up Redis for shared distributed caching",
    "Step 2: Add OAuth support for evaluating private repositories",
    "Step 3: Integrate webhook alerts for automated judging pipelines"
  ],
  "security_issues": [],
  "ppt_analysis": {
    "is_relevant": true,
    "is_ai_generated": false,
    "comments": "Deck clearly states the problem statement and competitive advantage."
  },
  "video_analysis": {
    "clarity_score": 8,
    "pacing_score": 8,
    "confidence_score": 9,
    "filler_words": "low",
    "comments": "Confident delivery with steady pace and minimal filler words."
  },
  "languages": { "JavaScript": 65000, "Python": 45000 },
  "files_count": 28,
  "estimated_loc": 2750,
  "site_analysis": null,
  "is_github": true,
  "judge_name": "CONSENSUS"
}
```

---

## 🧪 Verification & Test Suite

The test suite covers all core modules:
- `tests/test_consensus_mock.py`: Validates parallel consensus panel execution, score parsing, and fallback behaviors.
- `tests/test_video_analyzer.py`: Validates URL parsing, transcript caching, expiry thresholds, and speech metrics.
- `tests/test_github.py`: Validates BFS limits, language calculations, and secret detection.
- `tests/integration_test_video.py`: End-to-end integration test for YouTube transcription.

Run tests:
```bash
python3 -m unittest discover tests -v
```
