# -*- coding: utf-8 -*-
import re
import RU
import adm
import time
import tools
import logging
import calendar
import requests
import threading
from sqlite3 import Error
from SQLite import SQLite
from datetime import datetime
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
            sql='insert or ignore into membs (tgID, uName, fName) VALUES (?,?,?)',
            data=(user.id, user.name, user.first_name))
    except Error:
        return  tools.log('User "%s", error "%s"' % (user.id, error))
    markup = [[InlineKeyboardButton("Refresh", callback_data='refr'),]]
    update.message.reply_text(RU.welcome1.format(user.first_name), reply_markup=InlineKeyboardMarkup(markup))

def button(bot, update):
    db = SQLite()
    query = update.callback_query
    a = db.magic('select id, head from lot where buyer isnull').fetchall()
    ids = []
    for i in a:
        ids.append(i[0])
    if query.data == 'refr':
        if a is not None:
            keyboard = []
            for i in a:
                keyboard.append([InlineKeyboardButton(i[1], callback_data=i[0])])
            keyboard.append([InlineKeyboardButton('Back',callback_data='back')])
            bot.edit_message_text(text="text",
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            keyboard = [[InlineKeyboardButton('Back', callback_data='back')]]
            bot.edit_message_text(text=RU.empty,
                                  chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data == 'back':
        markup = [[InlineKeyboardButton("Refresh", callback_data='refr'), ]]
        bot.edit_message_text(text=RU.welcome1.format(query.from_user.first_name),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(markup))
    elif re.match('add1 ', query.data):
        lot = query.data[5:]
        lotData = db.magic('select * from lot where id = (?)', (lot,)).fetchall()[0]
        try: maxprice = float(db.magic('select max(price) from room where lotID = (?)', (lot,)).fetchall()[0][0])
        except: maxprice = lotData[4]
        maxprice += lotData[5]
        db.magic('replace into room(lotID, memberID, price) values (?,?,?)', (lot, query.from_user.id, maxprice))
        markup = [[
            InlineKeyboardButton("+{}".format(lotData[5]), callback_data='add1 {}'.format(lot)),
            InlineKeyboardButton("+{}".format(lotData[5]*10), callback_data='add10 {}'.format(lot)),
            InlineKeyboardButton("Set Price", callback_data='Set {}'.format(lot))]]
        bot.edit_message_text(text=RU.lot.format(lotData[1], maxprice),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(markup))

    elif re.match('add10', query.data):
        lot = query.data[6:]
        lotData = db.magic('select * from lot where id = (?)', (lot,)).fetchall()[0]
        try: maxprice = float(db.magic('select max(price) from room where lotID = (?)', (lot,)).fetchall()[0][0])
        except: maxprice = lotData[4]
        maxprice += lotData[5]*10
        db.magic('replace into room(lotID, memberID, price) values (?,?,?)', (lot, query.from_user.id, maxprice))
        markup = [[
            InlineKeyboardButton("+{}".format(lotData[5]), callback_data='add1 {}'.format(lot)),
            InlineKeyboardButton("+{}".format(lotData[5]*10), callback_data='add10 {}'.format(lot)),
            InlineKeyboardButton("Set Price", callback_data='Set {}'.format(lot))]]
        bot.edit_message_text(text=RU.lot.format(lotData[1], maxprice),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(markup))


    elif re.match('Set', query.data):
        lot = query.data[4:]

    elif int(query.data) in ids:
        d = datetime.utcnow()
        stamp = calendar.timegm(d.utctimetuple())
        lot = db.magic('select * from lot where id = (?)', (query.data,)).fetchall()[0]
        try:
            lotPrice = db.magic('select max(price) from room where lotID = {}'.format(lot,)).fetchall()
            lotPrice = float(lotPrice[0][0])
        except: lotPrice = lot[4]
        data = [stamp, query.data, query.from_user.id, lotPrice]                                #TODO change price to actual
        db.magic('insert into room(id, lotID, memberID, price) values (?,?,?,?)', (data,))
        markup = [[
            InlineKeyboardButton("+1", callback_data='add1 {}'.format(query.data)),
            InlineKeyboardButton("+10", callback_data='add10 {}'.format(query.data)),
            InlineKeyboardButton("Set Price", callback_data='Set {}'.format(query.data))]]
        bot.edit_message_text(text=RU.lot.format(lot[1], lot[4]),
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id,
                              reply_markup=InlineKeyboardMarkup(markup))


def setprice(bot, update):
    update.message.reply_text(RU.setyourprice)
    return SET

def upPrice(bot, update):
    user = update.message.from_user
    db = SQLite()


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    tools.log('Update {} caused error {}'.format(update, error), False)


def main():
    updater = Updater(RU.token)

    addlot_handler = adm.addlot()
    setPrice_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(pattern='Set', callback=setprice)],
        states={
            SET: [MessageHandler(Filters.text, upPrice)]
        },
        fallbacks=[CommandHandler('end', adm.end)]
    )
    updater.dispatcher.add_handler(addlot_handler)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(setPrice_handler)
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()