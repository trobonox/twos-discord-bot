import discord, logging, random
from discord.ext import commands
from utils import config

config = config.config()

class welcome(commands.Cog):
    def __init__(self, client):
        logging.info(f"Loaded {self.__class__.__name__.title()} module.")

        self.client = client
        self.welcome_prompts = self.load_welcome_prompts()
    
    def load_welcome_prompts(self):
        with open('prompts.txt') as file:
            return file.readlines()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        # If we are not in the configured server, ignore any joins
        if guild.id != config.guild:
            return

        if guild.system_channel is not None:
            welcome_message = f"Hi {member.mention}, welcome to the Happy Twosday Community! {random.choice(self.welcome_prompts)}"
            await guild.system_channel.send(welcome_message)

    @commands.command(
        command="showprompts", brief="Shows the currently loaded welcome prompts."
    )
    @commands.has_permissions(manage_guild=True)
    async def showprompts(self, ctx):
        prompts = "**Prompts**\n"
        counter = 1

        for prompt in self.welcome_prompts:
            prompts += f"{counter} - {prompt}"
            counter += 1

        await ctx.send(prompts)

    @commands.command(
        command="addprompt", brief="Adds a prompt."
    )
    @commands.has_permissions(manage_guild=True)
    async def addprompt(self, ctx, prompt):
        with open('prompts.txt', 'a') as file:
            file.write(f"{prompt}\n")

        await ctx.send(f"Successfully added prompt '{prompt}'. Please reload the welcome module to enable the prompt.")

    @commands.command(
        command="removeprompt", brief="Removes a prompt"
    )
    @commands.has_permissions(manage_server=True)
    async def removeprompt(self, ctx, prompt_number: int):
        with open("prompts.txt", "r+") as f:
            lines = f.readlines()
            del lines[prompt_number - 1]
            f.seek(0)
            f.truncate()
            f.writelines(lines)

        await ctx.send(f"Successfully removed prompt #{prompt_number}. Please reload the welcome module to enable the prompt.")

async def setup(client):
    await client.add_cog(welcome(client))