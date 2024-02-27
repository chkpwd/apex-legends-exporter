# Apex Legends Prometheus Exporter

The Apex Legends Prometheus Exporter is a Python application designed to collect real-time game data from Apex Legends, such as map rotation, player stats, and more. This data is then exposed as metrics that can be scraped by Prometheus. As well, in conjunction with visualization tools like Grafana.

## Features

- Fetch and expose current and next map rotation information.
- Collect detailed player statistics including level, rank, battle pass level, and much more.
- Expose game-related metrics for monitoring and analysis.
- Easy integration with Prometheus and Grafana for visualization and alerting.

## Prerequisites

- An API key from [Mozambique HeRe API](https://apexlegendsapi.com/) for fetching Apex Legends data.
- Docker / Docker Compose
- Prometheus server setup for collecting metrics.

## Installation

The Apex Legends Prometheus Exporter can be easily run as a container. This section covers pulling the Container Image from the GitHub Container Registry and running it.

### Pulling the Container Image

To pull the latest version of the Apex Legends Prometheus Exporter image, use the following command:
```sh
docker pull ghcr.io/chkpwd/apex-legends-exporter:latest && \
docker run --rm -p 5000:5000 \
  -e USER_ID="your_user_id" \
  -e PLAYER_NAME="player_name" \ # OPTIONAL, either USER_ID or PLAYER_NAME needs to be specified
  -e API_KEY="your_api_key" \
  -e PLATFORM="PC" \
  ghcr.io/chkpwd/apex-legends-exporter:latest
```
Alternatively, you can use Docker Compose to run the Apex Legends Prometheus Exporter. Create a docker-compose.yml file with the following content:
```yaml
version: '3.8'
services:
  apex-legends-exporter:
    image: ghcr.io/chkpwd/apex-legends-exporter:latest
    ports:
      - "5000:5000"
    environment:
      USER_ID: "your_user_id"
      API_KEY: "your_api_key"
      PLATFORM: "PC"
```
Then run with:
```sh
docker-compose up -d
```
Accessing Metrics

With the container running, you can access the exposed metrics by navigating to http://localhost:5000/metrics in your web browser or using a tool like curl:
```sh
curl http://<ip-address>:5000/metrics
```
