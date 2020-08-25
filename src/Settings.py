# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv
from json import load as json_load

# Load environment
load_dotenv()

# Environment variables
API_TOKEN = getenv("API_TOKEN")
DB_FILE = getenv("DB_FILE")
LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE ...]
IMG_NOT_AVAILABLE = getenv("IMG_NOT_AVAILABLE")
ADMIN_CHAT_ID = int(getenv("ADMIN_CHAT_ID"))
DEBUG = True if getenv("DEBUG") else False

# Checks
if not API_TOKEN: exit("Invalid token!")
if not DB_FILE: DB_FILE = "Database.db"
if not LANG_FILE: LANG_FILE = "IT"
if not IMG_NOT_AVAILABLE: print("Warning: missing IMG_NOT_AVAILABLE token! Sending messages that contain the placeholder 'photo not available' will not be sent and will generate an error.")
if not IMG_NOT_AVAILABLE: print("Warning: missing ADMIN_CHAT_ID! You will not be able to respond to user feedback.")
if DEBUG: 
    print(f"\nAPI_TOKEN: {API_TOKEN}\n" \
            f"DB_FILE: {DB_FILE}\n" \
            f"LANG_FILE: {LANG_FILE}\n" \
            f"IMG_NOT_AVAILABLE: {IMG_NOT_AVAILABLE}\n" \
            f"ADMIN_CHAT_ID: {ADMIN_CHAT_ID}\n" \
            f"DEBUG: {DEBUG}\n")

# Statements
with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json_load(lang_f)
