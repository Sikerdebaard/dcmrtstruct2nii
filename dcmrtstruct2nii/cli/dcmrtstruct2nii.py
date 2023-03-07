#!/usr/bin/env python

from cleo.application import Application

from dcmrtstruct2nii.cli import Convert, ListStructs 

import logging

application = Application()

application.add(Convert())
application.add(ListStructs())


def run():
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    application.run()


if __name__ == '__main__':
    run()
