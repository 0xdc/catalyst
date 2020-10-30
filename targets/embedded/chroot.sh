#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export DESTROOT="${clst_root_path}"
export clst_root_path="/"

echo "Installing dependencies into ${clst_root_path}..."
run_merge --update --onlydeps "${clst_embedded_packages}"

export clst_root_path="${DESTROOT}"
export INSTALL_MASK="${clst_install_mask}"

echo "Installing base system into ${clst_root_path}..."
run_merge --oneshot sys-apps/baselayout

export USE="-* build systemd udev"
run_merge --oneshot app-shells/bash sys-apps/systemd sys-libs/glibc
unset USE

echo "Installing packages into ${clst_root_path}..."
LC_CTYPE=C.utf8 run_merge --oneshot "${clst_embedded_packages}"
