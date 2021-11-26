import os

import toml
from pkg_resources import parse_version

# Exception: The ref refs/pull/55/merge is not valid.


def bump_version_from_ref() -> None:
    """Bumps the version property inside pyproject.toml."""

    ref = os.environ.get("GITHUB_REF", "refs/is/invalid")

    if not ref.startswith("refs/tags/v"):
        print(
            f"The given ref ({ref}) didn't match the requirements for a version increment."
        )
        return

    ref_suffix = ref.split("/")[-1]
    project_file = "pyproject.toml"
    project = toml.load(project_file)

    next_version = str(ref_suffix[1:])
    current_version = project["tool"]["poetry"]["version"]
    is_next_version = parse_version(next_version) > parse_version(current_version)

    if not is_next_version:
        print(
            f"✨ No version bump needed. Next version was {next_version} and current version is {current_version}."
        )
        return

    print(f"⭐ Next version will be: {next_version}")
    project["tool"]["poetry"]["version"] = next_version

    with open(project_file, "w") as f:
        toml.dump(project, f)


if __name__ == "__main__":
    bump_version_from_ref()
