# EntityX Discord Bot By raza.py
from __future__ import annotations

import discord
from discord.ext import commands
from termcolor import colored
from handlers._cogs import CogManager
from handlers._printer import ColorPrint
import traceback
import asyncio

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
            self.cog_manager = CogManager
            self.color_printer = ColorPrint
        except Exception:
            traceback.print_exc()

    async def on_ready(self):
        bot_ready = colored(f"{self.user} Is Started", 'black','on_cyan')
        print(bot_ready)
       
bot = EntityX(command_prefix='e.')

@bot.command(hidden=True, name='eval')
@commands.is_owner()
async def eval(ctx: commands.Context, *, body: str):
    """Evaluates a code"""
    env = {
        'bot': bot,
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message,
    }
    env.update(globals())
    body = cleanup_code(body)
    stdout = io.StringIO()
    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass
        if ret is None:
            if value:
                await ctx.send(f'```py\n{value}\n```')
        else:
            await ctx.send(f'```py\n{value}{ret}\n```')



async def main():
    '''Main function for starting bot and loading cogs once bot is ready'''
    loaded, failed = await bot.cog_manager().load_cogs(bot)
    bot.color_printer(f"Loaded Cogs : {loaded}").success()
    bot.color_printer(f"Failed Cogs : {failed}").failed()
    #print('starting bot')
    async with bot:
        await bot.start('MTIzODc2MDc3MTA1MjI0NTA0Mg.GgjXL_.mZouEX0uhtx-QdmB48bO7psYaMBbg6PWdzmPic')
        

if __name__ == "__main__":
    asyncio.run(main())