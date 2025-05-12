from discord.ext import commands
import discord
from discord_bot.utils.db import fetch_odds

class OddsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='odds')
    async def odds(self, ctx, sport='MLB'):
        """Fetches and displays game odds for the specified sport."""
        try:
            odds_data = await fetch_odds(sport)  # Fetch from Supabase
            if not odds_data:
                await ctx.send(f"No odds available for {sport}.")
                return
            embed = discord.Embed(title=f"{sport} Game Odds", color=0x00ff00)
            for game in odds_data:
                embed.add_field(
                    name=f"{game['home_team']} vs {game['away_team']}",
                    value=f"Moneyline: {game['moneyline_odds']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error fetching odds: {str(e)}")

async def setup(bot):
    await bot.add_cog(OddsCog(bot))