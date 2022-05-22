echo "What is your Bot's Token?"
read token

echo "Building Dockerfile for bot"

docker build -t tcr_event_bot .

echo "Finished building Dockerfile"

echo "Running RocketRider!"
docker-compose up -d -e TOKEN=$token