import xbmc, xbmcaddon, xbmcgui, xbmcvfs
import xml.etree.ElementTree as ET
from xml.dom import minidom
from threading import Timer
import sys, re
import json

def show_changelog():
    helper_addon = xbmcaddon.Addon("script.altus.helper")
    helper_version = helper_addon.getAddonInfo("version")
    skin_addon = xbmcaddon.Addon("skin.altus")
    skin_version = skin_addon.getAddonInfo("version")
    skin_name = skin_addon.getAddonInfo("name")
    changelog_path = xbmcvfs.translatePath("special://skin/altuschangelog.txt")
    with xbmcvfs.File(changelog_path) as file:
        changelog_text = file.read()
    if isinstance(changelog_text, bytes):
        changelog_text = changelog_text.decode("utf-8")
    changelog_text = re.sub(
        r"\[COLOR \w+\](Version \d+\.\d+\.\d+)\[/COLOR\]",
        f"[COLOR $VAR[FocusColorTheme]]\\1[/COLOR]",
        changelog_text,
    )
    changelog_text = re.sub(
        r"\[COLOR \w+\](Version \$INFO\[.*?\])\[/COLOR\]",
        f"[COLOR $VAR[FocusColorTheme]]\\1[/COLOR]",
        changelog_text,
    )
    helper_pattern = r"(Altus Helper: Latest: v([\d.]+)) \| Installed: v.*"
    helper_match = re.search(helper_pattern, changelog_text)
    if helper_match:
        latest_helper_version = helper_match.group(2)
        installed_part = f"Installed: v{helper_version}"
        if helper_version != latest_helper_version:
            installed_part = f"[COLOR red][B]{installed_part}[/B][/COLOR]"
            update_message = (
                "\n\n[COLOR red][B]An update is available for the Altus Helper. "
                "Please follow these instructions to update and get the latest features and ensure full continued functionality:[/B][/COLOR]"
                "\n\n1. Go to Settings [B]»[/B] System [B]»[/B] Addons tab [B]»[/B] Manage dependencies"
                "\n2. Find Altus Helper and click it"
                "\n3. Versions [B]»[/B] Click the latest version in ivarbrandt's Repository"
            )
        else:
            update_message = "\n\n[COLOR limegreen][B]Altus Helper up to date. No updates needed at this time.[/B][/COLOR]"
        new_helper_info = f"{helper_match.group(1)} | {installed_part}{update_message}"
        changelog_text = re.sub(
            helper_pattern, new_helper_info, changelog_text, count=1
        )
    header = f"CHANGELOG: {skin_name} v{skin_version}"
    dialog = xbmcgui.Dialog()
    dialog.textviewer(header, changelog_text)


def set_image():
    last_path = xbmc.getInfoLabel("Skin.String(LastImagePath)")
    image_file = xbmcgui.Dialog().browse(
        2,
        "Choose Custom Background Image",
        "network",
        ".jpg|.png|.bmp",
        False,
        False,
        last_path,
    )
    if image_file and image_file != last_path:
        xbmc.executebuiltin(f"Skin.SetString(LastImagePath,{image_file})")
        xbmc.executebuiltin(f"Skin.SetString(AltusCustomBackground,{image_file})")


def play_trailer():
    trailer_source = xbmc.getInfoLabel("Skin.String(TrailerSource)")
    play_url = None
    if trailer_source == "0":
        play_url = xbmc.getInfoLabel("ListItem.Trailer")
    elif trailer_source == "1":
        play_url = xbmc.getInfoLabel("Skin.String(TrailerPlaybackURL)")
    if play_url:
        xbmc.executebuiltin("Skin.SetString(TrailerPlaying, true)")
        xbmc.executebuiltin(f"PlayMedia({play_url},1,noresume)")


def set_blurradius():
    current_value = xbmc.getInfoLabel("Skin.String(BlurRadius)") or "20"
    dialog = xbmcgui.Dialog()
    value = dialog.numeric(0, "Enter blur radius value", current_value)
    if value == "":
        value = "20"
    xbmc.executebuiltin(f"Skin.SetString(BlurRadius,{value})")


def set_blursaturation():
    current_value = xbmc.getInfoLabel("Skin.String(BlurSaturation)") or "1.0"
    keyboard = xbmc.Keyboard(current_value, "Enter blur saturation value")
    keyboard.doModal()
    if keyboard.isConfirmed():
        text = keyboard.getText()
        if text == "":
            text = "1.0"
        xbmc.executebuiltin(f"Skin.SetString(BlurSaturation,{text})")


