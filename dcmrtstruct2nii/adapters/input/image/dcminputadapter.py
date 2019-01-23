import SimpleITK as sitk


from dcmrtstruct2nii.adapters.input.abstractinputadapter import AbstractInputAdapter
from dcmrtstruct2nii.exceptions import InvalidFileFormatException


class DcmInputAdapter(AbstractInputAdapter):
    def ingest(self, input_dir):
        '''
            Load DICOMs from input_dir to a single 3D image and make sure axial
            direction is on third axis.
            :param input_dir: Input directory where the dicom files are located
            :return: multidimensional array with pixel data, metadata
        '''
        dicom_reader = sitk.ImageSeriesReader()
        dicom_file_names = dicom_reader.GetGDCMSeriesFileNames(str(input_dir))

        if not dicom_file_names:
            raise InvalidFileFormatException('Directory {} is not a dicom'.format(input_dir))

        dicom_reader.SetFileNames(dicom_file_names)

        dicom_image = dicom_reader.Execute()

        return dicom_image
