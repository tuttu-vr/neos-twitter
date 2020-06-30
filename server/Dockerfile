FROM python:3.7-alpine3.11

RUN apk update && \
    apk add --no-cache wget bash curl supervisor build-base pcre-dev \
    build-base libffi-dev openssl openssl-dev \
    unzip jq

# a tool for local execute
ADD https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip /tmp

RUN unzip /tmp/ngrok-stable-linux-amd64.zip && \
    mv ngrok /usr/local/bin/

COPY supervisord/supervisord.conf /etc/
RUN install -d /var/log/supervisor/

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY *.py ./src/
COPY *.sh ./

EXPOSE 80

CMD [ "supervisord", "-c", "/etc/supervisord.conf" ]
