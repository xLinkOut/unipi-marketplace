# -*- coding: utf-8 -*-

import Keyboards
import Database

from Settings import *
from Misc import build_item_caption
from telegram import InputMediaPhoto

def prev(update, context):
    if context.user_data['last_count'] == 0:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_prev_items'],cache_time=5)
    else:
        context.user_data['last_count'] -= 1
        prev_item  = context.user_data['last_items'][context.user_data['last_count']]

        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['previous'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item,[context.user_data['last_count']+1, context.user_data['items_count']]),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)

def next(update, context):
    if context.user_data['last_count'] == context.user_data['items_count']-1:
        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['no_next_items'],cache_time=5)
    else:
        context.user_data['last_count'] += 1
        next_item = context.user_data['last_items'][context.user_data['last_count']]

        context.bot.answer_callback_query(
            update.callback_query.id,
            text=statements['callback_answers']['next'])
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=next_item.photo if not next_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(next_item,[context.user_data['last_count']+1,context.user_data['items_count']]),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['section'] == "sell" else Keyboards.NavigationChat)


def delete(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=Keyboards.Confirm
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=statements['callback_answers']['are_you_sure'],
        cache_time=0)

def yes(update, context):
    # BUG: last_count index error when deleting last item of my items menu
    item = context.user_data['last_items'][context.user_data['last_count']]
    db_item = Database.get_item_by_id(item.item_id)
    Database.session.delete(item)
    Database.session.commit()
    context.user_data['last_items'].remove(item)
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=f"{item.title}  🚮",
        cache_time=5)

    if len(context.user_data['last_items']) <= 0:
        context.user_data['last_items'] = None
        context.user_data['last_count'] = None
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=statements['sell']['my_items']['deleted_last_item'],
            parse_mode="Markdown")
    else:
        context.user_data['last_count'] -= 1
        # Load prev item
        prev_item  = context.user_data['last_items'][context.user_data['last_count']]
        context.bot.edit_message_media(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            media=InputMediaPhoto(
                media=prev_item.photo if not prev_item.photo == '0' else IMG_NOT_AVAILABLE,
                caption=build_item_caption(prev_item),
                parse_mode="Markdown"),
            reply_markup=Keyboards.NavigationDelete if context.user_data['items_count'] > 1 else Keyboards.OnlyDelete)


def no(update, context):
    context.bot.edit_message_reply_markup(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id,
        reply_markup=Keyboards.NavigationDelete if context.user_data['items_count'] > 1 else Keyboards.OnlyDelete
    )
    context.bot.answer_callback_query(
        update.callback_query.id,
        text=statements['callback_answers']['as_you_want'],
        cache_time=0)
