import time
import telebot
from telebot import types
from db import create_connection, create_table1, isuserintable, adduser, updateusersettings
from db import gettimewithoutsmoking, resetlastsmokedate, getuserdict
from datetime import datetime
from func import createmenukboard, getrecomendation
from threading import Thread

bot = telebot.TeleBot('Your token')  # Вставьте ваш токен сюда

connection1 = create_connection("nosmokers.sqlite")

create_table1(connection1)


@bot.message_handler(commands=["start"])
def start(m, res=False):
    check = isuserintable(connection1, m.from_user.id)

    if check:
        menukboard = createmenukboard(True)
        bot.send_message(m.chat.id, "Приветствую тебя", reply_markup=menukboard)
    else:
        menukboard = createmenukboard(False)
        bot.send_message(m.chat.id, "Приветствую тебя. Я бот для бросания курить."
                                    " Я буду твоим ассистентом в этом нелёгком деле. "
                                    "Давай для начала произведём простую настройку.", reply_markup=menukboard)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == "настройка":
        exitkboard = types.ReplyKeyboardMarkup(row_width=1)
        nonotifications = types.KeyboardButton(text="Не присылать уведомления")
        exit = types.KeyboardButton(text="Выход")
        exitkboard.add(nonotifications, exit)
        bot.send_message(message.chat.id, "Введи свой часовой пояс в формате UTC(от -12 до 12). "
                                          "Это нужно, чтобы присылать тебе уведомление в 12 часов "
                                          "по твоему времени. Если не хочешь получать уведомления, "
                                          "то просто введи 'Не получать уведомления'"
                                          "\nДля выхода в главное меню введи 'Выход'"
                                          "\nПример: '+5','-3', '0'", reply_markup=exitkboard)
        userdata = {"user_id": message.from_user.id,
                    "lastsmokedate": None,
                    "utc": None}
        bot.register_next_step_handler(message, settings_step1, userdata)
    elif message.text.lower() == "совет":
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, getrecomendation(), reply_markup=menukboard)
    elif message.text.lower() == "сколько я не курил?" and isuserintable(connection1, message.from_user.id):
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, gettimewithoutsmoking(connection1, message.from_user.id), reply_markup=menukboard)
    elif message.text.lower() == "я покурил :с" and isuserintable(connection1, message.from_user.id):
        sendmsg = resetlastsmokedate(connection1, message.from_user.id)
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, sendmsg, reply_markup=menukboard)
    else:
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, "Я тебя не понимаю", reply_markup=menukboard)


def settings_step1(message, userdata):
    if message.text.lower() == "выход":
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, "Возвращаемся в главное меню", reply_markup=menukboard)
    elif message.text.lower() == "не присылать уведомления":
        userdata["utc"] = -100
        menukboard = types.ReplyKeyboardMarkup(row_width=1)
        fromnow = types.KeyboardButton(text="Перестаю курить с этого момента")
        setdate = types.KeyboardButton(text="Указать время последнего курения")
        exit = types.KeyboardButton(text="Выход")
        menukboard.add(fromnow, setdate, exit)
        bot.send_message(message.chat.id, "Когда ты последний раз курил?", reply_markup=menukboard)
        bot.register_next_step_handler(message, settings_step2, userdata)
    else:
        try:
            utc = int(message.text)
            if -12 <= utc <= 12:
                userdata["utc"] = utc
                menukboard = types.ReplyKeyboardMarkup(row_width=1)
                fromnow = types.KeyboardButton(text="Перестаю курить с этого момента")
                setdate = types.KeyboardButton(text="Указать время последнего курения")
                exit = types.KeyboardButton(text="Выход")
                menukboard.add(fromnow, setdate, exit)
                bot.send_message(message.chat.id, "Когда ты последний раз курил?", reply_markup=menukboard)
                bot.register_next_step_handler(message, settings_step2, userdata)
            else:
                raise Exception
        except Exception:
            exitkboard = types.ReplyKeyboardMarkup(row_width=1)
            nonotifications = types.KeyboardButton(text="Не присылать уведомления")
            exit = types.KeyboardButton(text="Выход")
            exitkboard.add(nonotifications, exit)
            bot.send_message(message.chat.id, "Введено некорректное значение. Это нужно, чтобы присылать тебе "
                                              "уведомление в 12 часов по твоему времени. Если не хочешь получать "
                                              "уведомления, То просто введи 'Не получать уведомления'"
                                              "\nДля выхода в главное меню введи 'Выход'"
                                              "\nПример: '+5','-3', '0'", reply_markup=exitkboard)
            bot.register_next_step_handler(message, settings_step1, userdata)


