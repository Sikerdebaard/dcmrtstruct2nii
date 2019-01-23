import pydicom
from pydicom.errors import InvalidDicomError
import SimpleITK as sitk

from dcmrtstruct2nii.adapters.input.abstractinputadapter import AbstractInputAdapter
from dcmrtstruct2nii.exceptions import InvalidFileFormatException


class DcmMetadataInputAdapter(AbstractInputAdapter):
    def ingest(self, input_dir):
        '''
            Load DICOMs metadata
            :param input_dir: Input directory where the dicom files are located
            :return: dict of properties
        '''
        dicom_reader = sitk.ImageSeriesReader()
        dicom_file_names = dicom_reader.GetGDCMSeriesFileNames(str(input_dir))

        if not dicom_file_names:
            raise InvalidFileFormatException('Directory {} is not a dicom'.format(input_dir))

        try:
            # we probably want to use this in the future, once we start refactoring: [field for field in dir(dicom) if len(field) > 0 and field[0].isupper()]
            dicoms = []
            for i in range(0, len(dicom_file_names)):
                dicoms.append(pydicom.read_file(dicom_file_names[i]))
            return dicoms
            #return {field: getattr(dicom, field) for field in dir(dicom) if len(field) > 0 and field[0].isupper()}
            #return dict(pydicom.read_file(dicom_file_names[0])) # not the correct way to do this mapping, but ok for now
            # we should refactor this so that it maps based on the objects fields and values
        except (IsADirectoryError, InvalidDicomError):
            raise InvalidFileFormatException('File {} is not a dicom'.format(dicom_file_names[0]))
