import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="en Twitch"))
    print(f'Logged in as {bot.user}')

bot.load_extension("cogs.warzone")

keep_alive()
bot.run(TOKEN)
