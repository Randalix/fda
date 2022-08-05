import os
import sys
from pathlib import Path
from fda import config
from imp import reload
from fda import utils
import hou
reload(config)
reload(utils)


def save(nodepath=None):
    if not nodepath:
        selected = hou.selectedNodes()
        if selected:
            nodepath = selected[-1].path()
    if nodepath:
        node = hou.node(nodepath)
        name = node.name()
        if name == "/":
            name = hou.hipFile.basename()
        path = config.lib /  name
        path=str(path.resolve())
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
    folder = config.lib / name
    folder.mkdir(parents=True, exist_ok=True)
    for net in utils.savenetworks:
        path = folder / net
        path=str(path.resolve())
        node = hou.node('/' + net)
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

def loadscene(path):
    for net in config.savenetworks:
        netpath = Path(path) / net
        file = open(netpath, "r")
        coderead = file.read()
        # net = utils.currentNetworkEditor()
        # if net:
            # mouse_pos = utils.currentNetworkEditor().cursorPosition()
            # move = f"hou_node.move(hou.Vector2({mouse_pos}))"
            # lines = coderead.split("\n")
            # lines[6] = move
            # coderead ='\n'.join(lines)
        # code = f"###########\nhou_parent=hou.node('{parent}')\n{coderead}"
        exec(coderead)

def fdamenu():
    import subprocess
    p1 = subprocess.Popen(["ls", config.lib],
     stdout=subprocess.PIPE)
    file = subprocess.check_output(['menu'], stdin=p1.stdout).decode('utf-8').replace('\n','')
    print(file)
    load(config.lib / file)
