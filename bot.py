import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("TOKEN")

# -------- INTENTS --------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # POTRZEBNE DO POBIERANIA CZŁONKÓW ROLI

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================================================
# ---------------- FORMATOWANIE CHANGELOG -------------
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


# =====================================================
# ---------------- BOT READY --------------------------
# =====================================================

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Zalogowano jako {bot.user}")


# =====================================================
# ---------------- CHANGELOG --------------------------
# =====================================================

@bot.tree.command(name="changelog", description="Tworzy changelog")
async def changelog(interaction: discord.Interaction, data: str, tresc: str, ping: str):

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG

**{data}**

{formatted}

{ping}

**ZMIANY DOSTĘPNE PO 22**"""

    # Ukryta odpowiedź
    await interaction.response.send_message("✅ Changelog wysłany.", ephemeral=True)

    # Publiczna wiadomość od bota
    await interaction.channel.send(message)


# =====================================================
# ---------------- PV DO ROLI -------------------------
# =====================================================

@bot.tree.command(name="pv", description="Wyślij prywatną wiadomość do wszystkich z wybraną rolą")
@app_commands.describe(
    rola="Wybierz rolę",
    tresc="Treść wiadomości do wysłania"
)
@app_commands.checks.has_permissions(administrator=True)
async def pv(interaction: discord.Interaction, rola: discord.Role, tresc: str):

    # Dajemy więcej czasu na wykonanie
    await interaction.response.defer(ephemeral=True)

    sukces = []
    porazka = []

    # Pobieramy członków z rolą (bez botów)
    members = [m for m in rola.members if not m.bot]

    for member in members:

        embed = discord.Embed(
            title="📢 Wiadomość od administracji",
            description=f"━━━━━━━━━━━━━━\n{tresc}\n━━━━━━━━━━━━━━",
            color=discord.Color.blue()
        )

        embed.set_footer(text=f"Wysłano przez: {interaction.user}")

        try:
            # Wysyłanie DM
            await member.send(embed=embed)
            sukces.append(member)

        except discord.Forbidden:
            porazka.append((member, "Użytkownik ma zablokowane wiadomości prywatne"))

        except discord.HTTPException:
            porazka.append((member, "Bot nie może wysłać DM"))

    # ---------------- RAPORT ----------------

    raport = f"""📨 **Raport wysyłki PV**

👥 Liczba osób z rolą: {len(members)}
✅ Otrzymało wiadomość: {len(sukces)}
❌ Nie otrzymało: {len(porazka)}
"""

    if sukces:
        raport += "\n✅ Dostarczono:\n"
        for m in sukces:
            raport += f"- {m.mention}\n"

    if porazka:
        raport += "\n❌ Nie dostarczono:\n"
        for m, powod in porazka:
            raport += f"- {m.mention}\n  Powód: {powod}\n"

    await interaction.followup.send(raport, ephemeral=True)


# Obsługa braku permisji
@pv.error
async def pv_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "❌ Nie masz uprawnień administratora do użycia tej komendy.",
            ephemeral=True
        )


# =====================================================
# ---------------- START BOT --------------------------
# =====================================================

bot.run(TOKEN)
