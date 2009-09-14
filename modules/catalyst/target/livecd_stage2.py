
"""
Builder class for a LiveCD stage2 build.
"""

import os
from generic_stage import *
import catalyst
from catalyst.error import *
from catalyst.spawn import cmd
from catalyst.output import *

class livecd_stage2_target(generic_stage_target):
	def __init__(self):
		self.required_values=["boot/kernel"]

		self.valid_values=[]

		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm",\
			"livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type",\
			"livecd/readme","livecd/motd","livecd/overlay",\
			"livecd/modblacklist","livecd/splash_theme","livecd/rcadd",\
			"livecd/rcdel","livecd/fsscript","livecd/xinitrc",\
			"livecd/root_overlay","livecd/users","portage_overlay",\
			"livecd/fstype","livecd/fsops","livecd/linuxrc","livecd/bootargs",\
			"gamecd/conf","livecd/xdm","livecd/xsession","livecd/volid"])

		generic_stage_target.__init__(self)
		if not "livecd/type" in self.settings:
			self.settings["livecd/type"] = "generic-livecd"

		catalyst.util.file_locate(self.settings, ["cdtar","controller_file"])

	def set_source_path(self):
		self.settings["source_path"]=catalyst.util.normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
		if os.path.isfile(self.settings["source_path"]):
			self.settings["source_path_hash"]=catalyst.hash.generate_hash(self.settings["source_path"])
		else:
			self.settings["source_path"]=catalyst.util.normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/")
		if not os.path.exists(self.settings["source_path"]):
			raise CatalystError,"Source Path: "+self.settings["source_path"]+" does not exist."

	def set_target_path(self):
		self.settings["target_path"]=catalyst.util.normpath(self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/")
		if self.check_autoresume("setup_target_path"):
				msg("Resume point detected, skipping target path setup operation...")
		else:
			# first clean up any existing target stuff
			if os.path.isdir(self.settings["target_path"]):
				catalyst.util.remove_path(self.settings["target_path"])
			if not os.path.exists(self.settings["target_path"]):
				os.makedirs(self.settings["target_path"])

			self.set_autoresume("setup_target_path")

	def run_local(self):
		# what modules do we want to blacklist?
		if "livecd/modblacklist" in self.settings:
			try:
				myf=open(self.settings["chroot_path"]+"/etc/modprobe.d/blacklist.conf","a")
			except:
				self.unbind()
				raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/modprobe.d/blacklist.conf."

			myf.write("\n#Added by Catalyst:")
			for x in self.settings["livecd/modblacklist"]:
				myf.write("\nblacklist "+x)
			myf.close()

	def unpack(self):
		unpack=True
		display_msg=None

		clst_unpack_hash = catalyst.util.readfile(self.settings["autoresume_path"]+"unpack")

		if os.path.isdir(self.settings["source_path"]):
			unpack_cmd="rsync -a --delete "+self.settings["source_path"]+" "+self.settings["chroot_path"]
			display_msg="\nStarting rsync from "+self.settings["source_path"]+"\nto "+\
				self.settings["chroot_path"]+" (This may take some time) ...\n"
			error_msg="Rsync of "+self.settings["source_path"]+" to "+self.settings["chroot_path"]+" failed."
			invalid_snapshot=False

		if self.check_autoresume():
			if os.path.isdir(self.settings["source_path"]) and \
				self.check_autoresume("unpack"):
				msg("Resume point detected, skipping unpack operation...")
				unpack=False
			elif "source_path_hash" in self.settings:
				if self.settings["source_path_hash"] != clst_unpack_hash:
					invalid_snapshot=True

		if unpack:
			self.mount_safety_check()
			if invalid_snapshot:
				msg("No Valid Resume point detected, cleaning up...")
				#os.remove(self.settings["autoresume_path"]+"dir_setup")
				self.clear_autoresume()
				self.clear_chroot()
				#self.dir_setup()

			if not os.path.exists(self.settings["chroot_path"]):
				os.makedirs(self.settings["chroot_path"])

			if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
				os.makedirs(self.settings["chroot_path"]+"/tmp",1777)

			if "PKGCACHE" in self.settings:
				if not os.path.exists(self.settings["pkgcache_path"]):
					os.makedirs(self.settings["pkgcache_path"],0755)

			if not display_msg:
				raise CatalystError,"Could not find appropriate source. Please check the 'source_subpath' setting in the spec file."

			msg(display_msg)
			cmd(unpack_cmd,error_msg,env=self.env)

			if "source_path_hash" in self.settings:
				self.set_autoresume("unpack", self.settings["source_path_hash"])
			else:
				self.set_autoresume("unpack")

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay",\
				"bind","chroot_setup","setup_environment","run_local",\
				"build_kernel"]
		if not "FETCH" in self.settings:
			self.settings["action_sequence"] += ["bootloader","preclean",\
				"livecd_update","root_overlay","fsscript","rcupdate","unmerge",\
				"unbind","remove","empty","target_setup",\
				"setup_overlay","create_iso"]
		self.settings["action_sequence"].append("clear_autoresume")

__target_map = {"livecd-stage2":livecd_stage2_target}

# vim: ts=4 sw=4 sta noet sts=4 ai
