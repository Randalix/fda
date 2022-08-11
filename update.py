import hou
import nodesearch
from imp import reload
from fda import git
from fda import settings
from fda import free
from fda import config
from pathlib import Path
reload(git)
reload(free)
reload(settings)

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

# def update_parms(node, data):
    # uuid = node.parm("FDAUUID").eval()
    # default_parms = data["nodes"][uuid]["parms"]
    # parms = node.parms()
    # saved_parms = default_parms.keys()
    # ignore_parms = ["FDA", "FDAUUID", "FDALNK"]
    # for parm in parms:
        # parm_name = parm.name()
        # if parm_name in saved_parms and parm_name not in ignore_parms:
            # default_value = default_parms[parm_name]["value"]
            # value = parm.rawValue()
            # print(parm_name)
            # print(value, default_value)

def readparms(node):
    node_settings = {}
    for parm in node.parm():
        node_settings[parm.name()] = parm.rawValue()
    return node_settings

def non_default_parms(node, fdaname, fdaversion):
    data = settings.read(config.lib / fdaname, fdaversion)
    uuid = node.parm("FDAUUID").eval()
    default_parms = data["nodes"][uuid]["parms"]
    parms = node.parms()
    saved_parms = default_parms.keys()
    ignore_parms = ["FDA", "FDAUUID", "FDALNK"]
    parm_override_dict = {}
    for parm in parms:
        parm_name = parm.name()
        if parm_name in saved_parms and parm_name not in ignore_parms:
            default_value = default_parms[parm_name]["value"]
            value = parm.rawValue()
            if value != default_value:
                parm_override_dict[parm_name] = value

    return parm_override_dict

def reapply_custom_changes(node,override_parms):
    for parm in override_parms:
        node.parm(parm).set(override_parms[parm])


def recreate(node):
    inputs = node.inputConnections()
    outputs = node.outputConnections()
    fdaname = Path(node.parm("FDA").eval().split(':')[0])
    fdaversion = node.parm("FDA").eval().split(':')[1]
    override_parms = non_default_parms(node, fdaname, fdaversion)
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
            reapply_custom_changes(node, override_parms)

