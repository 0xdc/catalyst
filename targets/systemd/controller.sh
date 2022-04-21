#!/bin/bash

source ${clst_shdir}/support/functions.sh

case ${1} in
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot \
			${clst_shdir}/${clst_target}/chroot.sh
	;;


	fsscript)
		exec_in_chroot "${clst_fsscript}"
	;;

	*)
	;;

esac
exit $?
