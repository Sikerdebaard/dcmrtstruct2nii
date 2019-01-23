import pydicom
from pydicom.errors import InvalidDicomError

from dcmrtstruct2nii.adapters.input.abstractinputadapter import AbstractInputAdapter
from dcmrtstruct2nii.exceptions import InvalidFileFormatException


class RtStructInputAdapter(AbstractInputAdapter):
    def ingest(self, input_file, skip_contours=False):
        '''
            Load RT Struct DICOM from input_file and output intermediate format
            :param input_file: Path to the dicom rt-struct file
            :return: multidimensional array with ROI(s)
        '''

        try:
            rt_struct_image = pydicom.read_file(input_file)

            if not hasattr(rt_struct_image, 'StructureSetROISequence'):
                raise InvalidDicomError()

        except (IsADirectoryError, InvalidDicomError):
            raise InvalidFileFormatException('File {} is not an rt-struct dicom'.format(input_file))

        # lets extract the ROI(s) and dcmrtstruct2nii it to an intermediate format

        contours = [] # this var will hold the contours

        # first create a map so that we can easily trace referenced_roi_number back to its metadata
        metadata_mappings = {}
        for contour_metadata in rt_struct_image.StructureSetROISequence:
            metadata_mappings[contour_metadata.ROINumber] = contour_metadata

        for contour_sequence in rt_struct_image.ROIContourSequence:
            contour_data = {}

            metadata = metadata_mappings[contour_sequence.ReferencedROINumber] # retrieve metadata

            # I'm not sure if these attributes are always present in the metadata and contour_sequence
            # so I decided to write this in a defensive way.

            if hasattr(metadata, 'ROIName'):
                contour_data['name'] = metadata.ROIName

            if hasattr(metadata, 'ROINumber'):
                contour_data['roi_number'] = metadata.ROINumber

            if hasattr(metadata, 'ReferencedFrameOfReferenceUID'):
                contour_data['referenced_frame'] = metadata.ReferencedFrameOfReferenceUID

            if hasattr(contour_sequence, 'ROIDisplayColor') and len(contour_sequence.ROIDisplayColor) > 0:
                contour_data['display_color'] = contour_sequence.ROIDisplayColor

            if not skip_contours and hasattr(contour_sequence, 'ContourSequence') and len(contour_sequence.ContourSequence) > 0:
                contour_data['sequence'] = []
                for contour in contour_sequence.ContourSequence:
                    contour_data['sequence'].append({
                        'type': (contour.ContourGeometricType if hasattr(contour, 'ContourGeometricType') else 'unknown'),
                        'points': {
                            'x': ([contour.ContourData[index] for index in range(0, len(contour.ContourData), 3)] if hasattr(contour, 'ContourData') else None),  # this is just a fancy way to separate x, y, z from the rtstruct point array
                            'y': ([contour.ContourData[index + 1] for index in range(0, len(contour.ContourData), 3)] if hasattr(contour, 'ContourData') else None),  # this is just a fancy way to separate x, y, z from the rtstruct point array
                            'z': ([contour.ContourData[index + 2] for index in range(0, len(contour.ContourData), 3)] if hasattr(contour, 'ContourData') else None)   # this is just a fancy way to separate x, y, z from the rtstruct point array
                        }
                    })

            if contour_data:
                # only add contour if we successfully extracted (some) data
                contours.append(contour_data)

        return contours
