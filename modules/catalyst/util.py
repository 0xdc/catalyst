"""
Collection of utility functions for catalyst
"""

import sys, traceback, os, re, time, shutil, glob
import catalyst
from catalyst.error import *
from catalyst.output import *

def capture_traceback():
	etype, value, tb = sys.exc_info()
	s = [x.strip() for x in traceback.format_exception(etype, value, tb)]
	return s

def print_traceback():
	for x in capture_traceback():
		msg(x)

def load_module(name):
	try:
		# I'm not sure if it's better to use imp.load_module() for this, but
		# it seems to work just fine this way, and it's easier.
		exec("import " + name)
		return sys.modules[name]
	except Exception:
		return None

def find_binary(myc):
	"""look through the environmental path for an executable file named whatever myc is"""
	# this sucks. badly.
	p=os.getenv("PATH")
	if p == None:
		return None
	for x in p.split(":"):
		#if it exists, and is executable
		if os.path.exists("%s/%s" % (x,myc)) and os.stat("%s/%s" % (x,myc))[0] & 0x0248:
			return "%s/%s" % (x,myc)
	return None

def readfile(file):
	file_contents = ""
	try:
		myf = open(file, "r")
		file_contents = "".join(myf.readlines())
		myf.close()
		return file_contents
	except:
		return None
		#raise CatalystError, "Could not read file " + file

def list_bashify(mylist):
	if isinstance(mylist, str):
		mypack = [mylist]
	else:
		mypack = mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x] = "'" + mypack[x] + "'"
	mypack = "".join(mypack)
	return mypack

def list_to_string(mylist):
	if isinstance(mylist, str):
		mypack=[mylist]
	else:
		mypack=mylist[:]
	mypack = " ".join(mypack)
	return mypack

def normpath(mypath):
	newpath = os.path.normpath(mypath)
	if mypath.endswith('/'):
		newpath += '/'
	if len(newpath) > 1 and newpath[:2] == '//':
		newpath = newpath[1:]
	return newpath

def pathcompare(path1, path2):
	# Change double slashes to slash
	path1 = re.sub(r"//",r"/",path1)
	path2 = re.sub(r"//",r"/",path2)
	# Removing ending slash
	path1 = re.sub("/$","",path1)
	path2 = re.sub("/$","",path2)
	if path1 == path2:
		return True
	return False

def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return True
	a = os.popen("mount")
	mounts = [line.split()[2] for line in a.readlines()]
	a.close()
	for mount in mounts:
		if pathcompare(path, mount):
			return True
	return False

def touch(myfile):
	try:
		myf = open(myfile, "w")
		myf.close()
	except IOError:
		raise CatalystError, "Could not touch " + myfile + "."

def countdown(secs=5, doing="Starting"):
	if secs:
		msg(">>> Waiting " + secs + " seconds before starting...")
		msg(">>> (Control-C to abort)...")
		msg(doing + " in: ", newline=False)
		ticks = range(secs)
		ticks.reverse()
		for sec in ticks:
#			sys.stdout.write(str(sec+1) + " ")
			msg(str(sec+1), newline=False)
			sys.stdout.flush()
			time.sleep(1)
		msg()

def file_locate(settings, filelist, expand=True):
	#if expand is True, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if myfile in settings:
			# filenames such as cdtar are optional, so we don't assume the variable is defined.
			if not len(settings[myfile]):
				raise CatalystError, "File variable \"" + myfile + "\" has a length of zero (not specified)"
			if settings[myfile].startswith('/'):
				if not os.path.exists(settings[myfile]):
					raise CatalystError, "Cannot locate specified " + myfile + ": " + settings[myfile]
			elif expand and os.path.exists(os.getcwd() + "/" + settings[myfile]):
				settings[myfile] = os.getcwd() + "/" + settings[myfile]
			else:
				raise CatalystError, "Cannot locate specified " + myfile + ": " + settings[myfile] + " (2nd try)"

