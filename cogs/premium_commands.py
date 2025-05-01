import discord
from discord import app_commands
from discord.ext import commands
from firebase_admin import firestore
from premium import is_premium, set_premium, get_premium_expiry, redeem_token
import os
from datetime import datetime

db = firestore.client()

BOT_OWNER_ID = int(os.getenv("BOT_OWNER_ID"))

class PremiumCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # /premium_info
    @app_commands.command(name="premium_info", description="Muestra tu estado premium.")
    async def premium_info(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        expiry = get_premium_expiry(user_id)

        if not expiry:
            await interaction.response.send_message("🪙 No sos usuario premium actualmente.", ephemeral=True)
        else:
            expiry_str = datetime.fromisoformat(expiry.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M UTC")
            await interaction.response.send_message(
                f"✨ Sos premium hasta: **{expiry_str}**", ephemeral=True
            )

    # /redeem
    @app_commands.command(name="redeem", description="Canjea un token para activar premium.")
    @app_commands.describe(token="El token que te dieron")
    async def redeem(self, interaction: discord.Interaction, token: str):
        user_id = str(interaction.user.id)
        success = redeem_token(user_id, token)

        if success:
            expiry = get_premium_expiry(user_id)
            expiry_str = datetime.fromisoformat(expiry.replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M UTC")
            await interaction.response.send_message(
                f"✅ Token canjeado con éxito. Premium activo hasta **{expiry_str}**.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Token inválido o ya fue usado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PremiumCommands(bot))

