FROM python:3.9-slim

ENV JENKINS_TUI_CONFIG /jenkins/.jenkins-tui.toml

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

WORKDIR /jenkins

COPY dist/ /tmp/
RUN pip install --no-cache-dir /tmp/jenkins*.whl

ENTRYPOINT ["jenkins"]
