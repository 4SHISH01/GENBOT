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
        except FileNotFoundError:
            return {"whitelist": [], "bypass": [], "admins": [], "premium": [], "cooldowns": {}}

    def save_users(self, data):
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def is_owner(self, user_id):
        return user_id == OWNER_ID

    # -----------------------
    # Cog reload
    # -----------------------
    @commands.command()
    async def reload(self, ctx, cog_name: str = None):
        """Reload a specific cog (owner-only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only the owner can use this command.")
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
        """Add or remove users from whitelist (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")

        if not user or not action:
            return await ctx.send(f"❌ Usage: `{PREFIX}managewhitelist @user add/remove`")

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
        """Add or remove a user from bypass list (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")

        if not user or not action:
            return await ctx.send(f"❌ Usage: `{PREFIX}bypass @user add/remove`")

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
        """Add a new admin (owner-only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only the owner can use this command.")
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
        """Remove an admin (owner-only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only the owner can use this command.")
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

    # -----------------------
    # View lists
    # -----------------------
    @commands.command()
    async def listadmins(self, ctx):
        """List all admins."""
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

    @commands.command()
    async def listwhitelist(self, ctx):
        """List whitelisted users (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
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

    @commands.command()
    async def listbypass(self, ctx):
        """List bypassed users (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        bypass = users.get("bypass", [])
        if not bypass:
            return await ctx.send("⚠️ No users are in bypass list.")
        embed = discord.Embed(
            title="🛡️ Bypassed Users",
            description="\n".join([f"<@{uid}>" for uid in bypass]),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(bypass)} users")
        await ctx.send(embed=embed)

    # -----------------------
    # Stock commands
    # -----------------------
    @commands.command()
    async def addstock(self, ctx, category: str = None, *, items: str = None):
        """Add stock (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not category or not items:
            return await ctx.send(f"❌ Usage: `{PREFIX}addstock <category> <item1,item2,...>`")

        try:
            with open(GENERATED_FILE, "r") as f:
                gen_data = json.load(f)
        except FileNotFoundError:
            gen_data = {}

        category = category.upper()
        new_items = [i.strip() for i in items.split(",") if i.strip()]

        if category not in gen_data:
            gen_data[category] = []

        gen_data[category].extend(new_items)

        with open(GENERATED_FILE, "w") as f:
            json.dump(gen_data, f, indent=4)

        embed = discord.Embed(
            title="✅ Stock Added",
            description=f"Added **{len(new_items)} items** to `{category}`.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="showstock")
    async def show_stock(self, ctx, category: str = None):
        """Show stock counts (usable by everyone)."""
        try:
            with open(GENERATED_FILE, "r") as f:
                gen_data = json.load(f)
        except FileNotFoundError:
            return await ctx.send("⚠️ No stock data found.")

        if not gen_data:
            return await ctx.send("⚠️ Stock is currently empty.")

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
    # Premium users
    # -----------------------
    @commands.command(name="addpremium")
    async def add_premium(self, ctx, user: discord.Member = None):
        """Add premium user (owner-only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only owner can use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}addpremium @user`")
        users = self.load_users()
        premium = users.get("premium", [])
        if user.id in premium:
            return await ctx.send(f"✅ {user.mention} is already a premium user.")
        premium.append(user.id)
        users["premium"] = premium
        self.save_users(users)
        await ctx.send(f"✅ {user.mention} added to premium users.")

    @commands.command(name="removepremium")
    async def remove_premium(self, ctx, user: discord.Member = None):
        """Remove premium user (owner-only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only owner can use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}removepremium @user`")
        users = self.load_users()
        premium = users.get("premium", [])
        if user.id not in premium:
            return await ctx.send(f"⚠️ {user.mention} is not a premium user.")
        premium.remove(user.id)
        users["premium"] = premium
        self.save_users(users)
        await ctx.send(f"✅ {user.mention} removed from premium users.")

    @commands.command(name="listpremium")
    async def list_premium(self, ctx):
        """List premium users (admin/owner)."""
        users = self.load_users()
        admins = users.get("admins", [])
        premium = users.get("premium", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")
        if not premium:
            return await ctx.send("⚠️ No premium users found.")
        embed = discord.Embed(
            title="💎 Premium Users",
            description="\n".join([f"<@{uid}>" for uid in premium]),
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Total: {len(premium)} premium users")
        await ctx.send(embed=embed)

    # -----------------------
    # Utilities
    # -----------------------
    @commands.command()
    async def ping(self, ctx):
        """Check latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(embed=discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency} ms**",
            color=discord.Color.green()
        ))

    # -----------------------
    # Help
    # -----------------------
    @commands.command(name="adminhelp")
    async def admin_help(self, ctx):
        embed = discord.Embed(
            title="🛠️ Admin Commands Help",
            description=f"Prefix: `{PREFIX}`\n🔒 = Owner-only command.",
            color=discord.Color.orange()
        )

        owner_cmds = [
            ("reload <cog> 🔒", "Reload a cog."),
            ("addadmin @user 🔒 / removeadmin @user 🔒", "Manage admins."),
            ("addpremium @user 🔒 / removepremium @user 🔒", "Manage premium users."),
            ("addstock <cat> <items> 🔒", "Add stock items."),
        ]
        admin_cmds = [
            ("managewhitelist @user add/remove", "Manage whitelist."),
            ("bypass @user add/remove", "Manage bypass list."),
            ("listadmins", "Show all admins."),
            ("listpremium", "Show premium users."),
            ("listwhitelist", "Show whitelisted users."),
            ("listbypass", "Show bypassed users."),
            ("showstock", "Show stock counts."),
            ("ping", "Check latency."),
        ]

        for n, d in owner_cmds + admin_cmds:
            embed.add_field(name=f"{PREFIX}{n}", value=d, inline=False)

        embed.set_footer(text="🔒 = Owner-only")
        await ctx.send(embed=embed)


# -----------------------
# Setup
# -----------------------
async def setup(bot):
    await bot.add_cog(Admin(bot))
