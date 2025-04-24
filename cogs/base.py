from discord.ext import commands

class Base(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="about")
    async def about_command(self, ctx):
        await ctx.send("🧠 I am BLOG_BOT, built on Algorand and Discord!")

async def setup(bot):
    await bot.add_cog(Base(bot))