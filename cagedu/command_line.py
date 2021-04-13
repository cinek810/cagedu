#!/usr/bin/env python

from __future__ import absolute_import

import cagedu.cagedu as cdu
from cagedu.filestat import FileStat
import sys,os
import logging
import argparse
import time
import gzip, pickle

from anytree.exporter import DictExporter
from anytree.importer import DictImporter

parser = argparse.ArgumentParser(description='Disk usage analysis tool.')
def parse_options():
    parser.add_argument('-path', "--path", metavar='path', type=str, default='.',
            help='Path where to start disk usage analysis')
    parser.add_argument("-log", "--log", choices=["DEBUG", "INFO", "ERROR"],
            type=str, default="INFO", metavar='log', help="Log level")

    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, str(args.log)),
                format='cdu: %(name)s %(message)s')

    return args

def load_tree(path):
    importer = DictImporter()
    with gzip.open(path, 'rb') as f:
        dataRead = pickle.load(f);
        logging.debug("dataRead="+str(dataRead))
        rootNode = importer.import_(dataRead)

    return rootNode

def load_and_process(pathToLoad):
        start = time.time()
        logging.info("Loading tree...")
        rootNode = load_tree(pathToLoad)
        end = time.time()
        logging.info("\t took:%d seconds, processed:%d files" % (end - start, rootNode.totalFiles))

        start = time.time()
        logging.info("Processing data structure");
        cdu.calculateStats(rootNode)
        end = time.time()
        logging.info("\t took:%d seconds, processed:%d files" % (end - start, rootNode.totalFiles))
        return rootNode


DEF_BIN_PATH="./.cagedu.gz"
DEF_GRAPH_DIR="./dot-export"
DEF_SVG_DIR="./svg-export"
DEF_MAX_DEPTH=6

def main():

    if sys.argv[1] == "scan":
        (sys.argv).remove("scan")
        parser.add_argument ("-export", "--export", dest='exportFile', type=str, default=DEF_BIN_PATH,
                help='Path where to store scan result')
        parser.add_argument("-maxdepth", "--maxdepth", dest='maxDepth', type=int, default=DEF_MAX_DEPTH,
                help='Max depth where scan will store directories structure');
        args = parse_options()
        rootDir = args.path
        logging.info("Building the tree information for %s" % (rootDir));
        try:
            rootStat = os.stat(rootDir)
        except:
            logging.error("Stat on %d failed exiting" % (rootDir))
            os.exit(1)

        rootNode = FileStat(rootDir,rootStat)
        start = time.time()
        cdu.buildTree(rootNode, maxDepth=args.maxDepth)
        end = time.time()
        logging.info("\t took:%d seconds, processed:%d files" % (end - start, rootNode.totalFiles))

        with gzip.open(args.exportFile, 'wb') as f:
            exporter = DictExporter()
            pickle.dump(exporter.export(rootNode), f, pickle.HIGHEST_PROTOCOL)

    elif sys.argv[1] == "print":
        (sys.argv).remove("print")
        parser.add_argument('-import', "--import", dest='importFile', type=str, default=DEF_BIN_PATH,
                help='Path where to read results of scan');
        args = parse_options()
        rootNode = load_and_process(args.importFile)

        logging.info("Printing the tree...");
        cdu.printTree(rootNode)
    elif sys.argv[1] == "dotexport":
        (sys.argv).remove("dotexport")
        parser.add_argument('-import', "--import", dest='importFile', type=str, default=DEF_BIN_PATH,
                help='Path where to read results of scan');

        parser.add_argument('-out', "--out", dest='outDir', type=str, default=DEF_GRAPH_DIR,
                help='Path where to save the graphical output');
        args = parse_options()
        rootNode = load_and_process(args.importFile)
        logging.info("Saving the tree...")
        cdu.exportDot(rootNode, args.outDir)
    elif sys.argv[1] == "dot2svg":
        (sys.argv).remove("dot2svg")
        parser.add_argument('-import', "--import", dest='importDir', type=str, default=DEF_GRAPH_DIR,
                help='Path where to read .dot files');
        parser.add_argument('-out', "--out", dest='outDir', type=str, default=DEF_SVG_DIR,
                help='Path where to save .svg files');
        args = parse_options()
        logging.info("Converting dot to svg...")
        cdu.dot2svg(args.importDir, args.outDir)

    else:
        logging.error("No command given, supported sub commands are: scan and print")
     

