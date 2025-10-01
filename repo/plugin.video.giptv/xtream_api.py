import requests

# --- Global Configuration (Set by the main Kodi script) ---
# These variables will hold the credentials read from config.py.
SERVER = ""
USERNAME = ""
PASSWORD = ""

LIVE_TYPE = "live" # Standard API key for Live TV
VOD_TYPE = "vod"   # Standard API key for Movies
SERIES_TYPE = "series" # Standard API key for Series

# Required User-Agent to mimic a browser, avoiding server blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'
}

# --- Core API Calls ---

def authenticate():
    """Authenticates user credentials and returns the JSON response."""
    url = get_authenticate_URL()
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Xtream API Authentication Error: {e}")
        return None

def categories(streamType):
    """Fetches categories for Live, VOD, or Series streams."""
    if streamType == LIVE_TYPE:
        url = get_live_categories_URL()
    elif streamType == VOD_TYPE:
        url = get_vod_cat_URL()
    elif streamType == SERIES_TYPE:
        url = get_series_cat_URL()
    else:
        return None

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Xtream API Category Fetch Error for {streamType}: {e}")
        return None

def streams_by_category(streamType, category_id):
    """Fetches streams within a specific category."""
    if streamType == LIVE_TYPE:
        url = get_live_streams_URL_by_category(category_id)
    elif streamType == VOD_TYPE:
        url = get_vod_streams_URL_by_category(category_id)
    elif streamType == SERIES_TYPE:
        url = get_series_URL_by_category(category_id)
    else:
        return None

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Xtream API Stream Fetch Error for {streamType}: {e}")
        return None

# --- Stream URL Builder ---

def build_stream_url(stream_id, stream_type, container_extension="ts"):
    """
    Builds the final playable URL for a stream based on the Xtream Codes format.
    Example: http://vpn.shdsdb.xyz/live/8c7023e3bb/5ee8fe21ee/streamID.ts
    """
    
    # Determine the API path segment ('live', 'movie', or 'series')
    api_path_map = {
        'live': 'live',
        'movie': 'movie',
        'series': 'series'
    }
    api_path = api_path_map.get(stream_type.lower())
    
    if not api_path:
        # Fallback if stream_type is unexpected
        return None

    # Construct the URL
    full_url = '{}/{}/{}/{}/{}.{}'.format(
        SERVER.rstrip('/'),
        api_path,
        USERNAME,
        PASSWORD,
        stream_id,
        container_extension
    )
    return full_url


# --- URL-builder methods (using /player_api.php) ---
# These generate the request URLs for the server.

def get_authenticate_URL():
    URL = '%s/player_api.php?username=%s&password=%s' % (SERVER, USERNAME, PASSWORD)
    return URL

def get_live_categories_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (SERVER, USERNAME, PASSWORD, 'get_live_categories')
    return URL

def get_live_streams_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (SERVER, USERNAME, PASSWORD, 'get_live_streams', category_id)
    return URL

def get_vod_cat_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (SERVER, USERNAME, PASSWORD, 'get_vod_categories')
    return URL

def get_vod_streams_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (SERVER, USERNAME, PASSWORD, 'get_vod_streams', category_id)
    return URL

def get_series_cat_URL():
    URL = '%s/player_api.php?username=%s&password=%s&action=%s' % (SERVER, USERNAME, PASSWORD, 'get_series_categories')
    return URL

def get_series_URL_by_category(category_id):
    URL = '%s/player_api.php?username=%s&password=%s&action=%s&category_id=%s' % (SERVER, USERNAME, PASSWORD, 'get_series', category_id)
    return URL
