import xbmc

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
