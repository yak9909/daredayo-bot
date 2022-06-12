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
    @commands.has_permissions(administrator=True)
    async def kusodomain(self, ctx: commands.Context, value = None):
        srv = Server(ctx.guild.id)
        if value is None:
            await ctx.send(f"メッセージに対してクソドメインを送りつける迷惑機能です\n"
                           f"現在 {srv.read_config(['reply', 'kusodomain'], default=True)} に設定されています")
            return
        
        value = yktool.format_toggle(value)
        if value is None:
            await ctx.reply("設定値は `True` か `False` にしてください")
            return
        
        srv.write_config({"reply": {"kusodomain": value}})
        await ctx.reply(f"クソドメインの送りつけを" + ("有効" if value else "無効") + "にしました")
    
    @kusodomain.error
    async def kusodomain_error(self, ctx: commands.Context, error: commands.errors):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply("設定値は `True` か `False` にしてください")
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"`管理者` 権限が有効なユーザーにのみ実行可能なコマンドです")
    
    @config.command(name="aviutl")
    @commands.has_permissions(administrator=True)
    async def aviutl_spellcheck(self, ctx: commands.Context, value = None):
        srv = Server(ctx.guild.id)
        if value is None:
            await ctx.send(f"AviUtl の誤表記をゴミクソうざい煽り文で指摘してくるクソ機能です\n"
                           f"現在 {srv.read_config(['reply', 'aviutl'], default=True)} に設定されています")
            return
        
        value = yktool.format_toggle(value)
        if value is None:
            await ctx.reply("設定値は `True` か `False` にしてください")
            return
        
        srv.write_config({"reply": {"aviutl": value}})
        await ctx.reply(f"AviUtl 誤表記指摘を" + ("有効" if value else "無効") + "にしました")
    
    @aviutl_spellcheck.error
    async def aviutl_error(self, ctx: commands.Context, error: commands.errors):
        if isinstance(error, commands.errors.BadArgument):
            await ctx.reply("設定値は `True` か `False` にしてください")
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(f"`管理者` 権限が有効なユーザーにのみ実行可能なコマンドです")


def setup(bot):
    bot.add_cog(Configure(bot))
