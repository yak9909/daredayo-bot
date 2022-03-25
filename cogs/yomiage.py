import discord
from discord.ext import commands


class Yomiage(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        channel = await self.bot.fetch_channel(921297377858572308)

        if not before.channel:
            await channel.send(f"{after.channel.mention} {member.mention} おっぱい")

        if not after.channel:
            await channel.send(f"{member.mention} ちんちん・・・")


def setup(bot: commands.Bot):
    bot.add_cog(Yomiage(bot))
