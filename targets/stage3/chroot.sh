#!/bin/bash

source /tmp/chroot-functions.sh

export CONFIG_PROTECT="-* /etc/locale.gen"

echo "$locales" > /etc/locale.gen

run_merge -e --update --deep --with-bdeps=y @system || {
	USE=-harfbuzz run_merge -1 freetype
	run_merge -1 harfbuzz
	run_merge -e --update --deep --with-bdeps=y @system
}

# Replace modified /etc/locale.gen with default
etc-update --automode -5
