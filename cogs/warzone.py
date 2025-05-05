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

    @app_commands.command(name="loadouts", description="View available loadouts.")
    async def loadouts(self, interaction: Interaction):
        await interaction.response.defer()

        if interaction.guild_id in self.guild_channels:
            if interaction.channel.id != self.guild_channels[interaction.guild_id]:
                await interaction.followup.send("This command can only be used in the allowed channel.", ephemeral=True)
                return

        ref = get_server_loadouts(interaction.guild_id)
        docs = ref.stream()

        loadouts = [(doc.id, doc.to_dict().get('title', doc.id)) for doc in docs]

        if not loadouts:
            await interaction.followup.send("No loadouts available.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"{interaction.user.display_name}, here are the current loadouts:",
            color=discord.Color.dark_green()
        )
        loadouts_text = "\n".join([f"{idx}. {title}" for idx, (_, title) in enumerate(loadouts, 1)])
        embed.add_field(name="Loadouts:", value=loadouts_text, inline=False)

        await interaction.followup.send(embed=embed, view=LoadoutView(ref, loadouts), ephemeral=False)

    @app_commands.command(name="add_load", description="Add a new loadout. [ADMINISTRATOR]")
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
            await interaction.response.send_message("❌ You reached the limit of 5 loadouts. Upgrade to premium to save more.", ephemeral=True)
            return

        if image_url and not is_valid_url(image_url):
            await interaction.response.send_message("❌ Invalid image URL. Make sure it starts with http or https.", ephemeral=True)
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
        await interaction.response.send_message(f"✅ Loadout `{title}` added successfully.", ephemeral=True)

    @app_commands.command(name="edit_load", description="Edit an existing loadout. [ADMINISTRATOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def edit_load(self, interaction: Interaction,
                        weapon_name: str,
                        optic: str = None, muzzle: str = None, barrel: str = None,
                        underbarrel: str = None, magazine: str = None,
                        rear_grip: str = None, fire_mods: str = None,
                        stock: str = None, laser: str = None):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message("❌ This command is only for premium users.", ephemeral=True)
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc_ref = ref.document(weapon_name)
        doc = doc_ref.get()

        if not doc.exists:
            await interaction.response.send_message("Loadout not found.", ephemeral=True)
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

        await interaction.response.send_message(f"✅ Loadout `{weapon_name}` updated successfully.", ephemeral=True)

    @app_commands.command(name="del_load", description="Delete a loadout. [ADMINISTRATOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def del_load(self, interaction: Interaction, weapon_name: str):
        user_id = str(interaction.user.id)
        if not is_premium(user_id):
            await interaction.response.send_message("❌ This command is only for premium users.", ephemeral=True)
            return

        ref = get_server_loadouts(interaction.guild_id)
        doc = ref.document(weapon_name).get()

        if not doc.exists:
            await interaction.response.send_message("Loadout not found.", ephemeral=True)
            return

        ref.document(weapon_name).delete()
        await interaction.response.send_message(f"Loadout `{weapon_name}` deleted successfully.", ephemeral=True)

    @app_commands.command(name="offbot", description="Remove the bot from the server (Owner only).")
    async def offbot(self, interaction: Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        channel = interaction.guild.text_channels[0]
        embed = discord.Embed(
            title="Thanks for using the server",
            description="@everyone The bot is disconnecting. See you soon!",
            color=discord.Color.dark_green()
        )
        await channel.send(embed=embed)
        await asyncio.sleep(2)
        await interaction.guild.leave()

    @app_commands.command(name="setbot", description="Restrict /loadouts to a specific channel. [ADMINISTRATOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def setbot(self, interaction: Interaction, channel: discord.TextChannel):
        self.guild_channels[interaction.guild_id] = channel.id
        await interaction.response.send_message(f"Channel configured: {channel.mention}", ephemeral=True)

    @app_commands.command(name="unsetbot", description="Allow /loadouts in any channel. [ADMINISTRATOR - PREMIUM]")
    @app_commands.default_permissions(administrator=True)
    async def unsetbot(self, interaction: Interaction):
        if interaction.guild_id in self.guild_channels:
            del self.guild_channels[interaction.guild_id]
            await interaction.response.send_message("Channel restriction removed.", ephemeral=True)
        else:
            await interaction.response.send_message("There was no active restriction.", ephemeral=True)

    @app_commands.command(name="info", description="Information on how to get premium.")
    async def info(self, interaction: Interaction):
        embed = discord.Embed(
            title="⭐ Premium Info",
            description="Want more loadouts, exclusive features, and to invite the bot to your server?\n\n📩 Contact the developer directly via Discord: `AkariiDEV`",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Warzone(bot))

