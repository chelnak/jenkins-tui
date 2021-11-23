.DEFAULT_GOAL:= build
SHELL := /bin/bash
VENV ?= "$(shell poetry env list --full-path | cut -f1 -d " ")/bin/activate"

# Releasing
tag:
	@git tag -a $(version) -m "Release $(version) -> Jenkins TUI"
	@git push --follow-tags

# Building
build: check
	@source $(VENV)
	python tools/bump_version.py
	@poetry build

check:
	@source $(VENV)
	black --check .
	mypy tools
	isort --check src/jenkins_tui
	mypy src/jenkins_tui

# Developing
.PHONY: init
init:
	@poetry install
	@pre-commit install

.PHONY: env-build
env-build:
	@nerdctl compose --env-file dev/.env --project-directory dev up --build

.PHONY: env-run
env-run:
	@nerdctl compose --env-file dev/.env --project-directory dev up

.PHONY: env-clean
env-clean:
	@nerdctl container rm dev_controller_1
	@nerdctl container rm dev_agent_1
	@nerdctl volume rm dev_jenkins_home

.PHONY: app-run
app-run:
	@poetry env use 3.9
	@poetry run jenkins --config ./dev/.jenkins-tui.toml --debug
