import discord
from discord.ext import commands
from discord import app_commands
from firebase import get_server_loadouts
from premium import is_premium
import asyncio
import os

from cogs.loadouts_buttons import LoadoutView

OWNER_ID = int(os.getenv('OWNER_ID'))

class Warzone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_channels = {}

    # /loadouts
    @app_commands.command(name="loadouts", description="Ver los loadouts disponibles.")
    async def loadouts(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if interaction.guild_id in self.guild_channels:
            if interaction.channel.id != self.guild_channels[interaction.guild_id]:
                await interaction.followup.send("Este comando solo puede usarse en el canal permitido.", ephemeral=True)
                return

        ref = get_server_loadouts(interaction.guild_id)
        docs = ref.stream()

        loadouts = []
        for doc in docs:
            data = doc.to_dict()
            loadouts.append((doc.id, data.get('title', doc.id)))

        if not loadouts:
            await interaction.followup.send("No hay loadouts disponibles.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}, estos son los loadouts actuales:",
            color=discord.Color.dark_green()
        )

        loadouts_text = "\n".join([f"{idx}. {title}" for idx, (_, title) in enumerate(loadouts, 1)])
        embed.add_field(name="Loadouts:", value=loadouts_text, inline=False)

        await interaction.followup.send(embed=embed, view=LoadoutView(ref, loadouts), ephemeral=False)

    # /add_load con validación premium
    @app_commands.command(name="add_load", description="Agregar un nuevo loadout.")
    @app_commands.default_permissions(administrator=True)
    async def add_load(self, interaction: discord.Interaction,
                       weapon_name: str, title: str, image_url: str,
                       optic: str = "NO", muzzle: str = "NO", barrel: str = "NO",
                       underbarrel: str = "NO", magazine: str = "NO",
                       rear_grip: str = "NO", fire_mods: str = "NO"):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        ref = get_server_loadouts(guild_id)

        docs = list(ref.stream())
        if not is_premium(user_id) and len(docs) >= 5:
            await interaction.response.send_message(
                "❌ Alcanzaste el límite de 5 loadouts. Hazte premium para guardar más.",
                ephemeral=True
            )
            return

        ref.document(weapon_name).set({
            "title": title,
            "image_url": image_url,
            "Optic": optic,
            "Muzzle": muzzle,
            "Barrel": barrel,
            "Underbarrel": underbarrel,
            "Magazine": magazine,
            "Rear Grip": rear_grip,
            "Fire Mods": fire_mods
        })

        await interaction.response.send_message(f"✅ Loadout `{title}` agregado correctamente.", ephemeral=True)

    # /edit_load con validación premium
    @app_commands.command(name="edit_load", description="Editar un loadout existente.")
    @app_commands.default_permissions(administrator=True)
    async def edit_load(self, interaction: discord.Interaction,
                        weapon_name: str,
                        optic: str = None, muzzle: str = None, barrel: str = None,
                        underbarrel: str = None, magazine: str = None,
                        rear_grip: str = None, fire_mods: str = None):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message(
                "❌ Este comando es exclusivo para usuarios premium.",
                ephemeral=True
            )
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc_ref = ref.document(weapon_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado.", ephemeral=True)
            return

        update_data = {}
        fields = {
            "Optic": optic, "Muzzle": muzzle, "Barrel": barrel,
            "Underbarrel": underbarrel, "Magazine": magazine,
            "Rear Grip": rear_grip, "Fire Mods": fire_mods
        }

        for key, value in fields.items():
            if value is not None:
                update_data[key] = value

        doc_ref.update(update_data)
        await interaction.response.send_message(f"Loadout `{weapon_name}` actualizado.", ephemeral=True)

    # /del_load con validación premium
    @app_commands.command(name="del_load", description="Eliminar un loadout.")
    @app_commands.default_permissions(administrator=True)
    async def del_load(self, interaction: discord.Interaction, weapon_name: str):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message(
                "❌ Este comando es exclusivo para usuarios premium.",
                ephemeral=True
            )
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc = ref.document(weapon_name).get()

        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado.", ephemeral=True)
            return

        ref.document(weapon_name).delete()
        await interaction.response.send_message(f"Loadout `{weapon_name}` eliminado correctamente.", ephemeral=True)

    # /offbot solo para el owner
    @app_commands.command(name="offbot", description="Expulsar al bot del servidor (solo el Owner).")
    async def offbot(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("No tienes permiso para usar este comando.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        channel = interaction.guild.text_channels[0]
        embed = discord.Embed(
            title="Gracias por utilizar el servidor",
            description="@everyone El bot se está desconectando. ¡Hasta pronto!",
            color=discord.Color.dark_green()
        )
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await interaction.guild.leave()

    # /setbot para canal exclusivo
    @app_commands.command(name="setbot", description="Restringir /loadouts a un canal específico.")
    @app_commands.default_permissions(administrator=True)
    async def setbot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.guild_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"Canal configurado: {channel.mention}", ephemeral=True)

    # /unsetbot para permitir en todos los canales
    @app_commands.command(name="unsetbot", description="Permitir que /loadouts se use en cualquier canal.")
    @app_commands.default_permissions(administrator=True)
    async def unsetbot(self, interaction: discord.Interaction):
        if interaction.guild_id in self.guild_channels:
            del self.guild_channels[interaction.guild_id]
            await interaction.response.send_message("Restricción de canal eliminada.", ephemeral=True)
        else:
            await interaction.response.send_message("No había restricciones activas.", ephemeral=True)

    # /info para mostrar información sobre el premium
    @app_commands.command(name="info", description="Información sobre cómo obtener premium.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="⭐ Información Premium",
            description=(
                "¿Quieres más loadouts, funciones exclusivas e invitar el bot a tu servidor?\n\n"
                "📩 Contacta directamente al desarrollador por Discord: `AkariiDEV`"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warzone(bot))

