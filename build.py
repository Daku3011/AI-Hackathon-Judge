import os
import subprocess
import shutil
import sys
import time
import argparse

def run_command(command, check=True):
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True)
    if check and result.returncode != 0:
        print(f"Error executing command: {command}")
        sys.exit(1)

def get_latest_mtime(directory):
    latest_mtime = 0
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(path)
                if mtime > latest_mtime:
                    latest_mtime = mtime
            except OSError:
                pass
    return latest_mtime

def should_build_frontend(frontend_dir):
    dist_dir = os.path.join(frontend_dir, "dist")
    src_dir = os.path.join(frontend_dir, "src")
    package_json = os.path.join(frontend_dir, "package.json")
    
    if not os.path.exists(dist_dir):
        return True
        
    dist_mtime = os.path.getmtime(dist_dir)
    src_mtime = get_latest_mtime(src_dir)
    pkg_mtime = os.path.getmtime(package_json) if os.path.exists(package_json) else 0
    
    # If source or config is newer than dist, rebuild
    if src_mtime > dist_mtime or pkg_mtime > dist_mtime:
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description="Build the project.")
    parser.add_argument("--clean", action="store_true", help="Clean build directories before building.")
    args = parser.parse_args()

    # Define paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(project_root, "frontend")
    dist_dir = os.path.join(project_root, "dist")
    build_work_dir = os.path.join(project_root, "build")

    if args.clean:
        print("Cleaning build directories...")
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        if os.path.exists(build_work_dir):
            shutil.rmtree(build_work_dir)
        frontend_dist = os.path.join(frontend_dir, "dist")
        if os.path.exists(frontend_dist):
            shutil.rmtree(frontend_dist)

    # 1. Frontend Dependencies
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print("Installing frontend dependencies...")
        run_command(f"cd {frontend_dir} && npm install")
    else:
        print("Skipping npm install (node_modules exists).")

    # 2. Frontend Build
    if args.clean or should_build_frontend(frontend_dir):
        print("Building frontend...")
        run_command(f"cd {frontend_dir} && npm run build")
    else:
        print("Skipping frontend build (dist is up to date).")
    
    # 3. PyInstaller
    print("Running PyInstaller...")
    
    # Robustly clean output directory to prevent "Directory not empty" errors
    output_dir = os.path.join(dist_dir, "project_judge")
    if os.path.exists(output_dir):
        print(f"Cleaning output directory: {output_dir}")
        import platform
        if platform.system() != "Windows":
             run_command(f"rm -rf {output_dir}")
        else:
            try:
                shutil.rmtree(output_dir)
            except OSError as e:
                print(f"Warning: Could not remove {output_dir}: {e}")
    
    # Only use --clean if requested or if we are doing a fresh build
    pyinstaller_args = "--noconfirm"
    if args.clean:
        pyinstaller_args += " --clean"

    run_command(f"pyinstaller project_judge.spec {pyinstaller_args}")
    
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
