import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

def analyze_site(url: str):
    """
    Analyzes a general website URL to extract metadata, tech stack, and structure.
    """
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Basic Metadata
        title = soup.title.string if soup.title else "No title found"
        description = ""
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            description = meta_desc.get("content", "")
            
        # 2. Asset Counting
        scripts = soup.find_all('script')
        styles = soup.find_all('link', rel='stylesheet')
        images = soup.find_all('img')
        
        # 3. Link Mapping (Pinpoints)
        domain = urlparse(url).netloc
        links = soup.find_all('a', href=True)
        internal_links = set()
        external_links = set()
        
        for link in links:
            href = link['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == domain:
                # Clean up fragment/query
                clean_url = full_url.split('#')[0].split('?')[0].rstrip('/')
                if clean_url:
                    internal_links.add(clean_url)
            else:
                external_links.add(full_url)

        # 4. Tech Stack Detection
        tech_stack = []
        html_content = response.text.lower()
        
        tech_indicators = {
            "React": ["react", "react-dom", "_next/static"],
            "Vue": ["vue", "v-per"],
            "Angular": ["ng-version", "ng-app"],
            "WordPress": ["wp-content", "wp-includes"],
            "Tailwind": ["tailwind"],
            "Bootstrap": ["bootstrap"],
            "jQuery": ["jquery"],
            "Google Analytics": ["google-analytics.com", "gtag"],
            "Next.js": ["_next", "__NEXT_DATA__"]
        }
        
        for tech, indicators in tech_indicators.items():
            if any(ind in html_content for ind in indicators):
                tech_stack.append(tech)

        # 5. Size Estimation
        page_size_kb = len(response.content) / 1024
        
        summary = f"Site: {url}\n"
        summary += f"Title: {title}\n"
        summary += f"Description: {description}\n"
        summary += f"Page Size: {page_size_kb:.2f} KB\n"
        summary += f"Assets: {len(scripts)} scripts, {len(styles)} styles, {len(images)} images\n"
        summary += f"Internal Routes Found: {len(internal_links)}\n"
        summary += f"Tech Stack Detected: {', '.join(tech_stack) if tech_stack else 'Unknown'}\n"
        
        if internal_links:
            summary += "\n--- DETECTED ROUTES ---\n"
            summary += "\n".join(list(internal_links)[:20]) # Limit to 20 routes
            if len(internal_links) > 20:
                summary += f"\n... and {len(internal_links) - 20} more"

        return {
            "summary": summary,
            "title": title,
            "description": description,
            "tech_stack": tech_stack,
            "routes_count": len(internal_links),
            "assets": {
                "scripts": len(scripts),
                "styles": len(styles),
                "images": len(images)
            },
            "page_size_kb": page_size_kb
        }

    except Exception as e:
        print(f"Site Analysis Error: {e}")
        return {
            "summary": f"Failed to analyze site: {str(e)}",
            "error": str(e)
        }
