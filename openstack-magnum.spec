%global with_doc %{!?_without_doc:1}%{?_without_doc:0}
%global service magnum

Name:		openstack-magnum
Summary:	Container Management project for OpenStack
Epoch:		1
Version:	1.1.0
Release:	2%{?dist}
License:	ASL 2.0
URL:		https://github.com/openstack/magnum.git

Provides:	magnum

Source0:	http://tarballs.openstack.org/%{service}/%{service}-%{version}.tar.gz

Source1:	%{service}.logrotate
Source2:	openstack-magnum-api.service
Source3:	openstack-magnum-conductor.service

BuildArch: noarch

BuildRequires: git
BuildRequires: python2-devel
BuildRequires: python-pbr
BuildRequires: python-setuptools

BuildRequires: systemd-units

Requires: %{name}-common = %{epoch}:%{version}-%{release}
Requires: %{name}-conductor = %{epoch}:%{version}-%{release}
Requires: %{name}-api = %{epoch}:%{version}-%{release}

%description
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

%if 0%{?with_doc}
%package -n %{name}-doc
Summary:          Documentation for OpenStack Magnum

Requires:         %{name} = %{epoch}:%{version}-%{release}

BuildRequires:   python-sphinx
BuildRequires:   python-oslo-sphinx
BuildRequires:   python-stevedore

%description -n %{name}-doc
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

This package contains documentation files for Magnum.
%endif

# tests
%package -n %{name}-test
Summary:          Tests for OpenStack Magnum

Requires:         %{name} = %{epoch}:%{version}-%{release}

BuildRequires:   python-coverage
BuildRequires:   python-fixtures
BuildRequires:   python-mock
BuildRequires:   python-oslotest
BuildRequires:   python-os-testr
BuildRequires:   python-subunit
BuildRequires:   python-testrepository
BuildRequires:   python-testscenarios
BuildRequires:   python-testtools
BuildRequires:   python-tempest-lib
BuildRequires:   python-wsme
BuildRequires:   python-oslo-config
BuildRequires:   python-oslo-policy
BuildRequires:   python-jsonpatch
BuildRequires:   python-barbicanclient
BuildRequires:   python-eventlet
BuildRequires:   python-keystoneclient
BuildRequires:   python-cryptography
BuildRequires:   python-heatclient
BuildRequires:   python-oslo-messaging
BuildRequires:   python-oslo-service
BuildRequires:   python-taskflow
BuildRequires:   python-oslo-db
BuildRequires:   python-oslo-versionedobjects
BuildRequires:   python-glanceclient
BuildRequires:   python-keystonemiddleware
BuildRequires:   python-mox3
BuildRequires:   python-novaclient
BuildRequires:   python-docker-py
BuildRequires:   python-pecan
BuildRequires:   python-pep8

%description -n %{name}-test
Magnum is an OpenStack project which offers container orchestration engines
for deploying and managing containers as first class resources in OpenStack.

%prep
%setup -q -n %{service}-%{version}

# Let's handle dependencies ourselves
rm -rf {test-,}requirements{-bandit,}.txt tools/{pip,test}-requires

# Remove tests in contrib
find contrib -name tests -type d | xargs rm -rf

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}

# docs generation requires everything to be installed first
export PYTHONPATH="$( pwd ):$PYTHONPATH"

pushd doc

%if 0%{?with_doc}
SPHINX_DEBUG=1 sphinx-build -b html source build/html
# Fix hidden-file-or-dir warnings
rm -fr build/html/.doctrees build/html/.buildinfo
%endif
popd

mkdir -p %{buildroot}/var/log/magnum/
mkdir -p %{buildroot}/var/run/magnum/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-magnum

# install systemd unit files
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/openstack-magnum-api.service
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/openstack-magnum-conductor.service

mkdir -p %{buildroot}/var/lib/magnum/
mkdir -p %{buildroot}/var/lib/magnum/certificates/
mkdir -p %{buildroot}/etc/magnum/

rm -rf %{buildroot}/var/lib/magnum/.dummy
rm -rf %{buildroot}/%{python_sitelib}/magnum/tests

install -p -D -m 640 etc/magnum/magnum.conf.sample %{buildroot}/%{_sysconfdir}/magnum/magnum.conf
install -p -D -m 640 etc/magnum/policy.json %{buildroot}/%{_sysconfdir}/magnum

