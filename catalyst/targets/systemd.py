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
        "boot/kernel",
        "embedded/empty",
        "embedded/fsops",
        "embedded/fsscript",
        "embedded/fstype",
        "embedded/iso",
        "embedded/rm",
        "embedded/root_overlay",
        "embedded/use",
        "embedded/volid",
    ])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "embedded"

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.build_packages,
            self.build_kernel,
            self.bootloader,
            self.root_overlay,
            self.fsscript,
        ])
        self.finish_sequence.extend([
            self.remove,
            self.empty,
        ])
        self.set_completion_action_sequences()

    def set_completion_action_sequences(self):
        if "fetch" not in self.settings["options"]:
            iso = "%s/iso" % self.settings["spec_prefix"]
            if iso in self.settings:
                self.finish_sequence.extend([
                    self.target_setup,
                    self.create_iso,
                ])
            else:
                self.finish_sequence.append(self.capture)

        if "keepwork" in self.settings["options"]:
            self.finish_sequence.append(self.clear_autoresume)
        elif "seedcache" in self.settings["options"]:
            self.finish_sequence.append(self.remove_autoresume)
        else:
            self.finish_sequence.append(self.remove_autoresume)
            self.finish_sequence.append(self.remove_chroot)

    def set_root_path(self):
        self.settings["root_path"] = normpath("/tmp/mergeroot")
        log.info('mergeroot path is %s', self.settings['root_path'])
