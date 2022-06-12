from discord.ext import commands
import discord
import random
import re
import requests
from cogs import tools, help
from modules import yktool, ytpy
from modules.server import Server


async def get_quoter_webhook(channel):
    quote_webhook = discord.utils.find(lambda m: m.name == "Quoter", await channel.webhooks())
    if not quote_webhook:
        quote_webhook = await channel.create_webhook(name="Quoter")

    return quote_webhook


class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.kusodomains_map = {
            "https://soude.su/"                     : r'そう(です|(わ|だ)?よ)',
            "https://imanona.si/"                   : r'(いま|今)の(な|無)し',
            "https://mouyuru.site/"                 : r'(もう)?(ゆる|許)して(ください)?',
            "https://iyado.su/"                     : r'(や|いや|嫌)(だ|です|どす)',
            "https://nasa.so/"                      : r'(な|無)さそう',
            "https://otsu.care/"                    : r'(乙|(お(つか|疲)れ(さま|様)?)|おつ|o2|02)',
            "https://yoroshiku.onegai.shim.earth/"  : r'((よろ|宜)(し(く|こ)(お(ねが|願)いします)?)?|4649)',
            "https://sounanokamoshiremasen.ga/"     : r'そう(なの)?(かも(しれ(ない(の)?|ません|ん)((だ)?が|けど)))',
            "https://ohayougozaima.su/"             : r'(お(はよ(う|ー)?|早う)(ございます)?|(お|起)き(た|ました))',
            "https://soujyanai.ga/"                 : r'((ちが|違)う|そうじゃ(な(い(が)?|くて(さ|ね)?|ね(え|ぇ|ー)(よ)?)))',
            "https://sorehako.ml/"                  : r'(それは)?(こま|困)る((ん|の)(だ|です)(が|けど))?',
            "https://shinchokuda.me/"               : r'(しんちょく|進捗)(だめ|ダメ)です(。)?'
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # TOKENの削除
        if yktool.find_token(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention} Tokenが検出されたので削除しました。")

        if message.author.bot:
            return
        
        srv = Server(message.guild.id)

        if message.content.startswith(self.bot.command_prefix):
            return

        # クソドメイン送りつける
        if srv.read_config(["reply", "kusodomain"], default=True):
            for k,v in self.kusodomains_map.items():
                if re.match(v, message.content):
                    await message.channel.send(k)

        if message.content == "<@881540558236024843>":
            await message.channel.send(f"helpコマンドは `{self.bot.command_prefix}help` と送信する事で実行できます", delete_after=8)

        if url := yktool.find_url(message.content):
            if len(url) == 1 and "discord.com/channels/" in url[0]:
                if str(message.guild.id) == url[0].split("/")[-3]:
                    await message.add_reaction("⤵️")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
    
        channel: discord.TextChannel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        search_emoji = discord.utils.find(lambda m: m.emoji == str(payload.emoji), message.reactions)

        if str(payload.emoji) == "🔀":
            shuffled_msg = ''.join(random.sample(message.content, len(message.content)))
            await message.reply(shuffled_msg, mention_author=False)

        if search_emoji and message.author.id == payload.user_id:
            if [x async for x in search_emoji.users() if x.id == self.bot.user.id]:
        
                # メッセージの引用
                if str(payload.emoji) == "⤵️":
                    if url := yktool.find_url(message.content):
                        async with message.channel.typing():
                            await message.clear_reaction("⤵️")
                            chid = url[0].split("/")[-2]
                            msgid = url[0].split("/")[-1]
                            quote_channel = await message.guild.fetch_channel(chid)
                            quote_message = await quote_channel.fetch_message(msgid)
                            embed = discord.Embed(description=f"\n\n[メッセージにジャンプ]({url[0]})")
                            embed.set_author(name=f"{message.author.display_name} が引用", icon_url=message.author.avatar.url)
                            embed.set_footer(text=f"#{quote_channel.name}")
                        webhook = await get_quoter_webhook(channel)

                        # メンションを無効化する
                        content = quote_message.content
                        for i in quote_message.mentions:
                            content = content.replace(i.mention, f"@‌{i.name}")
                        for i in quote_message.role_mentions:
                            content = content.replace(i.mention, f"@‌{i.name}")
                        content = content.replace("@everyone", "@‌everyone")
                        content = content.replace("@here", "@‌here")

                        try:
                            await webhook.send(
                                content=content,
                                embed=embed,
                                username=quote_message.author.name,
                                avatar_url=quote_message.author.avatar.url,
                                files=[await x.to_file() for x in quote_message.attachments]
                            )
                        except discord.errors.HTTPException:
                            await webhook.send(
                                content=content,
                                embed=embed,
                                username=quote_message.author.name,
                                avatar_url=quote_message.author.avatar.url
                            )


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Checker(bot))
