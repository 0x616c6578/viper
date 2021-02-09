# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from viper.common.out import print_info
from viper.common.out import print_error
from viper.common.out import print_output
from viper.core.plugins import load_commands, load_modules
from viper.core.session import __sessions__
from viper.core.database import Database
from viper.core.config import __config__
from viper.core.storage import get_sample_path

cfg = __config__


def parse_commands(data):
    root = ''
    args = []
    words = data.split()
    root = words[0]

    if len(words) > 1:
        args = words[1:]

    return root, args


def autorun_module(file_hash):
    if not file_hash:
        return

    if not __sessions__.is_set():
        __sessions__.new(get_sample_path(file_hash))

    for cmd_line in cfg.autorun.modules.split(','):
        split_commands = cmd_line.split(';')

        for split_command in split_commands:
            split_command = split_command.strip()

            if not split_command:
                continue

            root, args = parse_commands(split_command)
            loaded_modules = load_modules()

            try:
                if root in loaded_modules:
                    print_info("Running module \"{0}\"".format(split_command))

                    module = loaded_modules[root]['obj']()
                    module.set_commandline(args)
                    module.run()

                    if cfg.modules.store_output and __sessions__.is_set():
                        Database().add_analysis(file_hash, split_command, module.output)

                    if cfg.autorun.verbose:
                        print_output(module.output)

                    del(module.output[:])
                else:
                    print_error("\"{0}\" is not a valid module. Please check your viper.conf file.".format(cmd_line))
            except Exception:
                print_error("Viper was unable to complete the module {0}".format(cmd_line))


def autorun_command(file_hash):
    if not file_hash:
        return

    if not __sessions__.is_set():
        __sessions__.new(get_sample_path(file_hash))

    loaded_commands = load_commands()

    # NOTE(Alex): this is a quick hack to determine if no commands are in viper.conf. This is likely to be an issue in other places
    # and should be addressed in a more efficient manner.
    autorun_commands = cfg.autorun.commands
    if not cfg.autorun.commands:
        return

    for cmd_line in autorun_commands.split(','):
        split_commands = cmd_line.split(';')

        for split_command in split_commands:
            split_command = split_command.strip()

            if not split_command:
                continue

            root, args = parse_commands(split_command)

            try:
                if root in loaded_commands:
                    print_info("Running command \"{0}\"".format(split_command))
                    # TODO(Alex): Find a way to pass args to a Command (abstracts.py).
                    # The code for Module could just be replicated, but that is likely to break other functionality.
                    command = loaded_commands[root]['obj']()
                else:
                    print_error("\"{0}\" is not a valid command. Please check your viper.conf file.".format(cmd_line))
            except Exception:
                print_error("Viper was unable to complete the command {0}".format(cmd_line))