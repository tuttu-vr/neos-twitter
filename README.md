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

# twitter developer settings

You have to set `http://localhost:8080/register` as `callback url`.

# run

At the root of this project, run
```
./build.sh full
docker-compose up
```

If you execute that, twitter collector and server will be launched.
Then you can access the api by the url of http://localhost:8080/login .
To see other api, check /server/app.py.
