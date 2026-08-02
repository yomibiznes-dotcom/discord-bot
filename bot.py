import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1115692704614060092  # 🔴 WSTAW ID SERWERA
WEZWANIE_CHANNEL_ID = 1533507726376964186

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =====================================================
# READY + CLEAN SYNC
# =====================================================

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # usuń globalne komendy
    bot.tree.clear_commands(guild=None)

    # usuń stare guild komendy
    bot.tree.clear_commands(guild=guild)

    # zsynchronizuj tylko guild
    synced = await bot.tree.sync(guild=guild)

    print(f"✅ Zsynchronizowano {len(synced)} komend (guild)")
    print(f"✅ Zalogowano jako {bot.user}")

# =====================================================
# WEZWIJ
# =====================================================

@bot.tree.command(
    name="wezwij",
    description="Wezwij gracza na poczekalnię",
    guild=discord.Object(id=GUILD_ID)
)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

    await interaction.response.send_message("✅ Wezwanie wysłane.", ephemeral=True)

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

    message = await channel.send(embed=embed)

    # TIMER
    while True:
        remaining = int((end_time - datetime.utcnow()).total_seconds())

        if remaining <= 0:
            embed.description = f"{gracz.mention}\n\n" \
                                f"**CZAS MINĄŁ ⛔**\n\n" \
                                f"*Wzywał {interaction.user.mention}*"
            embed.color = discord.Color.red()
            await message.edit(embed=embed)
            break

        minutes = remaining // 60
        seconds = remaining % 60

        embed.description = f"{gracz.mention}\n\n" \
                            f"**ZOSTAŁEŚ WEZWANY**\n" \
                            f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n" \
                            f"*Wzywa cię {interaction.user.mention}*\n\n" \
                            f"⏳ Pozostały czas: {minutes:02}:{seconds:02}"

        await message.edit(embed=embed)

        await asyncio.sleep(1)

# =====================================================
# START
# =====================================================

bot.run(TOKEN)
