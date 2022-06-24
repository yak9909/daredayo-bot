from discord.ext import commands
import discord
import requests
import json
import re


def get_offset(text):
    offset = re.findall(r'--offset ([0-9,a-z,A-Z]*)', text)
    offset = offset[0] if offset else ""
    return offset


class ArmConverter(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    # 機械語(16進数) から ARM Little Endian に変換 (with ARM Converter API)
    @commands.command()
    async def hextoarm(self, ctx: commands.Context):
        pass

    # ARM Little Endian から 機械語(16進数) に変換 (with ARM Converter API)
    @commands.command()
    async def armtohex(self, ctx: commands.Context):
        pass
    
    @commands.command(aliases=["cb"])
    async def calc_branch(self, ctx: commands.Context, from_address, to_address):
        calc_branch_offset = lambda From, To: ((((To - From) >> 2) - 2) & 0xFFFFFF)
        branch_arm = hex(calc_branch_offset(int(from_address, 16), int(to_address, 16)))[2:].rjust(8, '0')

        await ctx.send("EA" + branch_arm.upper()[2:])

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
            await message.reply(json.loads(res.text)["asm"]["armbe"][1], mention_author=False)

        command = self.bot.command_prefix + "armtohex"
        if message.content.startswith(command):
            val = message.content[len(command)+1:]

            #offset = re.findall(r'--offset ([0-9,a-z,A-Z]*)', val.split("\n")[0])

            #offset = (val := val.replace(val.split("\n")[0], "")) and offset[0] if offset else ""
            
            if offset := get_offset(val.split("\n")[0]):
                print(offset)
                val = val.replace(f'--offset {offset}', '')

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
                    
                    reps = [[f":{b}", f'[pc, #{((len(programs)+a+1)-(i+1+pc))*4}]'] for a,b in enumerate(labels.keys()) if f":{b}" in v]
                    if reps:
                        v = v.replace(reps[-1][0], reps[-1][1])
                results.insert(-len(labels),v)

            print(results)

            params = {
                "asm": "\n".join(results),
                "offset": offset,
                "arch": ["armbe"]
            }
            res = requests.post("https://armconverter.com/api/convert", json=params)
            arm_msg = await message.reply(json.loads(res.text)["hex"]["armbe"][1], mention_author=False)


def setup(bot):
    bot.add_cog(ArmConverter(bot))
