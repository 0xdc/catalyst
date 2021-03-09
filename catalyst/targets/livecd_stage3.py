"""
LiveCD stage3 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import normpath
from catalyst.fileops import clear_dir
from catalyst.targets.livecd_stage1 import livecd_stage1


class livecd_stage3(livecd_stage1):
    """
    Builder class for LiveCD stage3.

    Wraps any stage into a CD image

    Requires a cached kernel name and cdtar
    """
    required_values = frozenset([
        "boot/kernel",
        "livecd/cdtar",
    ])
    valid_values = required_values | frozenset([
        "livecd/bootargs",
        "livecd/empty",
        "livecd/fsscript",
        "livecd/fstype",
        "livecd/fsops",
        "livecd/iso",
        "livecd/rm",
        "livecd/root_overlay",
        "livecd/type",
        "livecd/verify",
        "livecd/volid",
    ])

    def set_action_sequence(self):
        self.settings['action_sequence'] = [
            "unpack",
            "bind",
            "setup_environment",
            "root_overlay",
            "bootloader",
            "unbind",
            "remove",
            "empty",
            "clean",
            "fsscript",
            "target_setup",
            "create_iso",
            "clear_autoresume",
            "remove_chroot",
        ]

    def set_target_path(self):
        '''Set the target path for the finished stage.

        This method runs the StageBase.set_target_path method,
        and additionally creates a staging directory for assembling
        the final components needed to produce the iso image.
        '''
        super(livecd_stage1, self).set_target_path()
        clear_dir(self.settings['target_path'])
