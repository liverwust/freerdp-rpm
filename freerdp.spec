%global commit0 b02943ae98d76420e5d6ee801a2d54db1d28f3ef
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# Can be rebuilt with FFmpeg/H264 support enabled by passing "--with=ffmpeg" and
# "--with=x264" to mock/rpmbuild or by globally setting this:

# %%global _with_ffmpeg 1
# %%global _with_x264 1

Name:           freerdp
Version:        2.0.0
Release:        6%{?shortcommit0:.git.%{shortcommit0}}.gfdl%{?dist}
Epoch:          2
Summary:        Free implementation of the Remote Desktop Protocol (RDP)
License:        ASL 2.0
URL:            http://www.freerdp.com/

Source0:        https://github.com/FreeRDP/FreeRDP/archive/%{commit0}/FreeRDP-%{commit0}.tar.gz#/FreeRDP-%{shortcommit0}.tar.gz
Patch0:         freerdp-aarch64.patch

BuildRequires:  alsa-lib-devel
BuildRequires:  cmake >= 2.8
BuildRequires:  cups-devel
%{?_with_ffmpeg:BuildRequires:  ffmpeg-devel}
BuildRequires:  gsm-devel
BuildRequires:  gstreamer-devel
BuildRequires:  gstreamer-plugins-base-devel
BuildRequires:  openssl-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libX11-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXdamage-devel
BuildRequires:  libXext-devel
BuildRequires:  libXi-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libxkbfile-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXv-devel
BuildRequires:  pcsc-lite-devel
BuildRequires:  pulseaudio-libs-devel
%{?_with_x264:BuildRequires:  x264-devel}
BuildRequires:  xmlto
BuildRequires:  zlib-devel

Provides:       xfreerdp = %{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       libwinpr%{?_isa} = %{?epoch}:%{version}-%{release}

%description
The xfreerdp Remote Desktop Protocol (RDP) client from the FreeRDP project.

xfreerdp can connect to RDP servers such as Microsoft Windows machines, xrdp and
VirtualBox.

%package        libs
Summary:        Core libraries implementing the RDP protocol
Requires:       libwinpr%{?_isa} = %{?epoch}:%{version}-%{release}
Obsoletes:      %{name}-plugins < 1:1.1.0
Provides:       %{name}-plugins = %{?epoch}:%{version}-%{release}
%description    libs
libfreerdp-core can be embedded in applications.

libfreerdp-channels and libfreerdp-kbd might be convenient to use in X
applications together with libfreerdp-core.

libfreerdp-core can be extended with plugins handling RDP channels.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 2.8

%description    devel
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}-libs.

%package        server
Summary:        Server support for %{name}

%description    server
The %{name}-server package contains servers which can export a desktop via
the RDP protocol.

%package -n     libwinpr
Summary:        Windows Portable Runtime
Provides:       %{name}-libwinpr = %{?epoch}:%{version}-%{release}
Obsoletes:      %{name}-libwinpr < %{?epoch}:%{version}-%{release}

%description -n libwinpr
WinPR provides API compatibility for applications targeting non-Windows
environments. When on Windows, the original native API is being used instead of
the equivalent WinPR implementation, without having to modify the code using it.

%package -n     libwinpr-devel
Summary:        Windows Portable Runtime development files
Requires:       libwinpr%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 2.8

%description -n libwinpr-devel
The %{name}-libwinpr-devel package contains libraries and header files for
developing applications that use %{name}-libwinpr.

%prep
%setup -qn FreeRDP-%{commit0}
%patch0 -p1 -b .aarch64

# Rpmlint fixes
find . -name "*.h" -exec chmod 664 {} \;

%build
%cmake %{?_cmake_skip_rpath} \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DWITH_ALSA=ON \
    -DWITH_CUPS=ON \
    -DWITH_CHANNELS=ON -DSTATIC_CHANNELS=OFF \
    -DWITH_CLIENT=ON \
    -DWITH_DIRECTFB=OFF \
    %{?_with_ffmpeg:-DWITH_FFMPEG=ON} \
    -DWITH_GSM=ON \
    -DWITH_GSTREAMER_0_10=ON \
    -DWITH_IPP=OFF \
    -DWITH_JPEG=ON \
    -DWITH_MANPAGES=ON \
    -DWITH_OPENSSL=ON \
    -DWITH_PCSC=ON \
    -DWITH_PULSE=ON \
    -DWITH_SERVER=ON \
    -DWITH_X11=ON \
    -DWITH_XCURSOR=ON \
    -DWITH_XEXT=ON \
    -DWITH_XKBFILE=ON \
    -DWITH_XI=ON \
    -DWITH_XINERAMA=ON \
    -DWITH_XRENDER=ON \
    -DWITH_XV=ON \
    -DWITH_ZLIB=ON \
    %{?_with_x264:-DWITH_X264=ON} \
%ifarch x86_64
    -DWITH_SSE2=ON \
%else
    -DWITH_SSE2=OFF \
%endif
%ifarch armv7hl
    -DARM_FP_ABI=hard \
    -DWITH_NEON=OFF \
