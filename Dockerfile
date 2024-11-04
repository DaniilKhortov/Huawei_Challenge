FROM python:3
WORKDIR /app
COPY . /app
RUN pip3 install numpy scipy redis celery fastapi uvicorn