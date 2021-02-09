import nibabel as nib
from filehash import FileHash
import numpy as np


def diffnii(left, right):
    hasher = FileHash('sha256')

    result = {}

    img1_hash = hasher.hash_file(left)
    img2_hash = hasher.hash_file(right)

    result['hash'] = {'left': img1_hash, 'right': img2_hash, 'equal': img1_hash == img2_hash}

    if result['hash']['equal']:
        result['similarity'] = 1.0
        return result

    img1 = nib.load(left)
    img1_data = img1.get_fdata()

    img2 = nib.load(right)
    img2_data = img2.get_fdata()

    totalvoxels1 = np.prod(img1.shape)
    totalvoxels2 = np.prod(img2.shape)

    result['total_voxels'] = {'left': totalvoxels1, 'right': totalvoxels2, 'equal': totalvoxels1 == totalvoxels2}
    result['shape'] = {'left': list(img1_data.shape), 'right': list(img2_data.shape), 'equal': img1_data.shape == img2_data.shape}

    if not result['shape']['equal']:
        result['similarity'] = min((totalvoxels1, totalvoxels2)) / max((totalvoxels1, totalvoxels2))
        return result

    result['voxel_val_sum'] = {'left': img1_data.sum(), 'right': img2_data.sum(), 'equal': img1_data.sum() - img2_data.sum() == 0}
    result['voxel_val_mean_diff'] = {'mean_diff': (img1_data - img2_data).mean(), 'equal': (img1_data - img2_data).mean() == 0}

    if not result['voxel_val_mean_diff']['equal']:
        m = abs(result['voxel_val_mean_diff']['mean_diff'])
        ma = (img1_data - img2_data).max()
        result['similarity'] = (ma - m) / ma
        return result

    result['similarity'] = 1.0
    return result
