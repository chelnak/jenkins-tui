# jenkins-tui :package:

![jenkins-tui](https://github.com/chelnak/jenkins-tui/actions/workflows/ci.yaml/badge.svg) [![PyPI version](https://badge.fury.io/py/jenkins-tui.svg)](https://badge.fury.io/py/jenkins-tui)

`jenkins-tui` is a terminal based user interface for Jenkins.

> :construction: :warning: This app is a prototype and in very early stages of development. There will be bugs and missing functionality. Additionally, it has only been tested on OSX.

:rocket: This project is powered by [textual](https://github.com/willmcgugan/textual) and [rich](https://github.com/willmcgugan/rich)!

## Installing with pip

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

Install dependencies with poetry:

```bash
poetry install
```

### Building

To keep local builds consistent with ci, use make to build and lint:

```bash
make build
```

### Install pre commit hooks

The project uses [pre-commit](https://pre-commit.com/) for commit time checking. You can find the configuration [here](.pre-commit-config.json).

```bash
pre-commit install
```

### Releasing stuff

Releasing is a semi manual but well oiled method. Tags are used to trigger the release steps in the ci process.

Running the following make command will tag and push the latest commit triggering a release.

```bash
make tag version="v0.0.5"
```

> Note: Releases can only be generated from the main branch.

### Runing locally

You can either build a new package using `make build` and install it or run the package directly:

```bash
cd src
python -m jenkins_tui.app
```
