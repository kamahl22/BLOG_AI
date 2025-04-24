from discord.ext import commands

class AlgoWallet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wallet(self, ctx):
        await ctx.send("🪙 TBLOG Wallet command loaded!")

async def setup(bot):
    await bot.add_cog(AlgoWallet(bot))