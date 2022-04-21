"""
systemd target, similar to the embedded target

A stage tarball is unpacked, but instead
of building packages for the stage, it emerges packages into another directory.
This way, we do not have to emerge GCC/portage into the staged system.
It may sound complicated but basically it runs
ROOT=/tmp/submerge emerge --something foo bar .
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
from catalyst.support import normpath
from catalyst.base.stagebase import StageBase


class systemd(StageBase):
    """
    Builder class for systemd target
    """
    required_values = frozenset([
        "embedded/packages",
    ])
    valid_values = required_values | frozenset([
        "embedded/empty",
        "embedded/fsscript",
        "embedded/fstype",
        "embedded/rm",
        "embedded/root_overlay",
        "embedded/use",
    ])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "embedded"

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.build_packages,
            self.root_overlay,
            self.fsscript,
        ])
        self.finish_sequence.extend([
            self.remove,
            self.empty,
        ])
        self.set_completion_action_sequences()

    def set_root_path(self):
        self.settings["root_path"] = normpath("/tmp/mergeroot")
        log.info('mergeroot path is %s', self.settings['root_path'])
