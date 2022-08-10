import hou
import nodesearch
from fda import git
from fda import free
from imp import reload
from fda import config
from pathlib import Path
reload(git)
reload(free)

def findfdas(networks=config.savenetworks):
    matcher = nodesearch.Parm("FDA", "!=", "")
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

def selectedtype():
    selected = hou.selectedNodes()
    for node in selected:
        fdaparm = node.parm("FDA")
        if fdaparm:
            name = fdaparm.eval().split(":")[0]
            searchPattern = f"{name}:*"
            matcher = nodesearch.Parm("FDA", "~=", searchPattern)
            matches = matcher.nodes(hou.node("/obj"), recursive=True)
            for fda in matches:
                if git.needsupdate(fda):
                    recreate(fda)

def recreate(node):
    inputs = node.inputConnections()
    outputs = node.outputConnections()
    fdaname = Path(node.parm("FDA").eval().split(':')[0])
    parent = node.parent()
    position = node.position()
    node.destroy()
    path = config.lib / fdaname / fdaname.name
    hou.clearAllSelected()
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

