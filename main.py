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
                [InlineKeyboardButton('Работа с пользователями', callback_data='ADM_work_users')],
                [InlineKeyboardButton('Результаты опроса', callback_data='ADM_result')]]
            markup = InlineKeyboardMarkup(inlinekeyboard)
            update.message.reply_text('''Что ты хочешь?''', reply_markup=markup)
        elif int(j[0][0]) == 2:
            inlinekeyboard = [
                [InlineKeyboardButton('Работа с пользователями', callback_data='SADM_work_users')],
                [InlineKeyboardButton('Структура мероприятия', callback_data='SADM_struc_evnt')],
                [InlineKeyboardButton('Результаты опроса', callback_data='ADM_result')]]
            markup = InlineKeyboardMarkup(inlinekeyboard)
            update.message.reply_text('''Чего желаешь, мастер?''', reply_markup=markup)
        else:
            inlinekeyboard = [
                [InlineKeyboardButton('Отключиться', callback_data='USR_turn_off')]]
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
    cur.execute('''UPDATE Timetable SET results = ?''', ('',))
    list_of_users = cur.execute('''SELECT telegram_id FROM Users ''').fetchall()
    con.commit()
    for i in list_of_users:
        list_of_activities = cur.execute('''SELECT name, Required, num_now FROM Activities''').fetchall()
        inlinekeyboard = []
        num_vis = cur.execute('''SELECT NumOfVisits FROM Users WHERE telegram_id = ?''', (i[0],)).fetchall()
        cur.execute('''UPDATE Users SET NumOfVisits = ? WHERE telegram_id = ?''', (num_vis[0][0][2:] + ' 0', i[0]))
        for j in list_of_activities:
            if int(j[1]) != -2:
                if int(j[1]) == -1:
                    a = j[0] + '. Необходимо: любое количество'
                else:
                    a = j[0] + '. Необходимо: ' + str(j[1])
                inlinekeyboard.append([InlineKeyboardButton(a, callback_data='poll_' + str(j[0]))])
        inlinekeyboard.append([InlineKeyboardButton('Меня не будет', callback_data='poll_' + 'не_буду')])
        markup = InlineKeyboardMarkup(inlinekeyboard)
        try:
            bot.sendMessage(i[0], 'Выбери, где ты хочешь быть', reply_markup=markup)
        except:
            cur.execute('''DELETE FROM Users WHERE telegram_id = ?''', (i[0],))
    con.commit()
    con.close()


