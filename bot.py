import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from datetime import datetime, timedelta, UTC

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1115692704614060092  # 🔴 WSTAW ID SERWERA
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

    await interaction.response.send_message("✅ Changelog wysłany.", ephemeral=True)

    formatted = format_changelog(tresc)

    message = f"""# CHANGELOG

**{data}**

{formatted}

{ping}

**ZMIANY DOSTĘPNE PO 22**"""

    await interaction.channel.send(message)

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

    await interaction.followup.send(
        f"✅ Otrzymało: {sukces}\n❌ Nie otrzymało: {porazka}",
        ephemeral=True
    )

# =====================================================
# VIEW Z PRZYCISKAMI
# =====================================================

class DecisionView(discord.ui.View):
    def __init__(self, target_id):
        super().__init__(timeout=None)
        self.target_id = target_id

    async def finish(self, interaction, status_text, color):
        call = active_calls.get(self.target_id)
        if not call:
            return

        embed = call["embed"]

        # usuń timer
        embed.description = embed.description.split("\n\n⏳")[0]

        embed.color = color
        embed.add_field(name="Status", value=status_text, inline=False)

        await call["message"].edit(embed=embed)

        active_calls.pop(self.target_id, None)

        for item in self.children:
            item.disabled = True

        await interaction.message.edit(view=self)

    @discord.ui.button(label="STAWIŁ/A SIĘ", style=discord.ButtonStyle.green)
    async def present(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("✅ Oznaczono jako stawił/a się.", ephemeral=True)
        await self.finish(interaction, "🟢 STAWIŁ/A SIĘ NA POCZEKALNI", discord.Color.green())

    @discord.ui.button(label="NIE STAWIŁ/A SIĘ", style=discord.ButtonStyle.red)
    async def absent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Oznaczono jako nie stawił/a się.", ephemeral=True)
        await self.finish(interaction, "🔴 NIE STAWIŁ/A SIĘ NA POCZEKALNI", discord.Color.red())

# =====================================================
# WEZWIJ
# =====================================================

@bot.tree.command(name="wezwij", guild=guild_obj)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

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

    embed.set_thumbnail(url=bot.user.display_avatar.url)

    msg = await channel.send(embed=embed)

    active_calls[gracz.id] = {
        "caller": interaction.user,
        "message": msg,
        "embed": embed,
        "end_time": end_time,
        "target": gracz
    }

    # DM bez timera
    dm_embed = discord.Embed(
        description=f"**ZOSTAŁEŚ WEZWANY**\n\n"
                    f"Masz 3 minuty aby wejść na poczekalnię.\n\n"
                    f"*Wzywa cię {interaction.user.mention}*",
        color=discord.Color.purple()
    )

    try:
        await gracz.send(embed=dm_embed)
    except:
        pass

    bot.loop.create_task(timer_task(gracz.id))
    bot.loop.create_task(reminder_task(gracz.id))

# =====================================================
# TIMER
# =====================================================

async def timer_task(user_id):

    while user_id in active_calls:

        call = active_calls[user_id]
        embed = call["embed"]
        msg = call["message"]
        end_time = call["end_time"]

        remaining = int((end_time - datetime.now(UTC)).total_seconds())

        if remaining <= 0:
            embed.description = embed.description.split("\n\n⏳")[0]
            embed.color = discord.Color.red()
            embed.add_field(name="Status", value="🔴 CZAS MINĄŁ", inline=False)
            await msg.edit(embed=embed)
            active_calls.pop(user_id, None)
            break

        minutes = remaining // 60
        seconds = remaining % 60

        embed.description = embed.description.split("\n\n⏳")[0] + f"\n\n⏳ {minutes:02}:{seconds:02}"
        await msg.edit(embed=embed)

        await asyncio.sleep(1)

# =====================================================
# PRZYPOMNIENIA
# =====================================================

async def reminder_task(user_id):

    for delay in [60, 120]:
        await asyncio.sleep(delay)
        if user_id not in active_calls:
            return

        target = active_calls[user_id]["target"]
        try:
            await target.send("⏰ Przypomnienie: zostałeś wezwany na poczekalnię.")
        except:
            pass

# =====================================================
# WYKRYCIE WEJŚCIA
# =====================================================

@bot.event
async def on_voice_state_update(member, before, after):

    if member.id not in active_calls:
        return

    if after.channel and after.channel.id == POCZEKALNIA_CHANNEL_ID:

        call = active_calls.get(member.id)
        caller = call["caller"]

        embed = discord.Embed(
            description=f"# {member.mention}\n\n"
                        f"**JEST NA POCZEKALNI**\n\n"
                        f"*Wezwany przez {caller.mention}*",
            color=discord.Color.orange()
        )

        embed.set_thumbnail(url=bot.user.display_avatar.url)

        view = DecisionView(member.id)

        try:
            await caller.send(embed=embed, view=view)
        except:
            pass

# =====================================================

bot.run(TOKEN)
