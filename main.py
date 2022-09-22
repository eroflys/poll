# con = sqlite3.connect("allusers.sqlite")
# cur = con.cursor()
# cur.execute('''UPDATE ADM SET status = 1 WHERE id = (SELECT id FROM allusers where tlgrmid = ?) ''',
#                 (update.message.from_user.id,))
#     a1 = cur.execute('''SELECT answered from JU WHERE id = (SELECT id FROM allusers where tlgrmid = ?) ''',
#                 (update.message.from_user.id,)).fetchall()
# con.commit()
# con.close()



# markup1 = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
#     inlinekeyboard = [[InlineKeyboardButton('ВК', url = 'https://vk.com/wolrusteens')], [InlineKeyboardButton('Telegram', url = 'https://t.me/wolrusteenss')],
#                       [InlineKeyboardButton('Сайт', url = 'https://wolrus.org/event/teensconf')],
#                       [InlineKeyboardButton('Наши подкасты', url = 'https://podcast.ru/1579849079')]
#                       [InlineKeyboardButton('В начало', callback_data='В начало')]]
#     markup = InlineKeyboardMarkup(inlinekeyboard)

from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
import sqlite3
from datetime import *
import time as sleeptime

bot = Bot(token='5774853658:AAGFBSWMB1aDvun4bVdzn_xRxsrVXxM4MvY')
updater = Updater('5774853658:AAGFBSWMB1aDvun4bVdzn_xRxsrVXxM4MvY', use_context=True)

def start(update, context):
    con = sqlite3.connect("ListOfUsers.db")
    cur = con.cursor()
    ids = cur.execute('''SELECT telegram_id FROM Users ''').fetchall()
    if (update.message.from_user.id,) not in ids:
        update.message.reply_text('''Видимо ты новенький, попроси у администратора дать тебе доступ''')
    else:
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''', (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 1:
            inlinekeyboard = [
                [InlineKeyboardButton('Добавить пользователя', callback_data='ADM_add_user')],
                # [InlineKeyboardButton('Провести опрос', callback_data='ADM_take_poll')],
                [InlineKeyboardButton('Результаты опроса', callback_data='ADM_result')]]
            markup = InlineKeyboardMarkup(inlinekeyboard)
            update.message.reply_text('''Что ты хочешь?''', reply_markup=markup)
        elif int(j[0][0]) == 2:
            inlinekeyboard = [
                [InlineKeyboardButton('Назначить или отстранить админа', callback_data='SADM_set_admin')],
                [InlineKeyboardButton('Назначит супер админа', callback_data='SADM_set_superadmin')],
                [InlineKeyboardButton('Добавить служение', callback_data='SADM_set_activity')],
                [InlineKeyboardButton('Добавить пользователей', callback_data='ADM_add_user')],
                [InlineKeyboardButton('Изменить расписание', callback_data='SADM_change_timetable')],
                [InlineKeyboardButton('Результаты опроса', callback_data='ADM_result')]]
            markup = InlineKeyboardMarkup(inlinekeyboard)
            update.message.reply_text('''Чего желаешь, мастер?''', reply_markup=markup)
        else:
            inlinekeyboard = [
                [InlineKeyboardButton('Кто я?', callback_data='USR_who_am_I')]]
            markup = InlineKeyboardMarkup(inlinekeyboard)
            update.message.reply_text('Что хочешь узнать?', reply_markup=markup)
    con.commit()
    con.close()


def poll():
    global bot
    con = sqlite3.connect("ListOfUsers.db")
    cur = con.cursor()
    cur.execute('''UPDATE Activities SET num_now = 0''')
    cur.execute('''UPDATE Users SET Result = ?''', ('empty',))
    list_of_users = cur.execute('''SELECT telegram_id FROM Users ''').fetchall()
    con.commit()
    for i in list_of_users:
        list_of_activities = cur.execute('''SELECT name, Required, num_now FROM Activities''').fetchall()
        inlinekeyboard = []
        for j in list_of_activities:
            a = j[0] + '. Необходимо: ' + str(j[1])
            inlinekeyboard.append([InlineKeyboardButton(a, callback_data='poll_' + str(j[0]))])
        inlinekeyboard.append([InlineKeyboardButton('Меня не будет', callback_data='poll_' + 'не_буду')])
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(i[0], 'Выбери, где ты хочешь быть', reply_markup=markup)
    con.commit()
    con.close()


def inldatd(update, context):
    global bot
    if update.callback_query.data == 'SADM_set_admin':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите id человека в формате "tgid" + id, которого хотите назначить или отстранить администратором')

    elif update.callback_query.data == 'SADM_set_activity':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите название и необходимое количество человек в формате: "stact_" + имя + "_" + необходимое количество человек')

    elif update.callback_query.data == 'SADM_set_superadmin':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите id человека в формате "setSA_" + id, которого хотите назначить или отстранить суперадминистратором. Будьте внимательны, остранить супреадминистротора нельзя!')

    elif update.callback_query.data == 'ADM_result':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        resultpoll = cur.execute('SELECT status, result FROM Users').fetchall()
        timetable = cur.execute('SELECT * FROM Timetable').fetchall()
        res = ''
        for i in timetable:
            res = res + i[0] + '  ---  ' + i[1] + '  ---  ' + i[2] + '''

