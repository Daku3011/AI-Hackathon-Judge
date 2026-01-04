# Release Notes v2.0.0 - The "Consensus & Vision" Update 🚀

This is a **major release** introducing parallel multi-judge evaluation, native video vision capabilities, and the upgrade to the Gemini 2.5 Flash architecture.

## 🌟 New Features

-   **🤖 Multi-Judge Consensus Panel**: 
    -   Why rely on one opinion? The system now spins up **5 parallel AI Personas** (VC, CTO, Product Manager, UI/UX Designer, Professor).
    -   Scores are mathematically aggregated to reduce bias.
    -   Receive diverse feedback: The VC asks about money, the CTO checks your code structure.

-   **🧠 Powered by Gemini 2.5 Flash**:
    -   The engine has been upgraded to target the `gemini-2.5-flash` model family.
    -   Improved reasoning capabilities for "Why you won't win" predictions.

-   **👁️ 3-Layer Video Analysis Engine**:
    -   We engineered a robust fallback system to ensure you *always* get a result:
        1.  **Fast Track**: Tries the standard YouTube Transcript API.
        2.  **Stealth Track**: Uses `yt-dlp` with browser spoofing to fetch subtitles if the API is blocked.
        3.  **Vision Track**: Downloads the video and uploads it to Gemini for native **Multimodal Analysis** (detects visual bugs, presentation confidence, and audio pacing).

-   **📘 Viva & Defense Guide**:
    -   Added `docs/PROJECT_VIVA_GUIDE.md`: A cheat sheet to answer "How does your project work?" during your final evaluation.

## 🛠️ Improvements & Polish

-   **Smart Networking**: Added modern User-Agent spoofing to `yt-dlp` to bypass "Sign in to verify you are not a bot" errors.
-   **Codebase Refactor**: 
    -   Cleaned up `main.py` and `services/` with professional docstrings and organized imports.
    -   Removed unused debug scripts from production builds.
-   **UI Updates**:
    -   Polished Loading Screen with accurate fun facts.
    -   Removed generic placeholders.

## 🐛 Bug Fixes

-   Fixed `404 NOT_FOUND` errors by ensuring API model aliases match the available 2025/2026 usage tier.
-   Fixed video download failures on cloud IPs (Render) by improving header negotiation.
