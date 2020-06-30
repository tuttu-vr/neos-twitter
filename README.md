# requirements

- Docker
- docker-compose

# environment variable

Write to collector/.env
```
TWITTER_CONSUMER_KEY=<your_key>
TWITTER_CONSUMER_SECRET=<your_secret>
```

Write to server/.env
```
TWITTER_CONSUMER_KEY=<your_key>
TWITTER_CONSUMER_SECRET=<your_secret>
FLASK_SESSION_SECRET=<any_random_string>
```

Add to server/.env if needed (to publish your server in private network)
```
NGROK_AUTH_TOKEN=<your_ngrok_token>
```

# run

At the root of this project, you run
```
docker-compose up
```

If you execute that, twitter collector and server will launch.
Then ngrok url(ex. http://xxxyyyzz.ngrok.io) will be displayed on your console.
You can access api by the url of http://xxxyyyzz.ngrok.io/recent .
