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


