import zipfile
from tempfile import TemporaryDirectory
import os

from viper.core.ui.cmd.store import Store
from viper.common.abstracts import Command
from viper.core.session import __sessions__
from viper.core.database import Database

# NOTE: This is a test Command only and should not be used in production.

class Extract(Command):
    cmd = "extract"
    description = "Archive exctractor"
    authors = ["0x616c6578"]

    def __init__(self):
        super(Extract, self).__init__()

    def run(self):
        parent = __sessions__.current.file

        with TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(__sessions__.current.file.path,"r") as archive:
                archive.extractall(tmpdir)
                self.log('info', "Archive extracted to temporary directory '{}'".format(tmpdir))

            for extracted_file in os.listdir(tmpdir):
                file_path = tmpdir + "/" + extracted_file
                __sessions__.new(file_path)
                # TODO(Alex): Add parameter to the Store Command so a parent can be defined when the file is stored.
                Store().run()
                Database().add_parent(__sessions__.current.file.sha256, parent.sha256)

        __sessions__.new(parent.path)
            