%endif
%ifarch armv7hnl
    -DARM_FP_ABI=hard \
    -DWITH_NEON=ON \
%endif
%ifarch armv5tel armv6l armv7l
    -DARM_FP_ABI=soft \
    -DWITH_NEON=OFF \
%endif
%ifarch aarch64
    -DWITH_SSE2=OFF \
%endif
    .

make %{?_smp_mflags}

pushd winpr/tools/makecert/cli
make %{?_smp_mflags}
popd

%install
make install DESTDIR=%{buildroot} INSTALL='install -p'
install -p -m 0755 winpr/tools/makecert/cli/winpr-makecert %{buildroot}%{_bindir}/

find %{buildroot} -name "*.a" -delete

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post -n libwinpr -p /sbin/ldconfig

%postun -n libwinpr -p /sbin/ldconfig

%files
%{_bindir}/winpr-makecert
%{_bindir}/xfreerdp
%{_mandir}/man1/xfreerdp.*

%files libs
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README ChangeLog
%{_libdir}/%{name}/
%{_libdir}/lib%{name}*.so.*
%{_libdir}/libx%{name}*.so.*
%{_libdir}/librdtk.so.*

%files devel
%{_libdir}/cmake/FreeRDP
%{_libdir}/cmake/RdTk
%{_includedir}/%{name}
%{_includedir}/rdtk
%{_libdir}/lib%{name}*.so
%{_libdir}/libx%{name}*.so
%{_libdir}/librdtk.so
%{_libdir}/pkgconfig/%{name}.pc

%files server
%{_bindir}/freerdp-shadow

%files -n libwinpr
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc README ChangeLog
%{_libdir}/libwinpr*.so.*

%files -n libwinpr-devel
%{_libdir}/cmake/WinPR
%{_includedir}/winpr
%{_libdir}/libwinpr*.so
%{_libdir}/pkgconfig/winpr.pc

%changelog
* Thu Oct 13 2016 Michael DePaulo - 2:2.0.0-6.git.b02943a
- Backport to EL6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-5.git.b02943a
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Dec 13 2015 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-4.git.b02943a
- Add FFMpeg/x264 build conditional.

* Sun Dec 13 2015 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-3.git.b02943a
- Move winpr-makecert into main package.

