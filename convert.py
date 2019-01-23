from dcmrtstruct2nii.adapters.convert.rtstructcontour2mask import DcmPatientCoords2Mask
from dcmrtstruct2nii.adapters.input.contours.rtstructinputadapter import RtStructInputAdapter
from dcmrtstruct2nii.adapters.input.image.dcminputadapter import DcmInputAdapter

import SimpleITK as sitk

rtreader = RtStructInputAdapter()
rtstructs = rtreader.ingest('/scratch/tphil/Data/stwstrategyhn1/HN1006/HN1006_20171106_CT/scans/1_3_6_1_4_1_40744_29_94197177514027086365367309890233877794-unknown/resources/secondary/files/1.3.6.1.4.1.40744.29.35479789258972220445348711225294050430-no-value-for-SeriesNumber-no-value-for-InstanceNumber-hwpu4y.dcm')

dicom_image = DcmInputAdapter().ingest('/scratch/tphil/Data/stwstrategyhn1/HN1006/HN1006_20171106_CT/scans/1_3_6_1_4_1_40744_29_54712191493031700552055858867725815574-unknown/resources/DICOM/files/')

for rtstruct in rtstructs:
    print('Working on mask {}'.format(rtstruct['name']))
    mask = DcmPatientCoords2Mask().convert(rtstruct['sequence'], dicom_image)
    #for i in range(0, 134):
    #    sitk.WriteImage(sitk.GetImageFromArray(sitk.GetArrayFromImage(mask)[:,:,i]), '/tmp/testout/{}.png'.format(i))

    mask.CopyInformation(dicom_image)
    sitk.WriteImage(mask, '/tmp/testout/mask_{}.nii'.format(rtstruct['name']))

print('Working on dcm2nii')

sitk.WriteImage(dicom_image, '/tmp/testout/image.nii')
