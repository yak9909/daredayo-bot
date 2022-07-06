from discord.ext import commands
import discord
import re
import requests
from modules import yktool, ytpy


async def search_archive(message: discord.Message, video):
    if re.match(r'^https?://', video):
        if not ytpy.is_youtube(video):
            await message.channel.send("YouTube動画のURLを入力してください！")
            return
    
    video = ytpy.Video(video)
    await message.reply(f"{video.url} のアーカイブを取得します…", mention_author=False)

    # アーカイブの取得
    async with message.channel.typing():
        archive = ytpy.Archive(video.url)

    if archive.url:
        # 動画情報の取得
        #async with message.channel.channel.typing():
        #    info = archive.get_info()

        author = f"`{author}`" if (author := archive.get_channel_name()) else "※取得できませんでした"
        title = f"`{title}`" if (title := archive.get_video_title()) else "※取得できませんでした"
        
        embed = discord.Embed(title="アーカイブが見つかりました！", description=f'[アーカイブURL]({archive.url})\nタイトル: {title}\nチャンネル名: {author}')
        await message.channel.send(embed=embed)
    else:
        await message.channel.send("アーカイブは見つかりませんでした…")


async def get_direct_video(ctx: commands.Context, url):
    if not url:
        if ctx.message.reference:
        
            try:
                reference_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
                url = re.match(r'^(https?://(youtu.be/|www.youtube.com/watch\?v=)[_\-,0-9,a-z,A-Z]*)', reference_msg.content).group()
            except Exception as e:
                return -1
            
            if not url:
                return -1
        else:
            return -2
    
    video = ytpy.Video(url)
    
    if video.is_available():
        direct_link = video.get_direct_link()

        try:
            res = requests.post("https://is.gd/create.php", {"url": direct_link})
            shorted_url = re.findall(r'(?<=id="short_url" value=")(.*)(?=" onclick="select_text\(\);")', res.content.decode("utf-8"))
            return shorted_url[0]
        except Exception as e:
            print(e)
            return -3
    else:
        return -4


class YouTube(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        
    # YouTube でアクセスできなくなった動画のアーカイブを検索
    @commands.command()
    async def archive(self, ctx: commands.Context, video = ""):
        await search_archive(ctx.message, video)
    
    @commands.command(name="videoinfo")
    async def get_video_info(self, ctx: commands.Context, url):
        video = ytpy.Video(url)
        video_info = video.get_video_info()
        embed = discord.Embed(title=video_info["title"], description=f'アップローダー: [{video_info["author_name"]}]({video_info["author_url"]})', url=video.url)
        embed.set_thumbnail(url=video_info["thumbnail_url"])
        
        await ctx.send(embed=embed)
    
    @commands.command(aliases=["tovid", "2vid"])
    async def tovideo(self, ctx: commands.Context, url = None):
        msg = await ctx.message.reply("動画のダイレクトリンクを取得中…", mention_author=False)
        
        async with ctx.channel.typing():
            result = await get_direct_video(ctx, url)
        
        if result == -1:
            await msg.edit(content="URLを確認できませんでした…")
        elif result == -2:
            await msg.edit(content=f"`{self.bot.command_prefix}tovideo url`\nもしくはYouTube動画のURLを含んだメッセージを返信しながら使用してください")
        elif result == -3:
            await msg.edit(content="ダイレクトリンクの取得に問題が発生したようです…\n開発者 (`やくると#6140`) に連絡してください")
        elif result == -4:
            await msg.edit(content="URLが有効ではありません")
        else:
            await msg.edit(content=result)
    
    @commands.command(aliases=["toaud", "2aud"])
    async def toaudio(self, ctx: commands.Context, url):
        if not ytpy.is_youtube(url):
            await ctx.message.reply("YouTube動画のリンクを入力してください!!", mention_author=False)
            return
    
        msg = await ctx.message.reply("音声のダイレクトリンク(m4a)を取得中…", mention_author=False)
        
        async with ctx.channel.typing():
            video = ytpy.Video(url)
            if video.is_available():
                link = video.mp3_direct_link("m4a")
            else:
                link = None
        
        if link:
            await msg.edit(content="", embed=discord.Embed(title=f"リンク", url=link))
        else:
            await msg.edit(content="動画にアクセスできませんでした")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith(self.bot.command_prefix):
            return

        if url := yktool.find_url(message.content):
            if len(url) == 1 and ytpy.is_youtube(url[0]):
                check_video = ytpy.Video(url[0])
                if check_video.id and not check_video.is_available():
                    await message.add_reaction("🔍")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
    
        channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        search_emoji = discord.utils.find(lambda m: m.emoji == str(payload.emoji), message.reactions)

        if search_emoji and message.author.id == payload.user_id:
            if [x async for x in search_emoji.users() if x.id == self.bot.user.id]:
            
                # アクセスが出来なくなったYouTube動画のアーカイブ検索
                if str(payload.emoji) == "🔍":
                    if url := yktool.find_url(message.content):
                        if len(url) == 1 and ytpy.is_youtube(url[0]):
                            await message.clear_reaction("🔍")
                            await search_archive(message, url[0])


def setup(bot):
    bot.add_cog(YouTube(bot))
