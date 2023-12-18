#!/bin/bash

source ${clst_shdir}/support/functions.sh

mksqfs() {
	SOURCE="${1}"
	DEST="${2}"
	if command -v mksquashfs; then
		mksquashfs "${SOURCE}" "${DEST}" ${clst_fsops} -noappend \
			|| die "mksquashfs failed"
	else
		gensquashfs -k -D "${SOURCE}" -q ${clst_fsops} "${DEST}" \
			|| die "Failed to create squashfs filesystem"
	fi
}

CDROOT="${1}"
mkdir -p "${CDROOT}"

echo "Creating ${clst_fstype} filesystem"
case ${clst_fstype} in
	squashfs)
		if [ "${distkernel}" = "yes" ]; then
			mksqfs "${clst_stage_path}" "${CDROOT}/LiveOS/squashfs.img"
		else
			mksqfs "${clst_stage_path}" "${CDROOT}/image.squashfs"
		fi
	;;
	jffs2)
		mkfs.jffs2 --root="${clst_stage_path}" --output="${CDROOT}/image.jffs" "${clst_fsops}" \
			|| die "Failed to create jffs2 filesystem"
	;;
esac
