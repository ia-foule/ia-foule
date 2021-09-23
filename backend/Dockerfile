FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
ARG BACKEND_PORT
EXPOSE $BACKEND_PORT

COPY requirements.txt .
COPY ./app .

RUN pip install -r requirements.txt
