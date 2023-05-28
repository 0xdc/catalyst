"""
LiveCD stage3 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
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
        "profile", # deprecated
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

    def set_profile_required(self):
        return frozenset([])

    def set_target_profile(self):
        if "profile" in self.settings:
            log.notice("Deprecated setting 'profile' is set in specfile.")

    def set_action_sequence(self):
        self.prepare_sequence = [
                self.unpack,
                # do not need:
                #   config_profile_link
                #   setup_confdir
                #   process_repos
        ]
        self.build_sequence = [
                self.bind,
                # chroot_setup
                self.setup_environment,
                # enter_chroot
                self.root_overlay,
                self.bootloader,
        ]
        self.finish_sequence.extend([
            self.remove,
            self.empty,
            self.clean,
            self.fsscript,
            self.target_setup,
            self.create_iso,
            self.clear_autoresume,
            self.remove_chroot,
        ])

    def set_target_path(self):
        '''Set the target path for the finished stage.

        This method runs the StageBase.set_target_path method,
        and additionally creates a staging directory for assembling
        the final components needed to produce the iso image.
        '''
        super(livecd_stage3, self).set_target_path()
        clear_dir(self.settings['target_path'])

    def clean(self):
        self.settings['options'].append("sticky-config")
        super(livecd_stage3, self).clean()
