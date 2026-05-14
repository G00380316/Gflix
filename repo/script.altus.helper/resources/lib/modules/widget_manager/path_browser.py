# -*- coding: utf-8 -*-
"""
Browsable path selector for the widget manager.
Supports video/music/program addons, library nodes, PVR, playlists, sources,
games, pictures, favourites, and more.
"""
import json
import re
import xbmc, xbmcgui

_LOCALIZE_RE = re.compile(r"\$LOCALIZE\[(\d+)\]")


def _resolve_localize(text):
    """Resolve $LOCALIZE[N] tokens to their localized strings."""
    return _LOCALIZE_RE.sub(lambda m: xbmc.getLocalizedString(int(m.group(1))), text)


dialog = xbmcgui.Dialog()
ListItem = xbmcgui.ListItem

# ── Root categories ──

ROOT_CATEGORIES = [
    ("$LOCALIZE[24001]", "__addons__", "videos"),
    ("$LOCALIZE[15100]", "__library__", "videos"),
    ("PVR", "__pvr__", "videos"),
    ("$LOCALIZE[136]", "__playlists__", "videos"),
    ("$LOCALIZE[20094]", "__sources__", "videos"),
    ("$LOCALIZE[10134]", "favourites://", "videos"),
    ("$LOCALIZE[15016]", "__games__", "games"),
    ("$LOCALIZE[8]", "__weather__", "videos"),
]

# ── Addon sub-menus ──

ADDON_NODES = [
    ("$LOCALIZE[31148]", "addons://", "addonbrowser"),
    ("$LOCALIZE[1037]", "addons://sources/video", "videos"),
    ("$LOCALIZE[1038]", "addons://sources/music", "music"),
    ("$LOCALIZE[1043]", "addons://sources/executable", "programs"),
    ("$LOCALIZE[1039]", "addons://sources/image", "pictures"),
    ("$LOCALIZE[35049]", "addons://sources/game", "games"),
    ("$LOCALIZE[20244]", "androidapp://sources/apps/", "programs"),
]

# ── Library sub-menus ──

LIBRARY_NODES = [
    ("$LOCALIZE[14236]", "__video_library__", "videos"),
    ("$LOCALIZE[14237]", "__music_library__", "music"),
    ("$LOCALIZE[1]", "__pictures__", "pictures"),
]

VIDEO_LIBRARY_NODES = [
    ("$LOCALIZE[342]", "__video_movies__", "videos"),
    ("$LOCALIZE[20343]", "__video_tvshows__", "videos"),
    ("$LOCALIZE[20389]", "__video_musicvideos__", "videos"),
    ("$LOCALIZE[31148]", "library://video/"),
]

VIDEO_MOVIES_NODES = [
    ("$LOCALIZE[31148]", "library://video/movies/"),
    ("$LOCALIZE[10024]", "videodb://movies/titles/"),
    ("$LOCALIZE[135]", "videodb://movies/genres/"),
    ("$LOCALIZE[652]", "videodb://movies/years/"),
    ("$LOCALIZE[344]", "videodb://movies/actors/"),
    ("$LOCALIZE[20348]", "videodb://movies/directors/"),
    ("$LOCALIZE[20388]", "videodb://movies/studios/"),
    ("$LOCALIZE[20451]", "videodb://movies/countries/"),
    ("$LOCALIZE[31075]", "videodb://movies/sets/"),
    ("$LOCALIZE[20459]", "videodb://movies/tags/"),
    ("$LOCALIZE[20386]", "videodb://recentlyaddedmovies/"),
    ("$LOCALIZE[31010]", "videodb://inprogressmovies/"),
]

VIDEO_TVSHOWS_NODES = [
    ("$LOCALIZE[31148]", "library://video/tvshows/"),
    ("$LOCALIZE[10024]", "videodb://tvshows/titles/"),
    ("$LOCALIZE[135]", "videodb://tvshows/genres/"),
    ("$LOCALIZE[652]", "videodb://tvshows/years/"),
    ("$LOCALIZE[344]", "videodb://tvshows/actors/"),
    ("$LOCALIZE[20388]", "videodb://tvshows/studios/"),
    ("$LOCALIZE[20459]", "videodb://tvshows/tags/"),
    ("$LOCALIZE[20387]", "videodb://recentlyaddedepisodes/"),
    ("$LOCALIZE[626]", "videodb://inprogresstvshows/"),
]

