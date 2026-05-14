# -*- coding: utf-8 -*-
"""
Creates default sections and widgets matching Estuary's standard home screen layout.
Called on fresh install when no existing config or migration data exists.

Display type mapping (Estuary → Altus):
  WidgetListCategories → WidgetListCategory
  WidgetListPoster     → WidgetListPoster
  WidgetListEpisodes   → WidgetListLandscape
  WidgetListSquare     → WidgetListSquare
  WidgetListPVR        → WidgetListPVR
"""
from modules.widget_manager.config_manager import ConfigManager

# Each section: (name, onclick, widgets)
# Each widget: (label, path, display_type, target, sortby, sortorder)
DEFAULT_SECTIONS = [
    {
        "name": "$LOCALIZE[342]",
        "onclick": "ActivateWindow(Videos,videodb://movies/titles/,return)",
        "icon": "icons/sidemenu/movies.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "library://video/movies/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31010]",
                "special://skin/playlists/inprogress_movies.xsp",
                "WidgetListPoster",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[20386]",
                "special://skin/playlists/recent_unwatched_movies.xsp",
                "WidgetListPoster",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31007]",
                "special://skin/playlists/unwatched_movies.xsp",
                "WidgetListPoster",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31006]",
                "special://skin/playlists/random_movies.xsp",
                "WidgetListPoster",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[135]",
                "videodb://movies/genres/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31075]",
                "videodb://movies/sets/",
                "WidgetListPoster",
                "videos",
                "random",
                "",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[20343]",
        "onclick": "ActivateWindow(Videos,videodb://tvshows/titles/,return)",
        "icon": "icons/sidemenu/tv.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "library://video/tvshows/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[626]",
                "videodb://inprogresstvshows/",
                "WidgetListPoster",
                "videos",
                "lastplayed",
                "descending",
            ),
            (
                "$LOCALIZE[20387]",
                "special://skin/playlists/recent_unwatched_episodes.xsp",
                "WidgetListLandscape",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31122]",
                "special://skin/playlists/unwatched_tvshows.xsp",
                "WidgetListPoster",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[135]",
                "videodb://tvshows/genres/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[20388]",
                "videodb://tvshows/studios/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[2]",
        "onclick": "ActivateWindow(Music,root,return)",
        "icon": "icons/sidemenu/music.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "library://music/",
                "WidgetListCategory",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[517]",
                "musicdb://recentlyplayedalbums/",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[359]",
                "musicdb://recentlyaddedalbums/",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[31012]",
                "special://skin/playlists/random_albums.xsp",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[31013]",
                "special://skin/playlists/random_artists.xsp",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[31014]",
                "special://skin/playlists/unplayed_albums.xsp",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[31011]",
                "special://skin/playlists/mostplayed_albums.xsp",
                "WidgetListSquare",
                "music",
                "playcount",
                "descending",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[20389]",
        "onclick": "ActivateWindow(Videos,musicvideos,return)",
        "icon": "icons/sidemenu/musicvideos.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "library://video/musicvideos/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[20390]",
                "videodb://recentlyaddedmusicvideos/",
                "WidgetListLandscape",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31151]",
                "special://skin/playlists/unwatched_musicvideos.xsp",
                "WidgetListLandscape",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[31013]",
                "special://skin/playlists/random_musicvideo_artists.xsp",
                "WidgetListSquare",
                "music",
                "",
                "",
            ),
            (
                "$LOCALIZE[31152]",
                "special://skin/playlists/random_musicvideos.xsp",
                "WidgetListLandscape",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[20388]",
                "videodb://musicvideos/studios/",
                "WidgetListCategory",
                "music",
                "",
                "",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[19020]",
        "onclick": "ActivateWindow(TVChannels)",
        "icon": "icons/sidemenu/livetv.png",
        "widgets": [
            ("$LOCALIZE[31148]", "pvr://tv/", "WidgetListCategory", "videos", "", ""),
            (
                "$LOCALIZE[31016]",
                "pvr://channels/tv/*?view=lastplayed",
                "WidgetListPVR",
                "tvchannels",
                "lastplayed",
                "descending",
            ),
            (
                "$LOCALIZE[31015]",
                "pvr://recordings/tv/active?view=flat",
                "WidgetListPVR",
                "tvrecordings",
                "date",
                "descending",
            ),
            (
                "$LOCALIZE[19040]",
                "pvr://timers/tv/timers/?view=hidedisabled",
                "WidgetListPVR",
                "tvtimers",
                "date",
                "ascending",
            ),
            (
                "$LOCALIZE[19173]",
                "pvr://channels/tv",
                "WidgetListSquare",
                "tvguide",
                "",
                "",
            ),
            (
                "$LOCALIZE[19337]",
                "pvr://search/tv/savedsearches",
                "WidgetListSquare",
                "tvsearch",
                "date",
                "descending",
            ),
            (
                "$LOCALIZE[855]",
                "pvr://channels/tv/*?view=dateadded",
                "WidgetListPVR",
                "tvchannels",
                "dateadded",
                "descending",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[19021]",
        "onclick": "ActivateWindow(RadioChannels)",
        "icon": "icons/sidemenu/radio.png",
        "widgets": [
            ("$LOCALIZE[31148]", "pvr://radio/", "WidgetListCategory", "music", "", ""),
            (
                "$LOCALIZE[31018]",
                "pvr://channels/radio/*?view=lastplayed",
                "WidgetListPVR",
                "radiochannels",
                "lastplayed",
                "descending",
            ),
            (
                "$LOCALIZE[31015]",
                "pvr://recordings/radio/active?view=flat",
                "WidgetListPVR",
                "radiorecordings",
                "date",
                "descending",
            ),
            (
                "$LOCALIZE[19040]",
                "pvr://timers/radio/timers/?view=hidedisabled",
                "WidgetListPVR",
                "radiotimers",
                "date",
                "ascending",
            ),
            (
                "$LOCALIZE[19174]",
                "pvr://channels/radio",
                "WidgetListSquare",
                "radioguide",
                "",
                "",
            ),
            (
                "$LOCALIZE[19337]",
                "pvr://search/radio/savedsearches",
                "WidgetListSquare",
                "radiosearch",
                "date",
                "descending",
            ),
            (
                "$LOCALIZE[855]",
                "pvr://channels/radio/*?view=dateadded",
                "WidgetListPVR",
                "radiochannels",
                "dateadded",
                "descending",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[24001]",
        "onclick": "ActivateWindow(AddonBrowser)",
        "icon": "icons/sidemenu/addons.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "addons://",
                "WidgetListCategory",
                "addonbrowser",
                "",
                "",
            ),
            (
                "$LOCALIZE[1037]",
                "addons://sources/video/",
                "WidgetListSquare",
                "videos",
                "lastused",
                "descending",
            ),
            (
                "$LOCALIZE[1038]",
                "addons://sources/audio/",
                "WidgetListSquare",
                "music",
                "lastused",
                "descending",
            ),
            (
                "$LOCALIZE[35049]",
                "addons://sources/game/",
                "WidgetListSquare",
                "games",
                "lastused",
                "descending",
            ),
            (
                "$LOCALIZE[1043]",
                "addons://sources/executable/",
                "WidgetListSquare",
                "programs",
                "lastused",
                "descending",
            ),
            (
                "$LOCALIZE[20244]",
                "androidapp://sources/apps/",
                "WidgetListSquare",
                "programs",
                "lastused",
                "descending",
            ),
            (
                "$LOCALIZE[1039]",
                "addons://sources/image/",
                "WidgetListSquare",
                "pictures",
                "lastused",
                "descending",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[1]",
        "onclick": "ActivateWindow(Pictures)",
        "icon": "icons/sidemenu/pictures.png",
        "widgets": [
            (
                "$LOCALIZE[20094]",
                "sources://pictures/",
                "WidgetListCategory",
                "pictures",
                "",
                "",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[3]",
        "onclick": "ActivateWindow(Videos,root)",
        "icon": "icons/sidemenu/videos.png",
        "widgets": [
            (
                "$LOCALIZE[31148]",
                "library://video/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[20094]",
                "sources://video/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
            (
                "$LOCALIZE[136]",
                "special://videoplaylists/",
                "WidgetListCategory",
                "videos",
                "",
                "",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[15016]",
        "onclick": "ActivateWindow(Games)",
        "icon": "icons/sidemenu/games.png",
        "widgets": [
            (
                "$LOCALIZE[35049]",
                "addons://sources/game/",
                "WidgetListSquare",
                "games",
                "lastused",
                "descending",
            ),
        ],
    },
    {
        "name": "$LOCALIZE[10134]",
        "onclick": "ActivateWindow(favouritesbrowser)",
        "icon": "icons/sidemenu/favourites.png",
        "widgets": [
            ("$LOCALIZE[10134]", "favourites://", "WidgetListFavourites", "videos", "", ""),
        ],
    },
    {
        "name": "$LOCALIZE[8]",
        "onclick": "ActivateWindow(Weather)",
        "icon": "$VAR[WeatherFanartCodeIcon]",
        "widgets": [],
    },
]


def create_default_sections():
    """Populate the config DB with default sections and widgets.

    Only call when no existing config exists (fresh install, no migration).
    Returns True if sections were created.
    """
    cm = ConfigManager()
    # Check if any sections already exist
    config = cm.get_full_config()
    if config:
        cm.close()
        return False
    for section_data in DEFAULT_SECTIONS:
        section_id = cm.add_section(
            name=section_data["name"],
            onclick=section_data["onclick"],
            icon=section_data.get("icon", ""),
        )
        for label, path, display_type, target, sortby, sortorder in section_data[
            "widgets"
        ]:
            cm.add_widget(
                section_id=section_id,
                path=path,
                label=label,
                display_type=display_type,
                target=target,
                sortby=sortby,
                sortorder=sortorder,
            )
    cm.close()
    return True
