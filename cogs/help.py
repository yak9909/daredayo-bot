from discord.ext import commands
import discord
import json
from modules import yktool
import math


class HelpPage(discord.ui.View):
    def __init__(self, references, category, max_items=3):
        super().__init__()

        self.references = references
        self.category = category

        self.current_page = 0
        self.max_page = 0
        self.max_items = max_items


class HelpDropdown(discord.ui.Select):
    def __init__(self, references):
        self.references = references
        self.selected = None

        options = []
        for k, v in self.references.items():
            options.append(discord.SelectOption(label=k, description=v["description"]))

        super().__init__(placeholder="カテゴリーを選択してください…", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.selected = self.references[self.values[0]]
        self.placeholder = self.values[0]
        self.view.current_page = 0
        embed = self.view.update()
        await interaction.message.edit(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, help_path, max_items=3):
        super().__init__()

        self.references = json.load(open(help_path, mode="r+", encoding="utf-8"))

        self.current_page = 0
        self.max_page = 0
        self.command_count = 0
        self.max_items = max_items

        self.prefix = yktool.load_config()["prefix"]

        self.help_dropdown = HelpDropdown(self.references)

        self.add_item(self.help_dropdown)

    @discord.ui.button(label="←", disabled=True)
    async def previous(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page -= 1
        embed = self.update()
        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="→", disabled=True)
    async def next(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current_page += 1
        embed = self.update()
        await interaction.message.edit(embed=embed, view=self)

    def update(self):
        self.command_count = len(self.help_dropdown.selected["commands"])
        self.max_page = math.ceil(self.command_count/self.max_items) - 1

        embed = discord.Embed(
            title=f"カテゴリ: {self.help_dropdown.values[0]} {self.current_page+1}/{self.max_page+1}",
            description=self.help_dropdown.selected["description"]
        )

        for i in range(self.current_page*self.max_items, min((self.current_page*self.max_items+self.max_items, self.command_count))):
            current_command = self.help_dropdown.selected["commands"][i]
            description = current_command["description"]
            usage = current_command["usage"].replace("%prefix%", self.prefix)

            embed.add_field(
                name=self.prefix + current_command["command"],
                value=f'{description}\n\n__**使い方**__\n```{usage}\n```\n――――――――――――――――',
                inline=False
            )

        self.previous.disabled = self.current_page <= 0
        self.next.disabled = self.current_page >= self.max_page

        return embed


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.help_path = "data/help.json"

    @commands.command(name="help")
    async def help_command(self, ctx: commands.Context, query=None):
        if query:
            return

        embed = discord.Embed(
            title="誰だよ botリファレンス",
            description="<@880946481002061845> が開発している誰だよbotのコマンド一覧が記載されています\n"
            "このメッセージに追加されているリストボックスから、\n"
            "コマンドのカテゴリーを選択してください"
        )

        category_view = HelpView(self.help_path, 2)

        await ctx.send(embed=embed, view=category_view)


def setup(bot):
    bot.add_cog(Help(bot))
