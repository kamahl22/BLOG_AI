#!/bin/bash
# setup.sh: Initialize the BLOG project structure

# Create project root and directories
mkdir -p ~/BLOG/{.github/workflows,chrome_extension,discord_bot/{cogs,utils},backend/app/{api,services},smart_contracts/tests,data_pipeline/{fetch,preprocess,model_training,storage/{raw,processed,predictions}},frontend/src/components,mobile/src,tests,docs}

# Navigate to project root
cd ~/BLOG

# Initialize Git repository
git init

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
      - name: Run tests
        run: pytest tests/
EOF

# Create chrome_extension/ files
touch chrome_extension/{manifest.json,popup.html,popup.js,content.js,requirements.txt}
cat << 'EOF' > chrome_extension/manifest.json
{
  "manifest_version": 3,
  "name": "BLOG Betting Assistant",
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
  <h1>BLOG Betting Assistant</h1>
  <p>Loading odds...</p>
  <script src="popup.js"></script>
</body>
</html>
EOF
cat << 'EOF' > chrome_extension/popup.js
console.log('BLOG extension loaded');
EOF
cat << 'EOF' > chrome_extension/content.js
console.log('BLOG content script loaded');
EOF
touch chrome_extension/requirements.txt

# Create discord_bot/ files
touch discord_bot/{bot.py,.env,requirements.txt} discord_bot/cogs/{__init__.py,hello.py,algo_wallet.py} discord_bot/utils/logger.py
cat << 'EOF' > discord_bot/bot.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

bot.load_extension('cogs.hello')
bot.run(TOKEN)
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
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger('BLOG')
EOF
cat << 'EOF' > discord_bot/.env
DISCORD_TOKEN=your_discord_bot_token
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
    return {'message': 'BLOG API'}
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
      <h1>BLOG: Sports Betting Platform</h1>
      <p>Welcome to BLOG!</p>
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
  "name": "blog-frontend",
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
# BLOG Frontend

React/Vite frontend for the BLOG platform.

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
      <Text>BLOG Mobile App</Text>
    </View>
  );
}
EOF
cat << 'EOF' > mobile/package.json
{
  "name": "blog-mobile",
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
# BLOG Mobile

React Native mobile app for the BLOG platform.

## Setup
1. Run `npm install`
2. Run `npm start`
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
2.میت

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
EOF
cat << 'EOF' > .env
# Root-level environment variables
DISCORD_TOKEN=your_discord_bot_token
ALGORAND_API_KEY=your_algorand_api_key
EOF
cat << 'EOF' > README.md
# BLOG: AI-Powered Sports Betting Platform

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
- `tests/`: Unit and integration tests
- `docs/`: Documentation
EOF
cat << 'EOF' > requirements.txt
pytest==8.3.3
flake8==7.1.1
EOF

# Git operations
git add .
git commit -m "Initial commit: Full project structure setup"
# Uncomment to push to GitHub after verifying
# git remote add origin https://github.com/kamahl22/BLOG.git
# git push -u origin main

echo "BLOG project structure created in ~/BLOG"
EOF

---

### Instructions to Use
1. **Save the Script**:
   - Copy the script content into a file named `setup.sh` in your home directory or desired location (e.g., `~/setup.sh`).
   - Alternatively, if you’re in a temporary directory, move it to `~/BLOG/setup.sh` after creation.

2. **Make Executable**:
   ```bash
   chmod +x ~/BLOG/setup.sh
   ```

3. **Run the Script**:
   ```bash
   ./setup.sh
   ```
   This will:
   - Create the `~/BLOG` directory and all subdirectories/files.
   - Initialize a Git repository.
   - Commit the initial structure.
   - Output: `BLOG project structure created in ~/BLOG`.

4. **Verify the Structure**:
   ```bash
   cd ~/BLOG
   tree -a
   ```
   Check that all directories and files match the recommended structure.

5. **Set Up GitHub** (Manual Step):
   - Create a repository at `https://github.com/kamahl22/BLOG` if it doesn’t exist.
   - Uncomment the Git push commands in `setup.sh` or run manually:
     ```bash
     git remote add origin https://github.com/kamahl22/BLOG.git
     git push -u origin main
     ```

6. **Next Steps**:
   - **Discord Bot**: Update `discord_bot/.env` with your bot token and run `python discord_bot/bot.py`.
   - **Backend**: Install dependencies (`pip install -r backend/requirements.txt`) and start the server (`uvicorn backend.app.main:app --reload`).
   - **Frontend**: Run `cd frontend && npm install && npm run dev` to start the React app.
   - **Mobile**: Run `cd mobile && npm install && npm start` for the React Native app.
   - **Tests**: Run `pytest tests/` after installing root dependencies (`pip install -r requirements.txt`).

---

### Notes
- **Fresh Start**: The script assumes a clean slate, creating `~/BLOG` from scratch. If `~/BLOG` already exists, delete it (`rm -rf ~/BLOG`) or modify the script to use a different path.
- **Placeholders**: Files like `fetch_espn.py`, `predict_model.py`, and `approval.teal` contain minimal placeholders to establish the structure. They’ll need implementation based on your requirements (e.g., odds parsing, ML models).
- **Diagram Model**: The `docs/architecture.mmd` includes a basic Mermaid diagram. If you upload your new diagram model, I can update it to reflect the exact data flow.
- **Dependencies**: Each component’s `requirements.txt` or `package.json` includes minimal dependencies. Add more as needed (e.g., `pybaseball` for `data_pipeline/`).
- **Security**: Update `.env` files with real tokens/keys and never commit them to Git.

Let me know if you want to:
- Implement specific files (e.g., `fetch_espn.py`, `popup.js`).
- Focus on a component (e.g., Chrome extension, Discord bot).
- Incorporate the new diagram model (please upload or describe it).
- Run initial tests or set up the Discord server.

This script sets up the full structure, ready for development!