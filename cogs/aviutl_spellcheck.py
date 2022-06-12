from discord.ext import commands
import discord
import random
import re
from modules import yktool
from modules.server import Server


class AviUtlSpellCheck(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.content.startswith(self.bot.command_prefix):
            return
        
        srv = Server(message.guild.id)
        
        # AviUtl 誤表記指摘おじさん
        if srv.read_config(["reply", "aviutl"], default=True):
            check_text = message.content
            for i in yktool.find_url(check_text):
                check_text = check_text.replace(i, "")

            matches = re.findall(r'(aviutl.exe|aviutl|aviutil)', check_text, flags=re.IGNORECASE)
        
            # AviUtl をスペルミスしてないか確認
            if wrong := [x for x in matches if not [y for y in ["aviutl.exe", "AviUtl"] if y == x]]:
                # 煽りメッセージの定義
                aori_messages = [
                    "`AviUtl`、ねｗ　二度と間違えないでもろてｗ",
                    "`AviUtl` だカス　間違えるなボケカスアホ　カス\n\nアホ",
                    "**AviUtl** だが？ｗ"
                ]
                
                # 一回のみのスペルミスだったら:
                if len(wrong) == 1:
                    aori_messages += [
                        f"`{wrong[0]}` じゃなく、 `AviUtl` だぞ？？今後このような間違えはしないようにねｗ スペルミスは、死ゾ！！ｗ",
                        f"{wrong[0]} ってなんすかｗ\nもしかして **AviUtl** のことっすか？ｗ",
                        f"そっちの世界、`AviUtl` のこと {wrong[0]} って言うんすねｗダサｗ",
                        f"なに {wrong[0]} って　**AviUtl** なら知ってるけど {wrong[0]} は知らんわｗ\n{wrong[0]} ってのがあるん？ｗ",
                        f"はいはーい {wrong[0]} じゃなくて **AviUtl** ねー　間違えないようにしてねー",
                        f"{wrong[0]} …ｗ　いやごめんｗ `AviUtl` のこと {wrong[0]} って呼ぶ人、なんか頭悪そうで…あいやｗごめんｗ",
                        f":x: {wrong[0]}\n:o: AviUtl\n\nこんな一般常識も知らないんスカｗ",
                    ]

                wrong = wrong[0]

                if wrong.lower() == "aviutl.exe":
                    aori_msg = random.choice(aori_messages)
                    aori_msg = aori_msg.replace(wrong, "XXX")
                    aori_msg = aori_msg.replace("AviUtl", "aviutl.exe")
                    aori_msg = aori_msg.replace("XXX", wrong)
                else:
                    aori_messages += [
                        f"うーわ…たまにいるんだよね **AviUtl** を aviutl だとか Aviutl だとか言う人ｗ\nいつも {wrong} って呼び方してるわけ？ｗ",
                        "おっと。正しいスペルは `AviUtl` です。これを見てください。\nhttp://spring-fragrance.mints.ne.jp/aviutl/\nサイト名にも書いてあるように、 `AviUtl` が正しいスペルですので、間違えないようにしましょうね。ｗ",
                        f"{wrong}…面白い冗談ですね、**AviUtl**をそのように表記するとは。\nスペル…**AviUtl**が正式名称ですよ。\nhttp://spring-fragrance.mints.ne.jp/aviutl/"
                    ]
                    aori_msg = random.choice(aori_messages)
            
                # ランダムで煽る
                await message.reply(aori_msg)

def setup(bot):
    bot.add_cog(AviUtlSpellCheck(bot))
