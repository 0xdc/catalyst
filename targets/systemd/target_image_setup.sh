#!/bin/bash

source ${clst_shdir}/support/functions.sh

mkdir -p "${1}"

echo "Creating ${clst_fstype} filesystem"
test -d "${1}/LiveOS" || mkdir -pv "${1}/LiveOS"
case ${clst_fstype} in
	squashfs)
		if command -v mksquashfs; then
			mksquashfs "${clst_stage_path}" "${1}/LiveOS/squashfs.img" ${clst_fsops} -noappend \
				|| die "mksquashfs failed"
		else
			gensquashfs -D "${clst_stage_path}" -q ${clst_fsops} "${1}/LiveOS/squashfs.img" \
				|| die "Failed to create squashfs filesystem"
		fi
	;;
	btrfs)
		squashdir="${clst_chroot_path}/tmp/livecd"
		mkdir -p "${squashdir}/LiveOS"

		mkfs.${clst_fstype} --rootdir="${clst_stage_path}" "${squashdir}/LiveOS/rootfs.img" \
			--shrink --force || die "Failed to create ${clst_fstype} filesystem"

		if command -v mksquashfs; then
			mksquashfs "${squashdir}" "${1}/LiveOS/squashfs.img" ${clst_fsops} -noappend \
				|| die "mksquashfs failed"
		else
			gensquashfs -D "${squashdir}" -q ${clst_fsops} "${1}/LiveOS/squashfs.img" \
				|| die "Failed to create squashfs filesystem"
		fi
	;;
	*)
		mkfs.${clst_fstype} --root="${clst_stage_path}" --output="${1}/LiveOS/rootfs.img" "${clst_fsops}" \
			|| die "Failed to create ${clst_fstype} filesystem"
	;;
esac
