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
intents.voice_states = True  # 🔥 potrzebne do wykrywania wejścia

bot = commands.Bot(command_prefix="!", intents=intents)
guild_obj = discord.Object(id=GUILD_ID)

# przechowujemy aktywne wezwania
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

class DecisionView(discord.ui.View):
    def __init__(self, caller_id, target_id, message):
        super().__init__(timeout=None)
        self.caller_id = caller_id
        self.target_id = target_id
        self.message = message

    async def disable_buttons(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="STAWIŁA SIĘ", style=discord.ButtonStyle.green)
    async def stawila(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("To nie twoje wezwanie.", ephemeral=True)

        call = active_calls.get(self.target_id)
        if call:
            embed = call["embed"]
            embed.color = discord.Color.green()
            embed.set_field_at(0, name="Status", value="🟢 STAWIŁ/A SIĘ NA POCZEKALNI", inline=False)
            await call["message"].edit(embed=embed)
            active_calls.pop(self.target_id, None)

        await interaction.response.send_message("✅ Oznaczono jako stawił/a się.", ephemeral=True)
        await self.disable_buttons()

    @discord.ui.button(label="OPUŚCIŁA KANAŁ", style=discord.ButtonStyle.red)
    async def opuscila(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.caller_id:
            return await interaction.response.send_message("To nie twoje wezwanie.", ephemeral=True)

        call = active_calls.get(self.target_id)
        if call:
            embed = call["embed"]
            embed.color = discord.Color.red()
            embed.set_field_at(0, name="Status", value="🔴 NIE STAWIŁ/A SIĘ NA POCZEKALNI", inline=False)
            await call["message"].edit(embed=embed)
            active_calls.pop(self.target_id, None)

        await interaction.response.send_message("❌ Oznaczono jako nie stawił/a się.", ephemeral=True)
        await self.disable_buttons()

@bot.tree.command(name="wezwij", guild=guild_obj)
async def wezwij(interaction: discord.Interaction, gracz: discord.Member):

    await interaction.response.defer(ephemeral=True)

    channel = bot.get_channel(WEZWANIE_CHANNEL_ID)

    end_time = datetime.now(UTC) + timedelta(minutes=3)

    embed = discord.Embed(
        description=f"# {gracz.mention}\n\n"
                    f"**ZOSTAŁEŚ WEZWANY**\n"
                    f"MASZ 3 MINUTY ABY WEJŚĆ NA POCZEKALNIĘ\n\n"
                    f"*Wzywa cię {interaction.user.mention}*",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Status", value="⏳ OCZEKIWANIE...", inline=False)

    msg = await channel.send(embed=embed)

    # DM bez timera
    try:
        await gracz.send(embed=embed)
    except:
        pass

    active_calls[gracz.id] = {
        "caller": interaction.user,
        "message": msg,
        "embed": embed,
        "end_time": end_time
    }

    await interaction.followup.send("✅ Wezwanie wysłane.", ephemeral=True)

    # stabilny timer
    while gracz.id in active_calls:
        remaining = int((end_time - datetime.now(UTC)).total_seconds())
        if remaining <= 0:
            embed.color = discord.Color.red()
            embed.set_field_at(0, name="Status", value="🔴 CZAS MINĄŁ", inline=False)
            await msg.edit(embed=embed)
            active_calls.pop(gracz.id, None)
            break

        await asyncio.sleep(1)

# =====================================================
# WYKRYWANIE WEJŚCIA NA KANAŁ
# =====================================================

@bot.event
async def on_voice_state_update(member, before, after):

    if member.id not in active_calls:
        return

    if after.channel and after.channel.id == POCZEKALNIA_CHANNEL_ID:

        call = active_calls.get(member.id)
        caller = call["caller"]

        embed = discord.Embed(
            description=f"OSOBA PRZEZ CIEBIE WEZWANA {member.mention} JEST NA POCZEKALNI",
            color=discord.Color.orange()
        )

        view = DecisionView(caller.id, member.id, None)
        msg = await caller.send(embed=embed, view=view)
        view.message = msg
