# ~/BLOG_AI/bot.py
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} is ready!')

bot.run('YOUR_DISCORD_TOKEN')