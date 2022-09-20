"""
LiveCD stage2 target, builds upon previous LiveCD stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import (normpath, file_locate, CatalystError)
from catalyst.fileops import clear_dir
from catalyst.base.stagebase import StageBase


class livecd_stage2(StageBase):
    """
    Builder class for a LiveCD stage2 build.
    """
    required_values = frozenset([
        "boot/kernel",
    ])
    valid_values = required_values | frozenset([
        "livecd/bootargs",
        "livecd/gk_mainargs",
        "livecd/readme",
        "livecd/type",
        "livecd/verify",
        "repos",
    ])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "livecd"

    def set_target_path(self):
        '''Set the target path for the finished stage.

        This method runs the StageBase.set_target_path mehtod,
        and additionally creates a staging directory for assembling
        the final components needed to produce the iso image.
        '''
        super(livecd_stage2, self).set_target_path()
        clear_dir(self.settings['target_path'])

    def run_local(self):
        # what modules do we want to blacklist?
        if "livecd/modblacklist" in self.settings:
            path = normpath(self.settings["chroot_path"] +
                            "/etc/modprobe.d/blacklist.conf")
            try:
                with open(path, "a") as myf:
                    myf.write("\n#Added by Catalyst:")
                    # workaround until config.py is using configparser
                    if isinstance(self.settings["livecd/modblacklist"], str):
                        self.settings["livecd/modblacklist"] = self.settings[
                            "livecd/modblacklist"].split()
                    for x in self.settings["livecd/modblacklist"]:
                        myf.write("\nblacklist "+x)
            except Exception as e:
                raise CatalystError("Couldn't open " +
                                    self.settings["chroot_path"] +
                                    "/etc/modprobe.d/blacklist.conf.",
                                    print_traceback=True) from e

    def set_stage_path(self):
        self.set_target_path()
        self.settings['stage_path'] = self.settings['target_path']

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.run_local,
        ])
        if "fetch" not in self.settings["options"]:
            self.build_sequence.extend([
                self.build_kernel,
                self.bootloader,
            ])
            self.set_completion_action_sequences()
