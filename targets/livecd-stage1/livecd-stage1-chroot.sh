#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

## START BUILD
setup_portage

run_emerge "${clst_packages}"
