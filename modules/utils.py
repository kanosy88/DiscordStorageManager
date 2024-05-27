import json
from typing import TypedDict

class Config(TypedDict):
    output_directory: str
    splitted_file_directory: str
    channel_id: str
    discord_token: str
    send_max_worker: int
    get_max_worker: int

def get_config() -> Config:
    with open('./config.json') as f:
        data = json.load(f)
        return data