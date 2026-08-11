import discord
from discord.ext import commands
from pathlib import Path
import traceback

class CogManager:
    def __init__(
        self,
        cogs_dir = Path(__file__).parent.parent / 'cogs'
   ):
       self.cogs_dir = cogs_dir
       
    def get_cogs(self):
        '''List of files inside cogs folder'''
        
        cogs_list = []
        for cog in self.cogs_dir.iterdir():
            if cog.name.endswith('.py'):
                try:
                    cogs_list.append(cog.name[:-3])
                except Exception:
                    traceback.print_exc()
        return cogs_list
        
    async def load_cogs(self, bot: commands.Bot):
        loaded = []
        failed = []
        cog_list = self.get_cogs()
        if cog_list == []:
            return [], []
        else:
            for cog in cog_list:
                try:
                    
                    await bot.load_extension(f"cogs.{cog}")
                    loaded.append(cog)
                except Exception:
                    failed.append(f"{cog} : {traceback.format_exc()}")
            return loaded, failed
            
    
        