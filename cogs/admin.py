import discord
import datetime
import os
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx):
        guild = ctx.guild

        embed = discord.Embed()
        embed.set_thumbnail(url=guild.icon_url)
        if guild.banner_url != "":
            embed.set_image(url=guild.banner_url)
        embed.add_field(name="Server Name", value=guild.name, inline=False)
        embed.add_field(name="# Voice Channels", value=len(
            guild.voice_channels), inline=True)
        embed.add_field(name="# Text Channels", value=len(
            guild.text_channels), inline=True)
        embed.add_field(name="# AFK Channel",
                        value=guild.afk_channel, inline=True)
        embed.set_author(name=self.bot.user.name)
        embed.set_footer(text=datetime.datetime.now())

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f"Could not load extension. Reason: {e}")
            return
        await ctx.send(f"Extension [{cog}] loaded.")

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send("Could not unload extension.")
            return
        await ctx.send(f"Extension [{cog}] unloaded.")


def setup(bot):
    bot.add_cog(Admin(bot))
