from cleo.commands.command import Command
from cleo.helpers import option

import logging

from dcmrtstruct2nii.facade.dcmrtstruct2nii import list_rt_structs


class ListStructs(Command):
    name = "ls"
    description = "List structures in RT Struct"

    options = [
        option(
            "rtstruct",
            "r",
            description="Path to DICOM RT Struct file, example: /tmp/DICOM/resources/secondary/rtstruct.dcm",
            flag=False,
        ),
    ]

    def handle(self):
        file_path = self.option('rtstruct')

        if not file_path:
            self.call('help', 'ls')
            return -1

        structs = list_rt_structs(file_path)

        for struct in structs:
            print(struct)

        print(f'Found {len(structs)} structures')
