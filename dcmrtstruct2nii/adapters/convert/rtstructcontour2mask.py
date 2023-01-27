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

def conditional_decorator(dec, condition):
    def decorator(func):
        if not condition:
            # Return the function unchanged, not decorated.
            return func
        return dec(func)
    return decorator

def _poly2mask(coords_x, coords_y, shape_x, shape_y):
    mask = draw.polygon2mask((shape_y, shape_x), np.column_stack((coords_y, coords_x)))
    return mask


@conditional_decorator(njit, numba_exists)
def _set_transform_variables(spacing, direction, origin):
    """
    this returns the basics needed to run _transform_physical_point_to_continuous_index
    """

    s = np.array(spacing)
    d = np.array(direction).reshape(3, 3)
    m_IndexToPhysicalPoint = np.multiply(d, s)
    m_PhysicalPointToIndex = np.linalg.inv(m_IndexToPhysicalPoint)
    origins = np.empty((1000, 3))
    for i in range(1000):
        origins[i] = origin

    return m_PhysicalPointToIndex, origins

@conditional_decorator(njit, numba_exists)
def update_array(np_mask, filled_poly, z, mask_foreground, mask_background):
    new_mask = np.logical_xor(np_mask[z, :, :], filled_poly)
    np_mask[z, :, :] = np.where(new_mask, mask_foreground, mask_background)


#@njit
def _transform_physical_point_to_continuous_index(coords, m_PhysicalPointToIndex, origins):
    """
    This method does the same as SimpleITK's TransformPhysicalPointToContinuousIndex, but in a vectorized fashion.
    The implementation is based on ITK's code found in https://itk.org/Doxygen/html/itkImageBase_8h_source.html#l00497 and
    https://discourse.itk.org/t/solved-transformindextophysicalpoint-manually/1031/2
    """
    if m_PhysicalPointToIndex is None:
        raise Exception("Run set transform variables first!")

    if coords.shape[0] <= len(origins):
        pts_intermediary = np.subtract(coords, origins[:coords.shape[0]])
        idxs = pts_intermediary @ m_PhysicalPointToIndex
        return idxs, origins
    else:
        new_origins = np.empty((len(origins)*2, 3))
        new_origins[:len(origins)] = origins

        for i in range(len(origins), len(new_origins)):
            new_origins[i] = origins[0]
        return _transform_physical_point_to_continuous_index(coords=coords,
                                                             m_PhysicalPointToIndex=m_PhysicalPointToIndex,
                                                             origins=origins)

class DcmPatientCoords2Mask:
    def __init__(self):
        self.m_PhysicalPointToIndex = None
        self.origins = None

    def _poly2mask(self, coords_x, coords_y, shape):
        mask = draw.polygon2mask(tuple(reversed(shape)), np.column_stack((coords_y, coords_x)))
        return mask

    def convert(self, rtstruct_contours, dicom_image, mask_background, mask_foreground):
        shape = dicom_image.GetSize()
        self.m_PhysicalPointToIndex, self.origins = _set_transform_variables(spacing=dicom_image.GetSpacing(),
                                                                             direction=dicom_image.GetDirection(),
                                                                             origin=dicom_image.GetOrigin())
        # Init np_mask
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
            pts, self.origins = _transform_physical_point_to_continuous_index(coords,
                                                                              m_PhysicalPointToIndex=self.m_PhysicalPointToIndex,
                                                                              origins=self.origins)
            filled_poly = _poly2mask(coords_x=pts[0], coords_y=pts[1], shape_x=shape[0], shape_y=shape[1])
            try:
                z = int(round(pts[0, 2]))
                update_array(np_mask=np_mask, filled_poly=filled_poly, z=z, mask_foreground=mask_foreground, mask_background=mask_background)
            except Exception as e:
                print(e)


        mask = sitk.GetImageFromArray(np_mask)
        mask.CopyInformation(dicom_image)

        return mask
