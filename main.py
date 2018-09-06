#!/usr/bin/python3
# -*- coding: utf-8 -*-
import re
import RU
import adm
import tools
from data import addlot_e, addtrade_e
from sqlite3 import Error
from data.SQLite import SQLite
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler


db = SQLite()



CANCEL,SET=range(2)

idlot = 0


def start(bot, update):
    user = update.message.from_user
    db = SQLite()
    try:
        db.magic(
            sql='insert or ignore into Memb (tgID, fname, uname) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return  tools.log('User "%s", error "%s"' % (user.id, Error))
    markup = [[InlineKeyboardButton(RU.new, callback_data='refr'),]]
    update.message.reply_text(RU.welcome1.format(user.first_name), reply_markup=InlineKeyboardMarkup(markup))

def button(bot, update):
    db = SQLite()
    query = update.callback_query
    user = query.from_user
    a = db.magic('select lotID from Trades ').fetchall()
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if query.data == 'refr':
        if len(a) != 0:
            keyboard = []
            for i in a:
                keyboard.append([InlineKeyboardButton(i[1], callback_data=i[0])])
            keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
            bot.edit_message_text(text=RU.tradelist,
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            keyboard = [[InlineKeyboardButton('Назад', callback_data='back')]]
            bot.edit_message_text(text=RU.empty,
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    elif query.data == 'back':
        markup = [[InlineKeyboardButton(RU.new, callback_data='refr'), ]]
        bot.edit_message_text(text=RU.welcome1.format(query.from_user.first_name),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(markup))
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    ids = []
    for i in a:
        ids.append(i[0])







def main():
    updater = Updater(RU.token)
    updater.dispatcher.add_handler(addlot_e.addlot())
    updater.dispatcher.add_handler(addtrade_e.addtrade())
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(adm.error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()