'''
        bot.sendMessage(update.callback_query.from_user.id, res)

    elif update.callback_query.data == 'ADM_add_user':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите данные человека, которого хотите добваить в формате: "addUSR_" + telegarm_id + "_" + имя + " " + фамилия')

    elif update.callback_query.data == 'ADM_change_timetable':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        curtt = cur.execute('SELECT * FROM Timetable').fetchall()
        for i in curtt:
            print(curtt[0] + ' --- ' + curtt[1])
        inlinekeyboard = [
            [InlineKeyboardButton('Изменить время для существующего порядка активностей', callback_data='SADM_cht')],
            [InlineKeyboardButton('Добавить новую активность в расписание', callback_data='SADM_ada')]]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Что вы хотите сделать?')

    elif update.callback_query.data[:5] == 'poll_':
        if update.callback_query.data[:5] != 'не_буду':
            con = sqlite3.connect("ListOfUsers.db")
            cur = con.cursor()
            num_now = cur.execute('''SELECT num_now FROM Activities WHERE name = ?''', (update.callback_query.data[5:],)).fetchall()
            recentpollres = cur.execute('''SELECT results FROM Timetable WHERE Name = ?''', (update.callback_query.data[5:],)).fetchall()
            nesname = cur.execute('''SELECT status FROM Users WHERE telegram_id = ?''', (update.callback_query.from_user.id,)).fetchall()
            print(num_now, update.callback_query.data[5:])
            cur.execute('''UPDATE Timetable SET result = ? WHERE name = ?''',
                        (recentpollres[0][0] + nesname[0][0], update.callback_query.data[5:]))
            cur.execute('''UPDATE Activities SET num_now = ? WHERE name = ?''', (str(int(num_now[0][0]) + 1), update.callback_query.data[5:]))
            cur.execute('''UPDATE Users SET result = ? WHERE telegram_id = ?''', (update.callback_query.data[5:], update.callback_query.from_user.id))
            con.commit()
            con.close()
        else:
            con = sqlite3.connect("ListOfUsers.db")
            cur = con.cursor()
            cur.execute('''UPDATE Users SET result = ? WHERE telegram_id = ?''',
                        (update.callback_query.data[5:], update.callback_query.from_user.id))
            con.commit()
            con.close()




def chlvl(update, context):
    if update['message']['text'][:4] == 'tgid':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            a1 = cur.execute('''SELECT IsItAdmin from Users WHERE telegram_id = ?''',
                             (update['message']['text'][4:],)).fetchall()
            if int(a1[0][0]) == 0:
                cur.execute('''UPDATE Users SET IsItAdmin = 1 WHERE id = ?''',
                            (update['message']['text'][4:],))
            else:
                cur.execute('''UPDATE Users SET IsItAdmin = 0 WHERE id = ?''',
                            (update['message']['text'][4:],))
            con.commit()
            con.close()
        else:
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:6] == 'stact_':
        temp_data = update['message']['text'].split('_')
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            a1 = cur.execute('''SELECT id FROM Activities''').fetchall()
            a1.sort(key=lambda x: x[0], reverse=True)
            id = int(a1[-1][0]) + 1
            cur.execute('''INSERT INTO Activities VALUES (?, ?, ?)''',
                        (id, temp_data[1], int(temp_data[2])))
            con.commit()
            con.close()
        else:
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:6] == 'setSA_':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            temp_data = update['message']['text'].split('_')
            a1 = cur.execute('''SELECT IsItAdmin from Users WHERE telegram_id = ?''',
                            (update['message']['text'][4:],)).fetchall()
            if int(a1[0][0]) == 0 or int(a1[0][0]) == 1:
                cur.execute('''UPDATE Users SET IsItAdmin = 2 WHERE id = ?''',
                            (temp_data[1],))
            con.commit()
            con.close()
        else:
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:7] == 'addUSR_':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2 or int(j[0][0]) == 1:
            temp_data = update['message']['text'].split('_')
            cur.execute('''INSERT INTO Users VALUES (?, 0, ?, ?)''',
                        (temp_data[1], temp_data[2], ' '))
            con.commit()
            con.close()
        else:
            con.commit()
            con.close()
            start(update, context)

    elif False:
        pass


    else:
        start(update, context)




def main():
    updater = Updater('5774853658:AAGFBSWMB1aDvun4bVdzn_xRxsrVXxM4MvY', use_context=True)

    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text, chlvl)
    dp.add_handler(CallbackQueryHandler(inldatd))

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(text_handler)
    updater.start_polling()
    poll()
    while True:
        if datetime.weekday(datetime.now()) == 4 and datetime.isoformat(datetime.combine(datetime.date(datetime.today()), time(hour=18, minute=30))) == datetime.isoformat(datetime.today())[:-7]:
            sleeptime.sleep(2)
            poll()


if __name__ == '__main__':
    main()
