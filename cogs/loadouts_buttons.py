import discord

class LoadoutButton(discord.ui.Button):
    def __init__(self, ref, doc_id, label):
        super().__init__(label=label, style=discord.ButtonStyle.success, custom_id=doc_id)
        self.ref = ref
        self.doc_id = doc_id

    async def callback(self, interaction: discord.Interaction):
        # Obtener el documento del loadout de la base de datos
        doc = self.ref.document(self.doc_id).get()
        if not doc.exists:
            await interaction.response.send_message("Loadout no encontrado.", ephemeral=False)
            return

        # Crear el embed con la información del loadout
        data = doc.to_dict()
        embed = discord.Embed(
            title=data.get('title', 'Loadout'),
            color=discord.Color.dark_green()
        )

        # Agregar los campos del loadout al embed
        fields = ["Optic", "Muzzle", "Barrel", "Underbarrel", "Magazine", "Rear Grip", "Fire Mods"]
        for field in fields:
            if field in data and data[field] != "NO":
                embed.add_field(name=field, value=data[field], inline=False)

        # Si hay una URL de imagen, agregarla al embed
        if "image_url" in data:
            embed.set_image(url=data["image_url"])

        # Enviar el mensaje con el embed a todos los miembros del servidor (en el canal actual)
        await interaction.followup.send(embed=embed, ephemeral=False)  # Esto hace que sea visible para todos
        await interaction.response.send_message("Aquí están los detalles del loadout", ephemeral=True)  # Respuesta efímera solo para el usuario

class LoadoutView(discord.ui.View):
    def __init__(self, ref, loadouts):
        super().__init__(timeout=None)
        # Crear un botón para cada loadout
        for doc_id, label in loadouts:
            self.add_item(LoadoutButton(ref, doc_id, label))

