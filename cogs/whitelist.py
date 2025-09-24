# cogs/whitelist.py
import json
from discord.ext import commands
from config import OWNER_ID

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "data/users.json"

    def load_users(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def save_users(self, data):
        with open(self.file, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def whitelist(self, ctx, action=None, member: commands.MemberConverter=None):
        if ctx.author.id != OWNER_ID:
            return await ctx.send("Only the owner can use this command.")

        users = self.load_users()
        if action == "add" and member:
            if member.id not in users["whitelist"]:
                users["whitelist"].append(member.id)
                self.save_users(users)
                await ctx.send(f"{member} has been whitelisted!")
            else:
                await ctx.send(f"{member} is already whitelisted.")
        elif action == "remove" and member:
            if member.id in users["whitelist"]:
                users["whitelist"].remove(member.id)
                self.save_users(users)
                await ctx.send(f"{member} has been removed from whitelist!")
            else:
                await ctx.send(f"{member} is not in whitelist.")
        else:
            await ctx.send("Usage: !whitelist add/remove @user")

# This is required for discord.py 2.x cogs
async def setup(bot):
    await bot.add_cog(Whitelist(bot))