def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([0-9a-zA-Z_]*)=(.*)")
	while pos<len(mylines):
		if len(mylines[pos])<=1:
			#skip blanks
			pos += 1
			continue
		if mylines[pos][0] in ["#"," ","\t"]:
			#skip indented lines, comments
			pos += 1
			continue
		else:
			myline=mylines[pos]
			mobj=pat.match(myline)
			pos += 1
			if mobj.group(2):
				clean_string = re.sub(r"\"",r"",mobj.group(2))
				mymakeconf[mobj.group(1)]=clean_string
	return mymakeconf

def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
		try:
			try:
				import snakeoil.fileutils
				return snakeoil.fileutils.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage.util
					return portage.util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except:
					try:
						import portage_util
						return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
					except ImportError:
						myf=open(mymakeconffile,"r")
						mylines=myf.readlines()
						myf.close()
						return parse_makeconf(mylines)
		except:
			raise CatalystError, "Could not parse make.conf file "+mymakeconffile
	else:
		makeconf={}
		return makeconf

def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	for x in addlargs.keys():
		if x not in validspec and x not in catalyst.config.valid_config_file_values and x not in requiredspec:
			raise CatalystError, "Argument \""+x+"\" not recognized."
		else:
			myspec[x]=addlargs[x]

	for x in requiredspec:
		if not x in myspec:
			raise CatalystError, "Required argument \""+x+"\" not specified."

def remove_path(path, glob=True):
	paths = None
	if glob:
		paths = glob.glob(path)
	else:
		paths = [path]
	for x in paths:
		if os.uname()[0] == "FreeBSD":
			cmd("chflags -R noschg " + x, \
				"Could not remove immutable flag for path " \
				+ x)
		if os.path.is_dir(x):
			try:
				shutil.rmtree(x)
			except:
				raise CatalystError("Could not remove directory '%s'" % (x,))
		else:
			try:
				os.remove(x)
			except:
				raise CatalystError("Could not remove file '%s'" % (x,))

def empty_dir(path):
	try:
		mystat = os.stat(path)
		remove_path(path, False)
		mkdir(path)
		os.chown(path, mystat[stat.ST_UID], mystat[stat.ST_GID])
		os.chmod(path, mystat[stat.ST_MODE])
	except:
		raise CatalystError("Could not empty directory '%s'" % (path,))

def create_symlink(src, dest, remove_existing=False):
	if os.path.exists(dest):
		if remove_existing:
			remove_path(dest)
		else:
			raise CatalystError("Could not create symlink at '%s' due to existing file" % (dest,))
	try:
		os.symlink(src, dest)
	except:
		raise CatalystError("Could not create symlink '%s' to '%s'" % (dest, src))

def rsync(src, dest, delete=False, extra_opts=""):
	retval = catalyst.spawn.spawn_bash("rsync -a --delete %s %s %s" % (extra_opts, src, dest))
	if retval != 0:
		raise CatalystError("Could not rsync '%s' to '%s'" % (src, dest))

def create_tarball(target, src, working_dir=None, keep_perm=False):
	pack_cmd = "tar "
	if keep_perm:
		pack_cmd += "cjpf "
	else:
		pack_cmd += "cjf "
	pack_cmd += target
	if working_dir:
		pack_cmd += " -C " + working_dir
	pack_cmd += " " + src
	retval = catalyst.spawn.spawn_bash(pack_cmd)
	if retval != 0:
		raise CatalystError("Could not create tarball '%s'" % (target,))

def unpack_tarball(src, dest, keep_perm=True):
	unpack_cmd = "tar "
	if keep_perm:
		unpack_cmd += "xjpf "
	else:
		unpack_cmd += "xjf "
	unpack_cmd += src + " -C " + dest
	retval = catalyst.spawn.spawn_bash(unpack_cmd)
	if retval != 0:
		raise CatalystError("Could not unpack tarball '%s'" % (src,))

def mkdir(path, perms=0755):
	try:
		os.makedirs(path, perms)
	except:
		raise CatalystError("Could not create directory '%s'" % (path,))

# vim: ts=4 sw=4 sta noet sts=4 ai
