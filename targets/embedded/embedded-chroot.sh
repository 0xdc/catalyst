#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export DESTROOT="${clst_root_path}"
export clst_root_path="/"

setup_pkgmgr

echo "Installing dependencies for ${DESTROOT}..."
run_merge --onlydeps --onlydeps-with-rdeps=n "${clst_embedded_packages}"

export clst_root_path="${DESTROOT}"
export INSTALL_MASK="${clst_install_mask}"

run_merge --oneshot --with-bdeps=n "${clst_embedded_packages}"
