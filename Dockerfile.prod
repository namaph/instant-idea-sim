FROM python:3.9-buster as builder
WORKDIR /opt/app
COPY requirements.txt /opt/app
RUN pip install -r requirements.txt


FROM python:3.9-slim-buster as runner
ENV PORT=8000
ENV REDISHOST="localhost"
ENV REDISPORT="6379"
ENV LOCAL='local'

WORKDIR /opt/app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY ./app.py /opt/app/
COPY ./mylib /opt/app/mylib/

ENV PYTHONUNBUFFERED=TRUE
CMD ["/bin/sh", "-c", "python -m uvicorn --host 0.0.0.0 --port $PORT app:app"]