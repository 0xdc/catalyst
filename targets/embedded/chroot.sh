#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies into /..."
ROOT=/ LC_CTYPE=C.utf8 run_merge --update --onlydeps --onlydeps-with-rdeps=n \
	--autounmask --autounmask-continue \
	"${clst_embedded_packages}"


export ROOT="${clst_root_path}"
mkdir -p "$ROOT"

echo "Installing base system into ${ROOT}..."
run_merge sys-apps/baselayout

export USE="-* build systemd udev"
for package in sys-libs/glibc app-shells/bash sys-apps/systemd; do
	run_merge "${package}"
done
unset USE

echo "Installing packages into ${ROOT}..."
for package in ${clst_embedded_packages}; do
	INSTALL_MASK="${clst_install_mask}" LC_CTYPE=C.utf8 \
		run_merge --oneshot "${package}"
done
