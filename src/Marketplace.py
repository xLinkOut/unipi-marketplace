# -*- coding: utf-8 -*-

import logging

# Modules
import Buy
import Menu
import Sell
import Feedback
import Keyboards
import Navigation

# Test
from time import time, sleep
from Database import session, User, Item

# Telegram Bot
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler

from Settings import *
        
if __name__ == "__main__":

    # UPDATER, DISPATCHER, LOGGING AND LANGUAGE
    updater = Updater(token=API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        level=logging.DEBUG if DEBUG else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # HANDLERS
    start_handler = CommandHandler('start', Menu.start)
   
    feedback_handler = ConversationHandler(
        entry_points = [CommandHandler('feedback', Feedback.feedback)],
        states = {
            "DONE": [MessageHandler(Filters.text, Feedback.feedback_done)],
            "ANSWER": [MessageHandler(Filters.text, Feedback.feedback_answer)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['abort']}$"), Feedback.feedback_undo)]
    )
    #feedback_answer_handler = CommandHandler

    sell_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['sell']}$"), Sell.sell)
    buy_handler   = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['buy']}$"), Buy.buy)
    info_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['start']['info']}$"), Menu.information)
    back_handler  = MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['back']}$"), Menu.back)
    instruction_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['instructions']}$"), Menu.instructions)

    sell_new_item_handler = ConversationHandler(
        entry_points = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['new_item']}$"), Sell.new_item)],
        states = {
            "TITLE":  [MessageHandler(Filters.text, Sell.title)],
            "PRICE":  [MessageHandler(Filters.text, Sell.price)],
            "PHOTO":  [MessageHandler(Filters.photo, Sell.photo),
                       MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['skip']}$"), Sell.photo)],
            "CYCLE":  [MessageHandler(Filters.text, Sell.cycle)],
            "COURSE": [MessageHandler(Filters.text, Sell.course)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['abort']}$"), Sell.undo), CommandHandler('cancel', Sell.undo)]
    )

    sell_my_items_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['sell']['my_items']}$"), Sell.my_items)
    
    buy_search_by_name_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_name']}$"), Buy.search_by_name)],
        states = {
            "DONE" : [MessageHandler(Filters.text, Buy.search_by_name_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['abort']}$"),Buy.search_by_name_undo), CommandHandler('cancel',Buy.search_by_name_undo)]
    )
    
    buy_search_by_course_handler = ConversationHandler(
        entry_points =[MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['search_by_course']}$"), Buy.search_by_course)],
        states = {
            "CYCLE" : [MessageHandler(Filters.text, Buy.search_by_course_cycle)],
            "DONE" : [MessageHandler(Filters.text, Buy.search_by_course_done)]
        },
        fallbacks = [MessageHandler(Filters.regex(rf"^{statements['keyboards']['misc']['abort']}$"), Buy.search_by_course_undo), CommandHandler('cancel',Buy.search_by_course_undo)]
    )

    buy_last_added_handler = MessageHandler(Filters.regex(rf"^{statements['keyboards']['buy']['last_added']}$"), Buy.last_added)

    buy_chat_handler = CallbackQueryHandler(Buy.chat,pattern=r"^chat$")

    # Navigation    
    navigation_prev_handler = CallbackQueryHandler(Navigation.prev,pattern=r"^prev$")
    navigation_next_handler = CallbackQueryHandler(Navigation.next,pattern=r"^next$")
    navigation_delete_handler = CallbackQueryHandler(Navigation.delete,pattern=r"^delete$")
    navigation_yes_handler = CallbackQueryHandler(Navigation.yes,pattern=r"yes")
    navigation_no_handler  = CallbackQueryHandler(Navigation.no,pattern=r"no")

    # TEST AREA
    def add_test(update, context):
        try:            
            #session.query(Item).delete()
            session.add(Item(chat_id=123456781,title="Primo libro",photo='0',price='5.00',course="Agraria",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456782,title="Secondo libro",photo='0',price='8.00',course="Biologia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456783,title="Terza dispensa",photo='0',price='10.00',course="Farmacia",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=ADMIN_CHAT_ID,title="Quarto libro",photo='0',price='12.00',course="Matematica",timestamp=int(time()),visible=True))
            sleep(1)
            session.add(Item(chat_id=123456785,title="Quinta dispensa",photo='0',price='15.00',course="Psicologia",timestamp=int(time()),visible=True))
            session.commit()
            context.bot.send_message(chat_id=update.message.chat_id,text="Ho aggiunti gli item al db!")
        except Exception as e:
            context.bot.send_message(chat_id=update.message.chat_id,text=f"Errore: {e}")
    def set_section(update, context):
        context.user_data['section'] = "sell"
    add_test_handler = CommandHandler('add', add_test)
    set_section_handler = CommandHandler('section', set_section)
    dispatcher.add_handler(add_test_handler)
    dispatcher.add_handler(set_section_handler)
    # END TEST AREA

    # DISPATCHER
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(sell_handler)
    dispatcher.add_handler(buy_handler)
    dispatcher.add_handler(info_handler)
    dispatcher.add_handler(back_handler)
    dispatcher.add_handler(instruction_handler)
    dispatcher.add_handler(sell_new_item_handler)
    dispatcher.add_handler(sell_my_items_handler)
    dispatcher.add_handler(feedback_handler)
    dispatcher.add_handler(buy_last_added_handler)
    dispatcher.add_handler(buy_search_by_name_handler)
    dispatcher.add_handler(buy_search_by_course_handler)
    dispatcher.add_handler(buy_chat_handler)
    dispatcher.add_handler(navigation_prev_handler)
    dispatcher.add_handler(navigation_next_handler)
    dispatcher.add_handler(navigation_delete_handler)
    dispatcher.add_handler(navigation_yes_handler)
    dispatcher.add_handler(navigation_no_handler)

    # POLLING
    updater.start_polling()
    updater.idle()
    updater.stop()