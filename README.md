# Git Repo Archive API

## Installation

To set up this application and create a virtual environment, follow these steps:

1. Install `pyenv` by following the instructions in the [official documentation](https://github.com/pyenv/pyenv#installation).

2. Create a virtual environment for this application using `pyenv`. Open your terminal and execute the following commands:

   ```bash
   pyenv install 3.11
   pyenv virtualenv 3.11 git-archive-api
   pyenv activate git-archive-api
   ```

3. Install the required dependencies by running the following command:

   ```bash
   pip install -r requirements.txt
   ```

## Run for Development

Run with reload enables

```bash
uvicorn app.api:app --reload --port 8080
```

or

```bash
python main.py
```

## Usage

```bash
curl -X 'POST' \
  'http://127.0.0.1:8080/archives/?repo_url=https%3A%2F%2Fgithub.com%2Fjulianschelb%2Fvscode-theme-solarized-dark' \
  -H 'accept: application/json' \
  -d ''
```


## Todo:

- [ ]  Avoid collisions of repository names
- [ ]  Return Git output in response (including errors)
- [ ]  Use a separate folder for (large) repositories which do not need to be updated
- [ ]  Functions for importing private keys into the Docker container
