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
import os


def download_subject(project, subject, datafolder, session, verbose=False):
    # Download all data and keep track of resources
    # download_counter = 0
    # resource_labels = list()
    for e in subject.experiments:
        # resmap = {}
        experiment = subject.experiments[e]

        # FIXME: Need a way to smartly check whether we have a matching RT struct and image
        # Current solution: We only download the CT sessions, no PET / MRI / Other scans
        # Specific for STW Strategy BMIA XNAT projects

        if experiment.session_type is None:  # some files in project don't have _CT postfix
            print(f"\tSkipping patient {subject.label}, experiment {experiment.label}: type is not CT but {experiment.session_type}.")
            continue

        if '_CT' not in experiment.session_type:
            print(f"\tSkipping patient {subject.label}, experiment {experiment.label}: type is not CT but {experiment.session_type}.")
            continue

        for s in experiment.scans:
            scan = experiment.scans[s]
            print(("\tDownloading patient {}, experiment {}, scan {}.").format(subject.label, experiment.label, scan.id))
            outdir = datafolder + '/{}'.format(subject.label)

            if not os.path.exists(outdir):
                os.makedirs(outdir)

            scan.download_dir(outdir)

            # for res in scan.resources:
            #     resource_label = scan.resources[res].label
            #     # Create output directory
            #     outdir = datafolder + '/{}'.format(subject.label)
            #     if not os.path.exists(outdir):
            #         os.makedirs(outdir)
            #
            #     resmap[resource_label] = scan
            #     print(f'resource is {resource_label}')
            #     scan.resources[res].download_dir(outdir)
            #     resource_labels.append(resource_label)
            #     download_counter += 1

    return True


def download_project(project_name, xnat_url, datafolder, nsubjects=10,
                     verbose=True):

    # Connect to XNAT and retreive project
    session = xnat.connect(xnat_url)
    project = session.projects[project_name]

    # Create the data folder if it does not exist yet
    datafolder = os.path.join(datafolder, project_name)
    if not os.path.exists(datafolder):
        os.makedirs(datafolder)

    subjects_len = len(project.subjects)
    if nsubjects == 'all':
        nsubjects = subjects_len
    else:
        nsubjects = min(nsubjects, subjects_len)

    subjects_counter = 1
    downloaded_subjects_counter = 0
    for s in range(0, subjects_len):
        s = project.subjects[s]
        print(f'Working on subject {subjects_counter}/{subjects_len}')
        subjects_counter += 1

        success = download_subject(project_name, s, datafolder, session, verbose)
        if success:
            downloaded_subjects_counter += 1

        # Stop downloading if we have reached the required number of subjects
        if downloaded_subjects_counter == nsubjects:
            break

    # Disconnect the session
    session.disconnect()
    if downloaded_subjects_counter < nsubjects:
        raise ValueError(f'Number of subjects downloaded {downloaded_subjects_counter} is smaller than the number required {nsubjects}.')

    print('Done downloading!')


def download_stwstrategyhn1(datafolder=None, nsubjects=10):
    if datafolder is None:
        # Download data to path in which this script is located + Data
        cwd = os.getcwd()
        datafolder = os.path.join(cwd, 'Data')
        if not os.path.exists(datafolder):
            os.makedirs(datafolder)

    xnat_url = 'https://xnat.bmia.nl'
    project_name = 'stwstrategyhn1'
    download_project(project_name, xnat_url, datafolder, nsubjects=nsubjects, verbose=True)
