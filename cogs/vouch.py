import discord, asyncio, time
from discord.ext import commands, tasks
from config import WAIT_TIME, VOUCH_CHANNEL_ID
from utils.database import load_data, save_data, mark_vouched, is_whitelisted

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_vouches.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != VOUCH_CHANNEL_ID or message.author.bot: return
        mark_vouched(message.author.id)

    @tasks.loop(minutes=10)
    async def check_vouches(self):
        await self.bot.wait_until_ready()
        data = load_data()
        for uid, last in list(data["cooldowns"].items()):
            if is_whitelisted(uid): continue
            if uid not in data["vouched"] and time.time() - last > WAIT_TIME:
                member = self.bot.get_user(int(uid))
                try:
                    guilds = self.bot.guilds
                    for g in guilds:
                        m = g.get_member(int(uid))
                        if m:
                            await m.ban(reason="Failed to vouch within 24h")
                            print(f"Banned {uid} for not vouching.")
                except:
                    pass

async def setup(bot):
    await bot.add_cog(Vouch(bot))
