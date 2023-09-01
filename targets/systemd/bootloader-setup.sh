#!/bin/bash

source ${clst_shdir}/support/functions.sh

# $1 is the destination root

if [[ -n ${clst_cdtar} ]]; then
	extract_cdtar $1
fi

extract_kernels $1/boot

cmdline_opts=()

# Add any additional options
if [ -n "${clst_livecd_bootargs}" ]
then
	for x in ${clst_livecd_bootargs}
	do
		cmdline_opts+=(${x})
	done
fi

case ${clst_fstype} in
	squashfs|btrfs)
		cmdline_opts+=(rd.live.overlay.overlayfs=1)
	;;
esac


default_append_line=(root=live:LABEL=ISOIMAGE ${cmdline_opts[@]})

case ${clst_hostarch} in
	amd64|arm64|ia64|ppc*|powerpc*|sparc*|x86)
		kern_subdir=/boot
		iacfg=$1/boot/grub/grub.cfg
		mkdir -p $1/boot/grub
		echo 'set default=0' > ${iacfg}
		echo 'set gfxpayload=keep' >> ${iacfg}
		echo 'set timeout=10' >> ${iacfg}
		echo 'insmod all_video' >> ${iacfg}
		echo '' >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			eval "kernel_console=\$clst_boot_kernel_${x}_console"

			echo "menuentry 'Boot LiveCD (kernel: ${x})' --class gnu-linux --class os {"  >> ${iacfg}
			echo "	linux ${kern_subdir}/${x} ${default_append_line[@]}" >> ${iacfg}
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			echo "" >> ${iacfg}
			echo "menuentry 'Boot LiveCD (kernel: ${x}) (cached)' --class gnu-linux --class os {"  >> ${iacfg}
			echo "	linux ${kern_subdir}/${x} ${default_append_line[@]} rd.live.ram=1" >> ${iacfg}
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			if [ -n "${kernel_console}" ]
			then
			echo 'serial --speed=115200' >> ${iacfg}
			echo 'terminal_input --append serial; terminal_output --append serial' >> ${iacfg}
			echo "submenu 'Special console options (kernel: ${x})' --class gnu-linux --class os {" >> ${iacfg}
				for y in ${kernel_console}
				do
					echo "menuentry 'Boot LiveCD (kernel: ${x} console=${y})' --class gnu-linux --class os {"  >> ${iacfg}
					echo "	linux ${kern_subdir}/${x} ${default_append_line[@]} console=${y}" >> ${iacfg}
					echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
					echo "}" >> ${iacfg}
					echo "" >> ${iacfg}
				done
				echo "}" >> ${iacfg}
			fi
			echo "" >> ${iacfg}
		done
	;;
esac
exit $?
