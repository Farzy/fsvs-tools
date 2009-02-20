Name:           fsvs
Version:        1.1.17
Release:        1eas
Summary:        Full system versioning with metadata support
Group:          Development/Tools
License:        GPLv3

# Fchier SPEC pour la compilation statique de FSVS sur RHEL 4
# Auteur : Farzad FARID <ffarid@pragmatic-source.com>
# Date : 07/10/2008
#
# Les librairies SVN 1.5.x et APR 1.x n'étant pas compatible avec
# RHEL 4, la compilation de fsvs sur cette plate-forme nécessite
# la compilation manuelle d'une version statique de toutes les
# dépendances.

# !!!!!!!!!!!!!!!! ATTENTION !!!!!!!!!!!!!!!!!!!
# A la compilation, le rpmbuild va créer et remplir le
# répertoire /opt/fsvs. J'ait fait ainsi pour simplifier
# le processus de compilation, qui n'est déjà pas simple.
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Definir ici la version de Subversion, et mettre
# les archives "subversion" et "subversion-deps" correspondantes
# dans le répertoire SOURCES, au format tar.bz2.
%define svn_version	1.5.2
%define source1		subversion-%{svn_version}.tar.bz2
%define source2		subversion-deps-%{svn_version}.tar.bz2
# Répertoire destination du paquet final
%define fsvs_dir	/opt/fsvs

URL:            http://fsvs.tigris.org/
Source0:        http://www.tigris.org/files/documents/3133/43014/fsvs-%{version}.tar.bz2
Source1:	%{source1}
Source2:	%{source2}
Source3:	fsvs-autocommit
Source4:	fsvs.cron
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


#BuildRequires:  apr-devel
#BuildRequires:  apr-util-devel
BuildRequires:  pcre-devel
#BuildRequires:  subversion-devel
BuildRequires:  gdbm-devel
BuildRequires:  ctags
# FSVS 1.1.17 ne compile qu'avec GCC 4
BuildRequires:  gcc4

%description
FSVS is a backup/restore/versioning/deployment tool for whole directory
trees or filesystems, with a subversion repository as the backend.
It can do overlays of multiple repositories, to achieve some content
separation (base install, local modifications, etc.) 


%prep
%setup -q
cd $RPM_BUILD_DIR/%{name}-%{version}
tar xjf $RPM_SOURCE_DIR/%{source1}
tar xjf $RPM_SOURCE_DIR/%{source2}

%build
# D'abord on compile Subversion et APR (ainsi que quelques autres
# dépendences comme Neon, Serf) en dynamique, mais installé dans
# un répertoire spécifique à notre version de FSVS.

