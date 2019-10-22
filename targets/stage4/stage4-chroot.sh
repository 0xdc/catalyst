#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

echo "Bringing @world up to date using profile specific use flags"
### re: @world over @system:
###	package.use changes added in a portage_confdir aren't picked up
###	unless those packages are in @system
run_merge --update --deep @world

echo "Emerging packages using stage4 use flags"

run_merge "${clst_packages}"
