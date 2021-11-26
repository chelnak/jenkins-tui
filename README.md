<!-- markdownlint-disable MD026 -->
# jenkins-tui :package:

![jenkins-tui](https://github.com/chelnak/jenkins-tui/actions/workflows/ci.yaml/badge.svg) [![PyPI version](https://badge.fury.io/py/jenkins-tui.svg)](https://badge.fury.io/py/jenkins-tui)

`jenkins-tui` is a terminal based user interface for Jenkins.

> :construction: :warning: This app is a prototype and in very early stages of development. There will be bugs, bad UX and missing functionality.

![home_view](media/home_view.png)

:rocket: This project is powered by [textual](https://github.com/willmcgugan/textual) and [rich](https://github.com/willmcgugan/rich)!

## Installation and Configuration

`jenkins-tui` is available on [pypi.org](https://pypi.org)!

```bash
pip install jenkins-tui
```

Once the app is installed you can run it from your terminal with the `jenkins` command.

```bash
jenkins
```

Alternatively, you can run the app with docker to keep your local dependencies squeaky clean 🧹

```bash
docker run --rm -it --volume $HOME:/jenkins ghcr.io/chelnak/jenkins-tui:latest
```

### Configuration

On first run you will be asked for some information so that the app can build your configuration file.

You'll need to enter a **url** for your Jenkins instance along with a **username** and **password**.

Alternatively you can manually pre-load a config file at `~/.jenkins-tui.toml` and use the following schema:

```bash
# .jenkins-tui.toml

url = ""
username = ""
password = ""
```

## Compatibility

This project has been tested on macOS and Linux (Arch, Ubuntu 20.04 and above) with Python 3.9 installed. It will likely work on any Linux distribution where Python 3.9 or above is available.
For Ubuntu 20.04, it may be necessary to install the `python3.9` package.

## Contributing

If you would like to contribute to `jenkins-tui` head over to the [contributing guide](CONTRIBUTING.md) to find out more!
