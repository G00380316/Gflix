import xbmc, xbmcvfs
import json
import os

# Localized string ID → view control ID
VIEW_IDS = {
    '535': '50', '310981': '51', '31099': '52', '31100': '53',
    '31101': '54', '311012': '55', '31107': '56', '311024': '57',
    '311022': '500', '311023': '501',
}

def get_content_type():
    if xbmc.getCondVisibility('Container.Content(episodes)'):
        if xbmc.getCondVisibility('String.StartsWith(Container.PluginCategory,Season)'):
            return 'episodes.inside'
        return 'episodes.outside'
    content = xbmc.getInfoLabel('Container.Content')
    return '' if not content else content

VIEW_PREFERENCES_PATH = os.path.join(
    xbmcvfs.translatePath("special://profile/addon_data/script.altus.helper/"),
    "view_preferences.json"
)

def load_view_preferences():
    if os.path.exists(VIEW_PREFERENCES_PATH):
        try:
            with open(VIEW_PREFERENCES_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def get_current_view_id():
    view_mode = xbmc.getInfoLabel('Container.Viewmode')
    for localized_id, view_id in VIEW_IDS.items():
        if xbmc.getLocalizedString(int(localized_id)) == view_mode:
            return view_id
    return ''

def save_view():
    plugin_name = xbmc.getInfoLabel('Container.PluginName') or ''
    addon_key = plugin_name if plugin_name else '__library__'
    content_type = get_content_type()
    view_mode = xbmc.getInfoLabel('Container.Viewmode') or ''
    view_id = get_current_view_id() or ''
    if content_type is None or not view_mode or not view_id:
        return
    # Set skin string immediately for instant feedback
    xbmc.executebuiltin(f'Skin.SetString(Skin.ForcedView.{content_type},{view_mode})')
    # Persist to JSON for per-addon recall
    prefs = load_view_preferences()
    if addon_key not in prefs:
        prefs[addon_key] = {}
    prefs[addon_key][content_type] = {'label': view_mode, 'viewid': view_id}
    try:
        with open(VIEW_PREFERENCES_PATH, 'w') as f:
            json.dump(prefs, f, indent=2)
    except IOError:
        pass
