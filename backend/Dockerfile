FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ARG BACKEND_PORT
EXPOSE $BACKEND_PORT

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y ffmpeg
COPY requirements.txt .
COPY ./app .

RUN pip install -r requirements.txt
