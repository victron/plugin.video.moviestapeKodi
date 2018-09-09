# -*- coding: utf-8 -*-
__author__ = 'vic'

import requests
import re
from bs4 import BeautifulSoup
import xbmc, xbmcgui
# from addon import connect_timeout, read_timeout, max_retries, too_slow_connection, waited_too_long_between_bytes,\
#     get_an_HTTPError, not_expected_output
# get web page source
# dialog = xbmcgui.Dialog()

url_root = 'http://moviestape.net'


def log(msg, level=xbmc.LOGDEBUG):
    """
    "print" and xbmc.log does not support unicode. Always encode unicode strings to utf-8.
    https://kodi.wiki/view/Add-on_unicode_paths
    :param msg:
    :param level:
    :return:
    """
    plugin = "movistape"

    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')

    xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)


def GetHTML(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) '
                            'Gecko/2008092417 Firefox/3.0.3',
               'Content-Type':'application/x-www-form-urlencoded'}
    session = requests.Session()
    session.mount("http://", requests.adapters.HTTPAdapter(max_retries=max_retries))
#    connect_timeout = 2.0011
#    read_timeout = 1.0
    try:
        response = session.get(url= url, timeout=(connect_timeout, read_timeout))
        #response = requests.get(url, timeout=(connect_timeout, read_timeout))
    except requests.exceptions.ConnectTimeout as e:
        xbmc.log(msg='[ex.ua.videos]' + 'Too slow connection', level=xbmc.LOGWARNING)
        return dialog.notification('connection problem', too_slow_connection, xbmcgui.NOTIFICATION_WARNING, 5000, True)
    except requests.exceptions.ReadTimeout as e:
        xbmc.log(msg='[ex.ua.videos]' + 'Waited too long between bytes.', level=xbmc.LOGERROR)
        return dialog.notification('connection problem', waited_too_long_between_bytes,
                                   xbmcgui.NOTIFICATION_WARNING, 5000, True)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        xbmc.log(msg='[ex.ua.videos]' + 'get an HTTPError: ' + e.message, level=xbmc.LOGERROR)
        return dialog.notification('connection problem', get_an_HTTPError + e.message,
                                   xbmcgui.NOTIFICATION_WARNING, 5000, True)
#    response = requests.get(url)
    return response.text


