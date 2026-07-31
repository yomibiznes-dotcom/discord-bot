import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1115692704614060092  # <-- TU WSTAW ID SWOJEGO SERWERA

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print(f"✅ Zalogowano jako {bot.user}")

# -------------------- PING --------------------

@bot.tree.command(name="ping", description="Sprawdza czy bot działa", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

# -------------------- LEAK --------------------

@bot.tree.command(name="leak", description="Wyślij wiadomość z tekstem, obrazem i plikiem", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    tekst="Co bot ma napisać",
    obraz_link="Link do zdjęcia",
    plik="Plik do wysłania"
)
async def leak(
    interaction: discord.Interaction,
    tekst: str,
    obraz_link: str,
    plik: discord.Attachment
):
    embed = discord.Embed(description=tekst, color=discord.Color.red())
    embed.set_image(url=obraz_link)

    await interaction.response.send_message(
        embed=embed,
        file=await plik.to_file()
    )

bot.run(TOKEN)
