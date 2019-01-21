from convert.adapters.convert.rtstructcontour2mask import DcmPatientCoords2Mask
from convert.adapters.input.contours.rtstructinputadapter import RtStructInputAdapter
from convert.adapters.input.image.dcminputadapter import DcmInputAdapter
from convert.adapters.input.metadata.dcmmetadatainputadapter import DcmMetadataInputAdapter

import SimpleITK as sitk

rtreader = RtStructInputAdapter()
rtstruct = rtreader.ingest('/scratch/tphil/Data/stwstrategyhn1/HN1106/HN1106_20171105_CT/scans/1_3_6_1_4_1_40744_29_322475528122510065681186952077195635023-unknown/resources/secondary/files/1.3.6.1.4.1.40744.29.98620429560543368888343318852469724196-no-value-for-SeriesNumber-no-value-for-InstanceNumber-hwpu4y.dcm')

dicom_image = DcmInputAdapter().ingest('/scratch/tphil/Data/stwstrategyhn1/HN1106/HN1106_20171105_CT/scans/1_3_6_1_4_1_40744_29_292945547339965086675980474368776076272-unknown/resources/DICOM/files/')
dicom_metadata = DcmMetadataInputAdapter().ingest('/scratch/tphil/Data/stwstrategyhn1/HN1106/HN1106_20171105_CT/scans/1_3_6_1_4_1_40744_29_292945547339965086675980474368776076272-unknown/resources/DICOM/files/')

coordinates = rtstruct[0]['sequence'][0]['points']

mask = DcmPatientCoords2Mask().convert(coordinates, dicom_image)