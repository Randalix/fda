from sys import platform
import  os
import hou

def open(path):
    if platform.startswith('darwin'):
        os.system('open "' + path + '"')
    elif platform.startswith('linux'):
        os.system('xdg-open "' + path + '"')
    elif platform.startswith('win32'):
        os.startfile(path)


def currentNetworkEditor():
    editor = [pane for pane in hou.ui.paneTabs() if isinstance(pane, hou.NetworkEditor) and pane.isUnderCursor()]
    if len(editor) >0:
        editor=editor[-1]
    else:
        import toolutils
        editor=toolutils.networkEditor()
    return editor



def getparent():
    if hou.selectedNodes():
        parent=hou.selectedNodes()[-1].parent()
    else:
        parent = currentNetworkEditor().pwd()
    return parent


def getfdatype():
    '''
    Check which houdini context the nodes belonging to 
    '''
    parent = getparent()
    fdatype = parent.childTypeCategory().name()
    return fdatype

def collapseselection(fdaname='tmp'):
    selection = hou.selectedNodes()
    if selection:
        parent = getparent()
        subnet = parent.createNode("subnet", fdaname, True)
        hou.copyNodesTo(selection, subnet)
        subnet.setSelected(True)
        return subnet

def extractsubnet():
    subnet = hou.selectedNodes()[0]
    parent = subnet.parent()
    children = subnet.children()
    hou.copyNodesTo(children, parent)
    subnet.destroy()


