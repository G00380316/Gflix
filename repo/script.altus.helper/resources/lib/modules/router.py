# -*- coding: utf-8 -*-
import sys
from urllib.parse import parse_qsl

import xbmc
import xbmcgui

from modules.widget_manager.config_manager import (
    ConfigManager,
    list_saved_configs,
    load_config,
    save_config_as,
    get_active_config,
    sanitize_config_name,
    rename_config,
    delete_config,
)
from modules.widget_manager.xml_generator import (
    generate_and_reload,
    _init_stacked_widgets,
)
from modules.widget_manager.default_config import create_default_sections
from modules.widget_manager.migration import migrate, import_from_skin

# from modules.logger import logger


def routing():
    params = dict(parse_qsl(sys.argv[1], keep_blank_values=True))
    _get = params.get
    mode = _get("mode", "check_for_update")

    if mode == "widget_monitor":
        from modules.widget_utils import widget_monitor

        return widget_monitor(_get("list_id"))

    if mode == "season_monitor":
        from modules.widget_utils import season_monitor

        return season_monitor(_get("container_id"))

    if mode == "icon_folder_debounce":
        from modules.widget_manager.manager_window import icon_folder_debounce

        return icon_folder_debounce()

    if mode == "open_channel_guide":
        from modules.pvr import open_channel_guide

        return open_channel_guide()

    if "actions" in mode:
        from modules import actions

        return exec("actions.%s(params)" % mode.split(".")[1])

    if mode == "check_for_update":
        from modules.version_monitor import check_for_update

        return check_for_update(_get("skin_id"))

    if mode == "check_for_profile_change":
        from modules.version_monitor import check_for_profile_change

        return check_for_profile_change(_get("skin_id"))

    if mode == "run_migration":
        return migrate()

    if mode == "generate_xml":
        generate_and_reload()
        xbmcgui.Dialog().notification(
            "Altus",
            "Menus and widgets rebuilt",
            xbmcgui.NOTIFICATION_INFO,
            3000,
        )
        return

    if mode == "migrate_and_generate":
        if not migrate():
            create_default_sections()
        return generate_and_reload()

    if mode == "create_default_sections":
        return create_default_sections()

    if mode == "import_widget_config":
        return import_from_skin()

    if mode == "new_widget_config":
        name = sanitize_config_name(
            xbmcgui.Dialog().input("Enter a name for the new config")
        )
        if not name:
            return
        existing = list_saved_configs()
        if name in existing:
            if not xbmcgui.Dialog().yesno(
                "New Widget Config",
                "A config named [B]%s[/B] already exists. Overwrite?" % name,
            ):
                return
        # Auto-save current config before switching
        active = get_active_config()
        if active:
            save_config_as(active)
        else:
            if xbmcgui.Dialog().yesno(
                "New Widget Config",
                "Your current config is unsaved and will be lost.[CR][CR]"
                "Save it first?",
            ):
                save_name = sanitize_config_name(
                    xbmcgui.Dialog().input("Enter a name for your current config")
                )
                if save_name:
                    save_config_as(save_name)
        # Wipe current config and create defaults
        cm = ConfigManager()
        for section in cm.get_sections():
            cm.remove_section(section["id"])
        cm.close()
        create_default_sections()
        # Set new profile as active and save it
        xbmc.executebuiltin("Skin.SetString(altus_active_widget_config,%s)" % name)
        save_config_as(name)
        generate_and_reload(active_config=name)
        return

    if mode == "load_widget_config":
        active = get_active_config()
        configs = [c for c in list_saved_configs() if c != active]
        if not configs:
            xbmcgui.Dialog().ok(
                "Load Widget Config",
                "No other saved configs found.[CR][CR]" "Create a new config first.",
            )
            return
        idx = xbmcgui.Dialog().select("Select config to load", configs)
        if idx < 0:
            return
        chosen = configs[idx]
        # Auto-save current config before switching
        if active:
            save_config_as(active)
        else:
            if xbmcgui.Dialog().yesno(
                "Load Widget Config",
                "Your current config is unsaved and will be lost.[CR][CR]"
                "Save it first?",
            ):
                save_name = sanitize_config_name(
                    xbmcgui.Dialog().input("Enter a name for your current config")
                )
                if save_name:
                    save_config_as(save_name)
        if load_config(chosen):
            xbmc.executebuiltin(
                "Skin.SetString(altus_active_widget_config,%s)" % chosen
            )
            generate_and_reload(active_config=chosen)
        else:
            xbmcgui.Dialog().notification(
                "Altus",
                "Failed to load config",
                xbmcgui.NOTIFICATION_ERROR,
                3000,
            )
        return

    if mode == "rename_widget_config":
        active = get_active_config()
        if not active:
            xbmcgui.Dialog().ok(
                "Rename Widget Config",
                "No active config to rename.[CR][CR]Save or create a config first.",
            )
            return
        new_name = sanitize_config_name(
            xbmcgui.Dialog().input('Rename "%s" to' % active, defaultt=active)
        )
        if not new_name or new_name == active:
            return
        existing = list_saved_configs()
        if new_name in existing:
            if not xbmcgui.Dialog().yesno(
                "Rename Widget Config",
                "A config named [B]%s[/B] already exists. Overwrite?" % new_name,
            ):
                return
        save_config_as(active)
        if rename_config(active, new_name):
            xbmc.executebuiltin(
                "Skin.SetString(altus_active_widget_config,%s)" % new_name
            )
        else:
            xbmcgui.Dialog().notification(
                "Altus",
                "Failed to rename config",
                xbmcgui.NOTIFICATION_ERROR,
                3000,
            )
        return

    if mode == "load_default_config":
        if not xbmcgui.Dialog().yesno(
            "Load Default Config",
            "Reset to the default widget configuration?[CR][CR]"
            "This will replace your current widget setup.",
        ):
            return
        active = get_active_config()
        if active:
            save_config_as(active)
        else:
            if xbmcgui.Dialog().yesno(
                "Load Default Config",
                "Your current config is unsaved and will be lost.[CR][CR]"
                "Save it first?",
            ):
                save_name = sanitize_config_name(
                    xbmcgui.Dialog().input("Enter a name for your current config")
                )
                if save_name:
                    save_config_as(save_name)
        cm = ConfigManager()
        for section in cm.get_sections():
            cm.remove_section(section["id"])
        cm.close()
        create_default_sections()
        xbmc.executebuiltin("Skin.Reset(altus_active_widget_config)")
        generate_and_reload(active_config="")
        return

    if mode == "delete_widget_config":
        active = get_active_config()
        configs = [c for c in list_saved_configs() if c != active]
        if not configs:
            xbmcgui.Dialog().ok("Delete Widget Config", "No saved configs to delete.")
            return
        idx = xbmcgui.Dialog().select("Select config to delete", configs)
        if idx < 0:
            return
        chosen = configs[idx]
        if not xbmcgui.Dialog().yesno(
            "Delete Widget Config",
            "Delete [B]%s[/B]? This cannot be undone." % chosen,
        ):
            return
        if delete_config(chosen):
            xbmcgui.Dialog().notification(
                "Altus",
                'Deleted config "%s"' % chosen,
                xbmcgui.NOTIFICATION_INFO,
                3000,
            )
        else:
            xbmcgui.Dialog().notification(
                "Altus",
                "Failed to delete config",
                xbmcgui.NOTIFICATION_ERROR,
                3000,
            )
        return

    if mode == "open_widget_manager":
        from modules.widget_manager.manager_window import open_manager

        return open_manager()

    if mode == "starting_widgets":
        cm = ConfigManager()
        config = cm.get_full_config()
        cm.close()
        return _init_stacked_widgets(config)

    if mode == "refresh_search_history":
        from modules.search_utils import SPaths

        return SPaths().refresh_search_history()

    if mode == "search_input":
        from modules.search_utils import SPaths

        return SPaths().search_input()

    if mode == "remove_all_spaths":
        from modules.search_utils import SPaths

        return SPaths().remove_all_spaths()

    if mode == "re_search":
        from modules.search_utils import SPaths

        return SPaths().re_search()

    if mode == "open_search_window":
        from modules.search_utils import SPaths

        return SPaths().open_search_window()

    if mode == "toggle_search_provider":
        from modules.search_utils import SPaths

        return SPaths().toggle_search_provider()

    if mode == "set_api_key":
        from modules.custom_actions import set_api_key

        return set_api_key()

    if mode == "save_view":
        from modules.select_view import save_view

        return save_view()

    if mode == "delete_all_ratings":
        from modules.databases.ratings import RatingsDatabase

        return RatingsDatabase().delete_all_ratings()

    if mode == "set_image":
        from modules.custom_actions import set_image

        return set_image()

    if mode == "set_blurradius":
        from modules.custom_actions import set_blurradius

        return set_blurradius()

    if mode == "set_blursaturation":
        from modules.custom_actions import set_blursaturation

        return set_blursaturation()

    if mode == "play_trailer":
        from modules.custom_actions import play_trailer

        return play_trailer()

    if mode == "clear_all_image_caches":
        from modules.helper import clear_all_image_caches

        return clear_all_image_caches()

    if mode == "calculate_cache_size":
        from modules.helper import calculate_cache_size

        return calculate_cache_size()

    if mode == "clear_color_cache":
        from modules.helper import clear_color_cache

        return clear_color_cache()

    if mode == "clear_logo_cache":
        from modules.helper import clear_logo_cache

        return clear_logo_cache()

    if mode == "clear_blur_cache":
        from modules.helper import clear_blur_cache

        return clear_blur_cache()

    if mode == "show_changelog":
        from modules.custom_actions import show_changelog

        return show_changelog()

    if mode == "check_api_key_on_load":
        from modules.custom_actions import check_api_key_on_load

        return check_api_key_on_load()

    # if mode == "getkodisettings":
    #     from modules.custom_actions import getkodisettings

    #     return getkodisettings(params)

    # if mode == "set_widget_boundaries":
    #     from modules.custom_actions import set_widget_boundaries

    #     return set_widget_boundaries()
