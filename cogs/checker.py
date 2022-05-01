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

        matches = re.findall(r'(aviutl|aviutil)', check_text, flags=re.IGNORECASE)
    
        # AviUtl をスペルミスしてないか確認
        if wrong := [x for x in matches if not x == "AviUtl"]:
            # 煽りメッセージの定義
            aori_messages = [
                "`AviUtl`、ねｗ　二度と間違えないでもろてｗ",
                "`AviUtl` だカス　間違えるなボケカスアホ　カス\n\nアホ",
                "おっと。正しいスペルは `AviUtl` です。これを見てください。\nhttp://spring-fragrance.mints.ne.jp/aviutl/\nサイト名にも書いてあるように、 `AviUtl` が正しいスペルですので、間違えないようにしましょうね。ｗ",
                "**AviUtl** だが？ｗ"
            ]
            
            # 一回のみのスペルミスだったら:
            if len(wrong) == 1:
                wrong = wrong[0]
                aori_messages += [
                    f"`{wrong}` じゃなく、 `AviUtl` だぞ？？今後このような間違えはしないようにねｗ スペルミスは、死ゾ！！ｗ",
                    f"{wrong} ってなんすかｗ\nもしかして **AviUtl** のことっすか？ｗ",
                    f"そっちの世界、`AviUtl` のこと {wrong} って言うんすねｗダサｗ",
                    f"なに {wrong} って　**AviUtl** なら知ってるけど {wrong} は知らんわｗ\n{wrong} ってのがあるん？ｗ",
                    f"はいはーい {wrong} じゃなくて **AviUtl** ねー　間違えないようにしてねー",
                    f"{wrong} …ｗ　いやごめんｗ `AviUtl` のこと {wrong} って呼ぶ人、なんか頭悪そうで…あいやｗごめんｗ",
                    f":x: {wrong}\n:o: AviUtl\n\nこんな一般常識も知らないんスカｗ",
                    f"うーわ…たまにいるんだよね **AviUtl** を aviutl だとか Aviutl だとか言う人ｗ\nいつも {wrong} って呼び方してるわけ？ｗ",
                    f"{wrong}…面白い冗談ですね、**AviUtl**をそのように表記するとは。\nスペル…**AviUtl**が正式名称ですよ。\nhttp://spring-fragrance.mints.ne.jp/aviutl/"
                ]
        
            # ランダムで煽る
            await message.reply(random.choice(aori_messages))

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
                            embed = discord.Embed(title=quote_message.author.display_name, description=quote_message.content + f"\n\n[メッセージにジャンプ]({url[0]})")
                            embed.set_thumbnail(url=quote_message.author.avatar.url)
                            embed.set_footer(text=f"{message.author.display_name} が引用: #{quote_channel.name}", icon_url=message.author.avatar.url)
                        await message.reply(embed=embed, mention_author=False)


# コグをセットアップするために必要
def setup(bot):
    bot.add_cog(Checker(bot))
