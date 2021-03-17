FROM docker.io/tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./ /app
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

ENV PYTHONPATH=./src
