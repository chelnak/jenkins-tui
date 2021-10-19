.DEFAULT_GOAL:= build
SHELL := /bin/bash
VENV ?= "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

tag:
	@git tag -a $(version) -m "Release $(version) -> Jenkins TUI"
	@git push --follow-tags

build: check
	@source $(VENV)
	@python tools/bump_version.py "$(shell git describe --tags --abbrev=0)"
	@poetry build

check:
	@source $(VENV)
	@black --check .
	@mypy src/jenkins_tui
