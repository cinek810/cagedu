#!/usr/bin/python

from __future__ import absolute_import

import os, sys, time, datetime
from stat import *
from anytree import NodeMixin, RenderTree, findall
from anytree.exporter import DotExporter
import logging
from cagedu.filestat import FileStat


#results = dict()
#hierarchy = dict()

def buildTree(top, maxDepth = 0, currentDepth = 0):
    logging.debug("currentDepth=%d maxDepth=%d" % (currentDepth, maxDepth))
    if maxDepth == 0 or currentDepth < maxDepth:
        for f in os.listdir(top.name):
            pathname = os.path.join(top.name, f)
            try:
                statResult = os.stat(pathname)
                mode = statResult.st_mode
            except:
                logging.debug('Stat failed, skipping %s' % pathname)
                continue

            logging.debug('Adding node %s to parent "%s"' % (pathname, top.name))
            try:
                newNode = FileStat(pathname, statResult, parent = top)
            except UnicodeDecodeError:
                logging.error("Encoding error with name: %s" % (pathname))
                continue
            
            if S_ISDIR(mode):
                newDepth = currentDepth + 1
                buildTree(newNode, maxDepth = maxDepth, currentDepth = newDepth)
    else:
        logging.debug("Adding stats without new nodes")
        for path, subdirs, files in os.walk(top.name):
            for f in files:
                logging.debug("Joining %s and %s" % (top.name, f));
                pathname = os.path.join(path, f)
                try:
                    statResult = os.stat(pathname)
                    mode = statResult.st_mode
                except:
                    logging.debug('Stat failed, skipping %s' % pathname)
                    continue
                logging.debug('Adding stat of %s to node "%s"' % (pathname, top.name))
                top.addStats(statResult.st_size, statResult.st_mtime)

def calculateStats(topNode):

    files = findall(topNode, lambda node: S_ISREG(node.st_mode))
    for fileNode in files:
        fileSize = fileNode.st_size
        fileAge = fileNode.st_mtime 

        logging.debug("calculate stat %s in %s" % (fileNode.name, fileNode.parent.name))
        fileNode.parent.addStats(fileNode.st_size, fileNode.st_mtime)



def printTree(node):
    for pre, fill, node in RenderTree(node):
        if S_ISDIR(node.st_mode):
            try:
                timestamp = datetime.datetime.fromtimestamp(node.byteAge / node.totalSize)
                date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                print("%s %s AveDate:%s Size:%.2fMB" % (unicode(pre), unicode(node.name), date , node.totalSize / 1024 / 1024 ))
            except ZeroDivisionError:
                print("%s %s (ZERO SIZE)" % (unicode(pre), unicode(node.name)))


def main(mainPath):
    rootDir = mainPath
    try:
        rootStat = os.stat(rootDir)
    except:
        logging.error("Stat on %d failed exiting" % (rootDir))
        os.exit(1)

    rootNode = FileStat(rootDir,rootStat)

    logging.info("Building the tree information");
    buildTree(rootNode, maxDepth=3)

    logging.info("Processing data structure");
    calculateStats(rootNode)

    logging.info("Printing the tree");
    printTree(rootNode)

if __name__ == '__main__':
    main(sys.argv[1])
    #DotExporter(rootNode, maxlevel=3).to_picture("/home/cinek/myTree.png");
