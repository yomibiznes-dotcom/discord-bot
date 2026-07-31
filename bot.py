import discord
import os
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot działa jako {bot.user}")

@bot.command()
async def hej(ctx):
    await ctx.send("Cześć!")

bot.run(TOKEN)
