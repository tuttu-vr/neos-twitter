FROM python:3.7.0-alpine3.8

RUN apk update && apk upgrade && apk add --no-cache --update sqlite-dev \
    gcc g++ libc-dev linux-headers && \
    # dev tools (can be removed)
    apk add sqlite vim && \
    rm -rf /var/cache/apk/*

ARG CLIENT_NAME=twitter
ENV COLLECTOR_CLIENT_NAME=$CLIENT_NAME

ENV TWITTER_CONSUMER_KEY=
ENV TWITTER_CONSUMER_SECRET=
ENV TWITTER_ACCESS_TOKEN=
ENV TWITTER_ACCESS_SECRET=

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN install -d data

COPY ./ ./src/
COPY entrypoint.sh ./

CMD [ "./entrypoint.sh" ]
