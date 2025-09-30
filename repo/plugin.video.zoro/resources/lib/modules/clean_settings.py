"""
	Venom Add-on
"""

import xml.etree.ElementTree as ET
from resources.lib.modules import control


def clean_settings():
	def _make_content(dict_object):
		content = '<settings version="2">'
		for item in dict_object:
			if item['id'] in active_settings:
				if 'default' in item and 'value' in item: content += '\n    <setting id="%s" default="%s">%s</setting>' % (item['id'], item['default'], item['value'])
				elif 'default' in item: content += '\n    <setting id="%s" default="%s"></setting>' % (item['id'], item['default'])
				elif 'value' in item: content += '\n    <setting id="%s">%s</setting>' % (item['id'], item['value'])
				else: content += '\n    <setting id="%s"></setting>'
			else: removed_settings.append(item)
		content += '\n</settings>'
		return content

	for addon_id in ['plugin.video.zoro']:
		try:
			removed_settings = []
			active_settings = []
			current_user_settings = []
			addon = control.addon(id=addon_id)
			addon_name = addon.getAddonInfo('name')
			addon_dir = control.transPath(addon.getAddonInfo('path'))
			profile_dir = control.transPath(addon.getAddonInfo('profile'))
			active_settings_xml = control.joinPath(addon_dir, 'resources', 'settings.xml')
			root = ET.parse(active_settings_xml).getroot()
			for item in root.findall('./category/setting'):
				setting_id = item.get('id')
				if setting_id:
					active_settings.append(setting_id)
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			root = ET.parse(settings_xml).getroot()
			for item in root:
				dict_item = {}
				setting_id = item.get('id')
				setting_default = item.get('default')
				setting_value = item.text
				dict_item['id'] = setting_id
				if setting_value:
					dict_item['value'] = setting_value
				if setting_default:
					dict_item['default'] = setting_default
				current_user_settings.append(dict_item)
			new_content = _make_content(current_user_settings)
			nfo_file = control.openFile(settings_xml, 'w')
			nfo_file.write(new_content)
			nfo_file.close()
			control.sleep(200)
			control.notification(title=addon_name, message=control.lang(32084).format(str(len(removed_settings))))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.notification(title=addon_name, message=32115)

def new_settings():
	_default_value = '\n    <setting id="%s" default="%s">%s</setting>'
	_value = '\n    <setting id="%s">%s</setting>'
	for addon_id in ['plugin.video.zoro']:
		try:
			current_user_settings = {}
			addon = control.addon(id=addon_id)
			addon_name = addon.getAddonInfo('name')
			addon_dir = control.transPath(addon.getAddonInfo('path'))
			profile_dir = control.transPath(addon.getAddonInfo('profile'))
			active_settings_xml = control.joinPath(addon_dir, 'resources', 'settings.xml')
			root = ET.parse(active_settings_xml).getroot()
			active_settings = {
				k: item.get('default', '')
				for item in root.findall('./category/setting')
				if (k := item.get('id'))
			}
			settings_xml = control.joinPath(profile_dir, 'settings.xml')
			root = ET.parse(settings_xml).getroot()
			for item in root:
				dict_item = {}
				setting_id = item.get('id')
				setting_default = item.get('default')
				setting_value = item.text
				if setting_value:
					dict_item['value'] = setting_value
				if setting_default:
					dict_item['default'] = setting_default
				current_user_settings[setting_id] = dict_item
			content = '<settings version="2">'
			for setting, default in active_settings.items():
				if setting not in current_user_settings:
					content += _value % (setting, default)
					continue
				item = current_user_settings.pop(setting)
				if 'default' in item and 'value' in item: content += _default_value % (setting, item['default'], default)
				elif 'default' in item: content += _default_value % (setting, item['default'], default)
#				elif 'value' in item: content += _value % (setting, item['value'])
				else: content += _value % (setting, item.get('value', default))
			content += '\n</settings>'
			nfo_file = control.openFile(settings_xml, 'w')
			nfo_file.write(content)
			nfo_file.close()
			control.sleep(200)
			control.notification(title=addon_name, message=control.lang(32084).format(str(len(current_user_settings))))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			control.notification(title=addon_name, message=32115)
