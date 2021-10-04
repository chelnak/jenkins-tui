# jenkins-tui :package:

![jenkins-tui](https://github.com/chelnak/jenkins-tui/actions/workflows/ci.yaml/badge.svg)

`jenkins-tui` is a terminal based user interface for Jenkins.

> :construction: :warning: This app is a prototype and in very early stages of development. There will be bugs and missing functionality. Additionally, it has only been tested on OSX.

## Install

```bash
pip install jenkins-tui
```

## Configure

The app stores the sensitive stuff at `~/.jenkins-tui.toml`. You can create it manually using the schema below or let the app do it for you on first run.

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
pre-commit install
```

### Run locally

```bash
cd src
python -m jenkins_tui.app
```
