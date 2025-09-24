# main.py
import discord
from discord.ext import commands
from config import BOT_TOKEN, PREFIX

# Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, help_command=None, intents=intents)

# Event: bot ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Bot is ready!")

# Load cogs function
async def setup_cogs():
    cogs = [
        "cogs.whitelist",
        "cogs.gen",
        "cogs.vouch",
        "cogs.admin"
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

# Properly start bot and load cogs
async def main():
    async with bot:
        await setup_cogs()
        await bot.start(BOT_TOKEN)

# Run the async main
import asyncio
asyncio.run(main())
