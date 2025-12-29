# AI Hackathon Judge 🤖⚖️

Evaluate your hackathon project locally before the real judges do. Point the app at your repo, deck, and demo video to get instant scores, persona-specific feedback, and a frank "why you won't win" verdict.

<div align="center">
  <img src="screenshots/Submisstion.png" alt="Home Screen" width="800"/>
  <p><em>Try personas like "The VC" or "Roast Master" before demo day.</em></p>
</div>

## ✨ Highlights

- **Multi-judge consensus**: Five AI personas (VC, CTO, Product, UI/UX, Professor) vote in parallel for an aggregated, less-biased score.
- **Bug & security sweeps**: Static checks for secrets, vulnerable dependencies, and risky patterns.
- **Persona Q&A**: Auto-generated judge questions tailored to your stack and pitch.
- **Winning likelihood**: A data-backed prediction of your odds, plus a blunt reason if you are not ready.
- **Video & speech analytics**: Delivery metrics from your demo (pacing, confidence, clarity).
- **Mentor roadmap**: Actionable next steps to move from prototype to production.

## 🎭 Judge Personas

- ⚖️ **Standard**: Balanced, neutral feedback.
- 💸 **The VC**: ROI, market size, moat.
- 🧔 **The CTO**: Code quality, security, architecture.
- 📦 **Product Manager**: Problem-solution fit, UX flow.
- 🎨 **UI/UX Designer**: Visual hierarchy, accessibility, polish.
- 🎓 **The Professor**: Algorithmic rigor and correctness.
- 🔥 **Roast Master**: Brutal but accurate.

## 🗂️ What You Can Analyze

- GitHub repository (code quality, docs, dependency risk)
- Pitch deck / PPTX or PDF
- Demo video (with speech-to-text for delivery insights)

## 🛠️ Tech Stack

- **Frontend**: React + Vite + Tailwind CSS v4
- **Backend**: FastAPI (Python)
- **AI**: Google Gemini 2.5 Flash (`models/gemini-2.5-flash` via `google-generativeai`)
- **Analysis**: PyGithub, speech-to-text for video transcripts
- **Packaging/Deploy**: Docker + Docker Compose; PyInstaller for native builds

## 🚀 Quickstart

### Option A: Docker (recommended)
1) Install Docker and Docker Compose.
2) Create `.env` in the project root:
   ```bash
   GEMINI_API_KEY=your_key_here    # access to models/gemini-2.5-flash required
   GITHUB_TOKEN=your_token_here    # improves repo analysis rate limits
   ```
3) Start everything:
   ```bash
   docker-compose up --build
   ```
4) Open http://localhost:8000 or https://0.0.0.0:8000

### Option B: Manual dev setup

Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Frontend
```bash
cd frontend
npm install
npm run dev
```

### Option C: Standalone executable

- **Linux**: Download `project_judge_linux.zip` from Releases, extract, run `./project_judge`.
- **Windows**: Run `build_windows.bat` to generate `project_judge.exe`, then execute it.

## 🔑 Environment variables

- `GEMINI_API_KEY` (required): Google Gemini 2.5 Flash access.
- `GITHUB_TOKEN` (optional but recommended): Better GitHub API rate limits.
- Optional video transcription keys if you swap providers (see backend/service configs).

## 🧪 Testing

Backend unit tests (from repo root):
```bash
cd backend
pytest
```

Frontend linting:
```bash
cd frontend
npm run lint
```

## 🖼️ Gallery

| Landing & Persona Picker | Detailed Scorecard | Strengths vs Weaknesses |
| :---: | :---: | :---: |
| <img src="screenshots/Submisstion.png" width="410" /> | <img src="screenshots/Detailed_Scorecard.png" width="310" /> | <img src="screenshots/Strengths_Weaknesses.png" width="310" /> |

| Suggested Questions | Video Analysis | AI Final Verdict |
| :---: | :---: | :---: |
| <img src="screenshots/Suggested_Questions.png" width="310" /> | <img src="screenshots/Video_Presentation_Analysis.png" width="310" /> | <img src="screenshots/AI_Verdict_New.png" width="310" /> |

| Why It Won't Win |
| :---: |
| <img src="screenshots/Why_It_Wont_Win.png" width="400"/> |

## 📝 Note

Built to help you stress-test your project before the judges do.
