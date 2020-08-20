# -*- coding: utf-8 -*-

from json import load

from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

from Settings import *

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

# CYCLE
Cycle = ReplyKeyboardMarkup([
    [statements['first_cycle'], statements['long_cycle']],
    [statements['abort']['abort']]
], resize_keyboard=True)

# FIRST CYCLE
FirstCycleButtons = list()
for i_course,j_course in zip(statements['courses']['first_cycle'][0::2], statements['courses']['first_cycle'][1::2]):
    FirstCycleButtons.append([i_course,j_course])
FirstCycleButtons.append([statements['long_cycle']])
FirstCycleButtons.append([statements['abort']['abort']])
FirstCycle = ReplyKeyboardMarkup(FirstCycleButtons, resize_keyboard=True)

# LONG CYCLE
LongCycleButtons = list()
for i_course,j_course in zip(statements['courses']['long_cycle'][0::2], statements['courses']['long_cycle'][1::2]):
    LongCycleButtons.append([i_course,j_course])
LongCycleButtons.append([statements['first_cycle']])
LongCycleButtons.append([statements['abort']['abort']])
LongCycle = ReplyKeyboardMarkup(LongCycleButtons, resize_keyboard=True)

# NAVIGATION
PrevButton   = InlineKeyboardButton(statements['navigation']['previous'], callback_data="prev")
NextButton   = InlineKeyboardButton(statements['navigation']['next'], callback_data="next")
DeleteButton = InlineKeyboardButton(statements['navigation']['delete'], callback_data="delete")
ChatButton   = InlineKeyboardButton(statements['navigation']['chat'], callback_data="chat")
YesButton    = InlineKeyboardButton(statements['navigation']['yes'], callback_data="yes")
NoButton     = InlineKeyboardButton(statements['navigation']['no'], callback_data="no")

Navigation = InlineKeyboardMarkup([[PrevButton,NextButton]])
NavigationDelete = InlineKeyboardMarkup([[PrevButton,NextButton],[DeleteButton]])
NavigationChat = InlineKeyboardMarkup([[PrevButton,NextButton],[ChatButton]])
OnlyDelete = InlineKeyboardMarkup([[DeleteButton]])
OnlyChat = InlineKeyboardMarkup([[ChatButton]])
Confirm = InlineKeyboardMarkup([[YesButton, NoButton]])
