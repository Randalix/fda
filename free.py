import os
import sys
from pathlib import Path
from fda import config
from imp import reload
from fda import utils
import hou
reload(config)
reload(utils)
from sys import exit

def savenode(node, path):
    code = node.asCode(
            brief=False,
            recurse=True,
            save_channels_only=False,
            save_creation_commands=True,
            save_keys_in_frames=False,
            save_outgoing_wires=False,
            save_parm_values_only=False,
            save_spare_parms=True,
            function_name=None
            )
    node_file = open(path, "w")
    node_file.write(code)
    node_file.close()

def savenfda(nodepath=None):
    if not nodepath:
        selected = hou.selectedNodes()
        if selected:
            nodepath = selected[-1].path()
    if nodepath:
        node = hou.node(nodepath)
        name = node.name()
        name_choice = hou.ui.readInput(message='Name FDA', buttons=('OK','Cancle'), default_choice=1, close_choice=-1, help=None, title=None, initial_contents=name)
        if name_choice[0]==0:
            name = name_choice[1]
            path = config.lib /  name
            path=str(path.resolve())
            savenode(node, path)


def load(path):
    parent = utils.getparent().path()
    file = open(path, "r")
    coderead = file.read()
    net = utils.currentNetworkEditor()
    if net:
        mouse_pos = utils.currentNetworkEditor().cursorPosition()
        move = f"hou_node.move(hou.Vector2({mouse_pos}))"
        lines = coderead.split("\n")
        lines[6] = move
        coderead ='\n'.join(lines)
    code = f"###########\nhou_parent=hou.node('{parent}')\n{coderead}"
    exec(code)

def savescene():
    name = hou.hipFile.basename()
    name_choice = hou.ui.readInput(message='Name Scene', buttons=('OK','Cancle'), default_choice=1, close_choice=-1, help=None, title=None, initial_contents=name)
    if name_choice[0]==0:
        name = name_choice[1]
        folder = config.lib / name
        folder.mkdir(parents=True, exist_ok=True)
        for net in config.savenetworks:
            path = folder / net
            path=str(path.resolve())
            node = hou.node('/' + net)
            savenode(node, path)

def loadscene(path):
    for net in config.savenetworks:
        netpath = Path(path) / net
        file = open(netpath, "r")
        coderead = file.read()
        exec(coderead)

def fdamenu():
    import subprocess
    p1 = subprocess.Popen(["ls", config.lib],
     stdout=subprocess.PIPE)
    file = subprocess.check_output(['menu'], stdin=p1.stdout).decode('utf-8').replace('\n','')
    load(config.lib / file)

def convert_hda(node_hda=None, copy_parm_values=1):
        if not node_hda:
                node_hda = hou.selectedNodes()[0]
        source_name = node_hda.name()
        source_pos = node_hda.position()
        source_type = node_hda.childTypeCategory().name()

        # CHECK IF WE NEED A GEO OBJ INSTEAD OF SUBNET, BECAUSECHILDEN ARE SOP BUT PARENT IS OBJECT
        if source_type == "Sop" and node_hda.parent().childTypeCategory().name() == "Object":
            my_node = node_hda.parent().createNode("geo", source_name + "_UNLOCKED",True)
        else:
            my_node = node_hda.parent().createNode("subnet",source_name + "_UNLOCKED",True)

        node_copy = hou.copyNodesTo(node_hda.children(),my_node)[0]
        hda_parms = node_hda.parmTemplateGroup()
        my_node.setParmTemplateGroup(hda_parms)

        if copy_parm_values == 1:
                source_parms = node_hda.parms()
                new_parms = my_node.parms()
                # FINDS CORRESPONDING PARAMETERS
                for new_parm in new_parms:
                    for source_parm in source_parms:
                        if new_parm.name() == source_parm.name():
                            if source_parm.keyframes():
                                try:
                                    my_node.parm(new_parm.name()).setExpression(source_parm.rawValue())
                                except:
                                    my_node.parm(new_parm.name()).set(source_parm.eval())
                            else:
                                try:
                                    my_node.parm(new_parm.name()).set(source_parm.rawValue())
                                except:
                                    my_node.parm(new_parm.name()).set(source_parm.eval())

        # SHIFT NEW NODETO THE RIGHT
        new_pos = pos = (source_pos[0] +2, source_pos[1])
        my_node.setPosition(new_pos)


        

