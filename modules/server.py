import discord
import json
import os
from modules import yktool


class Server:
    def __init__(self, guild_id) -> None:
        self.id = guild_id
        self.path = f"data/servers/{self.id}"
        self.config = self.load_config()
    
    def require(dir=[]):
        def _require(func):
            def wrapper(self, *args, **kwargs):
                for d in dir:
                    yktool.check_exist(d, self.path)
                return func(*args, **kwargs)
            return wrapper
        return _require
    
    def create_file(self, fn):
        if dir := "/".join(fn.split("/")[:-1]):
            yktool.check_exist(dir, self.path)
        
        print(f"create file '{self.path}/{fn}'")
        f = open(f"{self.path}/{fn}", mode="w+", encoding="utf-8")
        f.close()
    
    def load_file(self, fn, mode="r+"):
        yktool.check_exist(f"servers/{self.id}")
        
        if os.path.exists(f"{self.path}/{fn}"):
            return open(f"{self.path}/{fn}", mode=mode, encoding="utf-8")
        else:
            self.create_file(fn)
            return self.load_file(fn, mode)
    
    def load_config(self):
        config = {}
        x = self.load_file("config.json", "r")
        if os.stat(f"{self.path}/config.json").st_size > 0:
            config = json.load(x)
        x.close()
        return config
    
    def update_config(self):
        json.dump(self.config, self.load_file("config.json", "w+"), indent=4, ensure_ascii=False)
    
    def init_config(self, default, keys, ignore_check=False):
        if not ignore_check:
            if not self.read_config(keys, init=False, default=default) is None:
                return

        config = default
        for i in range(len(keys)):
            config = {keys[len(keys)-1 - i]: config}
        self.write_config(config)
    
    def read_config(self, keys, init=True, default=None):
        if init:
            self.init_config(default, keys)
        
        config = self.config = self.load_config()
        for key in keys:
            config = config.get(key)
            if config is None:
                break
            
        return config
    
    def write_config(self, value: dict):
        self.config = yktool.update_z(self.config, value)
        self.update_config()
        
        
    