import importlib
import logging

import SimpleITK as sitk
import numpy as np
from skimage import draw

try:
    import numba
    from numba import njit
except:
    print("Numba not installed")

numba_exists = importlib.util.find_spec("numba") is not None

def maybe_use_numba():
    def decorator(func):
        if not importlib.util.find_spec("numba"):
            return func
        return func
    return decorator

def _poly2mask(coords_yx, shape_x, shape_y):
    mask = draw.polygon2mask((shape_y, shape_x), coords_yx)
    return mask


@maybe_use_numba()
def _get_m_PhysicalPointToIndex(spacing, direction):
    """
    This generats the transform matrix used to turn coordinates into indices.
    See explanation under method "_transform_physical_point_to_continuous_index"
    """
    s = np.array(spacing) # XYZ
    d = np.array(direction).reshape(3, 3)

    # The variable names are the same as in ITK. Makes it easier to look for explanation
    m_IndexToPhysicalPoint = np.multiply(d, s)
    m_PhysicalPointToIndex = np.linalg.inv(m_IndexToPhysicalPoint)

    return m_PhysicalPointToIndex

@maybe_use_numba()
def update_array(np_mask, filled_poly, z, mask_foreground, mask_background):
    # xor logic to allow holes in contours
    new_mask = np.logical_xor(np_mask[z, :, :], filled_poly)

    # update array on the given z slice
    np_mask[z, :, :] = np.where(new_mask, mask_foreground, mask_background)


@maybe_use_numba()
def _transform_physical_point_to_continuous_index(coordinates, m_PhysicalPointToIndex, origin):
    """
    This method does the same as SimpleITK's TransformPhysicalPointToContinuousIndex, but in a vectorized fashion.
    The implementation is based on ITK's code found in https://itk.org/Doxygen/html/itkImageBase_8h_source.html#l00497 and
    https://discourse.itk.org/t/solved-transformindextophysicalpoint-manually/1031/2
    """
    if m_PhysicalPointToIndex is None:
        raise Exception("Run set transform variables first!")

    # See links above for explanation of this.
    # The full transform is coord_t = (coord - origin) * inverse_matrix_of(direction * spacing)
    pts_intermediary = np.empty_like(coordinates, dtype=coordinates.dtype)
    pts_intermediary[:, 0] = coordinates[:, 0] - origin[0]
    pts_intermediary[:, 1] = coordinates[:, 1] - origin[1]
    pts_intermediary[:, 2] = coordinates[:, 2] - origin[2]
    idxs = pts_intermediary @ m_PhysicalPointToIndex
    return idxs

class DcmPatientCoords2Mask:
    def __init__(self):
        self.m_PhysicalPointToIndex = None
        self.origin = None


    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground):
        shape = dicom_image.GetSize()
        self.origin = np.array(dicom_image.GetOrigin())
        self.m_PhysicalPointToIndex = _get_m_PhysicalPointToIndex(spacing=dicom_image.GetSpacing(),
                                                                  direction=dicom_image.GetDirection())
        # Init np_mask with z, y, x shape
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
            coords_t = _transform_physical_point_to_continuous_index(coordinates=coords,
                                                                m_PhysicalPointToIndex=self.m_PhysicalPointToIndex,
                                                                origin=self.origin)


            try:
                # Generate the mask from Y X transformed coordinates
                filled_poly = _poly2mask(coords_yx=coords_t[:, 1::-1], shape_x=shape[0], shape_y=shape[1])

                # Gets first Z of this contour
                z = int(round(coords_t[0, 2]))

                # Update the array. This way to take advantage of numba
                update_array(np_mask=np_mask, filled_poly=filled_poly, z=z, mask_foreground=mask_foreground, mask_background=mask_background)
            except Exception as e:
                print(e)


        # Get the generated mask as sitk.Image and copy information from dicom image
        mask = sitk.GetImageFromArray(np_mask)
        mask.CopyInformation(dicom_image)

        return mask
