import random

from discord.ext import commands


class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Gives a random numnber between 1 and 100")
    async def roll(self, ctx):
        n = random.randrange(1, 100)
        await ctx.send(f'You rolled: {n}')

    @commands.command(brief="Gives either Heads or Tails")
    async def coin(self, ctx):
        n = random.randrange(0, 1)
        await ctx.send(f'You rolled: { "Heads" if n == 1 else "Tails" }')


def setup(bot):
    bot.add_cog(RNG(bot))
