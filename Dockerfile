FROM python:3.9-slim

ENV JENKINS_TUI_CONFIG /jenkins/.jenkins-tui.toml

WORKDIR /jenkins

COPY dist/ /tmp/
RUN pip install --no-cache-dir /tmp/jenkins*.whl

ENTRYPOINT ["jenkins"]
