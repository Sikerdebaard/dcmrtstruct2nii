from cleo.commands.command import Command
from cleo.helpers import option

import logging

from dcmrtstruct2nii.facade.dcmrtstruct2nii import list_rt_structs, _default_maskname_pattern


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
        option(
            "maskname_pattern",
            "m",
            description="The naming pattern to use for the RTStruct mask names",
            flag=False,
            default=','.join(_default_maskname_pattern),
        ),
    ]

    def handle(self):
        file_path = self.option('rtstruct')

        if not file_path:
            self.call('help', 'ls')
            return -1

        maskname_pattern = self.option('maskname_pattern')
        if maskname_pattern:
            maskname_pattern = [x.strip() for x in maskname_pattern.split(',')]

        structs = list_rt_structs(file_path, maskname_pattern=maskname_pattern)

        for struct in structs:
            print(struct)

        print(f'Found {len(structs)} structures')