%check
%{__python2} setup.py test ||

%package common
Summary: Magnum common

Requires: MySQL-python
Requires: python-babel
Requires: python-prettytable
Requires: PyYAML
Requires: python-sqlalchemy
Requires: python2-wsme
Requires: python-webob
Requires: python-alembic
Requires: python-decorator
Requires: python-docker-py
Requires: python-eventlet
Requires: python-greenlet
Requires: python-iso8601
Requires: python-jsonpatch
Requires: python-keystonemiddleware
Requires: python-netaddr

Requires: python-oslo-concurrency
Requires: python-oslo-config
Requires: python-oslo-context
Requires: python-oslo-db
Requires: python-oslo-i18n
Requires: python-oslo-log
Requires: python-oslo-messaging
Requires: python-oslo-policy
Requires: python-oslo-serialization
Requires: python-oslo-service
Requires: python-oslo-utils
Requires: python-oslo-versionedobjects
Requires: python-oslo-reports

Requires: python-paramiko
Requires: python2-pecan

Requires: python-barbicanclient
Requires: python-glanceclient
Requires: python-heatclient
Requires: python-novaclient
Requires: python-keystoneclient

Requires: python-requests
Requires: python-six
Requires: python-stevedore
Requires: python-taskflow
Requires: python-cryptography
Requires: python-stevedore
Requires: python-urllib3


Requires(pre): shadow-utils

%description common
Components common to all OpenStack Magnum services

%files common
%{_bindir}/magnum-db-manage
%{_bindir}/magnum-template-manage
%license LICENSE
%{python_sitelib}/magnum*
%dir %attr(0750,magnum,root) %{_localstatedir}/log/magnum
%dir %attr(0755,magnum,root) %{_localstatedir}/run/magnum
%dir %attr(0755,magnum,root) %{_sharedstatedir}/magnum
%dir %attr(0755,magnum,root) %{_sharedstatedir}/magnum/certificates
%dir %attr(0755,magnum,root) %{_sysconfdir}/magnum
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-magnum
%config(noreplace) %attr(-, root, magnum) %{_sysconfdir}/magnum/magnum.conf
%config(noreplace) %attr(-, root, magnum) %{_sysconfdir}/magnum/policy.json
%pre common
# 1870:1870 for magnum - rhbz#845078
getent group magnum >/dev/null || groupadd -r --gid 1870 magnum
getent passwd magnum  >/dev/null || \
useradd --uid 1870 -r -g magnum -d %{_sharedstatedir}/magnum -s /sbin/nologin \
-c "OpenStack Magnum Daemons" magnum
exit 0


%package conductor
Summary: The Magnum conductor

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description conductor
OpenStack Magnum Conductor

%files conductor
%doc README.rst
%license LICENSE
%{_bindir}/magnum-conductor
%{_unitdir}/openstack-magnum-conductor.service

%post conductor
%systemd_post openstack-magnum-conductor.service

%preun conductor
%systemd_preun openstack-magnum-conductor.service

%postun conductor
%systemd_postun_with_restart openstack-magnum-conductor.service


%package api
Summary: The Magnum API

Requires: %{name}-common = %{epoch}:%{version}-%{release}

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description api
OpenStack-native ReST API to the Magnum Engine

%files api
%doc README.rst
%license LICENSE
%{_bindir}/magnum-api
%{_unitdir}/openstack-magnum-api.service


%if 0%{?with_doc}
%files -n %{name}-doc
%license LICENSE
%doc doc/build/html
%endif

%post api
%systemd_post openstack-magnum-api.service

%preun api
%systemd_preun openstack-magnum-api.service

%postun api
%systemd_postun_with_restart openstack-magnum-api.service

%changelog
* Wed Dec 2 2015 Chandan Kumar <chkumar246@gmail.com> 1:1.1.0-2
- Added Doc subpackage and enable tests

* Tue Dec 1 2015 Mathieu Velten <mathieu.velten@cern.ch> 1:1.1.0-1
- Mitaka M1 release

* Thu Nov 12 2015 Mathieu Velten <mathieu.velten@cern.ch> 1:1.0.0.0b2.dev4-1
- Initial Liberty release
