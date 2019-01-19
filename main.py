# -*- coding: utf-8 -*-
# Module: default
# Author: Viktor.Tsymbalyuk@gmail.com
# Created on: 2018-08-27
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
# Based on: https://github.com/romanvm/plugin.video.example/blob/master/main.py
# https://github.com/romanvm/plugin.video.example

import sys
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui, xbmc
import xbmcplugin
import resources.lib.movistape as movistape
from resources.lib.common import log
import requests
import re

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# base_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
# addon_handle = int(sys.argv[1])

cat = movistape.get_categories()
url_root = 'http://moviestape.net'


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.
    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    # args = urlparse.parse_qs(sys.argv[2][1:])
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    xbmcplugin.setPluginCategory(_handle, 'MovieStape')
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories; remove first 2 items from 'cat'
    categories = [i[0]['name'] for i in cat[2:]]
    for num, category in enumerate(categories):
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing', category=str(num))
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_subcategories(num_category):
    """
    Create the list of video categories in the Kodi interface.
    """
    category = int(num_category)
    subcategory = [i['name'] for i in cat[2:][category]]
    xbmcplugin.setPluginCategory(_handle, subcategory[0])
    subcategory[0] = 'ALL'
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories; remove first 2 items from 'cat'

    for num, _category in enumerate(subcategory):
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=_category)
        list_item.setInfo('video', {'title': _category,
                                    'genre': _category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='listing_video', category=num_category, subcategory=str(num), page='1')
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def list_videos(category_num, subcategory_num, page='1'):
    """
    Create the list of playable videos in the Kodi interface.
    :param category_num: Category number in list
    :param subcategory_num: dict num in subcategory list
    :param page: page number of videos pages
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    category_dict = cat[2:][int(category_num)][0]
    subcategory_dict = cat[2:][int(category_num)][int(subcategory_num)]
    category = category_dict['name'] + ' --- ' + subcategory_dict['name']
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.

    if page == '1':
        url_page = subcategory_dict['href']
    else:
        url_page = subcategory_dict['href'] + 'page/' + page + '/'

    log('url= ' + url_page + '; subcategory= ' + category, xbmc.LOGERROR)
    videos = movistape.movies(url_page)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['title'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['title'],
                                    # 'genre': video['genre'],
                                    'plot': video['description'],
                                    'genre': video['meta'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['img'], 'fanart': video['img']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['src'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    # next page
    page = str(int(page) + 1)
    list_item = xbmcgui.ListItem(label='Next')
    list_item.setInfo('video', {'title': 'Next',
                                'genre': 'next page... ' + page,
                                'mediatype': 'video'})
    url = get_url(action='listing_video', category=category_num, subcategory=subcategory_num, page=page)
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    get url on video, and route it for playing
    :param path: path to js script where final url located
    :return:
    """
    log('path to video= ' + path, xbmc.LOGERROR)
    resp_movie_direct = requests.get(path)
    reg_movie = re.compile('file:\"(.+?)\"')

    url = reg_movie.findall(resp_movie_direct.text)[0]
    play_item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring
    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_subcategories(params['category'])
        elif params['action'] == 'listing_video':
            list_videos(params['category'], params['subcategory'], params['page'])
        elif params['action'] == 'play':
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
