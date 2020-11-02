import discord
from discord.ext import commands
import json
import datetime
import os

# Loads the priviliged ones too, in the current state they're not particularly in much use but plans for later features
# will require
intents = discord.Intents.all()

# Bot token saved in a json file with the key "bot_token"
TOKEN = os.environ['DATABASE_URL']

# Basic stuffs
bot = commands.Bot(command_prefix='.', intents=intents)
bot.remove_command('help')


# Adding it to the log
@bot.event
async def on_ready():
    print(f"Successfully started process at {datetime.datetime.now()}")
    game = discord.Game("Type .help for usage")
    await bot.change_presence(status=discord.Status.online, activity=game)


# Loading up all the extensions here, done individually so any one can be taken down temporarily just by commenting
# out that line. Remember that the directories are period separated.
bot.load_extension('exts.utility')
bot.load_extension('exts.solos.helpcmd')
bot.load_extension('exts.moderation')
bot.load_extension('exts.level_system')
bot.load_extension('exts.fun')
bot.load_extension('exts.administration')
bot.run(TOKEN)