def inldatd(update, context):
    global bot
    if update.callback_query.data == 'SADM_set_admin':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите id человека в формате "tgid" + id, которого хотите назначить или отстранить администратором')

    elif update.callback_query.data == 'ADM_work_users':
        inlinekeyboard = [[InlineKeyboardButton('Статистика пользователя', callback_data='ADM_stat_user')],
            [InlineKeyboardButton('Добавить/обновить пользователя', callback_data='ADM_add_user')]]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Выберите что хотите сделать', reply_markup=markup)

    elif update.callback_query.data == 'SADM_work_users':
        inlinekeyboard = [
            [InlineKeyboardButton('Добавить/обновить пользователя', callback_data='ADM_add_user')],
            [InlineKeyboardButton('Статистика пользователя', callback_data='ADM_stat_user')],
            [InlineKeyboardButton('Назначить или отстранить админа', callback_data='SADM_set_admin')],
            [InlineKeyboardButton('Назначить супер админа', callback_data='SADM_set_superadmin')]
        ]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Выберите что хотите сделать', reply_markup=markup)

    elif update.callback_query.data == 'ADM_stat_user':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_users = cur.execute('''SELECT telegram_id, Status FROM Users ''').fetchall()
        strOfUsers = ''
        for i in list_of_users:
            strOfUsers += str(i[1]) + ' <code>' + str(i[0]) + '''</code>
'''
        bot.sendMessage(update.callback_query.from_user.id, strOfUsers,  parse_mode="HTML")
        bot.sendMessage(update.callback_query.from_user.id, 'Введите команду в формате: "usrstas_" + telegramid искомого пользователя')

    elif update.callback_query.data == 'SADM_struc_evnt':
        inlinekeyboard = [
            [InlineKeyboardButton('Добавить/удалить активность', callback_data='SADM_add_activity')],
            [InlineKeyboardButton('Изменить количество человек в активности', callback_data='SADM_chng_activity')],
            [InlineKeyboardButton('Изменить чек-лист', callback_data='SADM_chng_chlst')]
        ]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Выберите что хотите сделать', reply_markup=markup)

    elif update.callback_query.data == 'SADM_chng_chlst':
        inlinekeyboard = [
            [InlineKeyboardButton('Добавить активность в чек-лист', callback_data='SADM_add_cl_activity')],
            [InlineKeyboardButton('Изменить время на активность в чек-листе', callback_data='SADM_chng_cl_activity')]
        ]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Выберите что хотите сделать', reply_markup=markup)

    elif update.callback_query.data == 'SADM_add_activity':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT name FROM Activities''').fetchall()
        stOfActs = ', '.join(map(lambda x: str(x[0]), list_of_acts))
        bot.sendMessage(update.callback_query.from_user.id, 'Текущие активности: ' + stOfActs)
        bot.sendMessage(update.callback_query.from_user.id, 'Введите название и необходимое количество человек (введите -1, если нужно как можно больше или -2, если необходимо для всех)  в формате: "addact_" + имя + "_" + необходимое количество человек (если нужно удалить можно написать любое количество необходимых человек)')

    elif update.callback_query.data == 'SADM_chng_activity':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите название и необходимое количество человек в формате: "chngact_" + имя + "_" + необходимое количество человек')

    elif update.callback_query.data == 'SADM_add_cl_activity':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT time, Name FROM Timetable''').fetchall()
        nloa = []
        for i in list_of_acts:
            ti = i[0].split(' - ')
            nloa.append([i[0], i[1], ti[1].split(':')])
        nloa.sort(key=lambda x: x[2][1])
        nloa.sort(key=lambda x: x[2][0])
        ress = ''
        for i in nloa:
            ress += i[0] + ' --- ' + i[1] + '''
'''
        bot.sendMessage(update.callback_query.from_user.id, ress)
        bot.sendMessage(update.callback_query.from_user.id, 'Введите id активности и время в которое она проходит (оно должно быть между двумя соседними активностями): "addclact_" + имя + "_" + время в формате: "чч:мм - чч:мм"')

    elif update.callback_query.data == 'SADM_chng_cl_activity':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT time, Name FROM Timetable''').fetchall()
        nloa = []
        for i in list_of_acts:
            ti = i[0].split(' - ')
            nloa.append([i[0], i[1], ti[1].split(':')])
        nloa.sort(key=lambda x: x[2][1])
        nloa.sort(key=lambda x: x[2][0])
        ress = ''
        for i in nloa:
            ress += i[0] + ' --- ' + i[1] + '''
        '''
        bot.sendMessage(update.callback_query.from_user.id, ress)
        bot.sendMessage(update.callback_query.from_user.id, 'Введите границу времени которую хотите изменить и её новое значение: "chngclact_" + граница + "_" + новая граница')

    elif update.callback_query.data == 'SADM_set_superadmin':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите id человека в формате "setSA_" + id, которого хотите назначить или отстранить суперадминистратором. Будьте внимательны, остранить супреадминистротора нельзя!')

    elif update.callback_query.data == 'ADM_result':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT time, Name, results FROM Timetable''').fetchall()
        nloa = []
        for i in list_of_acts:
            ti = i[0].split(' - ')
            nloa.append([i[0], i[1], ti[1].split(':'), i[2]])
        nloa.sort(key=lambda x: x[2][1])
        nloa.sort(key=lambda x: x[2][0])
        ress = ''
        for i in nloa:
            ress += i[0] + ' --- ' + i[1] + ' --- ' + str(i[-1]) + '''

'''
        bot.sendMessage(update.callback_query.from_user.id, ress)

    elif update.callback_query.data == 'ADM_add_user':
        bot.sendMessage(update.callback_query.from_user.id, 'Введите данные человека, которого хотите добваить (если хотите обновить введите id и новые данные) в формате: "addUSR_" + telegarm_id + "_" + имя + " " + фамилия')

    elif update.callback_query.data == 'USR_turn_off':
        inlinekeyboard = [
            [InlineKeyboardButton('Изменить время для существующего порядка активностей', callback_data='USR_yes')]]
        markup = InlineKeyboardMarkup(inlinekeyboard)
        bot.sendMessage(update.callback_query.from_user.id, 'Уверен что хочешь отключиться?', markup=markup)

    elif update.callback_query.data == 'USR_yes':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        cur.execute('DELETE FROM Users WHERE telegram_id = ?', (update.callback_query.from_user.id,))
        con.commit()
        con.close()

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
        bot.sendMessage(update.callback_query.from_user.id, 'Что вы хотите сделать?', markup=markup)

    elif update.callback_query.data[:5] == 'poll_':
        if update.callback_query.data[:5] != 'не_буду':
            con = sqlite3.connect("ListOfUsers.db")
            cur = con.cursor()
            num_vis = cur.execute('''SELECT NumOfVisits FROM Users WHERE telegram_id = ?''', (update.callback_query.from_user.id,)).fetchall()
            cur.execute('''UPDATE Users SET NumOfVisits = ? WHERE telegram_id = ?''', (num_vis[0][0][:5] + ' 1', update.callback_query.from_user.id))
            num_now = cur.execute('''SELECT num_now FROM Activities WHERE name = ?''', (update.callback_query.data[5:],)).fetchall()
            recentpollres = cur.execute('''SELECT results FROM Timetable WHERE Name = ?''', (update.callback_query.data[5:],)).fetchall()
            nesname = cur.execute('''SELECT status FROM Users WHERE telegram_id = ?''', (update.callback_query.from_user.id,)).fetchall()
            print(num_now, update.callback_query.data[5:])
            if recentpollres[0][0]:
                cur.execute('''UPDATE Timetable SET results = ? WHERE name = ?''',
                            (str(recentpollres[0][0]) + ' ' + str(nesname[0][0]), update.callback_query.data[5:]))
            else:
                cur.execute('''UPDATE Timetable SET results = ? WHERE name = ?''',
                            (str(nesname[0][0]), update.callback_query.data[5:]))
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
                cur.execute('''UPDATE Users SET IsItAdmin = 1 WHERE telegram_id = ?''',
                            (update['message']['text'][4:],))
            elif int(a1[0][0]) != 2:
                cur.execute('''UPDATE Users SET IsItAdmin = 0 WHERE telegram_id = ?''',
                            (update['message']['text'][4:],))
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
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
            update.message.reply_text('''Ошибка: недостаточно прав''')
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
                            (update['message']['text'][6:],)).fetchall()
            if int(a1[0][0]) == 0 or int(a1[0][0]) == 1:
                cur.execute('''UPDATE Users SET IsItAdmin = 2 WHERE telegram_id = ?''',
                            (temp_data[1],))
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:7] == 'addUSR_':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2 or int(j[0][0]) == 1:
            try:
                temp_data = update['message']['text'].split('_')
                cur.execute('''INSERT INTO Users VALUES (?, 0, ?, ?, "0 0 0 0")''',
                            (temp_data[1], temp_data[2] + ' ' + temp_data[3], 'empty'))
            except:
                temp_data = update['message']['text'].split('_')
                cur.execute('''UPDATE Users SET Status = ? WHERE telegram_id = ?''',
                            (temp_data[2] + ' ' + temp_data[3], temp_data[1]))
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:7] == 'usrstas':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2 or int(j[0][0]) == 1:
            temp_data = update['message']['text'].split('_')
            vis = cur.execute('''SELECT NumOfVisits FROM Users WHERE telegram_id = ?''', (temp_data[1],)).fetchall()
            if len(vis) == 0:
                update.message.reply_text('''Ошибка: пользователя с таким id - нет''')
            else:
                update.message.reply_text('Посещения за последние 4 недели:' + vis[0][0])
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:6] == 'addact':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            temp_data = update['message']['text'].split('_')
            lastID = cur.execute('''SELECT id FROM Activities''').fetchall()
            names = cur.execute('''SELECT name FROM Activities''').fetchall()
            names = list(map(lambda x: x[0], names))
            if temp_data[1] in names:
                cur.execute('''DELETE FROM Activities WHERE name = ?''', (temp_data[1],))
            else:
                cur.execute('''INSERT INTO Activities VALUES (?, ?, ?, 0)''',
                            (sorted(lastID, key=lambda x: x[0])[-1][0] + 1, temp_data[1], temp_data[2]))
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:9] == 'chngclact':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT time, Name FROM Timetable''').fetchall()
        nloa = []
        for i in list_of_acts:
            ti = i[0].split(' - ')
            nloa.append([i[0], i[1], ti[0].split(':'), ti[1].split(':')])
        nloa.sort(key=lambda x: x[2][1])
        nloa.sort(key=lambda x: x[2][0])
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            temp_data = update['message']['text'].split('_')
            ti = temp_data[2].split(':')
            resim = False
            for i in nloa:
                if temp_data[1].split(':') == i[3]:
                    resim = i
                    break
            if resim:
                if int(ti[0]) < int(nloa[nloa.index(resim) + 1][3][0]) or (int(ti[0]) == int(nloa[nloa.index(resim) + 1][3][0]) and int(ti[1]) < int(nloa[nloa.index(resim) + 1][3][1])):
                    cur.execute('''UPDATE Timetable SET time = ? WHERE Name = ?''', (':'.join(resim[2]) + ' - ' + temp_data[2], resim[1]))
                    cur.execute('''UPDATE Timetable SET time = ? WHERE Name = ?''',
                                (temp_data[2] + ' - ' + ':'.join(nloa[nloa.index(resim) + 1][3]), nloa[nloa.index(resim) + 1][1]))
                else:
                    update.message.reply_text('''Ошибка: некорректно введено новое время''')
            else:
                update.message.reply_text('''Ошибка: несуществующее время''')
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:8] == 'addclact':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        list_of_acts = cur.execute('''SELECT time, Name FROM Timetable''').fetchall()
        nloa = []
        for i in list_of_acts:
            ti = i[0].split(' - ')
            nloa.append([i[0], i[1], ti[1].split(':'), ti[0].split(':')])
        nloa.sort(key=lambda x: x[2][1])
        nloa.sort(key=lambda x: x[2][0])
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            temp_data = update['message']['text'].split('_')
            ti = temp_data[2].split(' - ')
            tif = ti[0].split(':')
            tis = ti[1].split(':')
            print(tif, tis)
            resim = False
            for i in nloa:
                if (int(tif[0]) == int(i[2][0]) and int(tif[1]) < int(i[2][1])) or (int(tif[0]) < int(i[2][0])):
                    resim = i
                    break
            print(nloa[nloa.index(resim) + 1], nloa[nloa.index(resim)], tif)
            if int(tis[0]) < int(nloa[nloa.index(resim) + 1][2][0]) or (int(tis[0]) == int(nloa[nloa.index(resim) + 1][2][0]) and int(tis[1]) < int(nloa[nloa.index(resim) + 1][2][1])):
                idOa = cur.execute('''SELECT id FROM Activities WHERE name = ?''',
                                (temp_data[1],)).fetchall()
                if len(idOa) == 0:
                    update.message.reply_text('''Ошибка: активности с таким именем несуществует''')
                else:
                    cur.execute('''UPDATE Timetable SET time = ? WHERE Name = ?''', (':'.join(resim[3]) + ' - ' + ':'.join(tif), resim[1]))
                    cur.execute('''UPDATE Timetable SET time = ? WHERE Name = ?''',
                                (':'.join(tis) + ' - ' + ':'.join(nloa[nloa.index(resim) + 1][2]), nloa[nloa.index(resim) + 1][1]))
                    cur.execute('''INSERT INTO Timetable VALUES (?, ?, ?, Null)''', (temp_data[2], temp_data[1], idOa[0][0]))
            else:
                update.message.reply_text('''Ошибка: некорректно введено время''')
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif update['message']['text'][:7] == 'chngact':
        con = sqlite3.connect("ListOfUsers.db")
        cur = con.cursor()
        j = cur.execute('''SELECT IsItAdmin FROM Users WHERE telegram_id = ?''',
                        (update.message.from_user.id,)).fetchall()
        if int(j[0][0]) == 2:
            temp_data = update['message']['text'].split('_')
            NesName = cur.execute('''SELECT id FROM Activities WHERE name = ?''', (temp_data[1],)).fetchall()
            if len(NesName) > 0:
                cur.execute('''UPDATE Activities SET Required = ? WHERE id = ?''',
                            (temp_data[2], NesName[0][0]))
            else:
                update.message.reply_text('''Ошибка: активности с таким названием несуществует''')
            con.commit()
            con.close()
        else:
            update.message.reply_text('''Ошибка: недостаточно прав''')
            con.commit()
            con.close()
            start(update, context)

    elif False:
        pass


    else:
        update.message.reply_text('''Ошибка: неизвестный текст. Либо вы ошиблись в команде, либо вам необходимо использовать команду /start''')




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
