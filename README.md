# AutoTrackerEdit
This is a simple plugin that allows modifying trackers of a torrent automatically using regular expressions.
Trackers are changed when the plugin is enabled, when a torrent is resumed and when a torrent is added. If the regex
does not match, the tracker URLs are not affected. The `sub` method from the `re` module is used.

## Examples
This example shows how to edit the tracker from apollo.rip. A simple regex catches the domain and replaces it with
another one. The `"regex"` is what should be matched, and the `"repl"` is what replaces it. Backreferences can be used
in `"repl"`.

`~/.config/deluge/autotrackeredit.json`
```json
[
    {
        "regex": "^https?://mars.apollo.rip/",
        "repl": "http://apollo.rip:2095/"
    }
]
```

## Install
In the directory, use `make`. Upload the Python `.egg` file to your Deluge core
via whatever UI you use.
