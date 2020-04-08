#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export DESTROOT="${clst_root_path}"
export clst_root_path="/"

setup_pkgmgr

echo "Installing dependencies into ${clst_root_path}..."
export LC_CTYPE=C.utf8
timeout=4
# call emerge directly as run_merge has '|| exit 1' which we don't desire
until emerge --quiet --update --onlydeps \
		--usepkg --buildpkg --binpkg-respect-use=y \
		--autounmask --autounmask-write --keep-going --onlydeps-with-rdeps=n \
		${clst_embedded_packages[@]}; do
	test "$timeout" -gt 0 || exit 1
	etc-update --quiet --automode -5
	timeout=$(( $timeout - 1 ))
done
unset LC_CTYPE

export clst_root_path="${DESTROOT}"
export INSTALL_MASK="${clst_install_mask}"

echo "Installing base system into ${clst_root_path}..."
run_merge --oneshot sys-apps/baselayout

export USE="-* build systemd udev"
run_merge --oneshot app-shells/bash sys-apps/systemd sys-libs/glibc
unset USE

echo "Installing packages into ${clst_root_path}..."
LC_CTYPE=C.utf8 run_merge --oneshot "${clst_embedded_packages}"
