@echo off
echo Checking Frontend Build...
echo Building frontend...
cd frontend
call npm install
call npm run build
cd ..


echo Cleaning previous build...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo Running PyInstaller...
pyinstaller project_judge.spec --clean --noconfirm

if exist "dist\project_judge.exe" (
    echo Build successful! Executable found at dist\project_judge.exe
) else (
    echo Build failed.
    pause
    exit /b 1
)
pause
