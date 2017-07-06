#
# core.py
#
# Copyright (C) 2009 Simon Bernier St-Pierre <sbernierstpirre@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

# from deluge.log import LOG as log
import re

import deluge.component as component
from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
# from deluge.event import known_events

# print known_events
_RE_FIX_URL = re.compile(r'^https?://mars.apollo.rip/')


def update_trackers(trackers):
    changed = False
    ntrackers = []
    for url, tier in trackers:
        new_url = _RE_FIX_URL.sub('http://apollo.rip:2095/', url)
        if new_url != url:
            changed = True
        ntrackers.append(dict(url=new_url, tier=tier))
    return ntrackers, changed


class Core(CorePluginBase):
    def enable(self):
        log.info("ApolloFix has started.")
        self._core = component.get("Core")
        self._em = component.get("EventManager")
        self._em.register_event_handler("TorrentAddedEvent",
                                        self._scan_torrent)
        self._em.register_event_handler("TorrentResumedEvent",
                                        self._scan_torrent)
        for id in self._core.get_session_state():
            self._scan_torrent(id)

    def disable(self):
        pass

    def update(self):
        pass

    def _scan_torrent(self, id):
        status = self._core.get_torrent_status(id, ["name", "tracker",
                                                    "trackers"])

        trackers = []
        if len(status['tracker']) > 0:
            trackers.append((status['tracker'], 0))

        for t in status['trackers']:
            url = t['url']
            tier = t['tier']
            if len(url) > 0:
                trackers.append((url, tier))

        new_trackers, changed = update_trackers(trackers)
        if changed:
            log.info("Updated tracker for torrent: %s." % status['name'])
            self._core.set_torrent_trackers(id, new_trackers)
