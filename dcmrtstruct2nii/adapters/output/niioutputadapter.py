from dcmrtstruct2nii.adapters.output.abstractoutputadapter import AbstractOutputAdapter

import SimpleITK as sitk

class NiiOutputAdapter(AbstractOutputAdapter):
    def write(self, image, output_path, gzip):
        if gzip:
            sitk.WriteImage(image, output_path + '.nii.gz')
        else:
            sitk.WriteImage(image, output_path + '.nii')
