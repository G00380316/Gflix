"""
	Venom Add-on
"""

from json import dumps as jsdumps
from resources.lib.modules.control import dialog, getHighlightColor
from resources.lib.windows.base import BaseDialog


class TraktWatchlistManagerXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2050
		self.results = kwargs.get('results')
		self.total_results = str(len(self.results))
		self.selected_items = []
		self.make_items()
		self.set_properties()

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected_items

	# def onClick(self, controlID):
		# from resources.lib.modules import log_utils
		# log_utils.log('controlID=%s' % controlID)

	def onAction(self, action):
		try:
			if action in self.selection_actions:
				focus_id = self.getFocusId()
				if focus_id == 2050: # listItems
					position = self.get_position(self.window_id)
					chosen_listitem = self.item_list[position]
					trakt = chosen_listitem.getProperty('zoro.trakt')
					if chosen_listitem.getProperty('zoro.isSelected') == 'true':
						chosen_listitem.setProperty('zoro.isSelected', '')
						if trakt in self.selected_items: self.selected_items.remove(trakt)
					else:
						chosen_listitem.setProperty('zoro.isSelected', 'true')
						self.selected_items.append(trakt)
				elif focus_id == 2051: # OK Button
					self.close()
				elif focus_id == 2052: # Cancel Button
					self.selected_items = None
					self.close()

			# elif action in self.context_actions:
				# from resources.lib.modules import log_utils
				# chosen_source = self.item_list[self.get_position(self.window_id)]
				# source_trailer = chosen_source.getProperty('zoro.trailer')
				# if not source_trailer: return
				# log_utils.log('source_trailer=%s' % source_trailer)
				# cm = [('[B]Play Trailer[/B]', 'playTrailer'),]
				# chosen_cm_item = dialog.contextmenu([i[0] for i in cm])
				# if chosen_cm_item == -1: return
				# return self.execute_code('PlayMedia(%s, 1)' % source_trailer)

			elif action in self.closing_actions:
				self.selected_items = None
				self.close()
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
			self.close()

	def make_items(self):
		def builder():
			for count, item in enumerate(self.results, 1):
				try:
					listitem = self.make_listitem()
					listitem.setProperty('zoro.title', item.get('title'))
					listitem.setProperty('zoro.year', str(item.get('year')))
					listitem.setProperty('zoro.isSelected', '')
					listitem.setProperty('zoro.imdb', item.get('imdb'))
					listitem.setProperty('zoro.tmdb', item.get('tmdb'))
					listitem.setProperty('zoro.trakt', item.get('trakt'))
					listitem.setProperty('zoro.rating', str(round(float(item.get('rating', '0')), 1)))
					listitem.setProperty('zoro.trailer', item.get('trailer'))
					listitem.setProperty('zoro.studio', item.get('studio'))
					listitem.setProperty('zoro.genre', item.get('genre', ''))
					listitem.setProperty('zoro.duration', str(item.get('duration')))
					listitem.setProperty('zoro.mpaa', item.get('mpaa') or 'NA')
					listitem.setProperty('zoro.plot', item.get('plot'))
					listitem.setProperty('zoro.poster', item.get('poster', ''))
					listitem.setProperty('zoro.clearlogo', item.get('clearlogo', ''))
					listitem.setProperty('zoro.count', '%02d.)' % count)
					yield listitem
				except:
					from resources.lib.modules import log_utils
					log_utils.error()
		try:
			self.item_list = list(builder())
			self.total_results = str(len(self.item_list))
		except:
			from resources.lib.modules import log_utils
			log_utils.error()

	def set_properties(self):
		try:
			self.setProperty('zoro.total_results', self.total_results)
			self.setProperty('zoro.highlight.color', getHighlightColor())
		except:
			from resources.lib.modules import log_utils
			log_utils.error()
