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

.PHONY: dev-build
dev-build:
	@nerdctl compose --env-file dev/.env --project-directory dev up --build

.PHONY: dev-run
dev-run:
	@nerdctl compose --env-file dev/.env --project-directory dev up

.PHONY: dev-clean
dev-clean:
	@nerdctl container rm dev_controller_1
	@nerdctl container rm dev_agent_1
	@nerdctl volume rm dev_jenkins_home

.PHONY: run
run:
	@poetry env use 3.9
	@poetry run jenkins --config ./dev/.jenkins-tui.toml
