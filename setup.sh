#!/bin/bash
# setup.sh: Initialize the BLOG_AI project structure

# Create project root and directories
mkdir -p ~/BLOG_AI/{.github/workflows,chrome_extension,discord_bot/{cogs,utils},backend/app/{api,services},smart_contracts/tests,data_pipeline/{fetch,preprocess,model_training,storage/{raw,processed,predictions}},frontend/src/components,mobile/src,tests,docs,blockchain/{smart_contracts,scripts}}

# Navigate to project root
cd ~/BLOG_AI

# Initialize Git repository
if [ ! -d .git ]; then
    git init
fi

# Create root-level files
touch .gitignore .env README.md setup.sh requirements.txt

# Create CI/CD workflow
touch .github/workflows/ci.yml
cat << 'EOF' > .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r discord_bot/requirements.txt
          pip install -r backend/requirements.txt
          pip install -r data_pipeline/requirements.txt
          pip install -r blockchain/requirements.txt
      - name: Run tests
        run: pytest tests/
EOF

# Create chrome_extension/ files
touch chrome_extension/{manifest.json,popup.html,popup.js,content.js,requirements.txt}
cat << 'EOF' > chrome_extension/manifest.json
{
  "manifest_version": 3,
  "name": "BLOG_AI Betting Assistant",
  "version": "1.0",
  "permissions": ["activeTab"],
  "action": {
    "default_popup": "popup.html"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"]
    }
  ]
}
EOF
cat << 'EOF' > chrome_extension/popup.html
<!DOCTYPE html>
<html>
<body>
  <h1>BLOG_AI Betting Assistant</h1>
  <p>Loading odds...</p>
  <script src="popup.js"></script>
</body>
</html>
EOF
cat << 'EOF' > chrome_extension/popup.js
console.log('BLOG_AI extension loaded');
EOF
cat << 'EOF' > chrome_extension/content.js
console.log('BLOG_AI content script loaded');
EOF
touch chrome_extension/requirements.txt

# Create discord_bot/ files
touch discord_bot/{bot.py,.env,requirements.txt,.gitignore} discord_bot/cogs/{__init__.py,hello.py,algo_wallet.py} discord_bot/utils/logger.py
cat << 'EOF' > discord_bot/bot.py
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
EOF
cat << 'EOF' > discord_bot/cogs/hello.py
from discord.ext import commands

