# Ambience
Gtk (Handy) app to control LIFX smart lights using the [lifxlan](https://github.com/mclarkk/lifxlan) api.

![Screenshot](https://raw.githubusercontent.com/LukaJankovic/Ambience/stable/screenshots/window-full.png)

## Installation
Ambience is available on [flathub](https://flathub.org/apps/details/io.github.lukajankovic.ambience) and on [fedora copr](https://copr.fedorainfracloud.org/coprs/lukajan/Ambience/)!

Otherwise, the raw package files are available under releases.

If not running through flatpak, remember to install the [lifxlan](https://flathub.org/apps/details/io.github.lukajankovic.ambience) api:

```
# pip3 install lifxlan
```

rpm, deb (and maybe more) packages comming soon.

### Manual Configuration
The `lifxlan` package will generally take care of light discovery, but if you are unable to perform this due to firewall rules a manual configuration can be generated. 
The configuration file defaults to: `~/.config/lights.json` and is a JSON list of device mac and ip address. An example of this is as follows:

```
cat ~/.config/lights.json
[
   {
      "mac":"d0:xx:xx:xx:xx:xx",
      "ip":"192.168.1.10"
   }
]
```

## Todo
- [X] Flathub
- [X] Create rpm
- [ ] Create deb
- [ ] Show different controls for lights with different features
- [ ] Migrate to HdyFlap
- [ ] Migrate to GTK4
- [ ] Add translations (Will need help)
- [ ] ~~Edit location, group~~ Not available in API, requries more work. Postponed.