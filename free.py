import os
import sys
from pathlib import Path
from fda import config
from imp import reload
from fda import utils
import hou
reload(config)
# home=Path.home()
# lib=home / "fda"


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
        lines = code.split("\n")
        lines = lines[3:]
        create_node = lines[:3]
        lines = lines[15:]
        lines = create_node + lines
        new_code = "\n".join(lines)
        # new_code = "import jotools as jt\nreload(jt)\nnet = jt.currentNetworkEditor()\nhou_parent = net.pwd()\n" + new_code
        node_file = open(path, "w")
        node_file.write(new_code)
        node_file.close()

def creat(path):
    pass