class Hello(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

def setup(bot):
    bot.add_cog(Hello(bot))
EOF
cat << 'EOF' > discord_bot/cogs/algo_wallet.py
from discord.ext import commands

class AlgoWallet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wallet(self, ctx):
        await ctx.send('Algorand wallet integration coming soon!')

def setup(bot):
    bot.add_cog(AlgoWallet(bot))
EOF
cat << 'EOF' > discord_bot/utils/logger.py
import logging

def setup_logger():
    logger = logging.getLogger('BLOG_AI')
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(console_handler)
    file_handler = logging.FileHandler('discord_bot/bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    logger.addHandler(file_handler)
    return logger
EOF
cat << 'EOF' > discord_bot/.env
DISCORD_TOKEN=your_discord_bot_token
EOF
cat << 'EOF' > discord_bot/.gitignore
.env
__pycache__/
*.pyc
bot.log
EOF
cat << 'EOF' > discord_bot/requirements.txt
discord.py==2.3.2
python-dotenv==1.0.1
EOF

# Create backend/ files
touch backend/app/{main.py,config.py} backend/app/api/{predictions.py,blockchain.py} backend/app/services/{predict_model.py,train_model.py,algo_tools.py} backend/{.env,requirements.txt}
cat << 'EOF' > backend/app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def root():
    return {'message': 'BLOG_AI API'}
EOF
cat << 'EOF' > backend/app/config.py
from dotenv import load_dotenv
import os

load_dotenv()
ALGORAND_API_KEY = os.getenv('ALGORAND_API_KEY')
EOF
cat << 'EOF' > backend/app/api/predictions.py
from fastapi import APIRouter

router = APIRouter()

@router.get('/predictions')
async def get_predictions():
    return {'message': 'Prediction endpoint'}
EOF
cat << 'EOF' > backend/app/api/blockchain.py
from fastapi import APIRouter

router = APIRouter()

@router.get('/blockchain')
async def get_blockchain():
    return {'message': 'Blockchain endpoint'}
EOF
cat << 'EOF' > backend/app/services/predict_model.py
def load_model():
    return {'message': 'Model loading placeholder'}
EOF
cat << 'EOF' > backend/app/services/train_model.py
def train_model():
    return {'message': 'Model training placeholder'}
EOF
cat << 'EOF' > backend/app/services/algo_tools.py
def create_wallet():
    return {'message': 'Algorand wallet placeholder'}
EOF
cat << 'EOF' > backend/.env
ALGORAND_API_KEY=your_algorand_api_key
EOF
cat << 'EOF' > backend/requirements.txt
fastapi==0.115.0
uvicorn==0.30.6
python-dotenv==1.0.1
pandas==2.2.3
scikit-learn==1.5.2
algosdk==2.7.0
EOF

# Create smart_contracts/ files
touch smart_contracts/{approval.teal,clear.teal,compile_contracts.py,deploy_contract.py} smart_contracts/tests/test_contracts.py
cat << 'EOF' > smart_contracts/approval.teal
#pragma version 6
int 1
return
EOF
cat << 'EOF' > smart_contracts/clear.teal
#pragma version 6
int 1
return
EOF
cat << 'EOF' > smart_contracts/compile_contracts.py
def compile_teal():
    return {'message': 'TEAL compilation placeholder'}
EOF
cat << 'EOF' > smart_contracts/deploy_contract.py
def deploy_contract():
    return {'message': 'Contract deployment placeholder'}
EOF
cat << 'EOF' > smart_contracts/tests/test_contracts.py
def test_contract():
    assert True, 'Contract test placeholder'
EOF

# Create data_pipeline/ files
touch data_pipeline/fetch/{fetch_espn.py,fetch_teamrankings.py} data_pipeline/preprocess/clean_data.py data_pipeline/model_training/train_model.py data_pipeline/storage/storage_config.py data_pipeline/requirements.txt
cat << 'EOF' > data_pipeline/fetch/fetch_espn.py
def fetch_espn_data():
    return {'message': 'ESPN scraping placeholder'}
EOF
cat << 'EOF' > data_pipeline/fetch/fetch_teamrankings.py
def fetch_teamrankings_data():
    return {'message': 'TeamRankings scraping placeholder'}
EOF
cat << 'EOF' > data_pipeline/preprocess/clean_data.py
def clean_data():
    return {'message': 'Data cleaning placeholder'}
EOF
cat << 'EOF' > data_pipeline/model_training/train_model.py
def train_model():
    return {'message': 'Model training placeholder'}
EOF
cat << 'EOF' > data_pipeline/storage/storage_config.py
SQLITE_DB_PATH = 'sports_data.db'
EOF
cat << 'EOF' > data_pipeline/requirements.txt
requests==2.32.3
beautifulsoup4==4.12.3
pandas==2.2.3
sqlite3
EOF

# Create frontend/ files
mkdir -p frontend/{public,src}
touch frontend/src/{App.jsx,index.jsx} frontend/src/components/.gitkeep frontend/{vite.config.js,package.json,README.md}
cat << 'EOF' > frontend/src/App.jsx
import React from 'react';

function App() {
  return (
    <div>
      <h1>BLOG_AI: Sports Betting Platform</h1>
      <p>Welcome to BLOG_AI!</p>
    </div>
  );
}

export default App;
EOF
cat << 'EOF' > frontend/src/index.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
EOF
cat << 'EOF' > frontend/vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()]
});
EOF
cat << 'EOF' > frontend/package.json
{
  "name": "blog-ai-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "serve": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.4.8"
  }
}
EOF
cat << 'EOF' > frontend/README.md
# BLOG_AI Frontend

React/Vite frontend for the BLOG_AI platform.

## Setup
1. Run `npm install`
2. Run `npm run dev`
EOF

# Create mobile/ files
touch mobile/src/App.js mobile/{package.json,README.md}
cat << 'EOF' > mobile/src/App.js
import React from 'react';
import { View, Text } from 'react-native';

export default function App() {
  return (
    <View>
      <Text>BLOG_AI Mobile App</Text>
    </View>
  );
}
EOF
cat << 'EOF' > mobile/package.json
{
  "name": "blog-ai-mobile",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios"
  },
  "dependencies": {
    "expo": "~51.0.8",
    "react": "18.2.0",
    "react-native": "0.74.5"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0"
  }
}
EOF
cat << 'EOF' > mobile/README.md
# BLOG_AI Mobile

React Native mobile app for the BLOG_AI platform.

## Setup
1. Run `npm install`
2. Run `npm start`
EOF

# Create blockchain/ files
touch blockchain/{__init__.py,config.py,client.py,wallet.py,transactions.py,asa_utils.py,.env,.gitignore,requirements.txt}
touch blockchain/smart_contracts/{__init__.py,approval.teal,clear.teal,compile_contracts.py}
touch blockchain/scripts/{create_wallet.py,fund_wallet.py,send_token.py,deploy_smart_contract.py}
cat << 'EOF' > blockchain/__init__.py
EOF
cat << 'EOF' > blockchain/config.py
import os
from dotenv import load_dotenv

