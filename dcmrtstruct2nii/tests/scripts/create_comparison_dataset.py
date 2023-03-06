import xnat
import psutil
import shutil

from joblib import Parallel, delayed
from tqdm.auto import tqdm
from pathlib import Path
from dcmrtstruct2nii import dcmrtstruct2nii


outdir = Path('/tmp/dcmrtstruct2nii-testsets')
outdir.mkdir(exist_ok=True)


class ProgressParallel(Parallel):
    def __init__(self, use_tqdm=True, total=None, *args, **kwargs):
        self._use_tqdm = use_tqdm
        self._total = total
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        with tqdm(disable=not self._use_tqdm, total=self._total) as self._pbar:
            return Parallel.__call__(self, *args, **kwargs)

    def print_progress(self):
        if self._total is None:
            self._pbar.total = self.n_dispatched_tasks
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()


def download_bmia_stwstrategyhn1(outdir):
    xnat_url = 'https://xnat.bmia.nl'
    xnat_project = 'stwstrategyhn1'
    session = xnat.connect(xnat_url)

    project = session.projects[xnat_project]
    project.download_dir(str(outdir), verbose=True)


def convert_bmia_stwstrategyhn1(indir, outdir, n_jobs=psutil.cpu_count()):
    subjects = indir.glob('*/HN*')

    jobs = []
    for subjectdir in subjects:
        rtstructs = list(subjectdir.glob('*/scans/*/resources/secondary/files/*'))
        dicoms = list(subjectdir.glob('*_CT/scans/*/resources/DICOM/files'))

        assert len(rtstructs) == 1
        assert len(dicoms) == 1

        rtstruct = rtstructs[0]
        dicom = dicoms[0]

        subjoutdir = outdir / subjectdir.name
        subjoutdir.mkdir(exist_ok=True)

        jobs.append(delayed(dcmrtstruct2nii)(rtstruct, dicom, subjoutdir))

    ProgressParallel(n_jobs=n_jobs)(jobs)


def package_bmia_stwstrategyhn1(indir, outdir):
    for niifile in tqdm(list(indir.glob('*/*.nii.gz'))):
        if niifile.name.lower() == 'image.nii.gz':
            continue

        subject = niifile.parent.name
        subject_dir = outdir / subject
        subject_dir.mkdir(exist_ok=True)

        shutil.copy(niifile, subject_dir / niifile.name)


bmia_stwstrategyhn1_dir = outdir / 'stwstrategyhn1'
bmia_stwstrategyhn1_dir.mkdir(exist_ok=True)
download_dir = bmia_stwstrategyhn1_dir / 'download'
download_dir.mkdir(exist_ok=True)
convert_dir = bmia_stwstrategyhn1_dir / 'convert'
convert_dir.mkdir(exist_ok=True)
package_dir = bmia_stwstrategyhn1_dir / 'package'
package_dir.mkdir(exist_ok=True)

download_bmia_stwstrategyhn1(download_dir)
convert_bmia_stwstrategyhn1(download_dir, convert_dir)
package_bmia_stwstrategyhn1(convert_dir, package_dir)
