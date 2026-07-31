import discord
from discord import app_commands
from discord.ext import commands

TOKEN = "TU_WKLEJ_TOKEN"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class MyClient(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyClient()

@bot.event
async def on_ready():
    print(f"Zalogowano jako {bot.user}")

@bot.tree.command(name="leak", description="Wyślij wiadomość z obrazem i plikiem")
@app_commands.describe(
    tekst="Co bot ma napisać",
    obraz_link="Link do zdjęcia / filmu",
    plik="Plik do wysłania"
)
async def leak(interaction: discord.Interaction, tekst: str, obraz_link: str, plik: discord.Attachment):

    embed = discord.Embed(description=tekst, color=discord.Color.red())
    embed.set_image(url=obraz_link)

    await interaction.response.send_message(
        embed=embed,
        file=await plik.to_file()
    )

bot.run(TOKEN)
