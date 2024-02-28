from dcmrtstruct2nii.adapters.convert.rtstructcontour2mask import DcmPatientCoords2Mask
from dcmrtstruct2nii.adapters.convert.filenameconverter import FilenameConverter
from dcmrtstruct2nii.adapters.input.contours.rtstructinputadapter import RtStructInputAdapter
from dcmrtstruct2nii.adapters.input.image.dcminputadapter import DcmInputAdapter

import os.path

from dcmrtstruct2nii.adapters.output.niioutputadapter import NiiOutputAdapter
from dcmrtstruct2nii.exceptions import PathDoesNotExistException, ContourOutOfBoundsException

import logging


# cite
from dcmrtstruct2nii.cite import cite
from termcolor import cprint

cprint('\nPlease cite:', attrs=["bold"])
cprint(f'{cite}\n')


_default_maskname_pattern = ('ROINumber', 'ROIName')


def list_rt_structs(rtstruct_file, maskname_pattern=None):
    """
    Lists the structures in an DICOM RT Struct file by name.

    :param rtstruct_file: Path to the rtstruct file
    :return: A list of names, if any structures are found
    """
    if not maskname_pattern:
        maskname_pattern = _default_maskname_pattern

    if not os.path.exists(rtstruct_file):
        raise PathDoesNotExistException(f'rtstruct path does not exist: {rtstruct_file}')

    rtreader = RtStructInputAdapter()
    rtstructs = rtreader.ingest(rtstruct_file, maskname_pattern, True)
    return [struct['maskname'] for struct in rtstructs if 'maskname' in struct]


def dcmrtstruct2nii(rtstruct_file, dicom_file, output_path, structures=None, gzip=True, mask_background_value=0, mask_foreground_value=255, convert_original_dicom=True, series_id=None, maskname_pattern=None):  # noqa: C901 E501
    """
    Converts A DICOM and DICOM RT Struct file to nii

    :param rtstruct_file: Path to the rtstruct file
    :param dicom_file: Path to the dicom file
    :param output_path: Output path where the masks are written to
    :param structures: Optional, list of structures to convert
    :param gzip: Optional, output .nii.gz if set to True, default: True
    :param series_id: Optional, the Series Instance UID. Use  to specify the ID corresponding to the image if there are
    dicoms from more than one series in `dicom_file` folder

    :raise InvalidFileFormatException: Raised when an invalid file format is given.
    :raise PathDoesNotExistException: Raised when the given path does not exist.
    :raise UnsupportedTypeException: Raised when conversion is not supported.
    :raise ValueError: Raised when mask_background_value or mask_foreground_value is invalid.
    """
    output_path = os.path.join(output_path, '')  # make sure trailing slash is there

    if not maskname_pattern:
        maskname_pattern = _default_maskname_pattern

    if not os.path.exists(rtstruct_file):
        raise PathDoesNotExistException(f'rtstruct path does not exist: {rtstruct_file}')

    if not os.path.exists(dicom_file):
        raise PathDoesNotExistException(f'DICOM path does not exists: {dicom_file}')

    if mask_background_value < 0 or mask_background_value > 255:
        raise ValueError(f'Invalid value for mask_background_value: {mask_background_value}, must be between 0 and 255')

    if mask_foreground_value < 0 or mask_foreground_value > 255:
        raise ValueError(f'Invalid value for mask_foreground_value: {mask_foreground_value}, must be between 0 and 255')

    if structures is None:
        structures = []

    os.makedirs(output_path, exist_ok=True)

    filename_converter = FilenameConverter()
    rtreader = RtStructInputAdapter()

    rtstructs = rtreader.ingest(rtstruct_file, maskname_pattern=maskname_pattern)
    dicom_image = DcmInputAdapter().ingest(dicom_file, series_id=series_id)

    dcm_patient_coords_to_mask = DcmPatientCoords2Mask()
    nii_output_adapter = NiiOutputAdapter()
    for rtstruct in rtstructs:
        if len(structures) == 0 or rtstruct['name'] in structures:
            if 'sequence' not in rtstruct:
                logging.info('Skipping mask {} no shape/polygon found'.format(rtstruct['name']))
                continue

            maskname = rtstruct['maskname']
            logging.info(f'Working on mask {maskname}')
            try:
                mask = dcm_patient_coords_to_mask.convert(rtstruct['sequence'], dicom_image, mask_background_value, mask_foreground_value)
            except ContourOutOfBoundsException:
                logging.warning(f'Structure {maskname} is out of bounds, ignoring contour!')
                continue

            mask.CopyInformation(dicom_image)

            mask_filename = filename_converter.convert(f'mask_{maskname}')
            nii_output_adapter.write(mask, f'{output_path}{mask_filename}', gzip)

    if convert_original_dicom:
        logging.info('Converting original DICOM to nii')
        nii_output_adapter.write(dicom_image, f'{output_path}image', gzip)

    logging.info('Success!')
