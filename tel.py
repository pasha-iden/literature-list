import telebot, psycopg2
from telebot import types

bot = telebot.TeleBot('')


# Функция подачи SQL запроса
def dbaction(selection, query):
    datas=None
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",
            user="postgres",
            password="postgres",
            database="postgres",
            port=5432)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(query) # <--- сюда передается SQL запрос
            connection.commit()
            if selection==1:
                datas=cursor.fetchall()
    except Exception as _ex:
        print ('Error:', _ex)
    finally:
        if connection:
            connection.close()
    return datas

# SELECT функции
def genreslist():
    genres=dbaction(1, '''SELECT * FROM genres''')
    return genres
def bookslist():
    books=''
    gl=genreslist()
    for i in range(len(gl)):
        gbl=chgenrelist(gl[i][1])
        if gbl>[]:
            books=books + gl[i][1] + ': \n\n'
            for l in range(len(gbl)):
                books=books + gbl[l][1] + '\n' + gbl[l][2] + '\n\n'
    return books
def chgenrelist(choisengenre):
    query="SELECT * FROM books WHERE genre='" + choisengenre + "' ORDER BY numingenre"
    cgl=dbaction(1, query)
    return cgl

# INSERT функции
def bookadding (infoaboutbook):
    i = dbaction(1, '''SELECT MIN(id) FROM emptyids''')
    if i[0][0] == None:
        i = dbaction(1, '''SELECT MAX(id) FROM books''')
        if i[0][0] == None:
            infoaboutbook[0] = 1
        else:
            infoaboutbook[0] = i[0][0] + 1
    else:
        infoaboutbook[0] = i[0][0]
        query = "DELETE FROM emptyids WHERE id=" + str(i[0][0])
        n = dbaction(0, query)
    query='''INSERT INTO books VALUES (''' + str(infoaboutbook[0]) + ", '" + infoaboutbook[1] + "', '" + infoaboutbook[2] + "', '" + infoaboutbook[3] + "', '" + str(infoaboutbook[4]) + "')"
    n=dbaction(0, query)
def bookaddinginto (infoaboutbook):

    # определение списка книг, которые нужно сдвинуть в списке жанра
    query = "SELECT id, numingenre FROM books WHERE genre='" + infoaboutbook[3] + "' AND numingenre>" + str(int(infoaboutbook[4])-1)
    renuberingbooks = dbaction(1, query)

    # сдвиг книг в жанре
    for i in range(len(renuberingbooks)):
        query = "UPDATE books SET numingenre =" + str(renuberingbooks[i][1]+1) + " WHERE id=" + str(renuberingbooks[i][0])
        n = dbaction(0, query)

    # добавление книги в список
    i = dbaction(1, '''SELECT MIN(id) FROM emptyids''')
    if i[0][0] == None:
        i = dbaction(1, '''SELECT MAX(id) FROM books''')
        infoaboutbook[0] = i[0][0] + 1
    else:
        infoaboutbook[0] = i[0][0]
        query = "DELETE FROM emptyids WHERE id=" + str(i[0][0])
        n = dbaction(0, query)
    i = dbaction(0, '''SELECT MAX(id) FROM books''')
    query = '''INSERT INTO books VALUES (''' + str(infoaboutbook[0]) + ", '" + infoaboutbook[1] + "', '" + infoaboutbook[2] + "', '" + infoaboutbook[3] + "', '" + str(infoaboutbook[4]) + "')"
    n = dbaction(0, query)

# DELETE функция
def bookdelete (infoaboutbook):
    # сохранение номера освобождающейся ячейки, чтобы в будущем добавить книгу в нее
    query = "SELECT id FROM books WHERE genre='" + infoaboutbook[3] + "' AND numingenre=" + str(infoaboutbook[4])
    newemptyid = dbaction(1, query)
    query = "INSERT INTO emptyids (id) VALUES (" + str(newemptyid[0][0]) + ")"
    n = dbaction(0, query)

    # удаление книги из списка книг
    query = "DELETE FROM books WHERE genre='" + infoaboutbook[3] + "' AND numingenre=" + str(infoaboutbook[4])
    n = dbaction(0, query)

    # определение списка книг, которые нужно сдвинуть в списке жанра
    query = "SELECT id, numingenre FROM books WHERE genre='" + infoaboutbook[3] + "' AND numingenre>" + str(int(infoaboutbook[4]) - 1)
    renuberingbooks = dbaction(1, query)

    # сдвиг книг в жанре
    for i in range(len(renuberingbooks)):
        query = "UPDATE books SET numingenre =" + str(renuberingbooks[i][1]-1) + " WHERE id=" + str(renuberingbooks[i][0])
        n = dbaction(0, query)


bookforadd=[0, 0, 0, 0, 0]
actualact=[None]

