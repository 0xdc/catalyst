#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies..."
ROOT=/ run_merge --update --onlydeps "${clst_embedded_packages}"

echo "Installing packages into ${clst_root_path}..."
export ROOT="${clst_root_path}"
mkdir -p "$ROOT"

INSTALL_MASK="${clst_install_mask}" LC_CTYPE=C.utf8 \
	run_merge --oneshot "${clst_embedded_packages}"
