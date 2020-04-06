#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

echo "Bringing world up to date using profile specific use flags"
run_merge --update --deep --newuse @world

echo "Emerging packages using stage4 use flags"

LC_CTYPE=C.utf8 run_merge "${clst_packages}"