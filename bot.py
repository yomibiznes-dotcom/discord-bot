import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# -------- FORMATOWANIE --------

def format_changelog(text):
    lines = text.split("\n")
    new_lines = []

    for line in lines:
        lower = line.lower()

        if "dodano" in lower:
            new_lines.append(f"[+] {line}")
        elif "usunieto" in lower or "usunięto" in lower:
            new_lines.append(f"[-] {line}")
        elif "poprawiono" in lower or "naprawiono" in lower:
            new_lines.append(f"[/] {line}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines)

# -------- READY --------

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"✅ Zsynchronizowano {len(synced)} komend")
    print(f"✅ Zalogowano jako {bot.user}")

# -------- CHANGELOG --------

@bot.tree.command(name="changelog", description="Tworzy changelog")
async def changelog(interaction: discord.Interaction, data: str, tresc: str, ping: str):

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG ({data})

{formatted}

{ping}

ZMIANY DOSTĘPNE PO 22"""

    await interaction.response.send_message(message)

bot.run(TOKEN)
