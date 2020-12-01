#!/usr/bin/env python

from __future__ import absolute_import

import cagedu.cagedu as cdu
from cagedu.filestat import FileStat
import sys,os
import logging
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description='Disk usage analysis tool.')
    parser.add_argument('path', metavar='path', type=str, default='.',
            help='Path where to start disk usage analysis')
    parser.add_argument("-log", "--log", choices=["DEBUG", "INFO", "ERROR"],
            type=str, default="INFO", metavar='log', help="Log level")

    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, str(args.log)),
            format='cdu: %(name)s %(message)s')

    rootDir = args.path
    try:
        rootStat = os.stat(rootDir)
    except:
        logging.error("Stat on %d failed exiting" % (rootDir))
        os.exit(1)

    rootNode = FileStat(rootDir,rootStat)

    logging.info("Building the tree information");
    start = time.time()
    cdu.buildTree(rootNode, maxDepth=3)
    end = time.time()
    logging.info("\t took:%d seconds, processed:%d files" % (end-start, rootNode.totalFiles))

    logging.info("Processing data structure");
    cdu.calculateStats(rootNode)

    logging.info("Printing the tree");
    cdu.printTree(rootNode)
