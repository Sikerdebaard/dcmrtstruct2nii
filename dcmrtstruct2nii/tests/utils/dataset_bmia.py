#!/usr/bin/env python

# Copyright 2016-2020 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xnat
from pathlib import Path


_xnat_sessions = {}


def _cached_xnat(xnat_url, project_name):
    if (xnat_url, project_name, ) in _xnat_sessions:
        return _xnat_sessions[(xnat_url, project_name, )]
    session = xnat.connect(xnat_url)
    project = session.projects[project_name]
    _xnat_sessions[(xnat_url, project_name, )] = project

    return project


def _subjects(project_name, xnat_url):
    project = _cached_xnat(xnat_url, project_name)

    return project.subjects.values()


def list_subjects_stwstrategyhn1():
    return list_subjects('stwstrategyhn1')


def list_subjects(project_name):
    xnat_url = 'https://xnat.bmia.nl'
    return _subjects(project_name, xnat_url)


def download_subject(subject, datafolder):
    for e in subject.experiments:
        experiment = subject.experiments[e]

        if experiment.session_type is None:  # some files in project don't have _CT postfix
            print(f"Skipping patient {subject.label}, experiment {experiment.label}: type is not CT but {experiment.session_type}.")
            continue

        if '_CT' not in experiment.session_type:
            print(f"Skipping patient {subject.label}, experiment {experiment.label}: type is not CT but {experiment.session_type}.")
            continue

        for s in experiment.scans:
            scan = experiment.scans[s]
            print(("Downloading patient {}, experiment {}, scan {}.").format(subject.label, experiment.label, scan.id))
            outdir = Path(datafolder)

            outdir.mkdir(parents=True, exist_ok=True)

            scan.download_dir(str(outdir), verbose=False)

    return True

