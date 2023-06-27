#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies in seed stage..."
ROOT=/ run_merge --update --onlydeps \
		--autounmask --autounmask-continue \
		"${clst_embedded_packages}"

export ROOT="${clst_root_path}"

echo "Installing the base system into ${ROOT}..."
run_merge --oneshot sys-apps/baselayout

split_usr

export USE="-* build systemd udev gawk pigz"
for package in sys-libs/glibc sys-apps/systemd app-shells/bash; do
	run_merge "${package}"
done
unset USE

split_usr

echo "Installing packages into ${ROOT}..."
for package in ${clst_embedded_packages}; do
	INSTALL_MASK="${clst_install_mask}" \
		run_merge "${package}"
done
