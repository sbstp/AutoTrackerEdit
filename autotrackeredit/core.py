import json
import re

import deluge.component as component
from deluge.common import get_default_config_dir
from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase


class Core(CorePluginBase):

    def enable(self):
        log.info("AutoTrackerEdit: started")

        self._edits = []
        config_path = get_default_config_dir("autotrackeredit.json")
        try:
            with open(config_path) as f:
                items = json.load(f)
                for item in items:
                    try:
                        regex = re.compile(item['regex'])
                    except re.error:
                        log.info("AutoTrackerEdit: invalid regex %s" % item['regex'])
                    else:
                        self._edits.append((regex, item['repl']))
        except IOError:
            log.error("AutoTrackerEdit: failed to open config file")

        log.info("AutoTrackerEdit: loaded %d regex from the config file", len(self._edits))

        self._core = component.get("Core")
        self._em = component.get("EventManager")
        self._em.register_event_handler("TorrentAddedEvent", self._scan_torrent)
        self._em.register_event_handler("TorrentResumedEvent", self._scan_torrent)
        for id in self._core.get_session_state():
            self._scan_torrent(id)

    def disable(self):
        self._edits = []
        self._em.deregister_event_handler("TorrentAddedEvent", self._scan_torrent)
        self._em.deregister_event_handler("TorrentResumedEvent", self._scan_torrent)

    def update(self):
        pass

    def _scan_torrent(self, id):
        status = self._core.get_torrent_status(id, ["name", "tracker", "trackers"])

        trackers = []
        if len(status['tracker']) > 0:
            trackers.append((status['tracker'], 0))

        for t in status['trackers']:
            url = t['url']
            tier = t['tier']
            if len(url) > 0:
                trackers.append((url, tier))

        new_trackers, changed = self._update_trackers(trackers)
        if changed:
            log.info("AutoTrackerEdit: updated tracker(s) for torrent: %s" % status['name'])
            self._core.set_torrent_trackers(id, new_trackers)

    def _update_trackers(self, trackers):
        changed = False
        ntrackers = []
        for url, tier in trackers:
            for regex, repl in self._edits:
                new_url = regex.sub(repl, url)
                if new_url != url:
                    changed = True
                    url = new_url
                    break
            ntrackers.append(dict(url=url, tier=tier))

        return ntrackers, changed