def get_categories():
    """
    get list of categories from http://moviestape.net/
    :return:
[[{'name': 'Про кіно ', 'href': '/novyny_kino/'},
  {'name': 'Новини кіно', 'href': '/novyny_kino/'},
  {'name': 'Зірки кіно', 'href': '/persons/'},
  {'name': 'HD Трейлери', 'href': '/treilers/'},
  {'name': 'Скоро у кіно', 'href': '/newmovies/'}],
 [{'name': 'Кінорейтинги ', 'href': '/top250imdb_1.html'},
  {'name': 'IMDb Top 250', 'href': '/top250imdb_1.html'},
  {'name': 'Премія Оскар', 'href': '/oscar.html'},
  {'name': 'Кращі 50 фільмів', 'href': '/top50films.html'},
  {'name': 'Кращі 50 серіалів', 'href': '/top50serials.html'},
  {'name': 'Кращі 50 мультфільмів', 'href': '/top50multfilms.html'}],
 [{'name': 'Мультфільми ', 'href': '/katalog_filmiv/multfilm/'},
  {'name': 'Повнометражні', 'href': '/katalog_filmiv/multfilm/'},
  {'name': 'Багатосерійні', 'href': '/katalog_serialiv/multserialy/'},
  {'name': 'Короткі мультики', 'href': '/korotkometrazhky/'}],
 [{'name': 'Фільми ', 'href': '/ukrainian/'},
  {'name': 'Наше рідне', 'href': '/ukrainian/'},
  {'name': 'Бойовики', 'href': '/katalog_filmiv/bojovyky/'},
  {'name': 'Мелодрами', 'href': '/katalog_filmiv/melodrama/'},
  {'name': 'Комедії', 'href': '/katalog_filmiv/komedija/'},
  {'name': 'Пригоди', 'href': '/katalog_filmiv/prygody/'},
  {'name': 'Військові', 'href': '/katalog_filmiv/vijskovi/'},
  {'name': 'Детективи', 'href': '/katalog_filmiv/detektyv/'},
  {'name': 'Драми', 'href': '/katalog_filmiv/drama/'},
  {'name': 'Історичні', 'href': '/katalog_filmiv/istorychnyj/'},
  {'name': 'Кримінал', 'href': '/katalog_filmiv/kryminal/'},
  {'name': 'Спортивні', 'href': '/katalog_filmiv/sport/'},
  {'name': 'Трилери', 'href': '/katalog_filmiv/trylery/'},
  {'name': 'Жахи', 'href': '/katalog_filmiv/zhahy/'},
  {'name': 'Фантастика', 'href': '/katalog_filmiv/fantastyka/'},
  {'name': 'Фентезі', 'href': '/katalog_filmiv/fentezi/'},
  {'name': 'Музичні', 'href': '/katalog_filmiv/muzuchni/'},
  {'name': 'Еротика', 'href': '/erotic/'}],
 [{'name': 'Серіали ', 'href': '/katalog_serialiv/melodramy/'},
  {'name': 'Мелодрами', 'href': '/katalog_serialiv/melodramy/'},
  {'name': 'Детективи', 'href': '/katalog_serialiv/detektyvy/'},
  {'name': 'Драма', 'href': '/katalog_serialiv/dramy/'},
  {'name': 'Жахи', 'href': '/katalog_serialiv/zhah/'},
  {'name': 'Історичні', 'href': '/katalog_serialiv/istorychny/'},
  {'name': 'Комедії', 'href': '/katalog_serialiv/komedii/'},
  {'name': 'Пригоди', 'href': '/katalog_serialiv/prygodnycki/'},
  {'name': 'Трилери', 'href': '/katalog_serialiv/tryler/'},
  {'name': 'Фантастика', 'href': '/katalog_serialiv/fantastyk/'}]]

    """
    response = requests.get(url_root)
    soup = BeautifulSoup(response.text, 'html.parser')
    menu = soup.body.find('div', class_='menu').ul
    menu_list = []
    for submenu in menu.find_all('li', recursive=False):
        catogory_list = []
        catagory_dict = {}
        try:
            catagory_dict['name'] = submenu.a.get_text()
        except AttributeError:
            continue
        try:
            catagory_dict['href'] = submenu.a['href']
        except AttributeError:
            continue
        catogory_list.append(catagory_dict)
        try:
            for subcatogory in submenu.ul.find_all('li'):
                subcatagory_dict = {}
                remover = re.compile('[\xa0\xab]')
                # subcatagory_dict['name'] = subcatogory.a.get_text(strip=True).replace('\xa0', '')
                # subcatagory_dict['name'] = subcatagory_dict['name'].replace('\xab', '')
                subcatagory_dict['name'] = subcatogory.a.get_text(strip=True)
                subcatagory_dict['name'] = remover.sub('', subcatagory_dict['name'])
                log('name= ' + subcatagory_dict['name'], xbmc.LOGDEBUG)
                subcatagory_dict['href'] = subcatogory.a['href']
                catogory_list.append(subcatagory_dict)
        except AttributeError:
            continue
        menu_list.append(catogory_list)

    # test href, replace on redirected and on full path
    for submenu in menu_list:
        for dic in submenu:
            response = requests.get(url_root + dic['href'])
            dic['href'] = response.url

    return menu_list


def get_movie_details(url):
    """
    get details for movie, url to src file
    :param url: str
    :return: dict
    """
    resp_movie = requests.get(url)
    movie_soup = BeautifulSoup(resp_movie.text, 'html.parser')
    movie_meta = movie_soup.find('div', class_='f-content2')
    movie = {}
    movie['meta'] = movie_meta.get_text()
    movie_description = movie_soup.find('div', class_='f-content2_s')
    movie['description'] = movie_description.get_text()
    movie['src'] = movie_soup.find('iframe', id='pl')['src']
    return movie


