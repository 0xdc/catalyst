"""
LiveCD stage1 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import normpath
from catalyst.base.stagebase import StageBase


class livecd_stage1(StageBase):
    """
    Builder class for LiveCD stage1.
    """
    required_values = frozenset([
    ])
    valid_values = required_values | frozenset([
        "livecd/depclean",
        "livecd/empty",
        "livecd/fsscript",
        "livecd/packages",
        "livecd/rm",
        "livecd/root_overlay",
        "livecd/unmerge",
        "livecd/use",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.build_packages,
            self.unmerge,
        ])
        self.finish_sequence.extend([
            self.clean,
        ])
        self.set_completion_action_sequences()

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "livecd"

    def set_catalyst_use(self):
        StageBase.set_catalyst_use(self)
        if "catalyst_use" in self.settings:
            self.settings["catalyst_use"].append("livecd")
        else:
            self.settings["catalyst_use"] = ["livecd"]

    def set_packages(self):
        StageBase.set_packages(self)
        if self.settings["spec_prefix"]+"/packages" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix']+'/packages'], str):
                self.settings[self.settings["spec_prefix"]+"/packages"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/packages"].split()

    def set_pkgcache_path(self):
        if "pkgcache_path" in self.settings:
            if not isinstance(self.settings['pkgcache_path'], str):
                self.settings["pkgcache_path"] = normpath(
                    ' '.join(self.settings["pkgcache_path"]))
        else:
            StageBase.set_pkgcache_path(self)
