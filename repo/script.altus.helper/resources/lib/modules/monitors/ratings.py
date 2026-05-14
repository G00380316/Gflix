import xbmc
import xbmcgui
from threading import Thread, Lock
import json
import re
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any
from ..config import *
from ..databases import RatingsDatabase
from ..apis import MDbListClient, TMDbClient

CACHED_IDS_INDEX_PROP = "altus.cachedRatings.index"


@dataclass
class ReleaseWindowConfig:
    """Configuration for digital release windows."""
    recent_days: str = "7"
    expired_days: str = "21"

    @classmethod
    def from_skin_settings(cls):
        """Create config from current skin settings."""
        recent_days = xbmc.getInfoLabel("Skin.String(altus_digital_release_window)") or "7"
        expired_days = xbmc.getInfoLabel("Skin.String(altus_digital_expired_window)") or "21"
        return cls(recent_days=recent_days, expired_days=expired_days)

    def has_smart_status_settings_changes(self, other_config):
        """Check if recent_days or expired_days have changed."""
        return (self.recent_days != other_config.recent_days or
                self.expired_days != other_config.expired_days)


class RatingsMonitor:
    """Monitors and manages media ratings."""
    def __init__(self, database: RatingsDatabase, home_window: xbmcgui.Window):
        self.database = database
        self.home_window = home_window
        self.get_infolabel = xbmc.getInfoLabel
        self.tmdb_client = TMDbClient(TMDB_API_KEY)
        self.mdblist_client = MDbListClient("", self.database)
        self.last_set_id = None
        self.pending_id = None
        self.last_trailer_id = None
        self.current_ratings_thread = None
        self._rating_lock = Lock()
        self.config = ReleaseWindowConfig.from_skin_settings()


    def process_current_item(self) -> None:
        """Process the current media item."""
        self._check_smart_status_setting_changes()
        meta = self._get_current_item_meta()
        if not meta:
            return
        media_id = meta.get("id")
        if not media_id:
            return
        self._handle_trailer_update(media_id)
        if media_id != self.last_set_id or media_id != self.pending_id:
            self._process_ratings(media_id, meta)

    def _check_smart_status_setting_changes(self):
        current_config = ReleaseWindowConfig.from_skin_settings()
        if self.config.has_smart_status_settings_changes(current_config):
            self.config = current_config
            self.database.delete_all_ratings(silent=True)
            self.last_set_id = None
            self.pending_id = None
            self.last_trailer_id = None
            xbmcgui.Dialog().notification(
                "Smart status settings change detected",
                "Ratings cache cleared",
                "special://skin/resources/icon.jpg",
                3000
            )


    def _process_ratings(self, media_id: str, meta: Dict[str, Any]) -> None:
        """Process ratings for the current item."""
        with self._rating_lock:
            cached_ratings = self.home_window.getProperty(
                f"altus.cachedRatings.{media_id}"
            )
            if cached_ratings:
                self._set_ratings_from_cache(media_id, cached_ratings)
                return
            cached_data = self.database.get_cached_ratings(media_id)
            if cached_data:
                self._set_cached_property(media_id, json.dumps(cached_data))
                self._update_window_properties(cached_data)
                self.last_set_id = cached_data.get("imdbid") or media_id
                return

            # If no cache found anywhere or cached data is expired, fetch new data
            self._start_new_ratings_thread(media_id, meta)

    def _start_new_ratings_thread(self, media_id: str, meta: Dict[str, Any]) -> None:
        """Start a new thread to fetch ratings."""
        if self.current_ratings_thread and self.current_ratings_thread.is_alive():
            if self.pending_id != media_id:
                self.pending_id = None

        if self.pending_id != media_id:
            self.pending_id = media_id
            self.current_ratings_thread = Thread(
                target=self._fetch_ratings_thread, args=(media_id, meta)
            )
            self.current_ratings_thread.daemon = True
            self.current_ratings_thread.start()

    def _fetch_ratings_thread(self, media_id: str, meta: Dict[str, Any]) -> None:
        """Thread worker to fetch and process ratings with enhanced ID handling."""
        try:
            if media_id != self.pending_id:
                return

            self.mdblist_client.api_key = self.get_infolabel("Skin.String(mdblist_api_key)")
            client = self.mdblist_client

            imdb_id = meta.get("imdb_id")
            tmdb_id = meta.get("tmdb_id")

            # Always prefer using IMDb ID for fetching ratings if available
            lookup_id = imdb_id if imdb_id else tmdb_id
            if not lookup_id:
                lookup_id = media_id

            result = client.get_ratings_from_api(
                lookup_id, meta.get("media_type", "movie"), config=self.config
            )

            if media_id != self.pending_id:
                return

            if result:
                # Always preserve known IDs
                if imdb_id:
                    result["imdbid"] = imdb_id
                if tmdb_id:
                    result["tmdbid"] = tmdb_id

                self._cache_ratings(media_id, result)
                self._update_window_properties(result)
                self.last_set_id = result.get("imdbid") or media_id
        except Exception as e:
            xbmc.log(f"Error fetching ratings: {str(e)}", xbmc.LOGERROR)

    def _cache_ratings(self, primary_id: str, result: Dict[str, Any]) -> None:
        """Cache ratings in both database and window properties."""
        self.database.update_ratings(primary_id, result)

        imdb_id = result.get("imdbid")
        tmdb_id = result.get("tmdbid")
        payload = json.dumps(result)

        if imdb_id:
            self._set_cached_property(imdb_id, payload)
        if tmdb_id:
            self._set_cached_property(tmdb_id, payload)

    def _set_cached_property(self, media_id: str, payload: str) -> None:
        """Write a per-item cache property and register the id for later cleanup."""
        self.home_window.setProperty(f"altus.cachedRatings.{media_id}", payload)
        try:
            index_raw = self.home_window.getProperty(CACHED_IDS_INDEX_PROP)
            ids = set(json.loads(index_raw)) if index_raw else set()
            if media_id not in ids:
                ids.add(media_id)
                self.home_window.setProperty(CACHED_IDS_INDEX_PROP, json.dumps(list(ids)))
        except (ValueError, json.JSONDecodeError):
            self.home_window.setProperty(CACHED_IDS_INDEX_PROP, json.dumps([media_id]))

    def _update_window_properties(self, result: Dict[str, Any]) -> None:
        """Update window properties with new ratings data."""
        for key, value in result.items():
            if isinstance(value, (str, int, float)):
                self.home_window.setProperty(f"altus.{key}", str(value))

    def _clear_ratings_properties(self) -> None:
        """Clear all ratings properties."""
        for key, value in EMPTY_RATINGS.items():
            self.home_window.setProperty(f"altus.{key}", str(value))
        self.last_set_id = None
        self.pending_id = None

    @staticmethod
    def clear_properties_static(home_window):
        """Clear all ratings properties."""
        # List of all rating properties to clear
        for key, value in EMPTY_RATINGS.items():
            home_window.setProperty(f"altus.{key}", str(value))

    @staticmethod
    def clear_cached_props_static(home_window):
        """Clear every per-item cachedRatings.{id} property using the index registry."""
        index_raw = home_window.getProperty(CACHED_IDS_INDEX_PROP)
        if index_raw:
            try:
                for media_id in json.loads(index_raw):
                    home_window.clearProperty(f"altus.cachedRatings.{media_id}")
            except (ValueError, json.JSONDecodeError):
                pass
        home_window.clearProperty(CACHED_IDS_INDEX_PROP)


    def _get_current_item_meta(self) -> Optional[Dict[str, Any]]:
        """Get metadata for the current item."""
        dbtype = self.get_infolabel("ListItem.DBTYPE").lower()
        path = self.get_infolabel("ListItem.Path")
        if dbtype in ["movie", "tvshow"]:
            self.home_window.setProperty("CurrentDBType", dbtype)
        else:
            if not xbmc.getCondVisibility("Window.IsVisible(contextmenu) | Window.IsVisible(movieinformation)"):
                self.home_window.clearProperty("CurrentDBType")
        if not (dbtype in ["movie", "tvshow", "episode", "season"] or
            path.startswith("plugin://plugin.video.mediafusion")):
            return None

        # Try direct ID lookup first
        imdb_id = self.get_infolabel("ListItem.IMDBNumber") or self.get_infolabel(
            "ListItem.Property(imdb)"
        )
        tmdb_id = self.get_infolabel(
            "ListItem.Property(TMDb_ID)"
        ) or self.get_infolabel("ListItem.Property(tmdb)")

        if imdb_id and imdb_id.startswith("tt"):
            return {"id": imdb_id}
        elif tmdb_id:
            return {"id": tmdb_id, "media_type": self._get_media_type()}

        # Fallback to title lookup
        title = self.get_infolabel("ListItem.Label")
        if not title:
            return None

        meta = {
            "title": title,
            "premiered": self.get_infolabel("ListItem.Premiered"),
            "media_type": self._get_media_type(),
        }

        found_imdb_id, found_tmdb_id = self._lookup_imdb_id(meta)
        if not (found_imdb_id or found_tmdb_id):
            return None

        return {
            "id": found_imdb_id if found_imdb_id else found_tmdb_id,
            "media_type": meta["media_type"],
            "imdb_id": found_imdb_id,
            "tmdb_id": found_tmdb_id,
        }

    def _get_media_type(self) -> str:
        """Determine media type from current item."""
        dbtype = self.get_infolabel("ListItem.DBTYPE").lower()
        return "movie" if dbtype == "movie" else "tv"

    def _lookup_imdb_id(
        self, meta: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        """Lookup IMDb ID and TMDb ID for given metadata."""
        title = meta.get("title")
        if not title:
            return None, None

        premiered = meta.get("premiered")
        media_type = meta.get("media_type", "movie")

        if media_type == "tv":
            title = self._clean_tv_title(title)

        year = self._extract_year(premiered)

        # Check cache first
        cached_imdb_id, cached_tmdb_id = self.database.get_cached_ids(
            title, year, media_type
        )
        if cached_imdb_id:
            return cached_imdb_id, cached_tmdb_id

        # Try TMDb lookup
        found_imdb_id, found_tmdb_id = self.tmdb_client.search_by_info(
            title, premiered, media_type
        )

        if found_imdb_id or found_tmdb_id:
            self.database.cache_ids(
                title, year, media_type, found_imdb_id, found_tmdb_id
            )

        return found_imdb_id, found_tmdb_id

    def _clean_tv_title(self, title: str) -> str:
        """Clean TV show title by removing season information."""
        return re.sub(r"\s+season\s+\d+.*$", "", title, flags=re.IGNORECASE).strip()

    def _extract_year(self, premiered: Optional[str]) -> Optional[str]:
        """Extract year from premiered date."""
        if not premiered:
            return None

        if "/" in premiered:
            parts = premiered.split("/")
            return parts[2] if len(parts) == 3 and parts[2].isdigit() else None

        return premiered[:4] if premiered else None

    def _set_ratings_from_cache(self, media_id: str, cached_ratings: str) -> None:
        """Set ratings from cached data."""
        try:
            result = json.loads(cached_ratings)
            self._update_window_properties(result)
            self.last_set_id = media_id
        except json.JSONDecodeError:
            self._clear_ratings_properties()

    def _handle_trailer_update(self, media_id: str) -> None:
        """Handle trailer updates for the current item."""
        if media_id == self.last_set_id and media_id != self.last_trailer_id:
            trailer_url = self.get_infolabel("Window(Home).Property(altus.trailer)")
            if trailer_url:
                match = re.search(VIDEO_ID_PATTERN, trailer_url)
                if match:
                    video_id = match.group(1)
                    play_url = (
                        f"plugin://plugin.video.youtube/play/?video_id={video_id}"
                    )
                    xbmc.executebuiltin(
                        f"Skin.SetString(TrailerPlaybackURL,{play_url})"
                    )
                    self.last_trailer_id = media_id
