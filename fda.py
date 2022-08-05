import os
import hou
import config
from pathlib import Path
from imp import reload
reload(config)

def save():
    selected = hou.selectedNodes()
    if (selected != None):
        node = selected[-1]

        dir = config.lib
        name = node.name()
        path = dir / name + "_asCode.py"
        code = node.asCode(False, True)
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
        path = os.path.abspath(path)
        open(path)
