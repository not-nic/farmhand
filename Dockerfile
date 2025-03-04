FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

COPY . /app
COPY requirements.txt /app

RUN apk add --upgrade --no-cache && \
    pip install --upgrade pip && \
    pip install -r /app/requirements.txt --no-cache-dir

WORKDIR /app
EXPOSE 8000

CMD [ "./entrypoint.sh" ]