from cleo import Command
import logging

from dcmrtstruct2nii.facade.dcmrtstruct2nii import list_rt_structs


class ListStructs(Command):
    """
    List structures in RT Struct

    list
        {--r|rtstruct= : Path to DICOM RT Struct file}
    """
    def handle(self):
        file_path = self.option('rtstruct')

        if not file_path:
            logging.error('dcmrtstruct2nii list --rtstruct <..>')
            return -1

        structs = list_rt_structs(file_path)

        for struct in structs:
            print(struct)

        print(f'Found {len(struct)} structures')

