#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

case $1 in
	fsscript)
		exec_in_chroot ${clst_fsscript}
		;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch $1/livecd

		# We create a firmware directory, if necessary
		if [ -e ${clst_chroot_path}/lib/firmware.tar.bz2 ]
		then
			echo "Creating firmware directory in $1"
			mkdir -p $1/firmware
			# TODO: Unpack firmware into $1/firmware and remove it from the
			# chroot so newer livecd-tools/genkernel can find it and unpack it.
		fi

		# Move over the readme (if applicable)
		if [ -n "${clst_livecd_readme}" ]
		then
			cp -f ${clst_livecd_readme} $1/README.txt
		else
			cp -f ${clst_sharedir}/livecd/files/README.txt $1
		fi

		extract_cdtar $1

		for x in ${clst_boot_kernel}; do
			extract_modules ${clst_chroot_path} $x
		done
		;;

	target_image_setup)
		shift
		${clst_shdir}/support/target_image_setup.sh $1
		;;

	iso)
		shift
		${clst_shdir}/support/create-iso.sh $1
		;;
esac
exit $?
