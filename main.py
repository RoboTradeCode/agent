import tomli
from aeron import Subscriber, Publisher
from time import sleep
from requests import Session
from requests.adapters import HTTPAdapter
import schedule

CONFIG_PATH = "config.toml"
MAX_RETRIES = 5


class Agent:
    session: Session
    endpoint: str
    config_publisher: Publisher
    logs_subscriber: Subscriber
    logs_publisher: Publisher

    def __init__(self, config: dict):
        self.session = Session()
        self.endpoint = config["configurator"]["url"]
        self.session.mount(self.endpoint, HTTPAdapter(max_retries=MAX_RETRIES))

        self.config_publisher = Publisher(
            config["aeron"]["publishers"]["config"]["channel"],
            config["aeron"]["publishers"]["config"]["stream_id"],
        )

        self.logs_publisher = Publisher(
            config["aeron"]["publishers"]["logs"]["channel"],
            config["aeron"]["publishers"]["logs"]["stream_id"],
        )

        self.logs_subscriber = Subscriber(
            self.logs_handler,
            config["aeron"]["subscribers"]["logs"]["channel"],
            config["aeron"]["subscribers"]["logs"]["stream_id"],
            10,
            self,
        )

    @staticmethod
    def logs_handler(clientd: "Agent", message: str) -> None:
        clientd.logs_publisher.offer(message)

    def distribute_config(self):
        content = self.session.get(self.endpoint).text
        self.config_publisher.offer(content)

    def poll(self):
        self.logs_subscriber.poll()


def main() -> None:
    with open(CONFIG_PATH, "rb") as f:
        toml_dict = tomli.load(f)

    agent = Agent(toml_dict)
    schedule.every(toml_dict["configurator"]["update_seconds"]).seconds.do(
        lambda: agent.distribute_config()
    )

    while True:
        schedule.run_pending()
        agent.poll()
        sleep(1)


if __name__ == "__main__":
    main()
