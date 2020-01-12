FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.7

ENV STATIC_PATH /app/myapp/static

RUN apk --update add tzdata && \
    cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    apk del tzdata && \
    rm -rf /var/cache/apk/*
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
