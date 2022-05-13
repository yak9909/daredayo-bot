from discord.ext import commands
import discord
import random
import re
import requests
from cogs import tools
from cogs import help


# 文字列内からURLを抽出
def find_url(text):
    # findall() 正規表現に一致する文字列を検索する
    url = re.findall(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', text)
    return url 


def find_token(text):
    token = re.findall(r'[M-Z][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}', text)
    return token


def check_video_url(video_id):
    checker_url = "https://www.youtube.com/oembed?url=http://www.youtube.com/watch?v="
    video_url = checker_url + video_id
    request = requests.get(video_url)

    return request.status_code == 200


async def get_quoter_webhook(channel):
    quote_webhook = discord.utils.find(lambda m: m.name == "Quoter", await channel.webhooks())
    if not quote_webhook:
        quote_webhook = await channel.create_webhook(name="Quoter")

    return quote_webhook


class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # TOKENの削除
        if find_token(message.content):
            await message.delete()
            await message.channel.send(f"{message.author.mention} Tokenが検出されたので削除しました。")

        if message.author.bot:
            return

        check_text = message.content
        for i in find_url(check_text):
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

        if message.content.startswith(self.bot.command_prefix):
            return

        if message.content == "<@881540558236024843>":
            await message.channel.send(f"helpコマンドは `{self.bot.command_prefix}help` と送信する事で実行できます", delete_after=8)

        if url := find_url(message.content):
            if len(url) == 1 and "discord.com/channels/" in url[0]:
                if str(message.guild.id) == url[0].split("/")[-3]:
                    await message.add_reaction("⤵️")

        if url := find_url(message.content):
            if len(url) == 1 and url[0].startswith(("https://www.youtube.com/", "https://youtu.be/")):
                if not check_video_url(tools.url2id(url[0])):
                    await message.add_reaction("🔍")

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
            
                # アクセスが出来なくなったYouTube動画のアーカイブ検索
                if str(payload.emoji) == "🔍":
                    if url := find_url(message.content):
                        if len(url) == 1 and url[0].startswith(("https://www.youtube.com/", "https://youtu.be/")):
                            video_id = tools.url2id(url[0])

                            await message.clear_reaction("🔍")
                            await message.reply(f"https://youtu.be/{video_id} のアーカイブを取得します…", mention_author=False)

                            # アーカイブの取得
                            async with channel.typing():
                                archive = tools.get_video_archive(video_id)

                            if archive:
                                embed = discord.Embed(title="アーカイブが見つかりました！", description=f"[アーカイブURL]({archive})")
                                await channel.send(embed=embed)
                            else:
                                await channel.send("アーカイブは見つかりませんでした…")
        
                # メッセージの引用
                if str(payload.emoji) == "⤵️":
                    if url := find_url(message.content):
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
