#!/usr/bin/python

from __future__ import absolute_import

import os, sys, time, datetime
from stat import *
from anytree import NodeMixin, RenderTree, findall
import logging
from cagedu.filestat import FileStat
import hashlib


#results = dict()
#hierarchy = dict()


def scantree(path):
    for f in os.scandir(path):
        if f.is_dir(follow_symlinks=False):
            yield from scantree(f.path)
        else:
            yield f

def buildTree(top, maxDepth = 0, currentDepth = 0):
    logging.debug("currentDepth=%d maxDepth=%d" % (currentDepth, maxDepth))
    if maxDepth == 0 or currentDepth < maxDepth:
        for f in os.scandir(top.filename):
            if f.is_dir(follow_symlinks=False):
                logging.debug('Adding directory %s to parent "%s"' % (str(f.path).encode('utf-8'), top.filename))
                newNode = FileStat(name = f.path, parent = top)
                newDepth = currentDepth + 1
                buildTree(newNode, maxDepth = maxDepth, currentDepth = newDepth)
            elif f.is_file(follow_symlinks=False):
                try:
                    statResult = os.lstat(f.path)
                except:
                    logging.debug('Stat failed:%s, skipping %s' % (e, f.path))
                    continue

                logging.debug('Adding stat below maxDepth=%d currentDepth=%d for file=%s' % (maxDepth, currentDepth, f.path))
                top.addStats(statResult.st_size, statResult.st_mtime)
    else:
        logging.debug("Adding stats without new nodes")
        for f in scantree(top.filename):
            logging.debug("Joining %s" % (f.path));
            if f.is_file(follow_symlinks=False):
                top.statAndAdd(f.path)

def isRegular(node):
    try:
        if(S_ISREG(node.st_mode)):
            return True
    except:
        logging.error("Node doesn't have st_mode:%s" % (node));
        yield False

def calculateStats(topNode):
    files = findall(topNode, isRegular)
    for fileNode in files:
        logging.debug("Calculate stat on %s" % (fileNode))
        try:
            fileSize = fileNode.st_size
        except:
            logging.error("Node doesn't have st_size: %s" % (fileNode))
            continue

        try:
            fileAge = fileNode.st_mtime
        except:
            logging.error("Node doesn't have st_mtime");
            continue

        try:
            fileNode.parent.addStats(fileNode.st_size, fileNode.st_mtime)
        except Exception as e:
            logging.error("Failed to add stat to parent for %s, error: %s" % (fileNode, str(e)))

def printTree(node):
    for pre, fill, node in RenderTree(node):
        if isRegular(node):
            try:
                timestamp = datetime.datetime.fromtimestamp(node.byteAge / node.totalSize)
                date = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                print("%s %s AveDate:%s Size:%.2fMB" % (str(pre), str(node.filename), date , node.totalSize / 1024 / 1024 ))
            except ZeroDivisionError:
                print("%s %s (ZERO SIZE)" % (str(pre), str(node.filename)))

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
    style = 'href="'+str(node.name)+'.svg";style=filled;color=black;fillcolor="'+str(hexColor)+'";width="'+str(nodeSize)+'"fixedsize=true;'
    if not builtInFilter(node):
        style += style+"style=invis;fontsize=1;width=0.02,height=0.02"
    return style

def human_bytes(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

from os.path import basename
def nodeName(node):
    name = basename(node.filename)+"("+human_bytes(node.totalSize)+")"
    if builtInFilter(node):
        return name
    else:
        return ""

def sortByNodeSize(node):
    return node.totalSize

def builtInFilter(node):
    if node.depth == 0:
        return True

    if node.depth > 1 and node.totalSize < node.parent.totalSize * 0.15:
        logging.debug("Filtering out: "+node.filename+" because of size threshold")
        return False
    else:
        return True

def edgeStyle(parent, child):
    style = ""
    if not builtInFilter(child):
        style += "style=invis;fontsize=1;height=0.02;width=0.02"
    return style

###Limit to 2 levels is currently hardcoded
#For 2nd level totalSize sorting is performed, so biggest directories are
#displayed on top
#For 3rd level only subdirectories of size >= 25% of parent are displayed
def exportWithStyle(node, exportFile):
    index = 0

    orderedRanks = LevelOrderGroupIter(node, maxlevel=2, filter_ = builtInFilter);
    sortedList = []
    sortedSet = set()

    for group in  orderedRanks:
        if index == 0:
            index += 1
            continue
        for nnode in group:
            sortedSet.add(nnode)
    
    sortedString = ""
    if sortedSet:
        sortedSet = sorted(sortedSet, key = sortByNodeSize, reverse = True)
        sortedString = "{rank=same;rankdir=TB;"
        firstNode = True

        oldParent = None
        for nnode in sortedSet:
            if firstNode:
                firstNode = False
            else:
                sortedString += '->'
            if oldParent is not None and oldParent != nnode.parent:
                logging.info(str(nnode.filename)+"--"+str(oldParent.filename)+" !=  "+str(nnode.parent.filename))
                break
            sortedString += '"'+nodeName(nnode)+'"'
            oldParent = nnode.parent

        sortedString += "[style = invis];}"

    logging.error("%s" % (exportFile))

    UniqueDotExporter(node, options = ['rankdir=LR;', sortedString], nodenamefunc = nodeName,  nodeattrfunc = nodeStyle, edgeattrfunc = edgeStyle, indent = 1, maxlevel = 3).to_dotfile(exportFile)

from anytree.exporter import UniqueDotExporter
from anytree import PreOrderIter, LevelOrderGroupIter
from os import mkdir
import errno
def exportDot(node, exportDir):
    try:
        mkdir(exportDir)
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            logging.fatal("Cannot continue. Output directory "+str(exportDir)+" already exists")
        else:
            logging.fatal("Cannot continue. Error is:"+str(exc))


    exportWithStyle(node, exportDir+"/index.dot")
    for subNode in PreOrderIter(node):
        if subNode.name == -1:
            logging.error("Node name is -1 for %s, skipping it. This should never happen" % (subNode.filename));
            continue

        exportWithStyle(subNode, exportDir+"/"+subNode.name+".dot")

def dot2svg(inDir, outDir):
    try:
        os.system("dot -V")
    except:
        logging.fatal("dot2svg subcommand required dot app to be installed and available in $PATH");
        return

    if not os.path.exists(outDir):
        try:
            os.mkdir(outDir)
        except Exception as e:
            logging.fatal("Failed creating output directory: %s" % (str(e)))
        

    for file in os.scandir(inDir):
        nameNoExt = os.path.splitext(file.name)[0]
        os.system("dot -T svg "+inDir+"/"+file.name+" -o "+outDir+"/"+nameNoExt+".svg")


#
#def main(mainPath):
#    rootDir = mainPath
#    try:
#        rootStat = os.stat(rootDir)
#    except:
#        logging.error("Stat on %d failed exiting" % (rootDir))
#        os.exit(1)
#
#    rootNode = FileStat(rootDir,rootStat)
#
#    logging.info("Building the tree information");
#    buildTree(rootNode, maxDepth=3)
#
#    logging.info("Processing data structure");
#    calculateStats(rootNode)
#
#    logging.info("Printing the tree");
#    printTree(rootNode)
#
#if __name__ == '__main__':
#    main(sys.argv[1])
#    #DotExporter(rootNode, maxlevel=3).to_picture("/home/cinek/myTree.png");
