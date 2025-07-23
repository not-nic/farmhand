# Farmhand-Local

farmhand-local contains a `docker-compose.yml` to run the farmhand services locally in one stack 
creating images for the following services:

- [farmhand-api](https://github.com/not-nic/farmhand): this is the service that handles users, farms, fields etc.
- [farmhand-data-api](https://github.com/not-nic/farmhand-data-api): this service ingests data from the modhub, and the farming simulator game.
- Postgres: As this is running locally, I've bundled both databases into a single postgres instance, 
  and the `init_dbs.sh` script will create both databases on first time start up.

## Instruction Guide

for this stack to run you must first pull and build a docker image for the [farmhand-data-api](https://github.com/not-nic/farmhand-data-api):

1. Change directory out of `/farmhand` and clone the repository on your machine:
   ```bash
   git clone git@github.com:not-nic/farmhand-data-api.git
   cd farmhand-data-api
   ```

2. Build the image with the following command:
   ```bash
   docker build -t farmhand-data-api .
   ```

3. Start the docker compose stack with this directory the following command:
   ```
   docker compose --env-file ../.env -f docker-compose.yml up
   ```
   > [!NOTE]
   > This is using the .env file created from the steps within the README.md.
