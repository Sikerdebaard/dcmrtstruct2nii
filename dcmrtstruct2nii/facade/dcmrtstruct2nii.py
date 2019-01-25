from dcmrtstruct2nii.adapters.convert.rtstructcontour2mask import DcmPatientCoords2Mask
from dcmrtstruct2nii.adapters.input.contours.rtstructinputadapter import RtStructInputAdapter
from dcmrtstruct2nii.adapters.input.image.dcminputadapter import DcmInputAdapter

import SimpleITK as sitk
import os.path

from dcmrtstruct2nii.adapters.output.niioutputadapter import NiiOutputAdapter
from dcmrtstruct2nii.exceptions import PathDoesNotExistException, ContourOutOfBoundsException

import numpy as np

import logging


def list_rt_structs(rtstruct_file):
    """
    Lists the structures in an DICOM RT Struct file by name.

    :param rtstruct_file: Path to the rtstruct file
    :return: A list of names, if any structures are found
    """
    if not os.path.exists(rtstruct_file):
        raise PathDoesNotExistException(f'rtstruct path does not exist: {rtstruct_file}')

    rtreader = RtStructInputAdapter()
    rtstructs = rtreader.ingest(rtstruct_file, True)
    return [struct['name'] for struct in rtstructs]


def dcmrtstruct2nii(rtstruct_file, dicom_file, output_path, structures=None, transpose=[2,0,1], fliplr=False, gzip=True):
    """
    Converts A DICOM and DICOM RT Struct file to nii

    :param rtstruct_file: Path to the rtstruct file
    :param dicom_file: Path to the dicom file
    :param output_path: Output path where the masks are written to
    :param structures: Optional, list of structures to convert
    :param transpose: Optional, permute the dimensions of output mask, example: (2,0,1,)
    :param fliplr: Optional, flip mask in the left/right direction if set to True
    :param gzip: Optional, output .nii.gz if set to True, default: True

    :raise InvalidFileFormatException: Raised when an invalid file format is given.
    :raise PathDoesNotExistException: Raised when the given path does not exist.
    :raise UnsupportedTypeException: Raised when conversion is not supported.
    """
    output_path = os.path.join(output_path, '')  # make sure trailing slash is there

    if not os.path.exists(rtstruct_file):
        raise PathDoesNotExistException(f'rtstruct path does not exist: {rtstruct_file}')

    if not os.path.exists(dicom_file):
        raise PathDoesNotExistException(f'DICOM path does not exists: {dicom_file}')

    if structures is None:
        structures = []

    os.makedirs(output_path, exist_ok=True)

    rtreader = RtStructInputAdapter()

    rtstructs = rtreader.ingest(rtstruct_file)
    dicom_image = DcmInputAdapter().ingest(dicom_file)

    dcm_patient_coords_to_mask = DcmPatientCoords2Mask()
    nii_output_adapter = NiiOutputAdapter()
    for rtstruct in rtstructs:
        if len(structures) == 0 or rtstruct['name'] in structures:
            logging.info('Working on mask {}'.format(rtstruct['name']))
            try:
                mask = dcm_patient_coords_to_mask.convert(rtstruct['sequence'], dicom_image, transpose)
            except ContourOutOfBoundsException:
                logging.warning(f'Structure {rtstruct["name"]} is out of bounds, ignoring contour!')
                continue

            mask.CopyInformation(dicom_image)

            nii_output_adapter.write(mask, f'{output_path}mask_{rtstruct["name"]}'.format(), gzip)

    logging.info('Converting original DICOM to nii')
    nii_output_adapter.write(dicom_image, f'{output_path}image', gzip)

    logging.info('Success!')