export CC=gcc4
cd subversion-%{svn_version}
./configure --prefix=%{fsvs_dir}
make
# !!!!!!!!!!!! Voici l'étape qui écrase /opt/fsvs !!!!!!!!!!!!
make install
cd ..
# Retour à la compilation de FSVS
export CFLAGS="$RPM_OPT_FLAGS -I/usr/include/pcre"
export RPATH="%{fsvs_dir}/lib"
%configure --with-aprinc=%{fsvs_dir}/include/apr-1 --with-svninc=%{fsvs_dir}/include --with-aprlib=%{fsvs_dir}/lib --with-svnlib=%{fsvs_dir}/lib
cd src
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
# Installation des librairies d'abord
mkdir -p $RPM_BUILD_ROOT%{fsvs_dir}
cd subversion-%{svn_version}
DESTDIR=$RPM_BUILD_ROOT make install
# On enlève les fichiers inutiles..
rm -rf $RPM_BUILD_ROOT%{fsvs_dir}/bin
rm -rf $RPM_BUILD_ROOT%{fsvs_dir}/build-1
rm -rf $RPM_BUILD_ROOT%{fsvs_dir}/include
rm -rf $RPM_BUILD_ROOT%{fsvs_dir}/share
cd ..
# Installation de FSVS
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
cp -p src/fsvs $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{_docdir}/fsvs-%{version}/
cp -p CHANGES README LICENSE $RPM_BUILD_ROOT/%{_docdir}/fsvs-%{version}/
cp -p doc/PERFORMANCE doc/IGNORING doc/USAGE doc/FAQ $RPM_BUILD_ROOT/%{_docdir}/fsvs-%{version}/
# cp -pr example/ $RPM_BUILD_ROOT/%{_docdir}/fsvs-%{version}//example/
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man1
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man5
cp -p doc/fsvs.1 $RPM_BUILD_ROOT/%{_mandir}/man1/fsvs.1
cp -p doc/*.5 $RPM_BUILD_ROOT/%{_mandir}/man5
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/fsvs
mkdir -p $RPM_BUILD_ROOT/%{_var}/spool/fsvs
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/cron.d
cp -p $RPM_SOURCE_DIR/fsvs.cron $RPM_BUILD_ROOT/%{_sysconfdir}/cron.d/fsvs
cp -p $RPM_SOURCE_DIR/fsvs-autocommit $RPM_BUILD_ROOT/%{_sbindir}/fsvs-autocommit

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%attr(755,root,root) %{_bindir}/fsvs
%attr(755,root,root) %{_sbindir}/fsvs-autocommit
%config %{_sysconfdir}/fsvs/
%config %{_sysconfdir}/cron.d/fsvs
%config %{_var}/spool/fsvs/
%doc
%doc %{_docdir}/fsvs-%{version}/
# %{_docdir}/fsvs-%{version}//example/
%{_mandir}/man1/*
%{_mandir}/man5/*
%{fsvs_dir}/lib/*

%changelog
* Wed Nov  5 2008 Farzad FARID <ffarid@pragmatic-source.com> 1.1.17-1eas
- Upgraded to 1.1.17
- FSVS 1.1.17 does not compile with GCC 3.4 on RHEL4, use GCC 4 Preview instead
- Add new manpages

* Mon Nov  4 2008 Farzad FARID <ffarid@pragmatic-source.com> 1.1.16-3eas
- fsvs-autocommit : Need to pre-authenticate user with "svn" before running
  any action without user interaction.

* Mon Nov  3 2008 Farzad FARID <ffarid@pragmatic-source.com> 1.1.16-2eas
- Add cron script for autocommitting.

* Wed Oct  8 2008 Farzad FARID <ffarid@pragmatic-source.com> 1.1.16-1eas
- Custom version, compiled for RHEL 4, build with a special Subversion source 
  dependency package containing all the need libraries: 
  Subversion 1.5, APR 1.x, Neon, Serf..
- Compiles and installs all of its dependencies in /opt/fsvs/lib.

* Wed Jun 18 2008 David Fraser <davidf@sjsoft.com> 1.1.16-1
- Upgraded to 1.1.16
- Updated with new upstream description and summary

* Wed Apr 30 2008 David Fraser <davidf@sjsoft.com> 1.1.15-1
- Upgraded to 1.1.15

* Wed Apr 02 2008 David Fraser <davidf@sjsoft.com> 1.1.14-1
- Upgraded to 1.1.14

* Wed Mar 26 2008 Manual "lonely wolf" Wolfshant <wolfy@fedoraproject.org> 1.1.13-5
- man pages are gzipped automatically; cd .. in build is useless

* Wed Mar 26 2008 David Fraser <davidf@sjsoft.com> 1.1.13-4
- Removed unneccessary macros

* Tue Mar 25 2008 David Fraser <davidf@sjsoft.com> 1.1.13-3
- Removed example directory
- Adjusted Makefile to take RPM_OPT_FLAGS

* Tue Mar 25 2008 Manual "lonely wolf" Wolfshant <wolfy@fedoraproject.org> 1.1.13-2
- Fixed remaining /usr/bin, /etc and /var to use macros

* Tue Mar 25 2008 David Fraser <davidf@sjsoft.com> 1.1.13-1
- Upgraded to latest release
- New man file locations
- New example in doc directory

* Tue Mar 25 2008 David Fraser <davidf@sjsoft.com> 1.1.12-7
- Re-added doc_dir and man_dir, but make them use _docdir and _mandir
- Fixed version numbers in changelog

* Mon Mar 24 2008 Manuel "lonely wolf" Wolfshant <wolfy@fedoraproject.org> 1.1.12-6
- Missing BR, consistent use of macros

* Mon Mar 24 2008 David Fraser <davidf@sjsoft.com> 1.1.12-5
- Corrected rpmlint errors
- Removed manual doc_dir and man_dir definitions

* Thu Feb 21 2008 David Fraser <davidf@sjsoft.com> 1.1.12-4
- Added pcre dependency

* Thu Feb 21 2008 David Fraser <davidf@sjsoft.com> 1.1.12-3
- Added configuration and WAA directories

* Thu Feb 21 2008 David Fraser <davidf@sjsoft.com> 1.1.12-2
- Added documentation directories

* Sat Feb 16 2008 David Fraser <davidf@sjsoft.com> 1.1.12-1
- Initial build.

