import os
import re
import urllib.request
import json
import sys

def get_stars(repo):
    """Fetch star count for a given GitHub repository."""
    url = f"https://api.github.com/repos/{repo}"
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "GitHub-Star-Updater",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data.get("stargazers_count", 0)
    except Exception as e:
        print(f"Error fetching stars for {repo}: {e}", file=sys.stderr)
        return None

def update_readme(dry_run=False):
    """Find placeholders in README.md and update them with current star counts."""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        print(f"Error: {readme_path} not found.", file=sys.stderr)
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex to match <!-- stars:owner/repo --> ... <!-- endstars -->
    pattern = re.compile(r"(<!-- stars:([\w\-\./]+) -->).*?(<!-- endstars -->)", re.DOTALL)
    
    found_any = False
    
    def replacer(match):
        nonlocal found_any
        found_any = True
        prefix = match.group(1)
        repo = match.group(2)
        suffix = match.group(3)
        
        print(f"Fetching stars for {repo}...")
        stars = get_stars(repo)
        
        if stars is not None:
            new_text = f"{prefix} ⭐ {stars} {suffix}"
            if dry_run:
                print(f"  [Dry Run] Would update to: {stars} stars")
                return match.group(0)
            return new_text
        else:
            print(f"  Skipping {repo} due to error.")
            return match.group(0)

    new_content = pattern.sub(replacer, content)
    
    if not found_any:
        print("No star count placeholders found in README.md.")
        return

    if not dry_run:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated successfully.")
    else:
        print("Dry run completed. No changes made to README.md.")

if __name__ == "__main__":
    is_dry_run = "--dry-run" in sys.argv
    update_readme(dry_run=is_dry_run)
