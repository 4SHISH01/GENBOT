# cogs/admin.py
from discord.ext import commands
import discord
import json
from config import OWNER_ID, PREFIX

USERS_FILE = "data/users.json"
GENERATED_FILE = "data/generated.json"


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # Helpers
    # -----------------------
    def load_users(self):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"whitelist": [], "bypass": [], "admins": [], "cooldowns": {}, "premium": []}

    def save_users(self, data):
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def is_owner(self, user_id):
        return user_id == OWNER_ID

    # -----------------------
    # Reload command
    # -----------------------
    @commands.command()
    async def reload(self, ctx, cog_name: str = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not cog_name:
            return await ctx.send(f"❌ Usage: `{PREFIX}reload <cog>`")
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
            await self.bot.load_extension(f"cogs.{cog_name}")
            await ctx.send(f"✅ Successfully reloaded `{cog_name}`")
        except Exception as e:
            await ctx.send(f"❌ Could not reload `{cog_name}`.\nError: {e}")

    # -----------------------
    # Whitelist management
    # -----------------------
    @commands.command()
    async def managewhitelist(self, ctx, user: discord.Member = None, action: str = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not user or not action:
            return await ctx.send(f"❌ Usage: `{PREFIX}managewhitelist @user add/remove`")

        users = self.load_users()
        whitelist = users.get("whitelist", [])

        if action.lower() == "add":
            if user.id in whitelist:
                return await ctx.send(f"✅ {user} is already whitelisted.")
            whitelist.append(user.id)
            users["whitelist"] = whitelist
            self.save_users(users)
            await ctx.send(f"✅ {user} added to whitelist.")
        elif action.lower() == "remove":
            if user.id not in whitelist:
                return await ctx.send(f"❌ {user} is not whitelisted.")
            whitelist.remove(user.id)
            users["whitelist"] = whitelist
            self.save_users(users)
            await ctx.send(f"✅ {user} removed from whitelist.")
        else:
            await ctx.send("❌ Invalid action! Use `add` or `remove`.")

    # -----------------------
    # Bypass management
    # -----------------------
    @commands.command()
    async def bypass(self, ctx, user: discord.Member = None, action: str = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not user or not action:
            return await ctx.send(f"❌ Usage: `{PREFIX}bypass @user add/remove`")

        users = self.load_users()
        bypass_list = users.get("bypass", [])

        if action.lower() == "add":
            if user.id in bypass_list:
                return await ctx.send(f"✅ {user} is already in bypass list.")
            bypass_list.append(user.id)
            users["bypass"] = bypass_list
            self.save_users(users)
            await ctx.send(f"✅ {user} added to bypass list.")
        elif action.lower() == "remove":
            if user.id not in bypass_list:
                return await ctx.send(f"❌ {user} is not in bypass list.")
            bypass_list.remove(user.id)
            users["bypass"] = bypass_list
            self.save_users(users)
            await ctx.send(f"✅ {user} removed from bypass list.")
        else:
            await ctx.send("❌ Invalid action! Use `add` or `remove`.")

    # -----------------------
    # Admin management
    # -----------------------
    @commands.command()
    async def addadmin(self, ctx, user: discord.Member = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}addadmin @user`")
        users = self.load_users()
        admins = users.get("admins", [])
        if user.id in admins:
            return await ctx.send(f"✅ {user} is already an admin.")
        admins.append(user.id)
        users["admins"] = admins
        self.save_users(users)
        await ctx.send(f"✅ {user} added as admin.")

    @commands.command()
    async def removeadmin(self, ctx, user: discord.Member = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}removeadmin @user`")
        users = self.load_users()
        admins = users.get("admins", [])
        if user.id not in admins:
            return await ctx.send(f"❌ {user} is not an admin.")
        admins.remove(user.id)
        users["admins"] = admins
        self.save_users(users)
        await ctx.send(f"✅ {user} removed from admins.")

    @commands.command()
    async def listadmins(self, ctx):
        users = self.load_users()
        admins = users.get("admins", [])
        if not admins:
            return await ctx.send("⚠️ No admins found.")
        embed = discord.Embed(
            title="🛡️ Admins List",
            description="\n".join([f"<@{uid}>" for uid in admins]),
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Total admins: {len(admins)}")
        await ctx.send(embed=embed)

    # -----------------------
    # Show whitelisted users
    # -----------------------
    @commands.command()
    async def listwhitelist(self, ctx):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        users = self.load_users()
        whitelist = users.get("whitelist", [])
        if not whitelist:
            return await ctx.send("⚠️ No users are whitelisted.")
        embed = discord.Embed(
            title="📜 Whitelisted Users",
            description="\n".join([f"<@{uid}>" for uid in whitelist]),
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Total: {len(whitelist)} users")
        await ctx.send(embed=embed)

    # -----------------------
    # Show bypassed users
    # -----------------------
    @commands.command()
    async def listbypass(self, ctx):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        users = self.load_users()
        bypass_list = users.get("bypass", [])
        if not bypass_list:
            return await ctx.send("⚠️ No users are in bypass list.")
        embed = discord.Embed(
            title="🛡️ Bypassed Users",
            description="\n".join([f"<@{uid}>" for uid in bypass_list]),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(bypass_list)} users")
        await ctx.send(embed=embed)

    # -----------------------
    # Show stock counts
    # -----------------------
    @commands.command(name="showstock")
    async def show_stock(self, ctx, category: str = None):
        try:
            with open(GENERATED_FILE, "r") as f:
                gen_data = json.load(f)
        except FileNotFoundError:
            return await ctx.send("⚠️ No stock data found.")

        if not gen_data:
            return await ctx.send("⚠️ The stock is currently empty.")

        if category:
            category = category.upper()
            count = len(gen_data.get(category, []))
            if count == 0:
                return await ctx.send(f"⚠️ No stock available for `{category}`.")
            embed = discord.Embed(
                title=f"📦 Stock Count – {category}",
                description=f"**{count}** item(s) currently available.",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(title="📦 Stock Counts by Category", color=discord.Color.green())
        for cat, items in gen_data.items():
            embed.add_field(name=cat, value=f"**{len(items)}** item(s) available", inline=False)
        await ctx.send(embed=embed)


# -----------------------
# Setup
# -----------------------
async def setup(bot):
    await bot.add_cog(Admin(bot))
