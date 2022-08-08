from subprocess import run
from hou import ui

def init(path):
    commit_input = ui.readInput("Commit Message", buttons=('OK', 'Cancle'), initial_contents="inital commit")
    path = str( path.resolve() )
    if commit_input[0] == 0:
        commit_message = commit_input[1]
        run(["git",  "init"], cwd=path)
        run(["git",  "add", "."], cwd=path)
        run(["git",  "commit", "-m", commit_message], cwd=path)
        run(["hub",  "create"], cwd=path)

