# EntityX Discord Bot By raza.py
from __future__ import annotations

import discord
from discord.ext import commands
from colorama import init
from termcolor import colored
from handlers._cogs import CogManager
import traceback

class EntityX(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        ):
        
        super().__init__(
            command_prefix = command_prefix,
            intents = discord.Intents.all(),
            owner_id = 924617239301324856,
            application_id = 1238760771052245042         
          )
          
        try:
            self.cog_manager = CogManager(self)
        except Exception as e:
            print(e)
          
    async def setup_hook(self):
        try:
            loaded, failed = await bot.cog_manager.load_cogs()
            loaded_text = colored(f"Loaded Cogs : {loaded}", 'white', 'on_green')
            failed_text = colored(f"Failed To Load Cogs : {failed}", 'white', 'on_red')
            print(loaded_text)
            print(failed_text)
        except Exception as e:
            print(e)
            traceback.print_exc()
            pass

    async def on_ready(self):
        bot_ready = colored(f"{self.user} Is Started", 'black','on_cyan')
        print(bot_ready)
        
        
        
bot = EntityX(command_prefix='e.')
bot.run('MTIzODc2MDc3MTA1MjI0NTA0Mg.GgjXL_.mZouEX0uhtx-QdmB48bO7psYaMBbg6PWdzmPic')       