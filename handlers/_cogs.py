from discord.ext import commands
from pathlib import Path
import traceback


class CogHandler:
    def __init__(self, cogs_dir=Path(__file__).parent.parent / "cogs"):
        self.cogs_dir = cogs_dir

    def get_cogs(self):
        """List of files inside cogs folder"""

        cogs_list = []
        for cog in self.cogs_dir.iterdir():
            if cog.name.endswith(".py"):
                try:
                    cogs_list.append(cog.name[:-3])
                except Exception:
                    traceback.print_exc()
        return cogs_list

    async def load_cogs(self, bot: commands.Bot):
        """Load all cogs at once"""
        loaded = []
        failed = []
        cog_list = self.get_cogs()
        if cog_list == []:
            return [], []
        else:
            await bot.load_extension('jishaku')
            for cog in cog_list:
                try:
                    await bot.load_extension(f"cogs.{cog}")
                    loaded.append(cog)
                except Exception:
                    failed.append(f"{cog} : {traceback.format_exc()}")
            return loaded, failed

    async def load_cog(self, bot: commands.Bot, cog_name: str):
        try:
            await bot.load_extension(f"cogs.{cog_name}")
            return f"Successfully Loaded {cog_name}"
        except Exception as e:
            return f"Failed To Load : `{cog_name}` : {e}"

    async def unload_cog(self, bot: commands.Bot, cog_name: str):
        if cog_name == "cogmanager":
            return "Unable To Unload This Extension"
        try:
            await bot.unload_extension(f"cogs.{cog_name}")
            return f"Successfully Unloaded {cog_name}"
        except Exception as e:
            return f"Failed To Load `{cog_name}`: {e}"

    async def unload_cogs(self, bot: commands.Bot):
        """Unload all cogs at once"""
        unloaded = []
        failed = []
        cog_list = self.get_cogs()
        if cog_list == []:
            return [], []
        else:
            for cog in cog_list:
                if cog == "cogmanager":
                    pass
                try:
                    await bot.unload_extension(f"cogs.{cog}")
                    unloaded.append(cog)
                except Exception:
                    failed.append(f"{cog} : {traceback.format_exc()}")
            return unloaded, failed
