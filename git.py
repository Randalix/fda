from subprocess import run
from hou import ui

def init(path):
    path = str( path.resolve() )
    run(["git",  "init"], cwd=path)
    run(["git",  "add", "."], cwd=path)
    run(["git",  "commit", "-m", "inital commit"], cwd=path)
    run(["hub",  "create"], cwd=path)
    run(["git",  "push", "--set-upstream", "origin", "master"], cwd=path)

def update(path):
    commit_input = ui.readInput("Commit Message", buttons=('OK', 'Cancle'))
    path = str( path.resolve() )
    if commit_input[0] == 0 and commit_input[1] != "":
        commit_message = commit_input[1]
        run(["git",  "add", "."], cwd=path)
        run(["git",  "commit", "-m", commit_message], cwd=path)
        run(["git",  "", "-m", commit_message], cwd=path)
        run(["git",  "push", "--set-upstream", "origin", "master"], cwd=path)
        return True
    else:
        ui.displayMessage("Commit Aborted", buttons=('OK'))
        return False
