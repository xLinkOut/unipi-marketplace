# -*- coding: utf-8 -*-

from os import getenv
from json import load
from dotenv import load_dotenv

from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

load_dotenv()

LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE]
with open(f"lang/{LANG_FILE}.lang", 'r') as lang_file:
    statements = load(lang_file)['keyboards']

# START
Start = ReplyKeyboardMarkup([
    [statements['start']['sell'], statements['start']['buy']],
    [statements['start']['info']]
], resize_keyboard=True)

# SELL
Sell = ReplyKeyboardMarkup([
    [statements['sell']['new_item']],
    [statements['sell']['my_items']],
    [statements['sell']['back'], statements['sell']['instructions']]
], resize_keyboard=True)

# BUY
Buy = ReplyKeyboardMarkup([
    [statements['buy']['search_by_name']],
    [statements['buy']['search_by_course']],
    [statements['buy']['last_added']],
    [statements['buy']['back'], statements['buy']['instructions']]
], resize_keyboard=True)

# UNDO
Undo = ReplyKeyboardMarkup([
    [statements['abort']['abort']]
], resize_keyboard=True)

# SKIP
Skip = ReplyKeyboardMarkup([
    [statements['skip']['skip']],
    [statements['abort']['abort']]
], resize_keyboard=True)

# PRICE
Price = ReplyKeyboardMarkup([
    ["5,00€", "8,00€"],
    ["10,00€", "12,00€"],
    ["15,00€", "20,00€"],
    [statements['abort']['abort']]
], resize_keyboard=True)

# COURSES
Buttons = list()
for i_course,j_course in zip(statements['courses'][0::2], statements['courses'][1::2]):
    Buttons.append([i_course,j_course])
Buttons.append([statements['abort']['abort']])

Courses = ReplyKeyboardMarkup(Buttons, resize_keyboard=True)

# MY ITEMS
def build_my_items_keyboard(item_id,navigation=True):
    if navigation:    
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(statements['my_items']['previous'],callback_data=f"prev_{item_id}"),
            InlineKeyboardButton(statements['my_items']['next'],callback_data=f"next_{item_id}")],
            [InlineKeyboardButton(statements['my_items']['delete'],callback_data=f"delete_{item_id}")]
        ])
    else:
       return InlineKeyboardMarkup([
            [InlineKeyboardButton(statements['my_items']['delete'],callback_data=f"delete_{item_id}")]
        ]) 

# ITEM IN DB

SearchNavigation = InlineKeyboardMarkup([
    [InlineKeyboardButton(statements['search_items']['previous'],callback_data=f"s_prev"),
     InlineKeyboardButton(statements['search_items']['next'],callback_data=f"s_next")]
])

"""
def build_items_keyboard(prev_id,item_id,next_id): # Maybe useless prev/next? 
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(statements['search_items']['previous'],callback_data=f"s_prev_{item_id}"),
         InlineKeyboardButton(statements['search_items']['next'],callback_data=f"s_next_{item_id}")]
    ])
"""

# LAST ADDED
# TODO