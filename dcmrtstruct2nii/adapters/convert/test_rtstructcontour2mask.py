import random
import unittest
import SimpleITK as sitk
from adapters.convert.rtstructcontour2mask import _get_transform_matrix, _transform_physical_point_to_continuous_index
import numpy as np
def rand():
    return random.randint(1,100)/11
class TestRTStructcontour2mask(unittest.TestCase):
    def test__set_transform_variables(self):
        img = sitk.Image(300, 200, 100, sitk.sitkUInt8)
        img.SetSpacing((rand(), rand(), rand()))
        img.SetOrigin((rand(), rand(), rand()))
        m_transform, origins = _get_transform_matrix(img.GetSpacing(), img.GetDirection(), img.GetOrigin())
        self.assertIsNotNone(m_transform)
        self.assertIsNotNone(origins)

    def test__transform_physical_point_to_continuous_index(self):
        img = sitk.Image(300, 200, 100, sitk.sitkUInt8)
        img.SetSpacing((rand(), rand(), rand()))
        img.SetOrigin((rand(), rand(), rand()))
        m_transform, origins = _get_transform_matrix(img.GetSpacing(), img.GetDirection(), img.GetOrigin())

        ## Known to work:
        coords = [(random.randint(0,299),
                   random.randint(0,199),
                   random.randint(0,99)) for n in range(100)]
        known_idxs = np.empty((100,3))
        for i in range(len(coords)):
            idx = img.TransformPhysicalPointToContinuousIndex(coords[i])
            known_idxs[i,0] = idx[0]
            known_idxs[i, 1] = idx[1]
            known_idxs[i, 2] = idx[2]
        coords = np.array(coords)
        new_idxs, _ = _transform_physical_point_to_continuous_index(coords=coords, m_PhysicalPointToIndex=m_transform, origins=origins)
        self.assertTrue(np.array_equal(known_idxs, new_idxs))


if __name__ == '__main__':
    unittest.main()
