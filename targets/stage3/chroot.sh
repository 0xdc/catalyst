#!/bin/bash

source /tmp/chroot-functions.sh

export CONFIG_PROTECT="-* /etc/locale.gen"

echo "$locales" > /etc/locale.gen

case "${clst_profile}" in
*plasma*)
	USE=-harfbuzz run_merge --oneshot --update media-libs/freetype
	USE=-cairo run_merge --oneshot --update media-libs/harfbuzz
	;;
*gnome*)
	USE=-http2 run_merge --oneshot --update net-misc/curl
	;;
esac
run_merge -e --update --deep --with-bdeps=y @system

# Replace modified /etc/locale.gen with default
etc-update --automode -5
