FROM python:3.7-alpine3.11

RUN apk update && \
    apk add --no-cache wget bash curl supervisor build-base pcre-dev \
    build-base libffi-dev openssl openssl-dev \
    unzip jq

COPY supervisord/supervisord.conf /etc/
RUN install -d /var/log/supervisor/

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./ ./src/
RUN mv ./src/*.sh ./

EXPOSE 8080

HEALTHCHECK --interval=20s --timeout=5s --retries=2 CMD ./healthcheck.sh

CMD [ "supervisord", "-c", "/etc/supervisord.conf" ]
