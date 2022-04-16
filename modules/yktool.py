import json
import os
import threading
from flask import Flask, render_template


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


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


def _start_html():
    app.run(host='0.0.0.0', port=8080)


def start_html():
    https_thread = threading.Thread(target=_start_html)
    https_thread.start()
