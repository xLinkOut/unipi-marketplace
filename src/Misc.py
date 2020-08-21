# -*- coding: utf-8 -*-
from functools import wraps
from telegram import ChatAction
from Settings import LANG_FILE
import json
from datetime import datetime

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

# CHAT ACTION
def typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return command_func

def photo_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.UPLOAD_PHOTO)
        return func(update, context,  *args, **kwargs)
    return command_func

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

# BUILD ITEM CAPTION
def build_item_caption(item,page=[]):
    fromts = datetime.fromtimestamp(item.timestamp)
    date = "{0}/{1}/{2}".format('%02d' % fromts.day, '%02d' % fromts.month, fromts.year)
    caption = f"*{statements['caption']['title']}:* {item.title}\n" \
            f"*{statements['caption']['price']}:* {item.price}€\n" \
            f"*{statements['caption']['course']}:* {item.course}\n" \
            f"*{statements['caption']['posted']}:* {date}"
    if page:
        return f"*{statements['caption']['page']}:* {page[0]}/{page[1]}\n{caption}"
    else: 
        return caption
