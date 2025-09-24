# cogs/premiumgen.py
import discord
from discord.ext import commands
import json
import asyncio
from config import PREFIX, OWNER_ID

USERS_FILE = "data/users.json"
GENERATED_FILE = "data/generated.json"
COOLDOWN_TIME = 3600  # 1 hour in seconds

class PremiumGen(commands.Cog):
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

    def load_generated(self):
        try:
            with open(GENERATED_FILE, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_generated(self, data):
        with open(GENERATED_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def is_premium(self, user_id):
        users = self.load_users()
        return user_id in users.get("premium", [])

    def check_cooldown(self, user_id):
        users = self.load_users()
        cooldowns = users.get("cooldowns", {})
        last_time = cooldowns.get(str(user_id), 0)
        return (asyncio.get_event_loop().time() - last_time) < COOLDOWN_TIME

    def set_cooldown(self, user_id):
        users = self.load_users()
        if "cooldowns" not in users:
            users["cooldowns"] = {}
        users["cooldowns"][str(user_id)] = asyncio.get_event_loop().time()
        self.save_users(users)

    # -----------------------
    # Premium gen command
    # -----------------------
    @commands.command()
    async def premiumgen(self, ctx):
        user_id = ctx.author.id

        if not self.is_premium(user_id):
            return await ctx.send("❌ You are not a premium user. Contact an admin to get access.")

        if self.check_cooldown(user_id):
            return await ctx.send("⏳ You can only use this command once per hour. Wait before generating again.")

        # Load generated data
        gen_data = self.load_generated()
        categories = ["PMCFA", "STEAM"]

        # Create a button view
        class PremiumView(discord.ui.View):
            def __init__(self):
                super().__init__(timeout=60)  # buttons active for 60 seconds
                self.value = None

            async def disable_buttons(self):
                for child in self.children:
                    child.disabled = True

            @discord.ui.button(label="PMCFA", style=discord.ButtonStyle.success)
            async def pmcfa_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.send_item(interaction, "PMCFA")

            @discord.ui.button(label="STEAM", style=discord.ButtonStyle.success)
            async def steam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.send_item(interaction, "STEAM")

            async def send_item(self, interaction: discord.Interaction, category: str):
                items = gen_data.get(category, [])
                if not items:
                    await interaction.response.send_message(f"⚠️ No items left in `{category}`.", ephemeral=True)
                    return

                # Pop the first item
                item = items.pop(0)
                self.disable_buttons()  # disable buttons after use
                # Save updated generated.json
                PremiumGen.save_generated(self, gen_data)
                self.disable_buttons()
                # Send DM to user
                try:
                    await interaction.user.send(f"Here is your {category} item: `{item}`")
                    await interaction.response.send_message(f"✅ {category} key sent to your DMs!", ephemeral=False)
                    # Set cooldown
                    PremiumGen.set_cooldown(self, interaction.user.id)
                except discord.Forbidden:
                    await interaction.response.send_message("❌ I cannot DM you. Enable DMs and try again.", ephemeral=True)

        # Send the message with buttons
        embed = discord.Embed(
            title="🎁 Premium Generator",
            description="Select a category below to generate your item (1 per hour).",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed, view=PremiumView())

# -----------------------
# Setup function
# -----------------------
async def setup(bot):
    await bot.add_cog(PremiumGen(bot))
