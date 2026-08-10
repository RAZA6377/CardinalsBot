import discord
from discord.ext import commands
from pathlib import Path
import sys
import traceback

class CogManager:
    def __init__(
        self,
        bot : commands.Bot,
        cogs_dir = Path(__file__).parent.parent / 'cogs'
   ):
       self.cogs_dir = cogs_dir
       self.bot = bot
       
    def get_cogs(self):
        cogs_list = []
        cogs_files = self.cogs_dir.rglob('*.py')
        for cog in cogs_files:
            try:
                cogs_list.append(cog)
            except Exception as e:
                print(e)
                pass
        return cogs_list
        
    async def load_cogs(self):
        loaded = []
        failed = []
        cog_list = self.get_cogs()
        if cog_list == []:
            return "No cogs found", self.cogs_dir
        else:
            for cog in cog_list:
                try:
                    await self.bot.load_extension(cog)
                    loaded.append(cog)
                except Exception as e:
                    failed.append(f"{cog} : {traceback.print_exc()}")
            return loaded, failed
            
    
        