def get_movies_icons(soup):
    """
    parse pages icon style, for every icon get href and go to every movie and receive details
    :param url: str
    :param page: int
    :return: list
    """
    movies = []
    for icon in soup.find_all('div', class_='bnewmovie'):
        movie = {}
        movie['detail_href'] = icon.a['href']
        movie['img'] = icon.a.img['src']
        movie['title'] = icon.a.img['title']
        movie['ycc'] = icon.find('div', class_='ycc').get_text()
        remover = re.compile('[\xa0\xab]')
        movie['ycc'] = remover.sub('', movie['ycc'])

        movie.update(get_movie_details(movie['detail_href']))
        movies.append(movie)
    return movies


def get_movies_list(soup):
    """
    parse pages list style, for every list member get href and go to every movie and receive details
    :param url:
    :param page:
    :return:
[{'img': 'http://moviestape.net/uploads/posts/2012-04/1334321686_poster.jpg',
  'title': 'Астерікс в Британії',
  'detail_href': 'http://moviestape.net/katalog_multfilmiv/multfilm/1711-asteriks-v-brytanii.html',
  'meta': "\nЖанр: Мультфільми онлайн » Мультфільми \nТривалість:  78 хв. \nКраїна:  Франція \n\nПереклад:  Український (Професійний багатоголосий) \nРежисер:  Піно Ван Ламсвеерде \nАктори:  Роже Карель, П'єр Торнад, Грехем Бушнелл, П'єр Монді, Моріс Ріш, Ніколя Сільберг, Альбер Ожье, Пол Бісціліа \n\n",
  'description': 'Астерікс вирушає до Британії, щоб допомогти троюрідному брату здолати Юлія Цезаря і його армію.',
  'src': 'http://fs0.moviestape.net/show.php?name=cartoons/Asterix.chez.les.Bretons.mp4'},
 {'img': 'http://moviestape.net/uploads/posts/2012-04/1334320445_poster.jpg',
  'title': '12 подвигів Астерікса',
  'detail_href': 'http://moviestape.net/katalog_multfilmiv/multfilm/3182-12-podvygiv-asteriksa.html',
  'meta': "\nЖанр: Мультфільми онлайн » Мультфільми \nТривалість:  81 хв. \nКраїна:  Франція \n\nПереклад:  Український (Професійний багатоголосий) \nРежисер:  Рене Госинні, Генрі Грюель, Альбер Юдерзо \nАктори:  Роже Карель, П'єр Торнад, Жак Морель, Анрі Лабюсьер, Жан Мартінеллі, Паскаль Маззотта, Лоуренс Різнер, Жерар Ернандес \n\n",
  'description': "Не вірячи в наявність чарівного зілля, яке, згідно з повір'ями, і допомагає галлам залишатися нескореними, Цезар вирішує піти на крайні заходи. Згадавши, про 12 подвигів Геракла він вирішує доручити виконати галлам 12 таких же неймовірно складних завдань...",
  'src': 'http://fs0.moviestape.net/show.php?name=cartoons/Les.douze.travaux.d.Asterix.mp4'}]
    """
    movies = []
    for member in soup.find_all('img'):
        movie = {}
        movie['img'] = member['src']

        movie['title'] = member['title']
        try:
            movie['detail_href'] = member.parent['href']
        except KeyError:
            continue

        movie.update(get_movie_details(movie['detail_href']))
        for key in ['img']:
            if not movie[key].startswith('http'):
                movie[key] = url_root + movie[key]

        movies.append(movie)
    return movies


def movies(url):
    """
    recognize movies page types list or icon, and call function
    TODO: move to decorator
    :param url:
    :param page:
    :return: list
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    movies_list = soup.find('div', id='dle-content')
    if movies_list.find('div', class_='bnewmovie') is None:
        log('class_=\'bnewmovie\' is None', xbmc.LOGERROR)
        return get_movies_list(movies_list)
    else:
        log('[movistape]' + 'class_=\'bnewmovie\' is NOT None', xbmc.LOGERROR)
        return get_movies_icons(movies_list)

