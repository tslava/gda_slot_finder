import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID_CITIZENSHIP = int(os.environ['TELEGRAM_CHAT_ID_CITIZENSHIP'])
TELEGRAM_CHAT_ID_VNZ = int(os.environ['TELEGRAM_CHAT_ID_VNZ'])

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE_PATH = os.environ['GOOGLE_CREDENTIALS_FILE_PATH']
GOOGLE_TABLE_ID_CITIZENSHIP = os.environ['GOOGLE_TABLE_ID_CITIZENSHIP']
GOOGLE_TABLE_ID_VNZ = os.environ['GOOGLE_TABLE_ID_VNZ']

# API URLs - Citizenship service
CITIZENSHIP_DATES_URL = os.environ['CITIZENSHIP_DATES_URL']
CITIZENSHIP_TIMES_URL = os.environ['CITIZENSHIP_TIMES_URL']

# API URLs - VNZ service
VNZ_DATES_URL_BASE = os.environ['VNZ_DATES_URL_BASE']
VNZ_TIMES_URL_BASE = os.environ['VNZ_TIMES_URL_BASE']
