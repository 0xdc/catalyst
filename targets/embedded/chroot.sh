#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export DESTROOT="${clst_root_path}"
export clst_root_path="/"

echo "Installing dependencies into ${clst_root_path}..."
LC_CTYPE=C.utf8 run_merge --update --onlydeps --onlydeps-with-rdeps=n \
	--autounmask --autounmask-continue \
	"${clst_embedded_packages}"

export clst_root_path="${DESTROOT}"
export INSTALL_MASK="${clst_install_mask}"

echo "Installing base system into ${clst_root_path}..."
run_merge sys-apps/baselayout

export USE="-* build systemd udev"
for package in sys-libs/glibc app-shells/bash sys-apps/systemd; do
	run_merge "${package}"
done
unset USE

echo "Installing packages into ${clst_root_path}..."
for package in ${clst_embedded_packages}; do
	LC_CTYPE=C.utf8 run_merge "${package}"
done