VIDEO_MUSICVIDEOS_NODES = [
    ("$LOCALIZE[31148]", "library://video/musicvideos/"),
    ("$LOCALIZE[10024]", "videodb://musicvideos/titles/"),
    ("$LOCALIZE[135]", "videodb://musicvideos/genres/"),
    ("$LOCALIZE[652]", "videodb://musicvideos/years/"),
    ("$LOCALIZE[133]", "videodb://musicvideos/artists/"),
    ("$LOCALIZE[132]", "videodb://musicvideos/albums/"),
    ("$LOCALIZE[20388]", "videodb://musicvideos/studios/"),
    ("$LOCALIZE[20459]", "videodb://musicvideos/tags/"),
    ("$LOCALIZE[20390]", "videodb://recentlyaddedmusicvideos/"),
]

MUSIC_LIBRARY_NODES = [
    ("$LOCALIZE[133]", "musicdb://artists/"),
    ("$LOCALIZE[132]", "musicdb://albums/"),
    ("$LOCALIZE[134]", "musicdb://songs/"),
    ("$LOCALIZE[135]", "musicdb://genres/"),
    ("$LOCALIZE[652]", "musicdb://years/"),
    ("$LOCALIZE[359]", "musicdb://recentlyaddedalbums/"),
    ("$LOCALIZE[517]", "musicdb://recentlyplayedalbums/"),
    ("Recently Played Songs", "musicdb://recentlyplayedsongs/"),
    ("$LOCALIZE[10504]", "musicdb://top100/songs/"),
    ("$LOCALIZE[10505]", "musicdb://top100/albums/"),
    ("$LOCALIZE[521]", "musicdb://compilations/"),
    ("$LOCALIZE[31148]", "library://music/"),
]

# ── PVR sub-menus ──

PVR_NODES = [
    ("$LOCALIZE[19020]", "__pvr_tv__", "videos"),
    ("$LOCALIZE[19021]", "__pvr_radio__", "music"),
]

PVR_TV_NODES = [
    ("$LOCALIZE[31148]", "pvr://tv/", "videos"),
    ("$LOCALIZE[31016]", "pvr://channels/tv/*?view=lastplayed", "tvchannels"),
    ("$LOCALIZE[10700]", "pvr://channels/tv/", "tvchannels"),
    ("$LOCALIZE[31015]", "pvr://recordings/tv/active?view=flat", "tvrecordings"),
    ("$LOCALIZE[19040]", "pvr://timers/tv/timers/?view=hidedisabled", "tvtimers"),
    ("$LOCALIZE[19173]", "pvr://channels/tv", "tvguide"),
    ("$LOCALIZE[19337]", "pvr://search/tv/savedsearches", "tvsearch"),
    ("$LOCALIZE[855]", "pvr://channels/tv/*?view=dateadded", "tvchannels"),
]

PVR_RADIO_NODES = [
    ("$LOCALIZE[31148]", "pvr://radio/", "music"),
    ("$LOCALIZE[31018]", "pvr://channels/radio/*?view=lastplayed", "radiochannels"),
    ("$LOCALIZE[10705]", "pvr://channels/radio/", "radiochannels"),
    ("$LOCALIZE[31015]", "pvr://recordings/radio/active?view=flat", "radiorecordings"),
    ("$LOCALIZE[19040]", "pvr://timers/radio/timers/?view=hidedisabled", "radiotimers"),
    ("$LOCALIZE[19174]", "pvr://channels/radio", "radioguide"),
    ("$LOCALIZE[19337]", "pvr://search/radio/savedsearches", "radiosearch"),
    ("$LOCALIZE[855]", "pvr://channels/radio/*?view=dateadded", "radiochannels"),
]

# ── Pictures sub-menu ──

PICTURES_NODES = [
    ("$LOCALIZE[20094]", "sources://pictures/"),
]

# ── Playlists sub-menu ──

PLAYLIST_NODES = [
    ("$LOCALIZE[20012]", "special://profile/playlists/video/", "videos"),
    ("$LOCALIZE[20011]", "special://profile/playlists/music/", "music"),
    ("$LOCALIZE[166] $LOCALIZE[136]", "__skin_playlists__", "videos"),
]

