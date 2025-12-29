import os
import re
from github import Github
from urllib.parse import urlparse

def analyze_repo(repo_url: str):
    """
    Analyzes a GitHub repository to extract README content and file structure.
    Also performs basic static analysis for security and code quality.
    """
    try:
        # Parse URL to get "owner/repo"
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
             return {"summary": "Invalid GitHub URL", "files_count": 0}
        
        owner, repo_name = path_parts[0], path_parts[1]
        full_name = f"{owner}/{repo_name}"

        # Initialize GitHub API
        token = os.getenv("GITHUB_TOKEN")
        print(f"DEBUG: Analyzing repo: {full_name}")
        print(f"DEBUG: Token loaded: {bool(token)}")
        if token:
            print(f"DEBUG: Token prefix: {token[:4]}...")
            
        g = Github(token) if token else Github()
        
        repo = g.get_repo(full_name)
        
        # 1. Get README
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode("utf-8")
        except:
            readme_content = "No README.md found."

        # 2. Get File Structure & Key Files
        files_list = []
        if readme_content and "No README.md found" not in readme_content:
            files_list.append("README.md")
            
        dependency_files = {} # content of package.json, requirements.txt, etc.
        code_samples = {} # content of main.py, App.jsx, etc.
        
        target_configs = ["package.json", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "composer.json", "Pipfile", "pyproject.toml"]
        target_code = ["main.py", "app.py", "index.js", "App.jsx", "server.js", "src/App.jsx", "src/main.rs", "manage.py"]
        
        # Security & Privacy Patterns
        security_patterns = {
            "AWS Key": r"AKIA[0-9A-Z]{16}",
            "OpenAI Key": r"sk-[a-zA-Z0-9]{20}T3BlbkFJ",
            "Generic Secret": r"(?i)(password|secret|api_key|access_token)\s*[:=]\s*['\"][a-zA-Z0-9]{10,}['\"]"
        }
        
        detected_issues = []
        boilerplate_score = 0
        total_files_scanned = 0

        try:
            contents = repo.get_contents("")
            # BFS to find files (limit depth to 2 to save requests)
            queue = contents if isinstance(contents, list) else [contents]
            processed_count = 0
            
            while queue and processed_count < 50: # Limit to 50 files processed
                file_content = queue.pop(0)
                processed_count += 1
                
                if file_content.type == "dir":
                    try:
                        # Skip huge generic folders
                        if file_content.name in ["node_modules", "venv", ".git", "dist", "build"]:
                            continue
                        queue.extend(repo.get_contents(file_content.path))
                    except: pass
                else:
                    total_files_scanned += 1
                    if file_content.path != "README.md": # Avoid duplicates
                        files_list.append(file_content.path)
                    
                    # Fetch Content if interesting
                    content_str = ""
                    try:
                        # Only fetch if it's smaller than 100KB to ensure speed
                        if file_content.size < 100000:
                            content_str = file_content.decoded_content.decode("utf-8")
                    except: pass

                    # Security Scan
                    if content_str:
                        for pattern_name, pattern in security_patterns.items():
                            if re.search(pattern, content_str):
                                detected_issues.append(f"Security Alert: Potential {pattern_name} found in {file_content.path}")

                        # Code Quality / Boilerplate Check
                        if "react" in content_str and "create-react-app" in content_str:
                            boilerplate_score += 1
                        
                        if file_content.name in target_configs:
                            dependency_files[file_content.name] = content_str
                        elif file_content.name in target_code:
                            code_samples[file_content.path] = "\n".join(content_str.splitlines()[:100])
                    
        except:
            files_list.append("Error fetching file list")

        # 3. Construct Summary for LLM
        summary = f"Repository: {full_name}\n"
        summary += f"Description: {repo.description}\n"
        summary += f"Stars: {repo.stargazers_count}\n"
        summary += f"Primary Language: {repo.language}\n\n"
        
        summary += f"--- SECURITY REPORT ---\n"
        if detected_issues:
            summary += "\n".join(detected_issues) + "\n"
        else:
            summary += "No critical API key leaks detected.\n"
        summary += "\n"

        summary += f"--- FILE STRUCTURE (Partial) ---\n{', '.join(files_list[:60])}\n\n"
        
        summary += f"--- DEPENDENCIES ---\n"
        for fname, content in dependency_files.items():
            summary += f"[{fname}]\n{content[:500]}\n\n"
            
        summary += f"--- CODE SAMPLES ---\n"
        for fname, content in code_samples.items():
            summary += f"[{fname}]\n{content}\n\n"

        summary += f"--- README.md ---\n{readme_content[:3000]}\n"
        
        
        print(f"DEBUG: Found {len(files_list)} files.")
        
        return {
            "summary": summary,
            "files_count": len(files_list),
            "languages": repo.language,
            "security_issues": detected_issues
        }

    except Exception as e:
        print(f"GitHub Error: {e}")
        error_msg = str(e)
        if "404" in error_msg:
             return {
                "summary": "GitHub Error 404: Repository not found. It might be private or the URL is incorrect. (Or API rate limit exceeded)",
                "files_count": 0,
                "languages": "Unknown",
                "security_issues": []
            }
        elif "403" in error_msg:
             return {
                "summary": f"GitHub Error 403: Rate limit exceeded or access denied. Please try again later.",
                "files_count": 0,
                "languages": "Unknown",
                 "security_issues": []
            }
            
        return {
            "summary": f"Failed to analyze GitHub repo: {str(e)}",
            "files_count": 0,
            "languages": "Unknown",
            "security_issues": []
        }

