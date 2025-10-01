import sys
# Python 2/3 compatibility for URL parsing
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import xbmcgui
import xbmcplugin
import xbmcaddon

# Import the core API module
import xtream_api 
# import config # not needed for credentials handling here

# Get the plugin handle
PLUGIN_HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon()

# --- Configuration Setup ---
def setup_api_config():
    """Sets API credentials from Kodi settings."""
    try:
        # Get settings from Kodi config
        server = ADDON.getSetting('server').rstrip()
        username = ADDON.getSetting('username').rstrip()
        password = ADDON.getSetting('password').rstrip()
        
        if not server or not username or not password:
            # Open the settings dialog automatically
            ADDON.openSettings()
            return False

        # Set the global variables in the API module
        xtream_api.SERVER = server.rstrip('/')
        xtream_api.USERNAME = username
        xtream_api.PASSWORD = password
        return True
    except Exception as e:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), f"Configuration Setup Error: {e}")
        ADDON.openSettings()
        return False


# --- Listing Functions ---

def list_categories(stream_type):
    """
    Lists the top-level categories (e.g., Sports, News) for a given stream type.
    """
    if not setup_api_config():
        return

    # 1. Authenticate and check status
    auth_data = xtream_api.authenticate()
    if not auth_data or auth_data.get('user_info', {}).get('auth') != 1:
        error_msg = auth_data.get('user_info', {}).get('message', "Authentication Failed or Account Expired.")
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), error_msg)
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return

    # 2. Get categories
    category_list = xtream_api.categories(stream_type)

    if not category_list:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), "Failed to retrieve categories or list is empty.")
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return

    for category in category_list:
        name = category.get('category_name', 'Unknown Category')
        category_id = category.get('category_id')
        
        # Build the URL to call list_streams when this item is selected
        url = sys.argv[0] + '?' + urlparse.urlencode({
            'mode': 'list_streams',
            'stream_type': stream_type,
            'category_id': category_id,
            'name': name
        })
        
        # Add the directory item to Kodi
        list_item = xbmcgui.ListItem(label=name)
        list_item.setArt({'icon': 'DefaultFolder.png', 'thumb': 'DefaultFolder.png'})
        
        xbmcplugin.addDirectoryItem(
            handle=PLUGIN_HANDLE,
            url=url,
            listitem=list_item,
            isFolder=True
        )

    # Finish listing
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


def list_streams(stream_type, category_id, name):
    """
    Lists the actual streams (channels, movies, or series) within a selected category.
    """
    if not setup_api_config():
        return

    # Fetch streams for the given category ID
    stream_list = xtream_api.streams_by_category(stream_type, category_id)

    if not stream_list:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), f"No streams found in {name}.")
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)
        return

    for stream in stream_list:
        stream_name = stream.get('name', 'Unknown Stream')
        stream_id = stream.get('stream_id')
        
        # The API response typically uses 'stream_type' for live, 'movie', or 'series'
        stream_type_key = stream.get('stream_type', stream_type)
        
        # Get the appropriate container extension (usually 'ts' for live)
        ext = stream.get('container_extension', 'ts')
        
        # Build the final playable URL using the API format
        play_url = xtream_api.build_stream_url(
            stream_id=stream_id,
            stream_type=stream_type_key,
            container_extension=ext
        )
        
        if play_url:
            # Build the URL for playback
            url = sys.argv[0] + '?' + urlparse.urlencode({
                'mode': 'play_stream',
                'url': play_url,
                'name': stream_name
            })
            
            # Create list item
            list_item = xbmcgui.ListItem(label=stream_name)
            list_item.setProperty('IsPlayable', 'true') # Required to tell Kodi this item is a video
            
            # Set stream icon/thumbnail
            stream_icon = stream.get('stream_icon', '')
            if stream_icon:
                list_item.setArt({'thumb': stream_icon, 'icon': stream_icon})
            else:
                list_item.setArt({'icon': 'DefaultVideo.png', 'thumb': 'DefaultVideo.png'})

            xbmcplugin.addDirectoryItem(
                handle=PLUGIN_HANDLE,
                url=url,
                listitem=list_item,
                isFolder=False # This is a playable item, not a folder
            )
        
    # Finish listing
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


def play_stream(url, name):
    """
    Plays the final stream URL in Kodi.
    """
    play_item = xbmcgui.ListItem(path=url)
    play_item.setLabel(name)
    play_item.setProperty('IsPlayable', 'true')
    # Set the stream as the resolved URL for Kodi to begin playback
    xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, play_item)


# --- Router ---

def handle_routing(url_params):
    """
    Routes the request based on the 'mode' parameter extracted from the URL.
    """
    # Parameters come in as lists, so we use [0] to get the value
    mode = url_params.get('mode', [None])[0]
    
    if mode == 'list_streams':
        stream_type = url_params.get('stream_type', [''])[0]
        category_id = url_params.get('category_id', [''])[0]
        name = url_params.get('name', [''])[0]
        list_streams(stream_type, category_id, name)
    elif mode == 'play_stream':
        url = url_params.get('url', [''])[0]
        name = url_params.get('name', [''])[0]
        play_stream(url, name)
    elif mode is None:
        # Default entry point: Start by listing Live TV categories
        list_categories(xtream_api.LIVE_TYPE)
    else:
        xbmcgui.Dialog().ok(ADDON.getAddonInfo('name'), f"Unknown mode: {mode}")


# --- Main Execution ---

if __name__ == '__main__':
    # sys.argv[2] contains the URL parameters (the query string)
    # [1:] is used to remove the leading '?'
    params = urlparse.parse_qs(sys.argv[2][1:])
    handle_routing(params)