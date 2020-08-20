# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv

# Load environment
load_dotenv()

API_TOKEN = getenv("API_TOKEN")
DB_FILE = getenv("DB_FILE")
LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE ...]
IMG_NOT_AVAILABLE = getenv("IMG_NOT_AVAILABLE")
ADMIN_CHAT_ID = int(getenv("ADMIN_CHAT_ID"))
DEBUG = True if getenv("DEBUG") else False

if not API_TOKEN: exit("Invalid token!")
if not DB_FILE: DB_FILE = "Database.db"
if not LANG_FILE: LANG_FILE = "IT"
if not IMG_NOT_AVAILABLE: print("Warning: missing IMG_NOT_AVAILABLE token! Sending messages that contain the placeholder 'photo not available' will not be sent and will generate an error.")
if not IMG_NOT_AVAILABLE: print("Warning: missing ADMIN_CHAT_ID! You will not be able to respond to user feedback.")
if DEBUG: print(API_TOKEN,DB_FILE,LANG_FILE,IMG_NOT_AVAILABLE,ADMIN_CHAT_ID,DEBUG)