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
        g = Github(token) if token else Github()
        
        repo = g.get_repo(full_name)
        
        # 1. Get README
        readme_content = ""
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode("utf-8")
        except:
            readme_content = "No README.md found."

        # 2. Get File Structure (Root only to avoid hitting limits)
        files_list = []
        try:
            contents = repo.get_contents("")
            for content_file in contents:
                files_list.append(content_file.name)
        except:
             files_list = ["Error fetching file list"]

        # 3. Construct Summary for LLM
        summary = f"Repository: {full_name}\n"
        summary += f"Description: {repo.description}\n"
        summary += f"Stars: {repo.stargazers_count}\n"
        summary += f"Primary Language: {repo.language}\n\n"
        summary += f"--- FILES IN ROOT ---\n{', '.join(files_list)}\n\n"
        summary += f"--- README.md ---\n{readme_content}\n"
        
        return {
            "summary": summary,
            "files_count": len(files_list),
            "languages": repo.language
        }

    except Exception as e:
        print(f"GitHub Error: {e}")
        return {
            "summary": f"Failed to analyze GitHub repo: {str(e)}",
            "files_count": 0,
            "languages": "Unknown"
        }