def settings_step2(message, userdata: dict):
    if message.text.lower() == "выход":
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, "Возвращаемся в главное меню", reply_markup=menukboard)
    elif message.text.lower() == "перестаю курить с этого момента":
        userdata["lastsmokedate"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isuserintable(connection1, message.from_user.id):
            updateusersettings(connection1, userdata)
            menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
            lastsmokedate = userdata.get("lastsmokedate", "Ошибка")
            notifications = f"Включены, UTC-'{userdata['utc']}'" if userdata["utc"] != -100 else "Отключены"
            bot.send_message(message.chat.id, "Настройка завершена"
                                              "\nВаши параметры:"
                                              f"\nДата последнего курения: {lastsmokedate}"
                                              f"\nУведомления: {notifications}", reply_markup=menukboard)
        else:
            adduser(connection1, userdata)
            menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
            lastsmokedate = userdata.get("lastsmokedate", "Ошибка")
            notifications = f"Включены, UTC-{userdata['utc']}" if userdata["utc"] != -100 else "Отключены"
            bot.send_message(message.chat.id, "Настройка завершена"
                                              "\nВаши параметры:"
                                              f"\nДата последнего курения: {lastsmokedate}"
                                              f"\nУведомления: {notifications}", reply_markup=menukboard)
    elif message.text.lower() == "указать время последнего курения":
        menukboard = types.ReplyKeyboardMarkup(row_width=1)
        exit = types.KeyboardButton(text="Выход")
        menukboard.add(exit)
        bot.send_message(message.chat.id, "Укажи  дату своего последнего курения в формате ГГГГ-"
                                          "ММ-ДД ЧЧ:ММ:СС"
                                          "\nПример: 2021-05-15 16:15:00", reply_markup=menukboard)
        bot.register_next_step_handler(message, setlastsmokedate, userdata)


def setlastsmokedate(message, userdata):
    if message.text.lower() == "выход":
        menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
        bot.send_message(message.chat.id, "Возвращаемся в главное меню", reply_markup=menukboard)
    else:
        try:
            if datetime.strptime(message.text, "%Y-%m-%d %H:%M:%S") > datetime.now():
                raise Exception
            else:
                userdata["lastsmokedate"] = message.text

                if isuserintable(connection1, message.from_user.id):
                    updateusersettings(connection1, userdata)
                    menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
                    lastsmokedate = userdata.get("lastsmokedate", "Ошибка")
                    notifications = f"Включены, UTC-{userdata['utc']}" if userdata["utc"] != -100 else "Отключены"
                    bot.send_message(message.chat.id, "Настройка завершена"
                                                      "\nВаши параметры:"
                                                      f"\nДата последнего курения: {lastsmokedate}"
                                                      f"\nУведомления: {notifications}", reply_markup=menukboard)
                else:
                    adduser(connection1, userdata)
                    menukboard = createmenukboard(isuserintable(connection1, message.from_user.id))
                    lastsmokedate = userdata.get("lastsmokedate", "Ошибка")
                    notifications = f"Включены, UTC-{userdata['utc']}" if userdata["utc"] != -100 else "Отключены"
                    bot.send_message(message.chat.id, "Настройка завершена"
                                                      "\nВаши параметры:"
                                                      f"\nДата последнего курения: {lastsmokedate}"
                                                      f"\nУведомления: {notifications}", reply_markup=menukboard)
        except Exception:
            menukboard = types.ReplyKeyboardMarkup(row_width=1)
            exit = types.KeyboardButton(text="Выход")
            menukboard.add(exit)
            bot.send_message(message.chat.id, "Некорректная дата. Укажи  дату своего последнего курения в формате\n"
                                              "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
                                              "\nПример: 2021-05-15 16:15:00", reply_markup=menukboard)
            bot.register_next_step_handler(message, setlastsmokedate, userdata)


def notification(bot, connection1):
    while True:
        utclst = [s for s in range(-12, 12)]
        while utclst:
            try:
                userdict = getuserdict(connection1)
            except Exception:
                print("Не удалось получить словарь пользователей")
                continue
            currenthour = datetime.utcnow().hour
            utcwhere12h = 12 - currenthour
            if utcwhere12h in utclst and userdict[utcwhere12h]:
                for user_id in userdict[utcwhere12h]:
                    try:
                        msg = f"Ежедневный отчёт:\n{gettimewithoutsmoking(connection1, user_id)}"
                        bot.send_message(user_id, msg)
                    except Exception:
                        print(f"Не удалось отправить сообщение пользователю {user_id}")
                utclst.remove(utcwhere12h)
            time.sleep(60)


def main():
    th = Thread(target=notification, args=(bot, connection1))
    th.start()

    bot.polling(none_stop=True, interval=0)


if __name__ == "__main__":
    main()
