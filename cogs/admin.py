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
            return {"whitelist": [], "bypass": [], "admins": [], "cooldowns": {}}

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
    # Admin Help (usable by all)
    # -----------------------
    @commands.command(name="adminhelp")
    async def admin_help(self, ctx):
        embed = discord.Embed(
            title="🛠️ Admin Commands Help",
            description=f"Prefix: `{PREFIX}`\nCommands marked 🔒 are owner-only.",
            color=discord.Color.orange()
        )
        # OWNER ONLY COMMANDS
        embed.add_field(name=f"{PREFIX}reload <cog> 🔒", value="Reload a cog without restarting the bot.", inline=False)
        embed.add_field(name=f"{PREFIX}managewhitelist @user add/remove 🔒", value="Add or remove a user from whitelist.", inline=False)
        embed.add_field(name=f"{PREFIX}bypass @user add/remove 🔒", value="Add or remove a user from bypass list.", inline=False)
        embed.add_field(name=f"{PREFIX}listwhitelist 🔒", value="Show all whitelisted users.", inline=False)
        embed.add_field(name=f"{PREFIX}listbypass 🔒", value="Show all bypassed users.", inline=False)
        embed.add_field(name=f"{PREFIX}addadmin @user 🔒", value="Add a new admin.", inline=False)
        embed.add_field(name=f"{PREFIX}removeadmin @user 🔒", value="Remove an admin.", inline=False)
        embed.add_field(name=f"{PREFIX}addpremium @user 🔒", value="Add a user to premium access.", inline=False)
        embed.add_field(name=f"{PREFIX}removepremium @user 🔒", value="Remove a user from premium access.", inline=False)
        embed.add_field(name=f"{PREFIX}addstock <category> <item1,item2,...> 🔒", value="Add items to stock.", inline=False)

        #ADMIN ONLY COMMANDS
        embed.add_field(name=f"{PREFIX}listadmins", value="List all current admins.", inline=False)
        embed.add_field(name=f"{PREFIX}listpremium", value="Show all premium users.", inline=False)
        embed.add_field(name=f"{PREFIX}showstock", value="Show all stock items.", inline=False)
        embed.add_field(name=f"{PREFIX}ping", value="Check bot latency.", inline=False)
        embed.add_field(name=f"{PREFIX}modhelp", value="    Show Moderation Commands", inline=False)

        embed.set_footer(text="🔒 = Supreme Owner only | All members can view this help")
        await ctx.send(embed=embed)

    # -----------------------
    # Add stock (owner only)
    # -----------------------
    @commands.command()
    async def addstock(self, ctx, category: str = None, *, items: str = None):
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")

        if not category or not items:
            return await ctx.send(f"❌ Usage: `{PREFIX}addstock <category> <item1,item2,...>`")

        # Load generated.json
        try:
            with open(GENERATED_FILE, "r") as f:
                gen_data = json.load(f)
        except FileNotFoundError:
            gen_data = {}

        category = category.upper()
        new_items = [item.strip() for item in items.split(",") if item.strip()]

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
        embed.add_field(name="Items", value="\n".join(new_items), inline=False)
        await ctx.send(embed=embed)


    @commands.command()
    async def ping(self, ctx):
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)  # ms
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latency: **{latency} ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="showstock")
    async def show_stock(self, ctx, category: str = None):
        """Show all stock or a specific category (admins only)."""
        users = self.load_users()
        admins = users.get("admins", [])
        if ctx.author.id not in admins and not self.is_owner(ctx.author.id):
            return await ctx.send("❌ You are not allowed to use this command.")

        try:
            with open("data/generated.json", "r") as f:
                gen_data = json.load(f)
        except FileNotFoundError:
            return await ctx.send("⚠️ No stock data found.")

        if not gen_data:
            return await ctx.send("⚠️ The stock is currently empty.")

        # If a specific category is requested
        if category:
            category = category.upper()
            if category not in gen_data or not gen_data[category]:
                return await ctx.send(f"⚠️ No stock found for `{category}`.")
            embed = discord.Embed(
                title=f"📦 Stock for {category}",
                description="\n".join(gen_data[category]),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        # Otherwise show all categories
        embed = discord.Embed(
            title="📦 All Stock Categories",
            color=discord.Color.green()
        )
        for cat, items in gen_data.items():
            item_count = len(items)
            preview = ", ".join(items[:5]) + (" ..." if item_count > 5 else "")
            embed.add_field(
                name=f"{cat} ({item_count} items)",
                value=preview or "No items",
                inline=False
            )

        await ctx.send(embed=embed)

        # -----------------------
    # Premium User Management
    # -----------------------
    @commands.command(name="addpremium")
    async def add_premium(self, ctx, user: discord.Member = None):
        """Add a user to the premium list (owner only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only the Owner can use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}addpremium @user`")

        users = self.load_users()
        premium = users.get("premium", [])
        if user.id in premium:
            return await ctx.send(f"✅ {user.mention} is already a premium user.")
        premium.append(user.id)
        users["premium"] = premium
        self.save_users(users)
        await ctx.send(f"✅ {user.mention} has been added to premium users.")

    @commands.command(name="removepremium")
    async def remove_premium(self, ctx, user: discord.Member = None):
        """Remove a user from the premium list (owner only)."""
        if not self.is_owner(ctx.author.id):
            return await ctx.send("❌ Only the Owner can use this command.")
        if not user:
            return await ctx.send(f"❌ Usage: `{PREFIX}removepremium @user`")

        users = self.load_users()
        premium = users.get("premium", [])
        if user.id not in premium:
            return await ctx.send(f"⚠️ {user.mention} is not a premium user.")
        premium.remove(user.id)
        users["premium"] = premium
        self.save_users(users)
        await ctx.send(f"✅ {user.mention} has been removed from premium users.")

    @commands.command(name="listpremium")
    async def list_premium(self, ctx):
        """List all premium users (admins & owner only)."""
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
# Setup function
# -----------------------
async def setup(bot):
    await bot.add_cog(Admin(bot))
