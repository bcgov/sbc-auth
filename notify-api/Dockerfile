FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7-2019-10-15

COPY ./ /app
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

ENV PYTHONPATH=./src
