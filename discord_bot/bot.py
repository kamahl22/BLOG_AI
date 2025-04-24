import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logger = setup_logger()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')

async def load_cogs():
    try:
        await bot.load_extension('cogs.hello')
        await bot.load_extension('cogs.algo_wallet')
        logger.info("Cogs loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load cogs: {e}")

async def main():
    await load_cogs()
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
