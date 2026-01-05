from services.github_analyzer import analyze_repo
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
print(f"Token present: {bool(token)}")
if token:
    print(f"Token prefix: {token[:4]}")

url = "https://github.com/Daku3011/AI-Hackathon-Judge"
print(f"Testing URL: {url}")
result = analyze_repo(url)
print("Result:", result)
