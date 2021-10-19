import toml
import sys

from pkg_resources import parse_version


def bump_version(next_version: str, current_branch: str):
    """Bumps the version property inside pyproject.toml.

    Args:
        next_version (str): The next version in the sequence.
    """
    project_file = "pyproject.toml"
    project = toml.load(project_file)

    if next_version.startswith("v"):
        next_version = next_version[1:]

    is_main = current_branch == "main"
    current_version = project["tool"]["poetry"]["version"]
    is_next_version = parse_version(next_version) > parse_version(current_version)

    if is_next_version and is_main:
        print(f"⭐ Next version will be: {next_version}")
        project["tool"]["poetry"]["version"] = next_version
        with open(project_file, "w") as f:
            toml.dump(project, f)
    else:
        print(
            f"✨ No version bump needed. Next version was {next_version} and the current branch is {current_branch}"
        )


if __name__ == "__main__":
    bump_version(next_version=sys.argv[1], current_branch=sys.argv[2])
