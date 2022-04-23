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
		options=()
		for arg in ${clst_fsops}; do
			options+=(${arg})
		done
		mkfs.${clst_fstype} --rootdir="${clst_stage_path}" --force "${1}/LiveOS/rootfs.img" --shrink "${clst_fsops[@]}" \
			|| die "Failed to create ${clst_fstype} filesystem"
	;;
	*)
		mkfs.${clst_fstype} --root="${clst_stage_path}" --output="${1}/LiveOS/rootfs.img" "${clst_fsops}" \
			|| die "Failed to create ${clst_fstype} filesystem"
	;;
esac
