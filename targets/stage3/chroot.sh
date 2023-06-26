#!/bin/bash

source /tmp/chroot-functions.sh

export CONFIG_PROTECT="-* /etc/locale.gen"

echo "$locales" > /etc/locale.gen

USE=-harfbuzz run_merge --oneshot --update freetype
USE=-cairo run_merge --oneshot --update harfbuzz
run_merge -e --update --deep --with-bdeps=y @system

# Replace modified /etc/locale.gen with default
etc-update --automode -5
