import os
from github import Github
from urllib.parse import urlparse

def analyze_repo(repo_url: str):
    """
    Analyzes a GitHub repository to extract README content and file structure.
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
        # If GITHUB_TOKEN is not in env, this runs anonymously (low rate limit: 60/hr)
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
        
        target_configs = ["package.json", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "composer.json"]
        target_code = ["main.py", "app.py", "index.js", "App.jsx", "server.js", "src/App.jsx", "src/main.rs"]

        try:
            contents = repo.get_contents("")
            # BFS to find files (limit depth to 2 to save requests)
            queue = contents if isinstance(contents, list) else [contents]
            processed_count = 0
            
            while queue and processed_count < 30: # Limit to 30 files processed
                file_content = queue.pop(0)
                processed_count += 1
                
                if file_content.type == "dir":
                    try:
                        queue.extend(repo.get_contents(file_content.path))
                    except: pass
                else:
                    if file_content.path != "README.md": # Avoid duplicates
                        files_list.append(file_content.path)
                    
                    # Fetch Content if interesting
                    if file_content.name in target_configs:
                        try:
                            dependency_files[file_content.name] = file_content.decoded_content.decode("utf-8")
                        except: pass
                    elif file_content.name in target_code or file_content.path in target_code:
                         try:
                            # Only get first 100 lines of code
                            full_code = file_content.decoded_content.decode("utf-8")
                            code_samples[file_content.path] = "\n".join(full_code.splitlines()[:100])
                         except: pass

        except:
             files_list.append("Error fetching file list")

        # 3. Construct Summary for LLM
        summary = f"Repository: {full_name}\n"
        summary += f"Description: {repo.description}\n"
        summary += f"Stars: {repo.stargazers_count}\n"
        summary += f"Primary Language: {repo.language}\n\n"
        
        summary += f"--- FILE STRUCTURE (Partial) ---\n{', '.join(files_list[:50])}\n\n"
        
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
            "languages": repo.language
        }

    except Exception as e:
        print(f"GitHub Error: {e}")
        error_msg = str(e)
        if "404" in error_msg:
             return {
                "summary": "GitHub Error 404: Repository not found. It might be private or the URL is incorrect. (Or API rate limit exceeded)",
                "files_count": 0,
                "languages": "Unknown"
            }
        elif "403" in error_msg:
             return {
                "summary": f"GitHub Error 403: Rate limit exceeded or access denied. Please try again later.",
                "files_count": 0,
                "languages": "Unknown"
            }
            
        return {
            "summary": f"Failed to analyze GitHub repo: {str(e)}",
            "files_count": 0,
            "languages": "Unknown"
        }
