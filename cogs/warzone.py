import discord
from discord.ext import commands
from discord import app_commands
from firebase import get_server_loadouts
import asyncio
import os

from cogs.loadouts_buttons import LoadoutView  # 👈 Importamos el LoadoutView externo

OWNER_ID = int(os.getenv('OWNER_ID'))

class Warzone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_channels = {}

    # /loadouts
    @app_commands.command(name="loadouts", description="Ver los loadouts disponibles.")
    async def loadouts(self, interaction: discord.Interaction):
        await interaction.response.defer()

        # Verificar si el comando solo debe ejecutarse en un canal específico
        if interaction.guild_id in self.guild_channels:
            if interaction.channel.id != self.guild_channels[interaction.guild_id]:
                await interaction.followup.send("Este comando solo puede usarse en el canal permitido.", ephemeral=True)
                return

        # Obtener los loadouts de Firebase
        ref = get_server_loadouts(interaction.guild_id)
        docs = ref.stream()

        loadouts = []
        for doc in docs:
            data = doc.to_dict()
            loadouts.append((doc.id, data.get('title', doc.id)))

        if not loadouts:
            await interaction.followup.send("No hay loadouts disponibles.", ephemeral=True)
            return

        # Crear un embed con la lista de loadouts
        embed = discord.Embed(
            title=f"{interaction.user.display_name}, estos son los loadouts actuales:",
            color=discord.Color.dark_green()
        )

        for idx, (_, title) in enumerate(loadouts, 1):
            embed.add_field(name=f"{idx}.", value=title, inline=False)

        # Enviar el embed con los loadouts y los botones para interactuar con ellos
        await interaction.followup.send(embed=embed, view=LoadoutView(ref, loadouts), ephemeral=False)  # Esto es correcto: 'ephemeral=False' hace visible el mensaje para todos

    # Comando para agregar un nuevo loadout
    @app_commands.command(name="add_load", description="Agregar un nuevo loadout.")
    @app_commands.default_permissions(administrator=True)
    async def add_load(self, interaction: discord.Interaction,
                       weapon_name: str, title: str, image_url: str,
                       optic: str = "NO", muzzle: str = "NO", barrel: str = "NO",
                       underbarrel: str = "NO", magazine: str = "NO",
                       rear_grip: str = "NO", fire_mods: str = "NO"):
        ref = get_server_loadouts(interaction.guild_id)
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
        await interaction.response.send_message(f"Loadout `{title}` agregado correctamente.", ephemeral=True)

    # Comando para editar un loadout existente
    @app_commands.command(name="edit_load", description="Editar un loadout existente.")
    @app_commands.default_permissions(administrator=True)
    async def edit_load(self, interaction: discord.Interaction,
                        weapon_name: str,
                        optic: str = None, muzzle: str = None, barrel: str = None,
                        underbarrel: str = None, magazine: str = None,
                        rear_grip: str = None, fire_mods: str = None):
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

    # Comando para eliminar un loadout
    @app_commands.command(name="del_load", description="Eliminar un loadout.")
    @app_commands.default_permissions(administrator=True)
    async def del_load(self, interaction: discord.Interaction, weapon_name: str):
        ref = get_server_loadouts(interaction.guild_id)
        doc = ref.document(weapon_name).get()

        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado.", ephemeral=True)
            return

        ref.document(weapon_name).delete()
        await interaction.response.send_message(f"Loadout `{weapon_name}` eliminado correctamente.", ephemeral=True)

    # Comando para expulsar al bot
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

    # Comando para configurar un canal específico para usar el comando /loadouts
    @app_commands.command(name="setbot", description="Restringir /loadouts a un canal específico.")
    @app_commands.default_permissions(administrator=True)
    async def setbot(self, interaction: discord.Interaction, channel: discord.TextChannel):
        self.guild_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"Canal configurado: {channel.mention}", ephemeral=True)

    # Comando para eliminar la restricción del canal
    @app_commands.command(name="unsetbot", description="Permitir que /loadouts se use en cualquier canal.")
    @app_commands.default_permissions(administrator=True)
    async def unsetbot(self, interaction: discord.Interaction):
        if interaction.guild_id in self.guild_channels:
            del self.guild_channels[interaction.guild_id]
            await interaction.response.send_message("Restricción de canal eliminada.", ephemeral=True)
        else:
            await interaction.response.send_message("No había restricciones activas.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warzone(bot))

