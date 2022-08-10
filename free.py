import os
from subprocess import run, PIPE
from pathlib import Path
from imp import reload
from fda import config
from fda import utils
from fda import git
from fda import settings
import hou
from uuid import uuid4
reload(config)
reload(git)
reload(utils)
reload(settings)
from sys import exit
def removeValue(givenlist, value):
    # removing the value using remove()
    givenlist.remove(value)
    # return the list
    return givenlist

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


def isloose(selected):
    loose=False
    if len(selected)>1:
        loose=True
    return loose

def getrootnode(nodes):
    rootnode = None
    for node in nodes:
        if node.parm("FDA"):
            rootnode = node
            break
    if not rootnode:
        rootnode = nodes[0]
    return rootnode

def get_fda_name(node):
    fdaName = None
    parm = node.parm("FDA")
    if parm:
        fdaName = parm.eval().split(":")[0].split("/")[-1]
    return fdaName

def getfdaname(node):
    parm = node.parm("FDA")
    if parm:
        fdaName = get_fda_name(node)
    else:
        fdaName = node.name()
    # User Input Name
    name_choice = hou.ui.readInput(
            message='fdanameFDA',
            buttons=('OK','Cancle'),
            default_choice=0,
            close_choice=-1, 
            help=None,
            title=None,
            initial_contents=fdaName
            )
    if name_choice[0]==0: # Only proceed if pressed OK Button
        fdaName= name_choice[1]
    else:
        exit
    return fdaName

def savefda(nodepath=None):
    '''
        Saves the node selection as FDA
    '''
    # Get Selection
    if not nodepath:
        nodes = hou.selectedNodes()
        if not nodes:
            exit
    else:
        nodes = [hou.node(nodepath)]

    loose = isloose(nodes)
    rootnode = getrootnode(nodes)
    fdaName = getfdaname(rootnode)
    fdatype = utils.getfdatype() 

    # Check which houdini context the nodes belonging to 
    folder = config.lib / fdatype / fdaName

    exists = False
    if folder.exists():
        exists = True
    else:
        folder.mkdir(parents=True, exist_ok=True)

    path = folder /  fdaName

    adduuid(nodes)
    # write json
    settings.write(nodes, folder, loose)

    node = rootnode

    if loose: # Saving just 
        rootnode = utils.collapseselection(fdaName) 

    savenode(rootnode, path)

    if not exists:
        git.init(folder)
    else:
        git.update(folder)

    if loose:
        rootnode.destroy() # If it is a loose collection of nodes we delete the tmp container
    addfdaparm(node, path)
    # addtag(nodes, path, nodes[0].parm("FDAUUID").eval())

def nodesplitchilds(nodes, motheruuid):
    rootnode = nodes[-1]
    for node in nodes:
        uuidparm = node.parm("FDAUUID")
        if uuidparm:
            if node.parm("FDAUUID").eval() == motheruuid:
                rootnode = node
                break

    children = [node for node in nodes if node != rootnode]
    return rootnode, children

def loadfda(path, parent=None, pos=hou.Vector2(0,0)):
    folder = Path(path).parent
    if not parent:
        parent = utils.getparent()

    # Read Generated Creation Code
    file = open(path, "r")
    coderead = file.read()

    # Cange Creation Code
    # Position By mode
    # ToDo: Move to own funtion
    # net = utils.currentNetworkEditor()
    # if net:
        # mouse_pos = utils.currentNetworkEditor().cursorPosition()
    lines = coderead.split("\n")
    move = f"hou_node.move(hou.Vector2(0.0,0.0))"
    lines[6] = move
    lines = lines[3:]
    coderead ='\n'.join(lines)
    code = f"hou_parent=hou.node('{parent.path()}')\n{coderead}"

    # Run Creation Code
    hou.clearAllSelected()
    exec(code)
    nodes = hou.selectedNodes()

    # Read Json
    data = settings.read(folder)
    rootid = data["mother"]

    if int(data["nodecount"]) > 1:
        nodes = utils.extractsubnet()
    rootnode, children = nodesplitchilds(nodes, rootid)

    addlinks(rootnode, children)
    addfdaparm(rootnode, path)
    position_children(rootnode, children, pos)
    return nodes

def position_children(root, children, pos):
    rootpos = root.position()
    allnodes = [root] + children
    for node in allnodes:
        nodepos = node.position()
        delta = nodepos - rootpos
        goalpos = pos + delta
        node.setPosition(goalpos)


def savescene():
    fdaName= hou.hipFile.basename()
    name_choice = hou.ui.readInput(
            message='fdanameScene',
            buttons=('OK',
                'Cancle'
                ),
            default_choice=1,
            close_choice=-1,
            help=None,
            title=None,
            initial_contents=fdaName
            )
    if name_choice[0]==0:
        fdaName = name_choice[1]
        folder = config.lib / 'scenefiles' / fdaName
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
    mouse_pos = utils.currentNetworkEditor().cursorPosition()
    fdatype = utils.getfdatype()
    folder = config.lib / fdatype
    availablefda = os.listdir(str(folder))
    fdaName = menu(availablefda)
    loadfda(folder / fdaName / fdaName,  pos=mouse_pos)

def addlinks(rootnode, children):
    for x, node in enumerate(children):
        parmname = f"FDALNK{str(x)}"
        if not node.parm(parmname):
            group = rootnode.parmTemplateGroup()
            linkpath = f"../{node.name()}"
            parm = hou.StringParmTemplate(parmname, parmname, 1, default_value=[linkpath], string_type=hou.stringParmType.NodeReference, tags={ "oprelative" : ".", },  is_hidden=True)
            group.append(parm)
            rootnode.setParmTemplateGroup(group)

def addfdaparm(rootnode, path):
    if not rootnode.parm("FDA"):
        group = rootnode.parmTemplateGroup()
        parm = hou.StringParmTemplate("FDA", "FDA", 1, default_value=[""],  is_hidden=True)
        group.append(parm)
        rootnode.setParmTemplateGroup(group)
    version = git.currentversion(path.parent)
    relpath = str(path.parents[0].resolve())
    lib = str(config.lib.resolve())
    fdaName = relpath.replace(lib, '')[1:]
    rootnode.parm("FDA").set(f"{fdaName}:{version}")

def adduuid(nodes):
    for node in nodes:
        uuid = str(uuid4())
        parm_name ="FDAUUID"
        if not node.parm(parm_name):
            group = node.parmTemplateGroup()
            parm = hou.StringParmTemplate(parm_name, "UUID", 1, default_value=[uuid], is_hidden=True)
            group.append(parm)
            node.setParmTemplateGroup(group)