# ── Sources sub-menu ──

SOURCES_NODES = [
    ("$LOCALIZE[157] $LOCALIZE[39031]", "sources://video/", "videos"),
    ("$LOCALIZE[2] $LOCALIZE[39031]", "sources://music/", "music"),
    ("Picture Sources", "sources://pictures/", "pictures"),
]

# ── Games sub-menu ──

GAMES_NODES = [
    ("$LOCALIZE[35049]", "addons://sources/game/"),
]

# ── Skin playlists ──

SKIN_PLAYLIST_NODES = [
    ("$LOCALIZE[31012]", "special://skin/playlists/random_albums.xsp"),
    ("$LOCALIZE[31013]", "special://skin/playlists/random_artists.xsp"),
    ("$LOCALIZE[31014]", "special://skin/playlists/unplayed_albums.xsp"),
    ("$LOCALIZE[31011]", "special://skin/playlists/mostplayed_albums.xsp"),
    ("$LOCALIZE[31151]", "special://skin/playlists/unwatched_musicvideos.xsp"),
    (
        "$LOCALIZE[31013]",
        "special://skin/playlists/random_musicvideo_artists.xsp",
    ),
    ("$LOCALIZE[31152]", "special://skin/playlists/random_musicvideos.xsp"),
]

# ── Submenu routing ──

_SUBMENU_MAP = {
    "__addons__": ADDON_NODES,
    "__library__": LIBRARY_NODES,
    "__pvr__": PVR_NODES,
    "__playlists__": PLAYLIST_NODES,
    "__sources__": SOURCES_NODES,
    "__video_library__": VIDEO_LIBRARY_NODES,
    "__video_movies__": VIDEO_MOVIES_NODES,
    "__video_tvshows__": VIDEO_TVSHOWS_NODES,
    "__video_musicvideos__": VIDEO_MUSICVIDEOS_NODES,
    "__music_library__": MUSIC_LIBRARY_NODES,
    "__pvr_tv__": PVR_TV_NODES,
    "__pvr_radio__": PVR_RADIO_NODES,
    "__pictures__": PICTURES_NODES,
    "__games__": GAMES_NODES,
    "__skin_playlists__": SKIN_PLAYLIST_NODES,
}

# ── Window map for onclick construction ──

WINDOW_MAP = {
    "videos": "Videos",
    "music": "Music",
    "programs": "Programs",
    "pictures": "Pictures",
    "games": "Games",
    "files": "Files",
    "addons": "AddonBrowser",
    "addonbrowser": "AddonBrowser",
    "tvchannels": "TVChannels",
    "tvguide": "TVGuide",
    "tvrecordings": "TVRecordings",
    "tvtimers": "TVTimers",
    "tvsearch": "TVChannels",
    "radiochannels": "RadioChannels",
    "radioguide": "RadioChannels",
    "radiorecordings": "RadioRecordings",
    "radiotimers": "RadioTimers",
    "radiosearch": "RadioChannels",
}

# Special onclick overrides for paths that need non-standard window targets
_ONCLICK_OVERRIDES = {
    "pvr://channels/tv": "ActivateWindow(TVGuide)",
    "pvr://channels/radio": "ActivateWindow(RadioChannels)",
    "pvr://channels/tv/": "ActivateWindow(TVChannels)",
    "pvr://channels/radio/": "ActivateWindow(RadioChannels)",
    "favourites://": "ActivateWindow(favouritesbrowser)",
    "sources://pictures/": "ActivateWindow(Pictures)",
    "library://music/": "ActivateWindow(Music,root,return)",
    "library://video/": "ActivateWindow(Videos,root)",
}