load_dotenv()

ALGORAND_NODE = os.getenv("ALGORAND_NODE", "https://testnet-api.algonode.cloud")
ALGORAND_TOKEN = os.getenv("ALGORAND_TOKEN", "")
ALGORAND_INDEXER = os.getenv("ALGORAND_INDEXER", "https://testnet-idx.algonode.cloud")
EOF
cat << 'EOF' > blockchain/client.py
from algosdk.v2client import algod, indexer
from .config import ALGORAND_NODE, ALGORAND_TOKEN, ALGORAND_INDEXER

def get_algod_client():
    headers = {"X-API-Key": ALGORAND_TOKEN} if ALGORAND_TOKEN else {}
    return algod.AlgodClient(ALGORAND_TOKEN, ALGORAND_NODE, headers)

def get_indexer_client():
    headers = {"X-API-Key": ALGORAND_TOKEN} if ALGORAND_TOKEN else {}
    return indexer.IndexerClient("", ALGORAND_INDEXER, headers)
EOF
cat << 'EOF' > blockchain/wallet.py
from algosdk import account, mnemonic

def create_wallet():
    private_key, address = account.generate_account()
    mnemonic_phrase = mnemonic.from_private_key(private_key)
    return {"address": address, "private_key": private_key, "mnemonic": mnemonic_phrase}

def recover_wallet(mnemonic_phrase):
    private_key = mnemonic.to_private_key(mnemonic_phrase)
    address = account.address_from_private_key(private_key)
    return {"address": address, "private_key": private_key}
EOF
cat << 'EOF' > blockchain/transactions.py
from algosdk import transaction
from .client import get_algod_client

def send_algo(sender, receiver, amount, private_key, note=""):
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.PaymentTxn(sender, params, receiver, amount, note=note.encode())
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid
EOF
cat << 'EOF' > blockchain/asa_utils.py
from algosdk import transaction
from .client import get_algod_client

def create_asa(creator, total, decimals, asset_name, unit_name, private_key):
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator,
        sp=params,
        total=total,
        decimals=decimals,
        asset_name=asset_name,
        unit_name=unit_name,
        manager=creator,
        reserve=creator,
        freeze=creator,
        clawback=creator
    )
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid
EOF
cat << 'EOF' > blockchain/.env
ALGORAND_NODE=https://testnet-api.algonode.cloud
ALGORAND_INDEXER=https://testnet-idx.algonode.cloud
ALGORAND_TOKEN=
EOF
cat << 'EOF' > blockchain/.gitignore
.env
__pycache__/
*.pyc
EOF
cat << 'EOF' > blockchain/requirements.txt
algosdk==2.7.0
python-dotenv==1.0.1
EOF
cat << 'EOF' > blockchain/smart_contracts/__init__.py
EOF
cat << 'EOF' > blockchain/smart_contracts/approval.teal
#pragma version 6
int 1
return
EOF
cat << 'EOF' > blockchain/smart_contracts/clear.teal
#pragma version 6
int 1
return
EOF
cat << 'EOF' > blockchain/smart_contracts/compile_contracts.py
from algosdk import encoding
from blockchain.client import get_algod_client

def compile_teal(source_code):
    client = get_algod_client()
    compiled = client.compile(source_code)
    return encoding.decode_address(compiled["result"])
EOF
cat << 'EOF' > blockchain/scripts/create_wallet.py
from blockchain.wallet import create_wallet

if __name__ == "__main__":
    wallet = create_wallet()
    print(f"Address: {wallet['address']}")
    print(f"Mnemonic: {wallet['mnemonic']}")
    print("Store the mnemonic securely!")
EOF
cat << 'EOF' > blockchain/scripts/fund_wallet.py
from blockchain.transactions import send_algo

if __name__ == "__main__":
    sender = input("Enter sender address: ")
    receiver = input("Enter receiver address: ")
    amount = int(input("Enter amount in microAlgos: "))
    private_key = input("Enter sender private key: ")
    txid = send_algo(sender, receiver, amount, private_key)
    print(f"Transaction ID: {txid}")
EOF
cat << 'EOF' > blockchain/scripts/send_token.py
from algosdk import transaction
from blockchain.client import get_algod_client

if __name__ == "__main__":
    sender = input("Enter sender address: ")
    receiver = input("Enter receiver address: ")
    asset_id = int(input("Enter TBLOG asset ID: "))
    amount = int(input("Enter amount: "))
    private_key = input("Enter sender private key: ")
    client = get_algod_client()
    params = client.suggested_params()
    txn = transaction.AssetTransferTxn(sender, params, receiver, amount, asset_id)
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    print(f"Transaction ID: {txid}")
EOF
cat << 'EOF' > blockchain/scripts/deploy_smart_contract.py
from algosdk import transaction
from blockchain.client import get_algod_client

