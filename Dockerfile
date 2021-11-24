FROM python:3.9-slim

RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean

WORKDIR /jenkins
COPY dist/ /jenkins/
RUN pip install --no-cache-dir jenkins*.whl \
    && rm ./*
ENTRYPOINT ["jenkins"]
