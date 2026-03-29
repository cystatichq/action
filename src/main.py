import os
import json
import requests


print("ENV KEYS:", list(os.environ.keys())) # Debugging line to check available environment variables

def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise Exception(f"Missing env var: {name}")
    return value

github_token = get_env("INPUT_GITHUB_TOKEN")
cystatic_api_key = get_env("INPUT_CYSTATIC_API_KEY")
event_path = os.getenv("GITHUB_EVENT_PATH")
api_url = "https://cystatic-core.onrender.com"

with open(event_path, "r") as f:
    event = json.load(f)

pr = event["pull_request"]
repo = event["repository"]["full_name"]
pr_number = pr["number"]


# Get PR diff (source of truth)
diff_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github.v3.diff"
}

diff = requests.get(diff_url, headers=headers).text

# Forward ONLY to Cystatic API
payload = {
    "repo": repo,
    "pr_number": pr_number,
    "diff_url": diff_url,
    "diff": diff
}


response = requests.post(
    api_url+"/v1/analyze-pr",
    headers={
        "Authorization": f"Bearer {cystatic_api_key}",
        "Content-Type": "application/json"
    },
    json=payload
)

# No commenting, no formatting, no side effects
print(response.text)