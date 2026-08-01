import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

# 🔴 WSTAW TUTAJ ID SWOJEGO SERWERA
GUILD_ID = 1115692704614060092

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================================================
# READY + SYNC (GUILD ONLY)
# =====================================================

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    synced = await bot.tree.sync(guild=guild)
    print(f"✅ Zsynchronizowano {len(synced)} komend (guild)")
    print(f"✅ Zalogowano jako {bot.user}")

# =====================================================
# CHANGELOG
# =====================================================

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

@bot.tree.command(
    name="changelog",
    description="Tworzy changelog",
    guild=discord.Object(id=GUILD_ID)
)
async def changelog(interaction: discord.Interaction, data: str, tresc: str, ping: str):

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG

**{data}**

{formatted}

{ping}

**ZMIANY DOSTĘPNE PO 22**"""

    await interaction.response.send_message("✅ Changelog wysłany.", ephemeral=True)
    await interaction.channel.send(message)

# =====================================================
# PV DO ROLI
# =====================================================

@bot.tree.command(
    name="pv",
    description="Wyślij prywatną wiadomość do roli",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.checks.has_permissions(administrator=True)
async def pv(interaction: discord.Interaction, rola: discord.Role, tresc: str):

    await interaction.response.defer(ephemeral=True)

    sukces = []
    porazka = []

    members = [m for m in rola.members if not m.bot]

    for member in members:
        embed = discord.Embed(
            title="📢 Wiadomość od administracji",
            description=f"━━━━━━━━━━━━━━\n{tresc}\n━━━━━━━━━━━━━━",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Wysłano przez: {interaction.user}")

        try:
            await member.send(embed=embed)
            sukces.append(member)
        except discord.Forbidden:
            porazka.append((member, "Zablokowane DM"))
        except discord.HTTPException:
            porazka.append((member, "Błąd HTTP"))

    raport = f"""📨 **Raport wysyłki PV**

👥 Liczba osób z rolą: {len(members)}
✅ Otrzymało wiadomość: {len(sukces)}
❌ Nie otrzymało: {len(porazka)}
"""

    await interaction.followup.send(raport, ephemeral=True)

bot.run(TOKEN)
