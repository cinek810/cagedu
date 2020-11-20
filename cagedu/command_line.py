#!/usr/bin/env python

from __future__ import absolute_import

import cagedu.cagedu as cdu
from cagedu.filestat import FileStat
import sys,os
import logging

def main():
    logging.basicConfig(level=logging.DEBUG, format='cdu: %(name)s %(message)s')

    rootDir = sys.argv[1]
    try:
        rootStat = os.stat(rootDir)
    except:
        logging.error("Stat on %d failed exiting" % (rootDir))
        os.exit(1)

    rootNode = FileStat(rootDir,rootStat)

#    logging.info("Building the tree information");
    cdu.buildTree(rootNode, maxDepth=3)

#    logging.info("Processing data structure");
    cdu.calculateStats(rootNode)

#    logging.info("Printing the tree");
    cdu.printTree(rootNode)
