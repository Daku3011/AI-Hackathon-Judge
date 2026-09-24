# Build & Compilation Instructions 🏗️

This guide covers building the **AI Hackathon Judge** as a standalone executable (for Linux and Windows) and as a production-ready containerized Docker image.

---

## 📋 Prerequisites

1. **Python**: Version **3.10+** installed and available in your `PATH`.
2. **Node.js**: Version **18+** or **20+** with `npm` installed.
3. **Core Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   pip install pyinstaller
   ```

---

## 🐧 Building Standalone Executable on Linux

The project includes an automated build script (`build.py`) that compiles the React frontend, bundles it with the FastAPI backend, and invokes PyInstaller using `project_judge.spec`.

### Steps:
1. Open a terminal in the project root directory.
2. Run the build orchestrator:
   ```bash
   python3 build.py
   ```
   *What this script does:*
   - Changes into `frontend/` and runs `npm run build` to generate static production assets in `frontend/dist`.
   - Copies `frontend/dist` into the PyInstaller bundling folder.
   - Executes PyInstaller using `project_judge.spec`.
3. The resulting standalone binary folder will be located at:
   ```bash
   dist/project_judge/project_judge
   ```
4. Create a `.env` file in `dist/project_judge/` with your credentials:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GITHUB_TOKEN=your_github_token_here
   ```
5. Launch the executable:
   ```bash
   ./dist/project_judge/project_judge
   ```
   Open your browser at `http://localhost:8000`.

---

## 🪟 Building Standalone Executable on Windows

1. Open Command Prompt or PowerShell as Administrator in the project root directory.
2. Run the Windows batch script:
   ```cmd
   build_windows.bat
   ```
3. The executable and bundled internal dependencies will be located at:
   ```
   dist\project_judge\project_judge.exe
   ```
4. Place a `.env` file in `dist\project_judge\` with `GEMINI_API_KEY`.
5. Run `project_judge.exe` by double-clicking or from the terminal.

---

## 🐳 Building with Docker (Multi-Stage Container)

The project includes an optimized multi-stage `Dockerfile`:
- **Stage 1 (Node 20 Alpine)**: Installs frontend dependencies and compiles the React application into `/frontend_dist`.
- **Stage 2 (Python 3.10 Slim)**: Installs system utilities (`curl`, `ffmpeg` for video manipulation), installs Python requirements, copies the backend code, and mounts the compiled frontend distribution.

### Build and Run with Docker Compose:
```bash
# 1. Create .env in root
echo "GEMINI_API_KEY=your_key_here" >> .env
echo "GITHUB_TOKEN=your_token_here" >> .env

# 2. Build and start
docker-compose up --build
```

### Manual Docker Build:
```bash
docker build -t ai-hackathon-judge .
docker run -p 8000:8000 --env-file .env ai-hackathon-judge
```

---

## 🔍 How Frontend Static Asset Bundling Works

`backend/main.py` detects its execution environment dynamically:

1. **PyInstaller Frozen Mode**: If `sys.frozen == True`, it serves assets from `_internal/frontend/dist` or the executable's directory.
2. **Docker Production Mode**: If `/frontend_dist` exists (from multi-stage Docker build), it mounts static files from that path.
3. **Local Development Mode**: Falls back to `frontend/dist` relative to the backend root directory.

All unmatched non-API routes are caught by the `{catchall:path}` fallback handler and served `index.html` to support client-side SPA routing.

---

## ⚠️ Troubleshooting Build Failures

1. **"Directory not empty" or Permission Error**:
   - Manually remove the `build/` and `dist/` folders from the root directory and re-run `python3 build.py`.
2. **Missing Frontend Assets**:
   - Ensure you ran `npm run build` in `frontend/` prior to running PyInstaller directly without `build.py`.
3. **Video Analysis / yt-dlp Subprocess Issues in PyInstaller**:
   - Ensure `ffmpeg` is available on the system PATH if native video downloading or audio extraction is required.
