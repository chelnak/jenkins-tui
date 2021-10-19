import toml
import sys
import os
from pkg_resources import parse_version


def bump_version_from_ref():
    """Bumps the version property inside pyproject.toml."""

    ref = os.environ.get("GITHUB_REF", "v0.0.0")
    ref_suffix = ref.split("/")[-1]
    if "tags" not in ref or not ref_suffix.startswith("v"):
        raise Exception(f"The ref {ref} is not valid.")

    project_file = "pyproject.toml"
    project = toml.load(project_file)

    next_version = ref_suffix[1:]
    current_version = project["tool"]["poetry"]["version"]
    is_next_version = parse_version(next_version) > parse_version(current_version)

    if is_next_version:
        print(f"⭐ Next version will be: {next_version}")
        project["tool"]["poetry"]["version"] = next_version
        with open(project_file, "w") as f:
            toml.dump(project, f)
    else:
        print(
            f"✨ No version bump needed. Next version was {next_version} and current version is {current_version}."
        )


if __name__ == "__main__":
    bump_version_from_ref()
