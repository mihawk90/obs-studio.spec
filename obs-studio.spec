%global __brp_check_rpaths %{nil}
# bytecompile with Python 3
%global __python %{__python3}

%global version_cef 5060
%global version_aja v16.2-bugfix5

%ifarch %{power64}
# LuaJIT is not available for POWER
%bcond_with lua_scripting
%else
%bcond_without lua_scripting
%endif

Name:           obs-studio
Version:        30.0.0~rc1
Release:        11%{?dist}
Summary:        Open Broadcaster Software Studio

License:        GPLv2+
URL:            https://obsproject.com/
Source0:        https://github.com/obsproject/obs-studio/archive/%{version}/%{name}-%{version}.tar.gz
Source3:        https://cdn-fastly.obsproject.com/downloads/cef_binary_%{version_cef}_linux64.tar.bz2
Source4:        https://github.com/aja-video/ntv2/archive/refs/tags/%{version_aja}.tar.gz

BuildRequires:  gcc
BuildRequires:  cmake >= 3.0
BuildRequires:  ninja-build
BuildRequires:  libappstream-glib

BuildRequires:  alsa-lib-devel
BuildRequires:  asio-devel
BuildRequires:  desktop-file-utils
BuildRequires:  fdk-aac-free-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  jansson-devel
BuildRequires:  json-devel
BuildRequires:  libcurl-devel
BuildRequires:  libdatachannel-devel
BuildRequires:  libdrm-devel
%if 0%{?fedora}
BuildRequires:  libftl-devel
%endif
BuildRequires:  libGL-devel
BuildRequires:  libqrcodegencpp-devel
BuildRequires:  libuuid-devel
BuildRequires:  libv4l-devel
BuildRequires:  libva-devel
BuildRequires:  libX11-devel
BuildRequires:  libxcb-devel
BuildRequires:  libXcomposite-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libxkbcommon-devel
%if %{with lua_scripting}
BuildRequires:  luajit-devel
%endif
BuildRequires:  mbedtls-devel
BuildRequires:  oneVPL-devel
BuildRequires:  pciutils-devel
BuildRequires:  pipewire-devel
BuildRequires:  pipewire-jack-audio-connection-kit-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  python3-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qtwayland-devel
BuildRequires:  speexdsp-devel
BuildRequires:  swig
BuildRequires:  systemd-devel
BuildRequires:  vlc-devel
BuildRequires:  wayland-devel
BuildRequires:  websocketpp-devel
BuildRequires:  x264-devel

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       ffmpeg
Requires:       x264

# CEF dependencies, both for compiling Browser Source and running it
%define cef_runtime_deps nss, nss-util, nspr, atk, at-spi2-atk, libXrandr, at-spi2-core, libXdamage

BuildRequires: %{cef_runtime_deps}
Requires:      %{cef_runtime_deps}

%description
Open Broadcaster Software is free and open source
software for video recording and live streaming.

%package libs
Summary: Open Broadcaster Software Studio libraries
%{?_qt5:Requires: %{_qt5}%{?_isa} = %{_qt5_version}}

%description libs
Library files for Open Broadcaster Software

%package devel
Summary: Open Broadcaster Software Studio header files
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Header files for Open Broadcaster Software


%prep
%autosetup -p1 -n %{name}

# rpmlint reports E: hardcoded-library-path
# replace OBS_MULTIARCH_SUFFIX by LIB_SUFFIX
sed -i 's|OBS_MULTIARCH_SUFFIX|LIB_SUFFIX|g' cmake/Modules/ObsHelpers.cmake

# remove -Werror flag to mitigate FTBFS with ffmpeg 5.1
sed -i 's|-Werror-implicit-function-declaration||g' CMakeLists.txt

## remove Werror to fix compile error
# there's probably a cleaner way to do this by modifying what compile flags
# the rpmbuilder adds
sed -i 's|    -Werror||g' cmake/Modules/CompilerConfig.cmake

# unpack CEF wrapper
mkdir -p %{_builddir}/SOURCES/CEF
tar -xjf %{SOURCE3} -C %{_builddir}/SOURCES/CEF --strip-components=1

