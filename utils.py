from sys import platform
import  os

def open(path):
    if platform.startswith('darwin'):
        os.system('open "' + path + '"')
    elif platform.startswith('linux'):
        os.system('xdg-open "' + path + '"')
    elif platform.startswith('win32'):
        os.startfile(path)
