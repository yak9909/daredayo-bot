import discord
from discord.ext import commands


class Yomiage(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        channel = await self.bot.fetch_channel(921297377858572308)

        if member.guild.id == 908140851442618379:
            if after.channel:
                if len(after.channel.members) > 0:
                    await channel.send(f"{member.mention} が {after.channel.mention} で通話を開始しました")
            else:
                if len(before.channel.members) == 0:
                    await channel.send(f"{before.channel.mention} 通話が終了しました")


def setup(bot: commands.Bot):
    bot.add_cog(Yomiage(bot))
