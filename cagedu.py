#!/usr/bin/python

import os, sys, time, datetime
import logging
from stat import *
from anytree import NodeMixin, RenderTree, findall
from anytree.exporter import DotExporter

logging.basicConfig(level=logging.DEBUG, format='cdu: %(name)s %(message)s')

class FileStat(NodeMixin):
    def __init__(self, name, stat, parent=None, children=None):
        self.name = name
        self.parent = parent
        self.totalSize = 0
        self.byteAge = 0
        if children:
            self.children = children

        self.st_mode = stat.st_mode
        self.st_mtime = stat.st_mtime
        self.st_size = stat.st_size


    def addStats(self, fileSize, fileAge):
        self.totalSize += fileSize
        self.byteAge += fileSize * fileAge
        if self.parent:
            logging.debug("Internal adding stats to %s" %  (self.name)) 
            self.parent.addStats(fileSize, fileAge)


results = dict()
hierarchy = dict()

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
                newNode = FileStat(pathname.encode('utf-8'),statResult, parent = top)
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
                print("%s %s AveDate:%s Size:%.2fMB" % (pre, node.name, date , node.totalSize / 1024 / 1024 ))
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
    buildTree(rootNode, maxDepth=3)

    logging.info("Processing data structure");
    calculateStats(rootNode)

    logging.info("Printing the tree");
    printTree(rootNode)

    #DotExporter(rootNode, maxlevel=3).to_picture("/home/cinek/myTree.png");
