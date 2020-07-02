#!/bin/bash

copy_to_chroot() {
	local src="${1}"
	local dst="${clst_chroot_path}/${2:-/tmp}"
	cp -pPR "${src}" "${dst}"
}

delete_from_chroot() {
	rm -f "${clst_chroot_path}/${1}"
}

# Takes the full path to the source file as its argument
# copies the file to the /tmp directory of the chroot
# and executes it.
exec_in_chroot() {
	local file_name=$(basename ${1})

	copy_to_chroot ${1}
	copy_to_chroot ${clst_shdir}/support/chroot-functions.sh

	# Ensure the file has the executable bit set
	chmod +x ${clst_chroot_path}/tmp/${file_name}

	echo "Running ${file_name} in chroot:"
	echo "    ${clst_CHROOT} ${clst_chroot_path} /tmp/${file_name}"
	${clst_CHROOT} "${clst_chroot_path}" "/tmp/${file_name}" || exit 1

	delete_from_chroot /tmp/${file_name}
	delete_from_chroot /tmp/chroot-functions.sh
}

die() {
	echo "$1"
	exit 1
}

extract_cdtar() {
	# Create a filesystem tree for the ISO at
	# $clst_target_path. We extract the "cdtar" to this directory,
	# which will normally contains a pre-built binary
	# boot-loader/filesystem skeleton for the ISO.
	tar -I lbzip2 -xpf ${clst_cdtar} -C $1 || die "Couldn't extract cdtar ${cdtar}"
}

create_bootloader() {
	# For amd64 and x86 we attempt to copy boot loader files from the live system and configure it right
	# this prevents (among other issues) needing to keep a cdtar up to date.  All files are thrown into $clst_target_path
	# Future improvement may make bootloaders optional, but for now there is only one option
	pushd "${1}" || die "Failed to enter livecd dir ${1}"

	# while $1/grub is unused here, it triggers grub config building in bootloader-setup.sh
	mkdir -p boot/EFI/BOOT isolinux
	#create boot.msg for isolinux
	echo "Gentoo Linux Installation LiveCD                         http://www.gentoo.org/" > isolinux/boot.msg
	echo "Enter to boot; F1 for kernels  F2 for options." >> isolinux/boot.msg
	echo "Press any key in the next 15 seconds or we'll try to boot from disk." >> isolinux/boot.msg
	#install isolinux files
	for root in "" "${clst_chroot_path}"; do
		if [ -f "${root}"/usr/share/syslinux/isolinux.bin ]; then
			cp "${root}"/usr/share/syslinux/isolinux.bin isolinux/
			#isolinux support files
			for i in libcom32.c32 libutil.c32 ldlinux.c32 reboot.c32 vesamenu.c32; do
				if [ -f "${root}/usr/share/syslinux/${i}" ]; then
					cp "${root}/usr/share/syslinux/${i}" isolinux/
				fi
			done
			#isolinux hardware detection toolkit, useful for system info and debugging
			if [ -f "${root}/usr/share/syslinux/hdt.c32" ]; then
				cp "${root}"/usr/share/syslinux/hdt.c32 isolinux/
				if [ -f "${root}/usr/share/misc/pci.ids" ]; then
					cp "${root}"/usr/share/misc/pci.ids isolinux/
				fi
			fi
			#memtest goes under isolinux since it doesn't work for uefi right now
			if [ -f "${root}"/usr/share/memtest86+/memtest ]; then
				cp "${root}"/usr/share/memtest86+/memtest.bin isolinux/memtest86
			fi
		fi
	done
	unset root

	if [ ! -f isolinux/isolinux.bin ]; then
		echo "Missing isolinux/isolinux.bin, this livecd will not bios boot."
	elif [ ! -f isolinux/memtest86 ]; then
		echo "Missing isolinux/memtest86, this livecd will not have memtest86+ support."
	fi

	if [ -x "/usr/bin/grub2-mkstandalone" ]; then
		grubmkstndaln="/usr/bin/grub2-mkstandalone"
	elif [ -x "/usr/bin/grub-mkstandalone" ]; then
		grubmkstndaln="/usr/bin/grub-mkstandalone"
	elif [ -x "${clst_chroot_path}/usr/bin/grub-mkstandalone" ]; then
		grubmkstndaln="${clst_chroot_path}/usr/bin/grub-mkstandalone"
		root="${clst_chroot_path}"
	else
		if "${clst_bootloader}" = "nonfatal"; then
			return
		else
			die "Unable to find grub-mkstandalone"
		fi
	fi

	#create grub-stub.cfg for embedding in grub-mkstandalone
	echo "insmod part_gpt" > grub-stub.cfg
	echo "insmod part_msdos" >> grub-stub.cfg
	echo "search --no-floppy --set=root --file /livecd" >> grub-stub.cfg
	echo "configfile /boot/grub/grub.cfg" >> grub-stub.cfg

	# some 64 bit machines have 32 bit UEFI, and you might want to boot 32 bit on a 64 bit machine, so we take the safest path and include both
	# set up 32 bit uefi
	test -d "${root}/usr/lib/grub/i386-efi" && (
		${grubmkstndaln} /boot/grub/grub.cfg=./grub-stub.cfg --compress=xz -O i386-efi -o ./boot/EFI/BOOT/grubia32.efi -d "${root}/usr/lib/grub/i386-efi" --themes= || die "Failed to make grubia32.efi"
	)

	if test -f "${root}/usr/share/shim/BOOTIA32.EFI"; then
		#secure boot shim
		cp "${root}"/usr/share/shim/BOOTIA32.EFI boot/EFI/BOOT/
		cp "${root}"/usr/share/shim/mmia32.efi boot/EFI/BOOT/
	fi

	#set up 64 bit uefi
	${grubmkstndaln} /boot/grub/grub.cfg=./grub-stub.cfg --compress=xz -O x86_64-efi -o ./boot/EFI/BOOT/grubx64.efi -d "${root}/usr/lib/grub/x86_64-efi" --themes= || die "Failed to make grubx64.efi"
	if test -f "${root}/usr/share/shim/BOOTIA32.EFI"; then
		#secure boot shim
		cp "${root}"/usr/share/shim/BOOTX64.EFI boot/EFI/BOOT/
		cp "${root}"/usr/share/shim/mmx64.efi boot/EFI/BOOT/
	fi

	rm grub-stub.cfg || echo "Failed to remove grub-stub.cfg, but this hurts nothing"
	popd || die "Failed to leave livecd dir"
}

