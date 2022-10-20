from telebot import types
from random import randint


def createmenukboard(userintable):
    if userintable:
        menukboard = types.ReplyKeyboardMarkup(row_width=1)
        howmuch = types.KeyboardButton(text="Сколько я не курил?")
        advice = types.KeyboardButton(text="Совет")
        settings_step1 = types.KeyboardButton(text="Настройка")
        smoked = types.KeyboardButton(text="Я покурил :с")
        menukboard.add(howmuch, advice, settings_step1, smoked)
        return menukboard
    else:
        menukboard = types.ReplyKeyboardMarkup(row_width=1)
        settings_step1 = types.KeyboardButton(text="Настройка")
        menukboard.add(settings_step1)
        return menukboard


def getrecomendation():
    try:
        with open("recomendations.txt", "r", encoding='utf-8') as recomendation:
                message = recomendation.readlines()
                return message[randint(0,len(message))]
    except Exception:
        return "Прооизошла ошибка"

