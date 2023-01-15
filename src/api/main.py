import argparse
from enum import Enum

import uvicorn


class Environment(Enum):
    PROD = "prod"
    DEV = "dev"

    def __str__(self):
        return self.value


parser = argparse.ArgumentParser()
parser.add_argument(
    "--env",
    type=Environment,
    choices=list(Environment),
    default=Environment.PROD,
    help="Target environment",
)


def get_config(env: Environment = Environment.PROD) -> dict:
    config = {"host": "0.0.0.0", "port": 8000, "reload": False, "factory": True}

    if env == Environment.DEV:
        config["reload"] = True

    return config


def start():
    args = parser.parse_args()
    config = get_config(**vars(args))
    uvicorn.run("api.api:create_app", **config)
