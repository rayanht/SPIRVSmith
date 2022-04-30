import os

import git


def get_spirvsmith_version() -> str:
    if os.getenv("CI"):
        return "CI"
    repo: git.Repo = git.Repo(os.getcwd())
    tags: list[git.TagReference] = sorted(
        filter(None, repo.tags), key=lambda t: t.commit.committed_datetime
    )
    return tags[-1].name
