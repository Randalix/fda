import json
from fda import git
from shutil import copy

def write(nodes=None, folder=None, loose=False):
    data = {} # Main Dict
    fdanodes = {} # Included Nodes
    mother = None
    for x, node in enumerate(nodes):
        parms = {} # Node Parameters Dict
        nodesettings = {}
        if node.parm('FDA'):
            mother = node.parm("FDAUUID").eval()
        for parm in node.parms(): # Loop through Parms and Fill dicts
            values = {} # Per Parm Dict
            name = parm.name()
            value = parm.rawValue() 
            values["value"] = value
            parms[name] = value
            language = "None" # Save scripting Language
            try:
                language = values["language"] = parm.expressionLanguage().name()
            except:
                pass
            values["language"] = language
            parms[name] = values
        nodesettings["parms"] = parms
        uuid = node.parm("FDAUUID").eval()
        fdanodes[uuid] = nodesettings
    if not mother:
        mother = nodes[0].parm("FDAUUID").eval()
    data["nodes"] = fdanodes
    data["nodecount"] = len(nodes)
    data["mother"] = mother
    # writeout
    json_string = json.dumps(data, indent=4)
    settingsfolder = folder /  'settings' 
    settingspath = settingsfolder / 'settings'
    settingsfolder.mkdir(parents=True, exist_ok=True)
    settingsfile = open(settingspath, "w")
    settingsfile.write(json_string)
    settingsfile.close()

def backup(folder):
    settingsfolder = folder /  'settings' 
    settingspath = settingsfolder / 'settings'
    version = git.currentversion(folder)
    settings_commit_path = settingsfolder / version
    copy(str(settingspath), str(settings_commit_path))

def read(folder, name="settings"):
    settingspath = folder /  'settings' / name
    settingsfile = open(settingspath, "r")
    data = json.load(settingsfile)
    return data
