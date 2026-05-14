# -*- coding: utf-8 -*-
"""
Migrates data from the old custom_paths table to the new sections/widgets schema.
Runs once automatically on first launch after update.
Also supports importing configs from other skins (Nimbus, FENtastic).
"""
import sqlite3 as database
import xbmc, xbmcvfs, xbmcgui

from modules.widget_manager.config_manager import ConfigManager

old_database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.altus.helper/cpath_cache.db"
)

# Skins whose cpath_cache.db can be imported into Altus.
# type_map converts display types that don't exist in Altus to their closest equivalent.
IMPORTABLE_SKINS = [
    {
        "name": "Nimbus",
        "addon_id": "script.nimbus.helper",
        "path": "special://profile/addon_data/script.nimbus.helper/cpath_cache.db",
        "type_map": {
            "WidgetListPoster": "WidgetListSmallPoster",
        },
    },
    {
        "name": "FENtastic",
        "addon_id": "script.fentastic.helper",
        "path": "special://profile/addon_data/script.fentastic.helper/cpath_cache.db",
        "type_map": {
            "WidgetListPoster": "WidgetListSmallPoster",
            "WidgetListBigPoster": "WidgetListPoster",
            "WidgetListLandscape": "WidgetListSmallLandscape",
            "WidgetListBigLandscape": "WidgetListLandscape",
            "WidgetListEpisodes": "WidgetListSmallLandscape",
            "WidgetListBigEpisodes": "WidgetListLandscape",
        },
    },
]

# Old hardcoded section keys → default names, onclick templates, and old skin settings
OLD_SECTION_MAP = {
    "movie": {
        "name": "Movies",
        "onclick": "ActivateWindow(Videos,{path},return)",
        "old_skin_setting": "HomeMenuNoMovieButton",
    },
    "tvshow": {
        "name": "TV Shows",
        "onclick": "ActivateWindow(Videos,{path},return)",
        "old_skin_setting": "HomeMenuNoTVShowButton",
    },
    "custom1": {
        "name": "Custom 1",
        "onclick": "ActivateWindow(Videos,{path},return)",
        "old_skin_setting": "HomeMenuNoCustom1Button",
    },
    "custom2": {
        "name": "Custom 2",
        "onclick": "ActivateWindow(Videos,{path},return)",
        "old_skin_setting": "HomeMenuNoCustom2Button",
    },
    "custom3": {
        "name": "Custom 3",
        "onclick": "ActivateWindow(Videos,{path},return)",
        "old_skin_setting": "HomeMenuNoCustom3Button",
    },
}

OLD_SECTION_ORDER = ["movie", "tvshow", "custom1", "custom2", "custom3"]


def _old_table_exists(db_path=None):
    """Check if the old custom_paths table exists and has data."""
    path = db_path or old_database_path
    if not xbmcvfs.exists(path):
        return False
    try:
        dbcon = database.connect(path, timeout=20)
        result = dbcon.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='custom_paths'"
        ).fetchone()
        if not result:
            dbcon.close()
            return False
        count = dbcon.execute("SELECT COUNT(*) FROM custom_paths").fetchone()[0]
        dbcon.close()
        return count > 0
    except Exception:
        return False


def _read_old_data(db_path=None):
    """Read all rows from the old custom_paths table."""
    path = db_path or old_database_path
    dbcon = database.connect(path, timeout=20)
    rows = dbcon.execute("SELECT * FROM custom_paths").fetchall()
    dbcon.close()
    data = {}
    for row in rows:
        data[row[0]] = {
            "cpath_setting": row[0],
            "cpath_path": row[1],
            "cpath_header": row[2],
            "cpath_type": row[3],
            "cpath_label": row[4],
        }
    return data


def _parse_stacked_info(cpath_type, cpath_label):
    """Determine if a widget is stacked and extract the stacked display type.

    Old format: cpath_type stores the child display type with "Stacked" suffix.
        e.g. "WidgetListSmallPosterStacked"
    The parent type is always WidgetListCategoryStacked.
    Non-stacked types never end with "Stacked".
    """
    is_stacked = 1 if (cpath_type or "").endswith("Stacked") else 0
    stacked_type = ""
    if is_stacked:
        # Strip "Stacked" suffix to get the base child display type
        # e.g. "WidgetListSmallPosterStacked" → "WidgetListSmallPoster"
        stacked_type = cpath_type[:-7] if cpath_type.endswith("Stacked") else cpath_type
    return is_stacked, stacked_type


def _map_type(cpath_type, type_map):
    """Map a display type using the provided mapping.

    Handles both base types (WidgetListLandscape) and stacked variants
    (WidgetListLandscapeStacked) using the same base mapping.
    """
    if not type_map or not cpath_type:
        return cpath_type
    if cpath_type in type_map:
        return type_map[cpath_type]
    if cpath_type.endswith("Stacked"):
        base = cpath_type[:-7]
        if base in type_map:
            return type_map[base] + "Stacked"
    return cpath_type


