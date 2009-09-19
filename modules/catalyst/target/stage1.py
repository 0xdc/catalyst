
"""
Builder class for a stage1 installation tarball build.
"""

from generic_stage import *
import catalyst
from catalyst.output import *

class stage1_target(generic_stage_target):

	# We're leaving this empty since we can't do automatic source_subpath calculation for stage1
	depends = ()

	def __init__(self):
		generic_stage_target.__init__(self)

		self.required_values=[]
		self.valid_values=["chost"]

	def set_stage_path(self):
		self.settings["stage_path"]=catalyst.util.normpath(self.settings["chroot_path"]+self.settings["root_path"])
		msg("stage1 stage path is " + self.settings["stage_path"])

	def set_root_path(self):
		# sets the root path, relative to 'chroot_path', of the stage1 root
		self.settings["root_path"]=catalyst.util.normpath("/tmp/stage1root")
		msg("stage1 root path is " + self.settings["root_path"])

	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/usr/share/gettext",\
		"/usr/lib/python2.*/{test,email,lib-tk}",\
		"/usr/share/zoneinfo","/etc/portage"])

	# XXX: How do these override_foo() functions differ from the ones in generic_stage_target and why aren't they in stage3_target?

	def override_chost(self):
		if "chost" in self.settings:
			self.settings["CHOST"] = catalyst.util.list_to_string(self.settings["chost"])

	def override_cflags(self):
		if "cflags" in self.settings:
			self.settings["CFLAGS"] = catalyst.util.list_to_string(self.settings["cflags"])

	def override_cxxflags(self):
		if "cxxflags" in self.settings:
			self.settings["CXXFLAGS"] = catalyst.util.list_to_string(self.settings["cxxflags"])

	def override_ldflags(self):
		if "ldflags" in self.settings:
			self.settings["LDFLAGS"] = catalyst.util.list_to_string(self.settings["ldflags"])

	def set_portage_overlay(self):
		generic_stage_target.set_portage_overlay(self)
		if "portage_overlay" in self.settings:
			msg()
			msg("WARNING !!!!!")
			msg("\tUsing an portage overlay for earlier stages could cause build issues.")
			msg("\tIf you break it, you buy it. Don't complain to us about it.")
			msg("\tDont say we did not warn you")
			msg()

	def base_dirs(self):
		if os.uname()[0] == "FreeBSD":
			# baselayout no longer creates the .keep files in proc and dev for FreeBSD as it
			# would create them too late...we need them earlier before bind mounting filesystems
			# since proc and dev are not writeable, so...create them here
			if not os.path.exists(self.settings["stage_path"]+"/proc"):
				os.makedirs(self.settings["stage_path"]+"/proc")
			if not os.path.exists(self.settings["stage_path"]+"/dev"):
				os.makedirs(self.settings["stage_path"]+"/dev")
			if not os.path.isfile(self.settings["stage_path"]+"/proc/.keep"):
				try:
					proc_keepfile = open(self.settings["stage_path"]+"/proc/.keep","w")
					proc_keepfile.write('')
					proc_keepfile.close()
				except IOError:
					msg("!!! Failed to create %s" % (self.settings["stage_path"] + "/dev/.keep"))
			if not os.path.isfile(self.settings["stage_path"]+"/dev/.keep"):
				try:
					dev_keepfile = open(self.settings["stage_path"]+"/dev/.keep","w")
					dev_keepfile.write('')
					dev_keepfile.close()
				except IOError:
					msg("!!! Failed to create %s" % (self.settings["stage_path"]+"/dev/.keep"))
		else:
			pass

	def set_mounts(self):
		# stage_path/proc probably doesn't exist yet, so create it
		if not os.path.exists(self.settings["stage_path"]+"/proc"):
			os.makedirs(self.settings["stage_path"]+"/proc")

		# alter the mount mappings to bind mount proc onto it
		self.mounts.append("/tmp/stage1root/proc")
		self.mountmap["/tmp/stage1root/proc"]="/proc"


__target_map = { "stage1": stage1_target }

# vim: ts=4 sw=4 sta noet sts=4 ai
