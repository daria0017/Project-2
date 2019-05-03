# -*- coding: utf-8 -*-
import requests
import bs4
import sqlite3
import re
from app import bot
from datetime import date


conn = sqlite3.connect('../TVShows.db')
ref_title_info = ''


def create_table(cur, conn):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            rating FLOAT,
            genre VARCHAR(255),
            num_of_seasons INTEGER,
            status VARCHAR(255),
            poster VARCHAR(255),
            date VARCHAR(255),
            episode VARCHAR(255),
            site_url VARCHAR(255)
        )''')
    conn.commit()


@bot.message_handler(commands=['start'])
def handle_start(message):
    global ref_title_info
    ref_title_info = ''
    global counter
    counter = ''
    bot.send_message(message.chat.id, 'Привет! Я помогу тебе '
        'следить за любимыми сериалами. Какой сериал тебя интересует?')


@bot.message_handler(commands=['help'])
def handle_help(message):
    answer = u'\U0001F50E' + \
                    '*Доступные команды:*\n/start - получить' \
    ' приветствие бота\n/add число - добавить в избранное сериал, ' \
    'выведенный под определенным номером\n/getdate название - ' \
    'узнать, когда выйдет следующая серия сериала из ' \
    'избранного\n/showsaved - получить основную информацию о ' \
    'сериалах из избранного\n/getweekschedule - получить расписание ' \
    'выхода серий сериалов из избранного на следующие семь дней' \
    '\n/remove название - удалить сериал из избранного'
    bot.send_message(message.chat.id, answer, parse_mode="Markdown")


@bot.message_handler(commands=['getdate'])
def handle_get_date(message):
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    update()
    tv_show_name = message.text.partition(' ')[2].upper()
    with sqlite3.connect('../TVShows.db') as conn:
        query = '''SELECT favourites.date, favourites.episode
                                  FROM favourites
                                  WHERE favourites.name = '{}' 
                                        '''.format(tv_show_name)
        cur = conn.cursor()
        cur.execute(query)
        tv_show_date = cur.fetchall()
        try:
            if re.search(r'^\d+\s\w+\s\d{4}$', tv_show_date[0][0]):
                bot.send_message(message.chat.id, 'Следующая ' \
                'серия ({}) выйдет {}!'.format(tv_show_date[0][1],
                tv_show_date[0][0]) + u'\U0001F60D')
            elif re.search(r'^\d{4}$', tv_show_date[0][0]):
                bot.send_message(message.chat.id, 'Следующая ' \
                'серия ({}) выйдет в {}!'.format(tv_show_date[0][1],
                tv_show_date[0][0]) + u'\U0001F60D')
            else:
                bot.send_message(message.chat.id, tv_show_date[0][0])
        except:
            bot.send_message(message.chat.id, 'Такого сериала нет'
                                                    ' в избранном.')


@bot.message_handler(commands=['getweekschedule'])
def handle_get_week_schedule(message):
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    update()
    today = date.today()
    month_to_num = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }
    schedule = {}

    with sqlite3.connect('../TVShows.db') as conn:
        query = '''SELECT * FROM favourites'''
        cur = conn.cursor()
        cur.execute(query)
        tvshows = cur.fetchall()
        for tvshow in tvshows:
            if re.search(r'^[1-9]+\s\w+\s\d{4}$', tvshow[7]):
                next_date = date(int(tvshow[7].split(' ')[2]),
                        month_to_num[tvshow[7].split(' ')[1]],
                                int(tvshow[7].split(' ')[0]))
                if (next_date - today).days < 7:
                    schedule.update({tvshow : next_date})
        if len(schedule) == 0:
            bot.send_message(message.chat.id, 'В ближайшие 7' \
                    ' дней не выйдет ни одной серии ' + u'\U0001F622')
        else:
            answer = u'\U0001F525' + '*Расписание на неделю:* \n'
            for keys, values in sorted(schedule.items(),
                                       key=lambda item: item[1]):
                answer += values.strftime("%d/%m/%Y") +  ' - '\
                                                    + keys[1] + '\n'
            bot.send_message(message.chat.id, answer,
                                            parse_mode="Markdown")


@bot.message_handler(commands=['remove'])
def handle_remove(message):
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    tv_show_name = message.text.partition(' ')[2].upper()
    with sqlite3.connect('../TVShows.db') as conn:
        query = "DELETE FROM favourites WHERE name = " \
                            "'{}'".format(tv_show_name)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()


@bot.message_handler(commands=['showsaved'])
def handle_show_saved(message):
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    update()
    with sqlite3.connect('../TVShows.db') as conn:
        query = '''SELECT * FROM favourites'''
        cur = conn.cursor()
        cur.execute(query)
        names = cur.fetchall()
        for name in names:
            answer = u'\U00002764' + '* ' + str(name[1]) + '* \n'
            answer += '*Рейтинг: *' + str(name[2]) + u'\U00002B50' + '\n'
            answer += '*Жанр: *' + str(name[3]) + '\n'
            answer += '*Сезонов: *' + str(name[4]) + '\n'
            answer += '*Статус: *' + str(name[5]) + '\n'
            answer += '[Смотреть постер...]' + '(' + str(name[6]) + ')'
            bot.send_message(message.chat.id, answer,
                                    parse_mode="Markdown")
        if len(names) == 0:
            bot.send_message(message.chat.id,
                             'На данный момент не сохранен '
                                              'ни один сериал...')


def update():
    with sqlite3.connect('../TVShows.db') as conn:
        query = '''SELECT * FROM favourites'''
        cur = conn.cursor()
        cur.execute(query)
        names = cur.fetchall()
        if len(names) != 0:
            for name in names:
                tv_show_url = name[9]
                tv_show_site = requests.get(tv_show_url)
                show_site_prs_obj = bs4.BeautifulSoup(tv_show_site.text,
                                                      "html.parser")
                status =  show_site_prs_obj.findAll("div",
                    {"class" : "block_list"})[0].getText().strip()
                if status == 'Выходит':
                    date_of_new_episode = show_site_prs_obj.findAll('td',
                                {'id': 'not-air'})[2].getText().strip()
                    num_of_episode = show_site_prs_obj.findAll('td',
                        {'id': 'not-air'})[0].contents[0].attrs['name']
                else:
                    date_of_new_episode = 'Дата выхода следующей ' \
                                                'серии неизвестна.'
                    num_of_episode = '-'
                rating = show_site_prs_obj.find('meta', {'itemprop':
                                    'ratingValue'}).attrs['content']
                num_of_seasons = show_site_prs_obj.findAll('h2' 
                                '')[0].getText().split(' ')[1]
                cur.execute('''DELETE FROM favourites WHERE name = 
                                        '{}' '''.format(name[1]))
                cur.execute('''INSERT INTO favourites 
                (name, rating, genre, num_of_seasons, status,
                            poster, date,  episode, site_url) 
                VALUES ('{}', ' {} ', '{}', '{}', '{}', '{}', 
                            '{}', '{}', '{}')'''.format(name[1],
                    rating, name[3], num_of_seasons, status, name[6],
                        date_of_new_episode, num_of_episode, name[9]))


@bot.message_handler(commands=['add'])
def handle_add(message):
    global ref_title_info
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    try:
        idx = int(message.text.split()[1:][0]) - 1
        if ref_title_info != '' and idx < counter and idx >= 0:
            tv_show = ref_title_info[idx]
            tv_show_url = 'https://www.toramp.com/' + \
                                    tv_show.attrs['href']
            tv_show_site = requests.get(tv_show_url)
            show_site_prs_obj = bs4.BeautifulSoup(tv_show_site.text,
                                                        "html.parser")

            name = tv_show.getText().upper()
            rating = show_site_prs_obj.find('meta', {'itemprop':
                                    'ratingValue'}).attrs['content']
            genre = \
                tv_show_info[idx].findAll("div")[2].contents[1].strip()
            num_of_seasons = tv_show_info[idx].find("a").getText()
            if tv_show_info[idx].findAll("div"
                            "")[1].contents[1].strip() == 'Выходит':
                date_of_new_episode = show_site_prs_obj.findAll('td',
                            {'id': 'not-air'})[2].getText().strip()
                num_of_episode = show_site_prs_obj.findAll('td',
                    {'id': 'not-air'})[0].contents[0].attrs['name']
            else:
                date_of_new_episode = 'К сожалению, дата выхода ' \
                                    'следующей серии неизвестна.'
                num_of_episode = '-'
            poster_url = show_site_prs_obj.find('img', {'title':
                                    True}).attrs['src'].replace('(',
                                        '%28').replace(')', '%29')
            status = (tv_show_info[idx].findAll("div"
                                        "")[1]).contents[1].strip()

            with sqlite3.connect('../TVShows.db') as conn:
                cur = conn.cursor()
                select_str ='''
                    SELECT * FROM favourites WHERE name= '{}' 
                    '''.format(name)
                cur.execute(select_str)
                entry = cur.fetchone()
                if entry is None:
                    insert_str = '''INSERT INTO favourites 
                (name, rating, genre, num_of_seasons, status,
                poster, date, episode, site_url) 
                VALUES ('{}', '{}', ' {} ', '{}', '{}', '{}', '{}', 
                                     '{}', '{}')'''.format(name, rating,
                             genre, num_of_seasons, status, poster_url,
                            date_of_new_episode, num_of_episode, tv_show_url)
                    cur.execute(insert_str)
                    conn.commit()
        else:
            bot.send_message(message.chat.id, 'Не удалось сохранить ' \
                                    'сериал в избранное. Возможно ' \
                                        'был неверно введен номер.')
    except Exception:
        bot.send_message(message.chat.id, 'Не удалось сохранить ' \
                                    'сериал в избранное. Возможно ' \
                                        'был неверно введен номер.')


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    with sqlite3.connect('../TVShows.db') as conn:
        cur = conn.cursor()
        create_table(cur, conn)
    global counter
    counter = 0
    site_url = 'https://www.toramp.com/search.php?search=' + \
                                                str(message.text)
    site = requests.get(site_url)
    site_prs_obj = bs4.BeautifulSoup (site.text, "html.parser")
    global ref_title_info
    ref_title_info = site_prs_obj.find_all('a', {'class': 'title'})
    global tv_show_info
    tv_show_info = site_prs_obj.find_all('div', {'class': 'ser-info'})
    if not ref_title_info:
        bot.send_message(message.chat.id,
                                    'По запросу ничего не найдено.')
        ref_title_info = ''
    else:
        send_tv_shows(message)
        if len(ref_title_info) - counter > 0:
            bot.send_message(message.chat.id,
                                        'Показать больше сериалов?')
            bot.register_next_step_handler(message, show_more)
        else:
            bot.send_message(message.chat.id, 'Все сериалы по ' \
            'запросу "{}" показаны. Хочешь узнать дату выхода ' \
            'следующей серии одного из показанных сериалов?' \
                                        ''.format(message.text))
            bot.register_next_step_handler(message, show_date_answer)


def show_more(message):
    global counter
    if re.search(r'^[Дд][Аа]$', message.text):
        send_tv_shows(message)
        if len(ref_title_info) - counter > 0:
            bot.send_message(message.chat.id, 'Показать больше сериалов?')
            bot.register_next_step_handler(message, show_more)
        else:
            bot.send_message(message.chat.id, 'Все сериалы ' \
            'показаны. Хочешь узнать дату выхода следующей серии ' \
                                'одного из показанных сериалов?')
            bot.register_next_step_handler(message, show_date_answer)
    else:
        bot.send_message(message.chat.id, 'Хочешь узнать дату ' \
            'выхода следующей серии одного из показанных сериалов?')
        bot.register_next_step_handler(message, show_date_answer)


def show_date_answer(message):
     global counter
     if re.search(r'^[Дд][Аа]$', message.text):
        bot.send_message(message.chat.id, 'Введи номер ' \
                            'интересующего тебя сериала.')
        bot.register_next_step_handler(message, show_date_of_new_episode)


def send_tv_shows(message):
    global ref_title_info
    global tv_show_info
    global counter
    for idx in range(counter, counter + min(5,
                                    len(ref_title_info) - counter)):
        counter += 1
        tv_show = ref_title_info[idx]
        answer =  u'\U0001F4CC' + ' *' + str(counter) + '* \n'
        answer += 	u'\U0001F3AC' + '* ' + \
                            tv_show.getText().upper() + '* \n'
        tv_show_url = 'https://www.toramp.com/' + tv_show.attrs['href']
        tv_show_site = requests.get(tv_show_url)
        show_site_prs_obj = bs4.BeautifulSoup(tv_show_site.text,
                                                    "html.parser")
        answer += '*Рейтинг: *' + show_site_prs_obj.find('meta',
                        {'itemprop': 'ratingValue'}).attrs['content']\
                                                + u'\U00002B50' + '\n'
        answer += '*Жанр: *' + \
            (tv_show_info[idx].findAll("div")[2].contents[1].strip())\
                                                                + '\n'
        answer += '*Сезонов: *' + \
                    (tv_show_info[idx].find("a").getText()) + '\n'
        answer += '*Статус: *' + \
            (tv_show_info[idx].findAll("div")[1]).contents[1].strip()\
                                                                + '\n'
        image_ref = (show_site_prs_obj.find('img', {'title':
            True})).attrs['src'].replace('(', '%28').replace(')', '%29')
        answer += '[Смотреть постер...]' + '(' + image_ref + ')'
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")


def show_date_of_new_episode(message):
    global counter
    try:
        idx = int(message.text) - 1
        if idx < counter:
            if (tv_show_info[idx].findAll("div")[1]).contents[1].strip()\
                                                        == 'Выходит':
                tv_show = ref_title_info[idx]
                tv_show_url = 'https://www.toramp.com/' + \
                                        tv_show.attrs['href']
                tv_show_site = requests.get(tv_show_url)
                show_site_prs_obj = \
                            bs4.BeautifulSoup(tv_show_site.text,
                                                    "html.parser")
                bot.send_message(message.chat.id,
                                        'Следующая серия выйдет ' +
                            show_site_prs_obj.findAll('td', {'id':
                            'not-air'})[2].getText().strip() + '! ' +
                                                    u'\U0001F60D')
            else:
                bot.send_message(message.chat.id,
                                 'К сожалению, дата выхода следующей ' \
                                'серии неизвестна ' + u'\U0001F622')
        else:
            bot.send_message(message.chat.id,
                                    'Введен неправильный номер ' \
                                        'сериала ' + u'\U0001F622')
    except ValueError:
        bot.send_message(message.chat.id,
                                'Введен неправильный номер серила ' \
                                                    + u'\U0001F622')


