#!/bin/bash

source ${clst_shdir}/support/functions.sh

case ${1} in
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot \
			${clst_shdir}/${clst_target}/chroot.sh
	;;

	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
	;;

	kernel)
		shift
		export kname="${1}"

		exec_in_chroot ${clst_shdir}/support/kmerge.sh
	;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch ${1}/livecd

		${clst_shdir}/support/bootloader-setup.sh ${1}

		for x in ${clst_boot_kernel}; do
			extract_modules "${clst_chroot_path}/${clst_root_path}" $x
		done
	;;

	fsscript)
		exec_in_chroot "${clst_fsscript}"
	;;

	*)
	;;

esac
exit $?
