import discord
from discord.ext import commands


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member = None, reason: str = "No reason provided"):
        if member is not None:
            await ctx.guild.kick(member, reason=reason)
        else:
            await ctx.send("Please specify user to kick via mention.")
            return
        await ctx.send(f'User {member.name} kicked. Reason: {reason}.')

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member = None, reason: str = "No reason provided"):
        if member is not None:
            await ctx.guild.ban(member, reason=reason)
        else:
            await ctx.send("Please specify user to ban via mention.")
            return
        await ctx.send(f'User {member.name} banned. Reason: {reason}.')

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: str = "", reason: str = "No reason provided."):
        if member == "":
            await ctx.send("Please specify user to unban.")
            return
        bans = await ctx.guild.bans()
        for b in bans:
            if b.user.name == member:
                await ctx.guild.unban(member, reason=reason)
                await ctx.send(f'User {member} unbanned. Reason: {reason}.')
        await ctx.send(f'User {member} not found in ban list.')


def setup(bot):
    bot.add_cog(Moderator(bot))
