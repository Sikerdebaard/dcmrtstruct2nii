import SimpleITK as sitk
import numpy as np
import math


def crop_mask_to_roi(mask_as_img: sitk.Image, xy_scaling_factor):
    # find indexes in all axis
    mask_as_array = sitk.GetArrayFromImage(mask_as_img)
    zs, ys, xs = np.where(mask_as_array != 0)

    # extract cube with extreme limits of where are the values != 0
    bounding_box = [[int(min(xs)), int(max(xs) + 1)], [int(min(ys)), int(max(ys) + 1)], [int(min(zs)), int(max(zs) + 1)]]
    meta = {
        "original_direction": list([int(i) for i in mask_as_img.GetDirection()]),
        "original_size": list([int(i) for i in mask_as_img.GetSize()]),
        "original_origin": list([float(i) for i in mask_as_img.GetOrigin()]),
        "original_spacing": list([float(i) for i in mask_as_img.GetSpacing()]),
        "bounding_box": bounding_box,
        "bounding_box_ct_grid": list([[math.floor(min_max[0] / xy_scaling_factor),
                                       math.ceil(min_max[1] / xy_scaling_factor)]
                                      for min_max in bounding_box])
    }

    cropped_img = mask_as_img[min(xs): max(xs) + 1, min(ys): max(ys) + 1, min(zs): max(zs) + 1]
    return cropped_img, meta
