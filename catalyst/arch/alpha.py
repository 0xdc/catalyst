

from catalyst import builder


class generic_alpha(builder.generic):
	"abstract base class for all alpha builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-mieee -pipe"
		self.settings["CHOST"]="alpha-unknown-linux-gnu"
		self.settings["PROFILE_ARCH"] = "alpha"

class arch_ev4(generic_alpha):
	"builder class for generic alpha (ev4+)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev4"

class arch_ev45(generic_alpha):
	"builder class for alpha ev45"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev45"

class arch_ev5(generic_alpha):
	"builder class for alpha ev5"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev5"

class arch_ev56(generic_alpha):
	"builder class for alpha ev56 (ev5 plus BWX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev56"

class arch_pca56(generic_alpha):
	"builder class for alpha pca56 (ev5 plus BWX & MAX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=pca56"

class arch_ev6(generic_alpha):
	"builder class for alpha ev6"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev6"

class arch_ev67(generic_alpha):
	"builder class for alpha ev67 (ev6 plus CIX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2 -mcpu=ev67"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ "alpha":arch_ev4, "ev4":arch_ev4, "ev45":arch_ev45,
		"ev5":arch_ev5, "ev56":arch_ev56, "pca56":arch_pca56,
		"ev6":arch_ev6, "ev67":arch_ev67 },
	("alpha", ))
