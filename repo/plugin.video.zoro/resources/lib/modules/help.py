"""
	Venom Add-on
"""

from resources.lib.modules.control import addonPath, addonId, getzoroVersion, joinPath
from resources.lib.windows.textviewer import TextViewerXML


def get(file):
	zoro_path = addonPath(addonId())
	zoro_version = getzoroVersion()
	helpFile = joinPath(zoro_path, 'resources', 'help', file + '.txt')
	f = open(helpFile, 'r', encoding='utf-8', errors='ignore')
	text = f.read()
	f.close()
	heading = '[B]zoro -  v%s - %s[/B]' % (zoro_version, file)
	windows = TextViewerXML('textviewer.xml', zoro_path, heading=heading, text=text)
	windows.run()
	del windows
