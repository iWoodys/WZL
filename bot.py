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
LOG_CHANNEL_ID = 1367591515416825876  # 👈 Reemplazá esto por el ID de tu canal de logs

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

@bot.event
async def on_guild_join(guild):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if not log_channel:
        print("No se encontró el canal de log.")
        return

    invite_link = "No se pudo crear invitación"
    try:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                invite = await channel.create_invite(max_age=3600, max_uses=1)
                invite_link = invite.url
                break
    except Exception as e:
        print(f"No se pudo crear la invitación: {e}")

    embed = discord.Embed(
        title="🔔 Nuevo servidor detectado",
        color=discord.Color.green()
    )
    embed.add_field(name="📛 Nombre", value=guild.name, inline=False)
    embed.add_field(name="🆔 ID", value=str(guild.id), inline=False)
    embed.add_field(name="🔗 Invitación", value=invite_link, inline=False)
    embed.set_footer(text=f"Tiene {guild.member_count} miembros")

    await log_channel.send(embed=embed)

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
