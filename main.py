import discord
from discord.ext import commands
import traceback
from modules import yktool
import os


# コンフィグを読み込む
config = yktool.load_config()


# メインクラス
class Main(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)

        # コグ読み込み
        for cog in yktool.load_cogs():
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        print('-'*20)
        print()
        print('ログインしました。')
        print('Development by 誰？#6140')
        print()
        print('-'*20)
        print()
        print(f'BOT NAME: {self.user.name}')
        print(f'BOT ID: {self.user.id}')
        print()
        print(f'discord.py Version: {discord.__version__}')
        print()
        print('-'*20)


if __name__ == '__main__':
    bot = Main(command_prefix=config["prefix"])
    bot.run(os.environ['TOKEN'])
