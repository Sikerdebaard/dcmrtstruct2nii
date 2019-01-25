import numpy as np
from skimage import draw
import SimpleITK as sitk

from dcmrtstruct2nii.exceptions import ContourOutOfBoundsException

import logging

class DcmPatientCoords2Mask():
    def _poly2mask(self, coords_x, coords_y, shape):
        fill_coords_x, fill_coords_y = draw.polygon(coords_x, coords_y, shape)
        mask = np.zeros(shape, dtype=np.bool)
        mask[fill_coords_x, fill_coords_y] = True

        return mask

    def convert(self, rtstruct_contours, dicom_image, transpose):
        # lets convert world coordinates to voxel coordinates

        shape = dicom_image.GetSize()
        mask = np.zeros(shape, dtype=np.uint8)

        for contour in rtstruct_contours:
            if contour['type'].upper() != 'CLOSED_PLANAR':
                logging.info(f'Skipping contour {contour["name"]}, unsupported type: {contour["type"]}')
                continue

            coordinates = contour['points']

            pts = np.zeros([len(coordinates['x']), 3])

            for index in range(0, len(coordinates['x'])):
                world_coords = dicom_image.TransformPhysicalPointToIndex((coordinates['x'][index], coordinates['y'][index], coordinates['z'][index]))
                pts[index, 0] = world_coords[0]
                pts[index, 1] = world_coords[1]
                pts[index, 2] = world_coords[2]

            slice_index = int(pts[0, 2])

            try:
                filled_poly = np.logical_or(mask[:, :,  slice_index], self._poly2mask(pts[:, 0], pts[:, 1], [shape[0], shape[1]]))
            except IndexError:
                # if this is triggered the contour is out of bounds
                raise ContourOutOfBoundsException()


            mask[filled_poly, slice_index] = 255

        mask = np.transpose(mask, transpose) # rotate to correct orientation

        mask = sitk.GetImageFromArray(mask)

        return mask
