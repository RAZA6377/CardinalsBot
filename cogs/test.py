import discord
from discord.ext import commands
from discord import app_commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="emojis", description="emoji testing command")
    async def hello(self, interaction: discord.Interaction):
        for i in interaction.guild.emojis:
            
        await interaction.response.send_message(interaction.guild.emojis)
        print(emoji)


async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))
