from time import sleep
import schedule
import tomli
from aeron import Subscriber, Publisher
from requests import Session
from requests.adapters import HTTPAdapter

CONFIG_PATH = "config.toml"  # Путь к файлу с конфигурацией
MAX_RETRIES = 5  # Максимальное количество попыток получить ответ от конфигуратора


class Agent:
    """
    Торговый агент. Периодически получает конфигурацию от конфигуратора и публикует её в
    канал Aeron. Также ретранслирует логи
    """

    session: Session  # Сессия для подключения к конфигуратору
    endpoint: str  # URL конфигуратора
    config_publisher: Publisher
    logs_subscriber: Subscriber
    logs_publisher: Publisher

    def __init__(self, config: dict):
        """
        :param config: Конфигурация
        """
        # Инициализация сессии для подключения к конфигуратору
        self.session = Session()
        self.endpoint = config["configurator"]["url"]
        self.session.mount(self.endpoint, HTTPAdapter(max_retries=MAX_RETRIES))

        # Инициализация канала для публикации конфигураций
        self.config_publisher = Publisher(
            config["aeron"]["publishers"]["config"]["channel"],
            config["aeron"]["publishers"]["config"]["stream_id"],
        )

        # Инициализация канала для получения логов
        self.logs_publisher = Publisher(
            config["aeron"]["publishers"]["logs"]["channel"],
            config["aeron"]["publishers"]["logs"]["stream_id"],
        )

        # Инициализация канала для публикации логов
        self.logs_subscriber = Subscriber(
            self.logs_handler,
            config["aeron"]["subscribers"]["logs"]["channel"],
            config["aeron"]["subscribers"]["logs"]["stream_id"],
            config["aeron"]["subscribers"]["logs"]["fragments_limit"],
        )

    def logs_handler(self, message: str) -> None:
        """
        Функция обратного вызова для приёма логов из канала Aeron
        :param message: Сообщение, поступившее в канал
        """
        self.logs_publisher.offer(message)

    def distribute_config(self) -> None:
        """
        Получить и опубликовать новую конфигурацию
        """
        content = self.session.get(self.endpoint).text
        self.config_publisher.offer(content)

    def poll(self) -> None:
        """
        Проверить наличие новых сообщений в каналах Aeron
        """
        self.logs_subscriber.poll()


def main() -> None:
    # Чтение конфигурации в формате TOML
    with open(CONFIG_PATH, "rb") as f:
        toml_dict = tomli.load(f)

    # Инициализация торгового агента
    agent = Agent(toml_dict)

    # Планирование задачи для распространения конфигурации
    schedule.every(toml_dict["configurator"]["update_seconds"]).seconds.do(
        lambda: agent.distribute_config()
    )

    while True:
        schedule.run_pending()
        agent.poll()
        sleep(1)


if __name__ == "__main__":
    main()
