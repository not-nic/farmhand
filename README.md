# Farmhand API

![farmhand_logo_dark](https://github.com/user-attachments/assets/295abba9-c953-4cee-abd9-b2b68076555d)

This is the backend API for the Farmhand application written in Python & FastAPI. Farmhand is a companion service that can be used alongside Farming Simulator 2025 (and 2022!) to track, manage and plan your farm, vehicles, crops and more. 🌾

## Install Guide
1. Clone this repository on your machine:
   ```bash
   git clone git@github.com:not-nic/farmhand.git
   cd farmhand
   ```
2. Create a `.env` file with the following development variables:
   ```plaintext
   POSTGRES_HOST=database # localhost:5432 if running outside docker...
   POSTGRES_USER=postgres  
   POSTGRES_PASSWORD=postgres  
   POSTGRES_DB=farmhand  
   ENVIRONMENT=development  
  
   SERVICE_USER_USERNAME=service-user  
   SERVICE_USER_EMAIL=service-user@farmhand.uk  
   SERVICE_USER_PASSWORD=<your_password>
   ```
3. Start the service with docker:
   ```bash
   docker compose up
   ```

## Local Development
1. [Create a Python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) called `.venv` or `.farmhand` (ideally python 3.12.x)
   ```bash
   python -m venv .venv
   ```
2. On windows start the virtual environment by using:
   ```bash
   .venv\Scripts\activate
   ```
   or if you are on macOS / Linux use:
   ```bash
   source .venv/bin/activate
   ``` 
3. Inside the `.venv` install requirements with the following command:
   ```bash
   pip install -r requirements.txt
   ```
4. Build the application for docker development with the following command:
   ```bash
   docker compose up --build
   ```
5. Verify the application has started properly by checking the output:
   ```plaintext
    farmhand-api  |                                                  
    farmhand-api  | ______                   _                     _
    farmhand-api  | |  ___|                 | |                   | |
    farmhand-api  | | |_ __ _ _ __ _ __ ___ | |__   __ _ _ __   __| |
    farmhand-api  | |  _/ _` | '__| '_ ` _ \| '_ \ / _` | '_ \ / _` |
    farmhand-api  | | || (_| | |  | | | | | | | | | (_| | | | | (_| |
    farmhand-api  | \_| \__,_|_|  |_| |_| |_|_| |_|\__,_|_| |_|\__,_|
    farmhand-api  |
    farmhand-api  | =========== Farmhand service started ============
   ```
6. Visit the documentation for the application by going to:
   ```plaintext
   http://localhost:8000/docs
   ```

## Linting

Linting and formatting is handled with Ruff. This repository loosely follows the Black formatter and PEP8 style guide.

Run linting and formatting with the following commands:

```bash
ruff check
```

```bash
ruff format
```

## Tests

Running unit tests requires the application to be setup (see [Local Development](#local-development)).

Make sure the application is set up and then use the following command to run all tests:
```bash
pytest tests
```
or test individual files with:
```bash
pytest pytest tests/api/services/test_modhub_service.py::TestModHubService::test_scrape_mock_mod -s -vv 
```
> Note: you can also use -s for standard output (prints, log messages, etc.) or -vv to produce a very verbose output.

### Test Coverage

To check the test coverage of the repository use the following command:
```bash
pytest --cov src 
```
