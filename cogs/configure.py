from discord.ext import commands
import discord
from modules import yktool
from modules.server import Server


class Configure(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot: commands.Bot = bot
        
    @commands.group()
    async def config(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.send("y/config kusodomain")
    
    @config.command()
    async def kusodomain(self, ctx: commands.Context, value = None):
        srv = Server(ctx.guild.id)
        if value is None:
            await ctx.send(f"メッセージに対してクソドメインを送りつける迷惑機能です\n"
                           f"現在 {srv.read_config('reply', 'kusodomain')} に設定されています")
            return
        
        if (value := yktool.format_toggle(value)) is None:
            await ctx.reply("設定値は `True` か `False` にしてください")
            return
        
        srv.write_config({"reply": {"kusodomain": value}})
        await ctx.reply(f"クソドメインの送りつけを" + ("有効" if value else "無効") + "にしました")
    
    @kusodomain.error
    async def kusodomain_error(self, ctx: commands.Context, error: commands.errors):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply("設定値は `True` か `False` にしてください")


def setup(bot):
    bot.add_cog(Configure(bot))
