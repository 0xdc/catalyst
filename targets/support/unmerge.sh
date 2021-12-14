#!/bin/bash

source /tmp/chroot-functions.sh

test "${clst_packages}" && run_merge -C ${clst_packages}

exit 0
