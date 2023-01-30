import logging

import SimpleITK as sitk
import numpy as np
from numba import njit
from skimage import draw

from dcmrtstruct2nii.exceptions import ContourOutOfBoundsException


def scale_information_tuple(information_tuple: tuple, xy_scaling_factor: int, out_type: type, up: bool = True):
    scale_array = np.array([xy_scaling_factor, xy_scaling_factor, 1])
    if up:
        information_tuple = np.array(information_tuple) * scale_array
    else:
        information_tuple = np.array(information_tuple) / scale_array

    return tuple([out_type(info) for info in information_tuple])


@njit
def _get_transform_matrix(spacing, direction):
    """
    this returns the basics needed to run _transform_physical_point_to_continuous_index
    """
    s = np.array(spacing)
    d = np.array(direction).reshape(3, 3)
    m_IndexToPhysicalPoint = np.multiply(d, s)
    m_PhysicalPointToIndex = np.linalg.inv(m_IndexToPhysicalPoint)

    return m_PhysicalPointToIndex


@njit
def xor_update_np_mask(np_mask, filled_poly, z, mask_foreground, mask_background):
    overlay = np.logical_xor(np_mask[z, :, :], filled_poly)
    np_mask[z, :, :] = overlay


@njit
def scale_xy_coordinates(pts, xy_scaling_factor):
    pts[:, :2] *= xy_scaling_factor


@njit
def _transform_physical_point_to_continuous_index(coords, m_PhysicalPointToIndex, origin):
    """
    This method does the same as SimpleITK's TransformPhysicalPointToContinuousIndex, but in a vectorized fashion.
    The implementation is based on ITK's code found in https://itk.org/Doxygen/html/itkImageBase_8h_source.html#l00497 and
    https://discourse.itk.org/t/solved-transformindextophysicalpoint-manually/1031/2
    """
    if m_PhysicalPointToIndex is None:
        raise Exception("Run set transform variables first!")

    # pts_intermediary = np.subtract(coords, origins[:coords.shape[0]])
    pts_intermediary = np.empty_like(coords)
    pts_intermediary[:, 0] = coords[:, 0] - origin[0]
    pts_intermediary[:, 1] = coords[:, 1] - origin[1]
    pts_intermediary[:, 2] = coords[:, 2] - origin[2]

    idxs = pts_intermediary @ m_PhysicalPointToIndex
    return idxs


class DcmPatientCoords2Mask:
    def __init__(self):
        self.m_PhysicalPointToIndex = None
        self.origin = None

    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground, xy_scaling_factor):
        self.m_PhysicalPointToIndex = _get_transform_matrix(spacing=dicom_image.GetSpacing(),
                                                            direction=dicom_image.GetDirection())
        self.origin = dicom_image.GetOrigin()

        shape = scale_information_tuple(information_tuple=dicom_image.GetSize(), xy_scaling_factor=xy_scaling_factor, up=True, out_type=int)

        np_mask = np.empty(list(reversed(shape)))
        for contour in rtstruct_contours:
            if contour['type'].upper() not in ['CLOSED_PLANAR', 'INTERPOLATED_PLANAR']:
                if 'name' in contour:
                    logging.info(f'Skipping contour {contour["name"]}, unsupported type: {contour["type"]}')
                else:
                    logging.info(f'Skipping unnamed contour, unsupported type: {contour["type"]}')
                return

            # Stack coordinate components to one array
            coordinates = contour['points']
            coords = np.column_stack((coordinates["x"],
                                      coordinates["y"],
                                      coordinates["z"]))

            # transform points to continous index
            pts = _transform_physical_point_to_continuous_index(coords,
                                                                m_PhysicalPointToIndex=self.m_PhysicalPointToIndex,
                                                                origin=self.origin)
            z = int(round(pts[0, 2]))
            try:
                scale_xy_coordinates(pts, xy_scaling_factor=xy_scaling_factor)
                filled_poly = draw.polygon2mask((shape[1], shape[0]), pts[:, 1::-1])
                xor_update_np_mask(np_mask=np_mask, filled_poly=filled_poly, z=z, mask_background=mask_background, mask_foreground=mask_foreground)
            except IndexError:
                # if this is triggered the contour is out of bounds
                raise ContourOutOfBoundsException()
            except RuntimeError as e:
                # this error is sometimes thrown by SimpleITK if the index goes out of bounds
                if 'index out of bounds' in str(e):
                    raise ContourOutOfBoundsException()
                raise e  # something serious is going on
            except Exception as e:
                print(e)

        # To get correct type
        template_mask = sitk.Image(shape, sitk.sitkUInt8)
        template_type = sitk.GetArrayFromImage(template_mask).dtype

        # np_mask to image
        final_mask = sitk.GetImageFromArray(np_mask.astype(template_type))

        final_mask.SetDirection(dicom_image.GetDirection())
        final_mask.SetOrigin(dicom_image.GetOrigin())

        spacing = scale_information_tuple(information_tuple=dicom_image.GetSpacing(), xy_scaling_factor=xy_scaling_factor, up=False, out_type=float)
        final_mask.SetSpacing(spacing)

        return final_mask
