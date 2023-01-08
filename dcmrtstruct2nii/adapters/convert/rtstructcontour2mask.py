import logging

import SimpleITK as sitk
import numpy as np
from skimage import draw

from dcmrtstruct2nii.exceptions import ContourOutOfBoundsException


def scale_information_tuple(information_tuple: tuple, xy_scaling_factor: int, out_type: type, up: bool = True):
    scale_array = np.array([xy_scaling_factor, xy_scaling_factor, 1])
    if up:
        information_tuple = np.array(information_tuple) * scale_array
    else:
        information_tuple = np.array(information_tuple) / scale_array

    return out_type(information_tuple[0]), out_type(information_tuple[1]), out_type(information_tuple[2])


class DcmPatientCoords2Mask:
    def _poly2mask(self, coords_x, coords_y, shape, xy_scaling_factor):
        coords_x = coords_x * xy_scaling_factor
        coords_y = coords_y * xy_scaling_factor
        mask = draw.polygon2mask(tuple(reversed(shape)), np.column_stack((coords_y, coords_x)))

        return mask

    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground, xy_scaling_factor=1):
        shape = scale_information_tuple(information_tuple=dicom_image.GetSize(), xy_scaling_factor=xy_scaling_factor, up=True, out_type=int)
        spacing = scale_information_tuple(information_tuple=dicom_image.GetSpacing(), xy_scaling_factor=xy_scaling_factor, up=False, out_type=float)

        mask = sitk.Image(*shape, sitk.sitkUInt8)
        mask.SetSpacing(spacing)
        mask.SetDirection(dicom_image.GetDirection())
        mask.SetOrigin(dicom_image.GetOrigin())

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
                filled_poly = self._poly2mask(pts[:, 0], pts[:, 1], [shape[0], shape[1]], xy_scaling_factor=xy_scaling_factor)
                np_mask[z, filled_poly] = mask_foreground  # sitk is xyz, numpy is zyx
                # mask = sitk.GetImageFromArray(np_mask)
            except IndexError:
                # if this is triggered the contour is out of bounds
                raise ContourOutOfBoundsException()
            except RuntimeError as e:
                # this error is sometimes thrown by SimpleITK if the index goes out of bounds
                if 'index out of bounds' in str(e):
                    raise ContourOutOfBoundsException()
                raise e  # something serious is going on

        # Get image form final mask
        final_mask = sitk.GetImageFromArray(np_mask)

        # Adjusted spacing
        spacing = scale_information_tuple(information_tuple=dicom_image.GetSpacing(), xy_scaling_factor=xy_scaling_factor, up=False, out_type=float)
        final_mask.SetSpacing(spacing)

        # Original direction and origion
        final_mask.SetDirection(dicom_image.GetDirection())
        final_mask.SetOrigin(dicom_image.GetOrigin())

        return final_mask
