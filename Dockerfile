FROM python:3.12-alpine

RUN mkdir -p /app/
WORKDIR /app

COPY . /app/

RUN pip install -U pip setuptools wheel \
        && pip install . \
        && rm -rf /root/.cache

CMD ["schedule-notifier"]
