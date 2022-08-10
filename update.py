import hou
import nodesearch
from fda import git
from fda import free
from imp import reload
from fda import config
from pathlib import Path
reload(git)
reload(free)

def findfdas():
    matcher = nodesearch.Parm("FDA", "!=", "")
    networks = config.savenetworks
    fdas = []
    for net in networks:
        matches = matcher.nodes(hou.node(net), recursive=True)
        fdas += matches
    return fdas


def all():
    fdas = findfdas()
    for fda in fdas:
        if git.needsupdate(fda):
            hou.clearAllSelected()
            recreate(fda)

def recreate(fda):
    inputs = fda.inputConnections()
    outputs = fda.outputConnections()
    fdaname = Path(fda.parm("FDA").eval().split(':')[0])
    parent = fda.parent()
    position = fda.position()
    fda.destroy()
    path = config.lib / fdaname / fdaname.name
    nodes = free.loadfda(path, parent)
    hou.clearAllSelected()
    if nodes:
        for node in nodes:
            for input in inputs:
                node.setInput(input.inputIndex(), input.inputItem(), input.outputIndex())
            for output in outputs:
                input = output.outputItem()
                input.setInput(output.outputIndex(), node, output.outputIndex())
            node.setPosition(position)

