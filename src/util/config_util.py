import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'info.json')
SECRETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets')

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "hosts": [],
        "ports": [],
        "usernames": [],
        "passwords": [],
        "keypairs": [],
        "environments": []
    }

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)