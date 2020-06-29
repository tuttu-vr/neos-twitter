FROM python:3.7.0-alpine3.8

RUN apk update && apk upgrade && apk add --no-cache --update sqlite-dev \
    gcc g++ libc-dev linux-headers build-base libffi-dev openssl openssl-dev && \
    # dev tools (can be removed)
    apk add sqlite vim && \
    rm -rf /var/cache/apk/*

ARG CLIENT_NAME=twitter
ENV COLLECTOR_CLIENT_NAME=$CLIENT_NAME

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN install -d data

COPY ./ ./src/
COPY entrypoint.sh ./

CMD [ "./entrypoint.sh" ]
