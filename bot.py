import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime, timedelta, UTC

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1115692704614060092  # 🔴 WSTAW ID SERWERA
WEZWANIE_CHANNEL_ID = 1533507726376964186

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = discord.Object(id=GUILD_ID)

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
# PV (ADMIN ONLY)
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
# WEZWIJ
# =====================================================

@bot.tree.command(name="wezwij", guild=guild_obj)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

    await interaction.response.defer(ephemeral=True)

    channel = bot.get_channel(WEZWANIE_CHANNEL_ID)

    end_time = datetime.now(UTC) + timedelta(minutes=3)

    # ✅ EMBED NA KANAŁ (z timerem)
    embed_channel = discord.Embed(
        description=f"# {gracz.mention}\n\n"
                    f"**ZOSTAŁEŚ WEZWANY**\n"
                    f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n"
                    f"*Wzywa cię {interaction.user.mention}*\n\n"
                    f"⏳ Pozostały czas: 03:00",
        color=discord.Color.purple()
    )

    embed_channel.set_thumbnail(url=bot.user.display_avatar.url)

    message = await channel.send(embed=embed_channel)

    # ✅ EMBED NA PV (bez timera)
    embed_dm = discord.Embed(
        description=f"**ZOSTAŁEŚ WEZWANY**\n\n"
                    f"Masz 3 minuty aby wejść na poczekalnię.\n\n"
                    f"*Wzywa cię {interaction.user.mention}*",
        color=discord.Color.purple()
    )

    embed_dm.set_thumbnail(url=bot.user.display_avatar.url)

    try:
        await gracz.send(embed=embed_dm)
    except:
        pass

    await interaction.followup.send("✅ Wezwanie wysłane.", ephemeral=True)

    # ✅ TIMER TYLKO NA KANALE
    while True:
        remaining = int((end_time - datetime.now(UTC)).total_seconds())

        if remaining <= 0:
            embed_channel.description = f"# {gracz.mention}\n\n" \
                                        f"**ZOSTAŁEŚ WEZWANY**\n" \
                                        f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n" \
                                        f"*Wzywa cię {interaction.user.mention}*\n\n" \
                                        f"⛔ CZAS MINĄŁ"

            embed_channel.color = discord.Color.red()
            await message.edit(embed=embed_channel)
            break

        minutes = remaining // 60
        seconds = remaining % 60

        embed_channel.description = f"# {gracz.mention}\n\n" \
                                    f"**ZOSTAŁEŚ WEZWANY**\n" \
                                    f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n" \
                                    f"*Wzywa cię {interaction.user.mention}*\n\n" \
                                    f"⏳ Pozostały czas: {minutes:02}:{seconds:02}"

        await message.edit(embed=embed_channel)
        await asyncio.sleep(1)

# =====================================================

bot.run(TOKEN)
