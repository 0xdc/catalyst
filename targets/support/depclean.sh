#!/bin/bash

source /tmp/chroot-functions.sh

case "${clst_livecd_depclean}${clst_stage4_depclean}" in
keepbdeps)
	run_merge --depclean --with-bdeps=y
	;;
yes|all)
	run_merge --depclean --with-bdeps=n
	;;
esac

exit 0
