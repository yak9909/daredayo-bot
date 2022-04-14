from discord.ext import commands
import discord
import random
import re


# 文字列内からURLを抽出
def find_url(text):
    # findall() 正規表現に一致する文字列を検索する
    url = re.findall(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', text)
    return url 


def find_token(text):
    token = re.findall(r'[M-Z][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}', text)
    return token


class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        for i in find_url(message.content):
            message.content = message.content.replace(i, "")

        matches = re.findall(r'(aviutl|aviutil)', message.content, flags=re.IGNORECASE)
    
        # AviUtl をスペルミスしてないか確認
        if wrong := [x for x in matches if not x == "AviUtl"]:
            # 煽りメッセージの定義
            aori_messages = [
                "`AviUtl`、ねｗ　二度と間違えないでもろてｗ",
                "`AviUtl` だカス　間違えるなボケカスアホ　カス\n\nアホ",
                "おっと。正しいスペルは `AviUtl` です。これを見てください。\nhttp://spring-fragrance.mints.ne.jp/aviutl/\nサイト名にも書いてあるように、 `AviUtl` が正しいスペルですので、間違えないようにしましょうね。ｗ",
                "**AviUtl** だが？ｗ"
            ]
            
            # 一回のみのスペルミスだったら:
            if len(wrong) == 1:
                wrong = wrong[0]
                aori_messages += [
                    f"`{wrong}` じゃなく、 `AviUtl` だぞ？？今後このような間違えはしないようにねｗ スペルミスは、死ゾ！！ｗ",
                    f"{wrong} ってなんすかｗ\nもしかして **AviUtl** のことっすか？ｗ",
                    f"{wrong}…面白い冗談ですね、**AviUtl**をそのように表記するとは。\nスペル…**AviUtl**が正式名称ですよ。\nhttp://spring-fragrance.mints.ne.jp/aviutl/"
                ]
        
            # ランダムで煽る
            await message.reply(random.choice(aori_messages))

        if find_token(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention} Tokenが検出されたので削除しました。")


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Checker(bot))
