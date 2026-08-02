import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1115692704614060092  # 🔴 WSTAW ID
WEZWANIE_CHANNEL_ID = 1533507726376964186

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = discord.Object(id=GUILD_ID)

# =====================================================
# RESET GLOBALNYCH KOMEND (WYKONA SIĘ RAZ)
# =====================================================

@bot.event
async def setup_hook():
    # usuń wszystkie globalne komendy
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()

# =====================================================
# READY
# =====================================================

@bot.event
async def on_ready():
    synced = await bot.tree.sync(guild=guild_obj)
    print(f"✅ Zsynchronizowano {len(synced)} komend (guild)")
    print(f"✅ Zalogowano jako {bot.user}")

# =====================================================
# CHANGELOG
# =====================================================

def format_changelog(text):
    parts = text.split(".")
    lines = []

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

        lines.append(f"`{prefix} {line}`" if prefix else f"`{line}`")

    return "\n".join(lines)

@bot.tree.command(name="changelog", guild=guild_obj)
async def changelog(interaction: discord.Interaction, data: str, tresc: str, ping: str):

    await interaction.response.defer(ephemeral=True)

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG

**{data}**

{formatted}

{ping}

**ZMIANY DOSTĘPNE PO 22**"""

    await interaction.channel.send(message)
    await interaction.followup.send("✅ Changelog wysłany.", ephemeral=True)

# =====================================================
# PV
# =====================================================

@bot.tree.command(name="pv", guild=guild_obj)
@app_commands.checks.has_permissions(administrator=True)
async def pv(interaction: discord.Interaction, rola: discord.Role, tresc: str):

    await interaction.response.defer(ephemeral=True)

    sukces = 0
    porazka = 0

    for member in rola.members:
        if member.bot:
            continue

        embed = discord.Embed(
            title="📢 Wiadomość od administracji",
            description=f"━━━━━━━━━━━━━━\n{tresc}\n━━━━━━━━━━━━━━",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Wysłano przez: {interaction.user}")

        try:
            await member.send(embed=embed)
            sukces += 1
        except:
            porazka += 1

    raport = f"""📨 **Raport wysyłki PV**

✅ Otrzymało: {sukces}
❌ Nie otrzymało: {porazka}
"""

    await interaction.followup.send(raport, ephemeral=True)

# =====================================================
# WEZWIJ (z DM)
# =====================================================

@bot.tree.command(name="wezwij", guild=guild_obj)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

    await interaction.response.defer(ephemeral=True)

    channel = bot.get_channel(WEZWANIE_CHANNEL_ID)

    end_time = datetime.utcnow() + timedelta(minutes=3)

    embed = discord.Embed(
        description=f"{gracz.mention}\n\n"
                    f"**ZOSTAŁEŚ WEZWANY**\n"
                    f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n"
                    f"*Wzywa cię {interaction.user.mention}*\n\n"
                    f"⏳ Pozostały czas: 03:00",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    msg = await channel.send(embed=embed)

    # ✅ WYŚLIJ TEŻ DM DO WEZWANEGO
    try:
        await gracz.send(embed=embed)
    except:
        pass

    await interaction.followup.send("✅ Wezwanie wysłane.", ephemeral=True)

    while True:
        remaining = int((end_time - datetime.utcnow()).total_seconds())

        if remaining <= 0:
            embed.description = f"{gracz.mention}\n\n**CZAS MINĄŁ ⛔**"
            embed.color = discord.Color.red()
            await msg.edit(embed=embed)
            break

        m = remaining // 60
        s = remaining % 60

        embed.description = f"{gracz.mention}\n\n" \
                            f"**ZOSTAŁEŚ WEZWANY**\n" \
                            f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n" \
                            f"*Wzywa cię {interaction.user.mention}*\n\n" \
                            f"⏳ Pozostały czas: {m:02}:{s:02}"

        await msg.edit(embed=embed)
        await asyncio.sleep(1)

# =====================================================

bot.run(TOKEN)
