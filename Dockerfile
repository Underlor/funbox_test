FROM python:3.7.4-alpine3.10

LABEL \
    maintainer="Popov Aleksander <admin@alexue4.ru>"

WORKDIR /app

# Only in this case because the app is launched using docker-compose with db
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /app/wait
RUN chmod +x /app/wait

COPY Pipfile* ./

RUN set -ex \
    && pip install -U \
        pip \
        pipenv \
    && apk add --no-cache -t build-deps \
        alpine-sdk \
        linux-headers \
        postgresql-dev \
    && apk add --no-cache \
        postgresql-libs \
    && pipenv install --system --deploy \
    && apk del build-deps

COPY . .

WORKDIR src
