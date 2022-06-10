import discord
import json
import os
from modules import yktool


class Server:
    def __init__(self, guild_id) -> None:
        self.id = guild_id
        self.path = f"data/servers/{self.id}"
        
        x = self.load_file("config.json", "r")
        if os.stat(f"{self.path}/config.json").st_size > 0:
            self.config = json.load(x)
        else:
            self.config = {}
        x.close()
        
    
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
        
        f = open(f"{self.path}/{fn}", mode="w+", encoding="utf-8")
        f.close()
    
    def load_file(self, fn, mode="r+"):
        yktool.check_exist(f"servers/{self.id}")
        
        if os.path.exists(f"{self.path}/{fn}"):
            return open(f"{self.path}/{fn}", mode=mode, encoding="utf-8")
        else:
            self.create_file(fn)
            return self.load_file(fn, mode)
    
    def update_config(self):
        json.dump(self.config, self.load_file("config.json", "w+"), indent=4, ensure_ascii=False)
    
    def read_config(self, *args):
        config = self.config
        for key in args:
            if config := config.get(key):
                continue
            else:
                return None
            
        return config
        
    
    def write_config(self, value: dict):
        self.config.update(value)
        self.update_config()
        
        
    