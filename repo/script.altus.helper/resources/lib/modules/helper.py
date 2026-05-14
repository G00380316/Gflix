import xbmc, xbmcgui, xbmcvfs, xbmcaddon
import json
import os
import hashlib
import urllib.request as urllib
from .config import RATINGS_DATABASE_PATH
from .search_utils import SEARCH_DATABASE_PATH

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_DATA_PATH = xbmcvfs.translatePath(
    os.path.join("special://profile/addon_data/", ADDON_ID)
)
ADDON_DATA_IMG_PATH = os.path.join(ADDON_DATA_PATH, "image_cache")
ADDON_DATA_IMG_TEMP_PATH = os.path.join(ADDON_DATA_PATH, "image_cache/temp")
BLUR_PATH = os.path.join(ADDON_DATA_PATH, "blur_cache")
COLOR_CACHE_FILE = os.path.join(ADDON_DATA_PATH, "color_cache.json")


def md5hash(value):
    value = str(value).encode()
    return hashlib.md5(value).hexdigest()


def touch_file(filepath):
    os.utime(filepath, None)


def url_unquote(string):
    return urllib.unquote(string)


def winprop(key, value=None, clear=False, window_id=10000):
    window = xbmcgui.Window(window_id)

    if clear:
        window.clearProperty(key.replace(".json", "").replace(".bool", ""))

    elif value is not None:
        if key.endswith(".json"):
            key = key.replace(".json", "")
            value = json.dumps(value)

        elif key.endswith(".bool"):
            key = key.replace(".bool", "")
            value = "true" if value else "false"

        window.setProperty(key, value)

    else:
        result = window.getProperty(key.replace(".json", "").replace(".bool", ""))

        if result:
            if key.endswith(".json"):
                result = json.loads(result)
            elif key.endswith(".bool"):
                result = result in ("true", "1")

        return result


def get_directory_size(path):
    """Helper function to calculate directory size recursively"""
    dir_size = 0
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            dir_size += os.path.getsize(full_path)
        elif os.path.isdir(full_path):
            dir_size += get_directory_size(full_path)
    return dir_size


def calculate_cache_size():
    """Calculate sizes for color cache, image cache, blur cache, and ratings database separately and combined"""
    color_cache_size = 0
    image_cache_size = 0
    blur_cache_size = 0
    ratings_db_size = 0

    # Calculate color cache size
    if os.path.exists(COLOR_CACHE_FILE):
        color_cache_size = os.path.getsize(COLOR_CACHE_FILE)
        color_cache_mb = color_cache_size / (1024 * 1024)
        xbmc.executebuiltin(f"Skin.SetString(ColorCacheSize,{color_cache_mb:.2f} MB)")

    # Calculate image cache size
    if os.path.exists(ADDON_DATA_IMG_PATH):
        logo_cache_size = get_directory_size(ADDON_DATA_IMG_PATH)
        logo_cache_mb = logo_cache_size / (1024 * 1024)
        xbmc.executebuiltin(f"Skin.SetString(LogoCacheSize,{logo_cache_mb:.2f} MB)")

    # Calculate blur cache size
    if os.path.exists(BLUR_PATH):
        blur_cache_size = get_directory_size(BLUR_PATH)
        blur_cache_mb = blur_cache_size / (1024 * 1024)
        xbmc.executebuiltin(f"Skin.SetString(BlurCacheSize,{blur_cache_mb:.2f} MB)")

    # Calculate ratings database size
    if os.path.exists(RATINGS_DATABASE_PATH):
        ratings_db_size = os.path.getsize(RATINGS_DATABASE_PATH)
        ratings_db_mb = ratings_db_size / (1024 * 1024)
        xbmc.executebuiltin(
            f"Skin.SetString(RatingsDatabaseSize,{ratings_db_mb:.2f} MB)"
        )

    # Calculate ratings database size
    if os.path.exists(SEARCH_DATABASE_PATH):
        search_history_db_size = os.path.getsize(SEARCH_DATABASE_PATH)
        search_history_db_mb = search_history_db_size / (1024 * 1024)
        xbmc.executebuiltin(
            f"Skin.SetString(SearchHistoryDatabaseSize,{search_history_db_mb:.2f} MB)"
        )

    # Calculate and set total cache size
    total_size_mb = (color_cache_size + logo_cache_size + blur_cache_size) / (
        1024 * 1024
    )
    xbmc.executebuiltin(f"Skin.SetString(TotalImageCacheSize,{total_size_mb:.2f} MB)")

    return (
        color_cache_mb,
        logo_cache_mb,
        blur_cache_mb,
        ratings_db_mb,
        search_history_db_mb,
        total_size_mb,
    )


