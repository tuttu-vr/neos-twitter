FROM python:3.7

RUN apt update -y && \
    apt install -y wget bash curl supervisor libffi-dev libssl-dev \
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

COPY ./ ./src/
RUN mv ./src/*.sh ./

EXPOSE 80

CMD [ "supervisord", "-c", "/etc/supervisord.conf" ]
