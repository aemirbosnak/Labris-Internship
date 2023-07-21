Name:           netflow2ng
Version:        0.0.4
Release:        1%{?dist}
Summary:        netflow2ng packet

License:        MIT
URL:            https://github.com/synfinatic/%{name}
Source0:        https://github.com/synfinatic/%{name}-%{version}.tar.gz

BuildRequires:  make, go, zeromq-devel

%description
Software for netflow analysis.

%global debug_package %{nil}

%prep
%setup -n %{name} -q

%build
make

%install
mkdir -p %{buildroot}/usr/bin
cp %{_builddir}/%{name}/dist/%{name}-%{version} %{buildroot}/usr/bin/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}

%changelog
* Thu Jul 20 2023 Emir Bosnak <aebosnak2002@gmail.com - 0.0.4-1 
- Version 0.0.4 Release 1
