# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from viper.common.abstracts import Command
from viper.core.database import Database
from viper.core.storage import get_sample_path
from viper.core.session import __sessions__


class Parent(Command):
    """
    This command is used to view or edit the parent child relationship between files.
    """
    cmd = "parent"
    description = "Add or remove a parent file"

    def __init__(self):
        super(Parent, self).__init__()
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-a', '--add', metavar='SHA256', help="Add parent file by sha256")
        group.add_argument('-d', '--delete', action='store_true', help="Delete Parent")
        group.add_argument('-o', '--open', action='store_true', help="Open The Parent")

    
    def run(self, *args):
        try:
            args = self.parser.parse_args(args)
        except SystemExit:
            return

        # This command requires a session to be opened.
        if not __sessions__.is_set():
            self.log('error', "No open session. This command expects a file to be open.")
            self.parser.print_usage()
            return

        db = Database()

        # TODO(alex): Allow other fields similar to open.py i.e. md5/id
        if not db.find(key='sha256', value=__sessions__.current.file.sha256):
            self.log('error', "The opened file is not stored in the database. "
                              "If you want to add it use the `store` command.")
            return

        elif args.add:
            if not db.find(key='sha256', value=args.add):
                self.log('error', "the parent file is not found in the database. ")
                return
            db.add_parent(__sessions__.current.file.sha256, args.add)
            self.log('info', "parent added to the currently opened file")

            self.log('info', "Refreshing session to update attributes...")
            __sessions__.new(__sessions__.current.file.path)

        elif args.delete:
            db.delete_parent(__sessions__.current.file.sha256)
            self.log('info', "parent removed from the currently opened file")

            self.log('info', "Refreshing session to update attributes...")
            __sessions__.new(__sessions__.current.file.path)

        elif args.open:
            # Open a session on the parent
            if __sessions__.current.file.parent:
                __sessions__.new(get_sample_path(__sessions__.current.file.parent[-64:]))
            else:
                self.log('info', "No parent set for this sample")

        else:
            self.parser.print_usage()
            return
