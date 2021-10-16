VENV := "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

tag:
	# Usage: make version=v0.0.5 tag

	git tag -a $(version) -m "Release $(version) -> Jenkins TUI"
	git push --follow-tags

build:
	source $(VENV)
	poetry build

check:
	source $(VENV)
	black --check .
	mypy src/jenkins_tui
