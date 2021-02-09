# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import os

from viper.common.abstracts import Command
from viper.core.session import __sessions__
from viper.core.database import Database
from viper.core.storage import get_sample_path


class Delete(Command):
    """
    This command deletes the currently opened file (only if it's stored in
    the local repository) and removes the details from the database
    """
    cmd = "delete"
    description = "Delete the opened file"


    def __init__(self):
        super(Delete, self).__init__()
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-a', '--all', action='store_true', help="Delete ALL files in this project")
        group.add_argument('-f', '--find', action="store_true", help="Delete ALL files from last find")
        self.parser.add_argument('-p', '--preservechildren', action="store_true", help="Preserve child files.")


    def run(self, *args):
        try:
            args = self.parser.parse_args(args)
        except SystemExit:
            return

        while True:
            choice = input("Are you sure? It can't be reverted! [y/n] ")
            if choice == 'y':
                break
            elif choice == 'n':
                return

        db = Database()

        if args.all:
            if __sessions__.is_set():
                __sessions__.close()

            samples = db.find('all')
            for sample in samples:
                self.delete_file(sample)

            self.log('info', "Deleted a total of {} files.".format(len(samples)))

        elif args.find:
            if not __sessions__.find:
                self.log('error', "No find result")
                return

            samples = __sessions__.find
            for sample in samples:
                self.delete_file(sample)

            self.log('info', "Deleted {} files.".format(len(samples)))
                

        else:
            if not __sessions__.is_set():
                self.log('error', "No session open, and no --all argument. Nothing to delete.")
                return

            rows = db.find('sha256', __sessions__.current.file.sha256)
            if not rows:
                self.log('error', "No matching files were found in the current project.")
                return

            malware = rows[0]

            if args.preservechildren:
                # Remove the parent reference from first-level children
                children = db.list_children(malware.id)
                for child in children:
                    db.delete_parent(child.sha256)
            else:
                # Delete all children, recursively
                children_sha256 = db.get_children(malware.id, recursive=True)
                for child_sha256 in filter(None, children_sha256.split(",")):
                    child = db.find('sha256', child_sha256)
                    self.delete_file(child[0])

            self.delete_file(malware)

            __sessions__.close()

            self.log('info', "Deleted opened file.")


    def delete_file(self, malware):
        if Database().delete_file(malware.id):
            self.log("success", "File deleted '{}'".format(malware.name))
        else:
            self.log('error', "Unable to delete file '{}'".format(malware.name))
        os.remove(get_sample_path(malware.sha256))