def clear_color_cache(delete=False):
    """Clear only the color cache"""
    if not delete:
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Altus", "Are you sure you want to clear the color cache?"):
            delete = True

    if delete:
        try:
            if os.path.exists(COLOR_CACHE_FILE):
                with open(COLOR_CACHE_FILE, "w") as f:
                    json.dump({}, f)
                xbmc.log("Successfully cleared color cache", 2)
                calculate_cache_size()
                return True
        except Exception as e:
            xbmc.log(f"Error clearing color cache: {str(e)}", 2)
            dialog = xbmcgui.Dialog()
            dialog.notification(
                "Altus", "Error clearing color cache", xbmcgui.NOTIFICATION_ERROR
            )
            return False

    return True


def clear_logo_cache(delete=False):
    """Clear only the image cache"""
    if not delete:
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Altus", "Are you sure you want to clear the logo cache?"):
            delete = True

    if delete:
        try:
            if os.path.exists(ADDON_DATA_IMG_PATH):

                def clear_directory(path):
                    for item in os.listdir(path):
                        full_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(full_path):
                                os.remove(full_path)
                            else:
                                clear_directory(full_path)
                        except Exception as e:
                            xbmc.log(f"Error removing {full_path}: {str(e)}", 2)

                clear_directory(ADDON_DATA_IMG_PATH)
                xbmc.log("Successfully cleared logo cache", 2)
                calculate_cache_size()
                return True
        except Exception as e:
            xbmc.log(f"Error clearing logo cache: {str(e)}", 2)
            dialog = xbmcgui.Dialog()
            dialog.notification(
                "Altus", "Error clearing logo cache", xbmcgui.NOTIFICATION_ERROR
            )
            return False

    return True


def clear_blur_cache(delete=False):
    """Clear only the blur cache"""
    if not delete:
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Altus", "Are you sure you want to clear the blur cache?"):
            delete = True

    if delete:
        try:
            if os.path.exists(BLUR_PATH):

                def clear_directory(path):
                    for item in os.listdir(path):
                        full_path = os.path.join(path, item)
                        try:
                            if os.path.isfile(full_path):
                                os.remove(full_path)
                            else:
                                clear_directory(full_path)
                        except Exception as e:
                            xbmc.log(f"Error removing {full_path}: {str(e)}", 2)

                clear_directory(BLUR_PATH)
                xbmc.log("Successfully cleared blur cache", 2)
                calculate_cache_size()
                return True
        except Exception as e:
            xbmc.log(f"Error clearing blur cache: {str(e)}", 2)
            dialog = xbmcgui.Dialog()
            dialog.notification(
                "Altus", "Error clearing blur cache", xbmcgui.NOTIFICATION_ERROR
            )
            return False

    return True


def clear_all_image_caches(clear=False):
    """Clear both color cache and image cache"""
    if not clear:
        dialog = xbmcgui.Dialog()
        if dialog.yesno("Altus", "Are you sure you want to clear all caches?"):
            clear = True

    if clear:
        color_success = clear_color_cache(True)
        image_success = clear_logo_cache(True)
        blur_success = clear_blur_cache(True)

        if color_success and image_success and blur_success:
            calculate_cache_size()
            return True
        else:
            return False

    return True
