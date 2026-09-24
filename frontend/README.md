# AI Hackathon Judge - Frontend 🎨

The modern, responsive user interface for the AI Hackathon Judge, built with **React 18+**, **Vite**, and **Tailwind CSS v4**.

---

## 🚀 Key Features

- **💎 Glassmorphic & Modern Styling**: Built with Tailwind CSS v4 featuring translucent backdrops, vibrant gradients, blur filters, and micro-interactions.
- **⚡ Client-Side YouTube Transcript Fetching**: Uses `youtube-transcript` in the browser before submitting to the backend, bypassing cloud datacenter IP blocks (e.g. Render/AWS) cleanly without proxy setup.
- **🗳️ Multi-Judge Consensus HUD**: Visually partitions parallel evaluations from all 5 judges (VC, CTO, Product Manager, UI/UX Designer, Professor) with distinct persona cards, color badges, and individual ratings.
- **📝 Full Markdown Feedback Engine**: Uses `react-markdown` to format judge feedback, technical roadmaps, strengths, and areas for improvement with bold text, inline code snippets, and lists.
- **🌐 Dual Source Inspection View**:
  - **GitHub Codebases**: Visualizes language distribution percentages across languages, total file count, and estimated Lines of Code (LOC).
  - **Live Web Apps**: Displays total page weight (KB), internal route count ("pinpoints"), and detected tech stack tags (React, Next.js, Vue, Tailwind, WordPress, etc.).
- **📊 Real-time Win Probability™ Indicator**: Dynamic, color-coded probability rating (Legendary >70%, Candidate 40-70%, Needs Pivot <40%) reflecting aggregate judge sentiment.
- **📋 Shareable Scorecard**: One-click clipboard copy formatted with emojis, criteria breakdown, and security status ready to paste into Slack, Discord, or pitch decks.
- **🛡️ Security HUD**: Highlights detected API secrets, credentials, or insecure patterns with high-visibility alert callouts.

---

## 🛠️ Tech Stack & Dependencies

- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite`, `@tailwindcss/postcss`)
- **Icons**: Lucide React
- **Rich Text**: `react-markdown`
- **YouTube Client Extractor**: `youtube-transcript`
- **Linter**: ESLint with React Hooks & React Refresh rules

---

## 📦 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`. When running with `npm run dev`, API requests automatically default to `http://localhost:8000`.

### 3. Build for Production
```bash
npm run build
```
Builds optimized production assets into `dist/`. The backend is configured to automatically serve these static files when accessed directly at `http://localhost:8000`.

### 4. Code Linting
```bash
npm run lint
```

---

## 🏗️ Component Architecture

```
frontend/src/
├── App.jsx                     # Root application container, state machine, and API orchestrator
├── main.jsx                    # React DOM entry point
├── index.css                   # Global styles and Tailwind v4 theme configuration
├── App.css                     # Component style overrides and animations
└── components/
    ├── InputForm.jsx           # Submission form for repos, URLs, pitch decks, docs & persona picker
    ├── Scorecard.jsx           # Circular overall score, 6 criteria progress bars, share button
    ├── FeedbackSection.jsx     # AI feedback cards, Markdown parser, LOC stats, roadmap, and Q&A
    └── LoadingScreen.jsx       # Animated loading screen with hackathon facts & status messages
```

### Component Roles & Responsibilities

- **`App.jsx`**: Manages the application lifecycle (`input` → `analyzing` → `results`). Intercepts YouTube URLs to attempt client-side caption extraction via `youtube-transcript`, then dispatches `FormData` to `/analyze`.
- **`InputForm.jsx`**: Validates user inputs. Supports GitHub/Website URLs, YouTube links, manual transcript override, file drag/drop for `.pptx`, `.ppt`, `.pdf`, `.md`, `.txt`, and 8 distinct judge personas.
- **`Scorecard.jsx`**: Displays overall weighted project score with animated gradient ring, 6 rubric criteria ratings, security status badge, and copy-to-clipboard functionality.
- **`FeedbackSection.jsx`**: Renders language distribution bar, codebase/site metrics, Markdown-formatted judge critique (including individual persona cards when in Consensus mode), "Why It Won't Win" reality check, strengths, improvements, mentor roadmap, and likely Q&A questions.
- **`LoadingScreen.jsx`**: Entertaining loader cycling through hackathon wisdom and analysis stages while AI models and web parsers process data.

---

## ⚙️ Environment Configuration

| Variable | Description | Default |
| :--- | :--- | :--- |
| `VITE_API_URL` | Base URL of the backend API. When empty, defaults to same-origin in production, and `http://localhost:8000` in dev. | `""` |
