import discord

class LoadoutButton(discord.ui.Button):
    def __init__(self, ref, doc_id, label):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id=doc_id)
        self.ref = ref
        self.doc_id = doc_id

    async def callback(self, interaction: discord.Interaction):
        try:
            doc = self.ref.document(self.doc_id).get()
            if not doc.exists:
                await interaction.response.send_message("❌ Loadout not found.", ephemeral=True)
                return

            data = doc.to_dict()
            embed = discord.Embed(
                title=data.get('title', 'Loadout'),
                color=discord.Color.dark_green()
            )

            # Group attachments in a single section with formatted display
            fields = ["Optic", "Muzzle", "Barrel", "Underbarrel", "Magazine", "Rear Grip", "Fire Mods", "Stock", "Laser"]
            accessory_lines = [f"**{field}:** {data[field]}" for field in fields if field in data]
            if accessory_lines:
                embed.add_field(name="Attachments", value="\n".join(accessory_lines), inline=False)

            # Add image if available
            image_url = data.get("image_url", "")
            if image_url.startswith("http"):
                embed.set_image(url=image_url)

            await interaction.response.send_message(
                content="Here are the loadout details:",
                embed=embed,
                ephemeral=False
            )

        except Exception as e:
            await interaction.response.send_message("❌ An error occurred while showing the loadout.", ephemeral=True)
            print(f"Error in LoadoutButton: {e}")

class LoadoutView(discord.ui.View):
    def __init__(self, ref, loadouts):
        super().__init__(timeout=None)
        for doc_id, label in loadouts:
            self.add_item(LoadoutButton(ref, doc_id, label))

