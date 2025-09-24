# cogs/checks.py
from discord.ext import commands
from config import OWNER_ID

def is_owner():
    """Check if the user is the bot owner"""
    async def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)
