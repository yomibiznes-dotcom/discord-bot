import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import os
from datetime import datetime

TOKEN = os.getenv("TOKEN")

# 🔴 WSTAW ID SWOJEGO SERWERA DISCORD
GUILD_ID = 1115692704614060092

WEZWANIE_CHANNEL_ID = 1533507726376964186
POCZEKALNIA_CHANNEL_ID = 1115692705184497698

FIVEM_SERVER = "http://37.221.94.185:30170"

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

    # ✅ OPIS BOTA
    try:
        await bot.user.edit(bio="VEYRONRP WLOFF\n\n|| AUTOR: xvero ||")
    except:
        pass

    print("✅ Bot gotowy")

    bot.loop.create_task(update_status())

# =====================================================
# STATUS Z FIVEM
# =====================================================

async def update_status():
    await bot.wait_until_ready()

    while not bot.is_closed():

        players_online = 0
        max_players = 0
        server_online = True

        try:
            async with aiohttp.ClientSession() as session:

                async with session.get(f"{FIVEM_SERVER}/players.json", timeout=5) as r:
                    if r.status == 200:
                        data = await r.json()
                        players_online = len(data)
                    else:
                        server_online = False

                async with session.get(f"{FIVEM_SERVER}/info.json", timeout=5) as r:
                    if r.status == 200:
                        info = await r.json()
                        max_players = int(info["vars"].get("sv_maxClients", 0))
                    else:
                        server_online = False

        except:
            server_online = False

        if not server_online:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name="🔴 SERWER OFFLINE"
            )
        else:
            activity = discord.Activity(
                type=discord.ActivityType.watching,
                name=f"[{players_online}/{max_players}] na VEYRONRP"
            )

        await bot.change_presence(activity=activity)

        await asyncio.sleep(30)

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
# PRZYCISKI DECYZYJNE
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
        await interaction.response.send_message("✅ Oznaczono.", ephemeral=True)
        await self.finish(interaction, "🟢 STAWIŁ/A SIĘ NA POCZEKALNI", discord.Color.green())

    @discord.ui.button(label="NIE STAWIŁ/A SIĘ", style=discord.ButtonStyle.red)
    async def absent(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Oznaczono.", ephemeral=True)
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

    try:
        await gracz.send(embed=discord.Embed(
            description="**ZOSTAŁEŚ WEZWANY**\nMasz 3 minuty aby wejść na poczekalnię.",
            color=discord.Color.purple()
        ))
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

# =====================================================
# TICKETY VEYRONRP — CZĘŚĆ 1 (PANEL + TWORZENIE)
# =====================================================

TICKET_PANEL_CHANNEL = 1534559517155659976
TICKET_CATEGORY_ID = 1534563245279547432
TICKET_ADMIN_ROLE = 1533199994658619644
TICKET_COUNTER_FILE = "ticket_counter.json"

TICKET_COLOR = 0x00FFFF  # CYAN

# =====================================================
# LICZNIK TICKETÓW
# =====================================================

def load_ticket_counter():
    if not os.path.exists(TICKET_COUNTER_FILE):
        with open(TICKET_COUNTER_FILE, "w") as f:
            json.dump({"count": 0}, f)

    with open(TICKET_COUNTER_FILE, "r") as f:
        return json.load(f)["count"]

def save_ticket_counter(count):
    with open(TICKET_COUNTER_FILE, "w") as f:
        json.dump({"count": count}, f)

def get_next_ticket_number():
    count = load_ticket_counter() + 1
    save_ticket_counter(count)
    return count

# =====================================================
# MODAL (FORMULARZ)
# =====================================================

class TicketModal(discord.ui.Modal):
    def __init__(self, category_label):
        super().__init__(title="VeyronRP — Formularz Ticketa")

        self.category_label = category_label

        self.problem = discord.ui.TextInput(
            label="Opisz szczegółowo swój problem",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        )

        self.add_item(self.problem)

    async def on_submit(self, interaction: discord.Interaction):

        ticket_number = get_next_ticket_number()

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.get_role(TICKET_ADMIN_ROLE): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel_name = f"{self.category_label.lower().replace(' ', '-')}-{interaction.user.name}".replace("ą","a").replace("ł","l")

        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Nowy Ticket — VeyronRP",
            color=TICKET_COLOR
        )

        embed.add_field(name="Użytkownik", value=interaction.user.mention, inline=False)
        embed.add_field(name="ID", value=interaction.user.id, inline=False)
        embed.add_field(name="Kategoria", value=self.category_label, inline=False)
        embed.add_field(name="Numer Ticketu", value=f"#{ticket_number}", inline=False)
        embed.add_field(name="Problem", value=self.problem.value, inline=False)

        await ticket_channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Ticket utworzony: {ticket_channel.mention}",
            ephemeral=True
        )

