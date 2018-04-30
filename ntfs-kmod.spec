%global debug_package %{nil}
#rpmbuild --rebuild --define='kernels $(uname -r)' whatever.srpm
#%global buildforkernels akmod
Name: ntfs-kmod
Version: 0
Release: 7%{?dist}
Summary: Akmod package for kernel mode NTFS module

License: GPL
URL: http://www.kernel.org
#VERSION=$1
#git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git --depth 1 --branch v${VERSION}
#cd linux-stable
#git times # https://git.wiki.kernel.org/index.php/ExampleScripts
#tar cjf linux-fs-ntfs-${VERSION}.tar.xz fs/ntfs/
Source0: linux-fs-ntfs-4.16.4.tar.xz
Patch0: 0001-ntfs_volume_check_hiberfile-relaxed-too-strict-check.patch

BuildRequires:  %{_bindir}/kmodtool
Provides: ntfs-kmod-common

ExclusiveArch:  i686 x86_64
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Akmod package for kernel mode NTFS module

%prep
%{?kmodtool_check}

kmodtool --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T
mkdir %{name}-%{version}-src
pushd %{name}-%{version}-src
tar xf %{SOURCE0}
%patch0 -p1
popd

for kernel_version in %{?kernel_versions} ; do
 cp -a %{name}-%{version}-src _kmod_build_${kernel_version%%___*}
done

%build
#make -C /lib/modules/`uname -r`/build M=$PWD CONFIG_NTFS_FS=m CONFIG_NTFS_RW=y
for kernel_version in %{?kernel_versions}; do
 pushd _kmod_build_${kernel_version%%___*}/fs/ntfs/
 make -C ${kernel_version##*___} M=`pwd` CONFIG_NTFS_FS=m CONFIG_NTFS_RW=y modules
 popd
done

%install
rm -rf ${RPM_BUILD_ROOT}
for kernel_version in %{?kernel_versions}; do
 pushd _kmod_build_${kernel_version%%___*}/fs/ntfs/
 mkdir -p ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
 install -m 0755 *.ko ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
 popd
done

chmod 0755 $RPM_BUILD_ROOT%{kmodinstdir_prefix}*%{kmodinstdir_postfix}/* || :
%{?akmod_install}

%clean
rm -rf $RPM_BUILD_ROOT

%package -n ntfs-kmod-common
Summary: Dummy package

%description  -n ntfs-kmod-common
Dummy package

%files -n ntfs-kmod-common

%changelog
* Mon Apr 30 2018 Dick Marinus <dick@mrns.nl> - 0-7
- linux-fs-ntfs-4.16.4

* Wed Dec 20 2017 Dick Marinus <dick@mrns.nl> - 0-6
- linux-fs-ntfs-4.14.16

* Wed Dec 20 2017 Dick Marinus <dick@mrns.nl> - 0-5
- linux-fs-ntfs-4.14.6

* Mon Feb  8 2016 Dick Marinus <dick@mrns.nl> - 0-3
- linux-fs-ntfs-4.11.3

* Mon Feb  8 2016 Dick Marinus <dick@mrns.nl> - 0-2
- initial version
