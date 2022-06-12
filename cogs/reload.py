from discord.ext import commands
import discord
from modules import yktool


class Reload(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot

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


def setup(bot):
    bot.add_cog(Reload(bot))
