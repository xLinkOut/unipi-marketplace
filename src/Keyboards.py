# -*- coding: utf-8 -*-

from Settings import *
from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton

# START
Start = ReplyKeyboardMarkup([
    [statements['keyboards']['start']['sell'], statements['keyboards']['start']['buy']],
    [statements['keyboards']['start']['info']]
], resize_keyboard=True)

# SELL
Sell = ReplyKeyboardMarkup([
    [statements['keyboards']['sell']['new_item']],
    [statements['keyboards']['sell']['my_items']],
    [statements['keyboards']['misc']['back'], statements['keyboards']['misc']['instructions']]
], resize_keyboard=True)

# BUY
Buy = ReplyKeyboardMarkup([
    [statements['keyboards']['buy']['search_by_name']],
    [statements['keyboards']['buy']['search_by_course']],
    [statements['keyboards']['buy']['last_added']],
    [statements['keyboards']['misc']['back'], statements['keyboards']['misc']['instructions']]
], resize_keyboard=True)

# UNDO
Undo = ReplyKeyboardMarkup([
    [statements['keyboards']['misc']['abort']]
], resize_keyboard=True)

# SKIP
Skip = ReplyKeyboardMarkup([
    [statements['keyboards']['misc']['skip']],
    [statements['keyboards']['misc']['abort']]
], resize_keyboard=True)

# PRICE
Price = ReplyKeyboardMarkup([
    ["5,00€", "8,00€"],
    ["10,00€", "12,00€"],
    ["15,00€", "20,00€"],
    [statements['keyboards']['misc']['abort']]
], resize_keyboard=True)

# CYCLE
Cycle = ReplyKeyboardMarkup([
    [statements['keyboards']['courses']['first_cycle'], statements['keyboards']['courses']['long_cycle']],
    [statements['keyboards']['misc']['abort']]
], resize_keyboard=True)

# FIRST CYCLE
FirstCycleButtons = list()
for i_course,j_course in zip(statements['keyboards']['courses']['first_cycle_list'][0::2], statements['keyboards']['courses']['first_cycle_list'][1::2]):
    FirstCycleButtons.append([i_course,j_course])
FirstCycleButtons.append([statements['keyboards']['courses']['long_cycle']])
FirstCycleButtons.append([statements['keyboards']['misc']['abort']])
FirstCycle = ReplyKeyboardMarkup(FirstCycleButtons, resize_keyboard=True)

# LONG CYCLE
LongCycleButtons = list()
for i_course,j_course in zip(statements['keyboards']['courses']['long_cycle_list'][0::2], statements['keyboards']['courses']['long_cycle_list'][1::2]):
    LongCycleButtons.append([i_course,j_course])
LongCycleButtons.append([statements['keyboards']['courses']['first_cycle']])
LongCycleButtons.append([statements['keyboards']['misc']['abort']])
LongCycle = ReplyKeyboardMarkup(LongCycleButtons, resize_keyboard=True)

# NAVIGATION
PrevButton   = InlineKeyboardButton(statements['keyboards']['navigation']['previous'], callback_data="prev")
NextButton   = InlineKeyboardButton(statements['keyboards']['navigation']['next'], callback_data="next")
DeleteButton = InlineKeyboardButton(statements['keyboards']['navigation']['delete'], callback_data="delete")
ChatButton   = InlineKeyboardButton(statements['keyboards']['navigation']['chat'], callback_data="chat")
YesButton    = InlineKeyboardButton(statements['keyboards']['navigation']['yes'], callback_data="yes")
NoButton     = InlineKeyboardButton(statements['keyboards']['navigation']['no'], callback_data="no")

Navigation = InlineKeyboardMarkup([[PrevButton,NextButton]])
NavigationDelete = InlineKeyboardMarkup([[PrevButton,NextButton],[DeleteButton]])
NavigationChat = InlineKeyboardMarkup([[PrevButton,NextButton],[ChatButton]])
OnlyDelete = InlineKeyboardMarkup([[DeleteButton]])
OnlyChat = InlineKeyboardMarkup([[ChatButton]])
Confirm = InlineKeyboardMarkup([[YesButton, NoButton]])
