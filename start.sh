echo "What is your Bot's Token?"
read token

echo "Running RocketRider!"
docker-compose up -d -e TOKEN=$token