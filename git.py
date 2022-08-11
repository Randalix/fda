from subprocess import run
from subprocess import check_output
from hou import ui
from fda import config
from pathlib import Path

def init(path):
    path = str( path.resolve() )
    run(["git",  "init"], cwd=path)
    run(["git",  "add", "."], cwd=path)
    run(["git",  "commit", "-m", "inital commit"], cwd=path)
    if config.online:
        run(["hub",  "create"], cwd=path)
        run(["git",  "push", "--set-upstream", "origin", "master"], cwd=path)

def update(path):
    commit_input = ui.readInput(
            "Commit Message",
            buttons=('OK',
                'Cancle'),
            default_choice=0,
            close_choice=-1,
            )
    path = str( path.resolve() )
    if commit_input[0] == 0 and commit_input[1] != "":
        commit_message = commit_input[1]
        run(["git",  "add", "."], cwd=path)
        run(["git",  "commit", "-m", commit_message], cwd=path)
        run(["git",  "", "-m", commit_message], cwd=path)
        if config.online:
            run(["git",  "push", "--set-upstream", "origin", "master"], cwd=path)
        return True
    else:
        ui.displayMessage("Commit Aborted", buttons=('OK',))
        return False

def currentVersion(path):
    path = str( path.resolve() )
    version = check_output([ "git", "log", '--format="%H', "-n", "1"], cwd=path).decode("utf-8").replace('\n', '')[1:]
    return version

def needsupdate(node):
    tag = node.parm("FDA").eval().split(":")
    version = tag[1]
    path = Path(config.lib / tag[0])
    currentversion = currentVersion(path)
    if version != currentversion and version != "":
        return True
    else:
        return False
