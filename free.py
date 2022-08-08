import os
import sys
from pathlib import Path
from fda import config
from imp import reload
from fda import utils
from fda import git
import hou
reload(config)
reload(git)
reload(utils)
from sys import exit

def savenode(node, path):
    '''
        writes out the given node as python code
    '''
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

# def fdaexists():
    # exists = false

def markloose(folder):
    '''
        Creates an empty file to identify loose node collections
    '''
    loosemark = folder /  '.loose'
    loose_file = open(loosemark, "w")
    loose_file.write("")
    loose_file.close()


def savefda(nodepath=None):
    '''
        Saves the node selection as FDA
    '''
    loose=False # Variable to check if it's a single node or a collection of  loose nodes
    # Get Selection
    if not nodepath:
        selected = hou.selectedNodes()
        if selected:
            nodepath = selected[0].path()
            if len(selected)>1:
                loose=True
    if nodepath:
        node = hou.node(nodepath)
        fdaname= node.name() # Default name is node name
        name_choice = hou.ui.readInput(message='fdanameFDA', buttons=('OK','Cancle'), default_choice=1, close_choice=-1, help=None, title=None, initial_contents=fdaname) # User Input Name
        if name_choice[0]==0: # Only proceed if pressed OK Button
            fdaname= name_choice[1]
            fdatype = utils.getfdatype() # Check which houdini context the nodes belonging to 
            folder = config.lib / fdatype / fdaname
            exists = False
            if folder.exists():
                exists = True
            else:
                folder.mkdir(parents=True, exist_ok=True)
            path = folder /  fdaname
            if loose: # Saving just 
                markloose(folder)
                # If it is a loose collection of nodes we create a tmp container to bundle as single node
                node = utils.collapseselection(fdaname) 
            savenode(node, path)
            if not exists:
                git.init(folder)
                print("new node")
            else:
                git.update(folder)
            if loose:
                node.destroy() # If it is a loose collection of nodes we delete the tmp container




def loadfda(path):
    folder = Path(path).parent
    parent = utils.getparent()
    file = open(path, "r")
    coderead = file.read()
    net = utils.currentNetworkEditor()
    if net:
        mouse_pos = utils.currentNetworkEditor().cursorPosition()
        move = f"hou_node.move(hou.Vector2({mouse_pos}))"
        lines = coderead.split("\n")
        lines[6] = move
        lines = lines[3:]
        coderead ='\n'.join(lines)
    code = f"hou_parent=hou.node('{parent.path()}')\n{coderead}"
    exec(code)
    loosepath = folder / '.loose'
    if loosepath.is_file():
        utils.extractsubnet()


def savescene():
    fdaname= hou.hipFile.basename()
    name_choice = hou.ui.readInput(message='fdanameScene', buttons=('OK','Cancle'), default_choice=1, close_choice=-1, help=None, title=None, initial_contents=name)
    if name_choice[0]==0:
        fdaname = name_choice[1]
        folder = config.lib / 'scenefiles' / fdaname
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
    from subprocess import run, PIPE
    fdatype = utils.getfdatype()
    folder = config.lib / fdatype
    availablefda = os.listdir(str(folder))
    menuin = "\n".join(availablefda)
    p = run(['menu'], stdout=PIPE,
        input=menuin, encoding='ascii')
    fdaname = p.stdout.replace('\n', '')
    loadfda(folder / fdaname / fdaname)

