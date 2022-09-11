from unicodedata import name
import discord
import logging

from utils import config
from discord.ext import commands

# Bot version
__version__ = "1.0.0"

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

## Activity status
activity = discord.Activity(type=discord.ActivityType.listening, name=config.status)

## Client init
bot = commands.Bot(command_prefix=config.prefix, intents=intents, activity=activity)


@bot.event
async def on_ready():
    logging.info(
        f"Bot v{__version__} started and logged in as {bot.user}. Running discord.py version {discord.__version__}."
    )


@bot.event
async def on_member_join(member):
    guild = member.guild

    # If we are not in the configured server, ignore any joins
    if guild.id != config.guild:
        return

    if guild.system_channel is not None:
        welcome_message = f"Hi {member.mention}, welcome to the Twosday Community! Let us know if there is any *thing* we can help with and happy Twosday ✌"
        await guild.system_channel.send(welcome_message)


bot.run(config.token)
