import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True  # Por si usas eventos de voz en warzone.py
intents.message_content = True  # MUY IMPORTANTE para slash commands o texto

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="2.783.128 Players in Warzone"))
    print(f'Logged in as {bot.user}')

async def load_extensions():
    await bot.load_extension("cogs.warzone")

async def main():
    keep_alive()  # Levanta el servidor Flask para mantener Render activo
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
