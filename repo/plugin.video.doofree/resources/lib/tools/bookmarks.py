# -*- coding: utf-8 -*-

"""Resume points for DooFree.

Kodi only remembers playback positions for items in its own library, so a plugin
has to keep them itself. Positions live in a small SQLite database in the
addon's profile folder.

Items are keyed by a hash of the *page* URL of the episode or movie, never the
resolved video URL: the resolved URL carries a session token and changes between
plays, the page URL stays the same, so it is the only thing that still matches
when you come back a week later.
"""

import hashlib
import time

try:
    from sqlite3 import dbapi2 as database
except ImportError:
    from pysqlite2 import dbapi2 as database

from resources.lib.tools import control

# Stopping earlier than this counts as "never really started" - no resume point.
MIN_RESUME_SECONDS = 30

# Watched this far into a file counts as finished: the resume point is dropped so
# the next play starts from the beginning instead of the closing credits.
WATCHED_FRACTION = 0.92

# Resume slightly before where you stopped, so you get some context back.
REWIND_SECONDS = 10


def _connect():
    """Open the bookmark database, creating it on first use.

    `control.dataPath` is a `special://` path, which sqlite3 cannot open, so it
    is translated to a real filesystem path first.
    """
    control.makeFile(control.dataPath)
    conn = database.connect(control.transPath(control.bookmarksFile), timeout=10)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS bookmark ("
        "id TEXT PRIMARY KEY, position REAL, duration REAL, "
        "name TEXT, image TEXT, updated INTEGER)"
    )
    return conn


def item_id(url):
    """Stable key for a playable item, or None when there is no usable URL."""
    if not url:
        return None
    if not isinstance(url, bytes):
        url = url.encode('utf-8')
    return hashlib.md5(url).hexdigest()


def get(url):
    """Return (position, duration) in seconds; (0, 0) when there is no resume point."""
    key = item_id(url)
    if key is None:
        return 0.0, 0.0

    try:
        conn = _connect()
        row = conn.execute(
            "SELECT position, duration FROM bookmark WHERE id = ?", (key,)
        ).fetchone()
        conn.close()
    except Exception:
        return 0.0, 0.0

    if not row:
        return 0.0, 0.0
    return float(row[0] or 0), float(row[1] or 0)


def save(url, position, duration, name='', image=''):
    """Store a resume point, or drop it when the item is (nearly) finished."""
    key = item_id(url)
    if key is None:
        return

    position = float(position or 0)
    duration = float(duration or 0)

    if position < MIN_RESUME_SECONDS:
        clear(url)
        return
    if duration > 0 and position >= duration * WATCHED_FRACTION:
        clear(url)
        return

    try:
        conn = _connect()
        conn.execute(
            "REPLACE INTO bookmark (id, position, duration, name, image, updated) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (key, position, duration, name, image, int(time.time())),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def clear(url):
    """Forget the resume point for one item."""
    key = item_id(url)
    if key is None:
        return
    try:
        conn = _connect()
        conn.execute("DELETE FROM bookmark WHERE id = ?", (key,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def clear_all():
    """Forget every resume point."""
    try:
        conn = _connect()
        conn.execute("DELETE FROM bookmark")
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def resume_offset(position):
    """Where playback should actually start when resuming."""
    return max(0.0, float(position) - REWIND_SECONDS)


def time_label(seconds):
    """Format seconds as H:MM:SS, or M:SS when under an hour."""
    seconds = int(float(seconds or 0))
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return '%d:%02d:%02d' % (hours, minutes, secs)
    return '%d:%02d' % (minutes, secs)
