#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies into /..."
ROOT=/ run_merge --update --onlydeps "${clst_embedded_packages}"

export ROOT="${clst_root_path}"
mkdir -p "$ROOT"

echo "Installing packages into ${ROOT}..."
INSTALL_MASK="${clst_install_mask}" LC_CTYPE=C.utf8 \
	run_merge --oneshot "${clst_embedded_packages}"
