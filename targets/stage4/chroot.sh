#!/bin/bash

source /tmp/chroot-functions.sh

echo "Bringing world up to date using profile specific use flags"
run_merge --update --deep --newuse @world

echo "Emerging packages using stage4 use flags"

case "${clst_profile}" in
*gnome*)
	USE=minimal run_merge --oneshot --update media-libs/libsndfile
	;;
esac

run_merge "${clst_packages}"