# unpack AJA Libs
mkdir -p %{_builddir}/SOURCES/AJA/source/cmake-build
tar -xf %{SOURCE4} -C %{_builddir}/SOURCES/AJA/source --strip-components=1
# compile AJA libs
cd %{_builddir}/SOURCES/AJA/source/cmake-build
cmake -DCMAKE_BUILD_TYPE=Release -GNinja -DCMAKE_INSTALL_PREFIX=%{_builddir}/SOURCES/AJA/install ..
ninja -f build.ninja
cmake --install ajalibraries/ajantv2


%build
%cmake -DOBS_VERSION_OVERRIDE=%{version_no_tilde} \
       -DUNIX_STRUCTURE=1 -GNinja \
       -DBUILD_FOR_PPA=ON \
       -DENABLE_NEW_MPEGTS_OUTPUT=OFF \
%if ! %{with lua_scripting}
       -DDISABLE_LUA=ON \
%endif
       -DOpenGL_GL_PREFERENCE=GLVND \
       -DCMAKE_PREFIX_PATH="%{_builddir}/SOURCES/AJA/install" \
       -DBUILD_BROWSER=ON -DCEF_ROOT_DIR="%{_builddir}/SOURCES/CEF" \
       -DTWITCH_CLIENTID='' \
       -DTWITCH_HASH='' \
       -DRESTREAM_CLIENTID='' \
       -DRESTREAM_HASH='' \
       -DYOUTUBE_CLIENTID='' \
       -DYOUTUBE_CLIENTID_HASH='' \
       -DYOUTUBE_SECRET='' \
       -DYOUTUBE_SECRET_HASH=''
%cmake_build


%install
%cmake_install

# Add missing files to enable the build of obs-ndi
install -Dm644 UI/obs-frontend-api/obs-frontend-api.h %{buildroot}%{_includedir}/obs/

# copy CEF license because we need to distribute it with the binary
cp %{_builddir}/SOURCES/CEF/LICENSE.txt cef_license.txt


%check
/usr/bin/desktop-file-validate %{buildroot}/%{_datadir}/applications/com.obsproject.Studio.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/metainfo/*.appdata.xml

%files
%doc README.rst
%license UI/data/license/gplv2.txt
%license COPYING
%license cef_license.txt
%{_bindir}/obs
%{_bindir}/obs-ffmpeg-mux
%{_datadir}/metainfo/com.obsproject.Studio.appdata.xml
%{_datadir}/applications/com.obsproject.Studio.desktop
%{_datadir}/icons/hicolor/*/apps/com.obsproject.Studio.*
%{_datadir}/obs/

