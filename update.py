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
    matcher = nodesearch.Parm("__FDA", "!=", "")
    network = hou.node("/obj/")
    fdas = []
    for node in matcher.nodes(network, recursive=True):
        fdas.append(node)
    return fdas


def all():
    fdas = findfdas()
    for fda in fdas:
        if git.needsupdate(fda):
            recreate(fda)

def recreate(node):
    inputs = node.inputConnections()
    outputs = node.outputConnections()
    position = node.position()
    # node.destroy()
    fdaname = Path(node.parm("__FDA").eval().split(':')[0])
    path = config.lib / fdaname / fdaname.name
    nodes = free.loadfda(path, node.parent())
    if nodes:
        node = nodes[0]
        for input in inputs:
            node.setInput(input.inputIndex(), input.inputItem(), input.outputIndex())
