from tests.utils.dataset_bmia import list_subjects_stwstrategyhn1, download_subject
from tests.utils import diffnii
from pathlib import Path
from dcmrtstruct2nii import dcmrtstruct2nii
import shutil


def test_bmia_stwstrategyhn1(tmpdir):
    dataset = Path(tmpdir / 'stwstrategyhn1')
    dcmrtstruct2niidir = Path(tmpdir / 'dcmrtstruct2nii')

    dcmrtstruct2niidir.mkdir(exist_ok=True)

    counter = 0
    subjects = list_subjects_stwstrategyhn1()
    numsubjects = len(subjects)

    for subject in subjects:
        counter += 1
        print(f'Comparing {subject.label} {counter}/{numsubjects}')

        subject_dir = Path(dataset / subject.label)
        download_subject(subject, subject_dir)

        rtstructs = list(subject_dir.glob('*/scans/*/resources/secondary/files/*'))
        if len(rtstructs) > 1 or len(rtstructs) <= 0:
            assert False, f'> 1 RTSTRUCT or <= 0 RTSTRUCT found for subject {subject.label}, something changed in the dataset?'
        rtstruct = rtstructs[0]

        dicoms = list(subject_dir.glob('*/scans/*/resources/DICOM/files'))
        if len(dicoms) > 1 or len(dicoms) <= 0:
            assert False, f'> 1 DICOM or <= 0 DICOM found for subject {subject.label}, something changed in the dataset?'

        dicom = dicoms[0]

        subjoutdir = Path(dcmrtstruct2niidir / subject.label)
        subjoutdir.mkdir(exist_ok=True)

        dcmrtstruct2nii(rtstruct, dicom, subjoutdir)

        niicounter = 0
        for nii in subjoutdir.glob('*.nii.gz'):
            niicounter += 1
            niftis = list(subject_dir.glob(f'**/{nii.name}'))

            if len(niftis) > 1 or len(niftis) <= 0:
                assert False, f'> 1 niftis or <= 0 niftis {nii.name} found for subject {subject.label}, something changed in the dataset?'

            nii_stwstrategyhn1 = niftis[0]

            diff = diffnii(nii, nii_stwstrategyhn1)

            if not (diff['similarity'] > .95 and diff['similarity'] < 1.05):
                assert False, f'niftis not equal {diff["similarity"]}, {nii}:{nii_stwstrategyhn1} data: {diff}'

        print(f"Compared {niicounter} NiFTI's for subject {subject.label}")

        # cleanup, GitHub runners only have ~14 GB of space
        shutil.rmtree(subjoutdir)
        shutil.rmtree(subject_dir)

    assert True
