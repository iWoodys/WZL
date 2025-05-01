import discord
from discord.ext import commands, tasks
import os
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
OWNER_ID = int(os.getenv('OWNER_ID'))
BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

# ⚠️ Reemplazá este valor por el ID del canal que querés actualizar
GUILD_COUNT_CHANNEL_ID = 1367591515416825876

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

    # Iniciar tarea de actualización del canal
    actualizar_nombre_canal.start()

@tasks.loop(minutes=10)
async def actualizar_nombre_canal():
    canal = bot.get_channel(GUILD_COUNT_CHANNEL_ID)
    if canal:
        try:
            num_guilds = len(bot.guilds)
            nuevo_nombre = f"🌐 En {num_guilds} servidores"
            await canal.edit(name=nuevo_nombre)
        except Exception as e:
            print(f"❌ Error al actualizar el canal: {e}")
    else:
        print("⚠️ Canal no encontrado. Revisá el ID.")

async def load_extensions():
    await bot.load_extension("cogs.warzone")
    await bot.load_extension("cogs.premium_commands")

async def main():
    keep_alive()
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
