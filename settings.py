import json

def write(nodes=None, folder=None, loose=False):
    data = {} # Main Dict
    fdanodes = {} # Included Nodes
    for x, node in enumerate(nodes):
        parms = {} # Node Parameters Dict
        nodesettings = {}
        for parm in node.parms(): # Loop through Parms and Fill dicts
            values = {} # Per Parm Dict
            name = parm.name()
            value = parm.rawValue() 
            values["value"] = value
            parms[name] = value
            language = "None" # Save scripting Language
            try:
                language = values["language"] = parm.expressionLanguage().name()
            except:loose
                pass
            values["language"] = language
            parms[name] = values
        nodesettings["parms"] = parms
        fdanodes[f"FDA_{x}"] = nodesettings
    data["nodes"] = fdanodes
    data["loose"] = loose
    data["totalnodes"] = len(nodes)
    # writeout
    json_string = json.dumps(data, indent=4)
    settingspath = folder /  '.settings'
    settingsfile = open(settingspath, "w")
    settingsfile.write(json_string)
    settingsfile.close()

def read(folder):
    settingspath = folder /  '.settings'
    settingsfile = open(settingspath, "r")
    data = json.load(settingsfile)
    loose = data["loose"]
    parms = data["parms"]
    return loose, parms
