import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")  # Railway bierze token z Variables

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------- READY --------------------

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Zsynchronizowano {len(synced)} komend")
    except Exception as e:
        print(e)

    print(f"✅ Zalogowano jako {bot.user}")


# -------------------- PING --------------------

@bot.tree.command(name="ping", description="Sprawdza czy bot działa")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏓 Pong! {round(bot.latency * 1000)}ms"
    )


# -------------------- LEAK --------------------

@bot.tree.command(name="leak", description="Wyślij wiadomość z tekstem, obrazem i plikiem")
@app_commands.describe(
    tekst="Co bot ma napisać",
    obraz_link="Link do zdjęcia / filmu",
    plik="Plik do wysłania"
)
async def leak(
    interaction: discord.Interaction,
    tekst: str,
    obraz_link: str,
    plik: discord.Attachment
):
    embed = discord.Embed(
        description=tekst,
        color=discord.Color.red()
    )

    embed.set_image(url=obraz_link)

    await interaction.response.send_message(
        embed=embed,
        file=await plik.to_file()
    )


# -------------------- START --------------------

bot.run(TOKEN)
