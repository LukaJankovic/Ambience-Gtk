# Ambience
Gtk (Handy) app to control LIFX smart lights using the [lifxlan](https://github.com/mclarkk/lifxlan) api.

![Screenshot](https://raw.githubusercontent.com/LukaJankovic/Ambience/stable/screenshots/window-tiles.png)
![Screenshot](https://raw.githubusercontent.com/LukaJankovic/Ambience/stable/screenshots/window-controls.png)

<a href='https://flathub.org/apps/details/io.github.lukajankovic.ambience/'><img width='240' alt='Download on Flathub' src='https://flathub.org/assets/badges/flathub-badge-en.png'/></a>

## Installation

Ambience is available on [flathub](https://flathub.org/apps/details/io.github.lukajankovic.ambience) and on [fedora copr](https://copr.fedorainfracloud.org/coprs/lukajan/Ambience/)!

Otherwise, the raw package files are available under releases.

If not running through flatpak, remember to install the [lifxlan](https://flathub.org/apps/details/io.github.lukajankovic.ambience) api:

```
# pip3 install lifxlan
```

## Update 1.4

On the surface it might seem this update is relatively minor, simply disconnecting the groups from the lights,
allowing the user to create groups as they please. However, the theme of 1.3 has been continued, and many parts of the code have been abstracted, which took a lot of time but should make it easier to add features in the future, such as **presets / favorites** and **support for other vendors**!

## Update 1.3

With update 1.3 the UI has been reworked to allow easier management of lights in groups. This also makes adding new features in the future much easier (such as scenes etc.) **A lot of things have been changed, especially under the hood, and its difficult for me to test group features because I only have one light, so please report any bugs you encounter!**

## Configuration file
The lights are saved in `~/.config/ambience.json` with the format: 

```
{
  "version": "1.4"
  "groups": [
    {
      "label": "Group Label",
      "devices": [
        "label": "Light Label",
        "kind": "lifx"
        "data": {
          "ip": "172.16.2.xxx",
          "mac": "d0:xx:xx:xx:xx:xx",
        }
      ]
    }
  ]
}
```

This is different from previous versions, which stored lights in `~/.config/lights.json` in a different format. The old config file is converted automatically upon startup.