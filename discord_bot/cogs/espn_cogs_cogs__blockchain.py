import discord
from discord.ext import commands
from algosdk.v2client import algod
from dotenv import load_dotenv
import os

load_dotenv()

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
ASA_ID = 737897145

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

class Blockchain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='check_opt_in')
    async def check_opt_in(self, ctx, wallet_address: str):
        try:
            account_info = client.account_info(wallet_address)
            holding = next((a for a in account_info.get("assets", []) if a["asset-id"] == ASA_ID), None)
            if holding:
                await ctx.send(f"✅ Wallet `{wallet_address}` is opted in to TBLOG.")
            else:
                await ctx.send(f"❌ Wallet `{wallet_address}` is NOT opted in.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(Blockchain(bot))