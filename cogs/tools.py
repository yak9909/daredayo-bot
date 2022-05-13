from discord.ext import commands
import discord
import requests
import json
from modules import yktool, chord_finder
import urllib.parse, urllib.request
import re
from bs4 import BeautifulSoup
import lxml
import lxml.html


def get_redirect_url(url):
    resp = requests.head(url, allow_redirects=False)
    if 'Location' in resp.headers:
        return resp.headers['Location']
    return None


def url2id(video_url: str):
    video_id = None
    parsed = urllib.parse.urlparse(video_url)
    if parsed.netloc == "www.youtube.com":
        video_id = urllib.parse.parse_qs(parsed.query)["v"][0]
    else:
        video_id = parsed.path.split("/")[-1]

    return video_id


class YouTubeArchive:
    def __init__(self, url):
        self.id = url2id(url)

        # アーカイブを取得
        self.url = self.get_archive()

        # アーカイブのURLからタイムスタンプを取得
        self.timestamp = self.get_timestamp()

        self.html = None

        self.video_name = None
        self.channel_name = None

    def is_available(func):
        def check_url(self, *args, **kwargs):
            if self.url:
                return func(self, *args, **kwargs)
        return check_url

    def using_html(func):
        def check_html(self, *args, **kwargs):
            if self.html is None:
                self.html = self.get_html()

            return func(self, *args, **kwargs)
        return check_html

    @is_available
    def get_info(self):
        video_title = self.get_video_title()
        # 不安定
        # channel_name = self.get_channel_name()
        return {"title": video_title, "author_name": None}

    @is_available
    def get_html(self):
        # アーカイブ(YouTube)の取得
        archive_url = f"http://archive.org/wayback/available?url=http://www.youtube.com/watch?v={self.id}&timestamp={self.timestamp}"
        r = requests.get(archive_url).json()
        return requests.get(r['archived_snapshots']['closest']['url']).text

    @is_available
    def get_timestamp(self):
        timestamp = urllib.parse.urlparse(self.url).path.split("/")[2]
        return timestamp

    @is_available
    @using_html
    def get_video_title(self):
        # HTMLタイトルから動画タイトルを抽出する
        vid_name = BeautifulSoup(self.html, features="lxml").title.text
        vid_name = " - ".join(vid_name.split(" - ")[:-1])
        return vid_name

    @is_available
    @using_html
    def get_channel_name(self):
        channel_name = re.findall(r'(?<=\+json">).*?(?=</script>)', self.html.replace('\n', ''))
        channel_url = json.loads(channel_name[0])["itemListElement"][0]["item"]["@id"]
        channel_name = json.loads(channel_name[0])["itemListElement"][0]["item"]["name"]
        return channel_name

    def get_archive(self):
        archive = f"https://web.archive.org/web/2oe_/http://wayback-fakeurl.archive.org/yt/{self.id}"
        return get_redirect_url(archive)


class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 機械語(16進数) から ARM Little Endian に変換 (with ARM Converter API)
    @commands.command()
    async def hextoarm(self, ctx: commands.Context):
        pass

    # ARM Little Endian から 機械語(16進数) に変換 (with ARM Converter API)
    @commands.command()
    async def armtohex(self, ctx: commands.Context):
        pass

    # YouTube でアクセスできなくなった動画のアーカイブを検索
    @commands.command()
    async def archive(self, ctx: commands.Context, video):
        await ctx.send(f"https://youtu.be/{url2id(video)} のアーカイブを取得します…")

        if video.startswith(("http://", "https://")):
            # アーカイブの取得
            async with ctx.channel.typing():
                archive = YouTubeArchive(video)

        if archive.url:
            # 動画情報の取得
            async with ctx.channel.typing():
                info = archive.get_info()

            embed = discord.Embed(title="アーカイブが見つかりました！", description=f'[{info["title"]}]({archive.url})')
            await ctx.send(embed=embed)
        else:
            await ctx.send("アーカイブは見つかりませんでした…")

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
    
    @commands.command()
    async def test(self, ctx: commands.Context, url):
        video_id = url2id(url)
        video_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v=" + video_id
        res = requests.get(video_url).json()
        embed = discord.Embed(title=res["title"], description=f'アップローダー: [{res["author_name"]}]({res["author_url"]})', url=f'https://youtu.be/{video_id}')
        embed.set_thumbnail(url=res["thumbnail_url"])
        await ctx.send(embed=embed)

    @commands.command()
    async def test2(self, ctx: commands.Context, url):
        oEmbed = "https://publish.twitter.com/oembed?url=" + url
        res = requests.get(oEmbed).json()
        embed = discord.Embed(title=res["author_name"], description=res["html"], url=res["author_url"])
        await ctx.send(embed=embed)

    @commands.command(name="chord")
    async def chord_find(self, ctx: commands.Context, *args):
        result = chord_finder.find("".join(args))
        if result == "undefined":
            await ctx.send("コードが見つかりませんでした…")
            return

        await ctx.send(f'{" ".join(args)} のコード名は **{result}** です')

    @commands.command()
    async def chtest(self, ctx: commands.Context, chord):
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

        note = re.match(r"[A-G]#?m?", chord).group()
        ch = re.finditer(r"(M7|[67]|add9|sus4|aug|dim|[\+-](5|9|11|13)|/(9|11|13))", chord)
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

    @commands.command()
    async def reload(self, ctx: commands.Context):
        if yktool.is_moderator(ctx.author.id):
            # コグ読み込み
            for cog in yktool.load_cogs():
                self.bot.reload_extension(cog)
            await ctx.message.add_reaction("✅")
        else:
            await ctx.message.add_reaction("❓")
    
    @reload.error
    async def reload_error(self, ctx: commands.Context, error: discord.ext.commands.CommandError):
        await ctx.message.add_reaction("❌")
        print(error)

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
