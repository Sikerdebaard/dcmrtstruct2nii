from dcmrtstruct2nii.cli.wrapper.patchedcommand import PatchedCommand
from dcmrtstruct2nii.exceptions import InvalidFileFormatException, PathDoesNotExistException, UnsupportedTypeException
from dcmrtstruct2nii.facade.dcmrtstruct2nii import dcmrtstruct2nii

import logging

class Convert(PatchedCommand):
    """
    Convert RT Struct to nii. If no structures are specified all will be converted.

    convert
        {--r|rtstruct= : Path to DICOM RT Struct file, example: /tmp/DICOM/resources/secondary/rtstruct.dcm}
        {--d|dicom= : Path to original DICOM file, example: /tmp/DICOM/resources/files}
        {--o|output= : Output path, example: /tmp/output}
        {--t|transpose=? : Optional, permute the dimensions of output mask, example: 2,0,1}
        {--f|fliplr=?false : Optional, flip mask in the left/right direction}
        {--g|gzip=?true : Optional, gzip output .nii}
        {--s|structures=? : Optional, list of structures that need to be converted, example: Patient, Spinal, Dose-1}
    """
    def handle(self):
        rtstruct_file = self.option('rtstruct')
        dicom_file = self.option('dicom')

        output_path = self.option('output')

        transpose = self.option('transpose')
        fliplr = self._castToBool(self.option('fliplr'))
        gzip = self._castToBool(self.option('gzip'))
        structures = self.option('structures')

        if transpose:
            transpose = [int(x) for x in transpose.split(',')]
        else:
            transpose = [2, 0, 1]

        if structures:
            structures = [x.strip() for x in structures.split(',')]

        if not rtstruct_file or not dicom_file or not output_path:
            logging.error('dcmrtstruct2nii convert needs the following parameters at minimum: --rtstruct <..> --dicom <..> --output <..>')
            return -1

        try:
            dcmrtstruct2nii(rtstruct_file, dicom_file, output_path, structures, transpose, fliplr, gzip)
        except (InvalidFileFormatException, PathDoesNotExistException, UnsupportedTypeException,) as e:
            logging.error(str(e))
