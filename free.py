import os
from subprocess import run, PIPE
from pathlib import Path
from imp import reload
from fda import config
from fda import utils
from fda import git
from fda import settings
import hou
reload(config)
reload(git)
reload(utils)
reload(settings)
from sys import exit

def menu(menuin):
    path = Path(os.path.realpath(__file__))
    folder = path.parent
    menu = folder / "menu"
    os.environ["TERM"] = config.TERM
    os.environ["FZF"] = config.FZF
    menuin = "\n".join(menuin)
    p = run([menu], stdout=PIPE,
        input=menuin, encoding='ascii')
    menout = p.stdout.replace('\n', '')
    return menout


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
    else:
        selected = hou.node(nodepath)

    if nodepath:
        node = hou.node(nodepath)
        fdaname= node.name() # Default name is node name
        # User Input Name
        name_choice = hou.ui.readInput(
                message='fdanameFDA',
                buttons=('OK','Cancle'),
                default_choice=0,
                close_choice=-1, 
                help=None,
                title=None,
                initial_contents=fdaname
                )

        if name_choice[0]==0: # Only proceed if pressed OK Button
            fdaname= name_choice[1]
            fdatype = utils.getfdatype() 

            # Check which houdini context the nodes belonging to 
            folder = config.lib / fdatype / fdaname

            exists = False
            if folder.exists():
                exists = True
            else:
                folder.mkdir(parents=True, exist_ok=True)

            path = folder /  fdaname

            # write json
            settings.write(selected, folder, loose)

            if loose: # Saving just 
                node = utils.collapseselection(fdaname) 

            savenode(node, path)

            if not exists:
                git.init(folder)
            else:
                git.update(folder)
            if loose:
                node.destroy() # If it is a loose collection of nodes we delete the tmp container
            addtag(selected[0], path)




def loadfda(path, parent=None):
    folder = Path(path).parent
    if not parent:
        parent = utils.getparent()

    # Read Generated Creation Code
    file = open(path, "r")
    coderead = file.read()

    # Cange Creation Code
    # Position By mode
    # ToDo: Move to own funtion
    net = utils.currentNetworkEditor()
    if net:
        mouse_pos = utils.currentNetworkEditor().cursorPosition()
        move = f"hou_node.move(hou.Vector2({mouse_pos}))"
        lines = coderead.split("\n")
        lines[6] = move
        lines = lines[3:]
        coderead ='\n'.join(lines)
    code = f"hou_parent=hou.node('{parent.path()}')\n{coderead}"

    # Run Creation Code
    exec(code)
    nodes = hou.selectedNodes()

    # Read Json
    loose, parms = settings.read(folder)

    if loose:
        nodes = utils.extractsubnet()
    for node in nodes:
        addtag(node, path)
    return nodes


def savescene():
    fdaname= hou.hipFile.basename()
    name_choice = hou.ui.readInput(
            message='fdanameScene',
            buttons=('OK',
                'Cancle'
                ),
            default_choice=1,
            close_choice=-1,
            help=None,
            title=None,
            initial_contents=fdaname
            )
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
    fdatype = utils.getfdatype()
    folder = config.lib / fdatype
    availablefda = os.listdir(str(folder))
    fdaname = menu(availablefda)
    loadfda(folder / fdaname / fdaname)

def addtag(node, path):
    if not node.parm("__FDA"):
        group = node.parmTemplateGroup()
        parm = hou.StringParmTemplate("__FDA", "FDA", 1, default_value=[""],  is_hidden=True, is_label_hidden=True)
        group.append(parm)
        node.setParmTemplateGroup(group)
    version = git.currentversion(path.parent)
    relpath = str(path.parents[0].resolve())
    lib = str(config.lib.resolve())
    fdaname = relpath.replace(lib, '')[1:]
    node.parm("__FDA").set(f"{fdaname}:{version}")
