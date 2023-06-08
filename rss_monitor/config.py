import json
from pathlib import Path


def load_conf(CONF=str(Path(__file__).with_name('config.json'))):
    with open(CONF, 'r', encoding='utf8') as f:
        return json.load(f)
