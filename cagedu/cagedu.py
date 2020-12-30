#!/usr/bin/python

from __future__ import absolute_import

import os, sys, time, datetime
from stat import *
from anytree import NodeMixin, RenderTree, findall
import logging
from cagedu.filestat import FileStat


#results = dict()
#hierarchy = dict()

def buildTree(top, maxDepth = 0, currentDepth = 0):
    logging.debug("currentDepth=%d maxDepth=%d" % (currentDepth, maxDepth))
    if maxDepth == 0 or currentDepth < maxDepth:
        for f in os.listdir(top.filename):
            pathname = os.path.join(top.filename, f)
            try:
                statResult = os.lstat(pathname)
                mode = statResult.st_mode
            except Exception as e:
                logging.debug('Stat failed:%s, skipping %s' % (e, pathname))
                continue

            if S_ISDIR(mode):
                logging.debug('Adding directory %s to parent "%s"' % (unicode(pathname).encode('utf-8'), top.filename))
                newNode = FileStat(pathname, statResult, parent = top)
                newDepth = currentDepth + 1
                buildTree(newNode, maxDepth = maxDepth, currentDepth = newDepth)
            elif S_ISREG(mode):
                logging.debug('Adding stat below maxDepth=%d currentDepth=%d for file=%s' % (maxDepth, currentDepth, pathname))
                top.addStats(statResult.st_size, statResult.st_mtime)
    else:
        logging.debug("Adding stats without new nodes")
        for path, subdirs, files in os.walk(top.filename):
            for f in files:
                logging.debug("Joining %s and %s" % (top.filename, f));
                pathname = os.path.join(path, f)
                top.statAndAdd(pathname)

def calculateStats(topNode):

    files = findall(topNode, lambda node: S_ISREG(node.st_mode))
    for fileNode in files:
        fileSize = fileNode.st_size
        fileAge = fileNode.st_mtime 

        logging.debug("calculate stat %s in %s" % (fileNode.filename, fileNode.parent.filename))
        fileNode.parent.addStats(fileNode.st_size, fileNode.st_mtime)



def printTree(node):
    for pre, fill, node in RenderTree(node):
        if S_ISDIR(node.st_mode):
            try:
                timestamp = datetime.datetime.fromtimestamp(node.byteAge / node.totalSize)
                date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                print("%s %s AveDate:%s Size:%.2fMB" % (unicode(pre).encode('utf-8'), unicode(node.filename).encode('utf-8'), date , node.totalSize / 1024 / 1024 ))
            except ZeroDivisionError:
                print("%s %s (ZERO SIZE)" % (unicode(pre).encode('utf-8'), unicode(node.filename).encode('utf-8')))

import matplotlib as mpl
import matplotlib.cm as cm
import math
def nodeStyle(node):
    norm = mpl.colors.Normalize(vmin=1546020256, vmax=1609178677)
    cmap = cm.plasma
    color = cm.ScalarMappable(norm=norm, cmap=cmap)
    try:
        rgba = color.to_rgba(node.byteAge / node.totalSize)

    except ZeroDivisionError:
        rgba = (0.9, 0.9, 0.9, 0.8)
    hexColor = mpl.colors.rgb2hex(rgba)
    try:
        nodeSize = math.log10(node.totalSize)
    except Exception as e:
        if node.totalSize != 0:
            logging.info("log10 failed for node.totalSize = "+str(node.totalSize)+" with "+e.message)
        nodeSize = 1

    nodeSize = min(9, nodeSize)
    nodeSize = max(2, nodeSize)

    return 'href="subdir/'+str(node.name)+'.svg";style=filled;color=black;fillcolor="'+str(hexColor)+'";width="'+str(nodeSize)+'"fixedsize=true;'

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

from os.path import basename
def nodeName(node):
    return basename(node.filename)+"("+sizeof_fmt(node.totalSize)+")"

def exportWithStyle(node, exportFile):
    DotExporter(node, options = ['rankdir=LR;'], nodenamefunc = nodeName,  nodeattrfunc = nodeStyle, indent = 1, maxlevel = 3).to_dotfile(exportFile)

from anytree.exporter import DotExporter
from anytree import PreOrderIter
def exportDot(node, exportFile):
    exportWithStyle(node, "subdir/"+exportFile)
    for subNode in PreOrderIter(node):
        exportWithStyle(subNode, "subdir/"+str(subNode.name)+".dot")




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