def browse(include_weather=True, allow_multi=True, multi_heading=None):
    """
    Main entry point. Shows root category picker, then recursive path browser.
    Returns dict {"label", "path", "target", "display_type"} or None if cancelled.
    display_type is auto-assigned when possible, None when user should be prompted.

    Args:
        include_weather: If False, Weather is excluded from the root categories.
            Pass False when browsing for widget paths (Weather widgets are hardcoded).
    """
    categories = (
        ROOT_CATEGORIES
        if include_weather
        else [c for c in ROOT_CATEGORIES if c[1] != "__weather__"]
    )
    idx = dialog.select(
        "Choose content source", [_resolve_localize(c[0]) for c in categories]
    )
    if idx < 0:
        return None
    label, path, target = categories[idx]
    label = _resolve_localize(label)
    # Weather is a special section — no browsable path, hardcoded widgets in skin XML
    if path == "__weather__":
        return {"label": "Weather", "path": "", "target": "", "display_type": ""}
    nodes = _SUBMENU_MAP.get(path)
    if nodes is not None:
        result = _browse_submenu(
            nodes, target, allow_multi=allow_multi, multi_heading=multi_heading
        )
    else:
        result = _browse_path(
            path=path,
            label=label,
            allow_multi=allow_multi,
            multi_heading=multi_heading,
        )
        if result and "multi" not in result:
            result["target"] = target
    if result and "multi" in result:
        for item in result["multi"]:
            if not item.get("target"):
                item["target"] = target
            item["display_type"] = _auto_display_type(item["path"], item["target"])
        return result
    if result:
        result["display_type"] = _auto_display_type(result["path"], result["target"])
    return result


def build_onclick(path, target):
    """Build an onclick action string from a path and target.

    Checks for special overrides first (PVR guide, favourites, etc.),
    then falls back to ActivateWindow(Window,path,return).
    """
    # Check for exact match overrides
    override = _ONCLICK_OVERRIDES.get(path)
    if override:
        return override
    # Check prefix-based overrides for PVR paths
    if path.startswith("pvr://"):
        if "channels/tv/" in path:
            return "ActivateWindow(TVChannels)"
        if "channels/radio" in path:
            return "ActivateWindow(RadioChannels)"
        if "recordings/tv" in path:
            return "ActivateWindow(TVRecordings)"
        if "recordings/radio" in path:
            return "ActivateWindow(RadioRecordings)"
        if "timers/tv" in path:
            return "ActivateWindow(TVTimers)"
        if "timers/radio" in path:
            return "ActivateWindow(RadioTimers)"
        if "search/tv" in path:
            return "ActivateWindow(TVSearch)"
        if "search/radio" in path:
            return "ActivateWindow(RadioChannels)"
        # Generic PVR fallback
        return "ActivateWindow(TVChannels)"
    if path.startswith("addons://"):
        return "ActivateWindow(1100,%s,return)" % path
    if path.startswith("androidapp://"):
        return "StartAndroidActivity(%s)" % path
    window = WINDOW_MAP.get(target, "Videos")
    return "ActivateWindow(%s,%s,return)" % (window, path)


# ── Internal helpers ──


def _auto_display_type(path, target):
    """Determine display type from path and target.

    Returns an internal display type name when auto-assignable,
    or None when the user should be prompted (video content).
    """
    # PVR paths
    if path.startswith("pvr://"):
        # Top-level category browsers
        if path in ("pvr://tv/", "pvr://radio/"):
            return "WidgetListCategory"
        # Channel groups (for guide-style display)
        if path in ("pvr://channels/tv", "pvr://channels/radio"):
            return "WidgetListSquare"
        # Channels, recordings, timers → PVR layout
        return "WidgetListPVR"
    # Addon root categories → Category Other
    if path == "addons://":
        return "WidgetListCategory"
    # Addon / installed addon paths → Square
    if path.startswith("addons://") or path.startswith("androidapp://"):
        return "WidgetListSquare"
    # Favourites → Square
    if path.startswith("favourites://"):
        return "WidgetListFavourites"
    # Music library content → Square (album/artist artwork is square)
    if path.startswith("musicdb://"):
        return "WidgetListSquare"
    # Music library root → Category Other
    if path == "library://music/" or path.startswith("library://music/"):
        return "WidgetListCategory"
    # Music skin playlists → Square
    if target == "music":
        return "WidgetListSquare"
    # Picture sources → Category Other
    if path.startswith("sources://pictures/") or target == "pictures":
        return "WidgetListCategory"
    # Games → Square
    if target == "games":
        return "WidgetListSquare"
    # Programs → Square
    if target == "programs":
        return "WidgetListSquare"
    # Video library node paths (library://video/*/) → Category Other
    if path.startswith("library://video/"):
        return "WidgetListCategory"
    if path.startswith("sources://video/"):
        return "WidgetListCategory"
    if path.startswith("special://videoplaylists"):
        return "WidgetListCategory"
    # videodb category browsers (genres, studios, years, etc.) → Category Other
    if path.startswith("videodb://"):
        _CAT_SUFFIXES = (
            "genres/",
            "studios/",
            "years/",
            "actors/",
            "directors/",
            "countries/",
            "tags/",
            "artists/",
            "albums/",
        )
        for suffix in _CAT_SUFFIXES:
            if path.endswith(suffix):
                return "WidgetListCategory"
    # Video content (videodb://, plugin://, playlists) → prompt user
    return None


