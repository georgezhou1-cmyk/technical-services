"""Read the first page of tags from a public GitHub repo. Python 3.9+."""
import argparse
import json
import re
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FIXTURE = [
    {"name": "demo-v2", "commit": {"sha": "a" * 40}},
    {"name": "demo-v1", "commit": {"sha": "b" * 40}},
]


def parse_tags(payload):
    if not isinstance(payload, list):
        raise ValueError("Expected a JSON array of tags.")
    result = []
    for i, tag in enumerate(payload, start=1):
        if not isinstance(tag, dict) or not isinstance(tag.get("commit"), dict):
            raise ValueError(f"Tag {i} is missing its commit object.")
        name, sha = tag.get("name"), tag["commit"].get("sha")
        if not isinstance(name, str) or not name or not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
            raise ValueError(f"Tag {i} needs a name and a 40-character commit SHA.")
        result.append((name, sha))
    return result


def load_tags(repo="python/cpython", limit=2):
    if not re.fullmatch(r"[a-zA-Z0-9-]+/[a-zA-Z0-9_.-]+", repo) or repo.split("/")[1] in {".", ".."}:
        raise ValueError("Use a public repository in OWNER/REPO form.")
    if not 1 <= limit <= 100:
        raise ValueError("The page size must be between 1 and 100.")
    request = Request(f"https://api.github.com/repos/{repo}/tags?per_page={limit}",
                      headers={"Accept": "application/vnd.github+json", "User-Agent": "technical-services-demo"})
    with urlopen(request, timeout=12) as response:
        return parse_tags(json.load(response))


def http_message(error):
    headers = error.headers or {}
    if error.code == 404:
        hint = "Check the spelling and public visibility of the repository."
    elif error.code == 429 or (error.code == 403 and headers.get("X-RateLimit-Remaining") == "0"):
        hint = "Rate limit reached. Retry later or use --offline."
        if headers.get("X-RateLimit-Reset"):
            hint += f" Reset time (Unix seconds): {headers['X-RateLimit-Reset']}."
    else:
        hint = "Check the server response or run the offline example."
    return f"HTTP {error.code}. {hint} Request ID: {headers.get('X-GitHub-Request-Id', 'unavailable')}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="read two fictional tags without network access")
    parser.add_argument("--repo", default="python/cpython")
    parser.add_argument("--limit", type=int, choices=range(1, 101), metavar="1..100", default=2)
    args = parser.parse_args()
    try:
        tags = parse_tags(FIXTURE[:args.limit]) if args.offline else load_tags(args.repo, args.limit)
    except HTTPError as exc:
        parser.exit(2, http_message(exc) + "\n")
    except (URLError, OSError, HTTPException, ValueError) as exc:
        parser.exit(2, f"Unable to read tags: {exc}\n")
    if not tags:
        print("The repository has no published tags.")
    for name, sha in tags:
        print(f"{name}\t{sha[:12]}")


if __name__ == "__main__":
    main()
