"""
	Venom Add-on
"""

from json import dumps as jsdumps
from urllib.parse import quote_plus
from resources.lib.modules.control import joinPath, transPath, dialog, getSourceHighlightColor, notification, setting as getSetting
from resources.lib.modules.source_utils import getFileType
from resources.lib.modules import tools
from resources.lib.windows.base import BaseDialog


LIST_ID, WIDE_LIST_ID = 2000, 2001


class SourceResultsXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = {
			'List': LIST_ID,
			'Wide List': WIDE_LIST_ID
		}.get(getSetting('sources.select.wide_list')) or LIST_ID
		self.results = kwargs.get('results')
		self.uncached = kwargs.get('uncached')
		self.total_results = str(len(self.results))
		self.meta = kwargs.get('meta')
		self.make_items()
		self.set_properties()
		self.dnlds_enabled = True if getSetting('downloads') == 'true' and (getSetting('movie.download.path') != '' or getSetting('tv.download.path') != '') else False

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onAction(self, action):
		try:
			action_id = action.getId() # change to just "action" as the ID is already returned in that.
			if action_id in self.info_actions:
				chosen_source = self.item_list[self.get_position(self.window_id)]
				chosen_source = chosen_source.getProperty('zoro.source_dict')
				syssource = quote_plus(chosen_source)
				self.execute_code('RunPlugin(plugin://plugin.video.zoro/?action=sourceInfo&source=%s)' % syssource)
			if action_id in self.selection_actions:
				chosen_source = self.item_list[self.get_position(self.window_id)]
				source = chosen_source.getProperty('zoro.source')
				if 'load' in source:
					position = self.get_position(self.window_id)
					self.load_uncachedTorrents()
					self.setFocusId(self.window_id)
					self.getControl(self.window_id).selectItem(position)
					self.selected = (None, '')
					return
				elif 'UNCACHED' in source:
					debrid = chosen_source.getProperty('zoro.debrid')
					source_dict = chosen_source.getProperty('zoro.source_dict')
					link_type = 'pack' if 'package' in source_dict else 'single'
					sysname = quote_plus(self.meta.get('title'))
					if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta:
						poster = self.meta.get('season_poster') or self.meta.get('poster')
						sysname += quote_plus(' S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
					elif 'year' in self.meta: sysname += quote_plus(' (%s)' % self.meta['year'])
					try: new_sysname = quote_plus(chosen_source.getProperty('zoro.name'))
					except: new_sysname = sysname
					self.execute_code('RunPlugin(plugin://plugin.video.zoro/?action=cacheTorrent&caller=%s&type=%s&title=%s&items=%s&url=%s&source=%s&meta=%s)' %
											(debrid, link_type, sysname, quote_plus(jsdumps(self.results)), quote_plus(chosen_source.getProperty('zoro.url')), quote_plus(source_dict), quote_plus(jsdumps(self.meta))))
					self.selected = (None, '')
				else:
					self.selected = ('play_Item', chosen_source)
				return self.close()
			elif action_id in self.context_actions:
				from re import match as re_match
				chosen_source = self.item_list[self.get_position(self.window_id)]
				source_dict = chosen_source.getProperty('zoro.source_dict')
				cm_list = [('[B]Additional Link Info[/B]', 'sourceInfo')]
				if 'cached (pack)' in source_dict or 'unchecked (pack)' in source_dict:
					cm_list += [('[B]Browse Debrid Pack[/B]', 'showDebridPack')]
				source = chosen_source.getProperty('zoro.source')
				if not 'UNCACHED' in source and self.dnlds_enabled:
					cm_list += [('[B]Download[/B]', 'download')]
				if re_match(r'^CACHED.*TORRENT', source):
					debrid = chosen_source.getProperty('zoro.debrid')
					cm_list += [('[B]Save to %s Cloud[/B]' % debrid, 'saveToCloud')]
				chosen_cm_item = dialog.contextmenu([i[0] for i in cm_list])
				if chosen_cm_item == -1: return
				cm_action = cm_list[chosen_cm_item][1]
				if cm_action == 'sourceInfo':
					self.execute_code('RunPlugin(plugin://plugin.video.zoro/?action=sourceInfo&source=%s)' % quote_plus(source_dict))
				elif cm_action == 'showDebridPack':
					debrid = chosen_source.getProperty('zoro.debrid')
					name = chosen_source.getProperty('zoro.name')
					hash = chosen_source.getProperty('zoro.hash')
					self.execute_code('RunPlugin(plugin://plugin.video.zoro/?action=showDebridPack&caller=%s&name=%s&url=%s&source=%s)' %
									(quote_plus(debrid), quote_plus(name), quote_plus(chosen_source.getProperty('zoro.url')), quote_plus(hash)))
					self.selected = (None, '')
				elif cm_action == 'download':
					sysname = quote_plus(self.meta.get('title'))
					poster = self.meta.get('poster', '')
					if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta:
						sysname = quote_plus(self.meta.get('tvshowtitle'))
						poster = self.meta.get('season_poster') or self.meta.get('poster')
						sysname += quote_plus(' S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
					elif 'year' in self.meta: sysname += quote_plus(' (%s)' % self.meta['year'])
					try: new_sysname = quote_plus(chosen_source.getProperty('zoro.name'))
					except: new_sysname = sysname
					self.execute_code('RunPlugin(plugin://plugin.video.zoro/?action=download&name=%s&image=%s&source=%s&caller=sources&title=%s)' %
										(new_sysname, quote_plus(poster), quote_plus(source_dict), sysname))
					self.selected = (None, '')
				elif cm_action == 'saveToCloud':
					magnet = chosen_source.getProperty('zoro.url')
					if debrid == 'AD':
						from resources.lib.debrid import alldebrid
						transfer_function = alldebrid.AllDebrid
						debrid_icon = alldebrid.ad_icon
					elif debrid == 'PM':
						from resources.lib.debrid import premiumize
						transfer_function = premiumize.Premiumize
						debrid_icon = premiumize.pm_icon
					elif debrid == 'RD':
						from resources.lib.debrid import realdebrid
						transfer_function = realdebrid.RealDebrid
						debrid_icon = realdebrid.rd_icon
					elif debrid == 'OC':
						from resources.lib.debrid import offcloud
						transfer_function = offcloud.Offcloud
						debrid_icon = offcloud.oc_icon
					elif debrid == 'ED':
						from resources.lib.debrid import easydebrid
						transfer_function = easydebrid.EasyDebrid
						debrid_icon = easydebrid.ed_icon
					elif debrid == 'TB':
						from resources.lib.debrid import torbox
						transfer_function = torbox.TorBox
						debrid_icon = torbox.tb_icon
					result = transfer_function().create_transfer(magnet)
					if result: notification(message='Sending MAGNET to the %s cloud' % debrid, icon=debrid_icon)
			elif action in self.closing_actions:
				self.selected = (None, '')
				self.close()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def get_quality_iconPath(self, quality):
		try:
			return joinPath(transPath('special://home/addons/plugin.video.zoro/resources/skins/Default/media/resolution'), '%s.png' % quality)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def debrid_abv(self, debrid):
		try:
			d_dict = {'AllDebrid': 'AD', 'EasyDebrid': 'ED', 'Offcloud': 'OC', 'Premiumize.me': 'PM', 'Real-Debrid': 'RD', 'TorBox': 'TB'}
			d = d_dict[debrid]
		except:
			d = ''
		return d

	def make_items(self):
		def builder():
			for count, item in enumerate(self.results, 1):
				try:
					listitem = self.make_listitem()
					quality = item.get('quality', 'SD')
					quality_icon = self.get_quality_iconPath(quality)
					extra_info = item.get('info')
					extra_info = extra_info.replace('/', '')
					extra_info = extra_info.split('GB ', 1)[-1]
					size_label = '%.2f GB' % item.get('size', 0) if item.get('size') else 'NA'
					listitem.setProperty('zoro.source_dict', jsdumps([item]))
					listitem.setProperty('zoro.debrid', self.debrid_abv(item.get('debrid')))
					listitem.setProperty('zoro.provider', item.get('provider').upper())
					listitem.setProperty('zoro.source', item.get('source').upper())
					listitem.setProperty('zoro.seeders', str(item.get('seeders')))
					listitem.setProperty('zoro.hash', item.get('hash', 'N/A'))
					listitem.setProperty('zoro.name', item.get('name'))
					listitem.setProperty('zoro.quality', quality.upper())
					listitem.setProperty('zoro.quality_icon', quality_icon)
					listitem.setProperty('zoro.url', item.get('url'))
					listitem.setProperty('zoro.extra_info', extra_info)
					listitem.setProperty('zoro.size_label', size_label)
					listitem.setProperty('zoro.count', '%02d.' % count)
					yield listitem
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
		try:
			self.item_list = list(builder())
			self.total_results = str(len(self.item_list))
			if self.uncached and getSetting('torrent.remove.uncached') == 'true':
				icon = '/resources/skins/Default/media/common/play.png'
				quality_icon = transPath('special://home/addons/plugin.video.zoro' + icon)
				uncached = str(len(self.uncached))
				fill_char = str.rjust(' ', len(self.total_results) + 1, '>')
				listitem = self.make_listitem()
				listitem.setProperty('zoro.name', 'View Uncached Torrents')
				listitem.setProperty('zoro.source', 'load uncached torrents')
				listitem.setProperty('zoro.quality_icon', quality_icon)
				listitem.setProperty('zoro.size_label', uncached)
				listitem.setProperty('zoro.count', fill_char)
				self.item_list.append(listitem)
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def set_properties(self):
		if self.meta is None: return
		try:
			self.setProperty('zoro.highlight.color', getSourceHighlightColor())
			self.setProperty('zoro.total_results', self.total_results)
			self.setProperty('zoro.season', str(self.meta.get('season', '')))
			if 'tvshowtitle' in self.meta and 'season' in self.meta and 'episode' in self.meta: self.setProperty('zoro.seas_ep', 'S%02dE%02d' % (int(self.meta['season']), int(self.meta['episode'])))
			if self.meta.get('season_poster'): self.setProperty('zoro.poster', self.meta.get('season_poster', ''))
			else: self.setProperty('zoro.poster', self.meta.get('poster', ''))
			self.setProperty('zoro.fanart', self.meta.get('fanart', ''))
			self.setProperty('zoro.clearlogo', self.meta.get('clearlogo', ''))
			self.setProperty('zoro.plot', self.meta.get('plot', ''))
			self.setProperty('zoro.year', str(self.meta.get('year', '')))
			new_date = tools.convert_time(stringTime=str(self.meta.get('premiered', '')), formatInput='%Y-%m-%d', formatOutput='%m-%d-%Y', zoneFrom='utc', zoneTo='utc')
			self.setProperty('zoro.premiered', new_date)
			mpaa = self.meta.get('mpaa') if self.meta.get('mpaa') else ''
			self.setProperty('zoro.mpaa', mpaa)
			if self.meta.get('duration'):
				duration = int(self.meta.get('duration')) / 60
				duration = '%.0f min' % duration
			else: duration = ''
			self.setProperty('zoro.duration', duration)
			details = ' | '.join(i for i in (mpaa, duration) if i)
			self.setProperty('zoro.details', details)
			self.setProperty('zoro.wide_list', 'true' if self.window_id == WIDE_LIST_ID else 'false')
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def load_uncachedTorrents(self):
		try:
			from resources.lib.windows.uncached_results import UncachedResultsXML
			from resources.lib.modules.control import addonPath, addonId
			window = UncachedResultsXML('uncached_results.xml', addonPath(addonId()), uncached=self.uncached, meta=self.meta)
			window.run()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
