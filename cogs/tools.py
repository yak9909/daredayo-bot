from xmlrpc.client import Boolean
from discord.ext import commands
import discord
import requests
import json
from modules import yktool, chord_finder, ytpy
from modules.server import Server
import re


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # purge
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
                        messages = [msg async for msg in ctx.channel.history(limit=500, before=ms1, after=ms2)] + [ms1, ms2]
                        
                        deleted = await ctx.channel.delete_messages(messages)
                        await ctx.message.delete()
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

    @commands.command(name="gettweet")
    async def get_tweet_oEmbed(self, ctx: commands.Context, url):
        oEmbed = "https://publish.twitter.com/oembed?url=" + url
        res = requests.get(oEmbed).json()
        tweet = re.findall(r'<p .*>(.*?)</p>', res["html"])
        embed = discord.Embed(title=res["author_name"], description=tweet[0], url=res["author_url"])
        await ctx.send(embed=embed)

    @commands.command(aliases=["n2c", "chord"])
    async def notes2chord(self, ctx: commands.Context, *args):
        result = chord_finder.find("".join(args))
        if result == "undefined":
            await ctx.send("コードが見つかりませんでした…")
            return

        await ctx.send(f'{" ".join(args)} のコード名は **{result}** です')

    @commands.command(aliases=["c2n", "note"])
    async def chord2notes(self, ctx: commands.Context, chord):
        chord_st = {
            "root": 0,
            "2": -1,
            "3rd": 4,
            "4th": 7,
            "5th": -1,
            "-5": -1,
            "+5": -1,
            "6": -1,
            "7th": -1,
            "maj7": -1
        }

        key = 0

        chord_reference = json.load(open("./data/chord.json", encoding="utf-8"))

        xx = "|".join(list(chord_reference["chord"].keys())).replace("+", "\\+")
        """
        #ch = re.findall(r'(' + xx + r')', chord)
        seiki = r"^[A-G](#|b)?(-5|((add9|add2|add4)|(m|aug|dim)?((M7|M9|7|6?9?|11|12)((-|\+(5|9|11)).)?)?(sus4|sus2)?))(/[A-G](#|b)?)?$"
        #ch = [x[0] for x in re.findall(seiki, chord)[1:-1]]

        if len(chord) >= 3:
            await ctx.send("コード名に誤りがあるようです!")
            return
        """

        note = re.match(r"[A-G]#?", chord).group()
        ch = re.finditer(r"(m|M7|[67]|add9|sus4|aug|dim|[\+-](5|9|11|13)|/(9|11|13))", chord)
        ch = [x.group() for x in ch]

        key = [int(k) for k, v in chord_reference["note"].items() if v[0] in note][-1]

        for v in chord_reference['chord'].keys():
            if v in ch:
                chord_st.update(chord_reference['chord'][v])

        chord_st = {k: ((12 + v + key) % 12) for k, v in chord_st.items() if not v == -1}
        result = []

        for i in chord_st.values():
            result.append(str(i).replace(str(i), chord_reference["note"][str(i)][0]))

        await ctx.send(" ".join(result))


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Tools(bot))
