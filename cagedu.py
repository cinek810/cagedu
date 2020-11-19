#!/usr/bin/python

import os, sys, time
import logging
from stat import *
from anytree import NodeMixin, RenderTree, findall
from anytree.exporter import DotExporter

logging.basicConfig(level=logging.INFO, format='cdu: %(name)s %(message)s')

class FileStat(NodeMixin):
    def __init__(self, name, stat, parent=None, children=None):
        self.name = name
        self.parent = parent
        self.totalSize = 0
        self.byteAge = 0
        if children:
            self.children = children

        self.stat = stat

    def addStats(self, fileSize, fileAge):
        self.totalSize += fileSize
        self.byteAge = fileSize * fileAge
        if self.parent:
            logging.debug("Internal adding stats to %s" %  (self.name)) 
            self.parent.addStats(fileSize, fileAge)


results = dict()
hierarchy = dict()

def buildTree(top):

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
            newNode = FileStat(pathname.encode('utf-8'),statResult, parent = top)
        except UnicodeDecodeError:
            logging.error("Encoding error with name: %s" % (pathname))
            continue
        
        if S_ISDIR(mode):
            buildTree(newNode)

def calculateStats(topNode):
    now = time.time()

    files = findall(topNode, lambda node: S_ISREG(node.stat.st_mode))
    for fileNode in files:
        fileSize = fileNode.stat.st_size
        fileAge = now - fileNode.stat.st_mtime 

        logging.debug("calculate stat %s in %s" % (fileNode.name, fileNode.parent.name))
        fileNode.parent.addStats(fileSize, fileAge)

def printTree(node):
    for pre, fill, node in RenderTree(node):
        if S_ISDIR(node.stat.st_mode):
            try:
                print("%s %s AveByteAge:%d days Size:%.2fMB" % (pre, node.name, node.byteAge / node.totalSize / 3600 / 24 , node.totalSize / 1024 / 1024 ))
            except ZeroDivisionError:
                print("%s %s (ZERO SIZE)" % (pre, node.name))

if __name__ == '__main__':
    rootDir = sys.argv[1]
    try:
        rootStat = os.stat(rootDir)
    except:
        logging.error("Stat on %d failed exiting" % (rootDir))
        os.exit(1)

    rootNode = FileStat(rootDir,rootStat)

    logging.info("Building the tree information");
    buildTree(rootNode)

    logging.info("Processing data structure");
    calculateStats(rootNode)

    logging.info("Printing the tree");
    printTree(rootNode)

    DotExporter(rootNode).to_picture("/home/cinek/myTree.png");