%files libs
%{_libdir}/obs-plugins/
%{_libdir}/obs-scripting/
# unversioned so files packaged for third-party plugins (cf. rfbz#5999)
%{_libdir}/*.so
%{_libdir}/*.so.*

%files devel
%{_libdir}/cmake/libobs/
%{_libdir}/cmake/obs-frontend-api/
%{_libdir}/pkgconfig/libobs.pc
%{_includedir}/obs/

%changelog
* Sat Oct 14 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~rc1-11
- Update to 30.0.0~rc1

* Sat Sep 16 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~beta3-13
- Rebuild for new libdatachannel

* Wed Sep 13 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~beta3-12
- Enabled WebRTC
- Added libdatachannel-devel (thanks Neal Gompa)

* Sun Sep 10 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~beta3-11
- Update to 30.0.0~beta3
- Added libqrcodegencpp-devel

* Sun Aug 20 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~beta2-11
- Update to 30.0.0~beta2

* Thu Aug 17 2023 Tarulia <mihawk.90+git@googlemail.com> - 30.0.0~beta1-11
- Update to 30.0.0~beta1
- Removed Qt5 path due to removal from OBS
- Added oneVPL-devel
- Disable WebRTC until we figure out how to go about libdatachannel

* Sat Jul 08 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.3-12
- exclude libftl-devel from RHEL builds since it's not available;
  OBS uses the in-tree FTL-SDK instead

* Mon Jun 19 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.3-11
- Update to 29.1.3

* Sun May 28 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.2-11
- Update to 29.1.2

* Wed May 10 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.1-11
- Update to 29.1.1

* Wed May 03 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0-11
- Update to 29.1.0

* Wed Apr 26 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0~rc1-11
- Update to 29.1.0~rc1

* Wed Apr 19 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0~beta4-12
- Rebuild for new Qt5

* Fri Apr 14 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0~beta4-11
- Update to 29.1.0~beta4

* Thu Apr 06 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0~beta3-11
- Update to 29.1.0~beta3

* Wed Mar 29 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.1.0~beta1-11
- Update to 29.1.0~beta1
- added asio, json, libuuid, and websocketpp build dependencies
- added quick and dirty workaround for compile error

* Sun Feb 12 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.0.2-12
- Rebuild for new Qt5

* Sat Feb 04 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.0.2-11
- Update to 29.0.2

* Mon Jan 16 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.0.0-12
- Rebuild for new qt5

* Sat Jan 07 2023 Tarulia <mihawk.90+git@googlemail.com> - 29.0.0-11
- Update to 29.0.0

* Sat Nov 26 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.1.2-12
- Bump release after merge

* Thu Nov 17 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 28.1.2-2
- Rebuilt due to Qt update.

* Sun Nov 13 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.1.2-11
- Bump release after merge

* Sun Nov 06 2022 Leigh Scott <leigh123linux@gmail.com> - 28.1.2-1
- Update to 28.1.2

* Thu Nov 03 2022 Leigh Scott <leigh123linux@gmail.com> - 28.1.1-1
- Update to 28.1.1

* Tue Nov 01 2022 Leigh Scott <leigh123linux@gmail.com> - 28.1.0-1
- Update to 28.1.0

* Tue Nov 01 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.1.0-11
- Update to 28.1.0

* Fri Oct 21 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.1.0~rc1-11
- Update to 28.1.0-rc1

* Wed Oct 12 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.1.0~beta1-11
- Update to 28.1.0-beta1

* Mon Oct 03 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.3-1
- Update to 28.0.3

* Sat Oct 01 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.0.3-11
- Update to 28.0.3
- Remove patch as it is now upstream

* Fri Sep 30 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.0.2-13
- re-enable obs-websocket

* Thu Sep 29 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.0.2-12
- Rebuild for new qt5

* Mon Sep 26 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.2-1
- Update to 28.0.2
- Enable jack (rfbz#6419)

* Sun Sep 25 2022 Tarulia <mihawk.90+git@googlemail.com> - 28.0.2-11
- Update to 28.0.2
- remove submodule downloads (they are now handled in the build script)
- adjust AJA compilation and related flags for new build system

* Tue Sep 13 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.1-4
- Use qt6 for rawhide only

* Tue Sep 13 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.1-3
- Fix wrong svg names

* Tue Sep 13 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.1-2
- touch the missing sub-modules instead

* Tue Sep 13 2022 Leigh Scott <leigh123linux@gmail.com> - 28.0.1-1
- Update to 28.0.1
- Remove vst sub-module as it's qt5 only
- Add browser and websocket sub-modules so the source compiles
  Upstream can fix their own mess!

* Sun Aug 07 2022 RPM Fusion Release Engineering <sergiomb@rpmfusion.org> - 27.2.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild and ffmpeg
  5.1

* Sat Jul 23 2022 Leigh Scott <leigh123linux@gmail.com> - 27.2.4-4
- Rebuild for new qt5

* Sat Jun 25 2022 Robert-André Mauchin <zebob.m@gmail.com> - 27.2.4-3
- Rebuilt for Python 3.11

* Sun Jun 12 2022 Sérgio Basto <sergio@serjux.com> - 27.2.4-2
- Mass rebuild for x264-0.164

* Sun Apr 17 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.4-13
- Added support for AJA cards

* Sat Apr 16 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.4-12
- Bump release after merge

* Mon Apr 11 2022 Leigh Scott <leigh123linux@gmail.com> - 27.2.4-1
- Update to 27.2.4

* Thu Mar 31 2022 Leigh Scott <leigh123linux@gmail.com> - 27.2.1-2
- Rebuild for new qt

* Tue Mar 29 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.4-11
- Update to 27.2.4

* Thu Mar 17 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.2-11
- Update to 27.2.2

* Sat Feb 26 2022 Neal Gompa <ngompa@fedoraproject.org> - 27.2.1-1
- Update to 27.2.1
- Disable Lua scripting for POWER to fix ppc64le build
- Drop legacy Fedora and EL8 stuff

* Thu Feb 24 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.1-11
- Update to 27.2.1
- bump obs-browser commit
- bump obs-vst commit

* Mon Feb 14 2022 Neal Gompa <ngompa@fedoraproject.org> - 27.2.0-1
- Update to 27.2.0 final

* Tue Feb 08 2022 Neal Gompa <ngompa@fedoraproject.org> - 27.2.0~rc4-1
- Update to 27.2.0~rc4

* Mon Feb 07 2022 Leigh Scott <leigh123linux@gmail.com> - 27.2.0~rc1-1
- Update to 27.2.0~rc1

* Mon Jan 31 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.0~rc1-11
- Update to 27.2.0-rc1
- bump obs-browser commit
- bump obs-vst commit

* Mon Jan 24 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.0~beta4-11
- Update to 27.2.0-beta4
- bump obs-browser commit
- bump obs-vst commit

* Tue Jan 11 2022 Tarulia <mihawk.90+git@googlemail.com> - 27.2.0~beta3-11
- Update to 27.2.0-beta3
- bump obs-browser commit
- bump obs-vst commit

* Fri Dec 31 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.2.0~beta2-11
- Update to 27.2.0-beta2

* Thu Dec 30 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.2.0~beta1-11
- Update to 27.2.0-beta1
- added libxkbcommon-devel and pciutils-devel
- fix file list to accomodate for new icons
- bump obs-browser commit
- bump obs-vst commit
- bump CEF version

* Wed Dec 01 2021 Nicolas Chauvet <kwizart@gmail.com> - 27.1.3-2
- Rebuilt

* Wed Oct 06 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.3-11
- version-release bump to 11
- bump obs-browser commit

* Tue Oct 05 2021 Neal Gompa <ngompa@fedoraproject.org> - 27.1.3-1
- Update to 27.1.3

* Wed Sep 29 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.1-11
- version-release bump to 11

* Tue Sep 28 2021 Neal Gompa <ngompa@fedoraproject.org> - 27.1.1-1
- Bump to 27.1.1 final

* Tue Sep 28 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.0-11
- Update to 27.1.0
- bump obs-browser commit
- bump obs-vst commit

* Sat Sep 18 2021 Neal Gompa <ngompa@fedoraproject.org> - 27.1.0~rc3-2
- Backport fix for PipeWire screencasting on F35+

* Sat Sep 18 2021 Neal Gompa <ngompa@fedoraproject.org> - 27.1.0~rc3-1
- Update to 27.1.0~rc3

* Fri Sep 17 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.0~rc3-11
- Update to 27.1.0~rc3

* Sat Sep 11 2021 Neal Gompa <ngompa@fedoraproject.org> - 27.1.0~rc2-1
- Update to 27.1.0~rc2

* Mon Sep 06 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.0~rc2-11
- Update to 27.1.0~rc2

* Sat Aug 28 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.1.0~rc1-11
- Update to 27.1.0~rc1
- removed patch from 27.0.1-2 as it was merged upstream, see obsproject/obs-studio#4936
- Bump obs-browser submodule along with 27.1.0~rc1
- added YouTube integration compile flags

* Sat Aug 28 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.1-12
- version-release bump to 12

* Tue Aug 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 27.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sun Jul 11 2021 Sérgio Basto <sergio@serjux.com> - 27.0.1-3
- Mass rebuild for x264-0.163

* Sat Jun 26 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.1-2
- Backport fix for cursor positioning in Wayland screencasting

* Sun Jun 13 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.1-11
- version-release bump to 11

* Sat Jun 12 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.1-1
- Update to 27.0.1

* Tue Jun 08 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0-11
- Bump obs-browser submodule along with 27.0.0 final

* Tue Jun 01 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0-1
- Bump to 27.0.0 final
- Move unversioned so files to -libs for third-party plugins (rfbz#5999)
- Make build for EL8
- Drop legacy EL7 stuff

* Mon May 24 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc6-11
- identical to -1, release-bump for higher version only

* Mon May 24 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0~rc6-1
- Bump to 27.0.0~rc6

* Thu May 20 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0~rc5-1
- Bump to 27.0.0~rc5
- Drop upstreamed patch for building jack plugin

* Tue May 18 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc5-11
- Bump to 27.0.0~rc5
- Bump obs-vst submodule along with RC5

* Fri May 14 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc4-11
- Bump to 27.0.0~rc4
- Bump obs-browser submodule along with RC4
- remove temporary patch introduced in rc3-1 since it was merged upstream

* Thu May 13 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc3-3
- bump release version to include merged release

* Wed May 05 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0~rc3-2
- Fix detecting pipewire-libjack so jack plugin is built

* Wed May 05 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0~rc3-1
- Bump to 27.0.0~rc3

* Mon May 03 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc3-1
- Bump to 27.0.0~rc3
- Bump obs-browser submodule along with RC3

* Sun May 02 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc2-4
- Enable Twitch and Restream Service integrations
- manual compilation requires manual filling in of Client-IDs and Hashes

* Sun Apr 25 2021 Tarulia <mihawk.90+git@googlemail.com> - 27.0.0~rc2-3
- enable compilation of Browser Plugin

* Thu Apr 22 2021 Leigh Scott <leigh123linux@gmail.com> - 27.0.0~rc2-2
- Rebuild for libftl issue (rfbz5978)

* Sat Apr 17 2021 Neal Gompa <ngompa13@gmail.com> - 27.0.0~rc2-1
- Bump to 27.0.0~rc2

* Wed Feb 10 2021 Nicolas Chauvet <kwizart@gmail.com> - 26.1.2-3
- Add obs-vst plugins
- Build for all arches (armv7hl, aarch64, ppc64le)
- Re-order build dependencies

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 26.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jan 20 2021 Martin Gansser <martinkg@fedoraproject.org> - 26.1.2-1
- Update to 26.1.2

* Tue Jan 19 2021 Martin Gansser <martinkg@fedoraproject.org> - 26.1.1-1
- Update to 26.1.1

* Fri Jan  1 2021 Leigh Scott <leigh123linux@gmail.com> - 26.1.0-2
- Rebuilt for new ffmpeg snapshot

* Sat Dec 26 2020 Momcilo Medic <fedorauser@fedoraproject.org> - 26.1.0-1
- Updated to 26.1.0

* Fri Nov 27 2020 Sérgio Basto <sergio@serjux.com> - 26.0.2-3
- Mass rebuild for x264-0.161

* Wed Oct 14 2020 Momcilo Medic <fedorauser@fedoraproject.org> - 26.0.2-2
- Bumped release for setting developer toolset version

* Wed Oct 14 2020 Momcilo Medic <fedorauser@fedoraproject.org> - 26.0.2-1
- Removed doxygen bits as upstream removed it
- Updated to 26.0.2

* Tue Aug 18 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 25.0.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Aug 06 2020 Leigh Scott <leigh123linux@gmail.com> - 25.0.8-4
- Improve compatibility with new CMake macro

* Tue Jul 07 2020 Sérgio Basto <sergio@serjux.com> - 25.0.8-3
- Mass rebuild for x264

* Sat May 30 2020 Leigh Scott <leigh123linux@gmail.com> - 25.0.8-2
- Rebuild for python-3.9

* Tue Apr 28 2020 Leigh Scott <leigh123linux@googlemail.com> - 25.0.8-1
- Updated to 25.0.8

* Thu Apr 16 2020 Leigh Scott <leigh123linux@gmail.com> - 25.0.6-1
- Updated to 25.0.6

* Mon Apr 06 2020 Momcilo Medic <fedorauser@fedoraproject.org> - 25.0.4-1
- Updated to 25.0.4

* Tue Mar 31 2020 Momcilo Medic <fedorauser@fedoraproject.org> - 25.0.3-1
- Updated to 25.0.3

* Fri Mar 20 2020 Martin Gansser <martinkg@fedoraproject.org> - 25.0.1-1
- Update to 25.0.1

* Sat Feb 22 2020 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 24.0.6-2
- Rebuild for ffmpeg-4.3 git

* Fri Feb 21 2020 Martin Gansser <martinkg@fedoraproject.org> - 24.0.6-1
- Update to 24.0.6

* Wed Feb 05 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 24.0.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Dec 22 2019 Leigh Scott <leigh123linux@googlemail.com> - 24.0.5-1
- Updated to 24.0.5

* Tue Dec 17 2019 Leigh Scott <leigh123linux@gmail.com> - 24.0.3-3
- Mass rebuild for x264

* Sun Oct 13 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 24.0.3-2
- Switched BR gcc-objc to gcc to unify SPEC file across builds

* Sat Oct 12 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 24.0.3-1
- Updated to 24.0.3

* Sun Sep 22 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 24.0.1-1
- Updated to 24.0.1

* Sat Aug 24 2019 Leigh Scott <leigh123linux@gmail.com> - 23.2.1-3
- Rebuild for python-3.8

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 23.2.1-2
- Rebuild for new ffmpeg version

* Tue Jun 18 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 23.2.1-1
- Updated to 23.2.1

* Mon Apr 08 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 23.1.0-1
- Updated to 23.1.0

* Sun Apr 07 2019 Martin Gansser <martinkg@fedoraproject.org> - 23.0.2-4
- Add obs-frontend-api.h to devel subpkg, to enable build of obs-ndi
- Add ObsPluginHelpers.cmake to devel subpkg, to enable build of obs-ndi

* Mon Mar 18 2019 Xavier Bachelot <xavier@bachelot.org> - 23.0.2-3
- Fix BR: on speex/speexdsp for EL7.
- Fix BR: on python for EL7.

* Tue Mar 12 2019 Sérgio Basto <sergio@serjux.com> - 23.0.2-2
- Mass rebuild for x264

* Sun Mar 10 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 23.0.2-1
- Updated to 23.0.2

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 23.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Feb 25 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 23.0.0-1
- Updated to 23.0.0

* Wed Jan 9 2019 Momcilo Medic <fedorauser@fedoraproject.org> - 22.0.3-3
- Fixed missing dependencies
- Enabled scripting support

* Thu Oct 04 2018 Sérgio Basto <sergio@serjux.com> - 22.0.3-2
- Mass rebuild for x264 and/or x265

* Fri Sep 7 2018 Momcilo Medic <fedorauser@fedoraproject.org> - 22.0.3-1
- Updated to 22.0.3

* Wed Aug 22 2018 Momcilo Medic <fedorauser@fedoraproject.org> - 22.0.1-1
- Updated to 22.0.1

* Fri Jul 27 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 21.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jul 10 2018 Miro Hrončok <mhroncok@redhat.com> - 21.1.2-2
- Rebuilt for Python 3.7

* Wed May 16 2018 Leigh Scott <leigh123linux@googlemail.com> - 21.1.2-1
- Update to 21.1.2
- Fix requires

* Sat Mar 31 2018 Leigh Scott <leigh123linux@googlemail.com> - 21.1.1-1
- Update to 21.1.1

* Mon Mar 19 2018 Leigh Scott <leigh123linux@googlemail.com> - 21.1.0-1
- Update to 21.1.0

* Fri Mar 09 2018 Martin Gansser <martinkg@fedoraproject.org> - 21.0.3-1
- Update to 21.0.3
- Add BR python3-devel
- Add bytecompile with Python 3 %%global __python %%{__python3}A

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 21.0.2-4
- Rebuilt for new ffmpeg snapshot

* Thu Mar 01 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 21.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Feb 08 2018 Leigh Scott <leigh123linux@googlemail.com> - 21.0.2-2
- Fix scriptlets
- Use ninja to build

* Wed Feb 07 2018 Momcilo Medic <fedorauser@fedoraproject.org> - 21.0.2-1
- Updated to 21.0.2

* Thu Jan 18 2018 Leigh Scott <leigh123linux@googlemail.com> - 20.1.3-3
- Rebuilt for ffmpeg-3.5 git

* Sun Dec 31 2017 Sérgio Basto <sergio@serjux.com> - 20.1.3-2
- Mass rebuild for x264 and x265

* Fri Dec 08 2017 Leigh Scott <leigh123linux@googlemail.com> - 20.1.3-1
- Updated to 20.1.3

* Tue Oct 17 2017 Martin Gansser <martinkg@fedoraproject.org> - 20.0.1-1
- Updated to 20.0.1

* Thu Aug 10 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 20.0.0-1
- Updated to 20.0.0

* Sat Jul 08 2017 Martin Gansser <martinkg@fedoraproject.org> - 19.0.3-1
- Updated to 19.0.3

* Mon May 22 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 19.0.2-1
- Updated to 19.0.2

* Wed May 17 2017 Leigh Scott <leigh123linux@googlemail.com> - 18.0.2-2
- Rebuild for ffmpeg update

* Sat May 6 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 18.0.2-1
- Updated to 18.0.2

* Sat Apr 29 2017 Leigh Scott <leigh123linux@googlemail.com> - 18.0.1-3
- Rebuild for ffmpeg update

* Mon Mar 20 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 18.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Mar 8 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 18.0.1-1
- Updated to 18.0.1

* Wed Mar 1 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 18.0.0-1
- Updated to 18.0.0

* Mon Jan 30 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 17.0.2-2
- Reintroduced obs-ffmpeg-mux.patch
- Fixes #4436

* Wed Jan 18 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 17.0.2-1
- Updated to 17.0.2

* Tue Jan 03 2017 Momcilo Medic <fedorauser@fedoraproject.org> - 17.0.0-1
- Upstream fixed arch-dependent-file-in-usr-share
- Removed obs-ffmpeg-mux.patch
- Updated to 17.0.0

* Sun Nov 27 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.16.6-1
- Updated to 0.16.6

* Tue Nov 08 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.16.5-1
- Updated to 0.16.5

* Tue Oct 18 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.16.2-2.20161018git4505d5a
- Updated to git to resolve unversioned shared object
- Identified speexdsp-devel as a dependency

* Sat Oct 01 2016 Martin Gansser <martinkg@fedoraproject.org> - 0.16.2-1
- Updated to 0.16.2
- Build doxygen html documentation
- Added BR doxygen

* Fri Aug 26 2016 Leigh Scott <leigh123linux@googlemail.com> - 0.15.4-3
- Actually define FFMPEG_MUX_FIXED (fixes 'command not found' when trying to record)

* Sat Aug 13 2016 Leigh Scott <leigh123linux@googlemail.com> - 0.15.4-2
- Disable build for ARM (Arm gcc has no xmmintrin.h file)

* Fri Aug 12 2016 Leigh Scott <leigh123linux@googlemail.com> - 0.15.4-1
- Fix release tag (0.x release is for git releases)

* Mon Aug 08 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.4-0.1
- Updated to 0.15.4

* Fri Aug 05 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.2-0.5
- Added alsa-devel as BR for ALSA plugin.
- Added vlc-devel as BR for VLC plugin.
- Added systemd-devel as BR for Udev V4L.

* Wed Aug 03 2016 Leigh Scott <leigh123linux@googlemail.com> - 0.15.2-0.4
- Fix source tag (spectool now downloads in n-v format)
- Remove surplus ldconfig from postun (no public .so files in main package)
- Update scriptlets to meet guidelines (need full path)

* Wed Jul 20 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.2-0.3
- Added license file gplv2.txt

* Mon Jul 18 2016 Martin Gansser <martinkg@fedoraproject.org> - 0.15.2-0.2
- Fixed arch-dependent-file-in-usr-share
- Added obs-ffmpeg-mux.patch
- Added libs subpkg
- Call ldconfig in post(un) scripts for the shared library

* Sat Jul 16 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.2-0.1
- Updated to 0.15.2

* Sun Jul 10 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.1-0.1
- Updated to 0.15.1

* Sat Jul 09 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.15.0-0.1
- Updated to 0.15.0

* Mon May 16 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.14.2-0.1
- Updated to 0.14.2

* Mon Apr 25 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.14.1-0.1
- Updated to 0.14.1

* Sun Apr 24 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.14.0-0.1
- Updated to 0.14.0

* Tue Mar 22 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.13.4-0.1
- Updated to 0.13.4

* Sun Mar 20 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.13.3-0.1
- Updated to 0.13.3

* Tue Feb 23 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.13.2-0.1
- Updated to 0.13.2

* Sat Feb 06 2016 Momcilo Medic <fedorauser@fedoraproject.org> - 0.13.1-0.1
- Updated to 0.13.1

* Sun Dec 20 2015 Martin Gansser <martinkg@fedoraproject.org> - 0.12.4-0.2
- replace OBS_MULTIARCH_SUFFIX by LIB_SUFFIX

* Sat Dec 12 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.12.4-0.1
- Updated to 0.12.4

* Sat Dec 05 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.12.3-0.1
- Updated to 0.12.3

* Sat Nov 21 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.12.2-0.1
- Updated to 0.12.2

* Thu Nov 19 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.12.1-0.1
- Updated to 0.12.1

* Thu Sep 24 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.12.0-0.1
- Updated to 0.12.0

* Mon Aug 17 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.11.4-0.1
- Added OBS_VERSION_OVERRIDE to correct version in compilation
- Updated to 0.11.4

* Sat Aug 08 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.11.3-0.1
- Updated to 0.11.3

* Thu Jul 30 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.11.2-0.1
- Updated to 0.11.2

* Fri Jul 10 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.11.1-0.1
- Updated to 0.11.1

* Wed May 27 2015 Momcilo Medic <fedorauser@fedoraproject.org> - 0.10.1-0.1
- Initial .spec file
