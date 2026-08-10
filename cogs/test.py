import discord
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='hello', description='testing command')
    async def hello(self, ctx):
        await ctx.send('Hello There!')
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))