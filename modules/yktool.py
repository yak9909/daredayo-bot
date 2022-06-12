import json
import os
import threading
from flask import Flask, render_template
import re


def load_config() -> dict:
    file_path = "config.json"
    if os.path.exists("dev_config.json"):
        file_path = "dev_config.json"

    config_file = open(file_path, mode="r+", encoding="utf-8")
    return json.load(config_file)


def is_moderator(user_id):
    moderators_id = load_config()["moderator"]
    if user_id in moderators_id:
        return True
    return False


def read_file(file_path, write=False):
    mode = "r+"
    if write:
        mode = "w+"

    file = open(file_path, mode=mode, encoding="utf-8")
    return file


# cogs/ 内にある .py ファイルを返す
# 先頭に # がつくファイルは無視される
def load_cogs():
    Initial_Cogs = []
    for file in os.listdir("cogs/"):
        if file.startswith("#"):
            continue
        if file.endswith(".py"):
            print(f"cogs.{file.split('.')[0]}")
            Initial_Cogs.append(f"cogs.{file.split('.')[0]}")
    return Initial_Cogs


def check_exist(dir, root="./data"):
    if dir:
        d = dir.split("/")
        dx = ""
        for x in d:
            dx += x + "/"
            if not os.path.exists(f"{root}/{dx}"):
                print(f"directory '{x}' is not found.\ncreate '{root}/{dx}'")
                os.mkdir(f"{root}/{dx}")


def data_check(dir, root="./data"):
    def _data_check(func):
        def wrapper(*args, **kwargs):
            check_exist(dir, root)
            return func(*args, **kwargs)
        return wrapper
    return _data_check


def format_toggle(text):
    toggle_map = {
        "enable": ["enable", "on", "true"],
        "disable": ["disable", "off", "false"]
    }
    for k,v in toggle_map.items():
        for x in v:
            if text.lower() == x:
                if k == "enable":
                    return True
                elif k == "disable":
                    return False
    return None


def find_url(text):
    url = re.findall(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', text)
    return url 


def find_token(text):
    token = re.findall(r'[M-Z][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}', text)
    return token


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


def _start_html():
    app.run(host='0.0.0.0', port=8080)


def start_html():
    https_thread = threading.Thread(target=_start_html)
    https_thread.start()
