# -*- coding: utf-8 -*-

from os import getenv
from dotenv import load_dotenv
from telegram.ext import ConversationHandler
import json
import Database

load_dotenv()
LANG_FILE = getenv("LANG_FILE") # [IT, EN, ES, DE]
ADMIN_CHAT_ID = int(getenv("ADMIN_CHAT_ID"))

with open(f"lang/{LANG_FILE}.lang", 'r') as lang_f:
    statements = json.load(lang_f)

# FEEDBACK
def feedback(update, context):
    if int(update.message.chat_id) == ADMIN_CHAT_ID:
        # Answer
        user_chatid = update.message.text[10:]
        if not user_chatid:
            context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=statements['feedback_wrong_id'],
                parse_mode='markdown')
            return ConversationHandler.END
        elif not Database.get_user_by_chat_id(user_chatid):
            context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=statements['feedback_missing_user'],
                parse_mode='markdown')
            return ConversationHandler.END
        else:
            context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=statements['feedback_send_response'],
                parse_mode='markdown')
            context.user_data['feedback_id'] = int(user_chatid)
            return "ANSWER"
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements['feedback'],
            reply_markup=Keyboards.Undo,
            parse_mode="Markdown")
        return "DONE"

def feedback_done(update, context):
    if update.message.text == statements['keyboards']['abort']['abort']:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=statements["feedback_undo"],
            reply_markup=Keyboards.Start,
            parse_mode="markdown")
        return ConversationHandler.END

    username = f"@{update.message.chat.username}" if update.message.chat.username else choice(["🤷‍♀️","🤷‍♂️"])
    context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=statements['feedback_received'] \
            .replace('$$',str(update.message.chat_id),1) \
            .replace('$$',username, 1) \
            .replace('$$',update.message.chat.first_name, 1),
        parse_mode="markdown"
    )

    context.bot.forward_message(
        chat_id=ADMIN_CHAT_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['feedback_done'],
        reply_markup=Keyboards.Start,
        parse_mode="Markdown")
    return ConversationHandler.END

# Replace this mechanism when (and if) python-telegram-bot accepts my "reply-pattern" pr
def feedback_answer(update, context):
    if int(update.message.chat_id) == ADMIN_CHAT_ID:
        context.bot.send_message(
            chat_id=context.user_data['feedback_id'],
            text=statements['feedback_response']\
                .replace('$$',Database.get_user_by_chat_id(context.user_data['feedback_id']).first_name,1)\
                .replace('$$',update.message.text,1),
            parse_mode='markdown')
        
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=statements['feedback_response_sent'],
            parse_mode='markdown')

        context.user_data['feedback_id'] = None
        return ConversationHandler.END

def feedback_undo(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=statements['feedback_undo'],
        reply_markup=Keyboards.Start,
        parse_mode="Markdown")
