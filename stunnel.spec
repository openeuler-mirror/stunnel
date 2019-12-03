Name:           stunnel
Version:        5.48
Release:        2
Summary:        Secure traffic running between a TCP client and server
License:        GPLv2
URL:            http://www.stunnel.org/
Source0:        https://www.stunnel.org/downloads/stunnel-%{version}.tar.gz
Source1:        https://www.stunnel.org/downloads/stunnel-%{version}.tar.gz.asc
Source2:        Certificate-Creation
Source3:        sfinger.xinetd
Source4:        stunnel-sfinger.conf
Source5:        pop3-redirect.xinetd
Source6:        stunnel-pop3s-client.conf
Source7:        stunnel@.service
Patch0001:      stunnel-5.40-authpriv.patch
Patch0002:      stunnel-5.40-systemd-service.patch
Patch0003:      stunnel-5.46-system-ciphers.patch

BuildRequires:  openssl-devel pkgconfig util-linux autoconf automake libtool
BuildRequires:  perl-podlators perl nmap-ncat lsof procps-ng systemd
%{?systemd_requires}

%description
The stunnel program is designed to work as SSL encryption
wrapper between remote clients and local (inetd-startable)
or remote servers. The concept is that having non-SSL
aware daemons running on your system you can easily set
them up to communicate with clients over secure SSL chan-
nels.

stunnel can be used to add SSL functionality to commonly
used inetd daemons like POP-2, POP-3, and IMAP servers, to
standalone daemons like NNTP, SMTP and HTTP, and in tun-
neling PPP over network sockets without changes to the
source code.

%package        help
Summary:        This package contains help documents
Requires:       %{name} = %{version}-%{release}

%description    help
Files for help with stunnel.

%prep
%autosetup -n %{name}-%{version} -p1
change_date=`date +%Y.%m.%d`
sed -i "s/2018\.07\.02/${change_date}/g" `grep "2018\.07\.02" -lr ./`
sed -i '/yes).*result: no/,+1{s/result: no/result: yes/;s/as_echo "no"/as_echo "yes"/}' configure
sed -i '/client = yes/a \\  ciphers = PSK' tests/recipes/014_PSK_secrets

%build
CFLAGS="$RPM_OPT_FLAGS -fPIC `pkg-config --cflags openssl`"; export CFLAGS
LDFLAGS="`pkg-config --libs-only-L openssl`"; export LDFLAGS
%configure --enable-fips --enable-ipv6 --with-ssl=%{_prefix} --disable-libwrap \
        CPPFLAGS="-UPIDFILE -DPIDFILE='\"%{_localstatedir}/run/stunnel.pid\"'"
make V=1 LDADD="-pie -Wl,-z,defs,-z,relro,-z,now"

%install
%make_install
for lang in pl ; do
        install -d %{buildroot}/%{_mandir}/${lang}/man8
        mv %{buildroot}/%{_mandir}/man8/*.${lang}.8* %{buildroot}/%{_mandir}/${lang}/man8/
        rename ".${lang}" "" %{buildroot}/%{_mandir}/${lang}/man8/*
done
install -d srpm-docs
cp %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6} srpm-docs
install -D %{buildroot}%{_datadir}/doc/stunnel/examples/%{name}.service %{buildroot}%{_unitdir}/%{name}.service
install -D %{SOURCE7} %{buildroot}%{_unitdir}/%{name}@.service

%post
/sbin/ldconfig
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
/sbin/ldconfig
%systemd_postun_with_restart %{name}.service

%files
%doc COPY*
%{_bindir}/stunnel
%exclude %{_bindir}/stunnel3
%{_libdir}/stunnel
%exclude %{_libdir}/stunnel/libstunnel.la
%dir %{_sysconfdir}/%{name}
%exclude %{_sysconfdir}/stunnel/*
%{_unitdir}/%{name}*.service

%files help
%{_mandir}/man8/stunnel.8*
%doc tools/stunnel.conf-sample
%doc srpm-docs/*
%lang(en) %doc doc/en/*
%lang(pl) %doc doc/pl/*
%lang(pl) %{_mandir}/pl/man8/stunnel.8*
%exclude %{_datadir}/doc/stunnel

%changelog
* Mon Nov 25 2019 gulining<gulining1@huawei.com> - 5.48-2
- Pakcage init
