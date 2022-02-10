from discord.ext import commands, menus
import discord


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # aliases=["t"] はコマンドのエイリアス いくらでも登録できる
    @commands.command(aliases=["a2h", "armtohex"])
    async def arm2hex(self, ctx, *args):
        await ctx.send(f"入力されました: {args}")

    # メッセージを受信すると呼び出されるメソッド
    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        # 送信主がbotならreturnする
        if msg.author.bot:
            return


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Tools(bot))
