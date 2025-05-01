import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="2.783.128 Players in Warzone"
    ))
    print(f'✅ Bot conectado como {bot.user}')
    print(f'✅ Comandos slash sincronizados: {len(synced)}')

async def load_extensions():
    await bot.load_extension("cogs.warzone")
    await bot.load_extension("cogs.premium_commands")

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
