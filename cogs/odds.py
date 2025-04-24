from discord.ext import commands

class Odds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def odds(self, ctx):
        await ctx.send("📊 Fetching odds...")

async def setup(bot):
    await bot.add_cog(Odds(bot))