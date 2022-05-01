import discord
from discord.ext import commands
import traceback
from modules import yktool
import os
import math
import asyncio


# コンフィグを読み込む
config = yktool.load_config()


# メインクラス
class Main(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix=command_prefix)
        self.help_command = None

        # コグ読み込み
        for cog in yktool.load_cogs():
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        custom = discord.Game(f"{self.command_prefix}help")
        await self.change_presence(activity=custom)

        print('-'*20)
        print()
        print('ログインしました。')
        print('Development by やくると#6140')
        print()
        print('-'*20)
        print()
        print(f'BOT NAME: {self.user.name}')
        print(f'BOT ID: {self.user.id}')
        print()
        print(f'discord.py Version: {discord.__version__}')
        print()
        print('-'*20)

        """ 虹色ロール
        server = await self.fetch_guild(908140851442618379)
        role = server.get_role(954493282438762556)
        
        col_index = 0
        while True:
            await role.edit(
                colour=discord.Colour.from_rgb(
                    abs(round((math.sin(col_index/360)/1)*255)),
                    abs(round((math.sin(col_index/360+2)/1)*255)),
                    abs(round((math.sin(col_index/360+4)/1)*255))
                )
            )
            col_index += 62
            await asyncio.sleep(6)
        """


if __name__ == '__main__':
    # html
    yktool.start_html()

    bot = Main(command_prefix=config["prefix"])
    bot.run(os.environ['TOKEN'])