def _migrate_data(old_data, cm, migrate_skin_settings=False, type_map=None):
    """Core migration logic: create sections and widgets from old cpath data.

    Args:
        old_data: dict from _read_old_data()
        cm: open ConfigManager instance
        migrate_skin_settings: if True, migrate old visibility skin settings
        type_map: optional dict mapping source display types to Altus equivalents
    Returns:
        True if any sections were created.
    """
    created = False
    for old_section_key in OLD_SECTION_ORDER:
        info = OLD_SECTION_MAP[old_section_key]
        main_menu_key = "%s.main_menu" % old_section_key
        main_menu = old_data.get(main_menu_key)
        widgets = {k: v for k, v in old_data.items()
                   if k.startswith("%s.widget." % old_section_key)}
        if not main_menu and not widgets:
            continue
        onclick = ""
        name = info["name"]
        if main_menu:
            path = main_menu["cpath_path"]
            onclick = info["onclick"].format(path=path)
            if main_menu["cpath_header"]:
                name = main_menu["cpath_header"]
        section_id = cm.add_section(
            name=name,
            onclick=onclick,
        )
        created = True
        if migrate_skin_settings:
            old_setting = info["old_skin_setting"]
            if xbmc.getCondVisibility("Skin.HasSetting(%s)" % old_setting):
                xbmc.executebuiltin("Skin.SetBool(HomeMenuNoSection_%s)" % section_id)
        sorted_widgets = sorted(
            widgets.values(),
            key=lambda w: int(w["cpath_setting"].split(".")[-1]),
        )
        for widget_data in sorted_widgets:
            cpath_type = _map_type(widget_data["cpath_type"] or "", type_map)
            cpath_label = widget_data["cpath_label"] or ""
            is_stacked, stacked_type = _parse_stacked_info(cpath_type, cpath_label)
            if is_stacked:
                display_type = "WidgetListCategoryStacked"
            else:
                display_type = cpath_type
            cm.add_widget(
                section_id=section_id,
                path=widget_data["cpath_path"],
                label=widget_data["cpath_header"],
                display_type=display_type,
                is_stacked=is_stacked,
                stacked_type=stacked_type,
                target="videos",
            )
    return created


def migrate():
    """Migrate old custom_paths data to the new schema. Returns True if migration ran."""
    if not _old_table_exists():
        return False
    old_data = _read_old_data()
    if not old_data:
        return False
    cm = ConfigManager()
    count = cm.dbcur.execute("SELECT COUNT(*) FROM sections").fetchone()[0]
    if count > 0:
        cm.close()
        return False
    result = _migrate_data(old_data, cm, migrate_skin_settings=True)
    cm.close()
    return result


def import_from_skin():
    """Scan for importable skin configs and let the user choose one to import.

    Replaces the current Altus widget config with the imported data.
    """
    available = []
    for skin in IMPORTABLE_SKINS:
        db_path = xbmcvfs.translatePath(skin["path"])
        if _old_table_exists(db_path):
            available.append((skin["name"], db_path, skin.get("type_map", {})))
    if not available:
        xbmcgui.Dialog().ok(
            "Import Widget Config",
            "No importable widget configurations found.[CR][CR]"
            "Looked for configs from: %s" % ", ".join(s["name"] for s in IMPORTABLE_SKINS),
        )
        return False
    if len(available) == 1:
        chosen_name, chosen_path, chosen_type_map = available[0]
    else:
        names = [name for name, _, _ in available]
        idx = xbmcgui.Dialog().select("Select config to import", names)
        if idx < 0:
            return False
        chosen_name, chosen_path, chosen_type_map = available[idx]
    if not xbmcgui.Dialog().yesno(
        "Import Widget Config",
        "Import widget configuration from [B]%s[/B]?[CR][CR]"
        "This will replace your current Altus widget setup." % chosen_name,
    ):
        return False
    # Auto-save current config before overwriting
    from modules.widget_manager.config_manager import save_config_as, get_active_config, sanitize_config_name
    active = get_active_config()
    if active:
        save_config_as(active)
    else:
        if xbmcgui.Dialog().yesno(
            "Import Widget Config",
            "Your current config is unsaved and will be lost.[CR][CR]"
            "Save it first?",
        ):
            name = sanitize_config_name(xbmcgui.Dialog().input("Enter a name for your current config"))
            if name:
                save_config_as(name)
    old_data = _read_old_data(chosen_path)
    if not old_data:
        xbmcgui.Dialog().ok("Import Widget Config", "Failed to read data from %s config." % chosen_name)
        return False
    cm = ConfigManager()
    # Clear existing config
    for section in cm.get_sections():
        cm.remove_section(section["id"])
    result = _migrate_data(old_data, cm, type_map=chosen_type_map)
    cm.close()
    if result:
        xbmc.executebuiltin("Skin.SetString(altus_active_widget_config,%s)" % chosen_name)
        save_config_as(chosen_name)
        from modules.widget_manager.xml_generator import generate_and_reload
        generate_and_reload(active_config=chosen_name)
        xbmcgui.Dialog().ok(
            "Import Widget Config",
            "Successfully imported widget configuration from [B]%s[/B]." % chosen_name,
        )
    else:
        xbmcgui.Dialog().ok("Import Widget Config", "No sections or widgets found in %s config." % chosen_name)
    return result
