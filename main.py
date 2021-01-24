import os
import discord
from discord.ext import commands
from settings import *

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="#", intents=intents)

for file in os.listdir("./cogs"):
    if file.endswith(".py") and file != "__init__.py":
        bot.load_extension(f'cogs.{file[:-3]}')

bot.run(DISCORD_BOT_TOKEN)