@bot.message_handler(commands=['start'])
def start (message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Добавить книгу', callback_data='adding'))
    markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
    markup.add(types.InlineKeyboardButton('Удалить книгу', callback_data='deleting'))
    bot.send_message(message.chat.id, 'Действие', reply_markup=markup)

@bot.callback_query_handler(func = lambda callback:True)
def buttoms (callback):

    # Добавление книги 1: запрос указания названия книги
    if callback.data == 'adding':
        bot.send_message(callback.message.chat.id, 'Название книги')
        bot.register_next_step_handler(callback.message, adding_name)

    # Удаление книги 1: запрос указания жанра
    elif callback.data == 'deleting':
        genres = genreslist()
        markup = types.InlineKeyboardMarkup()
        for i in range(len(genres)):
            if genres[i][2] == 'russian':
                markup.add(types.InlineKeyboardButton('Русская художественная литература', callback_data=genres[i][2]))
            elif genres[i][2] == 'foreign':
                markup.add(types.InlineKeyboardButton('Зарубужная художественная литература', callback_data=genres[i][2]))
            else:
                markup.add(types.InlineKeyboardButton(genres[i][1], callback_data=genres[i][2]))
        bot.send_message(callback.message.chat.id, 'Жанр:', reply_markup=markup)
        actualact[0] = 'deleting'

    # Просмотр списка книг
    elif callback.data == 'watch':
        books = bookslist()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
        markup.add(types.InlineKeyboardButton('Перейти на сайт', url='http://92.118.114.135:1001/library'))
        bot.send_message(callback.message.chat.id, 'Список: \n\n' + books, reply_markup=markup)

    # Добавление книги 4: добавление жанра, запрос указания места в списке книг жанра.
    elif actualact[0] == 'adding':
        actualact[0] = None
        genres = genreslist()
        for i in range(len(genres)):
            if callback.data == genres[i][2]:
                bookforadd[3] = genres[i][1]
                choisengenrebooks=chgenrelist(bookforadd[3])
                if choisengenrebooks==[]:
                    bookforadd[4]=1
                    bookadding(bookforadd)
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
                    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='http://92.118.114.135:1001/library'))
                    bot.send_message(callback.message.chat.id, 'Книга добавлена: \n\n Книга: ' + bookforadd[1] + '\n Автор: ' + bookforadd[2] + '\n Жанр: ' + bookforadd[3] + '\n Место в списке: ' + str(bookforadd[4]), reply_markup=markup)
                else:
                    bl=str()
                    for l in range(len(choisengenrebooks)):
                        bl=bl + str(choisengenrebooks[l][4]) + '. ' + choisengenrebooks[l][1] + '\n' + choisengenrebooks[l][2] + '\n\n'
                    bot.send_message(callback.message.chat.id, 'На какое место поставить эту книгу: \n\n' + str(bl))
                    bot.register_next_step_handler(callback.message, accepting)

    # Удаление книги 2: проверка на пустоту жанра, добавление жанра, запрос указания номера книги в жанре
    elif actualact[0] == 'deleting':
        actualact[0] = None
        genres = genreslist()
        for i in range(len(genres)):
            if callback.data == genres[i][2]:
                bookforadd[3] = genres[i][1]
                choisengenrebooks = chgenrelist(bookforadd[3])
                if choisengenrebooks==[]:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
                    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='http://92.118.114.135:1001/library'))
                    bot.send_message(callback.message.chat.id, 'Жанр ' + bookforadd[3] + ' - пуст.', reply_markup=markup)
                else:
                    bl = str()
                    for l in range(len(choisengenrebooks)):
                        bl = bl + str(choisengenrebooks[l][4]) + '. ' + choisengenrebooks[l][1] + '\n' + \
                             choisengenrebooks[l][2] + '\n\n'
                    bot.send_message(callback.message.chat.id, 'Какую книгу удалить: \n\n' + str(bl))
                    bot.register_next_step_handler(callback.message, enddeleting)

# Добавление книги 2: добавление названия книги, запрос указания автора
def adding_name (message):
    bookforadd[1]=message.text
    bot.send_message(message.chat.id, 'Автор')
    bot.register_next_step_handler(message, genre_name)

# Добавление книги 3: добавление автора, запрос выбора жанра
def genre_name (message):
    bookforadd[2]=message.text
    genres = genreslist()
    markup = types.InlineKeyboardMarkup()
    for i in range(len(genres)):
        if genres [i][2]=='russian':
            markup.add(types.InlineKeyboardButton('Русская художественная литература', callback_data=genres[i][2]))
        elif genres [i][2]=='foreign':
            markup.add(types.InlineKeyboardButton('Зарубужная художественная литература', callback_data=genres[i][2]))
        else:
            markup.add(types.InlineKeyboardButton(genres[i][1], callback_data=genres[i][2]))
    bot.send_message(message.chat.id, 'Жанр:', reply_markup=markup)
    actualact[0] = 'adding'

# Добавление книги 5: добавление места книги в списке книг жанра, отчет о завершении добавления. Выбор дальнейшего действия.
def accepting (message):
    bookforadd[4] = message.text
    if int(bookforadd[4]) > len(chgenrelist(bookforadd[3])):
        bookadding(bookforadd)
    else:
        bookaddinginto(bookforadd)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='http://92.118.114.135:1001/library'))
    bot.send_message(message.chat.id, 'Книга добавлена: \n\n Книга: ' + bookforadd[1] + '\n Автор: ' + bookforadd[2] + '\n Жанр: ' + bookforadd[3] + '\n Место в списке: ' + str(bookforadd[4]), reply_markup=markup)

# Удаление книги 3: указание удаляемой книги, отчет о завершении удаления. Выбор дальнейшего действия.
def enddeleting (message):
    bookforadd[4] = message.text
    bookdelete(bookforadd)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Посмотреть весь список', callback_data='watch'))
    markup.add(types.InlineKeyboardButton('Перейти на сайт', url='http://92.118.114.135:1001/library'))
    bot.send_message(message.chat.id, 'Книга удалена.', reply_markup=markup)


bot.infinity_polling()