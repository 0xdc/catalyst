#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies..."
ROOT=/ \
	run_merge --update --onlydeps --onlydeps-with-rdeps=n \
	--autounmask --autounmask-continue \
	"${clst_embedded_packages}"

export ROOT="${clst_root_path}"

echo "Installing base system into ${ROOT}..."
run_merge sys-apps/baselayout

export USE="-* build systemd udev gawk pigz"
for package in sys-libs/glibc app-shells/bash sys-apps/systemd; do
	run_merge "${package}"
done
unset USE

echo "Installing packages into ${clst_root_path}..."
for package in ${clst_embedded_packages}; do
	INSTALL_MASK="${clst_install_mask}" \
		run_merge "${package}"
done
