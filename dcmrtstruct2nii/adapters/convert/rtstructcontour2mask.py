import logging

import SimpleITK as sitk
import numpy as np
from skimage import draw

from dcmrtstruct2nii.exceptions import ContourOutOfBoundsException


def _get_transform_matrix(spacing, direction):
    """
    this returns the basics needed to run _transform_physical_point_to_continuous_index
    """
    s = np.array(spacing)
    d = np.array(direction).reshape(3, 3)
    m_IndexToPhysicalPoint = np.multiply(d, s)
    m_PhysicalPointToIndex = np.linalg.inv(m_IndexToPhysicalPoint)

    return m_PhysicalPointToIndex


def xor_update_np_mask(np_mask, filled_poly, z, mask_foreground, mask_background):
    overlay = np.logical_xor(np_mask[z, :, :], filled_poly)
    np_mask[z, :, :] = np.where(overlay, mask_foreground, mask_background)
    return np_mask

def _transform_physical_point_to_continuous_index(coords, m_PhysicalPointToIndex, origin):
    """
    This method does the same as SimpleITK's TransformPhysicalPointToContinuousIndex, but in a vectorized fashion.
    The implementation is based on ITK's code found in https://itk.org/Doxygen/html/itkImageBase_8h_source.html#l00497 and
    https://discourse.itk.org/t/solved-transformindextophysicalpoint-manually/1031/2
    """

    if m_PhysicalPointToIndex is None:
        raise Exception("Run set transform variables first!")

    pts = np.empty_like(coords)
    pts[:, 0] = coords[:, 0]  # Index of contour
    pts[:, 1] = coords[:, 1] - origin[0]  # x
    pts[:, 2] = coords[:, 2] - origin[1]  # y
    pts[:, 3] = coords[:, 3] - origin[2]  # z

    pts[:, 1:] = pts[:, 1:].copy() @ m_PhysicalPointToIndex

    return pts


def get_cropped_origin(stacked_coords):
    float_min = np.min(stacked_coords[:, 1:], axis=0)
    return float_min


def stack_coords(rtstruct_contours):
    coords = None
    for i, contour in enumerate(rtstruct_contours):
        if contour['type'].upper() not in ['CLOSED_PLANAR', 'INTERPOLATED_PLANAR']:
            if 'name' in contour:
                logging.info(f'Skipping contour {contour["name"]}, unsupported type: {contour["type"]}')
            else:
                logging.info(f'Skipping unnamed contour, unsupported type: {contour["type"]}')
            continue

        # Stack coordinate components to one array
        temp_coords = contour['points']
        stack = np.column_stack((
            [i for u in range(len(temp_coords["x"]))],
            temp_coords["x"],
            temp_coords["y"],
            temp_coords["z"])
        )
        # Stack column 0 is index of contour, then x, y, z.
        if coords is None:
            coords = stack
        else:
            coords = np.concatenate([coords, stack])

    return coords


def get_shape(idx_pts):
    maxs = np.ceil(np.max(idx_pts[:, 1:], axis=0)).astype(int) + 1

    return maxs

class DcmPatientCoords2Mask():
    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground):
        self.m_PhysicalPointToIndex = _get_transform_matrix(spacing=dicom_image.GetSpacing(),
                                                            direction=dicom_image.GetDirection())

        # Stack coords with columns being (contour-id, x, y, z)
        stacked_coords = stack_coords(rtstruct_contours=rtstruct_contours)

        # Origin set to minimum of x, y and z
        self.origin = get_cropped_origin(stacked_coords)

        # Index of coords
        idx_pts = _transform_physical_point_to_continuous_index(stacked_coords,
                                                                m_PhysicalPointToIndex=self.m_PhysicalPointToIndex,
                                                                origin=self.origin)
        # Get Shape for rastering
        self.shape = get_shape(idx_pts)

        np_mask = np.zeros(list(reversed(self.shape)), dtype=np.uint8)
        for idx in np.unique(idx_pts[:, 0]):
            pts = idx_pts[idx_pts[:, 0] == idx][:, 1:]
            z = int(pts[0, 2])

            try:
                filled_poly = draw.polygon2mask((self.shape[1], self.shape[0]), pts[:, 1::-1])
                np_mask = xor_update_np_mask(np_mask=np_mask, filled_poly=filled_poly, z=z, mask_foreground=mask_foreground, mask_background=mask_background)
            except IndexError:
                # if this is triggered the contour is out of bounds
                raise ContourOutOfBoundsException()
            except RuntimeError as e:
                # this error is sometimes thrown by SimpleITK if the index goes out of bounds
                if 'index out of bounds' in str(e):
                    raise ContourOutOfBoundsException()
                raise e  # something serious is going on

        # np_mask to image
        mask = sitk.GetImageFromArray(np_mask.astype(np.uint8))  # Had trouble with the type. Use np.uint8!
        mask = sitk.Resample(mask,
                             dicom_image.GetSize(),
                             sitk.Transform(),
                             sitk.sitkNearestNeighbor,
                             dicom_image.GetOrigin(),
                             dicom_image.GetSpacing(),
                             dicom_image.GetDirection())
        return mask
