#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies..."
LC_CTYPE=C.utf8 ROOT=/ \
	run_merge --update --onlydeps --onlydeps-with-rdeps=n \
	--autounmask --autounmask-continue \
	"${clst_embedded_packages}"


export ROOT="${clst_root_path}"
echo "Installing base system into ${ROOT}..."
run_merge sys-apps/baselayout

export USE="-* build systemd udev"
run_merge sys-libs/glibc sys-apps/systemd
run_merge app-shells/bash
unset USE

echo "Installing packages into ${clst_root_path}..."

for package in ${clst_embedded_packages}; do
	INSTALL_MASK="${clst_install_mask}" LC_CTYPE=C.utf8 \
		run_merge "${package}"
done
