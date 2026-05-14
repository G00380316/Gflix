import sqlite3
import datetime as dt
from datetime import datetime, timedelta
import json
import time
from typing import Optional, Tuple, Dict, Any
from ..config import RATINGS_DATABASE_PATH, CACHE_DURATION_DAYS
from ..helper import calculate_cache_size
import xbmc, xbmcgui


class RatingsDatabase:
    def __init__(self):
        self.db_path = RATINGS_DATABASE_PATH
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path, timeout=60) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ratings (
                    imdb_id TEXT,
                    tmdb_id TEXT,
                    ratings TEXT,
                    last_updated TIMESTAMP,
                    PRIMARY KEY (imdb_id, tmdb_id)
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS id_mappings (
                    title TEXT,
                    year TEXT,
                    media_type TEXT,
                    imdb_id TEXT,
                    tmdb_id TEXT,
                    last_updated TIMESTAMP,
                    PRIMARY KEY (title, year, media_type)
                )
            """
            )

    def datetime_workaround(self, data, str_format):
        try:
            datetime_object = dt.datetime.strptime(data, str_format)
        except:
            datetime_object = dt.datetime(*(time.strptime(data, str_format)[0:6]))
        return datetime_object

    def get_cached_ratings(self, id_to_check: str) -> Optional[Dict[str, Any]]:
        """Get cached ratings if they exist and are not expired."""
        with sqlite3.connect(self.db_path, timeout=60) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ratings, last_updated FROM ratings 
                WHERE imdb_id=? OR tmdb_id=?
                """,
                (id_to_check, id_to_check),
            )
            result = cursor.fetchone()

            if result:
                ratings_data, last_updated = result
                last_updated_date = self.datetime_workaround(
                    last_updated, "%Y-%m-%d %H:%M:%S.%f"
                )
                if dt.datetime.now() - last_updated_date < dt.timedelta(
                    days=CACHE_DURATION_DAYS
                ):
                    return json.loads(ratings_data)
        return None

    def update_ratings(self, primary_id: str, result: Dict[str, Any]) -> None:
        """Update or insert ratings data, using primary_id as fallback."""
        # Extract IDs from result
        imdb_id = result.get(
            "imdbid", primary_id if primary_id.startswith("tt") else None
        )
        tmdb_id = result.get("tmdbid", primary_id if primary_id.isdigit() else None)
        if not imdb_id and not tmdb_id:
            return

        imdb_id = imdb_id or ""
        tmdb_id = tmdb_id or ""

        # Create a clean copy of the ratings data without IDs
        ratings_data = result.copy()
        ratings_data.pop("imdbid", None)
        ratings_data.pop("tmdbid", None)

        with sqlite3.connect(self.db_path, timeout=60) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO ratings (imdb_id, tmdb_id, ratings, last_updated)
                VALUES (?, ?, ?, ?)
                """,
                (imdb_id, tmdb_id, json.dumps(ratings_data), datetime.now()),
            )

    def get_cached_ids(
        self, title: str, year: str, media_type: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """Get cached ID mappings."""
        with sqlite3.connect(self.db_path, timeout=60) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT imdb_id, tmdb_id FROM id_mappings 
                WHERE title=? AND year=? AND media_type=?
                """,
                (title, year, media_type),
            )
            result = cursor.fetchone()
            return result if result else (None, None)

    def cache_ids(
        self,
        title: str,
        year: str,
        media_type: str,
        imdb_id: Optional[str],
        tmdb_id: Optional[str],
    ) -> None:
        """Cache ID mappings."""
        with sqlite3.connect(self.db_path, timeout=60) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO id_mappings 
                (title, year, media_type, imdb_id, tmdb_id, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    str(year) if year else "",
                    media_type,
                    imdb_id,
                    tmdb_id,
                    datetime.now(),
                ),
            )

    # def delete_all_ratings(self):
    #     with sqlite3.connect(self.db_path, timeout=60) as conn:
    #         cursor = conn.cursor()
    #     cursor.execute("DELETE FROM ratings")
    #     dialog = xbmcgui.Dialog()
    #     dialog.ok("Altus", "All ratings have been cleared from the database.")

    # def delete_all_ratings(self):
    #     dialog = xbmcgui.Dialog()
    #     if dialog.yesno("Altus", "Are you sure you want to clear all ratings?"):
    #         try:
    #             with sqlite3.connect(self.db_path, timeout=60) as conn:
    #                 cursor = conn.cursor()
    #                 cursor.execute("DELETE FROM ratings")
    #                 cursor.execute("VACUUM")
    #             dialog.ok("Altus", "All ratings have been cleared from the database.")
    #             calculate_cache_size()
    #         except Exception as e:
    #             xbmc.log(f"Error clearing ratings database: {str(e)}", 2)
    #             dialog.notification("Altus", "Error clearing ratings", xbmcgui.NOTIFICATION_ERROR)

    def delete_all_ratings(self, silent=False):
        if not silent:
            dialog = xbmcgui.Dialog()
            if not dialog.yesno("Altus", "Are you sure you want to clear all ratings?"):
                return
        try:
            with sqlite3.connect(self.db_path, timeout=60) as conn:
                cursor = conn.cursor()
                cursor.execute("DROP TABLE IF EXISTS ratings")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS ratings (
                        imdb_id TEXT,
                        tmdb_id TEXT,
                        ratings TEXT,
                        last_updated TIMESTAMP,
                        PRIMARY KEY (imdb_id, tmdb_id)
                    );
                    """
                )
                cursor.execute("VACUUM")
                home_window = xbmcgui.Window(10000)
                from modules.monitors.ratings import RatingsMonitor
                RatingsMonitor.clear_cached_props_static(home_window)
                RatingsMonitor.clear_properties_static(home_window)
                if not silent:
                    dialog = xbmcgui.Dialog()
                    dialog.ok("Altus", "All ratings have been cleared from the database.")
                calculate_cache_size()
        except Exception as e:
            xbmc.log(f"Error clearing ratings database: {str(e)}", 2)
            if not silent:
                dialog = xbmcgui.Dialog()
                dialog.notification("Altus", "Error clearing ratings", xbmcgui.NOTIFICATION_ERROR)


# import sqlite3 as database
# from datetime import datetime, timedelta
# import json
# from typing import Optional, Tuple, Dict, Any
# from .config import SETTINGS_PATH, RATINGS_DATABASE_PATH, CACHE_DURATION_DAYS
# import xbmcvfs

# class Database:
#     def __init__(self):
#         self.connect_database()

#     def connect_database(self):
#         if not xbmcvfs.exists(SETTINGS_PATH):
#             xbmcvfs.mkdir(SETTINGS_PATH)
#         self.dbcon = database.connect(RATINGS_DATABASE_PATH, timeout=60)
#         self.dbcon.execute("""
#             CREATE TABLE IF NOT EXISTS ratings (
#                 imdb_id TEXT,
#                 tmdb_id TEXT,
#                 ratings TEXT,
#                 last_updated TIMESTAMP,
#                 PRIMARY KEY (imdb_id, tmdb_id)
#             )
#         """)
#         self.dbcon.execute("""
#             CREATE TABLE IF NOT EXISTS id_mappings (
#                 title TEXT,
#                 year TEXT,
#                 media_type TEXT,
#                 imdb_id TEXT,
#                 tmdb_id TEXT,
#                 last_updated TIMESTAMP,
#                 PRIMARY KEY (title, year, media_type)
#             )
#         """)
#         self.dbcur = self.dbcon.cursor()

