# How to Build Project Judge

This project can be built as a standalone executable for both Linux and Windows.

## Prerequisites

1.  **Python 3.10+** installed.
2.  **Node.js 18+** installed.
3.  Install strict dependencies:
    ```bash
    pip install -r backend/requirements.txt
    pip install pyinstaller
    ```

## Building on Linux

1.  Open a terminal in the project root.
2.  Run the build script:
    ```bash
    python3 build.py
    ```
3.  The executable will be created at `dist/project_judge/project_judge`.
4.  Run it:
    ```bash
    ./dist/project_judge/project_judge
    ```

## Building on Windows

1.  Open Command Prompt or PowerShell in the project root.
2.  Run the Windows build batch file:
    ```cmd
    build_windows.bat
    ```
3.  The executable will be created at `dist\project_judge\project_judge.exe`.
4.  Run it by double-clicking the .exe or running it from the command line.

## Notes

-   **Frontend Assets**: The build process automatically builds the React frontend and bundles it into the executable.
-   **API Keys**: The executable needs environment variables to function correctly.
    -   Create a `.env` file next to the executable (e.g., in `dist/project_judge/`) with your keys:
        ```bash
        GEMINI_API_KEY=your_gemini_key
        GITHUB_TOKEN=your_github_personal_access_token
        ```
    -   `GEMINI_API_KEY` is **required** for AI analysis.
    -   `GITHUB_TOKEN` is **highly recommended** to avoid GitHub API rate limits and to allow analysis of private repositories (if permissions allow).
-   **Errors**: If the build fails with "Directory not empty", try deleting the `build` and `dist` folders manually and running the script again.
