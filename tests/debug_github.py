import os
from dotenv import load_dotenv
from services.github_analyzer import analyze_repo

load_dotenv()

repo_url = "https://github.com/Daku3011/AI-Hackathon-Judge"
print(f"Testing URL: {repo_url}")

# Ensure token is loaded
token = os.getenv("GITHUB_TOKEN")
print(f"Token loaded: {'Yes' if token else 'No'} (Length: {len(token) if token else 0})")

result = analyze_repo(repo_url)
print("--- Result ---")
print(f"Files Count: {result.get('files_count')}")
print(f"Summary Start: {result.get('summary')[:100]}")