#     def get_cached_ratings(self, id_to_check: str) -> Optional[Dict[str, Any]]:
#         """Get cached ratings if they exist and are not expired."""
#         self.dbcur.execute(
#             """
#             SELECT ratings, last_updated FROM ratings
#             WHERE imdb_id=? OR tmdb_id=?
#             """,
#             (id_to_check, id_to_check)
#         )
#         result = self.dbcur.fetchone()

#         if result:
#             ratings_data, last_updated = result
#             last_updated_date = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S.%f")
#             if datetime.now() - last_updated_date < timedelta(days=CACHE_DURATION_DAYS):
#                 return json.loads(ratings_data)
#         return None

#     def update_ratings(self, primary_id: str, result: Dict[str, Any]) -> None:
#         """Update or insert ratings data, using primary_id as fallback."""
#         imdb_id = result.get('imdbid', primary_id if primary_id.startswith('tt') else None)
#         tmdb_id = result.get('tmdbid', primary_id if primary_id.isdigit() else None)
#         if not imdb_id and not tmdb_id:
#             return

#         self.dbcur.execute(
#             """
#             INSERT OR REPLACE INTO ratings (imdb_id, tmdb_id, ratings, last_updated)
#             VALUES (?, ?, ?, ?)
#             """,
#             (imdb_id, tmdb_id, json.dumps(result), datetime.now())
#         )
#         self.dbcon.commit()

#     def get_cached_ids(self, title: str, year: str, media_type: str) -> Tuple[Optional[str], Optional[str]]:
#         """Get cached ID mappings."""
#         self.dbcur.execute(
#             """
#             SELECT imdb_id, tmdb_id FROM id_mappings
#             WHERE title=? AND year=? AND media_type=?
#             """,
#             (title, year, media_type)
#         )
#         result = self.dbcur.fetchone()
#         return result if result else (None, None)

#     def cache_ids(self, title: str, year: str, media_type: str,
#                  imdb_id: Optional[str], tmdb_id: Optional[str]) -> None:
#         """Cache ID mappings."""
#         self.dbcur.execute(
#             """
#             INSERT OR REPLACE INTO id_mappings
#             (title, year, media_type, imdb_id, tmdb_id, last_updated)
#             VALUES (?, ?, ?, ?, ?, ?)
#             """,
#             (title, str(year) if year else "", media_type, imdb_id, tmdb_id, datetime.now())
#         )
#         self.dbcon.commit()
