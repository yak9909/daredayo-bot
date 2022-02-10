from discord.ext import commands, menus
import discord
import requests
import json


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # メッセージを受信すると呼び出されるメソッド
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 送信主がbotならreturnする
        if message.author.bot:
            return
        
        command = self.bot.command_prefix + "hextoarm"
        if message.content.startswith(command):
            val = message.content[len(command)+1:]
            params = {
                "hex": val,
                "offset": "",
                "arch": ["armbe"]
            }
            res = requests.post("https://armconverter.com/api/convert", json=params)
            await message.channel.send(json.loads(res.text)["asm"]["armbe"][1])

        command = self.bot.command_prefix + "armtohex"
        if message.content.startswith(command):
            val = message.content[len(command)+1:]

            labels = {}
            conv_conds = ["ldr", "str"]
            programs = []
            results = []

            for i,v in enumerate(val.split("\n")):
                if v.startswith("var"):
                    label = v[4:].replace(" ", "").split("=")
                    value = format(int(label[1], 16), "08x")
                    results.append(f".word 0x{value}")
                    labels[label[0]] = value
                else:
                    if not v == "":
                        programs.append(v)

            for i,v in enumerate(programs):
                if [x for x in conv_conds if v.startswith(x)]:
                    pc = 2
                    
                    reps = [[f".{b}", f'[pc, #{((len(programs)+a+1)-(i+1+pc))*4}]'] for a,b in enumerate(labels.keys()) if f".{b}" in v][-1]
                    v = v.replace(reps[0], reps[1])
                results.insert(-len(labels),v)

            params = {
                "asm": "\n".join(results),
                "offset": "",
                "arch": ["armbe"]
            }
            res = requests.post("https://armconverter.com/api/convert", json=params)
            await message.channel.send(json.loads(res.text)["hex"]["armbe"][1])


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Tools(bot))
