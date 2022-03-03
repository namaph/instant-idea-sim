FROM python:3.9-buster as builder
WORKDIR /opt/app
RUN pip install poetry
COPY pyproject.toml poetry.lock /opt/app/
RUN poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt


FROM python:3.9-slim-buster as runner
ENV PORT=8000
ENV GOOGLE_APPLICATION_CREDENTIALS="$HOME/credentials.json"

WORKDIR /opt/app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY ./instant_sim /opt/app/

ENV PYTHONUNBUFFERED=TRUE
CMD ["/bin/sh", "-c", "exec /usr/local/bin/uvicorn --host 0.0.0.0 --port $PORT app:app"]