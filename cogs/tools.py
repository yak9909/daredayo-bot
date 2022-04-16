from discord.ext import commands
import discord
import requests
import json
from modules import yktool
import urllib.parse


def get_redirect_url(url):
    resp = requests.head(url, allow_redirects=False)
    if 'Location' in resp.headers:
        return resp.headers['Location']
    return None


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def hextoarm(self, ctx: commands.Context):
        pass
    
    @commands.command()
    async def armtohex(self, ctx: commands.Context):
        pass

    @commands.command()
    async def archive(self, ctx: commands.Context, video):
        video_id = video
        if video.startswith("https://"):
            parsed = urllib.parse.urlparse(video)
            if parsed.netloc == "www.youtube.com":
                video_id = urllib.parse.parse_qs(parsed.query)["v"][0]
            else:
                video_id = parsed.path.split("/")[-1]
        await ctx.send(f"https://youtu.be/{video_id} のアーカイブを取得します…")
        
        async with ctx.channel.typing():
            archive = f"https://web.archive.org/web/2oe_/http://wayback-fakeurl.archive.org/yt/{video_id}"
            res = get_redirect_url(archive)
        if res:
            embed = discord.Embed(title="アーカイブが見つかりました！", description=f"[アーカイブURL]({res})")
            await ctx.send(embed=embed)
        else:
            await ctx.send("アーカイブが見つかりませんでした…")

    @commands.command()
    async def purge(self, ctx: commands.Context, arg1, arg2=None):
        if yktool.is_moderator(ctx.author.id):
            if not arg2:
                async with ctx.typing():
                    try:
                        arg1 = int(arg1)
                        await ctx.message.delete()
                        deleted = await ctx.channel.purge(limit=arg1)
                        await ctx.channel.send(f"{len(deleted)}個のメッセージを削除しました！\nこのメッセージは5秒後に削除されます", delete_after=5)
                    except ValueError:
                        await ctx.channel.send("削除数は半角英数字で入力してください")
            else:
                
                async with ctx.channel.typing():
                    try:
                        arg1 = int(arg1)
                        arg2 = int(arg2)
                        
                        ms1 = await ctx.channel.fetch_message(arg1)
                        ms2 = await ctx.channel.fetch_message(arg2)
                        messages = [msg async for msg in ctx.channel.history(before=ms1, after=ms2)] + [ms1, ms2]
                        
                        await ctx.message.delete()
                        deleted = await ctx.channel.delete_messages(messages)
                        await ctx.channel.send(f"{len(messages)}個のメッセージを削除しました！\nこのメッセージは5秒後に削除されます", delete_after=5)
                        
                    except discord.errors.NotFound:
                        await ctx.send("メッセージが存在しないようです。\n正しいメッセージIDを入力してください！")
                    except ValueError:
                        await ctx.send("メッセージIDは半角英数字で入力してください")
        else:
            await ctx.send("コマンド実行に必要な権限がありません")

    @purge.error
    async def purge_error(self, ctx: commands.Context, error: discord.ext.commands.CommandError):        
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await self.purge_help(ctx)
        else:
            await ctx.send(f"予想外のエラーが発生したようです。開発者に連絡してください\nErrorType: {type(error)}")

    async def purge_help(self, ctx: commands.Context):
        await ctx.send(
            "使い方:\n```\n"
            f"{self.bot.command_prefix}purge (<メッセージ削除数> | <削除開始メッセージID> <削除終了メッセージID>)"
            "\n```"
        )

    # メッセージを受信すると呼び出されるメソッド
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 送信主がbotならreturnする
        if message.author.bot:
            return
        
        command = self.bot.command_prefix + "hextoarm"
        if message.content.startswith(f""):
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
