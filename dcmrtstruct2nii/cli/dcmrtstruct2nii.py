#!/usr/bin/env python

from cleo import Application

from dcmrtstruct2nii.cli import ListStructs, Convert

import logging

application = Application()

application.add(ListStructs())
application.add(Convert())

def run():
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    application.run()

if __name__ == '__main__':
    run()
