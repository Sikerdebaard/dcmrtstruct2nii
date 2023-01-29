import random
import unittest
import SimpleITK as sitk
from dcmrtstruct2nii.adapters.convert.rtstructcontour2mask import _get_m_PhysicalPointToIndex, _transform_physical_point_to_continuous_index
import numpy as np

class TestRTStructcontour2mask(unittest.TestCase):
    def setUp(self) -> None:
        self.img = sitk.Image(300, 200, 100, sitk.sitkUInt8)
        self.img.SetSpacing((1.11112, 1.11112, 3.0))
        self.img.SetOrigin((231.12, 78.09, 10.44))

    def test__get_m_PhysicalPointToIndex(self):
        # Checks that something is returned.
        m_transform = _get_m_PhysicalPointToIndex(self.img.GetSpacing(), self.img.GetDirection())
        self.assertIsNotNone(m_transform)
        self.assertIsInstance(m_transform, np.ndarray)
        self.assertEqual((3, 3), m_transform.shape)

    def test__transform_physical_point_to_continuous_index(self):
        # Known method to transform coordinate to cont. idx.:
        # Generate random coordinates
        coords = [[round(random.randint(0,299)/1.1, 1),
                  round(random.randint(0,199)/1.1, 1),
                  round(random.randint(0, 99) / 1.1, 1)] for n in range(100)]

        # Known transform method
        known_idxs = np.empty((100,3))
        for i in range(len(coords)):
            idx = self.img.TransformPhysicalPointToContinuousIndex(coords[i])
            known_idxs[i ,0] = idx[0]
            known_idxs[i, 1] = idx[1]
            known_idxs[i, 2] = idx[2]

        # New method here.
        coords = np.array(coords)
        m_transform = _get_m_PhysicalPointToIndex(self.img.GetSpacing(), self.img.GetDirection())
        origin = np.array(self.img.GetOrigin())
        new_idxs = _transform_physical_point_to_continuous_index(coordinates=coords, m_PhysicalPointToIndex=m_transform, origin=origin)

        # Did the two methods reach the same result?
        self.assertTrue(np.array_equal(known_idxs, new_idxs))

if __name__ == '__main__':
    unittest.main()
