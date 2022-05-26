if -f ".env" then
    echo "What is your Bot's Token?"
    read token

    echo $token >> .env
else
    echo "Using pre-existing .env file"
fi;

echo "Building Dockerfile for bot"

docker build -t tcr_event_bot .

echo "Finished building Dockerfile"

echo "Running RocketRider!"
docker-compose up -d --env-file=.env