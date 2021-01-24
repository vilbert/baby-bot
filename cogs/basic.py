from discord.ext import commands


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Ping: {round(self.bot.latency * 1000)}ms")

    @commands.command(brief="Create instant invite link to the channel that valids for 1 hour.")
    @commands.guild_only()
    async def invite(self, ctx):
        link = await ctx.channel.create_invite(max_age=3600)
        await ctx.send(f'{link}')


def setup(bot):
    bot.add_cog(Basic(bot))