def _browse_submenu(nodes, target, allow_multi=True, multi_heading=None):
    """Show a sub-menu of predefined nodes, then browse or return the selected one."""
    # Leaves are entries that resolve to real widget paths (i.e. NOT nav nodes
    # that lead to another submenu). Multi-select offers picking multiple of
    # these in one go.
    leaves = [n for n in nodes if n[1] not in _SUBMENU_MAP]
    show_multi_btn = allow_multi and len(leaves) >= 2
    if show_multi_btn:
        _set_home_prop(_PROP_ALLOW_MULTI, "true")
    else:
        _clear_home_prop(_PROP_ALLOW_MULTI)
    try:
        idx = dialog.select(
            "Choose category", [_resolve_localize(n[0]) for n in nodes]
        )
        if idx < 0:
            if _get_home_prop(_PROP_DO_MULTI) == "true":
                _clear_home_prop(_PROP_DO_MULTI)
                _clear_home_prop(_PROP_ALLOW_MULTI)
                picked = _multiselect_leaves(leaves, target, heading=multi_heading)
                if not picked:
                    return None
                return {"multi": picked}
            return None
    finally:
        _clear_home_prop(_PROP_ALLOW_MULTI)
    node = nodes[idx]
    label, path = _resolve_localize(node[0]), node[1]
    # 3-tuple nodes have their own target override
    node_target = node[2] if len(node) > 2 else target
    # Check if this node leads to another submenu (multi-level nesting)
    sub_nodes = _SUBMENU_MAP.get(path)
    if sub_nodes is not None:
        return _browse_submenu(
            sub_nodes,
            node_target,
            allow_multi=allow_multi,
            multi_heading=multi_heading,
        )
    # Paths that should be browsed into via _browse_path
    browsable = (
        path.startswith("videodb://")
        or path.startswith("musicdb://")
        or path.startswith("library://")
        or path.startswith("sources://")
        or path.startswith("special://profile/playlists/")
        or path.startswith("addons://sources/")
        or path.startswith("pvr://")
        or path.startswith("plugin://")
        or path.startswith("favourites://")
        or path.startswith("androidapp://")
    )
    if not browsable:
        return {"label": label, "path": path, "thumbnail": "", "target": node_target}
    result = _browse_path(
        path=path,
        label=label,
        allow_multi=allow_multi,
        multi_heading=multi_heading,
    )
    if result:
        result["target"] = node_target
    return result


_HOME_WIN = 10000  # Window(Home) for skin properties
_PROP_ALLOW_MULTI = "altus.pathbrowser.allow_multi"
_PROP_DO_MULTI = "altus.pathbrowser.do_multi"


def _set_home_prop(name, value):
    xbmcgui.Window(_HOME_WIN).setProperty(name, value)


def _get_home_prop(name):
    return xbmcgui.Window(_HOME_WIN).getProperty(name)


def _clear_home_prop(name):
    xbmcgui.Window(_HOME_WIN).clearProperty(name)


def _browse_path(path, label="", thumbnail="", allow_multi=True, multi_heading=None):
    """
    Browse a path via JSON-RPC Files.GetDirectory with a navigation stack.
    Returns dict {"label", "path", "thumbnail"} or None.

    When allow_multi is True, exposes a Multi-select button in the skinned
    DialogSelect via the altus.pathbrowser.allow_multi window property; the
    button sets altus.pathbrowser.do_multi and closes the dialog, which we
    detect and convert to a multi-select pick.
    """
    # Stack of (path, label, thumbnail) for back navigation
    stack = []
    cur_path, cur_label, cur_thumb = path, label, thumbnail
    # Ensure trigger is clean on entry
    _clear_home_prop(_PROP_DO_MULTI)
    _clear_home_prop(_PROP_ALLOW_MULTI)
    try:
        return _browse_path_loop(
            stack, cur_path, cur_label, cur_thumb, allow_multi, multi_heading
        )
    finally:
        _clear_home_prop(_PROP_DO_MULTI)
        _clear_home_prop(_PROP_ALLOW_MULTI)


