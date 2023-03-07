from dcmrtstruct2nii.cli.wrapper.patchedcommand import PatchedCommand
from dcmrtstruct2nii.exceptions import InvalidFileFormatException, PathDoesNotExistException, UnsupportedTypeException
from dcmrtstruct2nii.facade.dcmrtstruct2nii import dcmrtstruct2nii

from cleo.helpers import option

import logging


class Convert(PatchedCommand):
    name = "convert"
    description = "Convert RT Struct to nii. If no structures are specified all will be converted."

    options = [
        option(
            "rtstruct",
            "r",
            description="Path to DICOM RT Struct file, example: /tmp/DICOM/resources/secondary/rtstruct.dcm",
            flag=False,
        ),
        option(
            "dicom",
            "d",
            description="Path to original DICOM file, example: /tmp/DICOM/resources/files",
            flag=False,
        ),
        option(
            "output",
            "o",
            description="Output path, example: /tmp/output",
            flag=False,
        ),
        option(
            "gzip",
            "g",
            description="Gzip output .nii",
            flag=False,
            default=True,
        ),
        option(
            "structures",
            "s",
            description="List of structures that need to be converted, example: Patient, Spinal, Dose-1",
            multiple=True,
            flag=False,
        ),
        option(
            "series-id",
            "i",
            description="The Series ID of the image DICOMs. Use to exclude other series in the same directory",
            flag=False,
            default=None,
        ),
        option(
            "mask-foreground-color",
            "f",
            description="The foreground color used for the mask. Must be between 0-255.",
            default=255,
            flag=False,
        ),
        option(
            "mask-background-color",
            "b",
            description="The foreground color used for the mask. Must be between 0-255.",
            default=0,
            flag=False,
        ),
        option(
            "convert-original-dicom",
            "c",
            description="Convert the original dicom to nii.",
            default=True,
            flag=False,
        ),
    ]

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

        if structures:
            structures = [x.strip() for x in structures.split(',')]

        if not rtstruct_file or not dicom_file or not output_path:
            self.call('help', 'convert')
            return -1

        try:
            dcmrtstruct2nii(rtstruct_file, dicom_file, output_path, structures, gzip, mask_background, mask_foreground, convert_original_dicom, series_id)
        except (InvalidFileFormatException, PathDoesNotExistException, UnsupportedTypeException, ValueError,) as e:
            logging.error(str(e))
