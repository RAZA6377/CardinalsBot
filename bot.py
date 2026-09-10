# Cardinals Discord Bot By raza.py
from __future__ import annotations

import discord
from discord.ext import commands
from termcolor import colored
import traceback
import asyncio
import io
import textwrap
from contextlib import redirect_stdout
from dotenv import load_dotenv
import os
import typing

# --- Handlers ---
from handlers._cogs import CogHandler
from handlers._printer import ColorPrint
from handlers._data import DataManager
from handlers._account import BsAccount

# --- Handlers ----
load_dotenv()
token = os.getenv("BOT_TOKEN")


class CardinalsBot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
    ):
        super().__init__(
            command_prefix=command_prefix,
            intents=discord.Intents.all(),
            owner_id=924617239301324856,
            application_id=1539681826002575491,
        )

        try:
            self.acc_manager = BsAccount
            self.cog_handler = CogHandler
            self.data_manager = DataManager
            self.color_printer = ColorPrint
        except Exception:
            traceback.print_exc()

    async def setup_hook(self):
        try:
            slash_synced = await self.tree.sync()
            print(
                colored(
                    f"Loaded Tree Commands: {len(slash_synced)}", "black", "on_cyan"
                )
            )
        except Exception as e:
            print(e)

    async def on_ready(self):

        bot_ready = colored(
            f"{self.user} Is Started\nPrefix : {self.command_prefix}",
            "black",
            "on_cyan",
        )
        print(bot_ready)


bot = CardinalsBot(command_prefix="c.")


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:-1])
    return content.strip("` \n")


@bot.command(hidden=True, name="eval")
@commands.is_owner()
async def eval(ctx: commands.Context, *, body: str):
    """Evaluates a code"""
    env = {
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
    }
    env.update(globals())
    body = cleanup_code(body)
    stdout = io.StringIO()
    to_compile = f"async def func():\n{textwrap.indent(body, '  ')}"
    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")
    func = env["func"]
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception:
        value = stdout.getvalue()
        await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction("\u2705")
        except Exception:
            pass
        if ret is None:
            if value:
                await ctx.send(f"```py\n{value}\n```")
        else:
            await ctx.send(f"```py\n{value}{ret}\n```")


@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: typing.Optional[typing.Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()
        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return
    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1
    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def main():
    """Main function for starting bot and loading cogs once bot is ready"""
    loaded, failed = await bot.cog_handler().load_cogs(bot)
    bot.color_printer.success(f"Loaded Cogs : {loaded}")
    bot.color_printer.failed(f"Failed Cogs : {failed}")
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
