# -*- coding: utf-8 -*-
import os
import re
import sqlite3 as database
import xbmcvfs

settings_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.altus.helper/"
)
database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.altus.helper/widget_config.db"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    onclick TEXT DEFAULT '',
    icon TEXT DEFAULT '',
    visible TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS widgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    path TEXT NOT NULL,
    label TEXT NOT NULL,
    display_type TEXT NOT NULL,
    is_stacked INTEGER DEFAULT 0,
    stacked_type TEXT DEFAULT '',
    target TEXT DEFAULT 'videos',
    limit_num INTEGER DEFAULT 0,
    sortby TEXT DEFAULT '',
    sortorder TEXT DEFAULT '',
    onclick TEXT DEFAULT '',
    onclick_condition TEXT DEFAULT '',
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS submenus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    label TEXT NOT NULL,
    onclick TEXT DEFAULT '',
    icon TEXT DEFAULT '',
    visible TEXT DEFAULT '',
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);
"""


VALID_COLUMNS = {
    "sections": {"name", "position", "onclick", "icon", "visible"},
    "widgets": {
        "section_id", "position", "path", "label", "display_type", "is_stacked",
        "stacked_type", "target", "limit_num", "sortby", "sortorder", "onclick",
        "onclick_condition", "visible",
    },
    "submenus": {"section_id", "position", "label", "onclick", "icon", "visible"},
}


class ConfigManager:
    def __init__(self):
        if not xbmcvfs.exists(settings_path):
            xbmcvfs.mkdir(settings_path)
        self.dbcon = database.connect(database_path, timeout=20)
        self.dbcon.execute("PRAGMA foreign_keys = ON")
        self.dbcon.row_factory = database.Row
        self.dbcur = self.dbcon.cursor()
        for statement in SCHEMA.strip().split(";"):
            statement = statement.strip()
            if statement:
                self.dbcur.execute(statement)
        self.dbcon.commit()
        self._migrate_schema()

    def _migrate_schema(self):
        """Add columns that may be missing from older databases."""
        try:
            self.dbcur.execute("SELECT visible FROM widgets LIMIT 1")
        except database.OperationalError:
            self.dbcur.execute("ALTER TABLE widgets ADD COLUMN visible TEXT DEFAULT ''")
            self.dbcon.commit()

    def close(self):
        self.dbcon.close()

    # ── Sections ──

    def add_section(self, name, onclick="", icon="", visible=""):
        max_pos = self.dbcur.execute(
            "SELECT COALESCE(MAX(position), 0) FROM sections"
        ).fetchone()[0]
        self.dbcur.execute(
            "INSERT INTO sections (name, position, onclick, icon, visible) VALUES (?, ?, ?, ?, ?)",
            (name, max_pos + 1, onclick, icon, visible),
        )
        self.dbcon.commit()
        return self.dbcur.lastrowid

    def update_section(self, section_id, **kwargs):
        if not kwargs:
            return
        self._validate_columns("sections", kwargs)
        cols = ", ".join("%s = ?" % k for k in kwargs)
        vals = list(kwargs.values()) + [section_id]
        self.dbcur.execute(
            "UPDATE sections SET %s WHERE id = ?" % cols, vals
        )
        self.dbcon.commit()

    def remove_section(self, section_id):
        self.dbcur.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        self.dbcon.commit()
        self._reorder("sections")

    def get_sections(self):
        return self.dbcur.execute(
            "SELECT * FROM sections ORDER BY position"
        ).fetchall()

    def get_section(self, section_id):
        return self.dbcur.execute(
            "SELECT * FROM sections WHERE id = ?", (section_id,)
        ).fetchone()

    def reorder_section(self, section_id, new_position):
        self._move_item("sections", section_id, new_position)

    # ── Widgets ──

    def add_widget(self, section_id, path, label, display_type, is_stacked=0,
                   stacked_type="", target="videos", limit_num=0, sortby="",
                   sortorder="", onclick="", onclick_condition=""):
        max_pos = self.dbcur.execute(
            "SELECT COALESCE(MAX(position), 0) FROM widgets WHERE section_id = ?",
            (section_id,),
        ).fetchone()[0]
        self.dbcur.execute(
            """INSERT INTO widgets
            (section_id, position, path, label, display_type, is_stacked,
             stacked_type, target, limit_num, sortby, sortorder, onclick, onclick_condition)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (section_id, max_pos + 1, path, label, display_type, is_stacked,
             stacked_type, target, limit_num, sortby, sortorder, onclick, onclick_condition),
        )
        self.dbcon.commit()
        return self.dbcur.lastrowid

    def update_widget(self, widget_id, **kwargs):
        if not kwargs:
            return
        self._validate_columns("widgets", kwargs)
        cols = ", ".join("%s = ?" % k for k in kwargs)
        vals = list(kwargs.values()) + [widget_id]
        self.dbcur.execute(
            "UPDATE widgets SET %s WHERE id = ?" % cols, vals
        )
        self.dbcon.commit()

    def remove_widget(self, widget_id):
        row = self.dbcur.execute(
            "SELECT section_id FROM widgets WHERE id = ?", (widget_id,)
        ).fetchone()
        self.dbcur.execute("DELETE FROM widgets WHERE id = ?", (widget_id,))
        self.dbcon.commit()
        if row:
            self._reorder("widgets", section_id=row["section_id"])

    def get_widgets(self, section_id):
        return self.dbcur.execute(
            "SELECT * FROM widgets WHERE section_id = ? ORDER BY position",
            (section_id,),
        ).fetchall()

    def get_widget(self, widget_id):
        return self.dbcur.execute(
            "SELECT * FROM widgets WHERE id = ?", (widget_id,)
        ).fetchone()

    def get_all_widgets(self):
        return self.dbcur.execute(
            """SELECT w.*, s.name as section_name, s.position as section_position
            FROM widgets w JOIN sections s ON w.section_id = s.id
            ORDER BY s.position, w.position"""
        ).fetchall()

    def reorder_widget(self, widget_id, new_position):
        row = self.dbcur.execute(
            "SELECT section_id FROM widgets WHERE id = ?", (widget_id,)
        ).fetchone()
        if row:
            self._move_item("widgets", widget_id, new_position, section_id=row["section_id"])

    def move_widget_to_section(self, widget_id, new_section_id):
        max_pos = self.dbcur.execute(
            "SELECT COALESCE(MAX(position), 0) FROM widgets WHERE section_id = ?",
            (new_section_id,),
        ).fetchone()[0]
        old_row = self.dbcur.execute(
            "SELECT section_id FROM widgets WHERE id = ?", (widget_id,)
        ).fetchone()
        self.dbcur.execute(
            "UPDATE widgets SET section_id = ?, position = ? WHERE id = ?",
            (new_section_id, max_pos + 1, widget_id),
        )
        self.dbcon.commit()
        if old_row:
            self._reorder("widgets", section_id=old_row["section_id"])

    # ── Submenus ──

    def add_submenu(self, section_id, label, onclick="", icon="", visible=""):
        max_pos = self.dbcur.execute(
            "SELECT COALESCE(MAX(position), 0) FROM submenus WHERE section_id = ?",
            (section_id,),
        ).fetchone()[0]
        self.dbcur.execute(
            "INSERT INTO submenus (section_id, position, label, onclick, icon, visible) VALUES (?, ?, ?, ?, ?, ?)",
            (section_id, max_pos + 1, label, onclick, icon, visible),
        )
        self.dbcon.commit()
        return self.dbcur.lastrowid

    def update_submenu(self, submenu_id, **kwargs):
        if not kwargs:
            return
        self._validate_columns("submenus", kwargs)
        cols = ", ".join("%s = ?" % k for k in kwargs)
        vals = list(kwargs.values()) + [submenu_id]
        self.dbcur.execute(
            "UPDATE submenus SET %s WHERE id = ?" % cols, vals
        )
        self.dbcon.commit()

    def remove_submenu(self, submenu_id):
        row = self.dbcur.execute(
            "SELECT section_id FROM submenus WHERE id = ?", (submenu_id,)
        ).fetchone()
        self.dbcur.execute("DELETE FROM submenus WHERE id = ?", (submenu_id,))
        self.dbcon.commit()
        if row:
            self._reorder("submenus", section_id=row["section_id"])

    def get_submenus(self, section_id):
        return self.dbcur.execute(
            "SELECT * FROM submenus WHERE section_id = ? ORDER BY position",
            (section_id,),
        ).fetchall()

    def reorder_submenu(self, submenu_id, new_position):
        row = self.dbcur.execute(
            "SELECT section_id FROM submenus WHERE id = ?", (submenu_id,)
        ).fetchone()
        if row:
            self._move_item("submenus", submenu_id, new_position, section_id=row["section_id"])

    # ── Config Snapshot ──

    def get_full_config(self):
        """Load the entire config into memory. Returns dict keyed by section id."""
        sections = self.get_sections()
        config = {}
        for section in sections:
            sid = section["id"]
            config[sid] = {
                "section": dict(section),
                "widgets": [dict(w) for w in self.get_widgets(sid)],
                "submenus": [dict(s) for s in self.get_submenus(sid)],
            }
        return config

    # ── Internal Helpers ──

    def _validate_columns(self, table, kwargs):
        invalid = set(kwargs.keys()) - VALID_COLUMNS.get(table, set())
        if invalid:
            raise ValueError("Invalid columns for %s: %s" % (table, ", ".join(invalid)))

    def _reorder(self, table, section_id=None):
        if section_id is not None:
            rows = self.dbcur.execute(
                "SELECT id FROM %s WHERE section_id = ? ORDER BY position" % table,
                (section_id,),
            ).fetchall()
        else:
            rows = self.dbcur.execute(
                "SELECT id FROM %s ORDER BY position" % table
            ).fetchall()
        for i, row in enumerate(rows, 1):
            self.dbcur.execute(
                "UPDATE %s SET position = ? WHERE id = ?" % table,
                (i, row["id"]),
            )
        self.dbcon.commit()

    def _move_item(self, table, item_id, new_position, section_id=None):
        if section_id is not None:
            rows = self.dbcur.execute(
                "SELECT id FROM %s WHERE section_id = ? ORDER BY position" % table,
                (section_id,),
            ).fetchall()
        else:
            rows = self.dbcur.execute(
                "SELECT id FROM %s ORDER BY position" % table
            ).fetchall()
        ids = [row["id"] for row in rows]
        if item_id not in ids:
            return
        ids.remove(item_id)
        new_position = max(1, min(new_position, len(ids) + 1))
        ids.insert(new_position - 1, item_id)
        for i, rid in enumerate(ids, 1):
            self.dbcur.execute(
                "UPDATE %s SET position = ? WHERE id = ?" % table,
                (i, rid),
            )
        self.dbcon.commit()


