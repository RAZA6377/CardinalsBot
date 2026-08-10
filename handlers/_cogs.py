import discord
from discord.ext import commands
from pathlib import Path
import os
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
        for cog in os.listdir(self.cogs_dir):
            if cog.endswith('.py'):
                try:
                    cogs_list.append(cog[:-3])
                except Exception:
                    traceback.print_exc()
        return cogs_list
        
    async def load_cogs(self, bot: commands.Bot):
        loaded = []
        failed = []
        cog_list = self.get_cogs()
        if cog_list == []:
            return "No cogs found", self.cogs_dir
        else:
            for cog in cog_list:
                try:
                    
                    await bot.load_extension(f"cogs.{cog}")
                    loaded.append(cog)
                except Exception as e:
                    failed.append(f"{cog} : {traceback.print_exc()}")
            return loaded, failed
            
    
        