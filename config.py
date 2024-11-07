from os import getenv
from json import loads
from yaml import safe_load
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = getenv("CONFIG_PATH", "config.yml")
TOKEN = getenv("DISCORD_TOKEN")
DEBUG = bool(loads(getenv("DEBUG", "false")))

with open(CONFIG_PATH, "r", encoding="utf-8") as file:
    _config = safe_load(file)

def extract_period(param) -> timedelta:
    return timedelta(
        minutes=param.get("minutes", 0),
        hours=param.get("hours", 0),
        days=param.get("days", 0),
        weeks=param.get("weeks", 0)
    )

def config(param: str, default=None):
    params = param.split(".")
    current_layer = _config

    for name in params:
        if name in current_layer:
            current_layer = current_layer[name]
        else:
            return default
        
    return current_layer