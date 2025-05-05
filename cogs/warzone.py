import discord
from discord import Interaction, app_commands
from discord.ext import commands
from firebase import get_server_loadouts
from premium import is_premium
import asyncio
import os
from google.cloud import firestore
from urllib.parse import urlparse
from cogs.loadouts_buttons import LoadoutView

OWNER_ID = int(os.getenv('OWNER_ID'))

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except:
        return False

class Warzone(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_channels = {}

    @app_commands.command(name="loadouts", description="Ver los loadouts disponibles. | View available loadouts.")
    async def loadouts(self, interaction: Interaction):
        await interaction.response.defer()

        if interaction.guild_id in self.guild_channels:
            if interaction.channel.id != self.guild_channels[interaction.guild_id]:
                await interaction.followup.send("Este comando solo puede usarse en el canal permitido. | This command can only be used on the allowed channel.", ephemeral=True)
                return

        ref = get_server_loadouts(interaction.guild_id)
        docs = ref.stream()

        loadouts = [(doc.id, doc.to_dict().get('title', doc.id)) for doc in docs]

        if not loadouts:
            await interaction.followup.send("No hay loadouts disponibles. | No loadouts are available.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}, estos son los loadouts actuales: | these are the current loadouts:",
            color=discord.Color.dark_green()
        )
        loadouts_text = "\n".join([f"{idx}. {title}" for idx, (_, title) in enumerate(loadouts, 1)])
        embed.add_field(name="Loadouts:", value=loadouts_text, inline=False)

        await interaction.followup.send(embed=embed, view=LoadoutView(ref, loadouts), ephemeral=False)

    @app_commands.command(name="add_load", description="Agregar un nuevo loadout. | Add a new loadout [ADMINISTRADOR]")
    @app_commands.default_permissions(administrator=True)
    async def add_load(self, interaction: Interaction,
                       weapon_name: str, title: str, image_url: str = None,
                       optic: str = "NO", muzzle: str = "NO", barrel: str = "NO",
                       underbarrel: str = "NO", magazine: str = "NO",
                       rear_grip: str = "NO", fire_mods: str = "NO",
                       stock: str = "NO", laser: str = "NO"):
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild.id)
        ref = get_server_loadouts(guild_id)

        docs = list(ref.stream())
        if not is_premium(user_id) and len(docs) >= 5:
            await interaction.response.send_message("❌ Alcanzaste el límite de 5 loadouts. Hazte premium para guardar más. | ❌ You have reached the limit of 5 loadouts. Become premium to save more.", ephemeral=True)
            return

        if image_url and not is_valid_url(image_url):
            await interaction.response.send_message("❌ La URL de la imagen no es válida. Asegúrate de que comience con http o https. | ❌ The image URL is invalid. Make sure it starts with http or https.", ephemeral=True)
            return

        accessories = {
            "Optic": optic,
            "Muzzle": muzzle,
            "Barrel": barrel,
            "Underbarrel": underbarrel,
            "Magazine": magazine,
            "Rear Grip": rear_grip,
            "Fire Mods": fire_mods,
            "Stock": stock,
            "Laser": laser
        }
        accessories = {k: v for k, v in accessories.items() if v and v.upper() != "NO"}

        data = {
            "title": title,
            **accessories
        }

        if image_url:
            data["image_url"] = image_url

        ref.document(weapon_name).set(data)
        await interaction.response.send_message(f"✅ Loadout `{title}` agregado correctamente. | ✅ Loadout `{title}` added correctly.", ephemeral=True)

    @app_commands.command(name="edit_load", description="Editar un loadout existente. | Edit loadout [ADMINISTRADOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def edit_load(self, interaction: Interaction,
                        weapon_name: str,
                        optic: str = None, muzzle: str = None, barrel: str = None,
                        underbarrel: str = None, magazine: str = None,
                        rear_grip: str = None, fire_mods: str = None,
                        stock: str = None, laser: str = None):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message("❌ Este comando es exclusivo para usuarios premium. | ❌ This command is exclusive for premium users.", ephemeral=True)
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc_ref = ref.document(weapon_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado. | Loadout not found.", ephemeral=True)
            return

        update_data = {}
        delete_fields = []

        fields = {
            "Optic": optic,
            "Muzzle": muzzle,
            "Barrel": barrel,
            "Underbarrel": underbarrel,
            "Magazine": magazine,
            "Rear Grip": rear_grip,
            "Fire Mods": fire_mods,
            "Stock": stock,
            "Laser": laser
        }

        for key, value in fields.items():
            if value is not None:
                if value.upper() == "NO":
                    delete_fields.append(key)
                else:
                    update_data[key] = value

        if update_data:
            doc_ref.update(update_data)

        if delete_fields:
            doc_ref.update({field: firestore.DELETE_FIELD for field in delete_fields})

        await interaction.response.send_message(f"✅ Loadout `{weapon_name}` actualizado correctamente. | ✅ Loadout `{weapon_name}` updated correctly.", ephemeral=True)

    @app_commands.command(name="del_load", description="Eliminar un loadout. | Delete loadout[ADMINISTRADOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def del_load(self, interaction: Interaction, weapon_name: str):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message("❌ Este comando es exclusivo para usuarios premium. | ❌ This command is exclusive for premium users.", ephemeral=True)
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc = ref.document(weapon_name).get()

        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado. | Loadout not found.", ephemeral=True)
            return

        ref.document(weapon_name).delete()
        await interaction.response.send_message(f"Loadout `{weapon_name}` eliminado correctamente. | Loadout `{weapon_name}` correctly eliminated.", ephemeral=True)

    @app_commands.command(name="offbot", description="Expulsar al bot del servidor (solo el Owner).")
    async def offbot(self, interaction: Interaction):
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

    @app_commands.command(name="setbot", description="Restringir /loadouts a un canal específico. | Restrict /loadouts to a specific channel. [ADMINISTRADOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def setbot(self, interaction: Interaction, channel: discord.TextChannel):
        self.guild_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"Canal configurado: {channel.mention}", ephemeral=True)

    @app_commands.command(name="unsetbot", description="Permitir que /loadouts se use en cualquier canal. | Allow /loadouts to be used on any channel. [ADMINISTRADOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def unsetbot(self, interaction: Interaction):
        if interaction.guild_id in self.guild_channels:
            del self.guild_channels[interaction.guild_id]
            await interaction.response.send_message("Restricción de canal eliminada.", ephemeral=True)
        else:
            await interaction.response.send_message("No había restricciones activas.", ephemeral=True)

    @app_commands.command(name="info", description="Información sobre cómo obtener premium. | Information on how to obtain premium.")
    async def info(self, interaction: Interaction):
        # Primer embed en español (verde oscuro)
        embed_es = Embed(
            title="⭐ Información Premium",
            description="¿Quieres más loadouts, funciones exclusivas e invitar el bot a tu servidor?\n\n📩 Contacta directamente al desarrollador por Discord: `AkariiDEV`",
            color=Color.dark_green()
        )

        # Segundo embed en inglés (azul)
        embed_en = Embed(
            title="⭐ Premium Info",
            description="Want more loadouts, exclusive features, and to invite the bot to your server?\n\n📩 Contact the developer on Discord: `AkariiDEV`",
            color=Color.blue()
        )

        # Envía los dos embeds juntos
        await interaction.response.send_message(embeds=[embed_es, embed_en], ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warzone(bot))
