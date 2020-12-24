Name: ambience
Version: 1.1.0
Release: 1%{?dist}
Summary: Control LIFX lights on the local network.
License: GPLv3

URL: https://github.com/LukaJankovic/Ambience/
Source0: %{url}archive/v%{version}.tar.gz

BuildRequires: meson
BuildRequires: pkgconfig(libhandy-1)

%description
Control LIFX lights on the local network. Use the discovery mode to add the lights you wish to control to your main list.

%prep

%build
%meson
%meson_build

%install
%meson_install

%check
%meson_test

%files
%{_bindir}/%{name}
%dir %{_datarootdir}/%{name}
%{_datarootdir}/glib-2.0/schemas/io.github.lukajankovic.ambience.gschema.xml
%{_datarootdir}/icons/hicolor/scalable/apps/io.github.lukajankovic.ambience.svg
%{_datarootdir}/applications/io.github.lukajankovic.ambience.desktop
%{_datarootdir}/metainfo/io.github.lukajankovic.ambience.metainfo.xml

%changelog
* Thu Dec 24 2020 Luka Jankovic <lukjan1999@gmail.com> - 
- Initial RPM spec 

