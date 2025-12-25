import os
import subprocess
import shutil
import sys

def run_command(command):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Error executing command: {command}")
        sys.exit(1)

def main():
    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    backend_dir = os.path.join(project_root, "backend")
    dist_dir = os.path.join(project_root, "dist")
    
    # Check if frontend is built
    frontend_dist = os.path.join(frontend_dir, "dist")
    if not os.path.exists(frontend_dist):
        print("Frontend/dist not found. Building frontend...")
        run_command(f"cd {frontend_dir} && npm install && npm run build")
    
    # Run PyInstaller
    print("Running PyInstaller...")
    
    # Clean previous build to prevent "Directory not empty" errors
    if os.path.exists(dist_dir):
        print(f"Cleaning existing dist directory: {dist_dir}")
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"WARNING: Failed to clean dist directory: {e}")
            # Try to continue anyway, or exit? Best to continue and let PyInstaller try too.
            
    build_work_dir = os.path.join(project_root, "build")
    if os.path.exists(build_work_dir):
         try:
            shutil.rmtree(build_work_dir)
         except:
            pass

    # We use a spec file for configuration
    run_command(f"pyinstaller project_judge.spec --clean --noconfirm")
    
    # Check output
    executable_path = os.path.join(dist_dir, "project_judge")
    if os.path.exists(executable_path):
        print(f"Build successful! Executable found at: {executable_path}")
        print("To run: ./dist/project_judge")
    else:
        print("Build failed: Executable not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