* Sun Dec 13 2015 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-2.git.b02943a
- Update to latest snapshot.
- Build winpr-makecert (#1288900).

* Sun Nov 15 2015 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-1.git.be8f8f7
- Update to latest snapshot, remove upstreamed patches.
- Update to new packaging guidelines for GitHub sources and license tag.
- Adjust CMake options to latest release, enable Wayland backend.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.2.0-0.10.git.24a752a
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Mar 22 2015 Kalev Lember <kalevlember@gmail.com> - 2:1.2.0-0.9.git.24a752a
- Bump epoch after the version downgrade

* Wed Mar 18 2015 David Woodhouse <dwmw2@infradead.org> - 1:1.2.0-0.8.git.24a752a
- Fix version number. No epoch++ since it was only in rawhide & f22-beta updates-testing.

* Tue Mar 17 2015 David Woodhouse <dwmw2@infradead.org> - 1:1.2.1-0.2.git.24a752a
- Revert to an older snapshot (+fixes) to fix guacamole-server build failure

* Fri Mar 13 2015 Simone Caronni <negativo17@gmail.com> - 1:1.2.1-0.1.git.6ac7180
- Use packaging guidelines for Github snapshots.
- Version is now at 1.2.1-dev.

* Fri Mar 13 2015 David Woodhouse <dwmw2@infradead.org> - 1:1.2.0-0.7.beta.1
- Update to git snapshot (dfc12385) and enable server build

* Thu Jan 15 2015 Orion Poplawski <orion@cora.nwra.com> - 1:1.2.0-0.6.beta.1
- Use better upstream patch to fix command line parsing

* Wed Jan 14 2015 Orion Poplawski <orion@cora.nwra.com> - 1:1.2.0-0.5.beta.1
- Add patch to fix command line parsing segfault (bug #1150349) and to
  fix old style command line options

* Tue Dec 16 2014 Simone Caronni <negativo17@gmail.com> - 1:1.2.0-0.4.beta.1
- Fix build on CMake 3.1.

* Wed Nov 12 2014 Simone Caronni <negativo17@gmail.com> - 1:1.2.0-0.3.beta.1
- Update to latest 1.2.0 beta 1 refresh.

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.2.0-0.2.beta.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Jun 17 2014 Simone Caronni <negativo17@gmail.com> - 1:1.2.0-0.1.beta.1
- Update to latest 1.2.0 beta 1.
- Rename freerdp-libwinpr to libwinpr and create a separate libwinpr-devel
  subpackage now that is considered a different set of libraries.
- Put CMake files in devel subpackages.
- Enable new Gstreamer 1.0, OpenSSL, JPEG, GSM, Zlib, libXi and Xrandr support.
- Disable static channels.
- Add new BuildRequires, build options and sort them.
- Fix rpmlint complaints.
- Align all description etc. to column 80.
- Remove desktop file for xfreerdp, it is command line only and has its own
  icon.

* Sat Jun  7 2014 Peter Robinson <pbrobinson@fedoraproject.org> 1:1.1.0-0.12.beta.2013071101
- Fix aarch64

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.1.0-0.11.beta.2013071101
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 25 2014 Mads Kiilerich <mads@kiilerich.com> - 1:1.1.0-0.10.beta.2013071101
- Fix PulseAudio define

* Sun Feb  2 2014 Ville Skyttä <ville.skytta@iki.fi> - 1:1.1.0-0.9.beta.2013071101
- Install SVG icon.

* Sat Dec 21 2013 Ville Skyttä <ville.skytta@iki.fi> - 1:1.1.0-0.8.beta.2013071101
- Disable RPATH.

* Mon Nov 04 2013 Kalev Lember <kalevlember@gmail.com> - 1.1.0-0.7.beta.2013071101
- Add missing epoch to freerdp-plugins obsoletes

* Tue Sep 10 2013 Simone Caronni <negativo17@gmail.com> - 1.1.0-0.6.beta.2013071101
- Add epoch to requirements.

* Tue Sep 10 2013 Simone Caronni <negativo17@gmail.com> - 1.1.0-0.5.beta.2013071101
- Bump epoch.

* Thu Sep 05 2013 Mads Kiilerich <mads@kiilerich.com> - 1.1.0-0.4.beta.2013071101
- libxfreerdp-client is needed ...

* Tue Sep 03 2013 Mads Kiilerich <mads@kiilerich.com> - 1.1.0-0.3.beta1
- Add missing ldconfig for libwinpr
- Based on patch from Simone Caronni:
- Update to the latest beta 1 refresh (1.1.0-beta+2013071101).
- Remove obsolete defattr, Group and BuildRoot RPM tags for Fedora / RHEL 6+.
- Move license file and documentation to libwinpr subpackage so any combination
  of installed packages result in the LICENSE file available.

* Sun Sep 01 2013 Mads Kiilerich <mads@kiilerich.com> - 1.1.0-0.2.beta1
- SSE2 should only be used on x86_64

* Sun Sep 01 2013 Dennis Gilmore <dennis@ausil.us> - 1.1.0-0.1.beta1
- disable neon on armv7hl and armv5tel
- set arm floating point correctly for the different targets

* Sun Sep 01 2013 Mads Kiilerich <mads@kiilerich.com> - 1.1.0-0.beta+2013071101
- Update to 1.1.0 beta1, add winpr package, drop plugins package.
- Drop unnecessary rm -rf of build roots.

* Sat Aug 31 2013 Mads Kiilerich <mads@kiilerich.com> - 1.0.2-4
- don't make freerdp.png executable

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 02 2013 Mads Kiilerich <mads@kiilerich.com> - 1.0.2-1
- freerdp-1.0.2

* Sun Sep 30 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-7
- merge f17 1.0.1-6 - Backport fix for bug 816692

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Feb 29 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-5
- Use new upstream tar with standard naming
- Use _isa for subpackage dependencies

* Tue Feb 28 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-4
- Include patch for sending invalid extra data

* Tue Feb 28 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-3
- Install a freedesktop .desktop file and a high-res icon instead of relying on
  _NET_WM_ICON

* Sat Feb 25 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-2
- Explicit build requirement for xmlto - needed for EL6

* Wed Feb 22 2012 Mads Kiilerich <mads@kiilerich.com> - 1.0.1-1
- FreeRDP-1.0.1 - major upstream rewrite and relicensing under Apache license

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 28 2011 Mads Kiilerich <mads@kiilerich.com> - 0.8.2-2
- rebuild on rawhide because of broken dependencies

* Tue Nov 16 2010 Mads Kiilerich <mads@kiilerich.com> - 0.8.2-1
- freerdp-0.8.2

* Mon Nov 08 2010 Mads Kiilerich <mads@kiilerich.com> - 0.8.1-2
- make -devel require pkgconfig
- first official Fedora package

* Sun Nov 07 2010 Mads Kiilerich <mads@kiilerich.com> - 0.8.1-1
- freerdp-0.8.1

* Sat Sep 25 2010 Mads Kiilerich <mads@kiilerich.com> - 0.7.4-2
- hack the generated libtool to not set rpath on x86_64
- configure with alsa explicitly

* Tue Aug 24 2010 Mads Kiilerich <mads@kiilerich.com> - 0.7.4-1
- freerdp-0.7.4
- cleanup of packaging structure

* Wed Jul 28 2010 Mads Kiilerich <mads@kiilerich.com> - 0.7.3-1
- 0.7.3
- fix some minor pylint warnings

* Fri Jul 23 2010 Mads Kiilerich <mads@kiilerich.com> - 0.7.2-2
- 0.7.2
- Address many comments from cwickert:
- - cleanup of old formatting, alignment with spectemplate-lib.spec and
    cwickert spec from #616193
- - add alsa as build requirement
- - remove superfluous configure options and disable static libs
- - add missing rpm groups

* Sun Jun 13 2010 Mads Kiilerich <mads@kiilerich.com> - 0.7.0-1
- First official release, first review request
