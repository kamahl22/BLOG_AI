import discord
from discord.ext import commands
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class Roster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roster")
    async def get_roster(self, ctx, *, team_name: str):
        """
        !roster Yankees -> returns player list for Yankees from Supabase
        """
        try:
            response = supabase.table("roster_data").select("*").eq("team_name", team_name).execute()
            players = response.data

            if not players:
                await ctx.send(f"No roster found for `{team_name}`.")
                return

            message = f"**Roster for {team_name}:**\n"
            for player in players:
                message += f"- {player['player_name']} ({player['position']}, Age: {player['age']})\n"

            await ctx.send(message)
        except Exception as e:
            await ctx.send(f"Error fetching roster: {str(e)}")

def setup(bot):
    bot.add_cog(Roster(bot))