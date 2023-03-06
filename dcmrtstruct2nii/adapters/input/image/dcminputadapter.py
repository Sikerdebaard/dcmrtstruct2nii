import SimpleITK as sitk


from dcmrtstruct2nii.adapters.input.abstractinputadapter import AbstractInputAdapter
from dcmrtstruct2nii.exceptions import InvalidFileFormatException


class DcmInputAdapter(AbstractInputAdapter):
    def ingest(self, input_dir, series_id=None):
        '''
            Load DICOMs from input_dir to a single 3D image and make sure axial
            direction is on third axis.
            :param input_dir: Input directory where the dicom files are located
            :param series_id: Optional, the Series Instance UID for the image dicoms
            :return: multidimensional array with pixel data, metadata
        '''
        dicom_reader = sitk.ImageSeriesReader()

        if series_id is None:
            series_id = ''

        dicom_file_names = dicom_reader.GetGDCMSeriesFileNames(str(input_dir), seriesID=series_id)

        if not dicom_file_names:
            raise InvalidFileFormatException('Directory {} is not a dicom'.format(input_dir))

        dicom_reader.SetFileNames(dicom_file_names)

        dicom_image = dicom_reader.Execute()

        return dicom_image
