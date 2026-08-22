from discord.ext import commands


class CogManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="cog", description="A cog command group", invoke_without_command=True
    )
    @commands.is_owner()
    async def manager_cog(self, ctx):
        available_sub = ["load", "unload", "list", "loadall", "unloadall", "reload", "reloadall"]
        await ctx.send(f"`Enter a valid subcommand` : {available_sub}")

    @manager_cog.command(name="load", description="Loads a cog")
    @commands.is_owner()
    async def load_cog(self, ctx, cog_name: str):
        result = await self.bot.cog_handler().load_cog(self.bot, cog_name)
        await ctx.send(result)

    @manager_cog.command(name="unload", description="Unloads a cog")
    @commands.is_owner()
    async def unload_cog(self, ctx, cog_name: str):
        result = await self.bot.cog_handler().unload_cog(self.bot, cog_name)
        await ctx.send(result)

    @manager_cog.command(name="unloadall", description="Unloads all cogs at once")
    @commands.is_owner()
    async def unloadall_cog(self, ctx):
        result = await self.bot.cog_handler().unload_cogs()
        await ctx.send(result)

    @manager_cog.command(name="loadall", description="Loads all cogs at once")
    @commands.is_owner()
    async def loadall_cogs(self, ctx):
        result = await self.bot.cog_handler().load_cogs(self.bot)
        await ctx.send(result)

    @manager_cog.command(name="list", description="List of cogs")
    @commands.is_owner()
    async def list_cogs(self, ctx):
        try:
            result = self.bot.cog_handler().get_cogs()
            print(result)
            await ctx.send(f"Available Cogs\n{result}")
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(CogManager(bot))
