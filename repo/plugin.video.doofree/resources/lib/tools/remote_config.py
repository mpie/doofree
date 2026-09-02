# -*- coding: utf-8 -*-

"""Channel and category lists, fetched from the repository at runtime.

These change far more often than the code does: a live channel moves to another
URL, a category is added. Keeping them in the addon meant a release and a
download for every viewer just to fix one URL, so they live in a JSON file next
to the repository index instead. Editing and pushing that file is enough.

Three levels of fallback, in order: a fresh copy in the addon profile, whatever
the repository serves, and the copy shipped inside the addon. A file that fails
to parse or is missing its lists is ignored at every level, so a bad edit
degrades to the previous behaviour instead of an empty menu.
"""

import json
import os
import time

from resources.lib.tools import client, control

CONFIG_URL = 'https://raw.githubusercontent.com/mpie/doofree/master/repo/config/doofree.json'

# The schema the addon understands. A file declaring anything else is ignored.
SCHEMA = 1

# How long a downloaded copy is used before asking the repository again.
CACHE_HOURS = 6

# Seconds to wait for the repository before giving up and using what we have.
FETCH_TIMEOUT = 10

_cache_file = os.path.join(control.transPath(control.dataPath), 'config.json')
_bundled_file = os.path.join(control.transPath(control.addonInfo('path')),
                             'resources', 'data', 'channels.json')

_loaded = None


def load():
    """Return the configuration, never raising and never returning None."""
    global _loaded
    if _loaded is not None:
        return _loaded

    _loaded = _fresh_cache() or _from_repository() or _stale_cache() or _bundled() or _empty()
    return _loaded


def live_channels():
    return load().get('live', [])


def categories():
    return load().get('categories', [])


# ----------------------------------------------------------------------------
# Sources, tried in order
# ----------------------------------------------------------------------------

def _fresh_cache():
    """The downloaded copy, while it is still young enough to trust."""
    try:
        age = time.time() - os.path.getmtime(_cache_file)
        if age > CACHE_HOURS * 3600:
            return None
    except OSError:
        return None
    return _read(_cache_file)


def _stale_cache():
    """An old downloaded copy still beats nothing when the network is down."""
    return _read(_cache_file)


def _from_repository():
    try:
        raw = client.request(CONFIG_URL, timeout=str(FETCH_TIMEOUT))
        data = _valid(json.loads(raw))
    except Exception:
        return None

    if data:
        _write_cache(raw)
    return data


def _bundled():
    return _read(_bundled_file)


def _empty():
    return {'live': [], 'categories': []}


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _read(path):
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return _valid(json.load(handle))
    except Exception:
        return None


def _write_cache(raw):
    try:
        control.makeFile(control.dataPath)
        if isinstance(raw, bytes):
            raw = raw.decode('utf-8')
        with open(_cache_file, 'w', encoding='utf-8') as handle:
            handle.write(raw)
    except Exception:
        pass


def _valid(data):
    """Return the config only if it is actually usable, else None."""
    if not isinstance(data, dict):
        return None
    if data.get('schema') != SCHEMA:
        return None

    live = [c for c in data.get('live', [])
            if isinstance(c, dict) and c.get('name') and c.get('url')]
    cats = [c for c in data.get('categories', [])
            if isinstance(c, dict) and c.get('name') and c.get('catid')]

    # A config that lists neither is a broken edit, not an intentional one.
    if not live and not cats:
        return None

    return {'live': live, 'categories': cats}
