#!/bin/bash

mkdir -p blockchain/smart_contracts

touch blockchain/__init__.py
touch blockchain/config.py
touch blockchain/create_wallet.py
touch blockchain/check_balance.py
touch blockchain/send_token.py
touch blockchain/utils.py

touch blockchain/smart_contracts/__init__.py
touch blockchain/smart_contracts/compile_contract.py
touch blockchain/smart_contracts/deploy_contract.py
touch blockchain/smart_contracts/interaction.py

echo "✅ blockchain/ structure created!"