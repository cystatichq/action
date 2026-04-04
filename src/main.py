import os
import json
import requests

def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise Exception(f"Missing env var: {name}")
    return value

github_token = get_env("INPUT_GITHUB_TOKEN")
cystatic_api_key = get_env("INPUT_CYSTATIC_API_KEY")
event_path = get_env("GITHUB_EVENT_PATH")
api_url = "https://cystatic-core.onrender.com"

with open(event_path, "r") as f:
    event = json.load(f)

pr = event["pull_request"]
repo = event["repository"]["full_name"]
pr_number = pr["number"]

diff_url = f"https://github.com/{repo}/pull/{pr_number}.diff"

headers = {
    "Authorization": f"Bearer {github_token}",
    "Accept": "application/vnd.github.v3.diff"
}

diff = requests.get(diff_url, headers=headers).text

# Forward ONLY to Cystatic API
payload = {
    "repo": repo,
    "pr_number": pr_number,
    # "diff_url": diff_url,
    # "diff": diff
}

response = requests.post(
    f"{api_url}/v1/analyze-pr",
    headers={
        "x-api-key": cystatic_api_key,
        "Content-Type": "application/json"
    },
    json=payload,
    timeout=120
)

try:
    response.raise_for_status()
    data = response.json()
except requests.exceptions.HTTPError as e:
    raise Exception(
        f"[Cystatic API] HTTP error: {e.response.status_code} - {e.response.text}"
    )