def sanitize_config_name(name):
    """Remove characters that break filenames or Kodi skin builtins."""
    # Strip parentheses (breaks filename pattern), commas (breaks Skin.SetString)
    return re.sub(r'[(),]', '', name).strip()


def list_saved_configs():
    """List all saved widget config profiles.

    Returns list of profile names found as widget_config(name).db files.
    """
    names = []
    _dirs, files = xbmcvfs.listdir(settings_path)
    pattern = re.compile(r"^widget_config\((.+)\)\.db$")
    for f in files:
        match = pattern.match(f)
        if match:
            names.append(match.group(1))
    names.sort()
    return names


def save_config_as(name):
    """Save the current widget config as a named profile."""
    dest = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % name
    )
    return xbmcvfs.copy(database_path, dest)


def load_config(name):
    """Load a named profile as the active widget config."""
    source = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % name
    )
    if not xbmcvfs.exists(source):
        return False
    return xbmcvfs.copy(source, database_path)


def delete_config(name):
    """Delete a saved widget config profile."""
    path = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % name
    )
    if xbmcvfs.exists(path):
        return xbmcvfs.delete(path)
    return False


def rename_config(old_name, new_name):
    """Rename a saved widget config profile."""
    old_path = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % old_name
    )
    new_path = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % new_name
    )
    if not xbmcvfs.exists(old_path):
        return False
    if not xbmcvfs.copy(old_path, new_path):
        return False
    xbmcvfs.delete(old_path)
    return True


def get_active_config():
    """Get the active profile name, verified against the actual file.

    Returns the profile name if the skin string is set AND the file exists,
    otherwise clears the stale skin string and returns empty string.
    """
    import xbmc
    active = xbmc.getInfoLabel("Skin.String(altus_active_widget_config)")
    if not active:
        return ""
    path = xbmcvfs.translatePath(
        "special://profile/addon_data/script.altus.helper/widget_config(%s).db" % active
    )
    if xbmcvfs.exists(path):
        return active
    # Stale reference — file doesn't exist, clear the skin string
    xbmc.executebuiltin("Skin.Reset(altus_active_widget_config)")
    return ""
