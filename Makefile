SHELL := /bin/bash
.DEFAULT_GOAL:= build

ifdef VENV
virtualEnv = $(VENV)
else
virtualEnv := "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"
endif

tag:
	@git tag -a $(version) -m "Release $(version) -> Jenkins TUI"
	@git push --follow-tags

build: check
	@poetry install

	@source $(virtualEnv)
	@python tools/bump_version.py "$(shell git describe --tags --abbrev=0)"
	@poetry build

check:
	@source $(virtualEnv)
	@black --check .
	@mypy src/jenkins_tui
