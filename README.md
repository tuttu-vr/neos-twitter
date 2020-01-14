# requirements

- Docker
- docker-compose

# environment variable

Write to collector/.env
```
TWITTER_CONSUMER_KEY=<your_key>
TWITTER_CONSUMER_SECRET=<your_secret>
TWITTER_ACCESS_TOKEN=<your_access_token>
TWITTER_ACCESS_SECRET=<your_access_secret>
```

Write to server/.env if needed (to launch server in your private network)
```
NGROK_AUTH_TOKEN=<your_ngrok_token>
```

# run

```
docker-compose up
```