def check_api_key(api_key):
    import requests
    api_url = "https://mdblist.com/api/"
    params = {
        "apikey": api_key,
        "i": "tt0111161",
    }
    try:
        response = requests.get(api_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return ("valid", "ratings" in data and len(data["ratings"]) > 0)
    except requests.RequestException:
        return ("error", None)


def validate_api_key(api_key, silent=True):
    if not api_key:
        xbmc.executebuiltin("Skin.Reset(valid_api_key)")
        return
    xbmc.executebuiltin("Skin.SetString(checking_api_key,true)")
    try:
        status, is_valid = check_api_key(api_key)
        if status == "valid" and is_valid:
            xbmc.executebuiltin("Skin.SetString(valid_api_key,true)")
            if not silent:
                xbmcgui.Dialog().notification(
                    "Success",
                    "Features activated",
                    xbmcgui.NOTIFICATION_INFO,
                    3000,
                )
        elif status == "valid" and not is_valid:
            xbmc.executebuiltin("Skin.Reset(valid_api_key)")
        else:
            if not silent:
                xbmcgui.Dialog().notification(
                    "Connection Error",
                    "Unable to reach MDbList",
                    xbmcgui.NOTIFICATION_INFO,
                    3000,
                )
    finally:
        xbmc.executebuiltin("Skin.Reset(checking_api_key)")


def set_api_key():
    current_key = xbmc.getInfoLabel("Skin.String(mdblist_api_key)")
    keyboard = xbmc.Keyboard(current_key, "Enter MDbList API Key")
    keyboard.doModal()
    if keyboard.isConfirmed():
        new_key = keyboard.getText()
        if not new_key:
            xbmc.executebuiltin("Skin.Reset(mdblist_api_key)")
            xbmc.executebuiltin("Skin.Reset(valid_api_key)")
        else:
            xbmc.executebuiltin(f'Skin.SetString(mdblist_api_key,"{new_key}")')
            validate_api_key(new_key, silent=False)


def check_api_key_on_load():
    api_key = xbmc.getInfoLabel("Skin.String(mdblist_api_key)")
    validate_api_key(api_key, silent=True)


# def JsonRPC(method, properties=None, sort=None, query_filter=None, limit=None, params=None, item=None, options=None, limits=None):
#     json_string = {
#         'jsonrpc': '2.0',
#         'id': 1,
#         'method': method,
#         'params': {}
#     }

#     if properties is not None:
#         json_string['params']['properties'] = properties
#     if limit is not None:
#         json_string['params']['limits'] = {'start': 0, 'end': int(limit)}
#     if sort is not None:
#         json_string['params']['sort'] = sort
#     if query_filter is not None:
#         json_string['params']['filter'] = query_filter
#     if options is not None:
#         json_string['params']['options'] = options
#     if limits is not None:
#         json_string['params']['limits'] = limits
#     if item is not None:
#         json_string['params']['item'] = item
#     if params is not None:
#         json_string['params'].update(params)

#     jsonrpc_call = json.dumps(json_string)
#     result = xbmc.executeJSONRPC(jsonrpc_call)
#     return json.loads(result)

# def getkodisettings(params: dict):
#     WIN_HOME = 10000

#     params.pop('mode', None)
#     window_id = int(params.pop('window_id', WIN_HOME))

#     if len(params) == 0:
#         return

#     for window_prop in params:
#         try:
#             kodi_setting = params.get(window_prop)
#             json_query = JsonRPC('Settings.GetSettingValue', params={'setting': kodi_setting})

#             result = json_query['result']
#             result = result.get('value')
#             result = str(result)
#             if result.startswith('[') and result.endswith(']'):
#                 result = result[1:-1]

#             xbmcgui.Window(window_id).setProperty(window_prop, result)
#         except:
#             xbmcgui.Window(window_id).clearProperty(window_prop)


# def set_widget_boundaries():
#     if len(sys.argv) >= 3:
#         list_id = sys.argv[2]
#         if len(list_id) in (4, 5, 6):
#             # Determine container ID based on list ID length
#             container_id = (
#                 f"{list_id[:2]}001" if len(list_id) in (5, 6) else f"{list_id[0]}001"
#             )

#             try:
#                 # Get the number of items in the container
#                 num_items_str = xbmc.getInfoLabel(f"Container({container_id}).NumItems")

#                 if num_items_str and num_items_str.isdigit():
#                     num_items = int(num_items_str)

#                     # Collect widget IDs
#                     widget_ids = []

#                     # Fixed patterns that don't depend on num_items
#                     fixed_patterns = [
#                         f"{list_id[:2]}900",
#                         f"{list_id[:1]}200",
#                         f"{list_id[:1]}300",
#                         f"{list_id[:1]}400",
#                         f"{list_id[:1]}500",
#                         f"{list_id[:1]}600",
#                         f"{list_id[:1]}700",
#                         f"{list_id[:1]}800",
#                         f"{list_id[:1]}900",
#                         f"{list_id[:2]}200",
#                         f"{list_id[:2]}300",
#                         f"{list_id[:2]}400",
#                         f"{list_id[:2]}500",
#                         f"{list_id[:2]}600",
#                         f"{list_id[:2]}700",
#                         f"{list_id[:2]}800",
#                     ]

#                     # Patterns that depend on num_items
#                     dynamic_patterns = [
#                         [f"{list_id[:2]}0{i}0" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}1" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}2" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}3" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}4" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}5" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}6" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}7" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}8" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}9" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}11" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}21" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}31" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}41" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}51" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}61" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}71" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}81" for i in range(1, num_items + 1)],
#                         [f"{list_id[:2]}0{i}91" for i in range(1, num_items + 1)],
#                     ]

#                     # Combine patterns
#                     all_patterns = fixed_patterns + [
#                         pattern for sublist in dynamic_patterns for pattern in sublist
#                     ]

#                     # Try to find existing controls for these patterns
#                     for pattern in set(all_patterns):  # Use set to remove duplicates
#                         try:
#                             control_id = int(pattern)
#                             control = xbmcgui.Window(10000).getControl(control_id)

#                             # Check number of items in the container
#                             container_items_str = xbmc.getInfoLabel(
#                                 f"Container({control_id}).NumItems"
#                             )

#                             if container_items_str and container_items_str.isdigit():
#                                 num_container_items = int(container_items_str)

#                                 # Only append if number of items is greater than 0
#                                 if num_container_items > 0:
#                                     widget_ids.append(pattern)
#                                     xbmc.log(
#                                         f"Found widget: {pattern} with {num_container_items} items",
#                                         2,
#                                     )
#                         except Exception:
#                             pass

#                     # Sort the widget IDs
#                     widget_ids = list(set(widget_ids))  # Remove duplicates
#                     widget_ids.sort(key=lambda x: (not x.endswith("900"), x))

#                     # Log found widget IDs
#                     xbmc.log(f"All found widget IDs: {widget_ids}", 2)

#                     # Set properties if widgets are found
#                     if len(widget_ids) > 1:
#                         xbmc.executebuiltin(
#                             f"SetProperty(FirstWidgetID,{widget_ids[0]},Home)"
#                         )
#                         xbmc.executebuiltin(
#                             f"SetProperty(LastWidgetID,{widget_ids[-1]},Home)"
#                         )

#             except Exception as e:
#                 xbmc.log(f"Error in set_widget_boundaries: {str(e)}", 2)

# def color(self, img):
#         """Optimized color analysis with original text color logic and color binning."""
#         default_color = "FFCCCCCC"
#         default_text_color = "FF141515"

#         def get_luminance(r, g, b):
#             """Calculate luminance using perceived brightness weights."""
#             r = r / 255 if r <= 10 else ((r / 255 + 0.055) / 1.055) ** 2.4
#             g = g / 255 if g <= 10 else ((g / 255 + 0.055) / 1.055) ** 2.4
#             b = b / 255 if b <= 10 else ((b / 255 + 0.055) / 1.055) ** 2.4
#             return 0.2126 * r + 0.7152 * g + 0.0722 * b

#         def get_contrast_ratio(l1, l2):
#             """Calculate contrast ratio between two luminance values."""
#             lighter = max(l1, l2)
#             darker = min(l1, l2)
#             return (lighter + 0.05) / (darker + 0.05)

#         def get_best_text_color(bg_color):
#             """Determine best text color with bias towards white."""
#             bg_luminance = get_luminance(bg_color[0], bg_color[1], bg_color[2])

#             white = (255, 255, 255)
#             dark = (20, 21, 21)  # FF141515

#             white_contrast = get_contrast_ratio(get_luminance(*white), bg_luminance)
#             dark_contrast = get_contrast_ratio(get_luminance(*dark), bg_luminance)

#             # Bias towards white text (lower number equals higher bias)
#             if white_contrast >= dark_contrast * 0.52:  # This factor biases towards white
#                 return "FFFFFFFF"
#             return "FF141515"

#         try:
#             if img:
#                 # Resize to smaller size for color analysis
#                 img_resize = img.resize((25, 25))

#                 # Convert and get pixels once
#                 pixels = list(img_resize.convert("RGB").getdata())

#                 # Create color bins (simplify colors)
#                 color_bins = {}
#                 for pixel in pixels:
#                     # Simplify RGB values to reduce color space
#                     simple_color = (pixel[0]//10, pixel[1]//10, pixel[2]//10)
#                     if simple_color in color_bins:
#                         color_bins[simple_color] += 1
#                     else:
#                         color_bins[simple_color] = 1

#                 # Find the most common color
#                 dominant_color = max(color_bins.items(), key=lambda x: x[1])[0]

#                 # Scale the color back up
#                 r, g, b = [x * 10 for x in dominant_color]

#                 # Adjust brightness if needed
#                 h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
#                 if v < 0.65:  # Threshold for brightness adjustment
#                     v = min(v + 0.55, 1.0)
#                     r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]

#                 imagecolor = f"FF{r:02x}{g:02x}{b:02x}"
#                 textcolor = get_best_text_color((r, g, b))

#                 return imagecolor, textcolor

#         except Exception as e:
#             xbmc.log(f"Error processing image colors: {str(e)}", 2)

#         return default_color, default_text_color
