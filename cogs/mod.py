# cogs/mod.py
from discord.ext import commands
import discord
from config import PREFIX
from datetime import timedelta

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -----------------------
    # Kick Command
    # -----------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Kick a member from the server."""
        if not member:
            return await ctx.send(f"❌ Usage: `{PREFIX}kick @user <reason>`")

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member}** has been kicked from the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Kicked by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Could not kick {member}. Error: {e}")

    # -----------------------
    # Ban Command
    # -----------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Ban a member from the server."""
        if not member:
            return await ctx.send(f"❌ Usage: `{PREFIX}ban @user <reason>`")

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="⛔ Member Banned",
                description=f"**{member}** has been banned from the server.",
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Banned by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Could not ban {member}. Error: {e}")

    # -----------------------
    # Unban Command
    # -----------------------
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member_name: str = None):
        """Unban a member by name#discriminator."""
        if not member_name:
            return await ctx.send(f"❌ Usage: `{PREFIX}unban username#1234`")
        banned_users = await ctx.guild.bans()
        try:
            member_name, member_discriminator = member_name.split("#")
        except ValueError:
            return await ctx.send("❌ Please use the format `username#1234`.")

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(
                    title="✅ Member Unbanned",
                    description=f"**{user}** has been unbanned from the server.",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Unbanned by {ctx.author}")
                return await ctx.send(embed=embed)
        await ctx.send(f"❌ User `{member_name}#{member_discriminator}` not found in banned list.")

    # -----------------------
    # Mute Command (Timeout)
    # -----------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member = None, minutes: int = 5, *, reason: str = "No reason provided"):
        """Timeout a member for a specific duration in minutes."""
        if not member:
            return await ctx.send(f"❌ Usage: `{PREFIX}mute @user <minutes> <reason>`")
        if minutes < 1:
            return await ctx.send("❌ Duration must be at least 1 minute.")

        try:
            await member.timeout(duration=timedelta(minutes=minutes), reason=reason)
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"**{member}** has been muted for **{minutes} minutes**.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Muted by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Could not mute {member}. Error: {e}")

    # -----------------------
    # Unmute Command
    # -----------------------
    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member = None):
        """Remove timeout from a member."""
        if not member:
            return await ctx.send(f"❌ Usage: `{PREFIX}unmute @user`")
        try:
            await member.timeout(duration=None)
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"**{member}** has been unmuted.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Unmuted by {ctx.author}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Could not unmute {member}. Error: {e}")

    # -----------------------
    # Clear Messages
    # -----------------------
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Clear a number of messages from a channel."""
        if amount < 1:
            return await ctx.send("❌ Amount must be at least 1.")
        deleted = await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title="🧹 Messages Cleared",
            description=f"Deleted **{len(deleted)}** message(s).",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Cleared by {ctx.author}")
        await ctx.send(embed=embed, delete_after=5)

    # -----------------------
    # Warn Command
    # -----------------------
    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        """Warn a member."""
        if not member:
            return await ctx.send(f"❌ Usage: `{PREFIX}warn @user <reason>`")
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"**{member}** has been warned.",
            color=discord.Color.gold()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.set_footer(text=f"Warned by {ctx.author}")
        await ctx.send(embed=embed)

    # -----------------------
    # Moderation Help Command
    # -----------------------
    @commands.command(name="modhelp")
    async def mod_help(self, ctx):
        """Show moderation commands help."""
        embed = discord.Embed(
            title="🛡️ Moderation Commands Help",
            description=f"Prefix: `{PREFIX}`\nYou need proper permissions to use these commands.",
            color=discord.Color.orange()
        )

        commands_list = [
            (f"{PREFIX}kick @user <reason>", "Kick a member from the server."),
            (f"{PREFIX}ban @user <reason>", "Ban a member from the server."),
            (f"{PREFIX}unban username#1234", "Unban a member by name#discriminator."),
            (f"{PREFIX}mute @user <minutes> <reason>", "Mute a member for specific duration (timeout)."),
            (f"{PREFIX}unmute @user", "Remove timeout from a member."),
            (f"{PREFIX}clear <amount>", "Clear a number of messages from the channel."),
            (f"{PREFIX}warn @user <reason>", "Warn a member.")
        ]

        for name, desc in commands_list:
            embed.add_field(name=name, value=desc, inline=False)

        embed.set_footer(text="⚠️ Permissions required are noted per command | All members can view this help")
        await ctx.send(embed=embed)

# -----------------------
# Setup
# -----------------------
async def setup(bot):
    await bot.add_cog(Moderation(bot))
