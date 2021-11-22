FROM python:3.9-slim
WORKDIR /jenkins
COPY dist/ /jenkins/
RUN pip install --no-cache-dir jenkins*.whl \
    && rm ./*
ENTRYPOINT ["jenkins"]
