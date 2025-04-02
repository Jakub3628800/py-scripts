"""Create commit on github using github API.

1. Create repository on GitHub
2. edit GH_REPO = "repository123"
3. create initial commit in the repo (you can use create_new_ref function)
4. create token for github api that has permissions to commit to this repository
5. python make_commit.py --message "This is my commit message"
"""

import requests
import argparse
import os

# Replace hardcoded constants with environment variables
GH_USERNAME = os.environ.get("GH_USERNAME", "Jakub3628800")
GH_REPO = os.environ.get("GH_REPO", "entroppy")
MAIN_BRANCH = os.environ.get("MAIN_BRANCH", "master")  # Default to "master" if not set
GH_TOKEN = os.environ.get("GH_TOKEN")


auth_header = {
    "Authorization": f"token {GH_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
    "accept": "application/vnd.github+json",
}

base_url = f"https://api.github.com/repos/{GH_USERNAME}/{GH_REPO}"


def make_get_request(path: str) -> dict:
    return requests.get(url=f"{base_url}/{path}", headers=auth_header).json()


def make_post_request(path: str, post_data: dict) -> dict:
    return requests.post(
        f"{base_url}/{path}", headers=auth_header, json=post_data
    ).json()


def get_latest_commit_sha() -> str:
    """Get SHA of latest commit in main branch."""
    r = make_get_request(path=f"branches/{MAIN_BRANCH}")
    return r["commit"]["sha"]


def get_latest_tree_sha() -> str:
    """Get SHA of latest tree in main branch."""
    r = make_get_request(path=f"branches/{MAIN_BRANCH}")
    return r["commit"]["commit"]["tree"]["sha"]


def create_new_tree(base_tree_sha: str) -> str:
    """Create a new tree."""
    post_data = {
        "base_tree": base_tree_sha,
        "tree": [
            {
                "path": "README.md",
                "mode": "100644",
                "type": "blob",
                "content": "hello hello",
            }
        ],
    }
    r = make_post_request(path="git/trees", post_data=post_data)
    return r["sha"]


def create_new_commit(parent_commit_sha: str, tree_sha: str, message: str) -> str:
    """Create a new commit."""
    post_data = {
        "message": message,
        "author": {
            "name": "Jakub Test",
            "email": "jakubtest@github.com",
        },  # ,"date": f"{2008-07-09T16:13:30}+12
        "parents": [parent_commit_sha],
        "tree": tree_sha,
    }
    r = make_post_request(path="git/commits", post_data=post_data)
    return r["sha"]


def create_new_ref(ref_name: str, commit_sha: str) -> dict:
    """Create a new ref."""
    post_data = {"ref": "refs/heads/master", "sha": commit_sha}
    r = make_post_request(path="git/refs", post_data=post_data)
    return r


def update_ref(ref_name: str, commit_sha: str) -> dict:
    post_data = {"ref": "refs/heads/master", "sha": commit_sha}

    return requests.put(
        f"{base_url}/git/refs/heads/{ref_name}", headers=auth_header, json=post_data
    ).json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Commit message.")
    parser.add_argument(
        "--message", type=str, help="The commit message", default="This is a commit"
    )
    commit_message = parser.parse_args().message

    commit_sha = get_latest_commit_sha()
    tree_sha = get_latest_tree_sha()

    new_tree_sha = create_new_tree(base_tree_sha=tree_sha)
    new_commit_sha = create_new_commit(
        parent_commit_sha=commit_sha, tree_sha=new_tree_sha, message=commit_message
    )

    response = update_ref(ref_name="master", commit_sha=new_commit_sha)
    print(response)
    raise SystemExit(0)
