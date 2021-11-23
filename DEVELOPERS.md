# Developing

Welcome to the developer guid for `jenkins-tui`! All commands assume that you are running them from the root of the repository.

## Setting up your environment

```bash
make init
```

This will install dependencies and pre-commit hooks.

## Local Jenkins

The repo comes with a fully configured dev instance. To start it run the following command:

```bash
make env-run
```

Once it's started you can access it locally with the following details:

| host | user | password |
|------|------|----------|
| <http://localhost:8080> | admin | admin |

### Run the app in dev mode

You can also start an instance of jenkins-tui that is configured to talk to the local jenkins instance. This is recommended when developing as it essentially runs the app with the `--debug` switch along with some custom configuration for the local dev environment.

```bash
make app-run
```

## Releasing stuff

Releasing is a semi manual but well oiled method. Tags are used to trigger the release steps in the ci process.

The first step is to bump the version in [pyproject.toml](pyproject.toml).

Then run the following command. It will tag and push the latest commit triggering a release.

```bash
make tag version="v0.0.5"
```

## Credits

The dev env set up uses lots of the good stuff from this repository: <https://github.com/uhafner/warnings-ng-plugin-devenv/tree/main/docker>
