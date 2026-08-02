import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime, timedelta, UTC

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1115692704614060092  # 🔴 WSTAW ID
WEZWANIE_CHANNEL_ID = 1533507726376964186
POCZEKALNIA_CHANNEL_ID = 1115692705184497698

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = discord.Object(id=GUILD_ID)

active_calls = {}

# =====================================================
# READY
# =====================================================

@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild_obj)
    print("✅ Bot gotowy")

# =====================================================
# WEZWIJ
# =====================================================

@bot.tree.command(name="wezwij", guild=guild_obj)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

    # ✅ ODPOWIADA OD RAZU (naprawia "aplikacja nie reaguje")
    await interaction.response.send_message("✅ Wezwanie wysłane.", ephemeral=True)

    channel = bot.get_channel(WEZWANIE_CHANNEL_ID)
    end_time = datetime.now(UTC) + timedelta(minutes=3)

    embed = discord.Embed(
        description=f"# {gracz.mention}\n\n"
                    f"**ZOSTAŁEŚ WEZWANY**\n"
                    f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n"
                    f"*Wzywa cię {interaction.user.mention}*\n\n"
                    f"⏳ 03:00",
        color=discord.Color.purple()
    )

    embed.add_field(name="Status", value="⏳ OCZEKIWANIE...", inline=False)
    embed.set_thumbnail(url=bot.user.display_avatar.url)

    msg = await channel.send(embed=embed)

    active_calls[gracz.id] = {
        "caller": interaction.user,
        "message": msg,
        "embed": embed,
        "end_time": end_time
    }

    # DM
    try:
        await gracz.send(embed=embed)
    except:
        pass

    # TIMER (bez blokowania interakcji)
    bot.loop.create_task(timer_task(gracz.id))

# =====================================================
# TIMER TASK
# =====================================================

async def timer_task(user_id):
    while user_id in active_calls:

        call = active_calls[user_id]
        embed = call["embed"]
        msg = call["message"]
        end_time = call["end_time"]

        remaining = int((end_time - datetime.now(UTC)).total_seconds())

        if remaining <= 0:
            embed.color = discord.Color.red()
            embed.set_field_at(0, name="Status", value="🔴 CZAS MINĄŁ", inline=False)
            await msg.edit(embed=embed)
            active_calls.pop(user_id, None)
            break

        minutes = remaining // 60
        seconds = remaining % 60

        embed.description = embed.description.split("\n\n⏳")[0] + f"\n\n⏳ {minutes:02}:{seconds:02}"
        await msg.edit(embed=embed)

        await asyncio.sleep(1)

# =====================================================
# VOICE DETECTION
# =====================================================

@bot.event
async def on_voice_state_update(member, before, after):

    if member.id not in active_calls:
        return

    if after.channel and after.channel.id == POCZEKALNIA_CHANNEL_ID:

        call = active_calls[member.id]
        caller = call["caller"]

        try:
            await caller.send(
                f"OSOBA PRZEZ CIEBIE WEZWANA {member.mention} JEST NA POCZEKALNI"
            )
        except:
            pass

# =====================================================

bot.run(TOKEN)
