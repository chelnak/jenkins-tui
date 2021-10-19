.DEFAULT_GOAL:= build
SHELL := /bin/bash
VENV ?= "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

tag:
	@git tag -a $(version) -m "Release $(version) -> Jenkins TUI"
	@git push --follow-tags

build: check
	@source $(VENV)
	python tools/bump_version.py
	@poetry build

check:
	@source $(VENV)
	black --check .
	mypy tools
	mypy src/jenkins_tui
