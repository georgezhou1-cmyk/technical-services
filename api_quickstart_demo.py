"""Read two GitHub tag records from a public repository. Python 3.9+."""
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def load_tags():
    req = Request("https://api.github.com/repos/python/cpython/tags?per_page=2",
                  headers={"Accept": "application/vnd.github+json", "User-Agent": "technical-services-demo"})
    try:
        with urlopen(req, timeout=12) as response:
            tags = json.load(response)
    except HTTPError as error:
        print("HTTP status:", error.code)
        print("Request ID:", error.headers.get("X-GitHub-Request-Id", "unavailable"))
        raise
    return [(tag["name"], tag["commit"]["sha"]) for tag in tags]


if __name__ == "__main__":
    for name, sha in load_tags():
        print(f"{name}\t{sha[:12]}")
