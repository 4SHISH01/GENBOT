import discord
from discord.ext import commands
import json, asyncio, random, os, time

USERS_FILE = "data/users.json"
STOCK_FILE = "data/generated.json"
VOUCH_CHANNEL_ID = 1417034611116212305   # <== CHANGE THIS

class FreeGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helpers
    def load_users(self):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            return {"whitelist": [], "bypass": [], "admins": [], "cooldowns": {}, "premium": []}

    def save_users(self, data):
        with open(USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def load_stock(self):
        if not os.path.exists(STOCK_FILE):
            return {}
        with open(STOCK_FILE, "r") as f:
            return json.load(f)

    def save_stock(self, data):
        with open(STOCK_FILE, "w") as f:
            json.dump(data, f, indent=4)

    async def send_item(self, interaction: discord.Interaction, category: str):
        users = self.load_users()
        data = users.get("cooldowns", {})
        now = time.time()
        uid = str(interaction.user.id)

        # cooldown
        if uid in data and now - data[uid] < 3600:
            remain = int(3600 - (now - data[uid]))
            return await interaction.response.send_message(
                f"⏳ You must wait **{remain//60}m {remain%60}s** before generating again.",
                ephemeral=True
            )

        # whitelist/bypass check
        if interaction.user.id not in users.get("whitelist", []) and interaction.user.id not in users.get("bypass", []):
            return await interaction.response.send_message(
                "❌ You are not whitelisted to use free gen.", ephemeral=True
            )

        stock = self.load_stock()
        category = category.upper()
        if category not in stock or len(stock[category]) == 0:
            return await interaction.response.send_message(
                f"⚠️ No stock available for `{category}`.", ephemeral=True
            )

        # pop one item
        item = stock[category].pop(0)
        self.save_stock(stock)

        # update cooldown
        data[uid] = now
        users["cooldowns"] = data
        self.save_users(users)

        # success msg
        await interaction.response.send_message(
            f"🎁 **{category} Generated**\n```\n{item}\n```", ephemeral=False
        )

        # vouch reminder
        vouch_channel = interaction.guild.get_channel(VOUCH_CHANNEL_ID)
        if vouch_channel:
            await interaction.followup.send(
                f"✅ Please vouch in {vouch_channel.mention} to continue using the bot!",
                ephemeral=False
            )

    @commands.command(name="gen")
    async def gen_command(self, ctx):
        """Send the gen panel with buttons"""
        view = discord.ui.View(timeout=120)

        for cat in ["MCFA", "CRUNCHYROLL", "XBOX"]:
            async def make_callback(category):
                async def callback(interaction: discord.Interaction):
                    await self.send_item(interaction, category)
                    for b in view.children:
                        b.disabled = True
                    await interaction.message.edit(view=view)
                return callback

            btn = discord.ui.Button(label=cat, style=discord.ButtonStyle.green)
            btn.callback = await make_callback(cat)
            view.add_item(btn)

        embed = discord.Embed(
            title="🎯 Free Generator",
            description="Click a button to generate a stock item.\nCooldown: **1 hour**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(FreeGen(bot))
