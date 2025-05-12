import discord
from discord.ext import commands
from supabase import create_client
import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting bot script")

load_dotenv()

# Verify environment variables
discord_token = os.getenv("DISCORD_TOKEN")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
if not all([discord_token, supabase_url, supabase_key]):
    logger.error("Missing environment variables: DISCORD_TOKEN=%s, SUPABASE_URL=%s, SUPABASE_KEY=%s",
                 discord_token, supabase_url, supabase_key)
    exit(1)

logger.info("Environment variables loaded")

# Define intents
intents = discord.Intents.default()
intents.message_content = True
logger.info("Intents configured")

# Initialize bot
try:
    bot = commands.Bot(command_prefix="!", intents=intents)
    logger.info("Bot initialized")
except Exception as e:
    logger.error(f"Failed to initialize bot: {str(e)}")
    exit(1)

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user}")

@bot.command()
async def odds(ctx, *, team_name):
    logger.info(f"Received !odds command for {team_name}")
    try:
        supabase = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized")
        response = supabase.table("odds_data").select("*").eq("team_name", team_name).execute()
        if response.data:
            for game in response.data:
                await ctx.send(
                    f"{game['team_name']} vs {game['opponent']} ({game['game_date']}): "
                    f"Moneyline: {game['moneyline_odds']}, Spread: {game['spread']}, O/U: {game['over_under']}"
                )
        else:
            await ctx.send(f"No odds found for {team_name}")
    except Exception as e:
        logger.error(f"Error in !odds: {str(e)}")
        await ctx.send(f"Error: {str(e)}")

try:
    logger.info("Attempting to run bot")
    bot.run(discord_token)
except Exception as e:
    logger.error(f"Failed to run bot: {str(e)}")
    exit(1)