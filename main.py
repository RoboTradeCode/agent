"""
Агент
"""

from time import sleep
import schedule
import tomli
from requests import Session
from requests.adapters import HTTPAdapter

CONFIG_PATH = 'config.toml'  # Путь к файлу конфигурации
MAX_RETRIES = 5              # Максимальное количество попыток сделать запрос


def job(s: Session, url: str, params: dict) -> None:
    """
    Получает от конфигуратора настройки и отправляет их в канал Aeron

    :param s:      Сессия
    :param url:    Конечная точка API конфигуратора
    :param params: Параметры запроса
    """
    config = s.get(url, params).json()
    print(config)
    # TODO: publisher.offer(config)


def logs_handler(message: str) -> None:
    """
    Ретранслирует логи, поступающие в канал Aeron

    :param message: Логи
    """
    print(message)
    # TODO: publisher.offer()


def main() -> None:
    # Чтение конфигурации в формате TOML
    with open(CONFIG_PATH, 'rb') as f:
        toml_dict = tomli.load(f)

    # Создание сессии для запроса
    s = Session()
    s.mount(toml_dict['url'], HTTPAdapter(max_retries=MAX_RETRIES))

    # Планирование задачи
    request_params = {'agent.name': toml_dict['agent']['name'], 'agent.instance': toml_dict['agent']['instance']}
    job_args = {'s': s, 'url': toml_dict['url'], 'params': request_params}
    schedule.every(toml_dict['configurator']['update_seconds']).seconds.do(job, job_args)

    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    main()
