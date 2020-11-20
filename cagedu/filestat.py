from anytree import NodeMixin, RenderTree, findall
from anytree.exporter import DotExporter
import logging



#results = dict()
#hierarchy = dict()

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



