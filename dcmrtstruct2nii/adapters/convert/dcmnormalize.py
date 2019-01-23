import numpy as np
import SimpleITK as sitk

class DcmNormalize():
    def convert(self, dicom_image):
        dicom_image_as_array = sitk.GetArrayFromImage(dicom_image.astype(np.float32))
        dicom_image_as_array -= np.min(dicom_image_as_array)
        dicom_image_as_array = dicom_image_as_array.astype(np.float32)
        dicom_image_as_array /= np.max(dicom_image_as_array)
        dicom_image_as_array *= 255

        image = sitk.GetImageFromArray(dicom_image_as_array.astype(np.float32))

        return image
