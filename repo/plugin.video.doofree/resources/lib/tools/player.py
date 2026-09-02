# -*- coding: utf-8 -*-

import xbmc

from resources.lib.tools import bookmarks, control

# How long to wait for a stream to open before giving up on resuming it.
START_TIMEOUT_SECONDS = 45

# How long to wait for the duration to become known before seeking.
SEEK_TIMEOUT_SECONDS = 20

# How often the position is sampled while playing.
POLL_SECONDS = 5


class player(xbmc.Player):
    """Player that remembers where you stopped watching.

    Kodi clears the playback position before `onPlayBackStopped` runs, so asking
    for it there returns nothing. Instead the plugin process stays alive for the
    length of the film and samples the position every few seconds; the last
    sample is what gets written when playback ends.
    """

    def __init__(self):
        xbmc.Player.__init__(self)
        self.resume_url = None
        self.name = ''
        self.image = ''
        self.current_time = 0.0
        self.total_time = 0.0
        self.finished = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def playLiveStream(self, name, url, image):
        """Play a live channel. Live TV has no position worth remembering."""
        control.playlist.clear()
        self.play(url, self._list_item(name, url, image))

    def playStream(self, name, url, image, resume_url=None):
        """Play a film or episode, offering to resume where it was stopped.

        `url` is the resolved stream (it may carry a `|Referer:` suffix for Kodi),
        `resume_url` is the stable page URL the resume point is stored under.
        """
        self.resume_url = resume_url or url
        self.name = name
        self.image = image

        position, duration = bookmarks.get(self.resume_url)

        offset = 0.0
        if position >= bookmarks.MIN_RESUME_SECONDS:
            choice = self._ask_resume(position)
            if choice is None:
                return
            if choice:
                offset = bookmarks.resume_offset(position)

        item = self._list_item(name, url, image)
        if offset:
            # ResumeTime/TotalTime is what Kodi's own player reads; the explicit
            # seek in _monitor covers the streams where it is ignored.
            item.setProperty('ResumeTime', str(offset))
            item.setProperty('TotalTime', str(duration if duration else offset + 1))
            item.setProperty('StartOffset', str(offset))

        control.playlist.clear()
        self.play(url, item)
        self._monitor(offset)

    # ------------------------------------------------------------------
    # Kodi callbacks
    # ------------------------------------------------------------------

    def onPlayBackEnded(self):
        """Reached the end of the file: there is nothing left to resume."""
        self.finished = True
        if self.resume_url:
            bookmarks.clear(self.resume_url)

    def onPlayBackError(self):
        self.finished = True

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _ask_resume(self, position):
        """True to resume, False to start over, None when the user backed out."""
        choice = control.dialog.contextmenu([
            'Resume from %s' % bookmarks.time_label(position),
            'Play from beginning',
        ])
        if choice < 0:
            return None
        return choice == 0

    def _list_item(self, name, url, image):
        item = control.item(label=name, path=url)
        if image:
            item.setArt({'icon': image, 'thumb': image, 'poster': image})
        item.setInfo(type='Video', infoLabels={'title': name})
        item.setProperty('IsPlayable', 'true')
        return item

    def _monitor(self, offset):
        """Follow the playback until it stops, remembering the last position."""
        monitor = xbmc.Monitor()

        if not self._wait_for_playback(monitor):
            return

        if offset:
            self._seek(offset, monitor)

        while self.isPlayingVideo() and not self.finished:
            try:
                self.current_time = self.getTime()
                self.total_time = self.getTotalTime()
            except Exception:
                pass
            if monitor.waitForAbort(POLL_SECONDS):
                break

        self._store()

    def _wait_for_playback(self, monitor):
        """Wait for the stream to actually open; Thai sources can be slow."""
        waited = 0.0
        while waited < START_TIMEOUT_SECONDS:
            if self.isPlayingVideo():
                return True
            if self.finished or monitor.waitForAbort(0.5):
                return False
            waited += 0.5
        return False

    def _seek(self, offset, monitor):
        """Jump to the resume point once the duration is known."""
        waited = 0.0
        while waited < SEEK_TIMEOUT_SECONDS:
            try:
                if self.getTotalTime() > 0:
                    break
            except Exception:
                pass
            if monitor.waitForAbort(0.5):
                return
            waited += 0.5

        try:
            # Kodi may already have honoured ResumeTime; only seek if it did not.
            if self.getTime() < offset - 5:
                self.seekTime(offset)
        except Exception:
            pass

    def _store(self):
        if self.finished or not self.resume_url or self.current_time <= 0:
            return
        bookmarks.save(
            self.resume_url, self.current_time, self.total_time, self.name, self.image
        )
