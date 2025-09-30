import sys
import xbmc
from functools import cached_property


class ContextMenu:
    path_base = 'plugin.video.themoviedb.helper'
    path_kwgs = {}

    def __init__(self, info):
        self.path_info = info

    @cached_property
    def path_args(self):
        path_args = [
            self.path_base,
            self.path_info
        ] + [
            f'{k}={v}'
            for k, v in self.path_kwgs.items()
            if v not in (None, '')
        ]
        return tuple(path_args)

    @cached_property
    def path(self):
        path = ','.join(self.path_args)
        return f'RunScript({path})'

    def executebuiltin(self):
        xbmc.executebuiltin(self.path)


class ContextMenuBasic(ContextMenu):
    tmdb_type = None
    season = None
    episode = None
    episode_year = None

    @cached_property
    def tmdb_id(self):
        return sys.listitem.getUniqueID('tmdb')

    @cached_property
    def imdb_id(self):
        return sys.listitem.getUniqueID('imdb')

    @cached_property
    def query(self):
        return sys.listitem.getVideoInfoTag().getTitle() or sys.listitem.getLabel()

    @cached_property
    def year(self):
        return sys.listitem.getVideoInfoTag().getYear()

    @cached_property
    def path_kwgs(self):
        return {
            'tmdb_type': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'imdb_id': self.imdb_id,
            'query': self.query,
            'year': self.year,
            'season': self.season,
            'episode': self.episode,
            'episode_year': self.episode_year,
        }


class ContextMenuBasicMovie(ContextMenuBasic):
    tmdb_type = 'movie'


class ContextMenuBasicTvshow(ContextMenuBasic):
    tmdb_type = 'tv'


class ContextMenuBasicEpisode(ContextMenuBasic):
    tmdb_type = 'tv'
    year = None
    imdb_id = None

    @cached_property
    def tmdb_id(self):
        return sys.listitem.getUniqueID('tvshow.tmdb')

    @cached_property
    def query(self):
        return sys.listitem.getVideoInfoTag().getTVShowTitle()

    @cached_property
    def season(self):
        return sys.listitem.getVideoInfoTag().getSeason()

    @cached_property
    def episode(self):
        return sys.listitem.getVideoInfoTag().getEpisode()

    @cached_property
    def episode_year(self):
        return sys.listitem.getVideoInfoTag().getYear()


class ContextMenuPlayUsing:
    @cached_property
    def path_kwgs(self):
        return {
            'play': self.tmdb_type,
            'tmdb_id': self.tmdb_id,
            'imdb_id': self.imdb_id,
            'query': self.query,
            'year': self.year,
            'season': self.season,
            'episode': self.episode,
            'episode_year': self.episode_year,
            'ignore_default': 'true',
        }


class ContextMenuPlayUsingMovie(ContextMenuPlayUsing, ContextMenuBasicMovie):
    pass


class ContextMenuPlayUsingEpisode(ContextMenuPlayUsing, ContextMenuBasicEpisode):
    pass


ROUTES = {
    'play_using': {
        'base_class': 'ContextMenuPlayUsing',
        'permission': ('movie', 'episode')
    },
    'sync_trakt': {
        'base_class': 'ContextMenuBasic',
        'permission': ('movie', 'tvshow', 'episode')
    },
    'related_lists': {
        'base_class': 'ContextMenuBasic',
        'permission': ('movie', 'tvshow', 'episode')
    },
    'refresh_details': {
        'base_class': 'ContextMenuBasic',
        'permission': ('movie', 'tvshow', 'episode')
    },
}


def run_context(info):

    try:
        mediatype = sys.listitem.getVideoInfoTag().getMediaType()
        if mediatype not in ROUTES[info]['permission']:
            raise ValueError(f'Route does not permit {mediatype} mediatype key')
        class_object = getattr(sys.modules[__name__], f"{ROUTES[info]['base_class']}{mediatype.capitalize()}")
    except KeyError:
        class_object = ContextMenu
    except ValueError:
        return

    instance = class_object(info)
    instance.executebuiltin()
