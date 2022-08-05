import os
import sys
from pathlib import Path
from fda import config
from imp import reload
from fda import utils
import hou
reload(config)
reload(utils)


def save():
    selected = hou.selectedNodes()
    if (selected != None):
        node = selected[-1]
        name = node.name()
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
        # lines = code.split("\n")
        # lines = lines[3:]
        # create_node = lines[:3]
        # lines = lines[15:]
        # lines = create_node + lines
        # new_code = "\n".join(lines)
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
