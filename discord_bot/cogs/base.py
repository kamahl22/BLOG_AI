from discord.ext import commands

class Base(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send("🏓 Pong!")

    @commands.command(name="hello")
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.display_name}! Welcome to TBLOG 🤖")

async def setup(bot):
    await bot.add_cog(Base(bot))