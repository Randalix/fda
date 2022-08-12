import hou
import nodesearch
from imp import reload
from fda import git
from fda import settings
from fda import free
from fda import config
from pathlib import Path
from sys import exit
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


def readparms(node):
    node_settings = {}
    for parm in node.parm():
        node_settings[parm.name()] = parm.rawValue()
    return node_settings

def non_default_parms(node, data):
    exit
    uuid = node.parm("FDAUUID").eval()
    default_parms = data["nodes"][uuid]["parms"]
    parms = node.parms()
    saved_parms = default_parms.keys()
    ignore_parms = ["FDA", "FDAUUID", "FDALNK"]
    parm_overwrite = {}
    for parm in parms:
        parm_name = parm.name()
        if parm_name in saved_parms and parm_name not in ignore_parms:
            default_value = default_parms[parm_name]["value"]
            value = parm.rawValue()
            if value != default_value:
                parm_overwrite[parm_name] = value

    return parm_overwrite

def reapply_custom_changes(node,override_parms):
    for parm in override_parms:
        node.parm(parm).set(override_parms[parm])


def recreate(rootnode):
    fdaname = Path(rootnode.parm("FDA").eval().split(':')[0])
    fdaversion = rootnode.parm("FDA").eval().split(':')[-1]
    settings_path = config.lib / fdaname
    data = settings.read(settings_path, fdaversion)
    new_data = settings.read(settings_path)
    children = findchildren(rootnode, data)
    parent = rootnode.parent()
    nodes = [rootnode] + children
    path = config.lib / fdaname / fdaname.name

    for node in nodes:
        uuid = node.parm("FDAUUID").eval()
        inputs = []
        for input in node.inputConnectors():
            if len(input) > 0:
                item = input[0].inputItem()
                if not item in nodes:
                    inputs.append(input)

        outputs = []
        for output in node.outputConnectors():
            if len(output) > 0:
                item = output[0].outputItem()
                if not item in nodes:
                    outputs.append(output)

        outputs = node.outputConnectors()
        position = node.position()
        default_parms = data["nodes"][uuid]["parms"]
        new_data["nodes"][uuid]["position"] = position
        new_data["nodes"][uuid]["inputs"] = inputs
        new_data["nodes"][uuid]["outputs"] = outputs
        ignore_parms = ["FDA", "FDAUUID", "FDALNK"]
        saved_parms = [parm for parm in default_parms.keys() if not parm in ignore_parms]
        for parm in saved_parms:
            default_value = default_parms[parm]["value"]
            if node.parm(parm):
                value = node.parm(parm).rawValue()
                if value != default_value:
                    new_data["nodes"][uuid]["parms"][parm]["value"] = value

    old_nodes = nodes
    hou.clearAllSelected()
    nodes = free.loadfda(path, parent)
    hou.clearAllSelected()

    if nodes:
        for node in nodes:
            uuid = node.parm("FDAUUID").eval()
            savedparms = new_data["nodes"][uuid]["parms"].keys()
            inputs = new_data["nodes"][uuid]["inputs"]
            outputs = new_data["nodes"][uuid]["outputs"]
            for input in inputs:
                for x in input:
                    item = x.inputItem()
                    node.setInput(x.inputIndex(), x.inputItem(), x.outputIndex())
            for output in outputs:
                for x in output:
                    input = x.outputItem()
                    input.setInput(x.outputIndex(), node, x.outputIndex())
            position = new_data["nodes"][uuid]["position"]
            node.setPosition(position)
            for parm in savedparms:
                node_parm = node.parm(parm)
                if node_parm:
                    value = new_data["nodes"][uuid]["parms"][parm]["value"]
                    try:
                        node_parm.set(value)
                    except:
                        pass
        [node.destroy() for node in old_nodes]

def findchildren(rootnode, data):
    children = []
    nodecount = data["nodecount"]
    child_count = nodecount - 1
    for child in range(child_count):
        child_parm_name = f"FDALNK{child}"
        child_parm = rootnode.parm(child_parm_name)
        if child_parm:
            child = rootnode.node(child_parm.eval())
            children.append(child)
    return children


            # for parm in override_parms:
                # node.parm(parm).set(override_parms[parm])
