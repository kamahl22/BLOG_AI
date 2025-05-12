from discord.ext import commands

class AlgoWallet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wallet(self, ctx):
        await ctx.send('Algorand wallet integration coming soon!')

def setup(bot):
    bot.add_cog(AlgoWallet(bot))
