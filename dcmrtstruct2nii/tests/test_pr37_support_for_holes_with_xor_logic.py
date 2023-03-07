from dcmrtstruct2nii.tests.utils.dataset_bmia import download_subject_by_name
from dcmrtstruct2nii.tests.utils.compression import decompress_gzip
from dcmrtstruct2nii.tests.utils import compare_mask
from dcmrtstruct2nii import dcmrtstruct2nii

from pathlib import Path


def test_compare_iou(tmpdir):
    workdir = Path(tmpdir) / 'test_compare_iou'
    dicomdir = workdir / 'dicom'
    outdir = workdir / 'output'
    groundtruthdir = Path('testdata/pr37/')

    workdir.mkdir(exist_ok=True)
    dicomdir.mkdir(exist_ok=True)
    outdir.mkdir(exist_ok=True)

    project = 'stwstrategyhn1'
    subject = 'HN1004'

    download_subject_by_name(subject, dicomdir, project)

    # decompress gzipped rtstruct used for this test
    rtstructname = 'rtss_1.2.826.0.1.3680043.8.274.1.1.225842493.89446.1674812092.977037.dcm'
    rtstructfile = dicomdir / rtstructname
    decompress_gzip(groundtruthdir / 'rtss' / f'{rtstructname}.gz', rtstructfile)

    dicompath = list(dicomdir.glob('*/scans/*/resources/DICOM/files'))
    assert len(dicompath) == 1
    dicompath = dicompath[0]

    dcmrtstruct2nii(rtstructfile, dicompath, outdir)

    groundtruthniis = {f.name: f for f in groundtruthdir.glob('new_method/*.nii.gz')}
    oldmethodniis = {f.name: f for f in groundtruthdir.glob('old_method/*.nii.gz')}
    for nii in outdir.glob('*.nii.gz'):
        if nii.name == 'image.nii.gz':
            # skip main image
            continue

        diff = compare_mask(nii, groundtruthniis[nii.name])
        assert diff['iou'] > .9

        diff = compare_mask(nii, oldmethodniis[nii.name])
        print(f'{nii.name}: {diff}')

        if 'no-hole' in nii.name.lower():
            assert diff['iou'] > .9
        elif 'onehole' in nii.name.lower():
            assert diff['iou'] > .9
        else:
            assert diff['iou'] < .9
