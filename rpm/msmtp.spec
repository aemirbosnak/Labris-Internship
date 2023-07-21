Name:           msmtp
Version:        1.8.24
Release:        1%{?dist}
Summary:        mail client

License:        GPLv3
URL:            https://marlamm.de/%{name}
Source0:        https://marlamm.de/%{name}/releases/%{name}-%{version}.tar.xz

BuildRequires: gcc, make

%description
msmtp is an SMTP client.

%prep
%setup -q

%build
./configure
make

%install
%make_install

%files
%doc README COPYING INSTALL NEWS AUTHORS THANKS
%{_prefix}/local/bin/msmtp
%{_prefix}/local/bin/msmtpd

%{_prefix}/local/share/info/dir
%{_prefix}/local/share/info/msmtp.info
%{_prefix}/local/share/locale/de/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/eo/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/fr/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/pt_BR/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/ru/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/sr/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/sv/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/ta/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/locale/uk/LC_MESSAGES/msmtp.mo
%{_prefix}/local/share/man/man1/msmtp.1
%{_prefix}/local/share/man/man1/msmtpd.1


%changelog
*Tue Jul 18 2023 Emir Bosnak <aebosnak2002@gmail.com> - 1.8.24-1 
- Version 1.8.24 Release 1