def _browse_path_loop(stack, cur_path, cur_label, cur_thumb, allow_multi, multi_heading):
    while True:
        _show_busy()
        results = _get_directory(cur_path) or []
        _hide_busy()
        items = []
        is_addon_root = (
            cur_path.startswith("addons://sources/") or cur_path == "addons://"
        )
        # "Use this path" option (skip for addon source roots)
        if not is_addon_root:
            use_label = _clean(cur_label) or cur_path
            li = ListItem(
                "[B]%s[/B]" % use_label,
                "Use as widget path",
                offscreen=True,
            )
            if cur_thumb:
                li.setArt({"icon": cur_thumb})
            li.setProperty(
                "item",
                json.dumps(
                    {"label": cur_label, "path": cur_path, "thumbnail": cur_thumb}
                ),
            )
            items.append(li)
        # Toggle Multi-select button visibility based on whether subfolders exist
        has_dirs = any(
            r.get("filetype") == "directory" and not _is_next_page(r.get("label", ""))
            for r in results
        )
        if allow_multi and has_dirs:
            _set_home_prop(_PROP_ALLOW_MULTI, "true")
        else:
            _clear_home_prop(_PROP_ALLOW_MULTI)
        # Separate directories, file items, and next-page entries
        dirs = []
        next_pages = []
        file_items = []
        for r in results:
            if r.get("filetype") == "directory":
                raw = r.get("label", "")
                if _is_next_page(raw):
                    next_pages.append(r)
                else:
                    dirs.append(r)
            else:
                file_items.append(r)
        # Show directories first (browsable)
        for r in dirs:
            clean = _clean(r["label"])
            li = ListItem("%s" % clean, "Browse path...", offscreen=True)
            if r.get("thumbnail"):
                li.setArt({"icon": r["thumbnail"]})
            li.setProperty(
                "item",
                json.dumps(
                    {
                        "label": r["label"],
                        "path": r["file"],
                        "thumbnail": r.get("thumbnail", ""),
                        "filetype": "directory",
                    }
                ),
            )
            items.append(li)
        # Then show content items (non-browsable)
        for r in file_items:
            clean = _clean(r["label"])
            file_path = r.get("file", "")
            li = ListItem("%s" % clean, file_path, offscreen=True)
            if r.get("thumbnail"):
                li.setArt({"icon": r["thumbnail"]})
            li.setProperty(
                "item",
                json.dumps(
                    {
                        "label": r["label"],
                        "path": file_path,
                        "thumbnail": r.get("thumbnail", ""),
                        "filetype": "file",
                    }
                ),
            )
            items.append(li)
        # Next page at the bottom
        for r in next_pages:
            clean = _clean(r["label"])
            li = ListItem(
                "[B]%s[/B]" % (clean or "Next page"), "Load more...", offscreen=True
            )
            if r.get("thumbnail"):
                li.setArt({"icon": r["thumbnail"]})
            li.setProperty(
                "item",
                json.dumps(
                    {
                        "label": r["label"],
                        "path": r["file"],
                        "thumbnail": r.get("thumbnail", ""),
                        "filetype": "directory",
                    }
                ),
            )
            items.append(li)
        if not items:
            # Nothing at all — return path directly
            return {
                "label": _clean(cur_label),
                "path": cur_path,
                "thumbnail": cur_thumb,
            }
        choice = dialog.select("Choose path", items, useDetails=True)
        if choice < 0:
            # Multi-select button fires SetProperty + Action(Close), which lands here
            if _get_home_prop(_PROP_DO_MULTI) == "true":
                _clear_home_prop(_PROP_DO_MULTI)
                _clear_home_prop(_PROP_ALLOW_MULTI)
                picked = _multiselect_folders(results, heading=multi_heading)
                if not picked:
                    # Cancel or empty — stay in this directory
                    continue
                return {"multi": picked}
            if stack:
                cur_path, cur_label, cur_thumb = stack.pop()
            else:
                return None
            continue
        selected = json.loads(items[choice].getProperty("item"))
        if selected["path"] == cur_path:
            # User chose "Use as path"
            selected["label"] = _clean(selected["label"])
            return selected
        if selected.get("filetype") == "file":
            # Content item selected — re-show the same directory
            continue
        # Directory — push current onto stack and browse into it
        stack.append((cur_path, cur_label, cur_thumb))
        cur_path = selected["path"]
        cur_label = selected["label"]
        cur_thumb = selected.get("thumbnail", "")