extract_kernels() {
	# extract multiple kernels
	# $1 = Destination
	# ${clst_target_path}/kernel is often a good choice for ${1}

	# Takes the relative desination dir for the kernel as an arguement
	# i.e boot or isolinux
	[ -z "$clst_boot_kernel" ] && \
		die "Required key boot/kernel not defined, exiting"
	# install the kernels built in kmerge.sh
	for x in ${clst_boot_kernel}
	do
		first=${first:-""}
		kbinary="${clst_chroot_path}/tmp/kerncache/${x}-kernel-initrd-${clst_version_stamp}.tar.bz2"
		if [ -z "${first}" ]
		then
			# grab name of first kernel
			export first="${x}"
		fi

		[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kbinary} -C ${1}/

		# change config name from "config-*" to "gentoo-config", for example
		mv ${1}/config-* ${1}/${x}-config

		# change kernel name from "kernel" to "gentoo", for example
		if [ -e ${1}/kernel-* ]
		then
			mv ${1}/kernel-* ${1}/${x}
		fi
		if [ -e ${1}/kernelz-* ]
		then
			mv ${1}/kernelz-* ${1}/${x}
		fi
		if [ -e ${1}/vmlinuz-* ]
		then
			mv ${1}/vmlinuz-* ${1}/${x}
		fi

		# change initrd name from "initrd" to "gentoo.igz", for example
		if [ -e ${1}/initrd-* ]
		then
			mv ${1}/initrd-* ${1}/${x}.igz
		fi
		if [ -e ${1}/initramfs-* ]
		then
			mv ${1}/initramfs-* ${1}/${x}.igz
		fi

		# rename "System.map" to "System-gentoo.map", for example
		if [ -e ${1}/System.map-* ]
		then
			mv ${1}/System.map-* ${1}/System-${x}.map
		fi
	done
}

extract_modules() {
	# $1 = Destination
	# $2 = kname
	kmodules="${clst_chroot_path}/tmp/kerncache/${2}-modules-${clst_version_stamp}.tar.bz2"

	if [ -f "${kmodules}" ]
	then
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kmodules} --strip-components 1 -C ${1}/lib lib
	else
		echo "Can't find kernel modules tarball at ${kmodules}.  Skipping...."
	fi
}
