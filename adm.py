import RU
import tools
from SQLite import SQLite
from sqlite3 import Error
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

CHECK,NAME,DESCR,PRICE,MAX,RATE,PICTS,END=range(8)
picsID = ''

def addlot():
    return ConversationHandler(
        entry_points=[CommandHandler('addlot',       al1)], # TODO Filters.user()
        states={
            NAME:   [MessageHandler(Filters.text,  name) ],  # TODO Filters.user()
            DESCR:  [MessageHandler(Filters.text,  descr)],
            PRICE:  [MessageHandler(Filters.text,  price)],
            MAX:    [MessageHandler(Filters.text,  maxp) ],
            RATE:   [MessageHandler(Filters.text,  rate) ],
            PICTS:  [MessageHandler(Filters.photo, pics) ]
        },
        fallbacks=[CommandHandler('end', end)]
    )


def bttn(bot, update):
    db = SQLite()
    query = update.callback_query
    id = query.data[1:]
    lot = db.magic('select * from lot where id = {}'.format(id)).fetchall()[0]


def al1(bot, update):
    global idlot
    db = SQLite()
    idlot = tools.timestamp()
    db.magic('insert into lot(id) values (?)', (idlot,))
    update.message.reply_text(RU.aname)
    return NAME


def name(bot, update):
    db = SQLite()
    global idlot
    update.message.reply_text(RU.description)
    name = update.message.text
    db.magic('update lot set head = (?) where id = {}'.format(idlot), (name,))
    tools.log('Created lot {} with name {}'.format(idlot, name))
    return DESCR


def descr(bot, update):
    db = SQLite()
    global idlot
    update.message.reply_text(RU.price)
    descr = update.message.text
    db.magic('update lot set description = (?) where id = {}'.format(idlot), (descr,))
    tools.log('Lot {} description updated'.format(idlot))
    return PRICE


def price(bot, update):
    db = SQLite()
    global idlot
    update.message.reply_text(RU.maxprace)
    try: price = float(update.message.text)
    except ValueError: return update.message.reply_text(RU.pricewrong)
    db.magic('update lot set sPrice = (?), price = (?) where id = {}'.format(idlot), (price,price))
    tools.log('Lot {} price updated'.format(idlot))
    return MAX

def maxp(bot, update):
    db = SQLite()
    global idlot
    update.message.reply_text(RU.rate)
    try: price = float(update.message.text)
    except ValueError: return update.message.reply_text(RU.pricewrong)
    db.magic('update lot set maxPrice = (?) where id = {}'.format(idlot), (price,))
    tools.log('Lot {} rate updated'.format(idlot))
    return RATE


def rate(bot, update):
    db = SQLite()
    global idlot
    update.message.reply_text(RU.pics)
    try: price = float(update.message.text)
    except ValueError: return update.message.reply_text(RU.pricewrong)
    db.magic('update lot set rate = (?) where id = {}'.format(idlot), (price,))
    tools.log('Lot {} rate updated'.format(idlot))
    return PICTS



def pics(bot, update):
    db = SQLite()
    global idlot
    text = update.message.photo[4].file_id
    try: picsID = db.magic('select pictures from lot where id = (?)', (idlot,)).fetchall()[0][0]  #TODO is null
    except Error: pass
    if picsID is None:
        picsID = text
    else:
        picsID = str(picsID)+' '+text
    db.magic('update lot set pictures = (?) where id = {}'.format(idlot), (picsID,))


def end(bot,update):
    update.message.reply_text(RU.end)
    return ConversationHandler.END