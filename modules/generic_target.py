import os

from catalyst_support import *

class generic_target:
	"""
	The toplevel class for generic_stage_target. This is about as generic as we get.
	"""
	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		self.env = {
			'PATH': '/bin:/sbin:/usr/bin:/usr/sbin',
			'TERM': os.getenv('TERM', 'dumb'),
			}
