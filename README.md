<img src="https://user-images.githubusercontent.com/44947427/160296335-a12f6887-850e-4170-86bc-fb509beea189.svg" height="101" alt="Python">

# agent

[![Tests](https://github.com/RoboTradeCode/agent/actions/workflows/tests.yml/badge.svg)](https://github.com/RoboTradeCode/agent/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/downloads/)
[![CPython](https://img.shields.io/badge/implementation-cpython-blue)](https://github.com/python/cpython)
[![Linux](https://img.shields.io/badge/platform-linux-lightgrey)](https://ru.wikipedia.org/wiki/Linux)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Установка зависимостей

```shell
pipenv install
```

## Использование

```
pipenv run python main.py
```

### Конфигурация сервиса

```
[Unit]
Description=Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/agent
ExecStart=pipenv run python main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
