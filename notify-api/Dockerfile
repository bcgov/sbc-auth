FROM docker.io/tiangolo/uvicorn-gunicorn-fastapi:python3.8

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

COPY ./ /app
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

ENV PYTHONPATH=./src
