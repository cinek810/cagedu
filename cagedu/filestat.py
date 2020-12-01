from anytree import NodeMixin, RenderTree, findall
from anytree.exporter import DotExporter
import logging
import os



#results = dict()
#hierarchy = dict()

class FileStat(NodeMixin):
    def __init__(self, name, stat, parent=None, children=None):
        self.name = name
        self.parent = parent
        self.totalSize = 0
        self.byteAge = 0
        self.totalFiles = 0
        if children:
            self.children = children
        if parent is not None:
            logging.debug("Adding:%s with parent:%s" % (self.name, self.parent.name))

        self.st_mode = stat.st_mode
        self.st_mtime = stat.st_mtime
        self.st_size = stat.st_size


    def addStats(self, fileSize, fileAge):
        self.totalSize += fileSize
        self.byteAge += fileSize * fileAge
        self.totalFiles += 1
        logging.debug("totalFiles:%d name:%s" % (self.totalFiles, self.name))
        if self.parent:
            logging.debug("Internal adding stats to %s" %  (self.name)) 
            self.parent.addStats(fileSize, fileAge)

    def statAndAdd(self, pathname):
        try:
            statResult = os.stat(pathname)
            mode = statResult.st_mode
        except Exception as e:
            logging.debug('Stat failed:%s, skipping %s' % (e, pathname))
            return
        logging.debug('Adding stat of %s to node "%s"' % (pathname, self.name))
        self.addStats(statResult.st_size, statResult.st_mtime)



