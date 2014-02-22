"Catalyst is the release building tool used by Gentoo Linux"

import codecs as _codecs
from distutils.core import setup as _setup
from email.utils import parseaddr as _parseaddr
import itertools as _itertools
import os as _os

from catalyst import __version__, __maintainer__


_this_dir = _os.path.dirname(__file__)
_package_name = 'catalyst'
_maintainer_name, _maintainer_email = _parseaddr(__maintainer__)


def _posix_path(path):
	"""Convert a native path to a POSIX path

	Distutils wants all paths to be written in the Unix convention
	(i.e. slash-separated) [1], so that's what we'll do here.

	[1]: http://docs.python.org/2/distutils/setupscript.html#writing-the-setup-script
	"""
	if _os.path.sep != '/':
		return path.replace(_os.path.sep, '/')
	return path


def _files(prefix, root):
	"""Iterate through all the file paths under `root`

	Yielding `(target_dir, (file_source_paths, ...))` tuples.
	"""
	for dirpath, dirnames, filenames in _os.walk(root):
		reldir = _os.path.relpath(dirpath, root)
		install_directory = _posix_path(
			_os.path.join(prefix, reldir))
		file_source_paths = [
			_posix_path(_os.path.join(dirpath, filename))
			for filename in filenames]
		yield (install_directory, file_source_paths)


_setup(
	name=_package_name,
	version=__version__,
	maintainer=_maintainer_name,
	maintainer_email=_maintainer_email,
	url='http://www.gentoo.org/proj/en/releng/{0}/'.format(_package_name),
	download_url='http://distfiles.gentoo.org/distfiles/{0}-{1}.tar.bz2'.format(
		_package_name, __version__),
	license='GNU General Public License (GPL)',
	platforms=['all'],
	description=__doc__,
	long_description=_codecs.open(
		_os.path.join(_this_dir, 'README'), 'r', 'utf-8').read(),
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
		'Intended Audience :: System Administrators',
		'Operating System :: POSIX',
		'Topic :: System :: Archiving :: Packaging',
		'Topic :: System :: Installation/Setup',
		'Topic :: System :: Software Distribution',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		],
	scripts=['bin/{0}'.format(_package_name)],
	packages=[
		_package_name,
		'{0}.arch'.format(_package_name),
		'{0}.targets'.format(_package_name),
		],
	data_files=list(_itertools.chain(
		_files(prefix='/etc/catalyst', root='etc'),
		_files(prefix='lib/catalyst/livecd', root='livecd'),
		_files(prefix='lib/catalyst/targets', root='targets'),
		)),
	provides=[_package_name],
	)
