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


class YouTube(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        
    # YouTube でアクセスできなくなった動画のアーカイブを検索
    @commands.command()
    async def archive(self, ctx: commands.Context, video = ""):
        await search_archive(ctx.message, video)
    
    @commands.command()
    async def teest(self, ctx: commands.Context, video = "bb"):
        archive_url = f"http://archive.org/wayback/available?url=http://www.youtube.com/watch?v={video}"
        r = requests.get(archive_url)
        await ctx.send(r.content)
    
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
