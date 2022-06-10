from discord.ext import commands


class AntiSpam(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command
    async def test3(self, ctx: commands.Context):
        await ctx.send("test33333")

def setup(bot):
    bot: commands.Bot
    bot.add_cog(AntiSpam(bot))