def deploy_contract(approval_program, clear_program, creator, private_key):
    client = get_algod_client()
    params = client.suggested_params()
    app_create_txn = transaction.ApplicationCreateTxn(
        sender=creator,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval_program,
        clear_program=clear_program,
        global_schema=transaction.StateSchema(num_uints=1, num_byte_slices=1),
        local_schema=transaction.StateSchema(num_uints=0, num_byte_slices=0)
    )
    signed_txn = app_create_txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return txid

if __name__ == "__main__":
    print("Deploy smart contract: TBD")
EOF

# Create tests/ files
touch tests/{test_discord_bot.py,test_backend.py,test_data_pipeline.py,test_chrome_extension.py}
cat << 'EOF' > tests/test_discord_bot.py
def test_bot():
    assert True, 'Discord bot test placeholder'
EOF
cat << 'EOF' > tests/test_backend.py
def test_api():
    assert True, 'Backend API test placeholder'
EOF
cat << 'EOF' > tests/test_data_pipeline.py
def test_pipeline():
    assert True, 'Data pipeline test placeholder'
EOF
cat << 'EOF' > tests/test_chrome_extension.py
def test_extension():
    assert True, 'Chrome extension test placeholder'
EOF

# Create docs/ files
touch docs/{architecture.mmd,setup.md,api.md,data_pipeline.md,extension.md,business_plan.md,business_model.md,compliance.md}
cat << 'EOF' > docs/architecture.mmd
graph TD
    A[Chrome Extension] --> B[FastAPI Backend]
    C[Mobile App] --> B
    D[Website] --> B
    E[Discord Bot] --> B
    B --> F[ML Models]
    B --> G[Algorand Blockchain]
    F --> H[Data Pipeline]
    H --> I[Storage: SQLite]
EOF
cat << 'EOF' > docs/setup.md
# Setup Guide

1. Run `./setup.sh` to initialize the project.
2. See individual component READMEs for setup instructions.
EOF
cat << 'EOF' > docs/api.md
# API Documentation

Placeholder for FastAPI endpoints.
EOF
cat << 'EOF' > docs/data_pipeline.md
# Data Pipeline Documentation

Placeholder for data fetching and processing.
EOF
cat << 'EOF' > docs/extension.md
# Chrome Extension Documentation

Placeholder for extension setup and usage.
EOF
cat << 'EOF' > docs/business_plan.md
# Business Plan

Placeholder for BLOG_AI business strategy.
EOF
cat << 'EOF' > docs/business_model.md
# Business Model

Placeholder for BLOG_AI revenue model.
EOF
cat << 'EOF' > docs/compliance.md
# Compliance

Placeholder for legal and regulatory compliance.
EOF

# Create root-level files
cat << 'EOF' > .gitignore
node_modules/
.env
__pycache__/
*.db
*.log
frontend/dist/
mobile/android/
mobile/ios/
discord_bot/.env
backend/.env
blockchain/.env
EOF
cat << 'EOF' > .env
DISCORD_TOKEN=your_discord_bot_token
ALGORAND_API_KEY=your_algorand_api_key
EOF
cat << 'EOF' > README.md
# BLOG_AI: AI-Powered Sports Betting Platform

A decentralized sports betting platform with AI-driven predictions, Chrome extension, mobile app, website, and Discord bot. Uses TBLOG token on Algorand TestNet.

## Quick Start
1. Run `./setup.sh` to initialize.
2. See `docs/setup.md` for detailed instructions.

## Structure
- `chrome_extension/`: Odds parsing extension
- `discord_bot/`: Community engagement bot
- `backend/`: FastAPI API and blockchain services
- `smart_contracts/`: Algorand smart contracts
- `data_pipeline/`: Sports data and ML predictions
- `frontend/`: React/Vite website
- `mobile/`: React Native mobile app
- `blockchain/`: Algorand blockchain integration
- `tests/`: Unit and integration tests
- `docs/`: Documentation
EOF
cat << 'EOF' > requirements.txt
pytest==8.3.3
flake8==7.1.1
EOF

# Git operations
git add .
git commit -m "Initial commit: Full BLOG_AI project structure with blockchain"
# Set up remote (uncomment after creating https://github.com/kamahl22/BLOG_AI)
# git remote add origin https://github.com/kamahl22/BLOG_AI.git
# git push -u origin main

echo "BLOG_AI project structure created in ~/BLOG_AI"
echo "To push to GitHub, create https://github.com/kamahl22/BLOG_AI, then run:"
echo "  git remote add origin https://github.com/kamahl22/BLOG_AI.git"
echo "  git push -u origin main"
EOF