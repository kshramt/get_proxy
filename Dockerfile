from ubuntu:22.04 as base_py
env PYTHONUNBUFFERED 1
env PYTHONDONTWRITEBYTECODE 1
arg arch

from base_py as base_api
workdir /app
env PLAYWRIGHT_BROWSERS_PATH /my/playwright
run apt-get update \
   && apt-get install -y python3.11 python3-pip \
   && rm -rf /var/lib/apt/lists/* \
   && python3.11 -m pip install --no-cache-dir poetry==1.3.1
copy poetry.toml pyproject.toml poetry.lock .

from base_api as prod_api
run python3.11 -m poetry install --only main
run python3.11 -m poetry run python3 -m playwright install --with-deps \
   && rm -rf /var/lib/apt/lists/*
copy src src
run python3.11 -m poetry install --only main

from prod_api as test_api
run python3.11 -m poetry install
copy src src
run python3.11 -m poetry install
copy scripts/check.sh scripts/check.sh

from prod_api as prod
expose 8080

copy scripts/run.sh scripts/run.sh
entrypoint ["scripts/run.sh"]
