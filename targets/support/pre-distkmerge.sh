#!/bin/bash

RUN_DEFAULT_FUNCS="yes"

source /tmp/chroot-functions.sh

run_merge --update --oneshot sys-kernel/dracut sys-fs/lvm2 sys-apps/iucode_tool
