# jenkins-tui :package:

![jenkins-tui](https://github.com/chelnak/jenkins-tui/actions/workflows/ci.yml/badge.svg)

`jenkins-tui` is a terminal based user interface for Jenkins.

## Install

```bash
pip install jenkins-tui
```

## Configure

`jenkins-tui` stores the sensitive stuff at `~/.jenkins-tui.toml`. You can create it manually or let the app do it for you on first run.

```bash
# .jenkins-tui.toml

url = ""
username = ""
password = ""
```

## Run

```bash
jenkins
```

## Develop

### Install dependencies

```bash
poetry install
```

### Install pre commit hooks

```bash
pre-commit instsall
```

### Run locally

```bash
cd src
python -m jenkins_tui.app
```
