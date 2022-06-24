import discord
from modules import yktool
import random


client = discord.Client()
config = yktool.load_config()


@client.event
async def on_ready():
    print("ready")


@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content == "y/servers":
        guilds = [f"{x.name} : {x.id}" async for x in client.fetch_guilds()]
        await message.channel.send(f"導入サーバー一覧：\n" + "\n".join(guilds))


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    channel: discord.TextChannel = await client.fetch_channel(payload.channel_id)
    user = await channel.guild.fetch_member(payload.user_id)
    message = await channel.fetch_message(payload.message_id)

    if str(payload.emoji) == "💥":
        damage = random.randint(1, 100000)
        await message.reply(f"{user.mention} の攻撃！:boom:\n{message.author.name} に {damage} のダメージ！", mention_author=False)


client.run(config["token"])
