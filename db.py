import sqlite3
from sqlite3 import Error
from datetime import datetime


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path, check_same_thread=False)
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query, params={}):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred1")


def execute_read_query(connection, query, dict=''):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, dict)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query_all(connection, query, dict=''):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, dict)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def create_table1(connection):
    create_table = """
    CREATE TABLE IF NOT EXISTS nosmokers (
      user_id TEXT,
      lastsmokedate TEXT,
      utc INTEGER
    );
    """
    execute_query(connection, create_table)


def isuserintable(connection, user_id):
    select_user = f"SELECT * from nosmokers WHERE user_id = {user_id}"
    user = execute_read_query(connection, select_user)
    if user:
        return True
    else:
        return False


def adduser(connection, userdata):
    addquery = f"""
        INSERT INTO
          nosmokers (user_id, lastsmokedate, utc)
        VALUES
          (:user_id, :lastsmokedate, :utc)
        """
    # userdata = {'user_id': user_id, 'name': name, 'note': note, 'user_id': user_id}

    execute_query(connection, addquery, userdata)


def updateusersettings(connection, userdata):
    update = f"UPDATE nosmokers SET lastsmokedate = :lastsmokedate," \
                f"utc = :utc " \
                f"WHERE user_id = :user_id"
    execute_query(connection, update, userdata)


def gettimewithoutsmoking(connection, user_id):

    select_userdata = f"SELECT * from nosmokers WHERE user_id = {user_id}"
    lastsmokedate = execute_read_query(connection, select_userdata)[1]
    delta = getdelta(lastsmokedate)
    msg = "Вы не курили " + delta + ""

    msg += "Молодец!"
    if msg != "Произошла ошибка":
        return msg
    else:
        return msg


def getdelta(date: str):
    try:
        delta = datetime.now() - datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        days = delta.days
        minutes = delta.seconds % 3600 // 60
        hours = delta.seconds % 86400 // 3600
        seconds = delta.seconds % 3600 % 60
        result = ""

        if days % 10 == 1 and days % 100 != 11:
            result += f"{days} день "
        elif days % 10 < 5 and days % 10 != 0:
            result += f"{days} дня "
        else:
            result += f"{days} дней "

        if hours % 10 == 1 and hours % 100 != 11:
            result += f"{hours} час "
        elif hours % 100 < 5 and hours % 10 != 0:
            result += f"{hours} часа "
        else:
            result += f"{hours} часов "

        if minutes % 10 == 1 and minutes != 11:
            result += f"{minutes} минуту "
        elif minutes % 10 < 5 and minutes % 10 != 0:
            result += f"{minutes} минуты "
        else:
            result += f"{minutes} минут "

        if seconds % 10 == 1 and seconds != 11:
            result += f"{seconds} секунду "
        elif seconds % 10 < 5 and seconds % 10 != 0:
            result += f"{seconds} секунды "
        else:
            result += f"{seconds} секунд "
        return result
    except Exception:
        return "Произошла ошибка"


def resetlastsmokedate(connection, user_id):
    select_userdata = f"SELECT * from nosmokers WHERE user_id = {user_id}"
    lastsmokedate = execute_read_query(connection, select_userdata)[1]
    delta = getdelta(lastsmokedate)
    resettime = f"UPDATE nosmokers SET lastsmokedate = :lastsmokedate" \
                f" WHERE user_id = :user_id"
    time = {"lastsmokedate": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user_id": user_id}
    execute_query(connection, resettime, time)
    if delta != "Произошла ошибка":
        return f"Что ж, ты продержался {delta}. Не расстраивай меня больше"
    else:
        return delta


def getuserdict(connection):
    userdict = {}
    for i in range(-12, 12):
        userdict[i] = []

    select_userdata = f"SELECT user_id from nosmokers WHERE utc = -12"
    users = execute_read_query_all(connection, select_userdata)
    if users != None:
        for id in users:
            userdict[-12].append(id)

    select_userdata = f"SELECT user_id from nosmokers WHERE utc = 12"
    users = execute_read_query_all(connection, select_userdata)
    if users != None:
        for id in users:
            userdict[-12].append(id)

    for utc in range(-11,12):
        select_userdata = f"SELECT user_id from nosmokers WHERE utc = {utc}"
        users = execute_read_query_all(connection, select_userdata)
        if users != None:
            for id in users:
                userdict[utc].append(id)
    return userdict
