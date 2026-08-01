import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------- FORMATOWANIE --------

def format_changelog(text):
    parts = text.split(".")
    formatted_lines = []

    for part in parts:
        line = part.strip()
        if not line:
            continue

        lower = line.lower()

        if "dodano" in lower:
            prefix = "[+]"
        elif "usunieto" in lower or "usunięto" in lower:
            prefix = "[-]"
        elif "poprawiono" in lower or "naprawiono" in lower:
            prefix = "[/]"
        else:
            prefix = ""

        if prefix:
            formatted_lines.append(f"`{prefix} {line}`")
        else:
            formatted_lines.append(f"`{line}`")

    return "\n".join(formatted_lines)

# -------- READY --------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Zalogowano jako {bot.user}")

# -------- CHANGELOG --------

@bot.tree.command(name="changelog", description="Tworzy changelog")
async def changelog(interaction: discord.Interaction, data: str, tresc: str, ping: str):

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG

**{data}**

{formatted}

{ping}

**ZMIANY DOSTĘPNE PO 22**"""

    # Ukryta odpowiedź (żeby nie było "Janek użył komendy")
    await interaction.response.send_message("✅ Changelog wysłany.", ephemeral=True)

    # Normalna wiadomość jako bot
    await interaction.channel.send(message)

bot.run(TOKEN)
