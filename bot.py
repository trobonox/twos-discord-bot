import os
import sys
import random
import discord
import logging
import traceback

from utils import config, db
from discord.ext import commands

# Bot version
__version__ = "1.2.0"

# Load external JSON config
config = config.config()

# Extend default logging configuration
logging.basicConfig(
    format=" %(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d - %H:%M:%S",
    level=logging.INFO,
)

# Client setup
## Privileged gateway intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

## Activity status
activity = discord.Activity(type=discord.ActivityType.listening, name=config.status)

## Client init
bot = commands.Bot(command_prefix=config.prefix, intents=intents, activity=activity)


@bot.event
async def on_ready():
    logging.info(
        f"Bot v{__version__} started and logged in as {bot.user}. Running discord.py version {discord.__version__}."
    )

    db.init_db()

    await bot.load_extension("help")
    await loadModules()

async def loadModules():
    for filename in os.listdir("./modules"):
        if filename.endswith(".py"):
            await bot.load_extension(f"modules.{filename[:-3]}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    elif isinstance(error, commands.MissingPermissions):
        await ctx.reply("Error: You do not have permissions to do that!")
        return

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(
            f"Error: Please provide the required argument `{error.param.name}`! Use `{config.prefix}help [category]` for more info."
        )
        return

    elif isinstance(error, commands.BadArgument):
        await ctx.reply(
            f'Error: Invalid argument, please check if your arguments are correct! *Make sure you use quotes ("") for names or a text that has a space in it!*\n Use `{config.prefix}help [category]` for more info.'
        )
        return

    elif isinstance(error, commands.CheckFailure):
        return

    else:
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return

    await bot.process_commands(message)


@bot.command(name="poll")
async def poll(ctx, question, *options: str):
    if len(options) <= 1:
        await ctx.send("You need more than one option to make a poll!")
        return
    if len(options) > 10:
        await ctx.send("You cannot make a poll with more than 10 options!")
        return

    if len(options) == 2 and options[0] == "yes" and options[1] == "no":
        reactions = ["✅", "❌"]
    else:
        reactions = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]

    poll_content = []
    for index, option in enumerate(options):
        poll_content += "\n {} {}".format(reactions[index], option)

    embed = discord.Embed(title=question, description="".join(poll_content))
    poll_message = await ctx.send(embed=embed)

    for reaction in reactions[: len(options)]:
        await poll_message.add_reaction(reaction)


bot.run(config.token)