def _multiselect_folders(results, heading=None):
    """Show a multi-select dialog over the directories in `results`.

    Returns a list of dicts {label, path, thumbnail, filetype} for picked
    folders, or [] if the user cancelled or selected nothing.
    """
    folders = [
        r
        for r in results
        if r.get("filetype") == "directory" and not _is_next_page(r.get("label", ""))
    ]
    if not folders:
        return []
    options = []
    for r in folders:
        li = ListItem(_clean(r["label"]), "Folder", offscreen=True)
        if r.get("thumbnail"):
            li.setArt({"icon": r["thumbnail"]})
        options.append(li)
    picked_idx = dialog.multiselect(
        heading or "Add multiple widgets", options, useDetails=True
    )
    if not picked_idx:
        return []
    return [
        {
            "label": _clean(folders[i]["label"]),
            "path": folders[i]["file"],
            "thumbnail": folders[i].get("thumbnail", ""),
            "filetype": "directory",
        }
        for i in picked_idx
    ]


def _multiselect_leaves(leaves, parent_target, heading=None):
    """Show a multi-select dialog over submenu leaf entries.

    Each leaf is a tuple (label, path[, target]). Returns a list of widget
    result dicts {label, path, thumbnail, target}, or [] on cancel/empty.
    Per-leaf target overrides (3-tuple nodes) are preserved.
    """
    if not leaves:
        return []
    options = []
    for n in leaves:
        label = _resolve_localize(n[0])
        li = ListItem(label, "Submenu option", offscreen=True)
        options.append(li)
    picked_idx = dialog.multiselect(
        heading or "Add multiple widgets", options, useDetails=True
    )
    if not picked_idx:
        return []
    out = []
    for i in picked_idx:
        n = leaves[i]
        node_target = n[2] if len(n) > 2 else parent_target
        out.append(
            {
                "label": _resolve_localize(n[0]),
                "path": n[1],
                "thumbnail": "",
                "target": node_target,
            }
        )
    return out


def _get_directory(path):
    """Fetch all items from a Kodi path via JSON-RPC.

    Returns a list of dicts, each with a 'filetype' key ('directory' or 'file')
    so callers can distinguish browsable folders from content items.
    """
    command = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "Files.GetDirectory",
        "params": {
            "directory": path,
            "media": "files",
            "properties": ["title", "file", "thumbnail"],
        },
    }
    try:
        response = json.loads(xbmc.executeJSONRPC(json.dumps(command)))
        files = response.get("result", {}).get("files") or []
    except Exception:
        return []
    # Addon paths: only show plugin:// entries
    if path.startswith("plugin://") or path.startswith("addons://"):
        return [f for f in files if f.get("file", "").startswith("plugin://")]
    return files


def _is_next_page(raw_label):
    """Detect pagination entries from Kodi addons."""
    low = raw_label.lower().replace("[b]", "").replace("[/b]", "").strip()
    if "next page" in low or "next >>" in low:
        return True
    # Matches labels like ">> Next", ">>", or ending with ">>"
    stripped = raw_label.rstrip()
    if stripped.endswith(">>"):
        return True
    return False


def _clean(label):
    """Strip Kodi formatting tags from a label."""
    if not label:
        return label
    label = label.replace("[B]", "").replace("[/B]", "").replace(" >>", "")
    while "[COLOR" in label:
        start = label.find("[COLOR")
        end = label.find("]", start) + 1
        if end == 0:
            break
        label = label[:start] + label[end:]
    label = label.replace("[/COLOR]", "")
    return label.strip()


def _show_busy():
    xbmc.executebuiltin("ActivateWindow(busydialognocancel)")


def _hide_busy():
    xbmc.executebuiltin("Dialog.Close(busydialognocancel)")
    xbmc.executebuiltin("Dialog.Close(busydialog)")
