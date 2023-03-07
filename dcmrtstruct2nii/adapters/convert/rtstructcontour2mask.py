import numpy as np
from skimage import draw
import SimpleITK as sitk

from dcmrtstruct2nii.exceptions import ContourOutOfBoundsException

import logging


class DcmPatientCoords2Mask():
    def _poly2mask(self, coords_x, coords_y, shape):
        mask = draw.polygon2mask(tuple(reversed(shape)), np.column_stack((coords_y, coords_x)))

        return mask

    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground):
        shape = dicom_image.GetSize()

        mask = sitk.Image(shape, sitk.sitkUInt8)
        mask.CopyInformation(dicom_image)

        np_mask = sitk.GetArrayFromImage(mask)
        np_mask.fill(mask_background)

        for contour in rtstruct_contours:
            if contour['type'].upper() not in ['CLOSED_PLANAR', 'INTERPOLATED_PLANAR']:
                if 'name' in contour:
                    logging.info(f'Skipping contour {contour["name"]}, unsupported type: {contour["type"]}')
                else:
                    logging.info(f'Skipping unnamed contour, unsupported type: {contour["type"]}')
                continue

            coordinates = contour['points']

            pts = np.zeros([len(coordinates['x']), 3])

            for index in range(0, len(coordinates['x'])):
                # lets convert world coordinates to voxel coordinates
                world_coords = dicom_image.TransformPhysicalPointToContinuousIndex((coordinates['x'][index], coordinates['y'][index], coordinates['z'][index]))
                pts[index, 0] = world_coords[0]
                pts[index, 1] = world_coords[1]
                pts[index, 2] = world_coords[2]

            z = int(round(pts[0, 2]))

            try:
                filled_poly = self._poly2mask(pts[:, 0], pts[:, 1], [shape[0], shape[1]])
                new_mask = np.logical_xor(np_mask[z, :, :], filled_poly)
                np_mask[z, :, :] = np.where(new_mask, mask_foreground, mask_background)
            except IndexError:
                # if this is triggered the contour is out of bounds
                raise ContourOutOfBoundsException()
            except RuntimeError as e:
                # this error is sometimes thrown by SimpleITK if the index goes out of bounds
                if 'index out of bounds' in str(e):
                    raise ContourOutOfBoundsException()
                raise e  # something serious is going on

        mask = sitk.GetImageFromArray(np_mask)  # Avoid redundant calls by moving this here
        return mask
