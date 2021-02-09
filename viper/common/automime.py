#TODO(alex): This closely mirrors autorun.py. It should be possible to modify autorun.py to suit both needs.
from viper.common.out import print_info, print_error, print_output

from viper.core.mimetypes import __mimetypes__
from viper.core.session import __sessions__
from viper.core.plugins import load_commands, load_modules
from viper.core.database import Database


# Identify the commands for matching mimetype/s
def mimetype_modules(file_hash):
    if not file_hash:
        return

    if not __sessions__.is_set():
        __sessions__.new(get_sample_path(file_hash))

    mime_modules = __mimetypes__.get('modules')
    command_list = []

    for mimetype in mime_modules:
        if mimetype in __sessions__.current.file.mime:
            command_list.append(mime_modules[mimetype])

    option_verbose = __mimetypes__.get('autorun')['verbose']

    # Nested loops/logic make this difficult to follow. Consider refactoring.
    for commands in command_list:
        for cmd_line in commands.split(','):
            split_commands = cmd_line.split(';')

            for split_command in split_commands:
                split_command = split_command.strip()

                if not split_command:
                    continue

                root, args = parse_commands(split_command)
                loaded_modules = load_modules()

                try:
                    if root in loaded_modules:
                        print_info("Running command \"{0}\"".format(split_command))

                        module = loaded_modules[root]['obj']()
                        module.set_commandline(args)
                        module.run()

                        Database().add_analysis(file_hash, split_command, module.output)
                        if option_verbose:
                            print_output(module.output)

                        del(module.output[:])
                    else:
                        print_error("\"{0}\" is not a valid command. Please check your mime.conf file.".format(cmd_line))
                except Exception:
                    print_error("Viper was unable to complete the command {0}".format(cmd_line))


def mimetype_commands(file_hash):
    if not file_hash:
        return

    if not __sessions__.is_set():
        __sessions__.new(get_sample_path(file_hash))

    commands_list = load_commands()

    mime_commands = __mimetypes__.get('commands')
    command_list = []

    for mimetype in mime_commands:
        if mimetype in __sessions__.current.file.mime:
            command_list.append(mime_commands[mimetype])

    option_verbose = __mimetypes__.get('autorun')['verbose']

    loaded_commands = load_commands()

    # Nested loops/logic make this difficult to follow. Consider refactoring.
    for commands in command_list:
        for cmd_line in commands.split(','):
            split_commands = cmd_line.split(';')

            for split_command in split_commands:
                split_command = split_command.strip()

                if not split_command:
                    continue

                root, args = parse_commands(split_command)

                try:
                    if root in loaded_commands:
                        print_info("Running command \"{0}\"".format(split_command))
                        loaded_commands[root]['obj']()
                    else:
                        print_error("\"{0}\" is not a valid command. Please check your mime.conf file.".format(cmd_line))
                except Exception:
                    print_error("Viper was unable to complete the command {0}".format(cmd_line))



def parse_commands(data):
    root = ''
    args = []
    words = data.split()
    root = words[0]

    if len(words) > 1:
        args = words[1:]

    return root, args 