# =====================================================
# SELECT MENU
# =====================================================

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Sprawa ogólna"),
            discord.SelectOption(label="Sprawa do zarządu"),
            discord.SelectOption(label="Odbiór produktu"),
            discord.SelectOption(label="Ban od AntiCheata"),
            discord.SelectOption(label="Sprawa pojazdowa"),
        ]

        super().__init__(
            placeholder="Wybierz typ ticketa...",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(
            TicketModal(self.values[0])
        )

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# =====================================================
# KOMENDA DO WYSŁANIA PANELU
# =====================================================

@bot.tree.command(name="panelticket", description="Wyślij panel ticketów", guild=guild_obj)
@app_commands.checks.has_permissions(administrator=True)
async def panelticket(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 VeyronRP — System Ticketów",
        description="Administracja odpowiada do 24 godzin.\n\nWybierz typ ticketa poniżej.",
        color=TICKET_COLOR
    )

    embed.set_image(url="https://i.imgur.com/8Km9tLL.png")  # możesz podmienić

    await interaction.response.send_message("✅ Panel wysłany.", ephemeral=True)

    channel = bot.get_channel(TICKET_PANEL_CHANNEL)
    await channel.send(embed=embed, view=TicketPanelView())
    # =====================================================
# TICKETY VEYRONRP — CZĘŚĆ 2 (ADMIN + TRANSKRYPCJA)
# =====================================================

def is_ticket_channel(channel):
    return channel.category_id == TICKET_CATEGORY_ID


async def generate_transcript(channel):
    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%d.%m.%Y %H:%M")
        content = msg.content if msg.content else ""
        messages.append(f"[{timestamp}] {msg.author} ({msg.author.id}): {content}")

    txt_content = "\n".join(messages)

    html_content = "<html><body style='background:#1e1e2f;color:white;font-family:Arial;'>"
    html_content += f"<h2>Transkrypcja Ticketa — {channel.name}</h2><hr>"

    for line in messages:
        html_content += f"<p>{line}</p>"

    html_content += "</body></html>"

    txt_file = discord.File(
        fp=bytes(txt_content, "utf-8"),
        filename=f"{channel.name}.txt"
    )

    html_file = discord.File(
        fp=bytes(html_content, "utf-8"),
        filename=f"{channel.name}.html"
    )

    return txt_file, html_file


class TranscriptButton(discord.ui.View):
    def __init__(self, txt_file, html_file):
        super().__init__(timeout=None)
        self.txt_file = txt_file
        self.html_file = html_file

    @discord.ui.button(label="📄 Transkrypcja", style=discord.ButtonStyle.primary)
    async def send_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            files=[self.txt_file, self.html_file],
            ephemeral=True
        )


# =====================================================
# /DODAJ
# =====================================================

@bot.tree.command(name="dodaj", description="Dodaj osobę do ticketa", guild=guild_obj)
async def dodaj(interaction: discord.Interaction, osoba: discord.Member):

    if not is_ticket_channel(interaction.channel):
        return await interaction.response.send_message("❌ To nie jest ticket.", ephemeral=True)

    if TICKET_ADMIN_ROLE not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    await interaction.channel.set_permissions(osoba, view_channel=True, send_messages=True)

    await interaction.response.send_message(f"✅ Dodano {osoba.mention}", ephemeral=True)


# =====================================================
# /ZAMKNIJ
# =====================================================

@bot.tree.command(name="zamknij", description="Zamknij ticket", guild=guild_obj)
async def zamknij(interaction: discord.Interaction):

    if not is_ticket_channel(interaction.channel):
        return await interaction.response.send_message("❌ To nie jest ticket.", ephemeral=True)

    if TICKET_ADMIN_ROLE not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    await interaction.response.send_message("🔒 Zamykam ticket...", ephemeral=True)

    await close_ticket(interaction, None)


# =====================================================
# /ZAMKNIJPOWOD
# =====================================================

@bot.tree.command(name="zamknijpowod", description="Zamknij ticket z powodem", guild=guild_obj)
async def zamknijpowod(interaction: discord.Interaction, powod: str):

    if not is_ticket_channel(interaction.channel):
        return await interaction.response.send_message("❌ To nie jest ticket.", ephemeral=True)

    if TICKET_ADMIN_ROLE not in [r.id for r in interaction.user.roles]:
        return await interaction.response.send_message("❌ Brak uprawnień.", ephemeral=True)

    await interaction.response.send_message("🔒 Zamykam ticket...", ephemeral=True)

    await close_ticket(interaction, powod)


# =====================================================
# FUNKCJA ZAMYKANIA
# =====================================================

async def close_ticket(interaction, powod):

    channel = interaction.channel

    # Znajdź twórcę (pierwsza wiadomość embed)
    creator = None
    async for msg in channel.history(limit=10, oldest_first=True):
        if msg.embeds:
            try:
                creator_id = int(msg.embeds[0].fields[0].value.strip("<@>").replace("!", ""))
                creator = interaction.guild.get_member(creator_id)
                break
            except:
                pass

    txt_file, html_file = await generate_transcript(channel)

    if creator:
        embed = discord.Embed(
            title="🎫 Twój ticket został zamknięty",
            description=f"Zamknięty przez: {interaction.user.mention}",
            color=TICKET_COLOR
        )

        if powod:
            embed.add_field(name="Powód zamknięcia", value=powod, inline=False)

        view = TranscriptButton(txt_file, html_file)

        try:
            await creator.send(embed=embed, view=view)
        except:
            pass

    await channel.delete()

bot.run(TOKEN)
