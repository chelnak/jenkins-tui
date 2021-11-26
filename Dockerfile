FROM python:3.9-slim

ENV JENKINS_TUI_CONFIG /jenkins/.jenkins-tui.toml

RUN apt-get update \
    && apt-get install gcc -y \
    && bash \
    && apt-get clean

WORKDIR /jenkins
COPY dist/ /jenkins/
RUN pip install --no-cache-dir jenkins*.whl \
    && rm ./*

ENTRYPOINT ["jenkins"]
