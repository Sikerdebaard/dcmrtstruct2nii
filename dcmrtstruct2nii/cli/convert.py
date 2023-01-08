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
        {--g|gzip=?true : Optional, gzip output .nii}
        {--s|structures=? : Optional, list of structures that need to be converted, example: Patient, Spinal, Dose-1}
        {--i|series-id=? : Optional, the Series ID of the image DICOMs. Use to exclude other series in the same directory}
        {--f|mask-foreground-color=?255 : Optional, the foreground color used for the mask. Must be between 0-255.}
        {--b|mask-background-color=?0 : Optional, the background color used for the mask. Must be between 0-255.}
        {--c|convert-original-dicom=?true : Optional, convert the original dicom to nii}
        {--a|xy-scaling-factor=?1 : Optional, Increase pixel density with this factor in xy. Must be 1 or more}
    """
    def handle(self):
        rtstruct_file = self.option('rtstruct')
        dicom_file = self.option('dicom')

        output_path = self.option('output')

        gzip = self._castToBool(self.option('gzip'))
        structures = self.option('structures')

        mask_foreground = int(self.option('mask-foreground-color'))
        mask_background = int(self.option('mask-background-color'))

        convert_original_dicom = self._castToBool(self.option('convert-original-dicom'))

        series_id = self.option('series-id')

        xy_scaling_factor = int(self.option('xy-scaling-factor'))

        if structures:
            structures = [x.strip() for x in structures.split(',')]

        if not rtstruct_file or not dicom_file or not output_path:
            logging.error('dcmrtstruct2nii convert needs the following parameters at minimum: --rtstruct <..> --dicom <..> --output <..>')
            return -1

        if not xy_scaling_factor >= 1:
            logging.error('xy_scaling_factor must be a positive integer')
            return -1

        try:
            dcmrtstruct2nii(rtstruct_file, dicom_file, output_path, structures, gzip, mask_background, mask_foreground, convert_original_dicom, series_id,
                            xy_scaling_factor=xy_scaling_factor)
        except (InvalidFileFormatException, PathDoesNotExistException, UnsupportedTypeException, ValueError,) as e:
            logging.error(str(e))
